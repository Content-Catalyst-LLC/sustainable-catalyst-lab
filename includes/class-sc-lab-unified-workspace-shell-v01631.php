<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Unified_Workspace_Shell_V01631 {
    const VERSION = '0.163.1';

    public static function init() {
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), 240);
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
        $path = plugin_dir_path(dirname(__FILE__)) . ltrim($rel, '/');
        return is_file($path) ? (string) filemtime($path) : self::VERSION;
    }

    public static function enqueue() {
        if (!self::is_lab_request()) { return; }
        $css = 'assets/css/sc-lab-unified-workspace-shell-v01631.css';
        $js  = 'assets/js/sc-lab-unified-workspace-shell-v01631.js';
        wp_enqueue_style(
            'sc-lab-unified-workspace-shell-v01631',
            SC_LAB_URL . $css,
            array('sc-lab-institutional-governance-v01630'),
            self::asset_token($css)
        );
        wp_enqueue_script(
            'sc-lab-unified-workspace-shell-v01631',
            SC_LAB_URL . $js,
            array('sc-lab-institutional-governance-v01630', 'sc-lab-canonical-repair-v015701'),
            self::asset_token($js),
            true
        );
        wp_localize_script('sc-lab-unified-workspace-shell-v01631', 'SCLabUnifiedWorkspaceShellV01631', array(
            'version' => self::VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : self::VERSION,
            'defaultWorkspace' => 'overview',
            'specialistWorkspaceCount' => 11,
            'singleVisibleWorkspace' => true,
            'progressiveModuleNavigation' => true,
        ));
    }
}
