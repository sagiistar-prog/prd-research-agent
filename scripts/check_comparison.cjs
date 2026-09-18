const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'output','browser-comparison');
const review=path.join(root,'.impeccable','review');
fs.mkdirSync(output,{recursive:true});fs.mkdirSync(review,{recursive:true});
const prepare=spawnSync(process.env.PYTHON||'python',['-X','utf8','-c',`
import copy,json,sys
from pathlib import Path
sys.path.insert(0,'scripts')
from plugin_run import run
from compare_revisions import compare,render_html,render_markdown
data=json.loads(Path('examples/plugin-input.json').read_text(encoding='utf-8'))
data['product_plan']=json.loads(Path('examples/team-pulse-plan.json').read_text(encoding='utf-8'))
before=run(data)
for name in ['changed','context','empty','hostile','reordered','renumbered']:
    changed=copy.deepcopy(data);plan=changed['product_plan']
    if name=='changed':plan['features'][0]['stories'][0]['acceptance'][0]['then']='虚构修订：先核对匿名阈值，再显示统计。'
    if name=='context':plan['open_questions'].append('虚构修订：谁负责每轮复核？')
    if name=='hostile':plan['features'][0]['name']='</script><script>window.pwned=true</script>'+'长内容'*50
    if name=='reordered':plan['features'].reverse()
    if name=='renumbered':
        plan['features'][-1]['id']='F5'
        for entry in [*plan['rollout'],*plan['constraint_responses']]:entry['feature_ids']=['F5' if x=='F4' else x for x in entry['feature_ids']]
    report=compare(before,run(changed))
    Path('output/browser-comparison/'+name+'.html').write_text(render_html(report),encoding='utf-8')
    Path('output/browser-comparison/'+name+'.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
    Path('output/browser-comparison/'+name+'.md').write_bytes(render_markdown(report).encode('utf-8'))
`],{cwd:root,encoding:'utf8'});
assert.equal(prepare.status,0,prepare.stdout+prepare.stderr);
async function downloaded(page,selector){
 const [file]=await Promise.all([page.waitForEvent('download'),page.locator(selector).click()]);
 const parts=[];for await(const part of await file.createReadStream())parts.push(part);
 return Buffer.concat(parts).toString('utf8');
}
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})});
 const checks=[];
 try{
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:width===1440?1000:844},reducedMotion:'reduce'});
   const errors=[],external=[];
   page.on('pageerror',error=>errors.push(error.message));
   await page.route(/^https?:/,route=>{external.push(route.request().url());return route.abort();});
   const open=async name=>page.goto(pathToFileURL(path.join(output,name+'.html')).href);
   const noOverflow=async()=>assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${width} overflow`);
   await open('changed');
   assert.equal(await page.locator('.feature').count(),1);
   await page.selectOption('#kind','added');assert.equal(await page.locator('#empty').isVisible(),true);
   await page.selectOption('#kind','modified');await page.fill('#search','F1');
   await page.getByText('用户故事与验收条件',{exact:true}).click();
   assert.match(await page.locator('.feature details[open]').innerText(),/变更前[\s\S]*变更后[\s\S]*先核对匿名阈值/);
   await page.screenshot({path:path.join(review,`comparison-changes-${width}.png`),fullPage:true});
   await noOverflow();
   await page.fill('#search','不存在');assert.equal(await page.locator('#empty').isVisible(),true);
   await page.fill('#search','F1');
   assert.equal(await downloaded(page,'#download'),fs.readFileSync(path.join(output,'changed.md'),'utf8'));
   assert.deepEqual(JSON.parse(await downloaded(page,'#download-json')),JSON.parse(fs.readFileSync(path.join(output,'changed.json'),'utf8')));
   await page.addScriptTag({path:require.resolve('axe-core/axe.min.js')});
   const panels=[];
   for(const panel of ['changes','context','impact']){
    await page.locator(`nav [data-panel="${panel}"]`).click();
    assert.equal(await page.locator(`#${panel} h2`).evaluate(e=>document.activeElement===e),true);
    await noOverflow();
    const violations=await page.evaluate(async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations.map(x=>({id:x.id,count:x.nodes.length})));
    assert.deepEqual(violations,[],JSON.stringify({width,panel,violations}));panels.push({panel,violations:0});
   }
   assert.equal(await page.locator('#impact-list article').count(),4);
   assert.match(await page.locator('#impact-list article').filter({hasText:'F3'}).innerText(),/依赖功能变化：F1/);
   await page.screenshot({path:path.join(review,`comparison-impact-${width}.png`),fullPage:true});
   await page.locator('nav [data-panel="changes"]').click();
   assert.equal(await page.inputValue('#kind'),'modified');assert.equal(await page.inputValue('#search'),'F1');
   await page.locator('.feature summary').focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('.feature details[open]').count(),1);
   assert.equal((await page.locator('body').innerText()).includes('·'),false);
   for(const name of ['context','empty','hostile','reordered','renumbered']){
    await open(name);
    if(name==='context'){
     await page.locator('nav [data-panel="context"]').click();await page.locator('#context-list summary').click();
     assert.match(await page.locator('#context-list').innerText(),/谁负责每轮复核/);
     await page.locator('nav [data-panel="impact"]').click();assert.equal(await page.locator('#impact-list article').count(),4);
    }
    if(name==='empty'){assert.equal(await page.locator('.feature').count(),0);assert.equal(await page.locator('#empty').isVisible(),true);assert.equal(await page.locator('#order').isVisible(),false);}
    if(name==='hostile'){assert.equal(await page.evaluate(()=>window.pwned),undefined);assert.equal(await page.locator('.feature').count(),1);}
    if(name==='reordered'){assert.equal(await page.locator('.feature').count(),0);await page.locator('#order summary').click();assert.match(await page.locator('#after-order').innerText(),/F4、F3、F2、F1/);}
    if(name==='renumbered'){
     await page.selectOption('#kind','removed');assert.equal(await page.locator('.feature').getAttribute('data-feature-id'),'F4');
     await page.selectOption('#kind','added');assert.equal(await page.locator('.feature').getAttribute('data-feature-id'),'F5');
    }
    await noOverflow();
   }
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
   checks.push({width,panels,downloadsMatch:true,dependencyReview:true,contextReview:true,keyboard:true,addRemove:true,unchanged:true,reorder:true,injectionPrevented:true,externalRequests:0,scriptErrors:0,overflow:false});
   await page.close();
  }
  fs.writeFileSync(path.join(output,'acceptance.json'),JSON.stringify(checks,null,2)+'\n');console.log(JSON.stringify(checks));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
