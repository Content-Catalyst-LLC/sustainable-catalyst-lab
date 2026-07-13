<?php
/**
 * Urban Planning and Spatial Systems integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Urban_Planning_Spatial_Integration {
    const VERSION = '0.14.0';

    /**
     * Register the focused shortcode and conditional assets.
     *
     * @return void
     */
    public static function boot() {
        add_shortcode(
            'sc_lab_urban_planning_spatial',
            array(__CLASS__, 'shortcode')
        );

        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue')
        );
    }

    /**
     * Return the plugin-root asset URL.
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
     * Enqueue the v0.14.0 browser assets.
     *
     * @return void
     */
    public static function enqueue_assets() {
        $base_url = self::asset_url();

        wp_enqueue_style(
            'sc-lab-v0140',
            $base_url . 'css/sc-lab-v0140.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-urban-planning-spatial',
            $base_url . 'js/modules/urban-planning-spatial-lab.js',
            array(),
            self::VERSION,
            true
        );
    }

    /**
     * Load assets for either the main Lab or focused workspace.
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
                'sc_lab_urban_planning_spatial'
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
                    'Urban Planning and Spatial Systems',
                'description' =>
                    'Auditable calculations for land use, accessibility, mobility, networks, GIS, public services, equity, resilience, and urban scenarios.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_urban_planning_spatial'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-urban-planning-spatial"
            data-sc-lab-version="0.14.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/URBAN-PLANNING-SPATIAL
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div data-urban-planning-spatial-root></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These transparent screening methods do not replace
                    adopted plans, legal zoning interpretation, official
                    demographic forecasts, calibrated travel-demand models,
                    professional GIS workflows, infrastructure engineering,
                    environmental review, public engagement, or qualified
                    planning and design judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Urban_Planning_Spatial_Integration::boot();
