<?php
/** Sustainable Catalyst Lab v0.40.2 migration, compatibility, and public release hardening. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Public_Release_Hardening_V0402 {
 const VERSION='0.40.2'; private static $initialized=false;
 public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));add_filter('sc_lab_module_aliases_v02631',array(__CLASS__,'aliases'));add_filter('sc_lab_panel_aliases_v02631',array(__CLASS__,'aliases'));add_shortcode('sc_lab_public_release_hardening',array(__CLASS__,'shortcode'));add_shortcode('sc_lab_release_candidate_center',array(__CLASS__,'shortcode'));}
 public static function aliases($aliases){$aliases=is_array($aliases)?$aliases:array();foreach(array('public-release-hardening','release-candidate-center','migration-compatibility','compatibility-matrix','release-readiness') as $alias){$aliases[$alias]='public-release-hardening-v0402';}return $aliases;}
 public static function shortcode(){return do_shortcode('[sc_lab_app module="public-release-hardening-v0402"]');}
 public static function routes(){register_rest_route('sc-lab/v1','/public-release-hardening/v0402/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));}
 private static function state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
 public static function health(){$required=array('backend/app/public_release_hardening.py','backend/tests/test_public_release_hardening_v0402.py','assets/js/modules/public-release-hardening-v0402.js','assets/css/sc-lab-public-release-hardening-v0402.css','contracts/compatibility-matrix-v0402.schema.json','contracts/migration-assessment-v0402.schema.json','contracts/deprecation-record-v0402.schema.json','contracts/clean-install-report-v0402.schema.json','contracts/rollback-plan-v0402.schema.json','contracts/release-candidate-report-v0402.schema.json','contracts/public-release-hardening-policy-v0402.json');$files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'release-hardening-ready':'incomplete','version'=>self::VERSION,'migrationDefaultMode'=>'dry-run','forcePushPermitted'=>false,'productionFilesMayBeOverwrittenByApi'=>false,'files'=>$files,'time'=>gmdate('c')));}
}
SC_Lab_Public_Release_Hardening_V0402::init();
