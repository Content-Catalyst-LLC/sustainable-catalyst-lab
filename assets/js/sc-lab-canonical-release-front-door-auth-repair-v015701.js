(function(w,d){
'use strict';
const C=w.SCLabCanonicalRepairV015701||{};
const release=String(C.releaseVersion||C.version||'0.157.0.1');
const authenticated=!!C.authenticated;
const authMessage=String(C.authMessage||'Sign in to use server-backed project storage. Public Lab visualization remains available.');
const protectedPrefixes=[
 '/wp-json/sc-lab/v1/workspace/4d/v01530/',
 '/wp-json/sc-lab/v1/workspace/reproducible/v01540/',
 '/wp-json/sc-lab/v1/workspace/batch-campaigns/v01550/',
 '/wp-json/sc-lab/v1/workspace/distributed/v01560/',
 '/wp-json/sc-lab/v1/workspace/cross-study/v01570/',
 '/wp-json/sc-lab/v1/workspace/replication-network/v01580/'
];
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function isHealth(path){return /\/health\/?$/.test(path)}
function isProtectedPath(path){return protectedPrefixes.some(p=>path.indexOf(p)===0)&&!isHealth(path)}
function syntheticUnauthorized(){
 const body=JSON.stringify({code:'sc_lab_login_required',detail:authMessage,message:authMessage,data:{status:401}});
 if(typeof w.Response==='function')return Promise.resolve(new Response(body,{status:401,headers:{'Content-Type':'application/json'}}));
 return Promise.reject(new Error(authMessage));
}
function installFetchGate(){
 if(authenticated||!w.fetch||w.fetch.__scLabV015701)return;
 const native=w.fetch.bind(w);
 const wrapped=function(input,init){
  try{
   const raw=typeof input==='string'?input:(input&&input.url)||'';
   const u=new URL(raw,w.location.href);
   if(u.origin===w.location.origin&&isProtectedPath(u.pathname))return syntheticUnauthorized();
  }catch(_){ }
  return native(input,init);
 };
 wrapped.__scLabV015701=true; wrapped.__native=native; w.fetch=wrapped;
}
function replaceExactTextWithin(root,re){
 if(!root)return 0;let n=0;
 const walker=d.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
 nodes.forEach(node=>{const before=node.nodeValue||'';const trimmed=norm(before);if(re.test(trimmed)){node.nodeValue=before.replace(trimmed,'v'+release);n++;}});
 return n;
}
function syncLabAppIdentity(){
 d.querySelectorAll('.sc-lab-app .sc-lab-version').forEach(el=>{el.textContent='v'+release;el.dataset.canonicalRelease=release});
 d.querySelectorAll('[data-sc-lab-console-release]').forEach(el=>{el.textContent='v'+release});
 d.querySelectorAll('[data-sc-lab-release-version]').forEach(el=>{el.textContent=release});
 d.querySelectorAll('.sc-lab-app').forEach(app=>{
  app.dataset.canonicalRelease=release;
  const walker=d.createTreeWalker(app,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  nodes.forEach(node=>{
   const value=node.nodeValue||'';
   if(/canonical runtime/i.test(value)&&/Lab\s+0\.\d+(?:\.\d+){1,2}/i.test(value)){
    node.nodeValue=value.replace(/Lab\s+0\.\d+(?:\.\d+){1,2}/i,'Lab '+release);
   }
  });
 });
}
function landingCardContainer(label){
 let p=label;
 for(let i=0;i<6&&p;i++,p=p.parentElement){
  if(p.classList&&p.classList.contains('sc-lab-app'))return null;
  const t=norm(p.textContent);
  if(t.includes('LAB APP')&&(t.includes('Workbench')||t.includes('Decision Studio')||t.includes('Site Intelligence')))return p;
 }
 return label.parentElement;
}
function syncLandingCard(){
 const all=Array.from(d.querySelectorAll('body *')).filter(el=>norm(el.textContent)==='LAB APP'&&!el.closest('.sc-lab-app'));
 all.forEach(label=>{
  const box=landingCardContainer(label);if(!box)return;
  replaceExactTextWithin(box,/^v0\.\d+(?:\.\d+){1,2}$/i);
  box.dataset.scLabCanonicalRelease=release;
 });
}
const locked=[
 ['[data-v01530-workspace]','[data-v01530-status]'],
 ['[data-v01540-workspace]','[data-v01540-status]'],
 ['[data-v01550-workspace]','[data-v01550-status]'],
 ['[data-v01560-workspace]','[data-v01560-status]'],
 ['[data-v01570-workspace]','[data-v01570-status]'],
 ['[data-v01580-workspace]','[data-v01580-status]']
];
function applyAuthorizationPresentation(){
 if(authenticated)return;
 locked.forEach(pair=>{
  const root=d.querySelector(pair[0]);if(!root)return;
  root.classList.add('sc-lab-auth-required-v015701');root.dataset.authState='login-required';
  const status=root.querySelector(pair[1]);if(status){status.textContent=authMessage;status.dataset.state='auth-required'}
  root.querySelectorAll('button').forEach(btn=>{btn.disabled=true;btn.setAttribute('aria-disabled','true')});
  const project=root.querySelector('input[data-v01530-project],input[data-v01540-project],input[data-v01550-project],input[data-v01560-project],input[data-v01570-project],input[data-v01580-project]');
  if(project){project.value='';project.placeholder='Sign in to use project storage';project.disabled=true;project.setAttribute('aria-disabled','true')}
  if(!root.querySelector('[data-v015701-login]')&&C.loginUrl){
   const a=d.createElement('a');a.href=C.loginUrl;a.dataset.v015701Login='1';a.className='sc-lab-v015701-login';a.textContent='Sign in to use project storage';
   (status&&status.parentElement?status.parentElement:root).appendChild(a);
  }
 });
}
function synchronize(){syncLabAppIdentity();syncLandingCard();applyAuthorizationPresentation()}
installFetchGate();
if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',synchronize,{once:true});else synchronize();
let queued=false;const observer=new MutationObserver(()=>{if(queued)return;queued=true;w.requestAnimationFrame(()=>{queued=false;synchronize()})});
if(d.documentElement)observer.observe(d.documentElement,{childList:true,subtree:true});
w.SCLabCanonicalRepairV015701Runtime={version:'0.157.0.1',releaseVersion:release,authenticated,synchronize};
})(window,document);
