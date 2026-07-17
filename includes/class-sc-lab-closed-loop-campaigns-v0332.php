<?php
/** Sustainable Catalyst Lab v0.33.2 Closed-Loop Simulation and Instrument Campaigns. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Closed_Loop_Campaigns_V0332 {
    const VERSION = '0.33.2';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_closed_loop_campaigns', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_instrument_campaigns', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_simulation_campaigns', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('closed-loop-campaigns','closed-loop','instrument-campaigns','simulation-campaigns','experiment-control','instrument-control') as $alias) {
            $aliases[$alias] = 'closed-loop-campaigns';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="closed-loop-campaigns"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/closed-loop-campaigns/v0332/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/closed-loop-campaigns/v0332/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'loopSchema'=>'sc-lab-closed-loop-campaign/0.33.2',
            'measurementSchema'=>'sc-lab-closed-loop-measurement/0.33.2',
            'commandSchema'=>'sc-lab-closed-loop-command/0.33.2',
            'eventSchema'=>'sc-lab-closed-loop-event/0.33.2',
            'modes'=>array('simulation','instrument','hybrid'),
            'signedMeasurements'=>true,'operatorApproval'=>true,'safetyInterlocks'=>true,
            'directDeviceExecution'=>false,'arbitraryCallbacks'=>false,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/closed-loop-campaigns-v0332.js',
            'assets/css/sc-lab-closed-loop-campaigns-v0332.css',
            'contracts/closed-loop-campaign-v0332.schema.json',
            'contracts/closed-loop-measurement-v0332.schema.json',
            'contracts/closed-loop-command-v0332.schema.json',
            'contracts/closed-loop-event-v0332.schema.json',
            'contracts/closed-loop-policy-v0332.json',
            'includes/class-sc-lab-closed-loop-campaigns-v0332.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'closed-loop-simulation-instrument-campaigns',
            'databaseSchemaVersion'=>1,'signedMeasurementEnvelopes'=>true,
            'safetyInterlocks'=>true,'operatorCommandApproval'=>true,
            'directDeviceExecution'=>false,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
