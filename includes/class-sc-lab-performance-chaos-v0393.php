<?php
/** Sustainable Catalyst Lab v0.39.3 Performance, Load, and Chaos Validation. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Performance_Chaos_V0393 {
    const VERSION='0.39.3'; private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));add_filter('sc_lab_module_aliases_v02631',array(__CLASS__,'aliases'));add_filter('sc_lab_panel_aliases_v02631',array(__CLASS__,'aliases'));add_shortcode('sc_lab_performance_validation',array(__CLASS__,'shortcode'));add_shortcode('sc_lab_chaos_validation',array(__CLASS__,'shortcode'));}
    public static function aliases($aliases){$aliases=is_array($aliases)?$aliases:array();foreach(array('performance-validation','load-validation','chaos-validation','capacity-validation','performance-load-chaos') as $alias){$aliases[$alias]='performance-chaos-v0393';}return $aliases;}
    public static function shortcode(){return do_shortcode('[sc_lab_app module="performance-chaos-v0393"]');}
    public static function routes(){register_rest_route('sc-lab/v1','/performance-chaos/v0393/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));}
    private static function state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function health(){$required=array('backend/app/performance_chaos_validation.py','backend/tests/test_performance_chaos_validation_v0393.py','assets/js/modules/performance-chaos-v0393.js','assets/css/sc-lab-performance-chaos-v0393.css','contracts/performance-validation-run-v0393.schema.json','contracts/chaos-validation-run-v0393.schema.json','contracts/capacity-report-v0393.schema.json','contracts/performance-chaos-policy-v0393.json');$files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'loadProfiles'=>true,'latencyPercentiles'=>true,'throughputMeasurement'=>true,'safeChaosScenarios'=>true,'capacityReports'=>true,'productionChaos'=>false,'externalTraffic'=>false,'files'=>$files,'time'=>gmdate('c')));}
}
SC_Lab_Performance_Chaos_V0393::init();
