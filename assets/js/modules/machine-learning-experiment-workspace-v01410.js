(function(w){'use strict';
const V='0.141.0';
const states=['draft','designed','ready-for-execution','submitted','running','completed','failed','cancelled','archived'];
const computeTargets=['cpu','mps','cuda','remote_gpu'];
const taskTypes=['classification','regression','ranking','embedding','sequence','forecasting','vision','multimodal','graph'];
function normalize(x){x=x||{};return {
  schema:'sc-lab-machine-learning-experiment-client/0.141.0',version:V,
  experimentId:x.experimentId||x.id||null,projectId:x.projectId||x.studyId||null,
  state:states.includes(x.state)?x.state:'draft',taskType:taskTypes.includes(x.taskType)?x.taskType:'classification',
  computeTarget:computeTargets.includes(x.computeTarget)?x.computeTarget:'cpu',
  workspaceExecutes:true,labExecutesTraining:false,predictionIsEvidence:false,
  automaticBestModelSelection:false,automaticScientificValidity:false
};}
function workspaceHandoff(x){const p=normalize(x);return Object.assign({},p,{schema:'sc-workspace-neural-execution-request/1.0',automaticExecution:false,executionAuthority:'workspace'});}
w.SCLabMachineLearningExperimentWorkspaceV01410={version:V,states:states.slice(),computeTargets:computeTargets.slice(),taskTypes:taskTypes.slice(),normalize,workspaceHandoff};
})(window);
