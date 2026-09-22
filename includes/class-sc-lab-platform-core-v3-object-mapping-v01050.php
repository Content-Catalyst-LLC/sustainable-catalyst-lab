<?php
/** Sustainable Catalyst Lab v0.105.0 — Canonical Research Object Mapping. */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Platform_Core_V3_Object_Mapping_V01050 {
    const VERSION = '0.105.0';
    const CORE_REQUIRED_VERSION = '3.0.0';
    const PRODUCT_REF = 'product:sustainable-catalyst-lab';
    const MAPPING_SCHEMA = 'sc-lab-platform-core-v3-object-mapping/0.105.0';
    const OBJECT_SCHEMA = 'sc-lab-canonical-research-object/0.105.0';
    const BINDING_SCHEMA = 'sc-lab-platform-core-v3-object-binding/0.105.0';
    const CORE_OBJECT_BINDING_PATH = '/v1/research/unified-runtime/object-bindings';

    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01050/objects/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01050/objects/catalog', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'catalog'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/platform-core-v3/v01050/objects/schema', array(
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

    private static function mappings() {
        return array(
            'dataset' => 'dataset',
            'observation-set' => 'observation-set',
            'workflow' => 'workflow',
            'workflow-run' => 'workflow-run',
            'experiment' => 'experiment',
            'campaign' => 'campaign',
            'model' => 'model',
            'surrogate-model' => 'surrogate-model',
            'artifact' => 'artifact',
            'evidence-record' => 'evidence',
            'citation-set' => 'citation-set',
            'publication' => 'publication',
            'reproducibility-package' => 'reproducibility-package',
            'manuscript' => 'manuscript',
            'decision-packet' => 'decision-packet',
            'scenario' => 'scenario',
            'indicator-set' => 'indicator-set',
            'research-brief' => 'research-brief',
            'workspace-snapshot' => 'workspace-snapshot',
            'scientific-figure' => 'scientific-figure',
        );
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok' => true,
            'version' => self::VERSION,
            'mappingSchema' => self::MAPPING_SCHEMA,
            'objectSchema' => self::OBJECT_SCHEMA,
            'bindingSchema' => self::BINDING_SCHEMA,
            'batchSchema' => 'sc-lab-platform-core-v3-object-binding-batch/0.105.0',
            'legacyBridgeSchema' => 'sc-lab-platform-core-v3-legacy-object-bridge/0.105.0',
            'coreObjectBindingPath' => self::CORE_OBJECT_BINDING_PATH,
        ));
    }

    public static function catalog() {
        $rows = array();
        foreach (self::mappings() as $lab_type => $core_type) {
            $rows[] = array(
                'labType' => $lab_type,
                'coreObjectType' => $core_type,
                'authority' => self::PRODUCT_REF,
            );
        }
        return rest_ensure_response(array(
            'ok' => true,
            'status' => 'canonical-object-mapping-ready',
            'version' => self::VERSION,
            'requiredCoreRelease' => self::CORE_REQUIRED_VERSION,
            'mappingCount' => count($rows),
            'mappings' => $rows,
            'referenceFirst' => true,
            'automaticCoreSubmission' => false,
            'labObjectsRemainAuthoritative' => true,
        ));
    }

    public static function health() {
        $required = array(
            'backend/app/platform_core_v3_object_mapping_v01050.py',
            'contracts/platform-core-v3-object-mapping-v01050.schema.json',
            'contracts/platform-core-v3-object-mapping-policy-v01050.json',
            'includes/class-sc-lab-platform-core-v3-object-mapping-v01050.php',
        );
        $files = array();
        $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? 'platform-core-v3-canonical-object-mapping-ready' : 'incomplete',
            'version' => self::VERSION,
            'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'requiredCoreRelease' => self::CORE_REQUIRED_VERSION,
            'productRef' => self::PRODUCT_REF,
            'mappingCount' => count(self::mappings()),
            'coreObjectBindingPath' => self::CORE_OBJECT_BINDING_PATH,
            'referenceFirst' => true,
            'automaticCoreSubmission' => false,
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}

SC_Lab_Platform_Core_V3_Object_Mapping_V01050::init();
