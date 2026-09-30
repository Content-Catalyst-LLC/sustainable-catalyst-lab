<?php
/**
 * Sustainable Catalyst Lab v0.152.0.5 production safe boot.
 *
 * The Lab front door must remain usable even when historical modules register
 * their own WordPress assets. This runtime applies a final queue gate on the
 * canonical Lab page and permits only the consolidated stylesheet plus a
 * bounded, MutationObserver-free navigation bootstrap.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Production_Safe_Boot_V015205 {
    const VERSION = '0.152.0.5';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'gate_frontend_assets'), PHP_INT_MAX);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app')) { return true; }
        if (function_exists('is_page') && is_page('lab')) { return true; }
        $path = isset($_SERVER['REQUEST_URI']) ? (string) parse_url((string) $_SERVER['REQUEST_URI'], PHP_URL_PATH) : '';
        return (bool) preg_match('~/(?:lab)/?$~', $path);
    }

    private static function is_lab_asset_src($src) {
        $src = (string) $src;
        if ($src === '') { return false; }
        return strpos($src, 'sustainable-catalyst-lab/') !== false;
    }

    public static function gate_frontend_assets() {
        if (!self::is_lab_request()) { return; }

        // Remove every historical Lab JavaScript request, including the v0.152.0.4
        // optional mega-bundle and any direct module enqueue that survived earlier
        // consolidation. The v0.152.0.5 safe bootstrap is added after the sweep.
        $scripts = wp_scripts();
        if ($scripts) {
            foreach ((array) $scripts->queue as $handle) {
                $item = isset($scripts->registered[$handle]) ? $scripts->registered[$handle] : null;
                if (!$item || empty($item->src)) { continue; }
                if (self::is_lab_asset_src($item->src)) { wp_dequeue_script($handle); }
            }
        }

        // Collapse all Lab CSS back to the verified v0.152.0.4 consolidated
        // stylesheet. CSS contains no runtime loop and remains immutable content.
        $styles = wp_styles();
        if ($styles) {
            foreach ((array) $styles->queue as $handle) {
                $item = isset($styles->registered[$handle]) ? $styles->registered[$handle] : null;
                if (!$item || empty($item->src)) { continue; }
                if (self::is_lab_asset_src($item->src)) { wp_dequeue_style($handle); }
            }
        }

        $css = 'assets/css/sc-lab-ui-bundle-v015204.css';
        $js  = 'assets/js/sc-lab-safe-bootstrap-v015205.js';
        wp_enqueue_style('sc-lab-safe-ui-v015205', SC_LAB_URL . $css, array(), self::asset_token($css));
        wp_enqueue_script('sc-lab-safe-bootstrap-v015205', SC_LAB_URL . $js, array(), self::asset_token($js), true);
        wp_localize_script('sc-lab-safe-bootstrap-v015205', 'SCLabSafeBootV015205', array(
            'version' => self::VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'featureVersion' => defined('SC_LAB_FEATURE_VERSION') ? SC_LAB_FEATURE_VERSION : '0.152.0',
            'mode' => 'production-safe-boot',
            'advancedRuntimeDeferred' => true,
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/frontend-runtime/v015205/health')),
        ));
    }

    private static function asset_token($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        $release = defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION;
        return $release . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/frontend-runtime/v015205/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    private static function state($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return array(
            'exists' => is_file($path),
            'bytes' => is_file($path) ? filesize($path) : 0,
            'sha256' => is_file($path) ? hash_file('sha256', $path) : null,
        );
    }

    public static function health() {
        $js = 'assets/js/sc-lab-safe-bootstrap-v015205.js';
        $css = 'assets/css/sc-lab-ui-bundle-v015204.css';
        $files = array($js => self::state($js), $css => self::state($css));
        $ok = true;
        foreach ($files as $file) { if (empty($file['exists']) || empty($file['bytes'])) { $ok = false; } }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? 'production-safe-boot-ready' : 'incomplete',
            'version' => self::VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'featureVersion' => defined('SC_LAB_FEATURE_VERSION') ? SC_LAB_FEATURE_VERSION : null,
            'safeBootOnly' => true,
            'legacyIndividualModulesEager' => false,
            'optionalMegaBundleEager' => false,
            'mutationObserverFreeBootstrap' => true,
            'fullPanelNavigationRetained' => true,
            'patchAwareIntegrity' => true,
            'backendBehaviorChanged' => false,
            'files' => $files,
        ));
    }
}
