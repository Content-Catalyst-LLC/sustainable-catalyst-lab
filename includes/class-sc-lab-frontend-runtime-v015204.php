<?php
/** Sustainable Catalyst Lab v0.152.0.4 front-end request consolidation and runtime load recovery. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Frontend_Runtime_V015204 {
    const VERSION = '0.152.0.4';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/frontend-runtime/v015204/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'bytes'=>is_file($path)?filesize($path):0,'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function health() {
        $boot='assets/js/sc-lab-bootstrap-v015204.js';
        $optional='assets/js/sc-lab-optional-modules-v015204.js';
        $css='assets/css/sc-lab-ui-bundle-v015204.css';
        $files=array($boot=>self::state($boot),$optional=>self::state($optional),$css=>self::state($css));
        $ok=true; foreach($files as $f){ if(empty($f['exists']) || empty($f['bytes'])) {$ok=false;} }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'frontend-runtime-ready':'incomplete',
            'version'=>self::VERSION,
            'releaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'requestConsolidation'=>true,
            'criticalBootstrapBundle'=>true,
            'optionalModuleBundle'=>true,
            'cssBundle'=>true,
            'legacyHandleCompatibilityAliases'=>true,
            'earlyWordPressEnqueue'=>true,
            'backendBehaviorChanged'=>false,
            'files'=>$files,
        ));
    }
}
