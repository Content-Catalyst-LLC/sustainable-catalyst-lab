<?php
/** Sustainable Catalyst Lab v0.36.1 Institutional Node Federation and Local-Data Execution. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Institutional_Node_Federation_V0361 {
    const VERSION = '0.36.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_institutional_nodes', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_local_data_execution', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('institutional-nodes','node-federation','local-data-execution','federated-compute','institutional-compute') as $alias) { $aliases[$alias] = 'institutional-nodes'; }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="institutional-nodes"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/institutional-nodes/v0361/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/institutional-nodes/v0361/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'nodeSchema'=>'sc-lab-institutional-node/0.36.1',
            'dataAssetSchema'=>'sc-lab-local-data-asset/0.36.1',
            'requestSchema'=>'sc-lab-local-execution-request/0.36.1',
            'receiptSchema'=>'sc-lab-local-execution-receipt/0.36.1',
            'eventSchema'=>'sc-lab-node-federation-event/0.36.1',
            'localDataExecution'=>true,'signedExecutionEnvelopes'=>true,
            'nodeAttestations'=>true,'restrictedDataStaysLocal'=>true,
            'automaticRemoteCallbacks'=>false,'rawRestrictedDataExport'=>false,
            'arbitraryCode'=>false,'hardDelete'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/institutional-node-federation-v0361.js',
            'assets/css/sc-lab-institutional-node-federation-v0361.css',
            'contracts/institutional-node-federation-policy-v0361.json',
            'contracts/institutional-node-v0361.schema.json',
            'contracts/local-data-asset-v0361.schema.json',
            'contracts/local-execution-request-v0361.schema.json',
            'contracts/local-execution-receipt-v0361.schema.json',
            'contracts/node-federation-event-v0361.schema.json',
            'includes/class-sc-lab-institutional-node-federation-v0361.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) { $files[$relative]=self::state($relative); if (empty($files[$relative]['exists'])) { $ok=false; } }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'workspace-governed-institutional-node-federation-and-local-data-execution',
            'databaseSchemaVersion'=>1,'localDataExecution'=>true,'signedExecutionEnvelopes'=>true,
            'nodeAttestations'=>true,'restrictedDataStaysLocal'=>true,
            'automaticRemoteCallbacks'=>false,'rawRestrictedDataExport'=>false,
            'arbitraryCode'=>false,'hardDelete'=>false,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
