<?php
/**
 * Rocket Propulsion and Spaceflight integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Rocket_Propulsion_Spaceflight_Integration {
    const VERSION = '0.19.0';

    public static function boot() {
        add_action('init', array(__CLASS__, 'register_shortcode'), 99);
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue'),
            99
        );
    }

    public static function register_shortcode() {
        add_shortcode(
            'sc_lab_rocket_propulsion_spaceflight',
            array(__CLASS__, 'shortcode')
        );
    }

    private static function asset_url() {
        if (defined('SC_LAB_URL')) {
            return trailingslashit((string) constant('SC_LAB_URL'))
                . 'assets/';
        }

        $plugin_root_file = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($plugin_root_file) . 'assets/';
    }

    public static function enqueue_assets() {
        $base_url = self::asset_url();

        wp_enqueue_style(
            'sc-lab-v0190',
            $base_url . 'css/sc-lab-v0190.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-rocket-propulsion-spaceflight',
            $base_url
                . 'js/modules/rocket-propulsion-spaceflight-lab.js',
            array(),
            self::VERSION,
            true
        );
    }

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
                'sc_lab_rocket_propulsion_spaceflight'
            )
        ) {
            self::enqueue_assets();
        }
    }

    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Rocket Propulsion and Spaceflight',
                'description' =>
                    'Auditable educational and preliminary-design calculations for rocket performance, nozzle flow, launch-vehicle staging, ascent losses, orbital mechanics, spacecraft power and thermal systems, communications, and mission reliability.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_rocket_propulsion_spaceflight'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-rocket-propulsion-spaceflight"
            data-sc-lab-version="0.19.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/ROCKET-PROPULSION-SPACEFLIGHT
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div data-rocket-propulsion-spaceflight-root></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These transparent methods support education,
                    documentation, and preliminary civil-space systems
                    analysis. They do not replace tested engine data,
                    detailed combustion or turbomachinery models,
                    structural and thermal qualification, range-safety
                    analysis, launch licensing, flight software
                    verification, mission assurance, operational launch
                    procedures, or qualified propulsion, aerospace, and
                    spaceflight engineering judgment. The workspace is
                    not intended for weapon design or targeting.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Rocket_Propulsion_Spaceflight_Integration::boot();
