<?php
/**
 * Civil and Infrastructure formula-interface repair.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Civil_Infrastructure_Interface_Repair {
    const VERSION = '0.15.0';

    /**
     * Register the late shortcode override and assets.
     *
     * @return void
     */
    public static function boot() {
        add_action(
            'init',
            array(__CLASS__, 'register_shortcode'),
            99
        );

        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue'),
            100
        );
    }

    /**
     * Override the fragile original focused shortcode.
     *
     * @return void
     */
    public static function register_shortcode() {
        add_shortcode(
            'sc_lab_civil_infrastructure',
            array(__CLASS__, 'shortcode')
        );
    }

    /**
     * Return the plugin asset URL.
     *
     * @return string
     */
    private static function asset_url() {
        if (defined('SC_LAB_URL')) {
            return trailingslashit((string) constant('SC_LAB_URL'))
                . 'assets/';
        }

        $plugin_root_file = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($plugin_root_file) . 'assets/';
    }

    /**
     * Load the repaired civil interface.
     *
     * @return void
     */
    public static function enqueue_assets() {
        $base_url = self::asset_url();

        wp_enqueue_style(
            'sc-lab-v0150',
            $base_url . 'css/sc-lab-v0150.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-civil-infrastructure-v0150',
            $base_url
                . 'js/modules/civil-infrastructure-lab-v0150.js',
            array(),
            self::VERSION,
            true
        );
    }

    /**
     * Enqueue the repaired module on both Lab surfaces.
     *
     * @return void
     */
    public static function conditionally_enqueue() {
        global $post;

        if (!is_object($post) || empty($post->post_content)) {
            return;
        }

        $content = (string) $post->post_content;

        if (
            has_shortcode($content, 'sc_lab_app')
            || has_shortcode(
                $content,
                'sc_lab_civil_infrastructure'
            )
        ) {
            self::enqueue_assets();
        }
    }

    /**
     * Render a reliable focused Civil and Infrastructure workspace.
     *
     * @param array<string, mixed> $attributes Shortcode attributes.
     * @return string
     */
    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Civil Engineering and Infrastructure Systems',
                'description' =>
                    'Formula-visible calculations for structures, geotechnical systems, hydrology, transportation, water and wastewater, infrastructure risk, reliability, lifecycle cost, resilience, and embodied carbon.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_civil_infrastructure'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-civil-infrastructure-repaired"
            data-sc-lab-version="0.15.0"
            data-civil-interface-repair="0.15.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/CIVIL-INFRASTRUCTURE
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div data-civil-infrastructure-root></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These formula-visible screening calculations do not
                    replace design codes, site investigation, calibrated
                    models, detailed load combinations, permitting,
                    inspection, construction documents, or licensed civil,
                    structural, geotechnical, transportation, water, and
                    infrastructure engineering judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Civil_Infrastructure_Interface_Repair::boot();
