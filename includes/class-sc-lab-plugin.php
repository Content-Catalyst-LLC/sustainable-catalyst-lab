<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Plugin {
    private static $instance = null;
    private $assets_enqueued = false;

    public static function instance() {
        if (null === self::$instance) { self::$instance = new self(); }
        return self::$instance;
    }

    public static function activate() {
        $defaults = SC_Lab_Admin::defaults();
        if (!get_option('sc_lab_settings')) { add_option('sc_lab_settings', $defaults); }
        update_option('sc_lab_plugin_identity', array('slug'=>SC_LAB_PLUGIN_SLUG,'basename'=>SC_LAB_PLUGIN_BASENAME,'version'=>SC_LAB_VERSION,'activated_at'=>gmdate('c')), false);
        flush_rewrite_rules(false);
    }

    private function __construct() {
        new SC_Lab_REST();
        if (is_admin()) { new SC_Lab_Admin(); }

        add_shortcode('sc_lab_app', array($this, 'shortcode_app'));
        add_shortcode('sc_lab_periodic_table', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_stoichiometry', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_spectrometry', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_climate_map', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_physics', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_biology', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_astronomy', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_materials', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_earth_systems', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_energy', array($this, 'shortcode_focus'));
  add_shortcode('sc_lab_electrical', array($this, 'shortcode_focus'));
  add_shortcode('sc_lab_mechanical_thermal', array($this, 'shortcode_focus')); add_shortcode('sc_lab_civil_infrastructure', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_visualization', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_workspace_data', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_code_switcher', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_reports', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_report_studio', array($this, 'shortcode_focus'));
  add_shortcode('sc_lab_report_composer', array($this, 'shortcode_focus'));
    }

    public function enqueue_assets() {
        if ($this->assets_enqueued) { return; }
        $this->assets_enqueued = true;

        wp_enqueue_style('sc-lab-app', SC_LAB_URL . 'assets/css/sc-lab-app.css', array(), SC_LAB_VERSION);
  wp_enqueue_style('sc-lab-v0100', SC_LAB_URL . 'assets/css/sc-lab-v0100.css', array('sc-lab-app'), SC_LAB_VERSION);
  wp_enqueue_style('sc-lab-v0110', SC_LAB_URL . 'assets/css/sc-lab-v0110.css', array('sc-lab-app'), SC_LAB_VERSION); wp_enqueue_style('sc-lab-v0120', SC_LAB_URL . 'assets/css/sc-lab-v0120.css', array('sc-lab-app'), SC_LAB_VERSION);
  wp_enqueue_style('sc-lab-v095', SC_LAB_URL . 'assets/css/sc-lab-v095.css', array('sc-lab-app'), SC_LAB_VERSION);
        $deps = array();
        $modules = array('core','projects','feeds','climate-map','periodic-table','stoichiometry','chemistry-lab','spectrometry','calculators','datasets','observations','physics-lab','physics-validation','biology-lab','astronomy-lab','materials-lab','earth-lab','energy-lab','electrical-embedded-lab','mechanical-thermal-lab','civil-infrastructure-lab','method-contracts','compute-client','code-switcher','visualization','reporting','dimensional-visualization','data-management','workspace','release-v095');
        foreach ($modules as $module) {
            // SC_LAB_CIVIL_RUNTIME_SKIP_LEGACY:
            // Preserve the legacy key for compatibility tests,
            // but load Civil only through the authoritative runtime.
            if ($module === 'civil-infrastructure-lab') {
                continue;
            }

            // SC_LAB_CIVIL_DIRECT_LOADER_SKIP:
            // Keep the legacy module key for release-test compatibility,
            // but do not enqueue its v0.12.0 implementation. The repaired
            // v0.15.0 Civil interface is loaded by the direct loader.
            if ($module === 'civil-infrastructure-lab') {
                continue;
            }

            $handle = 'sc-lab-' . $module;
            wp_enqueue_script($handle, SC_LAB_URL . 'assets/js/modules/' . $module . '.js', $deps, SC_LAB_VERSION, true);
            $deps[] = $handle;
        }
        wp_enqueue_script('sc-lab-app', SC_LAB_URL . 'assets/js/sc-lab-app.js', $deps, SC_LAB_VERSION, true);

        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        wp_localize_script('sc-lab-app', 'SCLabConfig', array(
            'version' => SC_LAB_VERSION,
            'restBase' => esc_url_raw(rest_url('sc-lab/v1/')),
            'nonce' => wp_create_nonce('wp_rest'),
            'elementsUrl' => esc_url_raw(SC_LAB_URL . 'assets/data/elements.json'),
            'routes' => array(
                'workbench' => esc_url_raw($settings['workbench_url']),
                'decisionStudio' => esc_url_raw($settings['decision_studio_url']),
                'siteIntelligence' => esc_url_raw($settings['site_intelligence_url']),
            ),
            'features' => array(
                'feeds' => !empty($settings['enable_feeds']),
                'climateMaps' => !empty($settings['enable_climate_maps']),
                'remoteCompute' => !empty($settings['enable_remote_compute']),
            ),
            'compute' => array(
                'enabled' => !empty($settings['enable_remote_compute']),
                'configured' => !empty($settings['compute_backend_url']),
                'timeoutSeconds' => max(5, min(60, absint($settings['compute_timeout_seconds']))),
                'endpoints' => array(
                    'status' => esc_url_raw(rest_url('sc-lab/v1/compute/status')),
                    'languages' => esc_url_raw(rest_url('sc-lab/v1/compute/languages')),
                    'methods' => esc_url_raw(rest_url('sc-lab/v1/compute/methods')),
                    'execute' => esc_url_raw(rest_url('sc-lab/v1/compute/execute')),
                    'compare' => esc_url_raw(rest_url('sc-lab/v1/compute/compare')),
                    'jobs' => esc_url_raw(rest_url('sc-lab/v1/compute/jobs')),
                    'reportValidate' => esc_url_raw(rest_url('sc-lab/v1/compute/reports/validate')),
                    'reportPdf' => esc_url_raw(rest_url('sc-lab/v1/compute/reports/pdf')),
                    'handoffValidate' => esc_url_raw(rest_url('sc-lab/v1/compute/handoffs/decision-studio/validate')),
                ),
            ),
            'strings' => array(
                'networkError' => __('The scientific source could not be reached.', 'sustainable-catalyst-lab'),
                'saved' => __('Saved to the active Lab project.', 'sustainable-catalyst-lab'),
            ),
        ));
    }

    public function shortcode_app($atts = array()) {
        $atts = shortcode_atts(array('module' => 'overview', 'project' => 'default'), $atts, 'sc_lab_app');
        return $this->render_app(sanitize_key($atts['module']), sanitize_key($atts['project']));
    }

    public function shortcode_focus($atts, $content, $tag) {
        $map = array(
            'sc_lab_periodic_table' => 'chemistry',
            'sc_lab_stoichiometry' => 'chemistry',
            'sc_lab_spectrometry' => 'science-engineering',
            'sc_lab_climate_map' => 'climate-maps',
            'sc_lab_physics' => 'physics',
            'sc_lab_biology' => 'biology',
            'sc_lab_astronomy' => 'astronomy',
            'sc_lab_materials' => 'materials',
            'sc_lab_earth_systems' => 'earth-systems',
            'sc_lab_energy' => 'energy-engineering',
  'sc_lab_electrical' => 'electrical-embedded',
  'sc_lab_mechanical_thermal' => 'mechanical-thermal', 'sc_lab_civil_infrastructure' => 'civil-infrastructure',
            'sc_lab_visualization' => 'visualization-studio',
            'sc_lab_workspace_data' => 'workspace-data',
            'sc_lab_code_switcher' => 'code-studio',
            'sc_lab_reports' => 'report-studio',
            'sc_lab_report_studio' => 'report-studio',
  'sc_lab_report_composer' => 'report-studio',
        );
        $module = isset($map[$tag]) ? $map[$tag] : 'overview';
        return $this->render_app($module, 'default');
    }

    private function render_app($module, $project) {
        $this->enqueue_assets();
        ob_start();
        $sc_lab_initial_module = $module;
        $sc_lab_initial_project = $project;
        include SC_LAB_DIR . 'templates/lab-app.php';
        return ob_get_clean();
    }
}
