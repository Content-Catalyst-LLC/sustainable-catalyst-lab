<?php
/** Sustainable Catalyst Lab v0.109.0 — Visual Reasoning & Scientific Scene Bridge. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Platform_Core_V3_Visual_Scene_V01090 {
    const VERSION = '0.109.0';
    const MINIMUM_CORE_RELEASE = '3.0.0';
    const PRODUCT_REF = 'product:sustainable-catalyst-lab';
    const BRIDGE_SCHEMA = 'sc-lab-platform-core-v3-visual-reasoning-scientific-scene/0.109.0';
    const CORE_SCENE_CONTRACT = 'sc.visual-runtime.scene.v1';
    const CORE_REASONING_CONTRACT = 'sc.visual-runtime.unified-reasoning.v1';
    const CORE_VISUAL_BINDING_PATH = '/v1/research/unified-runtime/visual-bindings';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01090/visual-scene/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01090/visual-scene/manifest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01090/visual-scene/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }

    private static function file_state($relative) {
        $path=SC_LAB_DIR.$relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,
            'version'=>self::VERSION,
            'bridgeSchema'=>self::BRIDGE_SCHEMA,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'coreVisualSceneContract'=>self::CORE_SCENE_CONTRACT,
            'coreUnifiedVisualReasoningContract'=>self::CORE_REASONING_CONTRACT,
            'coreVisualBindingPath'=>self::CORE_VISUAL_BINDING_PATH,
            'automaticCoreSubmission'=>false,
            'automaticRenderingByCore'=>false,
        ));
    }

    public static function manifest() {
        return rest_ensure_response(array(
            'ok'=>true,
            'status'=>'visual-reasoning-scientific-scene-bridge-ready',
            'version'=>self::VERSION,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,
            'coreVisualSceneContract'=>self::CORE_SCENE_CONTRACT,
            'coreUnifiedVisualReasoningContract'=>self::CORE_REASONING_CONTRACT,
            'coreVisualBindingPath'=>self::CORE_VISUAL_BINDING_PATH,
            'labIsScientificRenderingAuthority'=>true,
            'coreIsRendererNeutral'=>true,
            'coreRendersVisuals'=>false,
            'corePerformsGpuWork'=>false,
            'automaticCoreSubmission'=>false,
            'automaticCoreMutation'=>false,
            'automaticVisualTruthInference'=>false,
            'automaticLinkInference'=>false,
            'automaticUncertaintyInference'=>false,
            'reproducibilityScholarlyPackageBridgeDeferredTo'=>'0.110.0',
        ));
    }

    public static function health() {
        $required=array(
            'contracts/platform-core-v3-visual-scene-v01090.schema.json',
            'contracts/platform-core-v3-visual-scene-policy-v01090.json',
            'includes/class-sc-lab-platform-core-v3-visual-scene-v01090.php'
        );
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'platform-core-v3-visual-reasoning-scientific-scene-ready':'incomplete',
            'version'=>self::VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,
            'coreVisualSceneContract'=>self::CORE_SCENE_CONTRACT,
            'coreVisualBindingPath'=>self::CORE_VISUAL_BINDING_PATH,
            'labIsScientificRenderingAuthority'=>true,
            'automaticCoreSubmission'=>false,
            'automaticRenderingByCore'=>false,
            'files'=>$files,
            'time'=>gmdate('c')
        ));
    }
}
SC_Lab_Platform_Core_V3_Visual_Scene_V01090::init();
