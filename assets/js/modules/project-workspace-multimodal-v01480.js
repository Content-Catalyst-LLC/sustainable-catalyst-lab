(function(w){'use strict';
function viewModel(study){study=(w.SCLabMultimodalScientificExperimentWorkspaceV01480||{}).normalizeStudy?w.SCLabMultimodalScientificExperimentWorkspaceV01480.normalizeStudy(study):study||{};return {version:'0.148.0',study:study,panels:['Study','Samples & Modalities','Alignment','Model & Fusion','Runs','Outputs','Evaluation','Explainability','Reproducibility'],originalSourcesPreserved:true,automaticSemanticEquivalence:false,predictionIsEvidence:false,crossModalSimilarityIsEvidence:false};}
w.SCLabProjectWorkspaceMultimodalV01480={version:'0.148.0',viewModel:viewModel};
})(window);
