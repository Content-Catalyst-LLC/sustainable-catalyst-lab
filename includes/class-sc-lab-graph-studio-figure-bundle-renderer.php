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
 *
 * SC-FIG-04 adds MapLibre geospatial views behind a third switch (default off, only effective with the
 * renderer on). MapLibre GL JS 5.24.0 (CSP build), its stylesheet and its worker are served from the plugin
 * only after all three match their pinned SHA-256. The worker is not enqueued: the browser fetches it from
 * this site, checks the SHA-384 given here and starts it from a blob: URL. No basemap, tile or imagery
 * provider is approved, so a map page requests nothing beyond these plugin files.
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

    const FIG04_OPTION = 'sc_lab_fig04_maplibre_enabled';
    const FIG04_CONTRACT_JS = 'assets/js/modules/graph-studio-maplibre-fig03a.js';
    const FIG04_JS = 'assets/js/modules/graph-studio-maplibre-renderer-fig04.js';
    const FIG04_CSS = 'assets/css/sc-lab-graph-studio-maplibre-fig04.css';
    const FIG04_VERSION = '0.1.0';
    const MAPLIBRE_VERSION = '5.24.0';
    /** role => array(path, pinned SHA-256). */
    const MAPLIBRE = array(
        'js' => array('assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp.js', 'a1f1847bac64aa00acbf80fbb79b2c5af24d8eecaaa5e2ad14080fab81f1de95'),
        'worker' => array('assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js', 'f950e7b15c49c8b9c7bb52136df2a2df2f6f03b83b8927774573fc98b067f7f0'),
        'css' => array('assets/lib/maplibre-gl-5.24.0/maplibre-gl.css', 'ab1e70d59ec40465bae7e7030da2f3ccf28133fd502e62bd598eefbadfd7a732'),
    );

    private static $vega_verified = null;
    private static $maplibre_verified = null;

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

    /** MapLibre views: only with the renderer on, the FIG-04 option '1' and the filter left true. */
    public static function fig04_enabled() {
        if (!self::is_enabled()) { return false; }
        $enabled = get_option(self::FIG04_OPTION, '0') === '1';
        return apply_filters('sc_lab_fig04_maplibre_enabled', $enabled) === true;
    }

    public static function maplibre_verified() {
        if (self::$maplibre_verified === null) {
            $ok = true;
            foreach (self::MAPLIBRE as $lib) {
                $path = SC_LAB_DIR . $lib[0];
                $ok = $ok && is_file($path) && hash_equals($lib[1], (string) hash_file('sha256', $path));
            }
            self::$maplibre_verified = $ok;
        }
        return self::$maplibre_verified;
    }

    /** Subresource-integrity value of the verified worker, checked again in the browser before it starts. */
    public static function maplibre_worker_integrity() {
        if (!self::maplibre_verified()) { return null; }
        return 'sha384-' . base64_encode(hash_file('sha384', SC_LAB_DIR . self::MAPLIBRE['worker'][0], true));
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
        // FIG-04: fail closed on any MapLibre file; the renderer then reports map views unsupported.
        $maplibre = self::fig04_enabled() && self::maplibre_verified();
        if ($maplibre) {
            if (!wp_style_is('sc-lab-maplibre-gl-5240', 'enqueued')) {
                wp_enqueue_style('sc-lab-maplibre-gl-5240', SC_LAB_URL . self::MAPLIBRE['css'][0], array(), self::MAPLIBRE_VERSION);
            }
            if (!wp_style_is('sc-lab-graph-studio-maplibre-fig04', 'enqueued')) {
                wp_enqueue_style('sc-lab-graph-studio-maplibre-fig04', SC_LAB_URL . self::FIG04_CSS, array('sc-lab-maplibre-gl-5240'), self::asset_token(self::FIG04_CSS));
            }
            if (!wp_script_is('sc-lab-maplibre-gl-5240', 'enqueued')) {
                wp_enqueue_script('sc-lab-maplibre-gl-5240', SC_LAB_URL . self::MAPLIBRE['js'][0], array(), self::MAPLIBRE_VERSION, true);
            }
            if (!wp_script_is('sc-lab-graph-studio-maplibre-fig03a', 'enqueued')) {
                wp_enqueue_script('sc-lab-graph-studio-maplibre-fig03a', SC_LAB_URL . self::FIG04_CONTRACT_JS, array('sc-lab-graph-studio-plotly-preview-fig02a'), self::asset_token(self::FIG04_CONTRACT_JS), true);
            }
            if (!wp_script_is('sc-lab-graph-studio-maplibre-fig04', 'enqueued')) {
                wp_enqueue_script('sc-lab-graph-studio-maplibre-fig04', SC_LAB_URL . self::FIG04_JS,
                    array('sc-lab-maplibre-gl-5240', 'sc-lab-graph-studio-maplibre-fig03a'), self::asset_token(self::FIG04_JS), true);
                wp_add_inline_script('sc-lab-graph-studio-maplibre-fig04', 'window.SCLabMapLibreFIG04Config = ' . wp_json_encode(array(
                    'workerUrl' => SC_LAB_URL . self::MAPLIBRE['worker'][0],
                    'workerIntegrity' => self::maplibre_worker_integrity(),
                    'maplibreVersion' => self::MAPLIBRE_VERSION,
                )) . ';', 'before');
            }
            $renderer_deps[] = 'sc-lab-graph-studio-maplibre-fig04';
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
                'maplibre' => $maplibre,
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
        $maplibre = self::fig04_enabled() && self::maplibre_verified();
        if ($maplibre) {
            $renderers['application/vnd.sc.maplibre-view.v1+json'] = 'maplibre-gl 5.24.0 CSP build (inline GeoJSON only; SI digests verified; no basemap or imagery)';
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
            'fig04' => array(
                'version' => self::FIG04_VERSION,
                'enabled' => self::fig04_enabled(),
                'defaultEnabled' => false,
                'maplibreVersion' => self::MAPLIBRE_VERSION,
                'maplibreSha256Verified' => self::maplibre_verified(),
                'served' => $maplibre,
                'workerIntegrity' => $maplibre ? 'sha384-checked-in-browser' : 'off',
                'approvedTileProviders' => array(),
                'earthObservation' => 'adapter-prepared-no-provider-approved',
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
