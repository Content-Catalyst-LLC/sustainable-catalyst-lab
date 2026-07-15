<?php
/**
 * Sustainable Catalyst Lab v0.26.6 production stability and recovery.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Production_Stability_V0266 {
    const VERSION = '0.26.6';
    const REPORT_OPTION = 'sc_lab_production_readiness_v0266';
    private static $initialized = false;
    private static $bootstrap_enqueued = false;
    private static $front_enqueued = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('admin_menu', array(__CLASS__, 'admin_menu'), 58);
        add_action('admin_enqueue_scripts', array(__CLASS__, 'admin_assets'));
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe']) || isset($_GET['sc_lab_stress']) || isset($_GET['sc_lab_recovery'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    /**
     * Enqueued by the primary plugin before project storage is initialized.
     */
    public static function enqueue_bootstrap() {
        if (self::$bootstrap_enqueued) { return; }
        self::$bootstrap_enqueued = true;
        $script = 'assets/js/sc-lab-production-bootstrap-v0266.js';
        wp_enqueue_script('sc-lab-production-bootstrap-v0266', SC_LAB_URL . $script, array(), self::asset_version($script), false);
        wp_localize_script('sc-lab-production-bootstrap-v0266', 'SCLabProductionBootstrapConfigV0266', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'safeMode' => isset($_GET['sc_lab_safe']),
            'recoveryMode' => isset($_GET['sc_lab_recovery']),
            'storageBudgetBytes' => 4194304,
            'projectKey' => 'scLabProjectsV010',
            'activeProjectKey' => 'scLabActiveProjectV010',
            'quarantineKey' => 'scLabRecoveryQuarantineV0266',
        ));
    }

    /**
     * Enqueued by the primary plugin after the Lab application runtime.
     */
    public static function enqueue_front() {
        if (self::$front_enqueued) { return; }
        self::$front_enqueued = true;
        $style = 'assets/css/sc-lab-production-stability-v0266.css';
        $script = 'assets/js/sc-lab-production-stability-v0266.js';
        wp_enqueue_style('sc-lab-production-stability-v0266', SC_LAB_URL . $style, array('sc-lab-app'), self::asset_version($style));
        wp_enqueue_script('sc-lab-production-stability-v0266', SC_LAB_URL . $script, array('sc-lab-app'), self::asset_version($script), true);
        wp_localize_script('sc-lab-production-stability-v0266', 'SCLabProductionConfigV0266', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'requestedModule' => isset($_GET['sc_lab_module']) ? sanitize_key(wp_unslash($_GET['sc_lab_module'])) : 'overview',
            'safeMode' => isset($_GET['sc_lab_safe']),
            'stressMode' => isset($_GET['sc_lab_stress']),
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/production/v0266/health')),
            'reportUrl' => esc_url_raw(rest_url('sc-lab/v1/production/v0266/reports')),
            'nonce' => wp_create_nonce('wp_rest'),
            'budgets' => array(
                'nodeWarning' => 5000,
                'nodeLimit' => 6500,
                'heapGrowthWarningBytes' => 50331648,
                'heapGrowthLimitBytes' => 100663296,
                'storageLimitBytes' => 4194304,
                'longTaskLimit' => 20,
                'runtimeErrorLimit' => 50,
            ),
            'stressModules' => array('overview','climate-maps','marine-biology','astronomy-observations','astronomy','microbiology-laboratory','chemistry','physics','biology','energy-engineering'),
            'strings' => array(
                'safeMode' => __('Safe mode is active. Persisted projects are not loaded or modified in this browser lifecycle.', 'sustainable-catalyst-lab'),
                'backendOffline' => __('Python Compute Core is temporarily unavailable. Active jobs will be checked again automatically.', 'sustainable-catalyst-lab'),
                'jobsRestored' => __('Queued compute jobs were restored after page reload.', 'sustainable-catalyst-lab'),
                'storageRepaired' => __('Damaged project storage was quarantined and a clean workspace was started.', 'sustainable-catalyst-lab'),
            ),
        ));
    }

    public static function admin_menu() {
        add_submenu_page('options-general.php', 'Lab Production Readiness', 'Lab Production Readiness', 'manage_options', 'sc-lab-production-readiness', array(__CLASS__, 'admin_page'));
    }

    public static function admin_assets($hook) {
        if ($hook !== 'settings_page_sc-lab-production-readiness') { return; }
        $style = 'assets/css/sc-lab-production-stability-v0266.css';
        $script = 'assets/js/sc-lab-production-health-admin-v0266.js';
        wp_enqueue_style('sc-lab-production-stability-v0266-admin', SC_LAB_URL . $style, array(), self::asset_version($style));
        wp_enqueue_script('sc-lab-production-health-admin-v0266', SC_LAB_URL . $script, array(), self::asset_version($script), true);
        wp_localize_script('sc-lab-production-health-admin-v0266', 'SCLabProductionHealthAdminConfigV0266', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'labUrl' => esc_url_raw(apply_filters('sc_lab_production_readiness_lab_url', home_url('/lab/'))),
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/production/v0266/health')),
            'saveUrl' => esc_url_raw(rest_url('sc-lab/v1/production/v0266/reports')),
            'latestUrl' => esc_url_raw(rest_url('sc-lab/v1/production/v0266/reports/latest')),
            'nonce' => wp_create_nonce('wp_rest'),
            'modules' => array('overview','climate-maps','marine-biology','astronomy-observations','astronomy','microbiology-laboratory','chemistry','physics','biology','energy-engineering'),
            'rounds' => 2,
            'frameTimeoutMs' => 25000,
        ));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/production/v0266/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/production/v0266/reports', array('methods'=>WP_REST_Server::CREATABLE,'callback'=>array(__CLASS__,'save_report'),'permission_callback'=>array(__CLASS__,'can_manage')));
        register_rest_route('sc-lab/v1', '/production/v0266/reports/latest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'latest_report'),'permission_callback'=>array(__CLASS__,'can_manage')));
    }

    public static function can_manage() { return current_user_can('manage_options'); }

    private static function required_files() {
        return array(
            'assets/js/sc-lab-production-bootstrap-v0266.js',
            'assets/js/sc-lab-production-stability-v0266.js',
            'assets/js/sc-lab-production-health-admin-v0266.js',
            'assets/css/sc-lab-production-stability-v0266.css',
            'contracts/production-readiness-v0266.schema.json',
            'docs/PRODUCTION_STABILITY_RECOVERY_V0266.md',
            'includes/class-sc-lab-production-stability-v0266.php',
            'assets/js/modules/projects.js',
            'assets/js/modules/compute-client.js',
            'includes/class-sc-lab-plugin.php',
            'sustainable-catalyst-lab.php',
        );
    }

    private static function memory_bytes($value) {
        if (is_numeric($value)) { return (int) $value; }
        $value = trim((string) $value);
        if ($value === '' || $value === '-1') { return -1; }
        $unit = strtolower(substr($value, -1));
        $number = (float) $value;
        if ($unit === 'g') { return (int) ($number * 1073741824); }
        if ($unit === 'm') { return (int) ($number * 1048576); }
        if ($unit === 'k') { return (int) ($number * 1024); }
        return (int) $number;
    }

    private static function manifest() {
        $path = SC_LAB_DIR . 'build/sc-lab-release-manifest.json';
        if (!is_file($path)) { return array(); }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array();
    }

    public static function health() {
        $files = array();
        $ok = true;
        foreach (self::required_files() as $relative) {
            $exists = is_file(SC_LAB_DIR . $relative);
            $files[$relative] = array('exists'=>$exists,'sha256'=>$exists ? hash_file('sha256', SC_LAB_DIR . $relative) : null);
            $ok = $ok && $exists;
        }
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        $manifest = self::manifest();
        $php_limit = self::memory_bytes(ini_get('memory_limit'));
        $wp_limit = defined('WP_MEMORY_LIMIT') ? self::memory_bytes(WP_MEMORY_LIMIT) : null;
        $max_limit = defined('WP_MAX_MEMORY_LIMIT') ? self::memory_bytes(WP_MAX_MEMORY_LIMIT) : null;
        $storage_free = function_exists('disk_free_space') ? @disk_free_space(WP_CONTENT_DIR) : null;
        $storage_total = function_exists('disk_total_space') ? @disk_total_space(WP_CONTENT_DIR) : null;
        $state = $ok ? 'ready' : 'missing_files';
        return rest_ensure_response(array(
            'ok' => $ok,
            'state' => $state,
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'manifestRelease' => isset($manifest['releaseVersion']) ? $manifest['releaseVersion'] : null,
            'features' => array(
                'safeModeStartup'=>true,
                'projectStorageQuarantine'=>true,
                'jobRestoration'=>true,
                'backendRecovery'=>true,
                'memoryBudgets'=>true,
                'switchStressRunner'=>true,
                'incidentBundleExport'=>true,
                'productionReadinessDashboard'=>true,
            ),
            'environment' => array(
                'phpVersion' => PHP_VERSION,
                'phpMemoryLimitBytes' => $php_limit,
                'wpMemoryLimitBytes' => $wp_limit,
                'wpMaxMemoryLimitBytes' => $max_limit,
                'diskFreeBytes' => is_numeric($storage_free) ? (int) $storage_free : null,
                'diskTotalBytes' => is_numeric($storage_total) ? (int) $storage_total : null,
                'remoteComputeEnabled' => !empty($settings['enable_remote_compute']),
                'remoteComputeConfigured' => !empty($settings['compute_backend_url']),
                'feedsEnabled' => !empty($settings['enable_feeds']),
                'climateMapsEnabled' => !empty($settings['enable_climate_maps']),
            ),
            'files' => $files,
            'latestReport' => get_option(self::REPORT_OPTION, null),
            'time' => gmdate('c'),
        ));
    }

    private static function sanitize_report_value($value, $depth = 0) {
        if ($depth > 9) { return null; }
        if (is_array($value)) {
            $out = array(); $count = 0;
            foreach ($value as $key => $item) {
                if ($count++ > 500) { break; }
                $safe_key = is_int($key) ? $key : sanitize_key((string) $key);
                $out[$safe_key] = self::sanitize_report_value($item, $depth + 1);
            }
            return $out;
        }
        if (is_bool($value) || is_int($value) || is_float($value) || is_null($value)) { return $value; }
        return substr(sanitize_textarea_field((string) $value), 0, 12000);
    }

    public static function save_report(WP_REST_Request $request) {
        $raw = $request->get_json_params();
        if (!is_array($raw)) { return new WP_Error('invalid_production_report', 'A JSON production-readiness report is required.', array('status'=>400)); }
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
        <div class="wrap sc-lab-production-admin-v0266" data-sc-lab-production-admin-v0266>
          <h1>Sustainable Catalyst Lab Production Readiness</h1>
          <p>Measures startup stability, browser memory and DOM budgets, repeated laboratory switching, project-storage recovery, compute-job restoration, backend interruption behavior, and incident diagnostics.</p>
          <div class="sc-lab-production-toolbar-v0266">
            <button type="button" class="button button-primary" data-production-run-readiness>Run readiness audit</button>
            <button type="button" class="button" data-production-run-stress>Run switching stress test</button>
            <button type="button" class="button" data-production-stop>Stop</button>
            <button type="button" class="button" data-production-export>Export incident bundle</button>
            <a class="button" target="_blank" rel="noopener" href="<?php echo esc_url(add_query_arg(array('sc_lab_safe'=>'1','sc_lab_recovery'=>'1'), apply_filters('sc_lab_production_readiness_lab_url', home_url('/lab/')))); ?>">Open Safe Start</a>
            <button type="button" class="button" data-production-refresh-server>Refresh server health</button>
          </div>
          <div class="sc-lab-production-summary-v0266" role="status" aria-live="polite" data-production-summary>Ready to evaluate production stability.</div>
          <div data-production-server></div>
          <div class="sc-lab-production-grid-v0266">
            <section>
              <h2>Stress runner</h2>
              <div class="sc-lab-production-frame-shell-v0266"><iframe title="Lab production stability runner" data-production-frame></iframe></div>
            </section>
            <section>
              <h2>Readiness results</h2>
              <table class="widefat striped"><thead><tr><th>Check</th><th>Status</th><th>Observed</th><th>Budget</th></tr></thead><tbody data-production-rows></tbody></table>
            </section>
          </div>
          <details><summary>Raw report</summary><pre data-production-json>No production-readiness report has been run.</pre></details>
        </div>
        <?php
    }
}
