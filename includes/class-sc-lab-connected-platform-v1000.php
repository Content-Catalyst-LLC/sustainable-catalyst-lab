<?php
/** Sustainable Catalyst Lab v1.0.0 Connected Scientific Research and Compute Platform. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Connected_Platform_V1000 {
 const VERSION='1.0.0'; private static $initialized=false;
 public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));add_filter('sc_lab_module_aliases_v02631',array(__CLASS__,'aliases'));add_filter('sc_lab_panel_aliases_v02631',array(__CLASS__,'aliases'));add_shortcode('sc_lab_connected_platform',array(__CLASS__,'shortcode'));add_shortcode('sc_lab_stable_platform',array(__CLASS__,'shortcode'));}
 public static function aliases($aliases){$aliases=is_array($aliases)?$aliases:array();foreach(array('connected-platform','stable-platform','scientific-research-platform','compute-platform','general-availability') as $alias){$aliases[$alias]='connected-platform-v1000';}return $aliases;}
 public static function shortcode(){return do_shortcode('[sc_lab_app module="connected-platform-v1000"]');}
 public static function routes(){register_rest_route('sc-lab/v1','/connected-platform/v1000/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));}
 private static function state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
 public static function health(){$required=array('backend/app/connected_platform.py','backend/tests/test_connected_platform_v1000.py','assets/js/modules/connected-platform-v1000.js','assets/css/sc-lab-connected-platform-v1000.css','contracts/stable-contract-v1000.schema.json','contracts/support-lifecycle-v1000.schema.json','contracts/upgrade-certification-v1000.schema.json','contracts/production-readiness-attestation-v1000.schema.json','contracts/incident-readiness-v1000.schema.json','contracts/general-availability-certification-v1000.schema.json','contracts/stable-platform-policy-v1000.json');$files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'stable-platform-ready':'incomplete','version'=>self::VERSION,'releaseStage'=>'general-availability','stablePublicContracts'=>true,'forcePushPermitted'=>false,'files'=>$files,'time'=>gmdate('c')));}
}
SC_Lab_Connected_Platform_V1000::init();
