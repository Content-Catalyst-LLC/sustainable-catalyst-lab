<?php
/**
 * Molecular Analysis Validation and Provenance interface.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Molecular_Validation_Provenance_V0213 {
    const VERSION = '0.21.3';
    const SCRIPT_HANDLE =
        'sc-lab-molecular-validation-provenance-v0213';
    const STYLE_HANDLE =
        'sc-lab-molecular-validation-provenance-v0213-style';
    const SHORTCODE =
        'sc_lab_molecular_validation_provenance';

    public static function boot() {
        add_action(
            'init',
            array(__CLASS__, 'register_shortcode')
        );

        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            50030
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

        if (
            class_exists(
                'SC_Lab_Biochemistry_Visualization_Batch_V0212'
            )
            && is_callable(
                array(
                    'SC_Lab_Biochemistry_Visualization_Batch_V0212',
                    'enqueue',
                )
            )
        ) {
            SC_Lab_Biochemistry_Visualization_Batch_V0212::
                enqueue();
        }

        $style =
            'css/'
            . 'sc-lab-molecular-analysis-validation-provenance-v0213.css';
        $script =
            'js/modules/'
            . 'molecular-analysis-validation-provenance-v0213.js';

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
                'sc-lab-biochemistry-visualization-batch-v0212',
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
                    'Molecular Analysis Validation and Provenance',
                'description' =>
                    'Acceptance testing, analytical validation '
                    . 'dossiers, SHA-256 fingerprints, evidence '
                    . 'links, and tamper-evident provenance chains.',
            ),
            is_array($attributes) ? $attributes : array(),
            self::SHORTCODE
        );

        ob_start();
        ?>
        <section class="sc-lab-module">
            <header class="sc-lab-module-header">
                <p class="sc-lab-kicker">
                    LAB/MOLECULAR/VALIDATION
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
                data-molecular-validation-provenance-root
            ></div>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Molecular_Validation_Provenance_V0213::boot();
