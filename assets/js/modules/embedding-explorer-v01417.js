(function(w){'use strict';
const NS='SCLabEmbeddingExplorerV01417';
function embeddings(results){return Array.isArray(results?.embeddings)?results.embeddings:[];}
function projectionPoints(projection){return Array.isArray(projection?.points)?projection.points:[];}
function neighborLabel(x){return `${x?.label||x?.embeddingId||'embedding'}${Number.isFinite(x?.distance)?` · ${x.distance.toFixed(4)}`:''}`;}
function projectionBadge(x){return x?.derivedRepresentation===true?'derived projection':'source geometry';}
w[NS]={version:'0.141.7',embeddings,projectionPoints,neighborLabel,projectionBadge,workspaceExecutionAuthority:true,labExecutesEmbeddingExtraction:false,labExecutesDimensionalityReduction:false,nearestNeighborIsRelationship:false,clusterMeaningInferred:false,semanticRelationshipInferred:false,projectionFaithfulnessCertified:false,automaticModelEndorsement:false,embeddingIsEvidence:false,boundary:'Embedding proximity, neighborhood membership, clusters, and projected layout are analytical geometry; they are not evidence of a real-world relationship or semantic truth by themselves.'};
})(window);
