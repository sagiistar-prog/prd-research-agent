'use strict';
const payload = JSON.parse(document.getElementById('review-data').textContent);
const result = payload.result;
const plan = result.product_plan;
const analysis = result.analysis;
const $ = id => document.getElementById(id);
const make = (tag, text, className) => { const node=document.createElement(tag); if(text!==undefined) node.textContent=text; if(className)node.className=className; return node; };
let returnTarget = null;
let returnScroll = 0;
function panel(name, moveFocus=true) {
  document.querySelectorAll('main>section').forEach(section => {section.hidden=section.id!==name;});
  document.querySelectorAll('nav button').forEach(button => { if(button.dataset.panel===name)button.setAttribute('aria-current','page'); else button.removeAttribute('aria-current'); });
  if(moveFocus) { const heading=$(name).querySelector('h2'); heading.tabIndex=-1; heading.focus(); }
}
document.querySelectorAll('nav button').forEach(button => button.addEventListener('click',()=>panel(button.dataset.panel)));
function download(filename, text, type) {
  const url=URL.createObjectURL(new Blob([text],{type})); const link=make('a'); link.href=url; link.download=filename; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('download').addEventListener('click',()=>download('product-review.md',result.markdown,'text/markdown;charset=utf-8'));
$('download-backlog').addEventListener('click',()=>download('backlog.json',JSON.stringify(result.backlog,null,2),'application/json'));
$('title').textContent=plan?plan.product_name:result.summary.product_name;
$('objective').textContent=plan?plan.objective.statement:(result.summary.one_liner||'整理输入资料，明确下一步需要做的产品决定。');
$('notice').textContent=plan?`待验证假设 ${plan.assumptions.length} 项，已登记约束响应 ${plan.constraint_responses.length} 项，其中 ${result.checks.constraint_decisions_pending} 项待决定。`:'先依据输入完成产品方案，再开始功能评审。';
$('state').textContent=plan?'待人工评审':'待补充产品方案';
$('raw-brief').textContent=analysis.requirement_markdown;
for(const e of analysis.evidence) {
  const row=make('article',undefined,'evidence-record'); row.id='source-'+e.id; row.tabIndex=-1;
  row.append(make('h3',e.id),make('p',`${e.source==='brief'?'需求原文':'竞品输入'} / 第 ${e.line} 行`,'muted'),make('blockquote',e.text)); $('evidence-list').append(row);
}
function sources(basis,container) {
  const links=make('div',undefined,'links');
  basis.evidence_refs.forEach(ref=>{
    const button=make('button',ref.id,'source'); button.setAttribute('aria-label','查看依据 '+ref.id);
    button.addEventListener('click',()=>{
      returnTarget=button; returnScroll=window.scrollY; $('return-feature').hidden=false; panel('evidence',false);
      document.querySelectorAll('.highlight').forEach(e=>e.classList.remove('highlight'));
      const target=$('source-'+ref.id); target.prepend($('return-feature')); target.classList.add('highlight'); target.focus({preventScroll:true}); target.scrollIntoView({block:'start',behavior:'instant'});
    }); links.append(button);
  });
  if(basis.assumption_ids.length)links.append(make('span','关联假设 '+basis.assumption_ids.join('、'),'muted'));
  container.append(links);
}
$('return-feature').addEventListener('click',()=>{
  if(returnTarget){const targetPanel=returnTarget.closest('section').id;panel(targetPanel,false);returnTarget.focus({preventScroll:true});window.scrollTo({top:returnScroll,behavior:'instant'});} $('return-feature').hidden=true;
});
const scopeName={mvp:'MVP',later:'后续版本'};
const priorityName={must:'必须',should:'应当',could:'可选'};
function renderFeatures() {
  const list=$('feature-list');list.replaceChildren();
  if(!plan){$('empty').hidden=false;$('empty').textContent='产品功能尚未决定。输入依据已整理，可以先阅读原文。';$('count').textContent='';return;}
  const query=$('search').value.trim().toLocaleLowerCase(); const scope=$('scope-filter').value;
  const features=plan.features.filter(f=>(scope==='all'||f.scope===scope)&&`${f.name} ${f.priority_rationale}`.toLocaleLowerCase().includes(query));
  $('count').textContent=`${features.length} / ${plan.features.length} 项`;$('empty').hidden=features.length>0;
  features.forEach(f=>{
    const row=make('article',undefined,'feature');row.id='feature-'+f.id;
    const head=make('div',undefined,'feature-head');head.append(make('h3',f.name),make('span',`${scopeName[f.scope]} / ${priorityName[f.priority]}`,'tag'));
    row.append(head,make('p',f.priority_rationale));
    const problems=plan.problems.filter(p=>f.problem_ids.includes(p.id));
    row.append(make('p','用户问题：'+problems.map(p=>p.description).join('；'),'muted')); sources(f.basis,row);
    const details=make('details'); details.append(make('summary','子功能与验收条件'));
    f.subfeatures.forEach(sub=>{const item=make('div',undefined,'fact-row');item.append(make('strong',sub.name),make('p',sub.description));details.append(item);});
    f.stories.forEach(s=>{
      const user=plan.users.find(u=>u.id===s.user_id);
      details.append(make('h4',`作为${user.name}，我希望${s.want}。`),make('p',s.benefit,'muted'));
      const criteria=make('ul',undefined,'acceptance');
      s.acceptance.forEach(c=>{const li=make('li');for(const [key,label]of [['given','给定'],['when','当'],['then','则']]){const p=make('p');p.append(make('strong',label),document.createTextNode(c[key]));li.append(p);}criteria.append(li);});details.append(criteria);
    });
    if(f.dependencies.length)details.append(make('p','前置功能：'+f.dependencies.map(id=>plan.features.find(x=>x.id===id).name).join('、'),'muted'));
    row.append(details);list.append(row);
  });
}
$('scope-filter').addEventListener('change',renderFeatures);$('search').addEventListener('input',renderFeatures);
function block(parent,title,body){const item=make('article',undefined,'block');item.append(make('h3',title));if(body)item.append(make('p',body));parent.append(item);return item;}
function list(parent,items){const ul=make('ul');items.forEach(text=>ul.append(make('li',text)));parent.append(ul);}
if(plan) {
 const planning=$('plan-content');
 for(const u of plan.users){const b=block(planning,u.name,u.job);sources(u.basis,b);}
 for(const s of plan.rollout){const b=block(planning,s.name,'包含：'+s.feature_ids.map(id=>plan.features.find(f=>f.id===id).name).join('、'));list(b,s.exit_criteria);}
 for(const m of plan.metrics){const b=block(planning,m.name+(m.kind==='guardrail'?' / 护栏':''),m.definition);b.append(make('p',`基线：${m.baseline||'未测量'}`),make('p',`目标：${m.target||'待确定'}（${{provided:'输入目标',proposed:'建议目标',unknown:'尚未确定'}[m.target_status]}）`),make('p','采集方式：'+m.collection,'muted'));sources(m.basis,b);}
 const exclusion=block(planning,'暂不纳入');plan.out_of_scope.forEach(o=>{exclusion.append(make('h4',o.item),make('p',o.reason));sources(o.basis,exclusion);});if(!plan.out_of_scope.length)exclusion.append(make('p','未登记排除项。'));
 const decisions=$('decision-content');
 for(const a of plan.assumptions){const b=block(decisions,a.id+' / '+{high:'高影响',medium:'中影响',low:'低影响'}[a.impact],a.claim);b.append(make('p','验证方法：'+a.validation));}
 if(!plan.assumptions.length)block(decisions,'未登记假设','评审时仍需核对是否遗漏。');
 const constraints=block(decisions,'约束响应');
 for(const c of plan.constraint_responses){const source=analysis.evidence.find(e=>e.id===c.evidence_id);constraints.append(make('h4',source.text),make('p',`${{honored:'已在方案中处理',deferred:'延后处理',needs_decision:'待决定'}[c.treatment]}：${c.implementation}`));sources({evidence_refs:[{id:c.evidence_id}],assumption_ids:[]},constraints);}
 if(!plan.constraint_responses.length)constraints.append(make('p','没有识别到独立约束字段，请核对原始需求。'));
 const questions=block(decisions,'评审问题');list(questions,plan.open_questions.length?plan.open_questions:['未登记其他问题，方案仍需人工确认。']);
} else {
 $('scope-filter').disabled=true;$('search').disabled=true;$('download-backlog').disabled=true;
 block($('plan-content'),'尚无产品方案','先根据输入定义用户、问题和有依据的功能范围。');
 block($('decision-content'),'先阅读原始需求','输入中没有独立标题的内容也可能包含用户和约束；不要仅凭字段缺失重复询问。');
}
renderFeatures();
