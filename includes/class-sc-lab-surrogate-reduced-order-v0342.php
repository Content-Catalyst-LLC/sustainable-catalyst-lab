<?php
/** Sustainable Catalyst Lab v0.34.2 Surrogate Models and Reduced-Order Analysis. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Surrogate_Reduced_Order_V0342 {
    const VERSION = '0.34.2';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_surrogate_models', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_reduced_order_analysis', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_rom_studio', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('surrogate-reduced-order','surrogate-models','reduced-order','rom','rom-studio','proper-orthogonal-decomposition','pod-analysis') as $alias) {
            $aliases[$alias] = 'surrogate-reduced-order';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="surrogate-reduced-order"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/surrogate-reduced-order/v0342/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/surrogate-reduced-order/v0342/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'studySchema'=>'sc-lab-surrogate-rom-study/0.34.2',
            'modelSchema'=>'sc-lab-surrogate-rom-model/0.34.2',
            'predictionSchema'=>'sc-lab-surrogate-rom-prediction/0.34.2',
            'modes'=>array('surrogate','reduced-order','hybrid-rom'),
            'algorithms'=>array('polynomial-ridge','radial-basis','gaussian-process'),
            'reducedOrderMethods'=>array('pod-svd'),
            'holdoutValidation'=>true,'errorBounds'=>true,'registryPublication'=>true,
            'arbitraryCode'=>false,'immutableTrainingRecords'=>true,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/surrogate-reduced-order-v0342.js',
            'assets/css/sc-lab-surrogate-reduced-order-v0342.css',
            'contracts/surrogate-rom-study-v0342.schema.json',
            'contracts/surrogate-rom-model-v0342.schema.json',
            'contracts/surrogate-rom-prediction-v0342.schema.json',
            'contracts/surrogate-rom-event-v0342.schema.json',
            'contracts/surrogate-rom-policy-v0342.json',
            'includes/class-sc-lab-surrogate-reduced-order-v0342.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'surrogate-models-reduced-order-analysis',
            'databaseSchemaVersion'=>1,'immutableTrainingRecords'=>true,
            'properOrthogonalDecomposition'=>true,'hybridRom'=>true,
            'modelRegistryIntegration'=>true,'arbitraryCode'=>false,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
