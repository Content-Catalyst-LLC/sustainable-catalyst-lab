<?php
/**
 * Microbiology Laboratory integration.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Microbiology_Laboratory_Integration {
    const VERSION = '0.20.0';

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
            'sc_lab_microbiology_laboratory',
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
            'sc-lab-v0200',
            $base_url . 'css/sc-lab-v0200.css',
            array(),
            self::VERSION
        );

        wp_enqueue_script(
            'sc-lab-microbiology-laboratory',
            $base_url . 'js/modules/microbiology-laboratory.js',
            array('sc-lab-core', 'sc-lab-projects', 'sc-lab-runtime-v02631'),
            SC_LAB_VERSION . '.' . substr(hash_file('sha256', dirname(__DIR__) . '/assets/js/modules/microbiology-laboratory.js'), 0, 12),
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
                'sc_lab_microbiology_laboratory'
            )
        ) {
            self::enqueue_assets();
        }
    }

    public static function shortcode($attributes = array()) {
        self::enqueue_assets();

        $attributes = shortcode_atts(
            array(
                'title' => 'Microbiology Laboratory',
                'description' =>
                    'Auditable calculations for microbial growth, continuous culture, enumeration, microscopy, environmental microbiology, antimicrobial screening, microbial ecology, and laboratory quality control.',
            ),
            is_array($attributes) ? $attributes : array(),
            'sc_lab_microbiology_laboratory'
        );

        ob_start();
        ?>
        <section
            class="sc-lab-focused-workspace sc-lab-microbiology-laboratory"
            data-sc-lab-version="0.20.0"
        >
            <header class="sc-lab-panel-header">
                <div>
                    <p class="sc-lab-kicker">
                        LAB/MICROBIOLOGY
                    </p>
                    <h2><?php echo esc_html($attributes['title']); ?></h2>
                    <p><?php echo esc_html($attributes['description']); ?></p>
                </div>
            </header>

            <div data-microbiology-laboratory-root></div>

            <aside class="sc-lab-responsible-use">
                <strong>Responsible-use boundary</strong>
                <p>
                    These transparent methods support education,
                    environmental and industrial research, laboratory
                    documentation, quality control, and reproducible
                    analysis. They do not replace validated laboratory
                    protocols, biosafety review, organism-specific risk
                    assessment, accredited testing, clinical diagnosis,
                    treatment selection, public-health decisions, or
                    qualified microbiology and laboratory judgment.
                </p>
            </aside>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Microbiology_Laboratory_Integration::boot();
