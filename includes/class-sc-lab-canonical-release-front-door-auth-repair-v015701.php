<?php
/**
 * Sustainable Catalyst Lab v0.157.0.1 — Canonical Release Identity,
 * Front-Door Synchronization & Workspace Authorization Repair.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Canonical_Release_Front_Door_Auth_Repair_V015701 {
    const VERSION = '0.157.0.1';
    const FEATURE_VERSION = '0.157.0';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string)$post->post_content, 'sc_lab_app')) { return true; }
        if (function_exists('is_page') && is_page('lab')) { return true; }
        $path = isset($_SERVER['REQUEST_URI']) ? (string)parse_url((string)$_SERVER['REQUEST_URI'], PHP_URL_PATH) : '';
        return (bool)preg_match('~/(?:lab)/?$~', $path);
    }

    private static function asset_token($relative) {
        $path = SC_LAB_DIR . ltrim((string)$relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    private static function release_version() {
        return defined('SC_LAB_RELEASE_VERSION') ? (string)SC_LAB_RELEASE_VERSION : self::VERSION;
    }

    private static function feature_version() {
        return defined('SC_LAB_FEATURE_VERSION') ? (string)SC_LAB_FEATURE_VERSION : self::FEATURE_VERSION;
    }

    public static function enqueue() {
        if (!self::is_lab_request()) { return; }
        $css = 'assets/css/sc-lab-canonical-release-front-door-auth-repair-v015701.css';
        $js  = 'assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js';
        wp_enqueue_style(
            'sc-lab-canonical-repair-v015701',
            SC_LAB_URL . $css,
            array(),
            self::asset_token($css)
        );
        wp_enqueue_script(
            'sc-lab-canonical-repair-v015701',
            SC_LAB_URL . $js,
            array('sc-lab-cross-study-meta-v01570'),
            self::asset_token($js),
            true
        );
        $logged_in = is_user_logged_in();
        wp_localize_script('sc-lab-canonical-repair-v015701', 'SCLabCanonicalRepairV015701', array(
            'version' => self::VERSION,
            'releaseVersion' => self::release_version(),
            'featureVersion' => self::feature_version(),
            'authenticated' => $logged_in,
            'defaultProjectId' => $logged_in ? 'project:wp-user-' . get_current_user_id() : '',
            'loginUrl' => esc_url_raw(wp_login_url(home_url('/lab/'))),
            'runtimeHealthUrl' => esc_url_raw(rest_url('sc-lab/v1/frontend-runtime/v015701/health')),
            'authMessage' => 'Sign in to use server-backed project storage. Public Lab visualization remains available.',
        ));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/frontend-runtime/v015701/health', array(
            'methods' => 'GET',
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        return rest_ensure_response(array(
            'ok' => true,
            'status' => 'canonical-release-front-door-auth-repaired',
            'version' => self::VERSION,
            'releaseVersion' => self::release_version(),
            'featureVersion' => self::feature_version(),
            'canonicalReleaseIdentity' => true,
            'frontDoorSynchronization' => true,
            'workspaceAuthorizationPresentation' => true,
            'serverBackedWorkspaceRequiresLogin' => true,
            'publicProjectDataExposure' => false,
            'subsystemIntroductionVersionsPreserved' => true,
            'backendBehaviorChanged' => false,
            'scientificBehaviorChanged' => false,
        ));
    }
}
