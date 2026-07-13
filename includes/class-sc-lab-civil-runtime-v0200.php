<?php
/**
 * Single authoritative Civil runtime for Lab v0.20.x.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Civil_Runtime_V0200 {
    const VERSION = '0.20.0-civil-runtime.1';
    const MODULE_HANDLE = 'sc-lab-civil-runtime-module-v0200';
    const BOOTSTRAP_HANDLE = 'sc-lab-civil-runtime-bootstrap-v0200';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            50000
        );

        add_filter(
            'script_loader_tag',
            array(__CLASS__, 'filter_script_tag'),
            50000,
            3
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

    private static function asset_path($relative) {
        return dirname(__DIR__)
            . '/assets/'
            . ltrim((string) $relative, '/');
    }

    private static function version_for($relative) {
        $path = self::asset_path($relative);

        if (is_file($path)) {
            return self::VERSION . '.' . filemtime($path);
        }

        return self::VERSION;
    }

    private static function is_civil_source($source) {
        $path = wp_parse_url((string) $source, PHP_URL_PATH);

        if (!is_string($path)) {
            return false;
        }

        return (
            strpos($path, '/civil-infrastructure-lab.js') !== false
            || strpos(
                $path,
                '/civil-infrastructure-lab-v0150.js'
            ) !== false
            || strpos(
                $path,
                '/civil-infrastructure-direct-loader-v0200.js'
            ) !== false
            || strpos(
                $path,
                '/civil-infrastructure-runtime-v0200.js'
            ) !== false
        );
    }

    private static function remove_competing_scripts() {
        global $wp_scripts;

        if (
            !is_object($wp_scripts)
            || !isset($wp_scripts->registered)
            || !is_array($wp_scripts->registered)
        ) {
            return;
        }

        foreach ($wp_scripts->registered as $handle => $registered) {
            if (
                $handle === self::MODULE_HANDLE
                || $handle === self::BOOTSTRAP_HANDLE
            ) {
                continue;
            }

            $source = isset($registered->src)
                ? (string) $registered->src
                : '';

            if (!self::is_civil_source($source)) {
                continue;
            }

            wp_dequeue_script($handle);
            wp_deregister_script($handle);
        }
    }

    public static function enqueue() {
        if (is_admin()) {
            return;
        }

        self::remove_competing_scripts();

        $module_relative =
            'js/modules/civil-infrastructure-lab-v0150.js';
        $bootstrap_relative =
            'js/modules/civil-infrastructure-runtime-v0200.js';

        wp_enqueue_script(
            self::MODULE_HANDLE,
            self::asset_url() . $module_relative,
            array(),
            self::version_for($module_relative),
            true
        );

        wp_enqueue_script(
            self::BOOTSTRAP_HANDLE,
            self::asset_url() . $bootstrap_relative,
            array(self::MODULE_HANDLE),
            self::version_for($bootstrap_relative),
            true
        );
    }

    public static function filter_script_tag(
        $tag,
        $handle,
        $source
    ) {
        if (!self::is_civil_source($source)) {
            return $tag;
        }

        if (
            $handle === self::MODULE_HANDLE
            || $handle === self::BOOTSTRAP_HANDLE
        ) {
            return $tag;
        }

        return '';
    }
}

SC_Lab_Civil_Runtime_V0200::boot();
