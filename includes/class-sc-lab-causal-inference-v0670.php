<?php
/** Sustainable Catalyst Lab v0.67.0 — Causal Inference & Quasi-Experimental Methods. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Causal_Inference_V0670 {
    const VERSION='0.67.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/causal-inference/v0670/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/causal-inference/v0670/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'designSchema'=>'sc-lab-causal-design/0.67.0','estimateSchema'=>'sc-lab-causal-estimate/0.67.0','diagnosticSchema'=>'sc-lab-causal-diagnostic/0.67.0','packetSchema'=>'sc-lab-causal-inference-packet/0.67.0'));}
    public static function health(){
        $required=array('backend/app/causal_inference_v0670.py','backend/tests/test_causal_inference_v0670.py','assets/js/modules/causal-inference-v0670.js','assets/css/sc-lab-causal-inference-v0670.css','contracts/causal-design-v0670.schema.json','contracts/causal-estimate-v0670.schema.json','contracts/causal-diagnostic-v0670.schema.json','contracts/causal-inference-packet-v0670.schema.json','contracts/causal-inference-policy-v0670.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'causal-inference-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'matching'=>true,'weighting'=>true,'differenceInDifferences'=>true,'interruptedTimeSeries'=>true,'regressionDiscontinuity'=>true,'identificationAssumptionsExplicit'=>true,'methodDiagnosticsExplicit'=>true,'sensitivityRequired'=>true,'humanCausalReviewRequired'=>true,'automaticCausalProof'=>false,'automaticAssumptionSatisfaction'=>false,'rawScientificDataAccepted'=>false,'participantLevelDataAccepted'=>false,'networkFetchDuringEvaluation'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
