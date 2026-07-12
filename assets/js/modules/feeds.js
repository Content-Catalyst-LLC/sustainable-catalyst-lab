(function(w){'use strict';
const Lab=w.SCLab=w.SCLab||{},U=Lab.util;
function url(source,params={}){const base=(w.SCLabConfig?.restBase||'/wp-json/sc-lab/v1/')+`feeds/${encodeURIComponent(source)}`;const q=new URLSearchParams(params);return base+'?'+q.toString()}
function queryParams(source,q,limit){const p={limit};if(q){if(source==='obis-marine')p.scientificName=q;else p.q=q}return p}
async function load(source,q='',limit=12){return U.fetchJson(url(source,queryParams(source,q,limit)),{headers:{'X-WP-Nonce':w.SCLabConfig?.nonce||''}})}
function card(record,projects,root){const el=document.createElement('article');el.className='sc-lab-feed-card';const img=record.thumbnail?`<img loading="lazy" src="${U.esc(record.thumbnail)}" alt="">`:'';el.innerHTML=`${img}<h4>${U.esc(record.title)}</h4><p>${U.esc((record.summary||record.abstract||'').slice(0,330))}</p><div class="sc-lab-feed-meta">${U.esc(record.source)} · ${U.esc(record.domain)}<br>${U.esc(U.fmt(record.observedAt))}</div><div class="sc-lab-card-actions"><button class="sc-lab-button" data-save-evidence>Save evidence</button><button class="sc-lab-button" data-cite-note>Cite notebook</button></div>`;
el.querySelector('[data-save-evidence]').addEventListener('click',()=>{projects.add('evidence',{title:record.title,summary:record.summary||record.abstract||'',source:record.source,url:record.url,observedAt:record.observedAt,record,status:'unreviewed'},`Evidence saved: ${record.title}`);U.toast(root,'Saved to evidence inbox.')});
el.querySelector('[data-cite-note]').addEventListener('click',()=>{projects.add('notes',{type:'source-citation',title:record.title,body:`Source: ${record.source}\nURL: ${record.url||''}\nObserved: ${record.observedAt||''}\n\n${record.summary||record.abstract||''}`,tags:['source',String(record.domain||'science').toLowerCase()]},`Notebook citation added: ${record.title}`);U.toast(root,'Citation added to notebook.')});return el}
function render(target,records,projects,root){target.innerHTML='';if(!records?.length){target.innerHTML='<div class="sc-lab-data-note">No records returned.</div>';return}records.forEach(r=>target.appendChild(card(r,projects,root)))}
Lab.Feeds={load,render};
})(window);
