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

    private function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim($relative, '/');
        return SC_LAB_VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 12) : '0');
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
        add_shortcode('sc_lab_numerical_methods', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_numerical_validation', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_long_jobs', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_solver_governance', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_numerical_visualization', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_project_workspace', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_reproducible_runs', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_research_provenance', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_method_review', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_scholarly_discovery', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_experiment_framework', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_design_studies', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_model_calibration', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_dataset_registry', array($this, 'shortcode_focus'));
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

        wp_enqueue_style('sc-lab-app', SC_LAB_URL . 'assets/css/sc-lab-app.css', array(), $this->asset_version('assets/css/sc-lab-app.css'));
  wp_enqueue_style('sc-lab-v0100', SC_LAB_URL . 'assets/css/sc-lab-v0100.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-v0100.css'));
  wp_enqueue_style('sc-lab-v0110', SC_LAB_URL . 'assets/css/sc-lab-v0110.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-v0110.css')); wp_enqueue_style('sc-lab-v0120', SC_LAB_URL . 'assets/css/sc-lab-v0120.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-v0120.css'));
  wp_enqueue_style('sc-lab-v095', SC_LAB_URL . 'assets/css/sc-lab-v095.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-v095.css'));
        wp_enqueue_style('sc-lab-numerical-methods-v0270', SC_LAB_URL . 'assets/css/sc-lab-numerical-methods-v0270.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-numerical-methods-v0270.css'));
        wp_enqueue_style('sc-lab-numerical-validation-v0271', SC_LAB_URL . 'assets/css/sc-lab-numerical-validation-v0271.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-numerical-validation-v0271.css'));
        wp_enqueue_style('sc-lab-long-jobs-v0272', SC_LAB_URL . 'assets/css/sc-lab-long-jobs-v0272.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-long-jobs-v0272.css'));
        wp_enqueue_style('sc-lab-numerical-governance-v0273', SC_LAB_URL . 'assets/css/sc-lab-numerical-governance-v0273.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-numerical-governance-v0273.css'));
        wp_enqueue_style('sc-lab-numerical-visualization-v0274', SC_LAB_URL . 'assets/css/sc-lab-numerical-visualization-v0274.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-numerical-visualization-v0274.css'));
        wp_enqueue_style('sc-lab-project-workspace-v0280', SC_LAB_URL . 'assets/css/sc-lab-project-workspace-v0280.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-project-workspace-v0280.css'));
        wp_enqueue_style('sc-lab-dataset-registry-v0281', SC_LAB_URL . 'assets/css/sc-lab-dataset-registry-v0281.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-dataset-registry-v0281.css'));
        wp_enqueue_style('sc-lab-research-provenance-v0290', SC_LAB_URL . 'assets/css/sc-lab-research-provenance-v0290.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-research-provenance-v0290.css'));
        wp_enqueue_style('sc-lab-research-quality-v0291', SC_LAB_URL . 'assets/css/sc-lab-research-quality-v0291.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-research-quality-v0291.css'));
        wp_enqueue_style('sc-lab-external-discovery-v0292', SC_LAB_URL . 'assets/css/sc-lab-external-discovery-v0292.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-external-discovery-v0292.css'));
        wp_enqueue_style('sc-lab-experiment-framework-v0300', SC_LAB_URL . 'assets/css/sc-lab-experiment-framework-v0300.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-experiment-framework-v0300.css'));
        wp_enqueue_style('sc-lab-design-studies-v0301', SC_LAB_URL . 'assets/css/sc-lab-design-studies-v0301.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-design-studies-v0301.css'));
        wp_enqueue_style('sc-lab-model-calibration-v0302', SC_LAB_URL . 'assets/css/sc-lab-model-calibration-v0302.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-model-calibration-v0302.css'));
        wp_enqueue_style('sc-lab-distributed-dispatcher-v0310', SC_LAB_URL . 'assets/css/sc-lab-distributed-dispatcher-v0310.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-distributed-dispatcher-v0310.css'));
        wp_enqueue_style('sc-lab-persistent-queue-v0311', SC_LAB_URL . 'assets/css/sc-lab-persistent-queue-v0311.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-persistent-queue-v0311.css'));
        wp_enqueue_style('sc-lab-worker-agent-v0312', SC_LAB_URL . 'assets/css/sc-lab-worker-agent-v0312.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-worker-agent-v0312.css'));
        wp_enqueue_style('sc-lab-artifact-transport-v0313', SC_LAB_URL . 'assets/css/sc-lab-artifact-transport-v0313.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-artifact-transport-v0313.css'));
        wp_enqueue_style('sc-lab-dispatcher-operations-v0314', SC_LAB_URL . 'assets/css/sc-lab-dispatcher-operations-v0314.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-dispatcher-operations-v0314.css'));
        wp_enqueue_style('sc-lab-workflow-orchestration-v0321', SC_LAB_URL . 'assets/css/sc-lab-workflow-orchestration-v0321.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-workflow-orchestration-v0321.css'));
        wp_enqueue_style('sc-lab-workflow-automation-v0322', SC_LAB_URL . 'assets/css/sc-lab-workflow-automation-v0322.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-workflow-automation-v0322.css'));
        wp_enqueue_style('sc-lab-experiment-campaigns-v0331', SC_LAB_URL . 'assets/css/sc-lab-experiment-campaigns-v0331.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-experiment-campaigns-v0331.css'));
        wp_enqueue_style('sc-lab-closed-loop-campaigns-v0332', SC_LAB_URL . 'assets/css/sc-lab-closed-loop-campaigns-v0332.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-closed-loop-campaigns-v0332.css'));
        wp_enqueue_style('sc-lab-model-registry-v0340', SC_LAB_URL . 'assets/css/sc-lab-model-registry-v0340.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-model-registry-v0340.css'));
        wp_enqueue_style('sc-lab-ensemble-uncertainty-v0341', SC_LAB_URL . 'assets/css/sc-lab-ensemble-uncertainty-v0341.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-ensemble-uncertainty-v0341.css'));
        wp_enqueue_style('sc-lab-surrogate-reduced-order-v0342', SC_LAB_URL . 'assets/css/sc-lab-surrogate-reduced-order-v0342.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-surrogate-reduced-order-v0342.css'));
        wp_enqueue_style('sc-lab-team-workspaces-v0350', SC_LAB_URL . 'assets/css/sc-lab-team-workspaces-v0350.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-team-workspaces-v0350.css'));
        wp_enqueue_style('sc-lab-workspace-review-v0351', SC_LAB_URL . 'assets/css/sc-lab-workspace-review-v0351.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-workspace-review-v0351.css'));
        wp_enqueue_style('sc-lab-workspace-versioning-v0352', SC_LAB_URL . 'assets/css/sc-lab-workspace-versioning-v0352.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-workspace-versioning-v0352.css'));
        wp_enqueue_style('sc-lab-artifact-repository-v0360', SC_LAB_URL . 'assets/css/sc-lab-artifact-repository-v0360.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-artifact-repository-v0360.css'));
        wp_enqueue_style('sc-lab-institutional-node-federation-v0361', SC_LAB_URL . 'assets/css/sc-lab-institutional-node-federation-v0361.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-institutional-node-federation-v0361.css'));
        wp_enqueue_style('sc-lab-offline-edge-sync-v0362', SC_LAB_URL . 'assets/css/sc-lab-offline-edge-sync-v0362.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-offline-edge-sync-v0362.css'));
        wp_enqueue_style('sc-lab-publication-studio-v0370', SC_LAB_URL . 'assets/css/sc-lab-publication-studio-v0370.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-publication-studio-v0370.css'));
        wp_enqueue_style('sc-lab-reproducible-runs-v0282', SC_LAB_URL . 'assets/css/sc-lab-reproducible-runs-v0282.css', array('sc-lab-app'), $this->asset_version('assets/css/sc-lab-reproducible-runs-v0282.css'));
        if (class_exists('SC_Lab_Production_Stability_V0266')) { SC_Lab_Production_Stability_V0266::enqueue_bootstrap(); }
        $deps = wp_script_is('sc-lab-production-bootstrap-v0266', 'enqueued') ? array('sc-lab-production-bootstrap-v0266') : array();
        $modules = array('core','projects','project-workspace-v0280','feeds','climate-map','periodic-table','stoichiometry','chemistry-lab','spectrometry','calculators','datasets','dataset-registry-v0281','reproducible-runs-v0282','research-provenance-v0290','research-quality-v0291','external-discovery-v0292','experiment-framework-v0300','design-studies-v0301','model-calibration-v0302','workflow-orchestration-v0321','workflow-automation-v0322','experiment-campaigns-v0331','closed-loop-campaigns-v0332','model-registry-v0340','ensemble-uncertainty-v0341','surrogate-reduced-order-v0342','team-workspaces-v0350','workspace-review-v0351','workspace-versioning-v0352','artifact-repository-v0360','institutional-node-federation-v0361','offline-edge-sync-v0362','publication-studio-v0370','distributed-dispatcher-v0310','persistent-queue-v0311','dispatcher-operations-v0314','worker-agent-v0312','artifact-transport-v0313','observations','physics-lab','physics-validation','biology-lab','astronomy-lab','materials-lab','earth-lab','energy-lab','electrical-embedded-lab','mechanical-thermal-lab','civil-infrastructure-lab','method-contracts','compute-client','numerical-methods-studio','numerical-validation-studio','numerical-governance-studio','numerical-visualization-studio','long-running-jobs-studio','code-switcher','visualization','reporting','dimensional-visualization','data-management','workspace','release-v095');
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
            wp_enqueue_script($handle, SC_LAB_URL . 'assets/js/modules/' . $module . '.js', $deps, $this->asset_version('assets/js/modules/' . $module . '.js'), true);
            $deps[] = $handle;
        }
        if (wp_script_is('sc-lab-runtime-v02631', 'registered') || wp_script_is('sc-lab-runtime-v02631', 'enqueued')) { $deps[] = 'sc-lab-runtime-v02631'; }
        if (wp_script_is('sc-lab-observe-domain-v02633', 'registered') || wp_script_is('sc-lab-observe-domain-v02633', 'enqueued')) { $deps[] = 'sc-lab-observe-domain-v02633'; }
        wp_enqueue_script('sc-lab-app', SC_LAB_URL . 'assets/js/sc-lab-app.js', array_values(array_unique($deps)), $this->asset_version('assets/js/sc-lab-app.js'), true);

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
                'jobTimeoutSeconds' => max(5, min(900, absint($settings['compute_job_timeout_seconds']))),
                'jobMaxAttempts' => max(1, min(5, absint($settings['compute_job_max_attempts']))),
                'jobPollMs' => max(500, min(10000, absint($settings['compute_job_poll_ms']))),
                'endpoints' => array(
                    'status' => esc_url_raw(rest_url('sc-lab/v1/compute/status')),
                    'languages' => esc_url_raw(rest_url('sc-lab/v1/compute/languages')),
                    'methods' => esc_url_raw(rest_url('sc-lab/v1/compute/methods')),
                    'execute' => esc_url_raw(rest_url('sc-lab/v1/compute/execute')),
                    'compare' => esc_url_raw(rest_url('sc-lab/v1/compute/compare')),
                    'jobs' => esc_url_raw(rest_url('sc-lab/v1/compute/jobs')),
                    'queueStatus' => esc_url_raw(rest_url('sc-lab/v1/compute/queue/status')),
                    'workers' => esc_url_raw(rest_url('sc-lab/v1/compute/workers')),
                    'cacheStatus' => esc_url_raw(rest_url('sc-lab/v1/compute/core/cache/status')),
                    'cachePurge' => esc_url_raw(rest_url('sc-lab/v1/compute/core/cache')),
                    'reportValidate' => esc_url_raw(rest_url('sc-lab/v1/compute/reports/validate')),
                    'reportPdf' => esc_url_raw(rest_url('sc-lab/v1/compute/reports/pdf')),
                    'handoffValidate' => esc_url_raw(rest_url('sc-lab/v1/compute/handoffs/decision-studio/validate')),
                    'capabilities' => esc_url_raw(rest_url('sc-lab/v1/compute/core/capabilities')),
                    'coreMethods' => esc_url_raw(rest_url('sc-lab/v1/compute/core/methods')),
                    'coreRun' => esc_url_raw(rest_url('sc-lab/v1/compute/core/run')),
                    'numericalCatalog' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0270/catalog')),
                    'numericalHealth' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0270/health')),
                    'benchmarks' => esc_url_raw(rest_url('sc-lab/v1/compute/core/benchmarks')),
                    'benchmarkRun' => esc_url_raw(rest_url('sc-lab/v1/compute/core/benchmarks/run')),
                    'benchmarkSuite' => esc_url_raw(rest_url('sc-lab/v1/compute/core/benchmarks/run-suite')),
                    'benchmarkConvergence' => esc_url_raw(rest_url('sc-lab/v1/compute/core/benchmarks/convergence')),
                    'governanceHealth' => esc_url_raw(rest_url('sc-lab/v1/compute/core/governance/health')),
                    'governancePolicies' => esc_url_raw(rest_url('sc-lab/v1/compute/core/governance/policies')),
                    'governanceRecommend' => esc_url_raw(rest_url('sc-lab/v1/compute/core/governance/recommend')),
                    'governanceCompare' => esc_url_raw(rest_url('sc-lab/v1/compute/core/governance/compare')),
                    'visualizationHealth' => esc_url_raw(rest_url('sc-lab/v1/compute/core/visualization/health')),
                    'visualizationProfiles' => esc_url_raw(rest_url('sc-lab/v1/compute/core/visualization/profiles')),
                    'visualizationSpec' => esc_url_raw(rest_url('sc-lab/v1/compute/core/visualization/spec')),
                    'visualizationCsv' => esc_url_raw(rest_url('sc-lab/v1/compute/core/visualization/csv')),
                    'reproducibilityHealth' => esc_url_raw(rest_url('sc-lab/v1/compute/core/reproducibility/health')),
                    'reproducibilityEnvironment' => esc_url_raw(rest_url('sc-lab/v1/compute/core/reproducibility/environment')),
                    'reproducibilityManifest' => esc_url_raw(rest_url('sc-lab/v1/compute/core/reproducibility/manifest')),
                    'reproducibilityVerify' => esc_url_raw(rest_url('sc-lab/v1/compute/core/reproducibility/verify')),
                    'reproducibilityCompare' => esc_url_raw(rest_url('sc-lab/v1/compute/core/reproducibility/compare')),
                    'researchQualityHealth' => esc_url_raw(rest_url('sc-lab/v1/compute/core/research-quality/health')),
                    'researchQualityPolicies' => esc_url_raw(rest_url('sc-lab/v1/compute/core/research-quality/policies')),
                    'researchQualityNormalize' => esc_url_raw(rest_url('sc-lab/v1/compute/core/research-quality/reviews/normalize')),
                    'researchQualityEvaluate' => esc_url_raw(rest_url('sc-lab/v1/compute/core/research-quality/reviews/evaluate')),
                    'researchQualityVerify' => esc_url_raw(rest_url('sc-lab/v1/compute/core/research-quality/reviews/verify')),
                    'researchQualityCompare' => esc_url_raw(rest_url('sc-lab/v1/compute/core/research-quality/reviews/compare')),
                    'discoveryHealth' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/health')),
                    'discoveryProviders' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/providers')),
                    'discoverySearch' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/search')),
                    'discoveryNormalize' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/normalize')),
                    'discoveryDeduplicate' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/deduplicate')),
                    'discoveryOpenAccess' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/open-access')),
                    'discoveryOpenUrl' => esc_url_raw(rest_url('sc-lab/v1/compute/core/discovery/openurl')),
                    'datasetHealth' => esc_url_raw(rest_url('sc-lab/v1/compute/core/datasets/health')),
                    'datasetProfile' => esc_url_raw(rest_url('sc-lab/v1/compute/core/datasets/profile')),
                ),
            ),
            'numerical' => array(
                'version' => '0.27.0',
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0270/catalog')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0270/health')),
                'registeredMethodCount' => 12,
            ),
            'governance' => array('version'=>'0.27.3','policiesUrl'=>esc_url_raw(rest_url('sc-lab/v1/numerical/v0273/policies')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/numerical/v0273/health')),'profiles'=>4),
            'researchProvenance' => array('version'=>'0.29.0','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/research-provenance/v0290/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/research-provenance/v0290/health')),'citationStyle'=>'harvard-author-date','storageMode'=>'browser-local-project-records','pythonVerification'=>true),
            'researchQuality' => array('version'=>'0.29.1','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/research-quality/v0291/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/research-quality/v0291/health')),'policiesUrl'=>esc_url_raw(rest_url('sc-lab/v1/research-quality/v0291/policies')),'storageMode'=>'browser-local-project-records','pythonEvaluation'=>true),
            'externalDiscovery' => array('version'=>'0.29.2','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/discovery/v0292/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/discovery/v0292/health')),'providersUrl'=>esc_url_raw(rest_url('sc-lab/v1/discovery/v0292/providers')),'storageMode'=>'browser-local-project-records','pythonDiscovery'=>true,'arbitraryRemoteFetch'=>false),
            'reproducibility' => array('version'=>'0.28.2','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/reproducibility/v0282/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/reproducibility/v0282/health')),'storageMode'=>'browser-local-project-records','pythonVerification'=>true),
            'datasetRegistry' => array('version'=>'0.28.1','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/datasets/v0281/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/datasets/v0281/health')),'formatsUrl'=>esc_url_raw(rest_url('sc-lab/v1/datasets/v0281/formats')),'storageMode'=>'browser-local','serverBacked'=>false),
            'workspaceArchitecture' => array('version'=>'0.28.0','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/workspace/v0280/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/workspace/v0280/health')),'storageMode'=>'browser-local','serverBacked'=>false),
            'visualization' => array('version'=>'0.27.4','profilesUrl'=>esc_url_raw(rest_url('sc-lab/v1/numerical/v0274/profiles')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/numerical/v0274/health')),'profiles'=>8,'formats'=>array('svg','png','csv','json')),
            'longJobs' => array(
                'version' => '0.27.2',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0272/health')),
                'checkpointableMethods' => array('simulation.parameter_sweep','uncertainty.bootstrap_mean_interval'),
            ),
            'validation' => array(
                'version' => '0.27.1',
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0271/benchmarks')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/numerical/v0271/health')),
                'benchmarkCount' => 14,
            ),
            'strings' => array(
                'networkError' => __('The scientific source could not be reached.', 'sustainable-catalyst-lab'),
                'saved' => __('Saved to the active Lab project.', 'sustainable-catalyst-lab'),
            ),
        ));
        if (class_exists('SC_Lab_Production_Stability_V0266')) { SC_Lab_Production_Stability_V0266::enqueue_front(); }
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
            'sc_lab_numerical_methods' => 'numerical-methods',
            'sc_lab_numerical_validation' => 'numerical-validation',
            'sc_lab_long_jobs' => 'long-running-jobs',
            'sc_lab_solver_governance' => 'numerical-governance',
            'sc_lab_numerical_visualization' => 'numerical-visualization',
            'sc_lab_project_workspace' => 'project-workspace',
            'sc_lab_reproducible_runs' => 'reproducible-runs',
            'sc_lab_research_provenance' => 'research-provenance',
            'sc_lab_method_review' => 'method-review',
            'sc_lab_dataset_registry' => 'dataset-registry',
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
