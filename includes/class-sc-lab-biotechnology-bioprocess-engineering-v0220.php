<?php
/**
 * Biotechnology and Bioprocess Engineering public interface.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biotechnology_Bioprocess_Engineering_V0220 {
    const VERSION = '0.22.0';
    const SCRIPT_HANDLE =
        'sc-lab-biotechnology-bioprocess-v0220';
    const STYLE_HANDLE =
        'sc-lab-biotechnology-bioprocess-v0220-style';
    const SHORTCODE =
        'sc_lab_biotechnology_bioprocess_engineering';

    public static function boot() {
        add_action(
            'init',
            array(__CLASS__, 'register_shortcode')
        );
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            50040
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

        return plugin_dir_url(
            dirname(__DIR__)
            . '/sustainable-catalyst-lab.php'
        )
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

        return is_file($path)
            ? self::VERSION . '.' . filemtime($path)
            : self::VERSION;
    }

    public static function enqueue() {
        if (is_admin()) {
            return;
        }

        $style =
            'css/'
            . 'sc-lab-biotechnology-bioprocess-engineering-v0220.css';
        $script =
            'js/modules/'
            . 'biotechnology-bioprocess-engineering-v0220.js';
        $dependencies = array();

        if (
            wp_script_is(
                'sc-lab-molecular-validation-provenance-v0213',
                'registered'
            )
        ) {
            $dependencies[] =
                'sc-lab-molecular-validation-provenance-v0213';
        }

        wp_enqueue_style(
            self::STYLE_HANDLE,
            self::asset_url($style),
            array(),
            self::asset_version($style)
        );

        wp_enqueue_script(
            self::SCRIPT_HANDLE,
            self::asset_url($script),
            $dependencies,
            self::asset_version($script),
            true
        );
    }

    public static function shortcode($attributes = array()) {
        self::enqueue();
        $attributes = shortcode_atts(
            array(
                'title' =>
                    'Biotechnology and Bioprocess Engineering',
                'description' =>
                    'Cell growth, reactor balances, feed strategy, '
                    . 'continuous culture, oxygen transfer, mixing, '
                    . 'scale-up, production, and downstream recovery.',
            ),
            is_array($attributes) ? $attributes : array(),
            self::SHORTCODE
        );

        ob_start();
        ?>
        <section class="sc-lab-module">
            <header class="sc-lab-module-header">
                <p class="sc-lab-kicker">
                    LAB/BIOTECHNOLOGY/BIOPROCESS
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
            <div data-biotechnology-bioprocess-root></div>
        </section>
        <?php

        return (string) ob_get_clean();
    }
}

SC_Lab_Biotechnology_Bioprocess_Engineering_V0220::boot();
