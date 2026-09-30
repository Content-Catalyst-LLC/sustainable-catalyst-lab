<?php
/**
 * Sustainable Catalyst Lab v0.152.0.10 4D Uncertainty, Sensitivity & Ensemble Explorer.
 *
 * Keeps the v0.152 safe shell and the bounded 4D front door while exposing a
 * user-driven multidimensional parameter explorer backed by the registered
 * Python Compute Core simulation.parameter_sweep method. No compute runs are
 * started automatically.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Uncertainty_Sensitivity_Ensemble_Explorer_V015210 {
    const VERSION = '0.152.0.10';
    private static $initialized = false;
    private static $notice_registered = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        self::replace_integrity_notice();
        add_action('plugins_loaded', array(__CLASS__, 'replace_integrity_notice'), PHP_INT_MAX);
        add_action('admin_init', array(__CLASS__, 'replace_integrity_notice'), PHP_INT_MAX);
        add_action('wp_enqueue_scripts', array(__CLASS__, 'gate_frontend_assets'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'gate_footer_scripts'), PHP_INT_MAX);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function replace_integrity_notice() {
        remove_action('admin_notices', array('SC_Lab_Integrity_V02632', 'admin_notice'));
        remove_action('admin_notices', array('SC_Lab_Production_Safe_Boot_V015206', 'admin_notice'));
        remove_action('admin_notices', array('SC_Lab_Interactive_4D_Front_Door_V015207', 'admin_notice'));
        remove_action('admin_notices', array('SC_Lab_Response_Surface_Parameter_Explorer_V015209', 'admin_notice'));
        if (!self::$notice_registered) {
            add_action('admin_notices', array(__CLASS__, 'admin_notice'), PHP_INT_MAX);
            self::$notice_registered = true;
        }
    }

    public static function admin_notice() {
        if (!current_user_can('activate_plugins')) { return; }
        if (!class_exists('SC_Lab_Integrity_V02632') || !method_exists('SC_Lab_Integrity_V02632', 'health')) { return; }
        $response = SC_Lab_Integrity_V02632::health();
        $state = $response instanceof WP_REST_Response ? $response->get_data() : (is_array($response) ? $response : array());
        if (!empty($state['ok'])) { return; }
        $issues = array();
        if (!empty($state['partialInstallRisk'])) { $issues[] = 'release files, version markers, plugin identity, or canonical route contracts do not match'; }
        if (!empty($state['duplicatePluginRisk'])) { $issues[] = 'more than one Sustainable Catalyst Lab plugin folder exists in the WordPress plugin directory'; }
        if (!$issues) { $issues[] = 'the canonical runtime health check is not verified'; }
        echo '<div class="notice notice-error"><p><strong>Sustainable Catalyst Lab integrity warning:</strong> ' . esc_html(implode('; ', $issues)) . '. Check <code>/wp-json/sc-lab/v1/runtime/health</code> before continuing upgrades.</p></div>';
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app')) { return true; }
        if (function_exists('is_page') && is_page('lab')) { return true; }
        $path = isset($_SERVER['REQUEST_URI']) ? (string) parse_url((string) $_SERVER['REQUEST_URI'], PHP_URL_PATH) : '';
        return (bool) preg_match('~/(?:lab)/?$~', $path);
    }

    private static function is_lab_asset_src($src) {
        return (string) $src !== '' && strpos((string) $src, 'sustainable-catalyst-lab/') !== false;
    }

    private static function safe_script_relative() { return 'assets/js/sc-lab-safe-bootstrap-v015210.js'; }
    private static function explorer_script_relative() { return 'assets/js/sc-lab-uncertainty-sensitivity-ensemble-v015210.js'; }
    private static function base_style_relative() { return 'assets/css/sc-lab-ui-bundle-v015204.css'; }
    private static function explorer_style_relative() { return 'assets/css/sc-lab-uncertainty-sensitivity-ensemble-v015210.css'; }

    private static function allowed_script_src($src) {
        $src = (string) $src;
        return strpos($src, self::safe_script_relative()) !== false || strpos($src, self::explorer_script_relative()) !== false;
    }
    private static function allowed_style_src($src) {
        $src = (string) $src;
        return strpos($src, self::base_style_relative()) !== false || strpos($src, self::explorer_style_relative()) !== false;
    }

    private static function prune_scripts() {
        $scripts = wp_scripts(); if (!$scripts) { return; }
        foreach ((array) $scripts->queue as $handle) {
            $item = isset($scripts->registered[$handle]) ? $scripts->registered[$handle] : null;
            if (!$item || empty($item->src) || !self::is_lab_asset_src($item->src)) { continue; }
            if (self::allowed_script_src($item->src)) { continue; }
            wp_dequeue_script($handle);
        }
    }
    private static function prune_styles() {
        $styles = wp_styles(); if (!$styles) { return; }
        foreach ((array) $styles->queue as $handle) {
            $item = isset($styles->registered[$handle]) ? $styles->registered[$handle] : null;
            if (!$item || empty($item->src) || !self::is_lab_asset_src($item->src)) { continue; }
            if (self::allowed_style_src($item->src)) { continue; }
            wp_dequeue_style($handle);
        }
    }

    private static function enqueue_runtime() {
        $base = self::base_style_relative(); $style = self::explorer_style_relative();
        $safe = self::safe_script_relative(); $explorer = self::explorer_script_relative();
        wp_enqueue_style('sc-lab-safe-ui-v015210', SC_LAB_URL . $base, array(), self::asset_token($base));
        wp_enqueue_style('sc-lab-uncertainty-explorer-v015210', SC_LAB_URL . $style, array('sc-lab-safe-ui-v015210'), self::asset_token($style));
        wp_enqueue_script('sc-lab-safe-bootstrap-v015210', SC_LAB_URL . $safe, array(), self::asset_token($safe), true);
        wp_enqueue_script('sc-lab-uncertainty-explorer-v015210', SC_LAB_URL . $explorer, array('sc-lab-safe-bootstrap-v015210'), self::asset_token($explorer), true);
        wp_localize_script('sc-lab-safe-bootstrap-v015210', 'SCLabSafeBootV015210', array(
            'version'=>self::VERSION,
            'releaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,
            'featureVersion'=>defined('SC_LAB_FEATURE_VERSION')?SC_LAB_FEATURE_VERSION:'0.152.0',
            'mode'=>'safe-shell-with-4d-uncertainty-sensitivity-ensemble-explorer',
            'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/frontend-runtime/v015210/health')),
        ));
        wp_localize_script('sc-lab-uncertainty-explorer-v015210', 'SCLabUncertaintyExplorerV015210', array(
            'version'=>self::VERSION,
            'computeHealthUrl'=>esc_url_raw(rest_url('sc-lab/v1/compute/core/health')),
            'computeCapabilitiesUrl'=>esc_url_raw(rest_url('sc-lab/v1/compute/core/capabilities')),
            'computeRunUrl'=>esc_url_raw(rest_url('sc-lab/v1/compute/core/run')),
            'nonce'=>wp_create_nonce('wp_rest'),
            'maxXSamples'=>41,
            'maxYLevels'=>7,
            'maxWSlices'=>5,
            'maxParallelRequests'=>3,
            'maxMonteCarloSamples'=>50000,
            'maxEnsembleMembers'=>7,
        ));
    }

    public static function gate_frontend_assets() {
        if (!self::is_lab_request()) { return; }
        self::prune_scripts(); self::prune_styles(); self::enqueue_runtime();
    }
    public static function gate_footer_scripts() {
        if (!self::is_lab_request()) { return; }
        self::prune_scripts(); self::enqueue_runtime();
    }

    private static function asset_token($relative) {
        $path = SC_LAB_DIR . ltrim((string)$relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . ltrim((string)$relative, '/');
        return array('exists'=>is_file($path),'bytes'=>is_file($path)?filesize($path):0,'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }

    public static function routes() {
        register_rest_route('sc-lab/v1','/frontend-runtime/v015210/health',array(
            'methods'=>WP_REST_Server::READABLE,
            'callback'=>array(__CLASS__,'health'),
            'permission_callback'=>'__return_true',
        ));
    }

    public static function health() {
        $files = array(
            self::safe_script_relative()=>self::state(self::safe_script_relative()),
            self::explorer_script_relative()=>self::state(self::explorer_script_relative()),
            self::base_style_relative()=>self::state(self::base_style_relative()),
            self::explorer_style_relative()=>self::state(self::explorer_style_relative()),
        );
        $ok = true; foreach ($files as $f) { if (empty($f['exists']) || empty($f['bytes'])) { $ok = false; } }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'uncertainty-sensitivity-ensemble-explorer-ready':'incomplete',
            'version'=>self::VERSION,
            'releaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'featureVersion'=>defined('SC_LAB_FEATURE_VERSION')?SC_LAB_FEATURE_VERSION:null,
            'safeShellRetained'=>true,
            'interactive4DFrontDoor'=>true,
            'responseSurfaceParameterExplorer'=>true,
            'uncertaintySensitivityEnsembleExplorer'=>true,
            'monteCarloMethod'=>'uncertainty.monte_carlo_propagation',
            'localSensitivityMethod'=>'sensitivity.local_finite_difference',
            'seedReplicationEnsemble'=>true,
            'maxMonteCarloSamples'=>50000,
            'maxEnsembleMembers'=>7,
            'modelFamilies'=>array('logistic_growth','projectile_range','photovoltaic_output','michaelis_menten'),
            'computeMethod'=>'simulation.parameter_sweep',
            'computeExecutionExplicitUserAction'=>true,
            'threeInputDimensions'=>array('x-parameter','y-parameter','w-parameter'),
            'zMappings'=>array('model-output','normalized-output','baseline-difference'),
            'boundedGrid'=>array('maxXSamples'=>41,'maxYLevels'=>7,'maxWSlices'=>5,'maxEvaluations'=>1435,'maxParallelRequests'=>3),
            'runMetadata'=>true,
            'baselineComparison'=>true,
            'savedConfigurations'=>true,
            'savedConfigurationStorage'=>'browser-localStorage',
            'exports'=>array('png','json','csv'),
            'phpOutputSafetyGateRetained'=>true,
            'legacyIndividualModulesEager'=>false,
            'optionalMegaBundleEager'=>false,
            'legacyProductionMonitorEager'=>false,
            'legacyPresentationRuntimeEager'=>false,
            'scientificBoundary'=>'Only registered model families are executed. Computed model output is not observation, evidence, calibration, or scientific validity; interpolation and baseline differences are visualization operations.',
            'backendBehaviorChanged'=>false,
            'files'=>$files,
        ));
    }
}
