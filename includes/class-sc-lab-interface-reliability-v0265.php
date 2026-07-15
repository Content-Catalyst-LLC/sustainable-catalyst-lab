<?php
/**
 * Sustainable Catalyst Lab v0.26.5 mobile, accessibility, and interface reliability.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Interface_Reliability_V0265 {
    const VERSION = '0.26.5';
    const REPORT_OPTION = 'sc_lab_interface_health_v0265';
    private static $initialized = false;
    private static $front_assets = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue_front'), 95);
        add_action('admin_menu', array(__CLASS__, 'admin_menu'), 55);
        add_action('admin_enqueue_scripts', array(__CLASS__, 'admin_assets'));
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe']) || isset($_GET['sc_lab_validation']) || isset($_GET['sc_lab_interface_audit'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    public static function maybe_enqueue_front() {
        if (!self::is_lab_request() || self::$front_assets) { return; }
        self::$front_assets = true;
        $style = 'assets/css/sc-lab-interface-v0265.css';
        $script = 'assets/js/sc-lab-interface-v0265.js';
        wp_enqueue_style('sc-lab-interface-v0265', SC_LAB_URL . $style, array('sc-lab-app'), self::asset_version($style));
        wp_enqueue_script('sc-lab-interface-v0265', SC_LAB_URL . $script, array('sc-lab-app'), self::asset_version($script), true);
        wp_localize_script('sc-lab-interface-v0265', 'SCLabInterfaceConfigV0265', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'requestedModule' => isset($_GET['sc_lab_module']) ? sanitize_key(wp_unslash($_GET['sc_lab_module'])) : null,
            'autoAudit' => isset($_GET['sc_lab_interface_audit']),
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/interface/v0265/health')),
            'reducedMotion' => __('Reduced motion is active.', 'sustainable-catalyst-lab'),
            'navigationOpened' => __('Laboratory navigation opened.', 'sustainable-catalyst-lab'),
            'navigationClosed' => __('Laboratory navigation closed.', 'sustainable-catalyst-lab'),
        ));
    }

    public static function admin_menu() {
        add_submenu_page('options-general.php', 'Lab Interface Health', 'Lab Interface Health', 'manage_options', 'sc-lab-interface-health', array(__CLASS__, 'admin_page'));
    }

    public static function admin_assets($hook) {
        if ($hook !== 'settings_page_sc-lab-interface-health') { return; }
        $style = 'assets/css/sc-lab-interface-v0265.css';
        $script = 'assets/js/sc-lab-interface-health-admin-v0265.js';
        wp_enqueue_style('sc-lab-interface-v0265-admin', SC_LAB_URL . $style, array(), self::asset_version($style));
        wp_enqueue_script('sc-lab-interface-health-admin-v0265', SC_LAB_URL . $script, array(), self::asset_version($script), true);
        wp_localize_script('sc-lab-interface-health-admin-v0265', 'SCLabInterfaceHealthAdminConfigV0265', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'labUrl' => esc_url_raw(apply_filters('sc_lab_interface_health_lab_url', home_url('/lab/'))),
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/interface/v0265/health')),
            'saveUrl' => esc_url_raw(rest_url('sc-lab/v1/interface/v0265/reports')),
            'latestUrl' => esc_url_raw(rest_url('sc-lab/v1/interface/v0265/reports/latest')),
            'nonce' => wp_create_nonce('wp_rest'),
        ));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/interface/v0265/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/interface/v0265/reports', array('methods'=>WP_REST_Server::CREATABLE,'callback'=>array(__CLASS__,'save_report'),'permission_callback'=>array(__CLASS__,'can_manage')));
        register_rest_route('sc-lab/v1', '/interface/v0265/reports/latest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'latest_report'),'permission_callback'=>array(__CLASS__,'can_manage')));
    }

    public static function can_manage() { return current_user_can('manage_options'); }

    private static function required_files() {
        return array(
            'assets/css/sc-lab-interface-v0265.css',
            'assets/js/sc-lab-interface-v0265.js',
            'assets/js/sc-lab-interface-health-admin-v0265.js',
            'contracts/interface-health-v0265.schema.json',
            'docs/MOBILE_ACCESSIBILITY_INTERFACE_RELIABILITY_V0265.md',
            'includes/class-sc-lab-interface-reliability-v0265.php',
            'templates/lab-app.php',
        );
    }

    public static function health() {
        $files = array();
        $ok = true;
        foreach (self::required_files() as $relative) {
            $exists = is_file(SC_LAB_DIR . $relative);
            $files[$relative] = array('exists'=>$exists,'sha256'=>$exists ? hash_file('sha256', SC_LAB_DIR . $relative) : null);
            $ok = $ok && $exists;
        }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'features'=>array(
                'responsiveLayout'=>true,
                'minimumTouchTargets'=>true,
                'keyboardTabs'=>true,
                'mobileNavigationFocusManagement'=>true,
                'screenReaderLiveRegions'=>true,
                'reducedMotion'=>true,
                'forcedColors'=>true,
                'accessibleTables'=>true,
                'accessibleVisualizations'=>true,
                'runtimeAudit'=>true,
            ),
            'files'=>$files,
            'latestReport'=>get_option(self::REPORT_OPTION, null),
            'time'=>gmdate('c'),
        ));
    }

    private static function sanitize_report_value($value, $depth = 0) {
        if ($depth > 8) { return null; }
        if (is_array($value)) {
            $out = array(); $count = 0;
            foreach ($value as $key => $item) {
                if ($count++ > 400) { break; }
                $safe_key = is_int($key) ? $key : sanitize_key((string) $key);
                $out[$safe_key] = self::sanitize_report_value($item, $depth + 1);
            }
            return $out;
        }
        if (is_bool($value) || is_int($value) || is_float($value) || is_null($value)) { return $value; }
        return substr(sanitize_textarea_field((string) $value), 0, 8000);
    }

    public static function save_report(WP_REST_Request $request) {
        $raw = $request->get_json_params();
        if (!is_array($raw)) { return new WP_Error('invalid_interface_report', 'A JSON interface-health report is required.', array('status'=>400)); }
        $report = self::sanitize_report_value($raw);
        $report['storedAt'] = gmdate('c');
        $report['storedBy'] = get_current_user_id();
        $report['runtimeVersion'] = self::VERSION;
        update_option(self::REPORT_OPTION, $report, false);
        return rest_ensure_response(array('ok'=>true,'storedAt'=>$report['storedAt'],'summary'=>isset($report['summary'])?$report['summary']:null));
    }

    public static function latest_report() {
        return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'report'=>get_option(self::REPORT_OPTION, null)));
    }

    public static function admin_page() {
        if (!current_user_can('manage_options')) { return; }
        ?>
        <div class="wrap sc-lab-interface-admin-v0265" data-sc-lab-interface-admin-v0265>
          <h1>Sustainable Catalyst Lab Interface Health</h1>
          <p>Runs a browser audit at phone, tablet, and desktop widths. It checks overflow, touch targets, keyboard tabs, accessible names, live regions, tables, visualizations, focus behavior, and active-panel integrity.</p>
          <div class="sc-lab-interface-admin-toolbar-v0265">
            <button type="button" class="button button-primary" data-interface-run-phone>Audit phone</button>
            <button type="button" class="button" data-interface-run-tablet>Audit tablet</button>
            <button type="button" class="button" data-interface-run-desktop>Audit desktop</button>
            <button type="button" class="button" data-interface-run-all>Audit all viewports</button>
            <button type="button" class="button" data-interface-export>Export report</button>
            <button type="button" class="button" data-interface-refresh-server>Refresh server health</button>
          </div>
          <div class="sc-lab-interface-admin-summary-v0265" role="status" aria-live="polite" data-interface-summary>Ready to audit the Lab interface.</div>
          <div data-interface-server></div>
          <div class="sc-lab-interface-admin-grid-v0265">
            <section>
              <h2>Viewport runner</h2>
              <div class="sc-lab-interface-frame-shell-v0265" data-interface-frame-shell>
                <iframe title="Lab mobile and accessibility audit runner" data-interface-frame></iframe>
              </div>
            </section>
            <section>
              <h2>Audit findings</h2>
              <table class="widefat striped"><thead><tr><th>Viewport</th><th>Severity</th><th>Check</th><th>Details</th></tr></thead><tbody data-interface-rows></tbody></table>
            </section>
          </div>
          <details><summary>Raw report</summary><pre data-interface-json>No interface audit has been run.</pre></details>
        </div>
        <?php
    }
}
