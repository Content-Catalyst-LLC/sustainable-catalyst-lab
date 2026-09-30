(function(w){'use strict';
const VERSION='0.147.0';
function arr(v){return Array.isArray(v)?v.slice():[];} function obj(v){return v&&typeof v==='object'&&!Array.isArray(v)?Object.assign({},v):{};}
function prediction(p){p=obj(p);const task=String(p.taskType||'other');const candidate=task==='link-prediction'||p.candidateEdge===true;return Object.assign({},p,{taskType:task,candidateOnly:candidate,relationshipEstablished:candidate?false:null,evidenceEdgeCreated:false,predictionIsEvidence:false});}
function normalizeStudy(x){x=obj(x);return Object.assign({},x,{version:VERSION,task:obj(x.task),dataset:obj(x.dataset),split:obj(x.split),model:obj(x.model),runs:arr(x.runs),predictions:arr(x.predictions).map(prediction),automaticRelationshipEstablishment:false,automaticModelRanking:false,automaticWinnerSelection:false,automaticScientificValidity:false,predictionIsEvidence:false});}
function candidateLinks(rows){return arr(rows).map(x=>prediction(Object.assign({},x,{taskType:'link-prediction',candidateEdge:true})));}
w.SCLabGraphMachineLearningExperimentWorkspaceV01470={version:VERSION,workspaceExecutionAuthority:true,workbenchPrototypeExecutionAuthority:true,platformCoreCanonicalAuthority:true,labExecutesGraphMLTraining:false,labExecutesGraphMLInference:false,candidatePredictionsRemainCandidates:true,automaticRelationshipEstablishment:false,automaticModelRanking:false,automaticWinnerSelection:false,automaticScientificValidity:false,predictionIsEvidence:false,normalizeStudy:normalizeStudy,prediction:prediction,candidateLinks:candidateLinks};
})(window);
