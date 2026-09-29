(function(w,d){'use strict';
function api(){return w.SCLabSimulationComputationalExperimentWorkspaceV01450||null;}
function hydrate(state){const a=api();return a?a.normalizeExperiment(state):state||{};}
function selectPanel(state,panel){const s=hydrate(state);s.activePanel=String(panel||'design');return s;}
function viewModel(state){const s=hydrate(state);return {version:'0.145.0',experiment:s,activePanel:s.activePanel||'design',scenarioCount:(s.scenarios||[]).length,runCount:(s.runs||[]).length,ensembleCount:(s.ensembles||[]).length,verificationValidationSeparated:true,modeledOutputIsEvidence:false,automaticPreferredScenario:false,scientificValidityCertified:false};}
w.SCLabProjectWorkspaceSimulationV01450={version:'0.145.0',hydrate:hydrate,selectPanel:selectPanel,viewModel:viewModel};
})(window,document);
