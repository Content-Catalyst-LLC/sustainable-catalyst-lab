<?php
/**
 * Biochemistry and Molecular Analysis interface.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biochemistry_Molecular_Analysis {
    const VERSION = '0.21.0';
    const SHORTCODE =
        'sc_lab_biochemistry_molecular_analysis';

    public static function boot() {
        add_action(
            'init',
            array(__CLASS__, 'register_shortcode')
        );

        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'maybe_enqueue')
        );
    }

    public static function register_shortcode() {
        add_shortcode(
            self::SHORTCODE,
            array(__CLASS__, 'shortcode')
        );
    }

    private static function asset_url() {
        if (defined('SC_LAB_URL')) {
            return trailingslashit(
                (string) constant('SC_LAB_URL')
            ) . 'assets/';
        }

        $plugin_root = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($plugin_root) . 'assets/';
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

    public static function enqueue_assets() {
        $style = 'css/sc-lab-v0210.css';
        $script =
            'js/modules/biochemistry-molecular-analysis.js';

        wp_enqueue_style(
            'sc-lab-biochemistry-molecular-analysis-v0210',
            self::asset_url() . $style,
            array(),
            self::version_for($style)
        );

        wp_enqueue_script(
            'sc-lab-biochemistry-molecular-analysis-v0210',
            self::asset_url() . $script,
            array(),
            self::version_for($script),
            true
        );
    }

    public static function maybe_enqueue() {
        global $post;

        if (!is_object($post) || empty($post->post_content)) {
            return;
        }

        $content = (string) $post->post_content;

        if (
            has_shortcode($content, 'sc_lab_app')
            || has_shortcode($content, self::SHORTCODE)
        ) {
            self::enqueue_assets();
        }
    }

    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Biochemistry and Molecular Analysis',
                'description' =>
                    'Auditable calculations for biomolecule '
                    . 'quantification, proteins, enzyme kinetics, '
                    . 'nucleic acids, binding, buffers, '
                    . 'spectroscopy, separations, and laboratory '
                    . 'quality control.',
            ),
            is_array($attributes) ? $attributes : array(),
            self::SHORTCODE
        );

        ob_start();
        ?>
        <section
            class="sc-lab-panel sc-lab-module"
            data-lab-module="biochemistry-molecular-analysis"
            data-module-panel="biochemistry-molecular-analysis"
        >
            <header class="sc-lab-module-header">
                <p class="sc-lab-kicker">
                    LAB/BIOCHEMISTRY
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
                data-biochemistry-molecular-analysis-root
            ></div>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Biochemistry_Molecular_Analysis::boot();
