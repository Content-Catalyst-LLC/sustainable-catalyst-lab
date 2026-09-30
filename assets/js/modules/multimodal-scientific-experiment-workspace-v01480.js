(function(w){'use strict';
const VERSION='0.148.0';
function arr(v){return Array.isArray(v)?v.slice():[];} function obj(v){return v&&typeof v==='object'&&!Array.isArray(v)?Object.assign({},v):{};}
function source(x){x=obj(x);return Object.assign({},x,{version:VERSION,originalSourcePreserved:true,derivedRepresentation:x.derivedRepresentation===true});}
function alignment(x){x=obj(x);return Object.assign({},x,{version:VERSION,semanticEquivalenceEstablished:false,physicalIdentityEstablished:false});}
function output(x){x=obj(x);return Object.assign({},x,{version:VERSION,predictionIsEvidence:false,semanticEquivalenceEstablished:false});}
function normalizeStudy(x){x=obj(x);return Object.assign({},x,{version:VERSION,samples:arr(x.samples),alignments:arr(x.alignments).map(alignment),model:obj(x.model),runs:arr(x.runs),outputs:arr(x.outputs).map(output),originalSourcesPreserved:true,derivedRepresentationsRemainDerived:true,automaticSemanticEquivalence:false,automaticModelRanking:false,automaticWinnerSelection:false,automaticScientificValidity:false,predictionIsEvidence:false,crossModalSimilarityIsEvidence:false});}
w.SCLabMultimodalScientificExperimentWorkspaceV01480={version:VERSION,workspaceExecutionAuthority:true,workbenchPrototypeExecutionAuthority:true,platformCoreCanonicalAuthority:true,labExecutesMultimodalTraining:false,labExecutesMultimodalInference:false,originalSourcesPreserved:true,derivedRepresentationsRemainDerived:true,automaticSemanticEquivalence:false,automaticModelRanking:false,automaticWinnerSelection:false,automaticScientificValidity:false,predictionIsEvidence:false,crossModalSimilarityIsEvidence:false,source:source,alignment:alignment,output:output,normalizeStudy:normalizeStudy};
})(window);
