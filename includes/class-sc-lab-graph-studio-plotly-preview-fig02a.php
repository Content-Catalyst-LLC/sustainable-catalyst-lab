<?php
if (!defined('ABSPATH')) { exit; }

/**
 * SC-FIG-01 / FIG-02A — Graph Studio Plotly preview.
 *
 * Default off. When enabled, Lab pages load the vendored plotly.js 3.3.1 (byte-identical to the
 * plotly.js used by the Workbench FIG-02A export worker) and a preview panel that renders a
 * Workbench compile response after recomputing its hashes. Presentation only: no scientific compute,
 * storage, review, authorization or publication semantics change, and nothing is fetched from a CDN.
 */
final class SC_Lab_Graph_Studio_Plotly_Preview_FIG02A {
    const VERSION = '0.1.0';
    const FEATURE = 'SC-FIG-01/FIG-02A';
    const OPTION = 'sc_lab_fig02a_plotly_preview_enabled';
    const PLOTLY_JS_VERSION = '3.3.1';
    const PLOTLY_JS_SHA256 = 'e2b0f77ee8156ff9d525852fe4acb7bfe7d85e8a2e1da0523f6d16209b848968';
    const PLOTLY_JS = 'assets/lib/plotly-3.3.1/plotly.min.js';
    const JS = 'assets/js/modules/graph-studio-plotly-preview-fig02a.js';
    const CSS = 'assets/css/sc-lab-graph-studio-plotly-preview-fig02a.css';

    private static $vendor_verified = null;

    public static function init() {
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
    }

    /** Off unless the option is set to '1'; the filter can only be used to switch it on or off explicitly. */
    public static function is_enabled() {
        $enabled = get_option(self::OPTION, '0') === '1';
        return apply_filters('sc_lab_fig02a_plotly_preview_enabled', $enabled) === true;
    }

    public static function vendor_verified() {
        if (self::$vendor_verified === null) {
            $path = SC_LAB_DIR . self::PLOTLY_JS;
            self::$vendor_verified = is_file($path) && hash_equals(self::PLOTLY_JS_SHA256, (string) hash_file('sha256', $path));
        }
        return self::$vendor_verified;
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app')) { return true; }
        if (function_exists('is_page') && is_page('lab')) { return true; }
        $path = isset($_SERVER['REQUEST_URI']) ? (string) parse_url((string) $_SERVER['REQUEST_URI'], PHP_URL_PATH) : '';
        return (bool) preg_match('~/(?:lab)/?$~', $path);
    }

    private static function asset_token($rel) {
        $path = SC_LAB_DIR . ltrim((string) $rel, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    public static function enqueue() {
        if (!self::is_lab_request() || !self::is_enabled()) { return; }
        // Fail closed: a modified or missing plotly.js is never served.
        if (!self::vendor_verified()) { return; }
        if (!wp_script_is('sc-lab-plotly-js-331', 'enqueued')) {
            wp_enqueue_script('sc-lab-plotly-js-331', SC_LAB_URL . self::PLOTLY_JS, array(), self::PLOTLY_JS_VERSION, true);
        }
        if (!wp_style_is('sc-lab-graph-studio-plotly-preview-fig02a', 'enqueued')) {
            wp_enqueue_style('sc-lab-graph-studio-plotly-preview-fig02a', SC_LAB_URL . self::CSS, array(), self::asset_token(self::CSS));
        }
        if (!wp_script_is('sc-lab-graph-studio-plotly-preview-fig02a', 'enqueued')) {
            wp_enqueue_script('sc-lab-graph-studio-plotly-preview-fig02a', SC_LAB_URL . self::JS, array('sc-lab-plotly-js-331'), self::asset_token(self::JS), true);
            // wp_localize_script() would stringify booleans ("1"); emit typed JSON instead.
            wp_add_inline_script('sc-lab-graph-studio-plotly-preview-fig02a', 'window.SCLabFig02aPlotlyPreviewConfig = ' . wp_json_encode(array(
                'enabled' => true,
                'version' => self::VERSION,
                'feature' => self::FEATURE,
                'plotlyJsVersion' => self::PLOTLY_JS_VERSION,
                'previewOnly' => true,
            )) . ';', 'before');
        }
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/graph-studio-plotly-preview/fig02a/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        return rest_ensure_response(array(
            'ok' => true,
            'version' => self::VERSION,
            'feature' => self::FEATURE,
            'enabled' => self::is_enabled(),
            'defaultEnabled' => false,
            'plotlyJsVersion' => self::PLOTLY_JS_VERSION,
            'plotlyJsVendored' => true,
            'plotlyJsSha256Verified' => self::vendor_verified(),
            'cdnUsed' => false,
            'responseHashesRecomputedInBrowser' => true,
            'previewOnly' => true,
            'persistence' => false,
            'uploadPerformed' => false,
            'reviewDecisionsSet' => false,
            'publicationPerformed' => false,
            'secondGraphStudio' => false,
        ));
    }
}
