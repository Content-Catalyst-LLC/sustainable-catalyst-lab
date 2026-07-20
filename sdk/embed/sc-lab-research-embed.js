(function(global){
  'use strict';
  async function mount(target, options){
    const node=typeof target==='string'?document.querySelector(target):target;
    if(!node) throw new Error('Embed target not found.');
    const base=String(options.baseUrl||'').replace(/\/$/,'');
    const token=String(options.token||'');
    const response=await fetch(base+'/v1/public/research-embeds/'+encodeURIComponent(token),{headers:{Accept:'application/json'}});
    const body=await response.json();
    if(!response.ok) throw new Error(body.detail||'Research embed unavailable.');
    const manifest=body.manifest||{}; const resource=manifest.resource||{};
    node.replaceChildren();
    const article=document.createElement('article'); article.className='sc-lab-research-embed';
    const eyebrow=document.createElement('p'); eyebrow.textContent='Sustainable Catalyst Research'; eyebrow.className='sc-lab-research-embed__eyebrow';
    const title=document.createElement('h2'); title.textContent=manifest.title||resource.title||resource.id||'Research record';
    const meta=document.createElement('p'); meta.textContent=(manifest.view||'research')+' · '+(resource.id||'record');
    article.append(eyebrow,title,meta); node.append(article); return body;
  }
  global.SustainableCatalystResearchEmbed={mount:mount,version:'1.0.0'};
})(window);
