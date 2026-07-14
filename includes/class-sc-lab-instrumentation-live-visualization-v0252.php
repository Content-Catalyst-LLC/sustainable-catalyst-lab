<?php
/**
 * Live sensor and instrument visualization interface.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Instrumentation_Live_Visualization_V0252 {
    const VERSION = '0.25.2';
    const ENGINE_VERSION = '0.25.0';
    const PRODUCTION_VERSION = '0.25.1';
    const SHORTCODE = 'sc_lab_live_sensor_instrument_visualization';
    const SCRIPT_HANDLE = 'sc-lab-instrumentation-live-v0252';
    const STYLE_HANDLE = 'sc-lab-instrumentation-live-v0252-style';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            60110
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
            ) . 'assets/' . ltrim((string) $relative, '/');
        }

        return plugin_dir_url(
            dirname(__DIR__) . '/sustainable-catalyst-lab.php'
        ) . 'assets/' . ltrim((string) $relative, '/');
    }

    private static function asset_path($relative) {
        return dirname(__DIR__) . '/assets/' . ltrim((string) $relative, '/');
    }

    private static function asset_version($relative) {
        $path = self::asset_path($relative);

        return is_file($path)
            ? self::VERSION . '.' . filemtime($path)
            : self::VERSION;
    }

    public static function enqueue() {
        if (function_exists('is_admin') && is_admin()) {
            return;
        }

        if (
            class_exists('SC_Lab_Instrumentation_Production_V0251')
            && is_callable(
                array(
                    'SC_Lab_Instrumentation_Production_V0251',
                    'enqueue',
                )
            )
        ) {
            SC_Lab_Instrumentation_Production_V0251::enqueue();
        }

        $style = 'css/sc-lab-instrumentation-live-visualization-v0252.css';
        $script = 'js/modules/instrumentation-live-visualization-v0252.js';

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

    public static function shortcode() {
        self::enqueue();

        return (
            '<div '
            . 'class="sc-lab-instrumentation-live-shortcode" '
            . 'data-instrumentation-live-visualization-root'
            . '></div>'
        );
    }
}

SC_Lab_Instrumentation_Live_Visualization_V0252::boot();
