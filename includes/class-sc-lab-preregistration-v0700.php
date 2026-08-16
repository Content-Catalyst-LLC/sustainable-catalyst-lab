<?php
/** Sustainable Catalyst Lab v0.70.0 — Research Questions, Hypothesis Registry & Preregistration. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Preregistration_V0700 {
    const VERSION='0.70.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/preregistration/v0700/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/preregistration/v0700/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'researchQuestionSchema'=>'sc-lab-research-question/0.70.0','hypothesisRegistrySchema'=>'sc-lab-hypothesis-registry/0.70.0','preregistrationSchema'=>'sc-lab-preregistration/0.70.0','deviationSchema'=>'sc-lab-preregistration-deviation/0.70.0','freezeSchema'=>'sc-lab-preregistration-freeze/0.70.0','packetSchema'=>'sc-lab-preregistration-packet/0.70.0'));}
    public static function health(){
        $required=array('backend/app/preregistration_v0700.py','backend/tests/test_preregistration_v0700.py','assets/js/modules/preregistration-v0700.js','assets/css/sc-lab-preregistration-v0700.css','contracts/research-question-v0700.schema.json','contracts/hypothesis-registry-v0700.schema.json','contracts/preregistration-v0700.schema.json','contracts/preregistration-deviation-v0700.schema.json','contracts/preregistration-freeze-v0700.schema.json','contracts/preregistration-packet-v0700.schema.json','contracts/preregistration-policy-v0700.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'preregistration-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'researchQuestionRegistry'=>true,'hypothesisRegistry'=>true,'preResultFreezeRequired'=>true,'frozenSnapshotImmutable'=>true,'timestampedDeviationLogRequired'=>true,'humanPreregistrationReviewRequired'=>true,'automaticHypothesisValidation'=>false,'automaticPostHocPreregistration'=>false,'automaticOutcomeReclassification'=>false,'rawScientificDataAccepted'=>false,'participantLevelDataAccepted'=>false,'networkFetchDuringEvaluation'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
