<?php
/**
 * Civil panel route and visibility repair for Lab v0.20.x.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Civil_Panel_Router_V0200 {
    const VERSION = '0.20.0-civil-router.1';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            60000
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

    private static function asset_version($relative) {
        $path = dirname(__DIR__)
            . '/assets/'
            . ltrim((string) $relative, '/');

        if (is_file($path)) {
            return self::VERSION . '.' . filemtime($path);
        }

        return self::VERSION;
    }

    public static function enqueue() {
        if (is_admin()) {
            return;
        }

        $relative = 'js/modules/civil-panel-router-v0200.js';

        wp_enqueue_script(
            'sc-lab-civil-panel-router-v0200',
            self::asset_url() . $relative,
            array(),
            self::asset_version($relative),
            true
        );
    }
}

SC_Lab_Civil_Panel_Router_V0200::boot();
