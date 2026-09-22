<?php
/** Sustainable Catalyst Lab v0.106.0 — Unified Project & Research Session Context. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Platform_Core_V3_Research_Context_V01060 {
    const VERSION = '0.106.0';
    const MINIMUM_CORE_RELEASE = '3.0.0';
    const PRODUCT_REF = 'product:sustainable-catalyst-lab';
    const CONTEXT_SCHEMA = 'sc-lab-platform-core-v3-research-context/0.106.0';
    const CORE_SESSION_PATH = '/v1/research/unified-runtime/sessions';
    const CORE_PRODUCT_BINDING_PATH = '/v1/research/unified-runtime/product-bindings';
    const CORE_OBJECT_BINDING_PATH = '/v1/research/unified-runtime/object-bindings';
    const CORE_HANDOFF_BINDING_PATH = '/v1/research/unified-runtime/handoff-bindings';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01060/context/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01060/context/manifest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01060/context/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path=SC_LAB_DIR.$relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'contextSchema'=>self::CONTEXT_SCHEMA,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'sessionPath'=>self::CORE_SESSION_PATH,'productBindingPath'=>self::CORE_PRODUCT_BINDING_PATH,'objectBindingPath'=>self::CORE_OBJECT_BINDING_PATH,'handoffBindingPath'=>self::CORE_HANDOFF_BINDING_PATH));
    }
    public static function manifest() {
        return rest_ensure_response(array('ok'=>true,'status'=>'unified-project-research-session-context-ready','version'=>self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'productRef'=>self::PRODUCT_REF,'coreOwnsSessionRegistry'=>true,'labOwnsScientificWorkspaceState'=>true,'referenceFirst'=>true,'automaticCoreSubmission'=>false,'automaticScientificExecution'=>false,'executionLineageDeferredTo'=>'0.107.0'));
    }
    public static function health() {
        $required=array('contracts/platform-core-v3-research-context-v01060.schema.json','contracts/platform-core-v3-research-context-policy-v01060.json','includes/class-sc-lab-platform-core-v3-research-context-v01060.php');
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'platform-core-v3-project-session-context-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'productRef'=>self::PRODUCT_REF,'automaticCoreSubmission'=>false,'automaticScientificExecution'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Platform_Core_V3_Research_Context_V01060::init();
