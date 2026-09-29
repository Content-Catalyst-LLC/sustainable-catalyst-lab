(function(w){'use strict';
const V='0.141.0';
function handoff(experiment){const api=w.SCLabMachineLearningExperimentWorkspaceV01410;return api?api.workspaceHandoff(experiment||{}):{version:V,automaticExecution:false,executionAuthority:'workspace'};}
w.SCLabProjectWorkspaceMachineLearningV01410={version:V,handoff};
})(window);
