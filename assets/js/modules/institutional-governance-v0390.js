(function(W,D){'use strict';
const Lab=W.SCLab||{},V='0.39.0';
function q(r,s){return r.querySelector(s)}
function api(path,method,body){
  const base=(W.SCLabSettings&&W.SCLabSettings.restUrl)||(W.SCLabConfig&&W.SCLabConfig.restBase)||'/wp-json/sc-lab/v1/';
  const headers={'Content-Type':'application/json'};const nonce=(W.SCLabConfig&&W.SCLabConfig.nonce)||'';if(nonce)headers['X-WP-Nonce']=nonce;
  const options={method:method||'GET',credentials:'same-origin',headers};if(body!==undefined)options.body=JSON.stringify(body);
  return fetch(base.replace(/\/$/,'/')+path.replace(/^\//,''),options).then(async response=>{const data=await response.json().catch(()=>({detail:'Invalid JSON response'}));if(!response.ok)throw new Error(data.detail||data.message||('HTTP '+response.status));return data;});
}
function parse(el){try{return JSON.parse((el&&el.value)||'{}')}catch(error){throw new Error('Invalid JSON: '+error.message)}}
function val(r,name){const el=q(r,'[data-ig-v0390-'+name+']');return el?el.value.trim():''}
function output(r,value){const el=q(r,'[data-ig-v0390-output]');if(el)el.textContent=JSON.stringify(value,null,2)}
function status(r,text,isError){const el=q(r,'[data-ig-v0390-status]');if(!el)return;el.textContent=text;el.classList.toggle('is-error',!!isError)}
function metric(label,value){const node=D.createElement('div');node.className='sc-ig0390-metric';const span=D.createElement('span');span.textContent=label;const strong=D.createElement('strong');strong.textContent=String(value);node.append(span,strong);return node}
async function refresh(r){
  const institution=val(r,'institution')||'catalyst-institute';
  const health=await api('compute/core/institutional-governance/health');
  let dashboard={counts:{}};try{dashboard=await api('compute/core/institutions/'+encodeURIComponent(institution)+'/governance-dashboard')}catch(ignore){}
  const counts=Object.assign({},health.counts||{},dashboard.counts||{}),metrics=q(r,'[data-ig-v0390-metrics]');
  if(metrics){metrics.textContent='';[['Institutions',counts.institutions||0],['Principals',counts.principals||0],['Bindings',counts.activeBindings||counts.roleBindings||0],['Workspaces',counts.governedWorkspaces||0],['Approvals',counts.pendingApprovals||0],['Version',V]].forEach(item=>metrics.appendChild(metric(item[0],item[1])))}
  output(r,{health,dashboard});status(r,'Institutional governance service ready.');
}
async function action(r,name){
  const institution=val(r,'institution')||'catalyst-institute',workspace=val(r,'workspace')||'research-team',binding=val(r,'binding'),approval=val(r,'approval');
  if(name==='refresh')return refresh(r);
  if(name==='policies')return output(r,await api('compute/core/institutional-governance/policies'));
  if(name==='institutions')return output(r,await api('compute/core/institutions'));
  if(name==='create-institution')return output(r,await api('compute/core/institutions','POST',parse(q(r,'[data-ig-v0390-institution-json]'))));
  if(name==='dashboard')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/governance-dashboard'));
  if(name==='units')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/units'));
  if(name==='create-unit')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/units','POST',parse(q(r,'[data-ig-v0390-unit-json]'))));
  if(name==='principals')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/principals'));
  if(name==='create-principal')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/principals','POST',parse(q(r,'[data-ig-v0390-principal-json]'))));
  if(name==='bindings')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/role-bindings'));
  if(name==='grant')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/role-bindings','POST',parse(q(r,'[data-ig-v0390-binding-json]'))));
  if(name==='revoke'){if(!binding)throw new Error('Enter a role binding ID.');return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/role-bindings/'+encodeURIComponent(binding),'DELETE',{}));}
  if(name==='retention')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/retention-policies'));
  if(name==='create-retention')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/retention-policies','POST',parse(q(r,'[data-ig-v0390-retention-json]'))));
  if(name==='govern')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/institutional-governance','POST',parse(q(r,'[data-ig-v0390-governance-json]'))));
  if(name==='workspace')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/institutional-governance'));
  if(name==='evaluate')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/institutional-governance/evaluate','POST',parse(q(r,'[data-ig-v0390-evaluate-json]'))));
  if(name==='approvals')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/governance-approvals'));
  if(name==='request-approval')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/governance-approvals','POST',parse(q(r,'[data-ig-v0390-approval-json]'))));
  if(name==='decide'){if(!approval)throw new Error('Enter an approval request ID.');return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/governance-approvals/'+encodeURIComponent(approval)+'/decisions','POST',parse(q(r,'[data-ig-v0390-decision-json]'))));}
  if(name==='timeline')return output(r,await api('compute/core/institutions/'+encodeURIComponent(institution)+'/governance-timeline?limit=500'));
}
function init(r){if(r.dataset.igV0390Ready)return;r.dataset.igV0390Ready='1';r.addEventListener('click',event=>{const button=event.target.closest('[data-ig-v0390-action]');if(!button)return;button.disabled=true;status(r,'Working…');Promise.resolve(action(r,button.dataset.igV0390Action)).then(()=>status(r,'Action completed.')).catch(error=>{status(r,error.message,true);output(r,{ok:false,error:error.message})}).finally(()=>{button.disabled=false})});refresh(r).catch(error=>{status(r,error.message,true);output(r,{ok:false,error:error.message})});}
Lab.registerModule?Lab.registerModule('institutional-governance-v0390',init):D.addEventListener('DOMContentLoaded',()=>D.querySelectorAll('[data-lab-module="institutional-governance-v0390"]').forEach(init));
})(window,document);
