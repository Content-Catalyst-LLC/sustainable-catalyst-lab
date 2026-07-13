<?php
/**
 * Circular Economy and Industrial Ecology integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Circular_Economy_Industrial_Ecology_Integration {
    const VERSION = '0.16.0';

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
            'sc_lab_circular_economy_industrial_ecology',
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
     * Enqueue v0.16.0 assets.
     *
     * @return void
     */
    public static function enqueue_assets() {
        $base_url = self::asset_url();

        wp_enqueue_style(
            'sc-lab-v0160',
            $base_url . 'css/sc-lab-v0160.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-circular-economy-industrial-ecology',
            $base_url
                . 'js/modules/circular-economy-industrial-ecology-lab.js',
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
                'sc_lab_circular_economy_industrial_ecology'
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
                    'Circular Economy and Industrial Ecology',
                'description' =>
                    'Auditable analysis for material flows, circular products, waste prevention, industrial symbiosis, lifecycle impacts, resource productivity, and circular transition scenarios.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_circular_economy_industrial_ecology'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-circular-economy-industrial-ecology"
            data-sc-lab-version="0.16.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/CIRCULAR-ECONOMY-INDUSTRIAL-ECOLOGY
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div
                data-circular-economy-industrial-ecology-root
            ></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These transparent screening methods do not replace
                    audited material-flow accounts, product engineering,
                    facility-specific process models, verified lifecycle
                    assessment, regulatory waste reporting, contractual
                    due diligence, market studies, or qualified industrial,
                    environmental, financial, and policy judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Circular_Economy_Industrial_Ecology_Integration::boot();
