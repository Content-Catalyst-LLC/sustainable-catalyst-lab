<?php
/** Sustainable Catalyst Lab v0.60.1 — Beta Field Diagnostics, Integration Soak & Runtime Repair. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Beta_Field_Diagnostics_V0601 {
    const VERSION='0.60.1';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/beta-diagnostics/v0601/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/beta-diagnostics/v0601/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'snapshotSchema'=>'sc-lab-beta-runtime-snapshot/0.60.1','soakSchema'=>'sc-lab-beta-integration-soak/0.60.1','packetSchema'=>'sc-lab-beta-field-diagnostic-packet/0.60.1'));}
    public static function health(){
        $required=array('backend/app/beta_field_diagnostics_v0601.py','backend/tests/test_beta_field_diagnostics_v0601.py','assets/js/modules/beta-field-diagnostics-v0601.js','assets/css/sc-lab-beta-field-diagnostics-v0601.css','contracts/beta-runtime-snapshot-v0601.schema.json','contracts/beta-integration-soak-v0601.schema.json','contracts/beta-field-diagnostic-packet-v0601.schema.json','contracts/beta-field-diagnostics-policy-v0601.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'beta-field-diagnostics-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'metadataOnly'=>true,'boundedUserInitiatedSoak'=>true,'automaticRepair'=>false,'externalTelemetry'=>false,'humanReviewRequired'=>true,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
