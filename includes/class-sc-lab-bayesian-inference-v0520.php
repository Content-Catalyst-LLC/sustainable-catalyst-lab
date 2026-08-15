<?php
/** Sustainable Catalyst Lab v0.52.0 — Bayesian Inference, Posterior Diagnostics & Posterior Predictive Modeling. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Bayesian_Inference_V0520 {
    const VERSION='0.52.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/bayesian/v0520/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/bayesian/v0520/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'studySchema'=>'sc-lab-bayesian-study/0.52.0','resultSchema'=>'sc-lab-bayesian-result/0.52.0','posteriorPredictiveSchema'=>'sc-lab-posterior-predictive/0.52.0',
        'families'=>array('gaussian','binomial-logit','poisson-log'),'modelTypes'=>array('linear','cubic-spline'),
        'priors'=>array('normal-coefficients','inverse-gamma-residual-variance','term-specific-normal-priors'),
        'diagnostics'=>array('split-rhat','autocorrelation-ess','mcse','acceptance-rate','trace'),
        'posteriorPredictive'=>true,'arbitraryCode'=>false,'automaticConvergenceCertification'=>false,
    ));}
    public static function health(){
        $required=array(
            'backend/app/bayesian_inference.py','backend/tests/test_bayesian_inference_v0520.py',
            'assets/js/modules/bayesian-inference-v0520.js','assets/css/sc-lab-bayesian-inference-v0520.css',
            'contracts/bayesian-study-v0520.schema.json','contracts/bayesian-result-v0520.schema.json','contracts/bayesian-policy-v0520.json','templates/lab-app.php'
        );$files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'bayesian-inference-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'gaussianBayesianRegression'=>true,'bayesianLogisticRegression'=>true,'bayesianPoissonRegression'=>true,'cubicSplines'=>true,
            'posteriorDiagnostics'=>true,'posteriorPredictiveModeling'=>true,'reproduciblePackageCompatible'=>true,'sharedGraphEngine'=>true,
            'arbitraryCode'=>false,'automaticConvergenceCertification'=>false,'automaticCausalClaims'=>false,'automaticPriorSelection'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
