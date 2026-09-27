/* Sustainable Catalyst Lab v0.137.0 — Research Change Impact & Living Analysis */
(function(W,D){'use strict';
const Lab=W.SCLab=W.SCLab||{},V='0.137.0',S={events:[],acknowledgements:[],mounted:false};
const uid=p=>`${p}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,8)}`;
function root(){return D.querySelector('[data-lab-module="graph-studio"]')}
function registerChange(x={}){const r={schema:'sc-lab-research-change-event/0.137.0',version:V,recordType:'research-change-event',collection:'graphStudioResearchChangeEvents',id:x.id||uid('change'),projectId:x.projectId||'unbound-project',objectId:String(x.objectId||'').trim(),objectType:x.objectType||'other',beforeRef:x.beforeRef||null,afterRef:x.afterRef||null,changeSummary:x.changeSummary||null,changedAt:x.changedAt||new Date().toISOString(),changedBy:x.changedBy||'user',boundary:'Declared dependency reachability only; human scientific review is required.'};if(!r.objectId)return false;S.events.push(r);dispatch();return r}
function acknowledge(x={}){if(!x.objectId||!x.action)return false;const r={id:x.id||uid('living-ack'),objectId:x.objectId,action:x.action,note:x.note||null,acknowledgedAt:new Date().toISOString(),scientificJudgment:'human'};S.acknowledgements.push(r);dispatch();return r}
function status(){return{version:V,mounted:S.mounted,changeEventCount:S.events.length,acknowledgementCount:S.acknowledgements.length,automaticScientificInvalidation:false,automaticTruthJudgment:false,automaticCausalInference:false}}
function dispatch(){root()?.dispatchEvent(new CustomEvent('sc-lab:living-analysis-state',{bubbles:true,detail:status()}))}
function mount(){S.mounted=true;dispatch();return true}
Lab.ResearchChangeImpactLivingAnalysisV01370={version:V,mount,registerChange,acknowledge,status};W.SCLabResearchChangeImpactLivingAnalysisV01370=Lab.ResearchChangeImpactLivingAnalysisV01370;
if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',mount);else mount();
})(window,document);
