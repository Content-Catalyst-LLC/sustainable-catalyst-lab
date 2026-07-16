<?php
/** Sustainable Catalyst Lab v0.31.4 Dispatcher Operations and Dead-Letter Recovery. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Dispatcher_Operations_V0314 {
    const VERSION = '0.31.4';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_dispatcher_operations', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('dispatcher-operations','dead-letter-queue','queue-observability','dispatch-operations','failure-recovery') as $alias) {
            $aliases[$alias] = 'dispatcher-operations';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="dispatcher-operations"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/dispatcher-operations/v0314/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/dispatcher-operations/v0314/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'failureSchema'=>'sc-lab-dispatch-failure/0.31.4',
            'deadLetterSchema'=>'sc-lab-dispatch-dead-letter/0.31.4',
            'operationsSchema'=>'sc-lab-dispatch-operations/0.31.4',
            'failureClassification'=>true,'boundedExponentialBackoff'=>true,
            'deadLetterRecovery'=>true,'operatorReplay'=>true,'bulkReplay'=>true,
            'queueMetrics'=>true,'eventTimelines'=>true,'databaseDiagnostics'=>true,
            'hardDelete'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/dispatcher-operations-v0314.js',
            'assets/css/sc-lab-dispatcher-operations-v0314.css',
            'contracts/dispatcher-failure-v0314.schema.json',
            'contracts/dispatcher-dead-letter-v0314.schema.json',
            'contracts/dispatcher-operations-policy-v0314.json',
            'includes/class-sc-lab-dispatcher-operations-v0314.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'dispatcher-operations-dead-letter-observability',
            'failureClassification'=>true,'deadLetterRecovery'=>true,'operatorReplay'=>true,
            'queueMetrics'=>true,'databaseDiagnostics'=>true,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
