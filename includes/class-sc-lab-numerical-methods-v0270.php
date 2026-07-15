<?php
/**
 * Sustainable Catalyst Lab v0.27.0 scientific computing and numerical methods.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Numerical_Methods_V0270 {
    const VERSION = '0.27.0';
    const CATALOG = 'contracts/numerical-methods-v0270.json';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
    }

    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        $aliases['numerical'] = 'numerical-methods';
        $aliases['numerics'] = 'numerical-methods';
        $aliases['numerical-analysis'] = 'numerical-methods';
        $aliases['scientific-computing'] = 'numerical-methods';
        return $aliases;
    }

    private static function catalog_data() {
        $path = SC_LAB_DIR . self::CATALOG;
        if (!is_file($path)) { return array('schema'=>'sc-lab-numerical-methods-catalog/1.0','version'=>self::VERSION,'methodCount'=>0,'methods'=>array()); }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array('schema'=>'sc-lab-numerical-methods-catalog/1.0','version'=>self::VERSION,'methodCount'=>0,'methods'=>array());
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/numerical/v0270/catalog', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'catalog'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/numerical/v0270/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function catalog() {
        $catalog = self::catalog_data();
        $catalog['ok'] = !empty($catalog['methods']);
        $catalog['release'] = defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION;
        return rest_ensure_response($catalog);
    }

    public static function health() {
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        $catalog = self::catalog_data();
        $required = array(
            'assets/js/modules/numerical-methods-studio.js',
            'assets/css/sc-lab-numerical-methods-v0270.css',
            self::CATALOG,
            'includes/class-sc-lab-numerical-methods-v0270.php',
        );
        $files = array();
        foreach ($required as $relative) {
            $path = SC_LAB_DIR . $relative;
            $files[$relative] = array(
                'exists' => is_file($path),
                'sha256' => is_file($path) ? hash_file('sha256', $path) : null,
            );
        }
        $all_present = !in_array(false, array_map(function($row){ return !empty($row['exists']); }, $files), true);
        return rest_ensure_response(array(
            'ok' => $all_present && count((array)($catalog['methods'] ?? array())) === 12,
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'architecture' => 'wordpress-control-plane-python-numerical-compute',
            'registeredMethods' => count((array)($catalog['methods'] ?? array())),
            'remoteComputeEnabled' => !empty($settings['enable_remote_compute']),
            'remoteComputeConfigured' => !empty($settings['compute_backend_url']),
            'arbitraryCodeExecution' => false,
            'queuedExecution' => true,
            'provenance' => true,
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}
