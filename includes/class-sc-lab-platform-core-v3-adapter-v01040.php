<?php
/** Sustainable Catalyst Lab v0.104.0 — Platform Core v3 Runtime Adapter & Capability Registration. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Platform_Core_V3_Adapter_V01040 {
    const VERSION = '0.104.0';
    const CORE_REQUIRED_VERSION = '3.0.0';
    const PRODUCT_REF = 'product:sustainable-catalyst-lab';
    const ADAPTER_REF = 'lab:adapter:platform-core-v3:0.104.0';
    const RUNTIME_BINDING_REF = 'lab:runtime:scientific-compute:0.104.0';
    const RUNTIME_CONTRACT = 'sc.research.unified-runtime-contract.v1';
    const UNIFIED_RUNTIME_CONTRACT = 'sc.research.unified-research-scientific-investigation-runtime.v1';

    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01040/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01040/manifest', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'manifest'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01040/schema', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'schema'),
            'permission_callback' => '__return_true',
        ));
    }

    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array(
            'exists' => is_file($path),
            'sha256' => is_file($path) ? hash_file('sha256', $path) : null,
        );
    }

    private static function boundaries() {
        return array(
            'coreIsReferenceFirstOrchestrator' => true,
            'labIsScientificExecutionAuthority' => true,
            'underlyingLabObjectsRemainAuthoritative' => true,
            'coreExecutesSpecialistWork' => false,
            'labCallsCoreAutomatically' => false,
            'labMutatesCoreAutomatically' => false,
            'adapterInfersScientificTruth' => false,
            'adapterCertifiesScientificValidity' => false,
        );
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok' => true,
            'version' => self::VERSION,
            'adapterSchema' => 'sc-lab-platform-core-v3-runtime-adapter/0.104.0',
            'contextSchema' => 'sc-lab-platform-core-v3-runtime-context/0.104.0',
            'handoffValidationSchema' => 'sc-lab-platform-core-v3-handoff-validation/0.104.0',
            'compatibilitySchema' => 'sc-lab-platform-core-v3-compatibility/0.104.0',
            'runtimeContract' => self::RUNTIME_CONTRACT,
            'unifiedRuntimeContract' => self::UNIFIED_RUNTIME_CONTRACT,
        ));
    }

    public static function manifest() {
        return rest_ensure_response(array(
            'ok' => true,
            'status' => 'ready',
            'releaseVersion' => self::VERSION,
            'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'requiredCoreRelease' => self::CORE_REQUIRED_VERSION,
            'productRef' => self::PRODUCT_REF,
            'role' => 'scientific-execution-authority',
            'adapterRef' => self::ADAPTER_REF,
            'runtimeBindingRef' => self::RUNTIME_BINDING_REF,
            'runtimeContract' => self::RUNTIME_CONTRACT,
            'unifiedRuntimeContract' => self::UNIFIED_RUNTIME_CONTRACT,
            'capabilities' => array(
                'capabilityRegistration' => true,
                'sessionProductBinding' => true,
                'runtimeContextNormalization' => true,
                'handoffValidation' => true,
                'coreReadinessCompatibilityCheck' => true,
                'legacyTypedHandoffBridge' => true,
            ),
            'boundaries' => self::boundaries(),
        ));
    }

    public static function health() {
        $required = array(
            'contracts/platform-core-v3-runtime-adapter-v01040.schema.json',
            'contracts/platform-core-v3-runtime-adapter-policy-v01040.json',
            'includes/class-sc-lab-platform-core-v3-adapter-v01040.php',
        );
        $files = array();
        $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? 'platform-core-v3-adapter-ready' : 'incomplete',
            'version' => self::VERSION,
            'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'requiredCoreRelease' => self::CORE_REQUIRED_VERSION,
            'productRef' => self::PRODUCT_REF,
            'adapterRef' => self::ADAPTER_REF,
            'runtimeBindingRef' => self::RUNTIME_BINDING_REF,
            'runtimeContract' => self::RUNTIME_CONTRACT,
            'unifiedRuntimeContract' => self::UNIFIED_RUNTIME_CONTRACT,
            'architecture' => 'reference-first-platform-core-v3-to-lab-scientific-execution-adapter',
            'boundaries' => self::boundaries(),
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}

SC_Lab_Platform_Core_V3_Adapter_V01040::init();
