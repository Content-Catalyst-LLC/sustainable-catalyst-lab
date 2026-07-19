<?php
/** Sustainable Catalyst Lab v0.38.1 Typed Cross-Product Research Handoffs. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Typed_Cross_Product_Handoffs_V0381 {
    const VERSION = '0.38.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_typed_cross_product_handoffs', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_product_handoff_studio', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('typed-cross-product-handoffs','typed-research-handoffs','product-handoff-studio','research-handoff-studio') as $alias) { $aliases[$alias] = 'typed-cross-product-handoffs'; }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="typed-cross-product-handoffs"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/typed-cross-product-handoffs/v0381/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/typed-cross-product-handoffs/v0381/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) { $path=SC_LAB_DIR.$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema() { return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'adapterSchema'=>'sc-typed-research-adapter/0.38.1','routeSchema'=>'sc-typed-research-route/0.38.1','planSchema'=>'sc-typed-research-handoff-plan/0.38.1','executableAdapterRegistry'=>true,'productPairRoutePlanning'=>true,'profileAwareSealing'=>true,'remoteCallbacks'=>false,'arbitraryCode'=>false)); }
    public static function health() {
        $required=array('backend/app/typed_cross_product_handoffs.py','assets/js/modules/typed-cross-product-handoffs-v0381.js','assets/css/sc-lab-typed-cross-product-handoffs-v0381.css','contracts/typed-research-adapter-v0381.schema.json','contracts/typed-research-route-v0381.schema.json','contracts/typed-research-handoff-plan-v0381.schema.json','contracts/typed-cross-product-handoff-policy-v0381.json','includes/class-sc-lab-typed-cross-product-handoffs-v0381.php');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'architecture'=>'executable-typed-product-adapters-over-governed-interoperability','adapterCount'=>13,'remoteCallbacks'=>false,'arbitraryCode'=>false,'embeddedRestrictedData'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Typed_Cross_Product_Handoffs_V0381::init();
