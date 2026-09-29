(function(w){
'use strict';
const VERSION='0.141.1';
function fp(value){const s=JSON.stringify(value||{},Object.keys(value||{}).sort());let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return ('00000000'+(h>>>0).toString(16)).slice(-8);}
function normalizeArchitecture(input){const a=Object.assign({},input||{});a.architectureId=a.architectureId||('arch-'+fp(a));a.family=a.family||'custom';a.layers=Array.isArray(a.layers)?a.layers:[];a.edges=Array.isArray(a.edges)?a.edges:[];a.automaticArchitectureApproval=false;return a;}
function normalizeTraining(input){const c=Object.assign({},input||{});c.configurationId=c.configurationId||('traincfg-'+fp(c));c.optimizer=c.optimizer||{name:'adamw'};c.loss=c.loss||{name:'cross-entropy'};c.scheduler=c.scheduler||{name:'none'};c.precision=c.precision||'runtime-default';c.computeTarget=c.computeTarget||'cpu';c.labExecutesTraining=false;c.automaticModelPromotion=false;return c;}
w.SCLabNeuralArchitectureTrainingConfigurationV01411={version:VERSION,normalizeArchitecture,normalizeTraining,boundary:'Lab designs and compares configurations; Workspace executes; Core defines governed neural semantics; predictions are not evidence.'};
})(window);
