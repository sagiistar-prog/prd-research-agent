'use strict';
const data=JSON.parse(document.getElementById('comparison-data').textContent), report=data.report;
const $=id=>document.getElementById(id);
const node=(tag,text,className)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;};
const labels={...data.labels,id:'编号',user_id:'用户',user_ids:'用户',want:'希望',benefit:'用户收益',acceptance:'验收条件',given:'给定',when:'当',then:'则',description:'说明',evidence_refs:'引用',assumption_ids:'假设',quote:'原文',claim:'判断',validation:'验证方法',impact:'影响',statement:'目标',job:'任务',definition:'定义',baseline:'基线',target:'目标值',target_status:'目标来源',collection:'采集方式',kind:'指标类型',feature_ids:'功能',exit_criteria:'退出条件',item:'事项',reason:'理由',evidence_id:'依据编号',treatment:'处理方式',implementation:'实现响应'};
const types={added:'新增',removed:'移除',modified:'修改'};
function readable(value){
 if(value===null)return '未提供';
 if(Array.isArray(value)){const list=node('ul');if(!value.length)return node('p','无');for(const item of value){const li=node('li');li.append(readable(item));list.append(li);}return list;}
 if(typeof value==='object'){const list=node('dl');for(const [key,item]of Object.entries(value)){list.append(node('dt',labels[key]||key));const dd=node('dd');dd.append(readable(item));list.append(dd);}return list;}
 return String(value);
}
function difference(parent,label,before,after){const details=node('details');details.append(node('summary',label));const pair=node('div',undefined,'comparison-pair');for(const [heading,value] of [['变更前',before],['变更后',after]]){const column=node('div',undefined,'comparison-value');column.append(node('h4',heading));const content=node('div');content.append(readable(value));column.append(content);pair.append(column);}details.append(pair);parent.append(details);}
function render(){
 const list=$('feature-list');list.replaceChildren();const query=$('search').value.trim().toLowerCase();
 const rows=report.features.filter(f=>($('kind').value==='all'||f.kind===$('kind').value)&&`${f.id} ${f.name}`.toLowerCase().includes(query));
 $('count').textContent=`${rows.length} / ${report.features.length} 项`;$('empty').hidden=rows.length>0;
 for(const row of rows){const article=node('article',undefined,'feature');article.dataset.featureId=row.id;article.append(node('h3',`${row.id} ${row.name}`),node('p',types[row.kind],'muted'));for(const field of row.fields)difference(article,labels[field]||field,row.before?.[field]??null,row.after?.[field]??null);list.append(article);}
}
function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type}));const link=node('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('download').addEventListener('click',()=>download('changes.md',data.markdown,'text/markdown;charset=utf-8'));
$('download-json').addEventListener('click',()=>download('changes.json',JSON.stringify(report,null,2),'application/json'));
$('kind').addEventListener('change',render);$('search').addEventListener('input',render);
$('title').textContent=report.product_name+' 版本比较';$('summary').textContent=`新增 ${report.summary.added} 项，移除 ${report.summary.removed} 项，修改 ${report.summary.modified} 项。`;
if(report.sections.length)$('summary').textContent+=` ${report.sections.length} 项规划背景变化。`;
if(report.inputs_changed)$('summary').textContent+=' 输入依据已更新。';
$('before-id').textContent='旧快照：'+report.before_snapshot;$('after-id').textContent='新快照：'+report.after_snapshot;
if(report.feature_order_changed){$('order').hidden=false;$('before-order').textContent='原次序：'+report.before_order.join('、');$('after-order').textContent='新次序：'+report.after_order.join('、');}
for(const row of [...report.sections,...report.input_changes])difference($('context-list'),labels[row.field]||row.field,row.before,row.after);
if(!report.sections.length&&!report.input_changes.length)$('context-list').append(node('p','背景与输入依据没有变化。'));
for(const row of report.review_candidates){const article=node('article',undefined,'block');article.append(node('h3',`${row.id} ${row.name}`));const reasons=node('ul');for(const reason of row.reasons)reasons.append(node('li',reason));article.append(reasons);$('impact-list').append(article);}
if(!report.review_candidates.length)$('impact-list').append(node('p','未发现需要连带复核的现有功能；这不代表方案已经获批。'));
document.querySelectorAll('nav button').forEach(button=>button.addEventListener('click',()=>{for(const section of document.querySelectorAll('main>section'))section.hidden=section.id!==button.dataset.panel;for(const other of document.querySelectorAll('nav button')){if(other===button)other.setAttribute('aria-current','page');else other.removeAttribute('aria-current');}const title=$(button.dataset.panel).querySelector('h2');title.tabIndex=-1;title.focus();}));
render();
