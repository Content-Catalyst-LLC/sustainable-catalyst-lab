<?php
/**
 * Sustainable Catalyst Lab v0.152.0.6 safe-boot stabilization.
 *
 * Final production recovery layer for the canonical Lab front door. It keeps
 * the verified v0.152.0.5 safe shell, adds a late footer queue gate so legacy
 * scripts cannot escape after wp_enqueue_scripts, removes the obsolete v0.26.6
 * production-budget monitor from the safe front door, establishes canonical
 * release-version presentation, and replaces the legacy admin integrity notice
 * callback with a health-backed notice authority.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Production_Safe_Boot_V015206 {
    const VERSION = '0.152.0.6';
    private static $initialized = false;
    private static $notice_registered = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;

        // The old integrity class remains the canonical verifier/REST source,
        // but its admin callback is replaced by this release-specific authority.
        self::replace_legacy_integrity_notice();
        add_action('plugins_loaded', array(__CLASS__, 'replace_legacy_integrity_notice'), PHP_INT_MAX);
        add_action('admin_init', array(__CLASS__, 'replace_legacy_integrity_notice'), 1);

        // First sweep after ordinary enqueue callbacks.
        add_action('wp_enqueue_scripts', array(__CLASS__, 'gate_frontend_assets'), PHP_INT_MAX);

        // Second sweep immediately before WordPress prints footer scripts. This
        // catches historical modules enqueued by shortcode/render-time code.
        add_action('wp_print_footer_scripts', array(__CLASS__, 'gate_footer_scripts'), 19);

        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function replace_legacy_integrity_notice() {
        remove_action('admin_notices', array('SC_Lab_Integrity_V02632', 'admin_notice'));
        if (!self::$notice_registered) {
            add_action('admin_notices', array(__CLASS__, 'admin_notice'), 10);
            self::$notice_registered = true;
        }
    }

    public static function admin_notice() {
        if (!current_user_can('activate_plugins')) { return; }
        if (!class_exists('SC_Lab_Integrity_V02632') || !method_exists('SC_Lab_Integrity_V02632', 'health')) { return; }
        $response = SC_Lab_Integrity_V02632::health();
        $state = $response instanceof WP_REST_Response ? $response->get_data() : (is_array($response) ? $response : array());
        if (!empty($state['ok'])) { return; }

        $issues = array();
        if (!empty($state['partialInstallRisk'])) {
            $issues[] = 'release files, version markers, plugin identity, or canonical route contracts do not match';
        }
        if (!empty($state['duplicatePluginRisk'])) {
            $issues[] = 'more than one Sustainable Catalyst Lab plugin folder exists in the WordPress plugin directory';
        }
        if (!$issues) { $issues[] = 'the canonical runtime health check is not verified'; }

        echo '<div class="notice notice-error"><p><strong>Sustainable Catalyst Lab integrity warning:</strong> ' . esc_html(implode('; ', $issues)) . '. Check <code>/wp-json/sc-lab/v1/runtime/health</code> before continuing upgrades.</p></div>';
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
        return $src !== '' && strpos($src, 'sustainable-catalyst-lab/') !== false;
    }

    private static function safe_script_relative() {
        return 'assets/js/sc-lab-safe-bootstrap-v015206.js';
    }

    private static function safe_style_relative() {
        return 'assets/css/sc-lab-ui-bundle-v015204.css';
    }

    private static function allowed_script_src($src) {
        return strpos((string) $src, self::safe_script_relative()) !== false;
    }

    private static function prune_lab_scripts() {
        $scripts = wp_scripts();
        if (!$scripts) { return; }
        foreach ((array) $scripts->queue as $handle) {
            $item = isset($scripts->registered[$handle]) ? $scripts->registered[$handle] : null;
            if (!$item || empty($item->src)) { continue; }
            if (!self::is_lab_asset_src($item->src)) { continue; }
            if (self::allowed_script_src($item->src)) { continue; }
            wp_dequeue_script($handle);
        }
    }

    private static function prune_lab_styles() {
        $styles = wp_styles();
        if (!$styles) { return; }
        foreach ((array) $styles->queue as $handle) {
            $item = isset($styles->registered[$handle]) ? $styles->registered[$handle] : null;
            if (!$item || empty($item->src)) { continue; }
            if (!self::is_lab_asset_src($item->src)) { continue; }
            if (strpos((string) $item->src, self::safe_style_relative()) !== false) { continue; }
            wp_dequeue_style($handle);
        }
    }

    private static function enqueue_safe_runtime() {
        $css = self::safe_style_relative();
        $js = self::safe_script_relative();

        if (!wp_style_is('sc-lab-safe-ui-v015206', 'enqueued')) {
            wp_enqueue_style('sc-lab-safe-ui-v015206', SC_LAB_URL . $css, array(), self::asset_token($css));
        }
        if (!wp_script_is('sc-lab-safe-bootstrap-v015206', 'enqueued')) {
            wp_enqueue_script('sc-lab-safe-bootstrap-v015206', SC_LAB_URL . $js, array(), self::asset_token($js), true);
            wp_localize_script('sc-lab-safe-bootstrap-v015206', 'SCLabSafeBootV015206', array(
                'version' => self::VERSION,
                'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
                'featureVersion' => defined('SC_LAB_FEATURE_VERSION') ? SC_LAB_FEATURE_VERSION : '0.152.0',
                'mode' => 'production-safe-boot-stabilized',
                'advancedRuntimeDeferred' => true,
                'legacyProductionMonitorDisabled' => true,
                'legacyPresentationRuntimeDisabled' => true,
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/frontend-runtime/v015206/health')),
            ));
        }
    }

    public static function gate_frontend_assets() {
        if (!self::is_lab_request()) { return; }
        self::prune_lab_scripts();
        self::prune_lab_styles();
        self::enqueue_safe_runtime();
    }

    public static function gate_footer_scripts() {
        if (!self::is_lab_request()) { return; }
        self::prune_lab_scripts();
        self::enqueue_safe_runtime();
    }

    private static function asset_token($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        $release = defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION;
        return $release . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    private static function state($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return array(
            'exists' => is_file($path),
            'bytes' => is_file($path) ? filesize($path) : 0,
            'sha256' => is_file($path) ? hash_file('sha256', $path) : null,
        );
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/frontend-runtime/v015206/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        $js = self::safe_script_relative();
        $css = self::safe_style_relative();
        $files = array($js => self::state($js), $css => self::state($css));
        $ok = true;
        foreach ($files as $file) {
            if (empty($file['exists']) || empty($file['bytes'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? 'safe-boot-stabilized' : 'incomplete',
            'version' => self::VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'featureVersion' => defined('SC_LAB_FEATURE_VERSION') ? SC_LAB_FEATURE_VERSION : null,
            'safeBootOnly' => true,
            'lateFooterAssetGate' => true,
            'legacyIndividualModulesEager' => false,
            'optionalMegaBundleEager' => false,
            'legacyProductionMonitorEager' => false,
            'legacyPresentationRuntimeEager' => false,
            'canonicalReleasePresentation' => true,
            'integrityNoticeAuthority' => 'v015206',
            'mutationObserverFreeBootstrap' => true,
            'fullPanelNavigationRetained' => true,
            'advancedRuntimeDeferred' => true,
            'backendBehaviorChanged' => false,
            'files' => $files,
        ));
    }
}
