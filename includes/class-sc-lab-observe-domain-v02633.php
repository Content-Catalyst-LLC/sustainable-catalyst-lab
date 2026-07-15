<?php
/**
 * Sustainable Catalyst Lab v0.26.3.3 Observe and domain activation repair.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Observe_Domain_V02633 {
    const VERSION = '0.26.3.3';
    private static $initialized = false;
    private static $enqueued = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue'), 2);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim($relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 12) : '0');
    }

    public static function maybe_enqueue() {
        if (!self::is_lab_request() || self::$enqueued) { return; }
        self::$enqueued = true;
        $relative = 'assets/js/sc-lab-observe-domain-v02633.js';
        wp_enqueue_script(
            'sc-lab-observe-domain-v02633',
            SC_LAB_URL . $relative,
            array('sc-lab-core', 'sc-lab-projects', 'sc-lab-feeds', 'sc-lab-climate-map', 'sc-lab-datasets', 'sc-lab-observations', 'sc-lab-runtime-v02631'),
            self::asset_version($relative),
            true
        );
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/runtime/v02633/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        $assets = array(
            'observeRuntime' => 'assets/js/sc-lab-observe-domain-v02633.js',
            'app' => 'assets/js/sc-lab-app.js',
            'microbiology' => 'assets/js/modules/microbiology-laboratory.js',
            'climate' => 'assets/js/modules/climate-map.js',
            'feeds' => 'assets/js/modules/feeds.js',
            'astronomy' => 'assets/js/modules/astronomy-lab.js',
        );
        $result = array();
        foreach ($assets as $key => $relative) {
            $path = SC_LAB_DIR . $relative;
            $result[$key] = array(
                'present' => is_file($path),
                'sha256' => is_file($path) ? hash_file('sha256', $path) : null,
            );
        }
        return rest_ensure_response(array(
            'ok' => true,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'activationRuntime' => self::VERSION,
            'observeModules' => array('scientific-feeds', 'climate-maps'),
            'feedModulesSupersededBy' => '0.26.3.4',
            'astronomyObserveRoute' => 'space-telescopes',
            'astronomyAnalysisRoute' => 'astronomy',
            'microbiologyFallbackMount' => true,
            'activeProjectInjection' => true,
            'assets' => $result,
        ));
    }
}
