<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Embedding_Explorer_V01417 {
    const VERSION='0.141.7';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/embedding-explorer/v01417/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/embedding-explorer/v01417/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/embedding-explorer/v01417/catalog',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'catalog'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'embeddingExplorer'=>true,'neuralExplainabilityWorkspaceVersion'=>'0.141.6',
        'ablationStudyFrameworkVersion'=>'0.141.5','hyperparameterStudySearchResultsVersion'=>'0.141.4','modelComparisonExperimentMatrixVersion'=>'0.141.3',
        'trainingCurvesMetricsCheckpointVisualizationVersion'=>'0.141.2','neuralArchitectureTrainingConfigurationVersion'=>'0.141.1',
        'machineLearningExperimentWorkspaceVersion'=>'0.141.0','manifestIntegrityBaseline'=>'0.140.0.1','workspaceExecutionAuthority'=>true,
        'labExecutesEmbeddingExtraction'=>false,'labExecutesDimensionalityReduction'=>false,'nearestNeighborIsRelationship'=>false,
        'clusterMeaningInferred'=>false,'semanticRelationshipInferred'=>false,'projectionFaithfulnessCertified'=>false,
        'automaticModelEndorsement'=>false,'embeddingIsEvidence'=>false)); }
    public static function acceptance(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'embeddingStudy'=>true,'workspaceExecutionHandoff'=>true,'embeddingNormalization'=>true,
        'vectorRegistry'=>true,'provenanceAudit'=>true,'dimensionalityAudit'=>true,'distanceMatrix'=>true,'neighborhoodQuery'=>true,
        'projectionRegistry'=>true,'projectionAudit'=>true,'clusterOverlay'=>true,'driftComparison'=>true,'spaceComparison'=>true,
        'visualSpecs'=>true,'coreVisualHandoff'=>true,'deterministicSnapshots'=>true,'reproducibilityPackages'=>true,
        'semanticRelationshipInferred'=>false,'projectionFaithfulnessCertified'=>false,'embeddingIsEvidence'=>false)); }
    public static function catalog(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'embeddingKinds'=>array('input','token','sentence','document','image','audio','graph-node','entity','multimodal','other'),
        'distanceMetrics'=>array('cosine','euclidean','manhattan','dot-product'),
        'projectionMethods'=>array('pca','tsne','umap','pacmap','random-projection','user-supplied','other'),
        'views'=>array('projection','neighborhood','distance-matrix','cluster-overlay','label-overlay','drift-comparison','space-comparison','provenance-matrix'))); }
}
SC_Lab_Embedding_Explorer_V01417::init();
