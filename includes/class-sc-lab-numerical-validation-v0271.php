<?php
/**
 * Sustainable Catalyst Lab v0.27.1 numerical validation and benchmark library.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Numerical_Validation_V0271 {
    const VERSION = '0.27.1';
    const CATALOG = 'contracts/numerical-benchmarks-v0271.json';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
    }

    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        $aliases['benchmarks'] = 'numerical-validation';
        $aliases['numerical-benchmarks'] = 'numerical-validation';
        $aliases['numerical-validation'] = 'numerical-validation';
        $aliases['validation-library'] = 'numerical-validation';
        return $aliases;
    }

    private static function catalog_data() {
        $path = SC_LAB_DIR . self::CATALOG;
        if (!is_file($path)) {
            return array('schema'=>'sc-lab-numerical-benchmark-catalog/1.0','version'=>self::VERSION,'benchmarkCount'=>0,'benchmarks'=>array());
        }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array('schema'=>'sc-lab-numerical-benchmark-catalog/1.0','version'=>self::VERSION,'benchmarkCount'=>0,'benchmarks'=>array());
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/numerical/v0271/benchmarks', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'catalog'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/numerical/v0271/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function catalog() {
        $catalog = self::catalog_data();
        $catalog['ok'] = !empty($catalog['benchmarks']);
        $catalog['release'] = defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION;
        return rest_ensure_response($catalog);
    }

    public static function health() {
        $catalog = self::catalog_data();
        $required = array(
            'assets/js/modules/numerical-validation-studio.js',
            'assets/css/sc-lab-numerical-validation-v0271.css',
            self::CATALOG,
            'includes/class-sc-lab-numerical-validation-v0271.php',
        );
        $files = array();
        foreach ($required as $relative) {
            $path = SC_LAB_DIR . $relative;
            $files[$relative] = array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
        }
        $all_present = !in_array(false, array_map(function($row){ return !empty($row['exists']); }, $files), true);
        return rest_ensure_response(array(
            'ok' => $all_present && count((array)($catalog['benchmarks'] ?? array())) === 14,
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'architecture' => 'known-answer-benchmark-library',
            'benchmarkCount' => count((array)($catalog['benchmarks'] ?? array())),
            'browserReferenceCount' => isset($catalog['validation']['browserReferenceBenchmarks']) ? (int)$catalog['validation']['browserReferenceBenchmarks'] : 0,
            'knownAnswerFixtures' => true,
            'toleranceControls' => true,
            'convergenceDiagnostics' => true,
            'unitAssertions' => true,
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}
