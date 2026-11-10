<?php
if (!defined('ABSPATH')) { exit; }

/**
 * SC-FIG-01 — generic sc.figure-bundle.v1 renderer in Graph Studio.
 *
 * Default off and independent of the FIG-02A preview switch. When enabled, Lab pages load the
 * FIG-02A primitives (canonical hashing, content policy) and the vendored plotly.js 3.3.1, then
 * mount a viewer that renders any governed figure bundle together with the view files it
 * references, after verifying every file against the bundle's artifact hashes. Presentation only.
 */
final class SC_Lab_Graph_Studio_Figure_Bundle_Renderer {
    const VERSION = '0.1.0';
    const FEATURE = 'SC-FIG-01/figure-bundle-renderer';
    const OPTION = 'sc_lab_figure_bundle_renderer_enabled';
    const JS = 'assets/js/modules/graph-studio-figure-bundle-renderer.js';
    const CSS = 'assets/css/sc-lab-graph-studio-figure-bundle-renderer.css';
    const FIG02A = 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A';

    public static function init() {
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
    }

    public static function is_enabled() {
        $enabled = get_option(self::OPTION, '0') === '1';
        return apply_filters('sc_lab_figure_bundle_renderer_enabled', $enabled) === true;
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
        if (!self::is_lab_request() || !self::is_enabled() || !class_exists(self::FIG02A)) { return; }
        $f = self::FIG02A;
        // Fail closed: a modified or missing plotly.js is never served.
        if (!$f::vendor_verified()) { return; }
        if (!wp_script_is('sc-lab-plotly-js-331', 'enqueued')) {
            wp_enqueue_script('sc-lab-plotly-js-331', SC_LAB_URL . $f::PLOTLY_JS, array(), $f::PLOTLY_JS_VERSION, true);
        }
        // FIG-02A module is loaded as a library; its own panel only mounts when FIG-02A is switched on.
        if (!wp_script_is('sc-lab-graph-studio-plotly-preview-fig02a', 'enqueued')) {
            wp_enqueue_script('sc-lab-graph-studio-plotly-preview-fig02a', SC_LAB_URL . $f::JS, array('sc-lab-plotly-js-331'), self::asset_token($f::JS), true);
        }
        if (!wp_style_is('sc-lab-graph-studio-plotly-preview-fig02a', 'enqueued')) {
            wp_enqueue_style('sc-lab-graph-studio-plotly-preview-fig02a', SC_LAB_URL . $f::CSS, array(), self::asset_token($f::CSS));
        }
        if (!wp_style_is('sc-lab-graph-studio-figure-bundle-renderer', 'enqueued')) {
            wp_enqueue_style('sc-lab-graph-studio-figure-bundle-renderer', SC_LAB_URL . self::CSS, array('sc-lab-graph-studio-plotly-preview-fig02a'), self::asset_token(self::CSS));
        }
        if (!wp_script_is('sc-lab-graph-studio-figure-bundle-renderer', 'enqueued')) {
            wp_enqueue_script('sc-lab-graph-studio-figure-bundle-renderer', SC_LAB_URL . self::JS, array('sc-lab-graph-studio-plotly-preview-fig02a'), self::asset_token(self::JS), true);
            wp_add_inline_script('sc-lab-graph-studio-figure-bundle-renderer', 'window.SCLabFigureBundleRendererConfig = ' . wp_json_encode(array(
                'enabled' => true,
                'version' => self::VERSION,
                'feature' => self::FEATURE,
                'bundleSchema' => 'sc.figure-bundle.v1',
                'previewOnly' => true,
            )) . ';', 'before');
        }
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/graph-studio/figure-bundle-renderer/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        $f = self::FIG02A;
        return rest_ensure_response(array(
            'ok' => true,
            'version' => self::VERSION,
            'feature' => self::FEATURE,
            'enabled' => self::is_enabled(),
            'defaultEnabled' => false,
            'bundleSchema' => 'sc.figure-bundle.v1',
            'renderers' => array('application/vnd.plotly.v1+json' => 'plotly.js 3.3.1', 'image/png' => 'static'),
            'otherMediaTypes' => 'reported-unsupported',
            'plotlyJsSha256Verified' => class_exists($f) ? $f::vendor_verified() : false,
            'artifactHashesVerifiedInBrowser' => true,
            'cdnUsed' => false,
            'previewOnly' => true,
            'persistence' => false,
            'uploadPerformed' => false,
            'publicationPerformed' => false,
            'secondGraphStudio' => false,
        ));
    }
}
