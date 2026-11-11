<?php
if (!defined('ABSPATH')) { exit; }

/**
 * SC-FIG-01 — generic sc.figure-bundle.v1 renderer in Graph Studio.
 *
 * Default off and independent of the FIG-02A preview switch. When enabled, Lab pages load the
 * FIG-02A primitives (canonical hashing, content policy) and the vendored plotly.js 3.3.1, then
 * mount a viewer that renders any governed figure bundle together with the view files it
 * references, after verifying every file against the bundle's artifact hashes. Presentation only.
 *
 * SC-FIG-02B adds Vega-Lite views and verified SVG export behind a second switch (also default off,
 * and only effective with the renderer on). Vega 6.4.0, Vega-Lite 6.5.0 and the CSP-safe
 * vega-interpreter 2.3.2 are served from the plugin only after every file matches its pinned SHA-256;
 * if any does not, none is served and Vega-Lite views are reported unsupported (Plotly is unaffected).
 */
final class SC_Lab_Graph_Studio_Figure_Bundle_Renderer {
    const VERSION = '0.1.0';
    const FEATURE = 'SC-FIG-01/figure-bundle-renderer';
    const OPTION = 'sc_lab_figure_bundle_renderer_enabled';
    const JS = 'assets/js/modules/graph-studio-figure-bundle-renderer.js';
    const CSS = 'assets/css/sc-lab-graph-studio-figure-bundle-renderer.css';
    const FIG02A = 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A';
    const FIG02B_OPTION = 'sc_lab_fig02b_vega_lite_enabled';
    const FIG02B_JS = 'assets/js/modules/graph-studio-vega-lite-fig02b.js';
    const FIG02B_VERSION = '0.1.0';
    /** handle => array(path, pinned SHA-256, version, dependencies), in load order. */
    const VEGA = array(
        'sc-lab-vega-640' => array('assets/lib/vega-6.4.0/vega.min.js', '8f6a3587cf8d4f42c7e08120e3eb05d067e746d554e39d2dcf52acc0bd5ba28f', '6.4.0', array()),
        'sc-lab-vega-lite-650' => array('assets/lib/vega-lite-6.5.0/vega-lite.min.js', '83e215e84e308ee8688fa6503ba0f1cf8a3c05c0d61df2841a0b92bf86809e00', '6.5.0', array('sc-lab-vega-640')),
        'sc-lab-vega-interpreter-232' => array('assets/lib/vega-interpreter-2.3.2/vega-interpreter.classic.js', '3bba66a9912c02968723f46d4fbf340e32ea752b6ccfdc1a321458ce9ea195d7', '2.3.2', array('sc-lab-vega-640')),
    );

    private static $vega_verified = null;

    public static function init() {
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
    }

    public static function is_enabled() {
        $enabled = get_option(self::OPTION, '0') === '1';
        return apply_filters('sc_lab_figure_bundle_renderer_enabled', $enabled) === true;
    }

    /** Vega-Lite views: only with the renderer on, the FIG-02B option '1' and the filter left true. */
    public static function fig02b_enabled() {
        if (!self::is_enabled()) { return false; }
        $enabled = get_option(self::FIG02B_OPTION, '0') === '1';
        return apply_filters('sc_lab_fig02b_vega_lite_enabled', $enabled) === true;
    }

    public static function vega_verified() {
        if (self::$vega_verified === null) {
            $ok = true;
            foreach (self::VEGA as $lib) {
                $path = SC_LAB_DIR . $lib[0];
                $ok = $ok && is_file($path) && hash_equals($lib[1], (string) hash_file('sha256', $path));
            }
            self::$vega_verified = $ok;
        }
        return self::$vega_verified;
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
        $renderer_deps = array('sc-lab-graph-studio-plotly-preview-fig02a');
        // FIG-02B: fail closed on any Vega file; the renderer then reports Vega-Lite views unsupported.
        $vega_lite = self::fig02b_enabled() && self::vega_verified();
        if ($vega_lite) {
            foreach (self::VEGA as $handle => $lib) {
                if (!wp_script_is($handle, 'enqueued')) {
                    wp_enqueue_script($handle, SC_LAB_URL . $lib[0], $lib[3], $lib[2], true);
                }
            }
            if (!wp_script_is('sc-lab-graph-studio-vega-lite-fig02b', 'enqueued')) {
                wp_enqueue_script('sc-lab-graph-studio-vega-lite-fig02b', SC_LAB_URL . self::FIG02B_JS,
                    array('sc-lab-graph-studio-plotly-preview-fig02a', 'sc-lab-vega-lite-650', 'sc-lab-vega-interpreter-232'), self::asset_token(self::FIG02B_JS), true);
            }
            $renderer_deps[] = 'sc-lab-graph-studio-vega-lite-fig02b';
        }
        if (!wp_script_is('sc-lab-graph-studio-figure-bundle-renderer', 'enqueued')) {
            wp_enqueue_script('sc-lab-graph-studio-figure-bundle-renderer', SC_LAB_URL . self::JS, $renderer_deps, self::asset_token(self::JS), true);
            wp_add_inline_script('sc-lab-graph-studio-figure-bundle-renderer', 'window.SCLabFigureBundleRendererConfig = ' . wp_json_encode(array(
                'enabled' => true,
                'version' => self::VERSION,
                'feature' => self::FEATURE,
                'bundleSchema' => 'sc.figure-bundle.v1',
                'previewOnly' => true,
                'vegaLite' => $vega_lite,
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
        $renderers = array('application/vnd.plotly.v1+json' => 'plotly.js 3.3.1', 'image/png' => 'static');
        $vega_lite = self::fig02b_enabled() && self::vega_verified();
        if ($vega_lite) {
            $renderers['application/vnd.vegalite.v5+json'] = 'vega-lite 6.5.0 / vega 6.4.0 (expression interpreter, no eval)';
            $renderers['application/vnd.vegalite.v6+json'] = 'vega-lite 6.5.0 / vega 6.4.0 (expression interpreter, no eval)';
            $renderers['image/svg+xml'] = 'verified static SVG (element allow-list, embedded provenance)';
        }
        return rest_ensure_response(array(
            'ok' => true,
            'version' => self::VERSION,
            'feature' => self::FEATURE,
            'enabled' => self::is_enabled(),
            'defaultEnabled' => false,
            'bundleSchema' => 'sc.figure-bundle.v1',
            'renderers' => $renderers,
            'fig02b' => array(
                'version' => self::FIG02B_VERSION,
                'enabled' => self::fig02b_enabled(),
                'defaultEnabled' => false,
                'vegaSha256Verified' => self::vega_verified(),
                'served' => $vega_lite,
                'svgExport' => $vega_lite ? 'verified-with-receipt' : 'off',
                'evalUsed' => false,
            ),
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
