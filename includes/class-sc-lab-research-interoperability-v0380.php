<?php
/** Sustainable Catalyst Lab v0.38.0 Research Interoperability Layer. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Research_Interoperability_V0380 {
    const VERSION = '0.38.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_research_interoperability', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_cross_product_handoffs', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('research-interoperability','cross-product-handoffs','interoperability','platform-handoffs','research-exchange') as $alias) { $aliases[$alias] = 'research-interoperability'; }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="research-interoperability"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/research-interoperability/v0380/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/research-interoperability/v0380/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'profileSchema'=>'sc-research-interoperability-profile/0.38.0',
            'envelopeSchema'=>'sc-research-handoff-envelope/0.38.0',
            'negotiationSchema'=>'sc-research-compatibility-negotiation/0.38.0',
            'receiptSchema'=>'sc-research-handoff-receipt/0.38.0',
            'eventSchema'=>'sc-research-interoperability-event/0.38.0',
            'typedCrossProductHandoffs'=>true,'contractNegotiation'=>true,'capabilityNegotiation'=>true,
            'idempotentImports'=>true,'signedReceipts'=>true,'workspaceGovernance'=>true,
            'directRemoteCallbacks'=>false,'arbitraryCode'=>false,'embeddedRestrictedData'=>false,'hardDelete'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'backend/app/research_interoperability.py',
            'assets/js/modules/research-interoperability-v0380.js',
            'assets/css/sc-lab-research-interoperability-v0380.css',
            'contracts/research-interoperability-policy-v0380.json',
            'contracts/interoperability-profile-v0380.schema.json',
            'contracts/research-handoff-envelope-v0380.schema.json',
            'contracts/compatibility-negotiation-v0380.schema.json',
            'contracts/research-handoff-receipt-v0380.schema.json',
            'contracts/research-interoperability-event-v0380.schema.json',
            'contracts/research-handoff-bundle-v0380.schema.json',
            'includes/class-sc-lab-research-interoperability-v0380.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) { $files[$relative]=self::state($relative); if (empty($files[$relative]['exists'])) { $ok=false; } }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'workspace-governed-typed-cross-product-research-handoffs',
            'databaseSchemaVersion'=>1,'typedCrossProductHandoffs'=>true,'canonicalEnvelopes'=>true,
            'contractNegotiation'=>true,'capabilityNegotiation'=>true,'idempotentImports'=>true,
            'signedReceipts'=>true,'directRemoteCallbacks'=>false,'embeddedRestrictedData'=>false,'hardDelete'=>false,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
SC_Lab_Research_Interoperability_V0380::init();
