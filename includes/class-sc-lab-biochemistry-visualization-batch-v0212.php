<?php
/**
 * Biochemistry Visualization and Batch Analysis.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biochemistry_Visualization_Batch_V0212 {
    const VERSION = '0.21.2';
    const SCRIPT_HANDLE =
        'sc-lab-biochemistry-visualization-batch-v0212';
    const STYLE_HANDLE =
        'sc-lab-biochemistry-visualization-batch-v0212-style';
    const SHORTCODE =
        'sc_lab_biochemistry_visualization_batch';

    public static function boot() {
        add_action(
            'init',
            array(__CLASS__, 'register_shortcode')
        );

        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            50020
        );
    }

    public static function register_shortcode() {
        add_shortcode(
            self::SHORTCODE,
            array(__CLASS__, 'shortcode')
        );
    }

    private static function asset_url($relative) {
        if (defined('SC_LAB_URL')) {
            return trailingslashit(
                (string) constant('SC_LAB_URL')
            )
                . 'assets/'
                . ltrim((string) $relative, '/');
        }

        $root_file = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($root_file)
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

        if (is_file($path)) {
            return self::VERSION . '.' . filemtime($path);
        }

        return self::VERSION;
    }

    public static function enqueue() {
        if (is_admin()) {
            return;
        }

        if (
            class_exists(
                'SC_Lab_Biochemistry_Molecular_Analysis'
            )
            && is_callable(
                array(
                    'SC_Lab_Biochemistry_Molecular_Analysis',
                    'enqueue_assets',
                )
            )
        ) {
            SC_Lab_Biochemistry_Molecular_Analysis::
                enqueue_assets();
        }

        $style =
            'css/'
            . 'sc-lab-biochemistry-visualization-batch-v0212.css';
        $script =
            'js/modules/'
            . 'biochemistry-visualization-batch-v0212.js';

        wp_enqueue_style(
            self::STYLE_HANDLE,
            self::asset_url($style),
            array(),
            self::asset_version($style)
        );

        wp_enqueue_script(
            self::SCRIPT_HANDLE,
            self::asset_url($script),
            array(
                'sc-lab-biochemistry-molecular-analysis-v0210',
            ),
            self::asset_version($script),
            true
        );
    }

    public static function shortcode($attributes = array()) {
        self::enqueue();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Biochemistry Visualization and Batch Analysis',
                'description' =>
                    'Scientific plots, replicate analysis, '
                    . 'quality-control statistics, and '
                    . 'reproducible exports for the validated '
                    . 'Biochemistry method catalog.',
            ),
            is_array($attributes) ? $attributes : array(),
            self::SHORTCODE
        );

        ob_start();
        ?>
        <section class="sc-lab-module">
            <header class="sc-lab-module-header">
                <p class="sc-lab-kicker">
                    LAB/BIOCHEMISTRY/ANALYSIS
                </p>
                <h2>
                    <?php echo esc_html($attributes['title']); ?>
                </h2>
                <p>
                    <?php echo esc_html(
                        $attributes['description']
                    ); ?>
                </p>
            </header>

            <div
                data-biochemistry-visualization-batch-root
            ></div>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Biochemistry_Visualization_Batch_V0212::boot();
