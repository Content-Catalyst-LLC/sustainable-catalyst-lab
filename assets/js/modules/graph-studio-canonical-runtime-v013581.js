/* Sustainable Catalyst Lab v0.135.8.1 — Graph Studio Canonical Runtime & Interface Recovery */
(function(W,D){'use strict';
const VERSION='0.135.8.1';
const ROOT_SEL='[data-lab-module="graph-studio"]';
const VIEW_ORDER=['figure','analysis','provenance','scene','compare','session','narrative','review'];
const VIEW_LABELS={figure:'Figure',analysis:'Analysis',provenance:'Provenance',scene:'Scene',compare:'Compare',session:'Session',narrative:'Narrative',review:'Review'};
const CAPABILITIES=[
 ['binding','.sc-gs0750-binding','Data binding'],['adaptive','.sc-gs0760-adaptive','Large data'],['scene-engine','.sc-gs0770-scene','3D scene'],['state','.sc-gs0780-state','4D state'],['linked','.sc-gs0790-compose','Linked views'],['spatial','.sc-gs0800-spatial','Spatial / raster'],['markup','.sc-gs0810-markup','Markup'],['uncertainty','.sc-gs0820-uncertainty','Uncertainty'],['provenance','.sc-gs0830-provenance','Figure provenance'],['gpu','.sc-gs0840-gpu','GPU plan'],['webgl2','.sc-gs0850-webgl','WebGL2'],['webgpu','.sc-gs0870-webgpu','WebGPU'],['advanced3d','.sc-gs0880','Advanced 3D']
];
const state={mounted:false,view:'figure',capability:null,root:null,observer:null};
const root=()=>D.querySelector(ROOT_SEL);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function storedView(){try{const v=W.sessionStorage?.getItem('sc-lab:graph-studio:view');return VIEW_ORDER.includes(v)?v:'figure'}catch(_){return 'figure'}}
function saveView(v){try{W.sessionStorage?.setItem('sc-lab:graph-studio:view',v)}catch(_){}}
function make(tag,cls,attrs={}){const n=D.createElement(tag);if(cls)n.className=cls;Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));return n}
function slot(shell,id){return shell.querySelector(`[data-gs13581-slot="${id}"]`)}
function ensureShell(r){
 const workspace=r.querySelector('.sc-gs0470-workspace'); if(!workspace)return null;
 let shell=workspace.querySelector('[data-gs13581-shell]'); if(shell)return shell;
 shell=make('section','sc-gs13581-shell',{'data-gs13581-shell':'','aria-label':'Graph Studio canonical scientific workspace'});
 shell.innerHTML=`<header class="sc-gs13581-command"><div class="sc-gs13581-identity"><span>GRAPH STUDIO · CANONICAL RUNTIME</span><strong>v${VERSION}</strong><small>one active research view · presentation state isolated</small></div><nav class="sc-gs13581-tabs" aria-label="Graph Studio research views">${VIEW_ORDER.map(v=>`<button type="button" data-gs13581-view="${v}" aria-pressed="false">${VIEW_LABELS[v]}</button>`).join('')}</nav><div class="sc-gs13581-runtime-state"><span data-gs13581-renderer>Primary renderer: SVG2D</span><span data-gs13581-owner>Owner: canonical runtime</span></div></header><div class="sc-gs13581-stage">${VIEW_ORDER.map(v=>`<section class="sc-gs13581-view" data-gs13581-slot="${v}" data-gs13581-view-panel="${v}" hidden></section>`).join('')}</div>`;
 const first=workspace.firstElementChild; workspace.insertBefore(shell,first||null);
 shell.addEventListener('click',e=>{const b=e.target.closest('[data-gs13581-view]');if(b)activateView(b.dataset.gs13581View);});
 return shell;
}
function moveIf(node,target){if(node&&target&&node.parentNode!==target)target.appendChild(node)}
function collectViews(r,shell){
 const workspace=r.querySelector('.sc-gs0470-workspace'); if(!workspace)return;
 moveIf(workspace.querySelector('.sc-gs0470-canvas-card'),slot(shell,'figure'));
 moveIf(workspace.querySelector('.sc-gs0470-library'),slot(shell,'figure'));
 const spec=workspace.querySelector('[data-gs-v0470-spec]'); moveIf(spec?spec.closest('details'):null,slot(shell,'figure'));
 moveIf(r.querySelector('[data-viz1351-experience-root]'),slot(shell,'analysis'));
 moveIf(r.querySelector('[data-viz1353-canvas-root]'),slot(shell,'analysis'));
 moveIf(r.querySelector('[data-viz1352-graph-root]'),slot(shell,'provenance'));
 moveIf(r.querySelector('[data-viz1354-scene-root]'),slot(shell,'scene'));
 moveIf(r.querySelector('[data-viz1355-context-root]'),slot(shell,'compare'));
 moveIf(r.querySelector('[data-viz1356-session-root]'),slot(shell,'session'));
 moveIf(r.querySelector('[data-viz1357-narrative-root]'),slot(shell,'narrative'));
 moveIf(r.querySelector('[data-viz1358-review-root]'),slot(shell,'review'));
}
function activateView(view){
 const r=state.root||root();if(!r)return;const shell=r.querySelector('[data-gs13581-shell]');if(!shell)return;
 if(!VIEW_ORDER.includes(view))view='figure';state.view=view;saveView(view);r.dataset.gs13581ActiveView=view;
 shell.querySelectorAll('[data-gs13581-view-panel]').forEach(p=>{const on=p.dataset.gs13581ViewPanel===view;p.hidden=!on;p.setAttribute('aria-hidden',on?'false':'true')});
 shell.querySelectorAll('[data-gs13581-view]').forEach(b=>{const on=b.dataset.gs13581View===view;b.classList.toggle('is-active',on);b.setAttribute('aria-pressed',on?'true':'false')});
 r.dispatchEvent(new CustomEvent('sc-lab:graph-studio-canonical-view',{bubbles:true,detail:{version:VERSION,view,presentationStateOnly:true,mutatesScience:false}}));
}
function capabilityDrawer(r){
 const controls=r.querySelector('.sc-gs0470-controls');if(!controls)return;
 let drawer=controls.querySelector('[data-gs13581-capabilities]');if(!drawer){
   drawer=make('details','sc-gs13581-capabilities',{'data-gs13581-capabilities':''});
   drawer.innerHTML='<summary><span>Advanced renderer & capability controls</span><small>isolated adapters · closed by default</small></summary><div class="sc-gs13581-cap-tabs" data-gs13581-cap-tabs></div><div class="sc-gs13581-cap-stage" data-gs13581-cap-stage></div>';
   const actions=[...controls.querySelectorAll('.sc-gs0470-card')].at(-1);controls.insertBefore(drawer,actions||null);
 }
 const tabs=drawer.querySelector('[data-gs13581-cap-tabs]'),stage=drawer.querySelector('[data-gs13581-cap-stage]');
 for(const [id,sel,label] of CAPABILITIES){const panel=r.querySelector(sel);if(!panel)continue;panel.dataset.gs13581Capability=id;panel.hidden=true;if(panel.parentNode!==stage)stage.appendChild(panel);if(!tabs.querySelector(`[data-gs13581-cap="${id}"]`)){const b=make('button','',{'type':'button','data-gs13581-cap':id,'aria-pressed':'false'});b.textContent=label;tabs.appendChild(b)}}
 if(!drawer.dataset.gs13581Bound){drawer.dataset.gs13581Bound='1';tabs.addEventListener('click',e=>{const b=e.target.closest('[data-gs13581-cap]');if(!b)return;activateCapability(r,b.dataset.gs13581Cap)});drawer.addEventListener('toggle',()=>{if(drawer.open&&!state.capability){const first=tabs.querySelector('[data-gs13581-cap]');if(first)activateCapability(r,first.dataset.gs13581Cap)}});}
}
function activateCapability(r,id){state.capability=id;r.dataset.gs13581ActiveCapability=id;r.querySelectorAll('[data-gs13581-capability]').forEach(p=>p.hidden=p.dataset.gs13581Capability!==id);r.querySelectorAll('[data-gs13581-cap]').forEach(b=>{const on=b.dataset.gs13581Cap===id;b.classList.toggle('is-active',on);b.setAttribute('aria-pressed',on?'true':'false')});}
function updateRuntimeState(r){
 const shell=r.querySelector('[data-gs13581-shell]');if(!shell)return;
 const badge=r.querySelector('[data-gs-v0730-renderer-badge]')?.textContent||'';const renderer=(badge.match(/SVG2D|Canvas2D|Canvas3D|Canvas4D|WebGL2|WebGPU/i)||['SVG2D'])[0];
 const rn=shell.querySelector('[data-gs13581-renderer]');if(rn)rn.textContent=`Primary renderer: ${renderer.toUpperCase()}`;
}
function quarantineDuplicatePresentation(r){
 r.classList.add('sc-gs13581-active');r.dataset.gs13581Runtime=VERSION;r.dataset.gs13581CanonicalOwner='graph-studio-canonical-runtime';r.dataset.gs13581ScientificMutation='off';
 // Historical capability adapters remain available but are not allowed to occupy the primary workspace.
 r.querySelectorAll('[data-gs13581-capability]').forEach(p=>p.setAttribute('data-gs13581-presentation-role','adapter'));
}
function repair(){const r=root();if(!r)return false;state.root=r;const shell=ensureShell(r);if(!shell)return false;collectViews(r,shell);capabilityDrawer(r);quarantineDuplicatePresentation(r);updateRuntimeState(r);activateView(state.view||storedView());return true}
function mount(){if(state.mounted&&state.root?.isConnected){repair();return true}state.view=storedView();if(!repair())return false;state.mounted=true;const r=state.root;let queued=false;state.observer=new MutationObserver(()=>{if(queued)return;queued=true;W.requestAnimationFrame(()=>{queued=false;collectViews(r,r.querySelector('[data-gs13581-shell]'));updateRuntimeState(r);activateView(state.view)})});state.observer.observe(r,{childList:true,subtree:true});D.addEventListener('sc-lab:module-unmounting',e=>{if(e.detail?.module==='graph-studio'){r.dispatchEvent(new CustomEvent('sc-lab:graph-studio-canonical-suspend',{detail:{version:VERSION}}))}});return true}
if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',mount);else mount();
W.SCLab=W.SCLab||{};W.SCLab.GraphStudioCanonicalRuntimeV013581={version:VERSION,mount,repair,activateView,activateCapability,status:()=>({mounted:state.mounted,view:state.view,capability:state.capability,canonicalOwner:'graph-studio-canonical-runtime',presentationStateOnly:true})};
})(window,document);
