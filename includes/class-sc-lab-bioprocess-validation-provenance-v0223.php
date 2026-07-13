<?php
/**
 * Bioprocess validation and provenance interface.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Bioprocess_Validation_Provenance_V0223 {
    const VERSION = '0.22.3';
    const SCRIPT_HANDLE =
        'sc-lab-bioprocess-validation-v0223';
    const STYLE_HANDLE =
        'sc-lab-bioprocess-validation-v0223-style';
    const SHORTCODE =
        'sc_lab_bioprocess_validation_provenance';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'register_assets'),
            60060
        );

        if (function_exists('add_shortcode')) {
            add_shortcode(
                self::SHORTCODE,
                array(__CLASS__, 'shortcode')
            );
        }
    }

    private static function asset_url($relative) {
        if (defined('SC_LAB_URL')) {
            return trailingslashit(
                (string) constant('SC_LAB_URL')
            )
                . 'assets/'
                . ltrim((string) $relative, '/');
        }

        return plugin_dir_url(
            dirname(__DIR__)
            . '/sustainable-catalyst-lab.php'
        )
            . 'assets/'
            . ltrim((string) $relative, '/');
    }

    private static function asset_path($relative) {
        return dirname(__DIR__)
            . '/assets/'
            . ltrim((string) $relative, '/');
    }

    private static function asset_version($relative) {
        $path = self::asset_path($relative);

        return is_file($path)
            ? self::VERSION . '.' . filemtime($path)
            : self::VERSION;
    }

    public static function register_assets() {
        if (is_admin()) {
            return;
        }

        if (
            class_exists(
                'SC_Lab_Bioprocess_Monitoring_Control_V0222'
            )
            && is_callable(
                array(
                    'SC_Lab_Bioprocess_Monitoring_Control_V0222',
                    'enqueue',
                )
            )
        ) {
            SC_Lab_Bioprocess_Monitoring_Control_V0222::
                enqueue();
        }

        $style =
            'css/'
            . 'sc-lab-bioprocess-validation-provenance-v0223.css';
        $script =
            'js/modules/'
            . 'bioprocess-validation-provenance-v0223.js';

        wp_enqueue_style(
            self::STYLE_HANDLE,
            self::asset_url($style),
            array(),
            self::asset_version($style)
        );

        wp_enqueue_script(
            self::SCRIPT_HANDLE,
            self::asset_url($script),
            array(),
            self::asset_version($script),
            true
        );
    }

    public static function enqueue() {
        self::register_assets();
    }

    public static function shortcode() {
        self::register_assets();

        return (
            '<div '
            . 'class="sc-lab-bioprocess-validation-shortcode" '
            . 'data-bioprocess-validation-provenance-root'
            . '></div>'
        );
    }
}

SC_Lab_Bioprocess_Validation_Provenance_V0223::boot();
