<?php
/** Sustainable Catalyst Lab v0.31.2 Secure Worker Agent Runtime. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Worker_Agent_V0312 {
    const VERSION = '0.31.2';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_worker_agent', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('worker-agent','secure-worker-agent','worker-runtime','pull-worker','compute-agent') as $alias) {
            $aliases[$alias] = 'worker-agent';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="worker-agent"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/worker-agent/v0312/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/worker-agent/v0312/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,
            'version'=>self::VERSION,
            'configSchema'=>'sc-lab-worker-agent-config/0.31.2',
            'enrollmentSchema'=>'sc-lab-worker-enrollment/0.31.2',
            'receiptSchema'=>'sc-lab-worker-execution-receipt/0.31.2',
            'pullBased'=>true,
            'workerScopedCredentials'=>true,
            'registeredMethodsOnly'=>true,
            'arbitraryCode'=>false,
            'localContractVerification'=>true,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/worker-agent-v0312.js',
            'assets/css/sc-lab-worker-agent-v0312.css',
            'contracts/worker-agent-policy-v0312.json',
            'contracts/worker-agent-config-v0312.schema.json',
            'contracts/worker-enrollment-v0312.schema.json',
            'contracts/worker-execution-receipt-v0312.schema.json',
            'includes/class-sc-lab-worker-agent-v0312.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'ready':'incomplete',
            'version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'secure-pull-based-worker-agent-runtime',
            'credentialRotation'=>true,
            'credentialRevocation'=>true,
            'leaseRenewal'=>true,
            'completionReceipts'=>true,
            'files'=>$files,
            'time'=>gmdate('c'),
        ));
    }
}
