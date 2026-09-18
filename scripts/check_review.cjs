const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'output','browser-check');
const review=path.join(root,'.impeccable','review');
fs.mkdirSync(output,{recursive:true});fs.mkdirSync(review,{recursive:true});
const python=process.env.PYTHON||'python';
const prepare=spawnSync(python,['-X','utf8','-c',`
import json,sys
from pathlib import Path
sys.path.insert(0,'scripts')
from plugin_run import run
from review_renderer import render_review
for name,source,plan in [('team','examples/plugin-input.json','examples/team-pulse-plan.json'),('fitcheck','examples/fitcheck-input.json','examples/fitcheck-plan.json'),('empty',None,None),('hostile',None,None)]:
    data=json.loads(Path(source).read_text(encoding='utf-8')) if source else {'requirement_markdown':'No product plan yet.' if name=='empty' else '</script><script>window.pwned=true</script>'}
    if plan: data['product_plan']=json.loads(Path(plan).read_text(encoding='utf-8'))
    result=run(data)
    Path('output/browser-check/'+name+'.html').write_text(render_review(result),encoding='utf-8')
    Path('output/browser-check/'+name+'.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
`],{cwd:root,encoding:'utf8'});
assert.equal(prepare.status,0,prepare.stderr);
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})});
 const checks=[];
 try{
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:width===1440?1000:844},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(output,'team.html')).href);
  await page.getByRole('heading',{name:'TeamPulse 团队健康度助手',exact:true}).waitFor();
  await page.screenshot({path:path.join(review,width===1440?'desktop.png':'mobile.png'),fullPage:true});
  await page.selectOption('#scope-filter','mvp');assert.equal(await page.locator('.feature').count(),3);
  await page.selectOption('#scope-filter','later');assert.equal(await page.locator('.feature').count(),1);
  await page.fill('#search','不存在的功能');assert.equal(await page.locator('#empty').isVisible(),true);
  await page.fill('#search','');await page.selectOption('#scope-filter','mvp');
  await page.locator('.feature summary').first().click();assert.equal(await page.locator('.feature details[open] .acceptance li').count(),2);
  const returnVisibility=[];
  for(const sourceId of ['E007','E016']){
   const source=page.locator('.feature .source').filter({hasText:sourceId}).first();
   await source.scrollIntoViewIfNeeded();const previousScroll=await page.evaluate(()=>window.scrollY);
   await source.click();assert.equal(await page.locator('#evidence').isVisible(),true);assert.equal(await page.locator('.highlight h3').textContent(),sourceId);
   const back=page.getByRole('button',{name:'返回评审'});
   const rect=await back.boundingBox();assert(rect.y>=0&&rect.y+rect.height<=(width===1440?1000:844),'Return must be visible before automation scrolls');
   await page.keyboard.press('Tab');assert.equal(await back.evaluate(e=>e===document.activeElement),true);
   await page.screenshot({path:path.join(review,`source-${sourceId}-${width}.png`),fullPage:false});
   await page.keyboard.press('Enter');assert.equal(await source.evaluate(e=>e===document.activeElement),true);
   assert.equal(await page.inputValue('#scope-filter'),'mvp');assert.equal(await page.locator('.feature details[open]').count(),1);
   assert(Math.abs((await page.evaluate(()=>window.scrollY))-previousScroll)<=1,'Return should restore scroll');
   returnVisibility.push({sourceId,visible:true,forwardKeyboard:true,filterAndDisclosurePreserved:true,scrollRestored:true});
  }
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#download').click()]);
  const stream=await download.createReadStream();const chunks=[];for await(const chunk of stream)chunks.push(chunk);
  const expected=JSON.parse(fs.readFileSync(path.join(output,'team.json'),'utf8'));
  assert.equal(Buffer.concat(chunks).toString('utf8'),expected.result.markdown);
  const [backlog]=await Promise.all([page.waitForEvent('download'),page.locator('#download-backlog').click()]);
  const bstream=await backlog.createReadStream();const bchunks=[];for await(const chunk of bstream)bchunks.push(chunk);
  assert.deepEqual(JSON.parse(Buffer.concat(bchunks).toString('utf8')),expected.result.backlog);
  const axe=[];
  await page.addScriptTag({path:require.resolve('axe-core/axe.min.js')});
  for(const panel of ['scope','planning','decisions','evidence']){
   await page.locator(`nav [data-panel="${panel}"]`).click();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,`${width} ${panel} overflow`);
   const violations=await page.evaluate(async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations.map(x=>({id:x.id,count:x.nodes.length})));
   assert.deepEqual(violations,[],JSON.stringify({width,panel,violations}));axe.push({panel,violations:0});
  }
  assert.equal(await page.locator('body').innerText().then(t=>t.includes('·')),false);
  for(const name of ['fitcheck','empty','hostile']){
   await page.goto(pathToFileURL(path.join(output,name+'.html')).href);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
   if(name==='fitcheck'){assert.match(await page.title(),/FitCheck/);assert.equal(await page.locator('.feature').count(),5);}
   if(name==='empty'){assert.equal(await page.locator('#empty').isVisible(),true);assert.equal(await page.locator('#download-backlog').isDisabled(),true);}
   if(name==='hostile'){assert.equal(await page.evaluate(()=>window.pwned),undefined);assert.equal(await page.locator('#title').textContent(),'未命名需求');}
  }
  assert.deepEqual(errors,[]);checks.push({width,axe,scriptErrors:0,overflow:false,downloadsMatch:true,sourceRoundTrip:true,returnVisibility});await page.close();
 }
 fs.writeFileSync(path.join(output,'acceptance.json'),JSON.stringify(checks,null,2)+'\n');console.log(JSON.stringify(checks));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
