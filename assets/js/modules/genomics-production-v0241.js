(() => {
'use strict';
const W=typeof window!=='undefined'?window:globalThis,Lab=W.SCLab=W.SCLab||{};
const VERSION='0.24.1',ENGINE_VERSION='0.24.0',PANEL='genetics-genomics-sequence-analysis',ROOT='[data-genetics-genomics-root]';
const state={attempts:0,repairs:0,duplicatesRemoved:0,lastError:null,lastReason:null,observerActive:false};
function engine(){return Lab.GeneticsGenomicsSequenceAnalysis;}
function roots(){return typeof document==='undefined'?[]:[...document.querySelectorAll(ROOT)];}
function panel(){return typeof document==='undefined'?null:document.querySelector(`[data-lab-module="${PANEL}"],[data-module-panel="${PANEL}"]`);}
function repair(reason='manual'){
 state.attempts++;state.lastReason=reason;
 if(typeof document==='undefined')return false;
 let p=panel();
 if(!p){state.lastError='Genomics panel not found.';return false;}
 p.classList.add('sc-lab-panel','sc-lab-module');p.dataset.labModule=PANEL;p.dataset.modulePanel=PANEL;
 let all=roots();let root=all.find(x=>x.querySelector('.sc-genomics-shell'))||all[0];
 if(!root){root=document.createElement('div');root.setAttribute('data-genetics-genomics-root','');p.appendChild(root);all=[root];}
 for(const dup of all){if(dup!==root){dup.remove();state.duplicatesRemoved++;}}
 if(!root.querySelector('.sc-genomics-shell')){
   root.innerHTML=`<section class="sc-genomics-shell"><header><p>LAB/GENOMICS</p><h3>Genetics, Genomics, and Sequence Analysis</h3><p>48 deterministic research methods are active. Use the focused calculator, visualization, and validation workspaces for analysis.</p></header><pre>${JSON.stringify(engine()?.status?.()||{},null,2)}</pre><p class="sc-genomics-boundary">Research and education only. Not for clinical variant interpretation or regulated reporting.</p></section>`;
 }
 root.dataset.scGenomicsProductionVersion=VERSION;state.repairs++;state.lastError=null;return true;
}
function scheduleRepair(reason){[0,80,220,600,1400,3000].forEach(d=>W.setTimeout(()=>repair(reason),d));}
function open(){const p=panel();if(!p)return false;p.hidden=false;p.removeAttribute('hidden');scheduleRepair('open');return true;}
function health(){const e=engine(),all=roots(),rendered=all.filter(x=>x.querySelector('.sc-genomics-shell'));const ready=e?.definitions?.length===48&&e?.benchmarks?.length===48&&e?.categories?.length===8&&all.length===1&&rendered.length===1;return{ok:ready,status:ready?'ready':'repair-required',release:VERSION,engineRelease:ENGINE_VERSION,methodCount:e?.definitions?.length||0,benchmarkCount:e?.benchmarks?.length||0,categoryCount:e?.categories?.length||0,rootCount:all.length,renderedRootCount:rendered.length,attempts:state.attempts,repairs:state.repairs,duplicatesRemoved:state.duplicatesRemoved,lastReason:state.lastReason,lastError:state.lastError,observerActive:state.observerActive};}
function init(){scheduleRepair('startup');if(typeof document!=='undefined'){document.addEventListener('click',e=>{if(e.target?.closest?.(`[data-lab-target="${PANEL}"],[data-module-target="${PANEL}"]`))scheduleRepair('navigation-click');});document.addEventListener('sc-lab:module-opened',()=>scheduleRepair('module-opened'));if(typeof MutationObserver!=='undefined'){const o=new MutationObserver(()=>repair('mutation'));o.observe(document.documentElement,{childList:true,subtree:true});state.observerActive=true;}}if(W.addEventListener){for(const ev of ['pageshow','focus','popstate','hashchange'])W.addEventListener(ev,()=>scheduleRepair(ev));}}
Lab.GenomicsProduction={VERSION,ENGINE_VERSION,repair,scheduleRepair,open,health,status:health,state};
if(typeof document!=='undefined'){document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init,{once:true}):init();}
})();
