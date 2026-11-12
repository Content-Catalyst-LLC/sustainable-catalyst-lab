<?php
/**
 * SC-FIG-04.1 — Lab / Research bridge pairing guard.
 *
 * Lab 0.163.1.8 renders the SC-FIG-04 views that sc-research-bridge 0.4.x releases. Bridge 0.3.x pins
 * Lab 0.163.1.7, so the two must not run together:
 *
 * - Lab refuses to activate while a 0.3.x bridge is active;
 * - while Lab is active, activating a 0.3.x bridge is refused;
 * - if plugin files are replaced without an activation, the figure-bundle renderer fails closed and an
 *   admin notice names the mismatch.
 *
 * Bridges older than 0.3 pin no Lab release and are not affected. The bridge is recognised by its plugin
 * header name, wherever it is installed.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Plugin_Compatibility_FIG041 {
    const BRIDGE_NAME = 'Sustainable Catalyst Research Bridge';
    const INCOMPATIBLE_BRIDGE = '/^0\.3\./';

    private static $incompatible = false;

    public static function init($main_file) {
        register_activation_hook($main_file, array(__CLASS__, 'on_activate'));
        add_action('activate_plugin', array(__CLASS__, 'on_plugin_activation'), 1, 1);
        add_action('admin_notices', array(__CLASS__, 'notice'));
    }

    private static function header($relative) {
        $file = WP_PLUGIN_DIR . '/' . ltrim((string) $relative, '/');
        if (!is_file($file)) { return null; }
        $h = get_file_data($file, array('Name' => 'Plugin Name', 'Version' => 'Version'));
        return is_array($h) ? $h : null;
    }

    private static function pins_another_lab($header) {
        return is_array($header) && $header['Name'] === self::BRIDGE_NAME && preg_match(self::INCOMPATIBLE_BRIDGE, (string) $header['Version']) === 1;
    }

    /** Version of an active bridge that is paired with another Lab release, or null. */
    public static function incompatible_bridge() {
        if (self::$incompatible !== false) { return self::$incompatible; }
        $active = (array) get_option('active_plugins', array());
        if (function_exists('is_multisite') && is_multisite()) {
            $active = array_merge($active, array_keys((array) get_site_option('active_sitewide_plugins', array())));
        }
        self::$incompatible = null;
        foreach ($active as $relative) {
            $h = self::header($relative);
            if (self::pins_another_lab($h)) { self::$incompatible = (string) $h['Version']; break; }
        }
        return self::$incompatible;
    }

    public static function message($bridge_version) {
        return sprintf('Sustainable Catalyst Lab %s cannot run with Sustainable Catalyst Research Bridge %s. Bridge 0.3.x is paired with Lab 0.163.1.7 and bridge 0.4.x with Lab 0.163.1.8; install a matching pair.',
            SC_LAB_RELEASE_VERSION, $bridge_version);
    }

    private static function refuse($bridge_version) {
        wp_die(esc_html(self::message($bridge_version)), 'Incompatible plugin combination', array('response' => 409, 'back_link' => true));
    }

    public static function on_activate() {
        self::$incompatible = false;
        $v = self::incompatible_bridge();
        if ($v !== null) { self::refuse($v); }
    }

    public static function on_plugin_activation($plugin) {
        $h = self::header($plugin);
        if (self::pins_another_lab($h)) { self::refuse((string) $h['Version']); }
    }

    public static function notice() {
        if (!current_user_can('activate_plugins')) { return; }
        $v = self::incompatible_bridge();
        if ($v === null) { return; }
        echo '<div class="notice notice-error"><p>' . esc_html(self::message($v) . ' Figure rendering is off until then.') . '</p></div>';
    }
}
