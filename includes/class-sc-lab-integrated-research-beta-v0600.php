<?php
/** Sustainable Catalyst Lab v0.60.0 — Integrated Scientific Research Beta. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Integrated_Research_Beta_V0600 {
    const VERSION='0.60.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/integrated-research/v0600/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/integrated-research/v0600/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'journeySchema'=>'sc-lab-integrated-research-journey/0.60.0','readinessSchema'=>'sc-lab-integrated-beta-readiness/0.60.0','packetSchema'=>'sc-lab-integrated-research-beta-packet/0.60.0'));}
    public static function health(){
        $required=array('backend/app/integrated_research_beta_v0600.py','backend/tests/test_integrated_research_beta_v0600.py','assets/js/modules/integrated-research-beta-v0600.js','assets/css/sc-lab-integrated-research-beta-v0600.css','contracts/integrated-research-journey-v0600.schema.json','contracts/integrated-beta-readiness-v0600.schema.json','contracts/integrated-research-beta-packet-v0600.schema.json','contracts/integrated-research-beta-policy-v0600.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'integrated-scientific-research-beta-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'humanReviewRequired'=>true,'automaticScientificCertification'=>false,'automaticPublication'=>false,'rawSensitiveDataInBetaPacket'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
