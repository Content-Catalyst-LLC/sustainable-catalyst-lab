<?php
/** Sustainable Catalyst Lab v0.107.0 — Scientific Execution Lineage Bridge. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Platform_Core_V3_Execution_Lineage_V01070 {
    const VERSION = '0.107.0';
    const MINIMUM_CORE_RELEASE = '3.0.0';
    const PRODUCT_REF = 'product:sustainable-catalyst-lab';
    const EXECUTION_SCHEMA = 'sc-lab-scientific-execution-lineage/0.107.0';
    const CORE_EXECUTION_BINDING_PATH = '/v1/research/unified-runtime/execution-bindings';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01070/executions/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01070/executions/manifest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01070/executions/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }

    private static function file_state($relative) {
        $path=SC_LAB_DIR.$relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,
            'version'=>self::VERSION,
            'executionSchema'=>self::EXECUTION_SCHEMA,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'executionBindingPath'=>self::CORE_EXECUTION_BINDING_PATH,
            'referenceFirst'=>true,
            'automaticCoreSubmission'=>false,
            'automaticScientificExecution'=>false,
        ));
    }

    public static function manifest() {
        return rest_ensure_response(array(
            'ok'=>true,
            'status'=>'scientific-execution-lineage-bridge-ready',
            'version'=>self::VERSION,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,
            'coreExecutionBindingPath'=>self::CORE_EXECUTION_BINDING_PATH,
            'labIsScientificExecutionAuthority'=>true,
            'coreRecordsExecutionReferencesAndLineage'=>true,
            'underlyingExecutionRemainsAuthoritativeInLab'=>true,
            'lineageIsDeclaredNotInferred'=>true,
            'automaticCoreSubmission'=>false,
            'automaticScientificExecution'=>false,
            'scientificValidityCertifiedByBridge'=>false,
            'findingsClaimsValidationBridgeDeferredTo'=>'0.108.0',
        ));
    }

    public static function health() {
        $required=array(
            'contracts/platform-core-v3-execution-lineage-v01070.schema.json',
            'contracts/platform-core-v3-execution-lineage-policy-v01070.json',
            'includes/class-sc-lab-platform-core-v3-execution-lineage-v01070.php'
        );
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'platform-core-v3-scientific-execution-lineage-ready':'incomplete',
            'version'=>self::VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,
            'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,
            'coreExecutionBindingPath'=>self::CORE_EXECUTION_BINDING_PATH,
            'automaticCoreSubmission'=>false,
            'automaticScientificExecution'=>false,
            'files'=>$files,
            'time'=>gmdate('c')
        ));
    }
}
SC_Lab_Platform_Core_V3_Execution_Lineage_V01070::init();
