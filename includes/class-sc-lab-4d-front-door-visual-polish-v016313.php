<?php
if (!defined('ABSPATH')) { exit; }

/**
 * Lab v0.163.1.3 — 4D Front-Door Visual Polish & Compact Control Layout.
 *
 * Presentation-only layer. It does not change scientific compute, storage,
 * provenance, authorization, or workspace semantics.
 */
final class SC_Lab_4D_Front_Door_Visual_Polish_V016313 {
    const VERSION = '0.163.1.3';
    const FEATURE_VERSION = '0.163.1';

    public static function init() {
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue_after_front_door_repair'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'enqueue_after_front_door_repair'), PHP_INT_MAX);
        add_filter('body_class', array(__CLASS__, 'body_class'), PHP_INT_MAX);
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

    public static function body_class($classes) {
        if (self::is_lab_request()) { $classes[] = 'sc-lab-v016313-polish'; }
        return array_values(array_unique($classes));
    }

    public static function enqueue_after_front_door_repair() {
        if (!self::is_lab_request()) { return; }

        $css = 'assets/css/sc-lab-4d-front-door-visual-polish-v016313.css';
        $js  = 'assets/js/sc-lab-4d-front-door-visual-polish-v016313.js';

        // Registered at the end of plugin initialization and at PHP_INT_MAX so
        // the visual polish layer survives the historical v0.154 asset gate and
        // follows the v0.163.1.2 retention repair.
        if (!wp_style_is('sc-lab-4d-front-door-visual-polish-v016313', 'enqueued')) {
            wp_enqueue_style(
                'sc-lab-4d-front-door-visual-polish-v016313',
                SC_LAB_URL . $css,
                array('sc-lab-unified-workspace-shell-v016312'),
                self::asset_token($css)
            );
        }
        if (!wp_script_is('sc-lab-4d-front-door-visual-polish-v016313', 'enqueued')) {
            wp_enqueue_script(
                'sc-lab-4d-front-door-visual-polish-v016313',
                SC_LAB_URL . $js,
                array('sc-lab-unified-workspace-shell-v016312'),
                self::asset_token($js),
                true
            );
            wp_localize_script('sc-lab-4d-front-door-visual-polish-v016313', 'SCLabFrontDoorPolishV016313', array(
                'version' => self::VERSION,
                'featureVersion' => self::FEATURE_VERSION,
                'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
                'presentationOnly' => true,
                'compactCanvas' => true,
                'responseSurfacePrimary' => true,
                'advancedPanelsProgressive' => true,
                'collapsedByDefault' => array('uncertainty', 'linked', 'scene', 'project'),
                'preserveScientificSignals' => true,
                'preserveSpecialistShell' => true,
                'scientificComputeMethodsChanged' => false,
                'scientificSemanticsChanged' => false,
            ));
        }
    }
}
