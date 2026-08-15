<?php
/** Sustainable Catalyst Lab v0.51.0 — Advanced Statistical Modeling & Generalized Regression. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Advanced_Statistical_Modeling_V0510 {
    const VERSION='0.51.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/statistics/v0510/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/statistics/v0510/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'studySchema'=>'sc-lab-statistical-model-study/0.51.0','resultSchema'=>'sc-lab-statistical-model-result/0.51.0',
        'families'=>array('gaussian','binomial-logit','poisson-log'),
        'estimators'=>array('ols','weighted-least-squares','huber','ridge','lasso','elastic-net','glm'),
        'cubicSplines'=>true,'crossValidation'=>true,'comparison'=>true,'arbitraryCode'=>false,
    ));}
    public static function health(){
        $required=array(
            'backend/app/advanced_statistical_modeling.py','backend/tests/test_advanced_statistical_modeling_v0510.py',
            'assets/js/modules/advanced-statistical-modeling-v0510.js','assets/css/sc-lab-advanced-statistical-modeling-v0510.css',
            'contracts/statistical-model-result-v0510.schema.json','contracts/statistical-model-policy-v0510.json','templates/lab-app.php'
        );$files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'advanced-statistical-modeling-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'gaussianRegression'=>true,'robustRegression'=>true,'regularizedRegression'=>true,'generalizedLinearModels'=>true,'cubicSplines'=>true,
            'crossValidation'=>true,'modelComparison'=>true,'reproduciblePackageCompatible'=>true,'sharedGraphEngine'=>true,
            'arbitraryCode'=>false,'automaticCausalClaims'=>false,'automaticFeatureSelection'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
