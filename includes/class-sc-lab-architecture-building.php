<?php
/**
 * Architecture and Building Performance integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Architecture_Building_Integration {
    const VERSION = '0.13.0';

    /**
     * Register hooks.
     *
     * @return void
     */
    public static function boot() {
        add_shortcode(
            'sc_lab_architecture_building',
            array(__CLASS__, 'shortcode')
        );

        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue')
        );
    }

    /**
     * Enqueue the v0.13.0 assets.
     *
     * @return void
     */
    public static function enqueue_assets() {
        $base_url = defined('SC_LAB_URL')
            ? trailingslashit((string) constant('SC_LAB_URL')) . 'assets/'
            : trailingslashit(
                plugins_url('../assets', __FILE__)
            );

        wp_enqueue_style(
            'sc-lab-v0130',
            $base_url . 'css/sc-lab-v0130.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-architecture-building',
            $base_url . 'js/modules/architecture-building-lab.js',
            array(),
            self::VERSION,
            true
        );
    }

    /**
     * Load assets on the main Lab page or the focused workspace.
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
            || has_shortcode($content, 'sc_lab_architecture_building')
        ) {
            self::enqueue_assets();
        }
    }

    /**
     * Render the focused architecture and building-performance workspace.
     *
     * @param array<string, mixed> $attributes Shortcode attributes.
     * @return string
     */
    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Architecture and Building Performance',
                'description' =>
                    'Auditable calculations for building geometry, envelope performance, daylight, ventilation, energy, water, carbon, acoustics, and resilience.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_architecture_building'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-architecture-building"
            data-sc-lab-version="0.13.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/ARCHITECTURE-BUILDING
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div data-architecture-building-root></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These transparent screening calculations do not replace
                    whole-building simulation, calibrated energy models,
                    hygrothermal analysis, daylight or glare simulation,
                    code compliance, commissioning, field verification, or
                    licensed architectural and engineering judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Architecture_Building_Integration::boot();
