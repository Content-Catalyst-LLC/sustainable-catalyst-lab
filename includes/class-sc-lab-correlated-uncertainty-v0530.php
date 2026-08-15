<?php
/** Sustainable Catalyst Lab v0.53.0 — Correlated Uncertainty & Probabilistic Dependency Models. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Correlated_Uncertainty_V0530 {
    const VERSION='0.53.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/correlated-uncertainty/v0530/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/correlated-uncertainty/v0530/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'studySchema'=>'sc-lab-dependent-probabilistic-study/0.53.0','resultSchema'=>'sc-lab-dependent-probabilistic-analysis/0.53.0','dependencySchema'=>'sc-lab-probabilistic-dependency/0.53.0',
        'dependencyMethods'=>array('independent','gaussian-copula'),'matrixTypes'=>array('correlation','covariance'),'marginalDistributions'=>array('uniform','normal','lognormal','triangular'),
        'dependentSaltelliSobol'=>false,'automaticDependencyInference'=>false,'automaticCausalInterpretation'=>false,'arbitraryCode'=>false
    ));}
    public static function health(){
        $required=array('backend/app/correlated_uncertainty.py','backend/tests/test_correlated_uncertainty_v0530.py','assets/css/sc-lab-correlated-uncertainty-v0530.css','contracts/dependent-probabilistic-study-v0530.schema.json','contracts/dependent-probabilistic-analysis-v0530.schema.json','contracts/probabilistic-dependency-v0530.schema.json','contracts/correlated-uncertainty-policy-v0530.json','templates/lab-app.php');$files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'correlated-uncertainty-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'correlationMatrices'=>true,'covarianceMatrices'=>true,'gaussianCopula'=>true,'dependencyHeatmap'=>true,'empiricalDependencyEstimation'=>true,'dependentSaltelliSobol'=>false,'automaticDependencyInference'=>false,'automaticCausalInterpretation'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
