<?php
/** Biosignal visualization, annotation, and comparison interface. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Biosignal_Visualization_Comparison_V0232 {
    const VERSION = '0.23.2';
    const SCRIPT_HANDLE = 'sc-lab-biosignal-visualization-v0232';
    const STYLE_HANDLE = 'sc-lab-biosignal-visualization-v0232-style';
    const SHORTCODE = 'sc_lab_biosignal_visualization_comparison';
    public static function boot() {
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), 60100);
        if (function_exists('add_shortcode')) { add_shortcode(self::SHORTCODE, array(__CLASS__, 'shortcode')); }
    }
    private static function asset_url($relative) {
        if (defined('SC_LAB_URL')) { return trailingslashit((string) constant('SC_LAB_URL')) . 'assets/' . ltrim((string) $relative, '/'); }
        return plugin_dir_url(dirname(__DIR__) . '/sustainable-catalyst-lab.php') . 'assets/' . ltrim((string) $relative, '/');
    }
    private static function asset_path($relative) { return dirname(__DIR__) . '/assets/' . ltrim((string) $relative, '/'); }
    private static function asset_version($relative) { $path=self::asset_path($relative); return is_file($path) ? self::VERSION . '.' . filemtime($path) : self::VERSION; }
    public static function enqueue() {
        if (function_exists('is_admin') && is_admin()) { return; }
        if (class_exists('SC_Lab_Biosignal_Production_V0231') && is_callable(array('SC_Lab_Biosignal_Production_V0231','enqueue'))) { SC_Lab_Biosignal_Production_V0231::enqueue(); }
        $style='css/sc-lab-biosignal-visualization-comparison-v0232.css';
        $script='js/modules/biosignal-visualization-comparison-v0232.js';
        wp_enqueue_style(self::STYLE_HANDLE, self::asset_url($style), array(), self::asset_version($style));
        wp_enqueue_script(self::SCRIPT_HANDLE, self::asset_url($script), array(), self::asset_version($script), true);
    }
    public static function shortcode() { self::enqueue(); return '<div class="sc-lab-biosignal-visualization-shortcode" data-biosignal-visualization-root></div>'; }
}
SC_Lab_Biosignal_Visualization_Comparison_V0232::boot();
