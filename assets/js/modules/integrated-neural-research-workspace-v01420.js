(function(w){'use strict';
const panels=[
 {id:'experiment',label:'Experiment Design & Runs',sourceVersion:'0.141.0'},
 {id:'architecture',label:'Architecture & Training',sourceVersion:'0.141.1'},
 {id:'telemetry',label:'Training Curves & Checkpoints',sourceVersion:'0.141.2'},
 {id:'comparison',label:'Model Comparison',sourceVersion:'0.141.3'},
 {id:'search',label:'Hyperparameter Search',sourceVersion:'0.141.4'},
 {id:'ablation',label:'Ablation Studies',sourceVersion:'0.141.5'},
 {id:'explainability',label:'Explainability',sourceVersion:'0.141.6'},
 {id:'embeddings',label:'Embeddings',sourceVersion:'0.141.7'},
 {id:'reproducibility',label:'Reproducibility',sourceVersion:'0.141.8'}
];
function safeArray(x){return Array.isArray(x)?x:[];}
function normalizeSession(x){x=x&&typeof x==='object'?x:{};const active=panels.some(p=>p.id===x.activePanel)?x.activePanel:'experiment';return {sessionId:String(x.sessionId||x.id||''),projectRef:String(x.projectRef||''),studyRef:String(x.studyRef||''),experimentRef:String(x.experimentRef||''),title:String(x.title||'Integrated neural research session'),state:String(x.state||'draft'),activePanel:active,focusedObjectId:String(x.focusedObjectId||''),pinnedObjectIds:safeArray(x.pinnedObjectIds).map(String),objects:safeArray(x.objects),limitations:safeArray(x.limitations),review:x.review&&typeof x.review==='object'?x.review:{}};}
function panelObjects(s,id){s=normalizeSession(s);return safeArray(s.objects).filter(o=>o&&o.panel===id);}
function panelCounts(s){const out={};panels.forEach(p=>out[p.id]=panelObjects(s,p.id).length);return out;}
function linkedRefs(o){if(!o||typeof o!=='object')return {};const keys=['runRef','experimentRef','datasetRef','modelRef','checkpointRef','provenanceRef'];const out={};keys.forEach(k=>{if(o[k])out[k]=o[k];});return out;}
w.SCLabIntegratedNeuralResearchWorkspaceV01420={version:'0.142.0',panels:panels,panelCount:9,workspaceExecutionAuthority:true,platformCoreCanonicalAuthority:true,labExecutesTraining:false,labExecutesSearch:false,labExecutesExplainabilityCompute:false,labExecutesEmbeddingExtraction:false,labExecutesReproduction:false,automaticWorkflowAdvance:false,automaticModelPromotion:false,automaticScientificValidity:false,predictionIsEvidence:false,normalizeSession:normalizeSession,panelObjects:panelObjects,panelCounts:panelCounts,linkedRefs:linkedRefs};
})(window);
