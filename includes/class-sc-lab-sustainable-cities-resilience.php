<?php
/**
 * Sustainable Cities and Urban Resilience integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Sustainable_Cities_Resilience_Integration {
    const VERSION = '0.15.0';

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
            'sc_lab_sustainable_cities_resilience',
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
     * Enqueue v0.15.0 assets.
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
            'sc-lab-sustainable-cities-resilience',
            $base_url
                . 'js/modules/sustainable-cities-resilience-lab.js',
            array(),
            self::VERSION,
            true
        );
    }

    /**
     * Load assets on the main Lab or focused workspace.
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
                'sc_lab_sustainable_cities_resilience'
            )
        ) {
            self::enqueue_assets();
        }
    }

    /**
     * Render the focused Sustainable Cities workspace.
     *
     * @param array<string, mixed> $attributes Shortcode attributes.
     * @return string
     */
    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Sustainable Cities and Urban Resilience',
                'description' =>
                    'Auditable analysis for urban resource flows, decarbonization, climate adaptation, critical infrastructure, equity, and integrated city scenarios.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_sustainable_cities_resilience'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-sustainable-cities-resilience"
            data-sc-lab-version="0.15.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/SUSTAINABLE-CITIES-RESILIENCE
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div data-sustainable-cities-resilience-root></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These methods support transparent screening,
                    comparative analysis, documentation, and scenario
                    design. They do not replace adopted plans, official
                    emissions inventories, calibrated hazard models,
                    infrastructure engineering, public-health or clinical
                    assessment, environmental review, public engagement,
                    legal requirements, or qualified professional judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Sustainable_Cities_Resilience_Integration::boot();
