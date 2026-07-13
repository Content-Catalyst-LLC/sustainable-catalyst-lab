<?php
/**
 * v0.20.0 engineering-interface loading repair.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Engineering_Interface_Repair_V0200 {
    const VERSION = '0.20.0-repair.1';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'conditionally_enqueue'),
            999
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

    private static function relevant_shortcode($content) {
        foreach (
            array(
                'sc_lab_app',
                'sc_lab_electrical',
                'sc_lab_mechanical_thermal',
                'sc_lab_civil_infrastructure',
            )
            as $shortcode
        ) {
            if (has_shortcode($content, $shortcode)) {
                return true;
            }
        }

        return false;
    }

    public static function conditionally_enqueue() {
        global $post;

        if (!is_object($post) || empty($post->post_content)) {
            return;
        }

        if (!self::relevant_shortcode((string) $post->post_content)) {
            return;
        }

        $dependencies = array();

        if (wp_script_is('sc-lab-app', 'registered')) {
            $dependencies[] = 'sc-lab-app';
        }

        if (
            wp_script_is(
                'sc-lab-civil-infrastructure-v0150',
                'registered'
            )
        ) {
            $dependencies[] =
                'sc-lab-civil-infrastructure-v0150';
        }

        wp_enqueue_script(
            'sc-lab-engineering-interface-repair-v0200',
            self::asset_url()
                . 'js/modules/'
                . 'engineering-interface-repair-v0200.js',
            $dependencies,
            self::VERSION,
            true
        );
    }
}

SC_Lab_Engineering_Interface_Repair_V0200::boot();
