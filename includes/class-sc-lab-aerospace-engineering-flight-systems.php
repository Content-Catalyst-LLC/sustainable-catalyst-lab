<?php
/**
 * Aerospace Engineering and Flight Systems integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Aerospace_Engineering_Flight_Systems_Integration {
    const VERSION = '0.18.0';

    /**
     * Register hooks.
     *
     * @return void
     */
    public static function boot() {
        add_action('init', array(__CLASS__, 'register_shortcode'), 99);
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue'),
            99
        );
    }

    /**
     * Register the focused shortcode.
     *
     * @return void
     */
    public static function register_shortcode() {
        add_shortcode(
            'sc_lab_aerospace_engineering_flight_systems',
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
     * Enqueue v0.18.0 assets.
     *
     * @return void
     */
    public static function enqueue_assets() {
        $base_url = self::asset_url();

        wp_enqueue_style(
            'sc-lab-v0180',
            $base_url . 'css/sc-lab-v0180.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-aerospace-engineering-flight-systems',
            $base_url
                . 'js/modules/aerospace-engineering-flight-systems-lab.js',
            array(),
            self::VERSION,
            true
        );
    }

    /**
     * Load assets on the main or focused Lab surface.
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
                'sc_lab_aerospace_engineering_flight_systems'
            )
        ) {
            self::enqueue_assets();
        }
    }

    /**
     * Render the focused workspace.
     *
     * @param array<string, mixed> $attributes Shortcode attributes.
     * @return string
     */
    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Aerospace Engineering and Flight Systems',
                'description' =>
                    'Auditable calculations for aerodynamics, flight mechanics, aircraft performance, stability and control, propulsion integration, structures and loads, aeroelastic screening, navigation, mission analysis, and flight-system reliability.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_aerospace_engineering_flight_systems'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-aerospace-engineering-flight-systems"
            data-sc-lab-version="0.18.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/AEROSPACE-ENGINEERING-FLIGHT-SYSTEMS
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div
                data-aerospace-engineering-flight-systems-root
            ></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These transparent engineering-screening methods do
                    not replace certified aerodynamic data, wind-tunnel
                    or flight testing, approved flight manuals, detailed
                    stability-and-control analysis, propulsion maps,
                    finite-element or aeroelastic models, safety
                    assessment, airworthiness requirements, operational
                    limitations, or qualified aerospace engineering and
                    flight-test judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Aerospace_Engineering_Flight_Systems_Integration::boot();
