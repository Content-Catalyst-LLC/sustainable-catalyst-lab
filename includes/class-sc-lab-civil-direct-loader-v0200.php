<?php
/**
 * Direct, cache-busting loader for the repaired Civil interface.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Civil_Direct_Loader_V0200 {
    const VERSION = '0.20.0-civil-direct.1';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue'),
            10001
        );
    }

    private static function asset_url() {
        if (defined('SC_LAB_URL')) {
            return trailingslashit((string) constant('SC_LAB_URL'))
                . 'assets/';
        }

        $plugin_root_file = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($plugin_root_file) . 'assets/';
    }

    private static function is_relevant($content) {
        foreach (
            array(
                'sc_lab_app',
                'sc_lab_civil_infrastructure',
            )
            as $shortcode
        ) {
            if (has_shortcode($content, $shortcode)) {
                return true;
            }
        }

        return false;
    }

    public static function conditionally_enqueue() {
        global $post;

        if (!is_object($post) || empty($post->post_content)) {
            return;
        }

        if (!self::is_relevant((string) $post->post_content)) {
            return;
        }

        wp_enqueue_script(
            'sc-lab-civil-direct-loader-v0200',
            self::asset_url()
                . 'js/modules/'
                . 'civil-infrastructure-direct-loader-v0200.js',
            array(),
            self::VERSION,
            true
        );
    }
}

SC_Lab_Civil_Direct_Loader_V0200::boot();
