<?php
/** Sustainable Catalyst Lab v0.34.0 Scientific Model Registry and Environment Reproduction. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Model_Registry_V0340 {
    const VERSION = '0.34.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_model_registry', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_scientific_models', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_environment_reproduction', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('model-registry','scientific-models','model-versions','environment-reproduction','reproducible-models','model-governance') as $alias) {
            $aliases[$alias] = 'model-registry';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="model-registry"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/model-registry/v0340/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/model-registry/v0340/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'modelSchema'=>'sc-lab-scientific-model-version/0.34.0',
            'environmentSchema'=>'sc-lab-reproduction-environment/0.34.0',
            'reproductionSchema'=>'sc-lab-model-reproduction-manifest/0.34.0',
            'channels'=>array('draft','candidate','production','deprecated','archived'),
            'immutableVersions'=>true,'dependencyLocks'=>true,'environmentCapture'=>true,
            'promotionWorkflow'=>true,'deprecationHistory'=>true,
            'arbitraryCode'=>false,'registeredMethodsOnly'=>true,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/model-registry-v0340.js',
            'assets/css/sc-lab-model-registry-v0340.css',
            'contracts/scientific-model-v0340.schema.json',
            'contracts/reproduction-environment-v0340.schema.json',
            'contracts/model-reproduction-manifest-v0340.schema.json',
            'contracts/model-registry-event-v0340.schema.json',
            'contracts/model-registry-policy-v0340.json',
            'includes/class-sc-lab-model-registry-v0340.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'scientific-model-registry-environment-reproduction',
            'databaseSchemaVersion'=>1,'immutableSemanticVersions'=>true,
            'environmentLocking'=>true,'reproductionVerification'=>true,
            'arbitraryCode'=>false,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
