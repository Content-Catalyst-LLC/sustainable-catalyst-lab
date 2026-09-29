(function(w){'use strict';
const NS='SCLabNeuralExplainabilityWorkspaceV01416';
function explanations(results){return Array.isArray(results?.explanations)?results.explanations:[];}
function attributionRows(matrix){return Array.isArray(matrix?.rows)?matrix.rows:[];}
function methodLabel(x){const m=x?.method||{};return `${m.family||'method'}${m.version?` · ${m.version}`:''}`;}
function explanationBadge(x){return x?.explanationFaithfulnessCertified===true?'certified':'interpret with method context';}
w[NS]={version:'0.141.6',explanations,attributionRows,methodLabel,explanationBadge,workspaceExecutionAuthority:true,labExecutesExplanationCompute:false,causalMechanismInferred:false,explanationFaithfulnessCertified:false,automaticExplanationRanking:false,automaticConsensus:false,automaticModelEndorsement:false,explanationIsEvidence:false,boundary:'Attributions and saliency are method-dependent analytical outputs; they are not causal mechanisms, model validation, or scientific evidence by themselves.'};
})(window);
