(function(W,D){'use strict';
const Lab=W.SCLab=W.SCLab||{},VERSION='0.48.3',PREF_KEY='scLabNavigationV0483';
const contexts={
 project:{label:'Project',primary:'overview',items:[['overview','Overview'],['project-workspace','Architecture'],['dataset-registry','Datasets'],['research-provenance','Provenance'],['activity','Activity']]},
 model:{label:'Model Studio',primary:'model-studio',items:[['model-studio','Define'],['model-calibration','Calibration'],['design-studies','Design studies'],['probabilistic-analysis','Uncertainty'],['model-registry','Registry'],['ensemble-uncertainty','Ensembles'],['surrogate-reduced-order','Surrogates']]},
 graph:{label:'Graph Studio',primary:'graph-studio',items:[['graph-studio','Figures'],['numerical-visualization','Scientific visualization'],['visualization-studio','Visualization & export']]},
 experiment:{label:'Experiments',primary:'experiments',items:[['experiments','Experiments'],['experiment-framework','Framework'],['reproducible-runs','Reproducible runs'],['experiment-campaigns','Campaigns'],['closed-loop-campaigns','Closed loop']]},
 observe:{label:'Observations',primary:'scientific-feeds',items:[['scientific-feeds','Observation board'],['climate-maps','Climate maps'],['space-telescopes','Space & astronomy'],['marine-biology','Marine biology']]},
 record:{label:'Research record',primary:'notebook',items:[['notebook','Notebook'],['evidence-decisions','Evidence'],['report-studio','Reports'],['documentation','Documentation'],['manuscript-assembly','Manuscript']]}
};
const moduleContext={};Object.keys(contexts).forEach(key=>contexts[key].items.forEach(([id])=>{if(!(id in moduleContext))moduleContext[id]=key;}));
const q=(r,s)=>r&&r.querySelector(s),qa=(r,s)=>Array.from((r||D).querySelectorAll(s));
function readPrefs(){try{return JSON.parse(localStorage.getItem(PREF_KEY)||'{}')||{}}catch(_){return{}}}
function writePrefs(next){try{localStorage.setItem(PREF_KEY,JSON.stringify(next))}catch(_){}}
function contextFor(module){return moduleContext[module]||null}
function renderContext(root,module){const bar=q(root,'[data-v0483-context-nav]'),label=q(bar,'[data-v0483-context-label]'),items=q(bar,'[data-v0483-context-items]');if(!bar||!items)return;const key=contextFor(module);if(!key){bar.hidden=true;items.innerHTML='';return;}const ctx=contexts[key];bar.hidden=false;if(label)label.textContent=ctx.label;items.innerHTML=ctx.items.map(([id,text])=>`<button type="button" data-open-module="${id}"${id===module?' class="is-active" aria-current="page"':''}>${text}</button>`).join('');}
function updatePrimary(root,module){const key=contextFor(module),primary=key?contexts[key].primary:(module==='overview'?'overview':null);qa(root,'[data-v0483-primary]').forEach(btn=>{const on=btn.dataset.v0483Primary===primary;btn.classList.toggle('is-active',on);if(on)btn.setAttribute('aria-current','page');else btn.removeAttribute('aria-current');});const more=q(root,'[data-v0483-tools-toggle]');if(more)more.classList.toggle('is-active',!primary&&module!=='overview');}
function setTools(root,open){const drawer=q(root,'[data-v0483-tools]'),toggle=q(root,'[data-v0483-tools-toggle]');if(!drawer)return;drawer.hidden=!open;root.classList.toggle('is-tools-open-v0483',open);if(toggle)toggle.setAttribute('aria-expanded',String(open));if(open){const input=q(drawer,'[data-v0483-tools-search]');requestAnimationFrame(()=>input&&input.focus());}}
function filterTools(root,value){const term=String(value||'').toLowerCase().trim();qa(root,'[data-v0483-tools] [data-lab-nav-group]').forEach(group=>{let count=0;qa(group,'[data-lab-module-button]').forEach(btn=>{const show=!term||btn.textContent.toLowerCase().includes(term)||String(btn.dataset.labModuleButton||'').toLowerCase().includes(term);btn.hidden=!show;if(show)count++;});group.hidden=count===0;if(term&&count)group.classList.remove('is-collapsed');});}
function setCollapsed(root,collapsed){root.classList.toggle('is-rail-collapsed-v0483',collapsed);const btn=q(root,'[data-v0483-rail-collapse]');if(btn){btn.setAttribute('aria-pressed',String(collapsed));const label=q(btn,'.sc-lab-rail-label-v0483');if(label)label.textContent=collapsed?'Expand rail':'Collapse rail';const icon=q(btn,'span[aria-hidden]');if(icon)icon.textContent=collapsed?'⇥':'⇤';}writePrefs({...readPrefs(),collapsed});}
function initialize(root){if(!root||root.dataset.v0483NavigationReady==='1')return;root.dataset.v0483NavigationReady='1';root.dataset.labNavigationVersion=VERSION;const prefs=readPrefs();setCollapsed(root,!!prefs.collapsed);const active=root.dataset.activeModule||root.dataset.initialModule||'overview';renderContext(root,active);updatePrimary(root,active);
 const toolsToggle=q(root,'[data-v0483-tools-toggle]'),toolsClose=q(root,'[data-v0483-tools-close]'),toolsSearch=q(root,'[data-v0483-tools-search]'),railCollapse=q(root,'[data-v0483-rail-collapse]'),search=q(root,'[data-v0483-search]');
 toolsToggle&&toolsToggle.addEventListener('click',()=>setTools(root,q(root,'[data-v0483-tools]')?.hidden!==false));
 toolsClose&&toolsClose.addEventListener('click',()=>setTools(root,false));
 toolsSearch&&toolsSearch.addEventListener('input',()=>filterTools(root,toolsSearch.value));
 railCollapse&&railCollapse.addEventListener('click',()=>setCollapsed(root,!root.classList.contains('is-rail-collapsed-v0483')));
 search&&search.addEventListener('click',()=>{const input=q(root,'[data-lab-command-input]');if(input){input.focus();input.select();}if(W.innerWidth<=980)q(root,'[data-lab-nav]')?.classList.remove('is-open');});
 root.addEventListener('sc-lab:module-opened',ev=>{const module=ev.detail?.module||root.dataset.activeModule||'overview';renderContext(root,module);updatePrimary(root,module);setTools(root,false);});
 root.addEventListener('click',ev=>{if(ev.target.closest('[data-v0483-tools] [data-lab-module-button]'))setTools(root,false);});
 D.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&!q(root,'[data-v0483-tools]')?.hidden)setTools(root,false);});
}
function boot(ev){const explicit=ev?.detail?.root;if(explicit)initialize(explicit);else qa(D,'.sc-lab-app').forEach(initialize)}
D.addEventListener('sc-lab:app-ready',boot);if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
Lab.ContextualNavigationV0483={version:VERSION,contexts,initialize};
})(window,document);
