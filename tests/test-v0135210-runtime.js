const fs=require('fs'),vm=require('vm');
class E{constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.disabled=false;this.parentNode=null;this.listeners={};this._innerHTML='';this._selectors={}}set innerHTML(v){this._innerHTML=v;this._selectors={};for(const key of ['hydrate','certify','save','context','status']){const e=new E(key==='status'?'span':'button');if(key==='save')e.disabled=true;this._selectors[`[data-gs135210-${key}]`]=e}}get innerHTML(){return this._innerHTML}appendChild(x){x.parentNode=this;this.children.push(x);return x}prepend(x){x.parentNode=this;this.children.unshift(x);return x}remove(){}addEventListener(k,f){this.listeners[k]=f}querySelector(s){if(s==='[data-gs135210-bar]')return this.children.find(x=>x.dataset.gs135210Bar!==undefined)||null;return this._selectors[s]||null}querySelectorAll(s){if(s==='[data-gs135210-bar]')return this.children.filter(x=>x.dataset.gs135210Bar!==undefined);return[]}closest(s){return s==='.sc-lab-app'?this._app||null:null}}
const app=new E('div');app._scLabProjects={activeProjectId:'p1',list(name){return name==='graphStudioReviewThreads'?[{id:'t2'},{id:'t1'}]:[]},add(){},update(){}};
const root=new E(),stage=new E(),host=new E();root._app=app;host.querySelector=s=>s==='[data-gs13583-stage]'?stage:null;
const listeners={};const document={readyState:'complete',querySelector:s=>s==='[data-lab-module="graph-studio"]'?root:null,getElementById:id=>id==='sc-lab-graph-studio-renderer-root'?host:null,createElement:t=>new E(t),addEventListener(k,f){(listeners[k]??=[]).push(f)},dispatchEvent(){}};
const Lab={GraphStudioRendererReplacementV013582:{version:'0.135.8.2'},GraphStudioNativeProvenanceV013585:{version:'0.135.8.5.3'}};
const window={SCLab:Lab,SCLabGraphStudioReviewClosureV0135200:{version:'0.135.20.0'},sessionStorage:{setItem(){},getItem(){return null}}};global.CustomEvent=function(){};
vm.runInNewContext(fs.readFileSync('assets/js/modules/graph-studio-review-workspace-consolidation-v0135210.js','utf8'),{window,document,CustomEvent:global.CustomEvent,console,setTimeout,Date,Math,JSON,Object,Array,String});
const a=window.SCLabGraphStudioReviewWorkspaceConsolidationV0135210;if(!a||a.version!=='0.135.21.0')throw Error('API missing');
const one=a.hydrate(),two=a.hydrate();if(one.stateDigest!==two.stateDigest)throw Error('digest not deterministic');
const cert=a.certify();if(!cert.certified||cert.fullGraphRedraw!==false)throw Error('certification failed');
if(stage.querySelectorAll('[data-gs135210-bar]').length!==1)throw Error('duplicate consolidated toolbar');
if(a.state.listenerBindings!==1)throw Error('listener binding not singular');
const ac=a.acceptance();if(ac.automaticScientificValidity!==false||ac.automaticPublicationAcceptance!==false)throw Error('scientific boundary failure');
console.log('PASS: v0.135.21.0 JS runtime contract');
