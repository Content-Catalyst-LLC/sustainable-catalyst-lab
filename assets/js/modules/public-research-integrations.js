(function(W,D){'use strict';
const Lab=W.SCLab||{},V='0.38.2';
function q(r,s){return r.querySelector(s)}
function api(path,method,body){
  const base=(W.SCLabSettings&&W.SCLabSettings.restUrl)||(W.SCLabConfig&&W.SCLabConfig.restUrl)||'/wp-json/sc-lab/v1/';
  const headers={'Content-Type':'application/json'};
  const nonce=(W.SCLabConfig&&W.SCLabConfig.nonce)||''; if(nonce)headers['X-WP-Nonce']=nonce;
  const options={method:method||'GET',credentials:'same-origin',headers};
  if(body!==undefined)options.body=JSON.stringify(body);
  return fetch(base.replace(/\/$/,'/')+path.replace(/^\//,''),options).then(async response=>{
    const data=await response.json().catch(()=>({detail:'Invalid JSON response'}));
    if(!response.ok)throw new Error(data.detail||data.message||('HTTP '+response.status));
    return data;
  });
}
function parse(el){try{return JSON.parse((el&&el.value)||'{}')}catch(error){throw new Error('Invalid JSON: '+error.message)}}
function val(r,name){const el=q(r,'[data-pri-v0382-'+name+']');return el?el.value.trim():''}
function output(r,value){const el=q(r,'[data-pri-v0382-output]');if(el)el.textContent=JSON.stringify(value,null,2)}
function status(r,text,isError){const el=q(r,'[data-pri-v0382-status]');if(!el)return;el.textContent=text;el.classList.toggle('is-error',!!isError)}
function metric(label,value){const node=D.createElement('div');node.className='sc-pri0382-metric';const span=D.createElement('span');span.textContent=label;const strong=D.createElement('strong');strong.textContent=String(value);node.append(span,strong);return node}
async function refresh(r){
  const [health,catalog,sdk]=await Promise.all([
    api('compute/core/research-integrations/health'),
    api('compute/core/public-research-api'),
    api('compute/core/research-integrations/sdk')
  ]);
  const metrics=q(r,'[data-pri-v0382-metrics]'); if(metrics){metrics.textContent='';[
    ['API',catalog.apiVersion||'v1'],
    ['Events',(health.eventTypes||[]).length],
    ['Embed views',(health.embedViews||[]).length],
    ['SDK packages',(sdk.packages||[]).length],
    ['Delivery',health.deliveryEnabled?'Enabled':'Queue only'],
    ['Version',V]
  ].forEach(item=>metrics.appendChild(metric(item[0],item[1])));}
  output(r,{health,catalog,sdk}); status(r,'Public research integration service ready.');
}
async function action(r,name){
  const workspace=val(r,'workspace')||'research-team';
  const subscription=val(r,'subscription');
  const delivery=val(r,'delivery');
  if(name==='refresh')return refresh(r);
  if(name==='catalog')return output(r,await api('compute/core/public-research-api'));
  if(name==='policies')return output(r,await api('compute/core/research-integrations/policies'));
  if(name==='sdk')return output(r,await api('compute/core/research-integrations/sdk'));
  if(name==='webhooks')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/webhooks'));
  if(name==='register-webhook')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/webhooks','POST',parse(q(r,'[data-pri-v0382-webhook-json]'))));
  if(name==='update-webhook'){
    if(!subscription)throw new Error('Enter a webhook subscription ID.');
    return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/webhooks/'+encodeURIComponent(subscription),'PATCH',parse(q(r,'[data-pri-v0382-webhook-update-json]'))));
  }
  if(name==='emit')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/webhook-events','POST',parse(q(r,'[data-pri-v0382-event-json]'))));
  if(name==='deliveries')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/webhook-deliveries?limit=200'));
  if(name==='dispatch'){
    if(!delivery)throw new Error('Enter a webhook delivery ID.');
    return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/webhook-deliveries/'+encodeURIComponent(delivery)+'/dispatch','POST',{}));
  }
  if(name==='embed')return output(r,await api('compute/core/team-workspaces/'+encodeURIComponent(workspace)+'/research-embeds','POST',parse(q(r,'[data-pri-v0382-embed-json]'))));
}
function init(r){
  if(r.dataset.priV0382Ready)return; r.dataset.priV0382Ready='1';
  r.addEventListener('click',event=>{
    const button=event.target.closest('[data-pri-v0382-action]'); if(!button)return;
    button.disabled=true;status(r,'Working…');
    Promise.resolve(action(r,button.dataset.priV0382Action)).then(()=>status(r,'Action completed.')).catch(error=>{status(r,error.message,true);output(r,{ok:false,error:error.message})}).finally(()=>{button.disabled=false});
  });
  refresh(r).catch(error=>{status(r,error.message,true);output(r,{ok:false,error:error.message})});
}
Lab.registerModule?Lab.registerModule('public-research-integrations',init):D.addEventListener('DOMContentLoaded',()=>D.querySelectorAll('[data-lab-module="public-research-integrations"]').forEach(init));
})(window,document);
