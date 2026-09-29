<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Ablation_Study_Framework_V01415 {
    const VERSION='0.141.5';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/ablation-study-framework/v01415/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/ablation-study-framework/v01415/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/ablation-study-framework/v01415/catalog',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'catalog'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'ablationStudyFramework'=>true,'hyperparameterStudySearchResultsVersion'=>'0.141.4','modelComparisonExperimentMatrixVersion'=>'0.141.3','trainingCurvesMetricsCheckpointVisualizationVersion'=>'0.141.2','neuralArchitectureTrainingConfigurationVersion'=>'0.141.1','machineLearningExperimentWorkspaceVersion'=>'0.141.0','manifestIntegrityBaseline'=>'0.140.0.1','workspaceExecutionAuthority'=>true,'labExecutesTraining'=>false,'controlledContrastRequired'=>true,'causalEffectInferred'=>false,'automaticRanking'=>false,'automaticWinnerSelection'=>false,'automaticModelPromotion'=>false,'predictionIsEvidence'=>false)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'ablationPlan'=>true,'workspaceExecutionHandoff'=>true,'variantRegistry'=>true,'baselineAudit'=>true,'comparabilityAudit'=>true,'pairedDeltaMatrix'=>true,'componentEffectSummary'=>true,'replicateSummary'=>true,'interactionGuardrail'=>true,'confoundingAudit'=>true,'candidateReview'=>true,'visualSpecs'=>true,'coreVisualHandoff'=>true,'deterministicSnapshots'=>true,'reproducibilityPackages'=>true,'causalEffectInferred'=>false,'automaticWinnerSelection'=>false)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'actions'=>array('remove','disable','replace','freeze','mask','zero','reparameterize','other'),'views'=>array('variant-matrix','metric-delta-matrix','component-effect-summary','replicate-distribution','interaction-summary','failure-audit','provenance-matrix'))); }
}
SC_Lab_Ablation_Study_Framework_V01415::init();
