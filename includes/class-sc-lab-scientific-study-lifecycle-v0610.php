<?php
/** Sustainable Catalyst Lab v0.61.0 — End-to-End Scientific Study & Research Project Lifecycle. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Study_Lifecycle_V0610 {
    const VERSION='0.61.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-studies/v0610/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-studies/v0610/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'studySchema'=>'sc-lab-scientific-study/0.61.0','lifecycleSchema'=>'sc-lab-scientific-study-lifecycle/0.61.0','reviewSchema'=>'sc-lab-scientific-study-stage-review/0.61.0','packetSchema'=>'sc-lab-scientific-study-evidence-packet/0.61.0'));}
    public static function health(){
        $required=array('backend/app/scientific_study_lifecycle_v0610.py','backend/tests/test_scientific_study_lifecycle_v0610.py','assets/js/modules/scientific-study-lifecycle-v0610.js','assets/css/sc-lab-scientific-study-lifecycle-v0610.css','contracts/scientific-study-v0610.schema.json','contracts/scientific-study-lifecycle-v0610.schema.json','contracts/scientific-study-stage-review-v0610.schema.json','contracts/scientific-study-evidence-packet-v0610.schema.json','contracts/scientific-study-lifecycle-policy-v0610.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-study-lifecycle-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'endToEndStudyLifecycle'=>true,'humanStageReviewRequired'=>true,'metadataEvidenceBoundary'=>true,'automaticScientificCertification'=>false,'automaticCausalClaim'=>false,'automaticPublication'=>false,'automaticExperimentExecution'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
