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
        update_option('sc_lab_plugin_identity', array('slug'=>SC_LAB_PLUGIN_SLUG,'basename'=>SC_LAB_PLUGIN_BASENAME,'version'=>(defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:SC_LAB_VERSION),'platformVersion'=>(defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:SC_LAB_VERSION),'activated_at'=>gmdate('c')), false);
        flush_rewrite_rules(false);
    }

    private function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim($relative, '/');
        return (defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : SC_LAB_VERSION) . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 12) : '0');
    }

    private function __construct() {
        new SC_Lab_REST();
        if (is_admin()) { new SC_Lab_Admin(); }

        add_action('wp_enqueue_scripts', array($this, 'maybe_enqueue_frontend_assets'), 20);

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
        add_shortcode('sc_lab_model_studio', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_graph_studio', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_probabilistic_analysis', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_uncertainty_studio', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_dataset_registry', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_materials', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_earth_systems', array($this, 'shortcode_focus'));
        add_shortcode('sc_lab_soil_organic_carbon', array($this, 'shortcode_focus'));
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


    public function maybe_enqueue_frontend_assets() {
        if (is_admin()) { return; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app')) {
            $this->enqueue_assets();
        }
    }

    public function enqueue_assets() {
        if ($this->assets_enqueued) { return; }
        $this->assets_enqueued = true;

        // v0.152.0.4: consolidate the 183-style front door into one immutable bundle.
        // Legacy handles remain registered as zero-request aliases so historical dependencies resolve.
        wp_enqueue_style('sc-lab-app', SC_LAB_URL . 'assets/css/sc-lab-ui-bundle-v015204.css', array(), $this->asset_version('assets/css/sc-lab-ui-bundle-v015204.css'));
        wp_register_style('sc-lab-release-console-v0821', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-v0100', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-v0110', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-v0120', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-v095', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-numerical-methods-v0270', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-numerical-validation-v0271', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-long-jobs-v0272', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-numerical-governance-v0273', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-numerical-visualization-v0274', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-project-workspace-v0280', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-dataset-registry-v0281', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-provenance-v0290', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-quality-v0291', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-external-discovery-v0292', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-experiment-framework-v0300', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-design-studies-v0301', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-model-calibration-v0302', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-visualization-engine-v0440', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-visualization-engine-v0730', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-visualization-engine-v0740', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-visualization-design-system-v01140', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-advanced-statistical-uncertainty-graphics-v01150', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-interactive-scientific-dashboards-v01160', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-advanced-3d-4d-scientific-visualization-v01170', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-visual-research-narrative-figure-composer-v01180', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-figure-intelligence-automatic-layout-v01190', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-exploratory-data-analysis-studio-v01200', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-statistical-modeling-diagnostics-studio-v01210', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-bayesian-analysis-workbench-v01220', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-simulation-monte-carlo-research-studio-v01230', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-sensitivity-global-uncertainty-analysis-studio-v01240', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-causal-research-studio-v01250', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-spatial-spatiotemporal-research-studio-v01260', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-time-series-laboratory-v01270', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-experimental-design-power-analysis-v01280', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-reproduction-replication-studio-v01290', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-research-project-studio-v01300', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-question-hypothesis-workspace-v01310', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-method-selection-intelligence-v01320', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-statistical-assumption-diagnostic-intelligence-v01330', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-evidence-synthesis-intelligence-ii-v01340', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-competing-model-hypothesis-analysis-v01350', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-data-binding-v0750', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-large-data-visualization-v0760', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-scene-v0770', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-time-parameter-space-v0780', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-linked-views-v0790', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-spatial-geospatial-raster-v0800', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-markup-v0810', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-uncertainty-v0820', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-provenance-v0830', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-gpu-v0840', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-webgl2-v0850', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-system-dynamics-v0860', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-webgpu-v0870', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-advanced-3d-v0880', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-model-studio-v0460', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-v0470', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-visualization-experience-v01351', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-model-architecture-provenance-graphs-v01352', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-multi-view-scientific-analysis-canvas-v01353', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-interactive-scientific-scene-drilldown-v01354', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-scene-linking-comparative-context-v01355', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-reproducible-visual-analysis-sessions-v01356', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-visual-research-narrative-findings-v01357', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-review-critique-revision-v01358', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-canonical-runtime-v013581', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-renderer-replacement-v013582', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-recovery-v013583', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-bootstrap-finalization-v0135831', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-live-binding-v013584', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-native-provenance-v013585', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-context-relationships-v0135853', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-object-explorer-v013590', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-path-analysis-v0135100', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-competing-paths-v0135110', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-review-threads-v0135120', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-review-resolution-v0135130', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-review-audit-v0135140', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-verification-artifacts-v0135150', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-revision-impact-v0135160', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-review-reproduction-v0135170', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-multi-reviewer-panels-v0135180', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-cross-review-synthesis-v0135190', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-review-closure-v0135200', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-studio-review-workspace-consolidation-v0135210', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-probabilistic-analysis-v0480', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-interface-v0470', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-presentation-v0481', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-contextual-navigation-v0483', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-shared-model-handoff-v0490', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-reproducible-model-package-v0500', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-advanced-statistical-modeling-v0510', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-bayesian-inference-v0520', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-correlated-uncertainty-v0530', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-dynamic-systems-v0540', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-data-transformations-v0550', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-advanced-experimental-design-v0560', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-workflow-composer-v0570', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-compute-hardening-v0580', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-audit-v0590', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-integrated-research-beta-v0600', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-beta-field-diagnostics-v0601', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-study-lifecycle-v0610', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-claims-v0620', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-literature-v0630', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-evidence-synthesis-v0640', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-evidence-grading-v0650', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-argumentation-v0660', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-causal-inference-v0670', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-hierarchical-modeling-v0680', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-theory-v0690', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-preregistration-v0700', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-advanced-visualization-front-door-v0710', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-distributed-dispatcher-v0310', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-persistent-queue-v0311', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-worker-agent-v0312', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-artifact-transport-v0313', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-dispatcher-operations-v0314', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-workflow-orchestration-v0321', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-workflow-automation-v0322', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-experiment-campaigns-v0331', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-closed-loop-campaigns-v0332', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-model-registry-v0340', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-ensemble-uncertainty-v0341', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-surrogate-reduced-order-v0342', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-team-workspaces-v0350', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-workspace-review-v0351', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-workspace-versioning-v0352', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-artifact-repository-v0360', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-institutional-node-federation-v0361', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-offline-edge-sync-v0362', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-publication-studio-v0370', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-manuscript-assembly-v0371', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-public-reproduction-v0372', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-interoperability-v0380', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-typed-cross-product-handoffs-v0381', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-public-research-integrations-v0382', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-institutional-governance-v0390', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-security-privacy-v0391', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-multi-instance-operations-v0392', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-performance-chaos-v0393', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-connected-platform-beta-v0400', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-interface-finalization-v0401', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-public-release-hardening-v0402', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-connected-platform-v1000', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-reproducible-runs-v0282', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-soil-organic-carbon-v0890', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-soil-carbon-sampling-v0900', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-soil-carbon-change-v0910', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-soil-carbon-uncertainty-v0920', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-soil-carbon-scenarios-v0930', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-whole-farm-ghg-v0940', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-carbon-mrv-registry-v0950', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-carbon-mrv-protocol-v0960', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-carbon-mrv-monitoring-v0970', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-carbon-mrv-uncertainty-v0980', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-carbon-mrv-verification-ledger-v0990', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-carbon-mrv-reporting-v01000', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-research-program-intelligence-v01380', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scholarly-study-original-research-package-v01390', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-research-operating-system-v01400', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-machine-learning-experiment-workspace-v01410', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-neural-architecture-training-configuration-v01411', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-training-curves-metrics-checkpoint-visualization-v01412', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-model-comparison-experiment-matrix-v01413', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-hyperparameter-study-search-results-v01414', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-ablation-study-framework-v01415', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-neural-explainability-workspace-v01416', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-embedding-explorer-v01417', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-reproducible-neural-research-package-v01418', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-integrated-neural-research-workspace-v01420', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-computational-linguistics-research-workspace-v01430', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-statistical-econometric-research-workspace-v01440', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-simulation-computational-experiment-workspace-v01450', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-network-science-research-workspace-v01460', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-graph-machine-learning-experiment-workspace-v01470', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-multimodal-scientific-experiment-workspace-v01480', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-model-validation-benchmark-laboratory-v01490', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-integrated-computational-research-laboratory-v01500', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-scientific-workflow-experiment-orchestration-v01510', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        wp_register_style('sc-lab-cross-workspace-research-dependency-graph-v01520', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION);
        if (class_exists('SC_Lab_Production_Stability_V0266')) { SC_Lab_Production_Stability_V0266::enqueue_bootstrap(); }
        $deps = wp_script_is('sc-lab-production-bootstrap-v0266', 'enqueued') ? array('sc-lab-production-bootstrap-v0266') : array();
        // v0.152.0.4: front-end request consolidation.
        // The critical application runtime is one bundle; the historical module fleet is one
        // isolated optional bundle. This replaces hundreds of blocking HTTP requests without
        // removing any module source from the repository.
        $modules = array('core','projects','project-workspace-v0280','feeds','climate-map','periodic-table','stoichiometry','chemistry-lab','spectrometry','calculators','datasets','data-transformations-v0550','dataset-registry-v0281','reproducible-runs-v0282','research-provenance-v0290','research-quality-v0291','external-discovery-v0292','experiment-framework-v0300','design-studies-v0301','advanced-experimental-design-v0560','model-calibration-v0302','scientific-visualization-engine-v0440','scientific-visualization-engine-v0730','scientific-visualization-engine-v0740','scientific-visualization-design-system-v01140','advanced-statistical-uncertainty-graphics-v01150','interactive-scientific-dashboards-v01160','advanced-3d-4d-scientific-visualization-v01170','visual-research-narrative-figure-composer-v01180','scientific-figure-intelligence-automatic-layout-v01190','exploratory-data-analysis-studio-v01200','statistical-modeling-diagnostics-studio-v01210','bayesian-analysis-workbench-v01220','simulation-monte-carlo-research-studio-v01230','sensitivity-global-uncertainty-analysis-studio-v01240','causal-research-studio-v01250','spatial-spatiotemporal-research-studio-v01260','scientific-time-series-laboratory-v01270','experimental-design-power-analysis-v01280','research-reproduction-replication-studio-v01290','scientific-research-project-studio-v01300','research-question-hypothesis-workspace-v01310','method-selection-intelligence-v01320','statistical-assumption-diagnostic-intelligence-v01330','evidence-synthesis-intelligence-ii-v01340','competing-model-hypothesis-analysis-v01350','scientific-data-binding-v0750','large-data-visualization-v0760','scientific-scene-engine-v0770','time-parameter-space-v0780','linked-views-v0790','spatial-geospatial-raster-v0800','scientific-markup-v0810','uncertainty-ensemble-distribution-v0820','provenance-aware-figures-v0830','gpu-renderer-architecture-v0840','webgl2-scientific-renderer-v0850','webgpu-scientific-renderer-v0870','advanced-scientific-scene-v0880','soil-organic-carbon-v0890','soil-carbon-sampling-v0900','soil-carbon-change-v0910','soil-carbon-uncertainty-v0920','soil-carbon-scenarios-v0930','whole-farm-ghg-v0940','carbon-mrv-registry-v0950','carbon-mrv-protocol-v0960','carbon-mrv-monitoring-v0970','carbon-mrv-uncertainty-v0980','carbon-mrv-verification-ledger-v0990','carbon-mrv-reporting-v01000','model-studio-v0460','graph-studio-v0470','dynamic-systems-v0540','system-dynamics-v0860','shared-model-handoff-v0490','reproducible-model-package-v0500','advanced-statistical-modeling-v0510','bayesian-inference-v0520','graph-studio-v0790','graph-studio-v0800','graph-studio-v0810','graph-studio-v0820','graph-studio-v0830','graph-studio-v0840','graph-studio-v0850','graph-studio-v0870','graph-studio-v0880','scientific-visualization-experience-v01351','model-architecture-provenance-graphs-v01352','multi-view-scientific-analysis-canvas-v01353','interactive-scientific-scene-drilldown-v01354','scientific-scene-linking-comparative-context-v01355','reproducible-visual-analysis-sessions-v01356','visual-research-narrative-findings-v01357','research-review-critique-revision-v01358','graph-studio-canonical-runtime-v013581','graph-studio-renderer-replacement-v013582','graph-studio-recovery-v013583','graph-studio-bootstrap-finalization-v0135831','graph-studio-provenance-authority-v0135851','graph-studio-live-binding-v013584','graph-studio-provenance-interaction-recovery-v0135841','graph-studio-native-provenance-v013585','graph-studio-object-explorer-v013590','graph-studio-path-analysis-v0135100','graph-studio-competing-paths-v0135110','graph-studio-review-threads-v0135120','graph-studio-review-resolution-v0135130','graph-studio-review-audit-v0135140','graph-studio-verification-artifacts-v0135150','graph-studio-revision-impact-v0135160','graph-studio-review-reproduction-v0135170','graph-studio-multi-reviewer-panels-v0135180','graph-studio-cross-review-synthesis-v0135190','graph-studio-review-closure-v0135200','graph-studio-review-workspace-consolidation-v0135210','research-change-impact-living-analysis-v01370','project-workspace-living-analysis-v01370','research-program-intelligence-v01380','project-workspace-research-program-v01380','scholarly-study-original-research-package-v01390','project-workspace-original-research-v01390','scientific-research-operating-system-v01400','project-workspace-research-os-v01400','machine-learning-experiment-workspace-v01410','neural-architecture-training-configuration-v01411','training-curves-metrics-checkpoint-visualization-v01412','model-comparison-experiment-matrix-v01413','hyperparameter-study-search-results-v01414','ablation-study-framework-v01415','neural-explainability-workspace-v01416','embedding-explorer-v01417','reproducible-neural-research-package-v01418','integrated-neural-research-workspace-v01420','project-workspace-integrated-neural-v01420','computational-linguistics-research-workspace-v01430','project-workspace-computational-linguistics-v01430','statistical-econometric-research-workspace-v01440','project-workspace-statistical-econometric-v01440','simulation-computational-experiment-workspace-v01450','project-workspace-simulation-v01450','graph-network-science-research-workspace-v01460','project-workspace-graph-network-v01460','graph-machine-learning-experiment-workspace-v01470','project-workspace-graph-ml-v01470','multimodal-scientific-experiment-workspace-v01480','project-workspace-multimodal-v01480','scientific-model-validation-benchmark-laboratory-v01490','project-workspace-model-validation-v01490','integrated-computational-research-laboratory-v01500','project-workspace-integrated-computational-v01500','scientific-workflow-experiment-orchestration-v01510','project-workspace-scientific-workflow-v01510','cross-workspace-research-dependency-graph-v01520','project-workspace-research-dependency-v01520','project-workspace-machine-learning-v01410','project-workspace-provenance-focus-v013590','project-workspace-research-context-v0135100','project-workspace-path-comparison-v0135110','project-workspace-review-thread-v0135120','project-workspace-review-resolution-v0135130','project-workspace-review-audit-v0135140','project-workspace-verification-artifacts-v0135150','project-workspace-revision-impact-v0135160','project-workspace-review-reproduction-v0135170','project-workspace-multi-reviewer-panels-v0135180','project-workspace-cross-review-synthesis-v0135190','project-workspace-review-closure-v0135200','project-workspace-review-workspace-v0135210','probabilistic-analysis-v0480','interface-reorganization-v0470','presentation-runtime-v0482','contextual-navigation-v0483','workflow-orchestration-v0321','scientific-workflow-composer-v0570','scientific-compute-hardening-v0580','scientific-audit-v0590','integrated-research-beta-v0600','beta-field-diagnostics-v0601','scientific-study-lifecycle-v0610','scientific-claims-v0620','scientific-literature-v0630','evidence-synthesis-v0640','evidence-grading-v0650','scientific-argumentation-v0660','causal-inference-v0670','hierarchical-modeling-v0680','scientific-theory-v0690','preregistration-v0700','advanced-visualization-front-door-v0710','workflow-automation-v0322','experiment-campaigns-v0331','closed-loop-campaigns-v0332','model-registry-v0340','ensemble-uncertainty-v0341','surrogate-reduced-order-v0342','team-workspaces-v0350','workspace-review-v0351','workspace-versioning-v0352','artifact-repository-v0360','institutional-node-federation-v0361','offline-edge-sync-v0362','publication-studio-v0370','manuscript-assembly-v0371','public-reproduction-v0372','research-interoperability-v0380','typed-cross-product-handoffs-v0381','public-research-integrations','institutional-governance-v0390','security-privacy-v0391','multi-instance-operations-v0392','performance-chaos-v0393','connected-platform-beta-v0400','interface-finalization-v0401','public-release-hardening-v0402','connected-platform-v1000','distributed-dispatcher-v0310','persistent-queue-v0311','dispatcher-operations-v0314','worker-agent-v0312','artifact-transport-v0313','observations','physics-lab','physics-validation','biology-lab','astronomy-lab','materials-lab','earth-lab','energy-lab','electrical-embedded-lab','mechanical-thermal-lab','civil-infrastructure-lab','method-contracts','compute-client','numerical-methods-studio','numerical-validation-studio','numerical-governance-studio','numerical-visualization-studio','long-running-jobs-studio','code-switcher','visualization','reporting','dimensional-visualization','data-management','workspace','release-v095');
        $critical_modules = array('core','projects','workspace','feeds','project-workspace-v0280');
        $bundled_skip_modules = array('civil-infrastructure-lab','graph-studio-provenance-interaction-recovery-v0135841','graph-studio-v0790','graph-studio-v0800','graph-studio-v0810','graph-studio-v0820','graph-studio-v0830','graph-studio-v0840','graph-studio-v0850','graph-studio-v0870','graph-studio-v0880');
        $app_deps = $deps;
        if (wp_script_is('sc-lab-runtime-v02631', 'registered') || wp_script_is('sc-lab-runtime-v02631', 'enqueued')) { $app_deps[] = 'sc-lab-runtime-v02631'; }
        if (wp_script_is('sc-lab-observe-domain-v02633', 'registered') || wp_script_is('sc-lab-observe-domain-v02633', 'enqueued')) { $app_deps[] = 'sc-lab-observe-domain-v02633'; }
        // v0.152.0.5: the front door is safe-booted by SC_Lab_Production_Safe_Boot_V015205.
        // Preserve the historical sc-lab-app handle as a zero-request compatibility alias;
        // do not eagerly execute the v0.152.0.4 critical or optional bundles.
        wp_register_script('sc-lab-app', false, array(), SC_LAB_RELEASE_VERSION, true);
        wp_enqueue_script('sc-lab-app');
        wp_register_script('sc-lab-optional-bundle-v015204', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION, true);

        // Replace historical per-module handles with zero-request compatibility aliases.
        // Any downstream script that depends on a historical handle waits for the optional bundle.
        foreach ($modules as $module) {
            $handle = 'sc-lab-' . $module;
            wp_dequeue_script($handle);
            wp_deregister_script($handle);
            $alias_dep = in_array($module, $critical_modules, true) ? 'sc-lab-app' : 'sc-lab-optional-bundle-v015204';
            wp_register_script($handle, false, array($alias_dep), SC_LAB_RELEASE_VERSION, true);
        }
        wp_dequeue_script('sc-lab-navigation-recovery-v015201');
        wp_deregister_script('sc-lab-navigation-recovery-v015201');
        wp_register_script('sc-lab-navigation-recovery-v015201', false, array('sc-lab-app'), SC_LAB_RELEASE_VERSION, true);
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        wp_localize_script('sc-lab-app', 'SCLabConfig', array(
            'version' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'platformVersion' => defined('SC_LAB_PLATFORM_COMPAT_VERSION') ? SC_LAB_PLATFORM_COMPAT_VERSION : null,
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
                        'visualizationEngine2' => array('version'=>'0.88.0','engineVersion'=>'2.14.0','schemaUrl'=>esc_url_raw(rest_url('sc-lab/v1/visualization/v0880/schema')),'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/visualization/v0880/health')),'renderers'=>array('svg2d','canvas2d','canvas3d','canvas4d','canvas-spatial','webgl2','webgpu'),'rendererRegistry'=>array('svg2d','canvas2d','canvas3d','canvas4d','canvas-spatial','webgl2','webgpu'),'candidateGpuRenderers'=>array(),'overlays'=>array('scientific-markup','uncertainty-distribution','figure-provenance'),'rendererCapabilityRegistry'=>true,'browserFeatureDetection'=>true,'safeRendererNegotiation'=>true,'explicitFallbackRecording'=>true,'gpuBufferContracts'=>true,'shaderRegistryContracts'=>true,'pickingContracts'=>true,'memoryBudgets'=>true,'rendererDiagnostics'=>true,'webgl2CapabilityDetection'=>true,'webgpuCapabilityDetection'=>true,'webgl2ProductionRendererReady'=>true,'webgpuProductionRendererReady'=>true,'depthBuffered3D'=>true,'gpuPointClouds'=>true,'gpuLineSegments'=>true,'gpuTriangleMeshes'=>true,'instancedGeometry'=>true,'rasterTextures'=>true,'framebufferObjectPicking'=>true,'approvedInternalShadersOnly'=>true,'webgpuComputeReady'=>true,'advanced3DSceneEngineII'=>true,'sceneGraphs'=>true,'advanced3DLighting'=>true,'advanced3DInstancing'=>true,'scientific3DInteraction'=>true,'threeJSCompatibilityAdapter'=>true,'threeJSRuntimeBundled'=>false,'nativeWebGPUSceneRendererReady'=>true,'gpuFiltering'=>true,'gpuHistogram'=>true,'gpuReduction'=>true,'gpuSpatialBinning'=>true,'approvedWGSLOnly'=>true,'explicitWebGL2Fallback'=>true,'advanced2d'=>true,'datasetBinding'=>true,'transformationPipeline'=>true,'largeDataVisualization'=>true,'adaptiveRendering'=>true,'progressiveRendering'=>true,'scientificScene3d'=>true,'fourDimensionalProjection'=>true,'timeStatePlayback'=>true,'parameterSweep'=>true,'linkedViews'=>true,'linkedSelection'=>true,'linkedFiltering'=>true,'linkedStateAxis'=>true,'faceting'=>true,'mixedRendererComposition'=>true,'spatialVisualization'=>true,'geospatialVisualization'=>true,'vectorGeometry'=>true,'rasterVisualization'=>true,'coordinateReferenceMetadata'=>true,'bboxSelection'=>true,'scientificAnnotation'=>true,'scientificMeasurement'=>true,'scientificMarkupLayers'=>true,'annotationProvenance'=>true,'intervalBands'=>true,'quantileRibbons'=>true,'empiricalHistogram'=>true,'ecdf'=>true,'boxSummary'=>true,'posteriorSamples'=>true,'ensembleTrajectories'=>true,'ensembleEnvelopes'=>true,'uncertaintyProvenance'=>true,'datasetFingerprinting'=>true,'transformationFingerprinting'=>true,'modelFingerprinting'=>true,'rendererProvenance'=>true,'interactionStateFingerprinting'=>true,'exportManifest'=>true,'lineageVerification'=>true,'baseFigurePreservation'=>true,'gpuRequiredForScientificCorrectness'=>false,'serverAssumesBrowserGPU'=>false,'silentRendererFallback'=>false,'automaticScientificSemanticsChange'=>false,'arbitraryShaderSource'=>false,'automaticUncertaintyInference'=>false,'automaticDistributionAssumption'=>false,'automaticParametricFit'=>false,'automaticKDE'=>false,'automaticIntervalConversion'=>false,'automaticEnsembleAlignment'=>false,'temporalInterpolation'=>false,'spatialInterpolation'=>false,'syntheticSamples'=>false,'forecasting'=>false,'annotationIsObservation'=>false,'automaticObservationCreation'=>false,'automaticScientificInterpretation'=>false,'automaticUnitConversion'=>false,'automaticGeodesicMeasurement'=>false,'automaticGeometrySnapping'=>false,'automaticLinkInference'=>false,'crossDatasetJoin'=>false,'statisticalCouplingInference'=>false,'syntheticPanels'=>false,'automaticCRSInference'=>false,'automaticReprojection'=>false,'automaticGeocoding'=>false,'automaticSpatialJoin'=>false,'topologyRepair'=>false,'rasterInterpolation'=>false,'rasterResampling'=>false,'nodataImputation'=>false,'networkBasemaps'=>false,'surfaceInterpolation'=>false),
            'soilOrganicCarbon' => array(
                'domainVersion' => '0.6.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.89.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/policies')),
                'layerStockUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/layer-stock')),
                'profileStockUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/profile-stock')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0600/project-packet')),
                'basis' => 'fixed-depth-fine-earth-corrected',
            ),
            'socSampling' => array(
                'domainVersion' => '0.7.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.90.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/policies')),
                'sampleNormalizeUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/sample/normalize')),
                'sampleBatchUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/samples/normalize')),
                'bulkDensityUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/bulk-density')),
                'designUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/design')),
                'profileHandoffUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/profile-handoff')),
                'fieldPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0700/sampling/field-packet')),
            ),
            'socChange' => array(
                'domainVersion' => '0.8.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.91.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/policies')),
                'compareUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/compare')),
                'seriesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/series')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0800/change/project-packet')),
                'basis' => 'matched-fixed-depth-fine-earth-corrected',
            ),
            'socUncertainty' => array(
                'domainVersion' => '0.9.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.92.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/policies')),
                'replicatesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/replicates')),
                'stratifiedUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/stratified')),
                'changeUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/change')),
                'layerPropagationUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/layer-propagation')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v0900/uncertainty/project-packet')),
            ),
            'socScenarios' => array(
                'domainVersion' => '0.10.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.93.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/policies')),
                'projectUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/project')),
                'compareUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/compare')),
                'sensitivityUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/sensitivity')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/soc/v1000/scenarios/project-packet')),
            ),
            'wholeFarmGhg' => array(
                'domainVersion' => '0.11.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.94.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/policies')),
                'entryUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/entry')),
                'calculateUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/calculate')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/ghg/v1100/balance/project-packet')),
            ),
            'carbonMrvRegistry' => array(
                'domainVersion' => '0.12.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.95.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/policies')),
                'methodsUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/methods')),
                'methodUrlTemplate' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/methods/__METHOD_KEY__')),
                'compareUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/compare')),
                'readinessUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/readiness')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1200/registry/project-packet')),
            ),
            'carbonMrvProtocol' => array(
                'domainVersion' => '0.13.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.96.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/policies')),
                'templateUrlTemplate' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/template/__METHOD_KEY__')),
                'buildUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/build')),
                'validateUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/validate')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1300/protocol/project-packet')),
            ),
            'carbonMrvMonitoring' => array(
                'domainVersion' => '0.14.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.97.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/policies')),
                'templateUrlTemplate' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/template/__METHOD_KEY__')),
                'sampleSizeUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/sample-size')),
                'allocationUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/strata-allocation')),
                'buildUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/build')),
                'validateUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/validate')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1400/monitoring/project-packet')),
            ),
            'carbonMrvUncertainty' => array(
                'domainVersion' => '0.15.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.98.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/policies')),
                'budgetUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/budget')),
                'changeDetectionUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/change-detection')),
                'sampleSizeUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/detection-sample-size')),
                'buildUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/build')),
                'validateUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/validate')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1500/uncertainty/project-packet')),
            ),
            'carbonMrvVerificationLedger' => array(
                'domainVersion' => '0.16.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.99.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/policies')),
                'evidenceEntryUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/evidence-entry')),
                'buildUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/build')),
                'validateUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/validate')),
                'chainCheckUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/chain-check')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1600/verification-ledger/project-packet')),
            ),
            'carbonMrvReporting' => array(
                'domainVersion' => '0.17.0',
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.100.0',
                'moduleUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/module')),
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/health')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/schema')),
                'policiesUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/policies')),
                'templateUrlTemplate' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/template/__REPORT_TYPE__')),
                'buildUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/report/build')),
                'validateUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/report/validate')),
                'auditPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/audit-packet/build')),
                'projectPacketUrl' => esc_url_raw(rest_url('sc-lab/v1/carbon-nature/mrv/v1700/reporting/project-packet')),
            ),
            'platformCoreV3Adapter' => array(
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.105.0',
                'requiredCoreRelease' => '3.0.0',
                'productRef' => 'product:sustainable-catalyst-lab',
                'runtimeContract' => 'sc.research.unified-runtime-contract.v1',
                'unifiedRuntimeContract' => 'sc.research.unified-research-scientific-investigation-runtime.v1',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01040/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01040/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01040/schema')),
                'automaticCoreCalls' => false,
                'automaticExecution' => false,
            ),
            'platformCoreV3ObjectMapping' => array(
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.105.0',
                'requiredCoreRelease' => '3.0.0',
                'productRef' => 'product:sustainable-catalyst-lab',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01050/objects/health')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01050/objects/catalog')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01050/objects/schema')),
                'coreObjectBindingPath' => '/v1/research/unified-runtime/object-bindings',
                'mappingCount' => 20,
                'referenceFirst' => true,
                'automaticCoreSubmission' => false,
            ),
            'platformCoreV3ResearchContext' => array(
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.106.0',
                'minimumCoreRelease' => '3.0.0',
                'productRef' => 'product:sustainable-catalyst-lab',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01060/context/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01060/context/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01060/context/schema')),
                'coreSessionPath' => '/v1/research/unified-runtime/sessions',
                'coreProductBindingPath' => '/v1/research/unified-runtime/product-bindings',
                'coreObjectBindingPath' => '/v1/research/unified-runtime/object-bindings',
                'coreHandoffBindingPath' => '/v1/research/unified-runtime/handoff-bindings',
                'automaticCoreSubmission' => false,
                'automaticExecution' => false,
            ),
            'platformCoreV3ExecutionLineage' => array(
                'labReleaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : '0.107.0',
                'minimumCoreRelease' => '3.0.0',
                'productRef' => 'product:sustainable-catalyst-lab',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01070/executions/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01070/executions/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01070/executions/schema')),
                'coreExecutionBindingPath' => '/v1/research/unified-runtime/execution-bindings',
                'labIsScientificExecutionAuthority' => true,
                'coreRecordsExecutionReferencesAndLineage' => true,
                'automaticCoreSubmission' => false,
                'automaticExecution' => false,
            ),
            'platformCoreV3FindingsValidation' => array(
                'version' => '0.108.0',
                'minimumCoreRelease' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01080/research-intelligence/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01080/research-intelligence/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01080/research-intelligence/schema')),
                'automaticCoreSubmission' => false,
                'automaticScientificCertification' => false,
            ),
            'platformCoreV3VisualScene' => array(
                'version' => '0.109.0',
                'minimumCoreRelease' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01090/visual-scene/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01090/visual-scene/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01090/visual-scene/schema')),
                'coreVisualBindingPath' => '/v1/research/unified-runtime/visual-bindings',
                'coreVisualSceneContract' => 'sc.visual-runtime.scene.v1',
                'labIsScientificRenderingAuthority' => true,
                'coreIsRendererNeutral' => true,
                'automaticCoreSubmission' => false,
                'automaticRenderingByCore' => false,
            ),
            'platformCoreV3ScholarlyPackage' => array(
                'version' => '0.110.0',
                'minimumCoreRelease' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01100/scholarly-packages/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01100/scholarly-packages/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01100/scholarly-packages/schema')),
                'corePackageBindingPath' => '/v1/research/unified-runtime/package-bindings',
                'coreScholarlyBasePath' => '/v1/research/scholarly-packages',
                'labIsUnderlyingPackageAuthority' => true,
                'automaticCoreSubmission' => false,
                'automaticPublication' => false,
                'automaticReproducibilityCertification' => false,
            ),
            'platformCoreV3ScientificInvestigation' => array(
                'version' => '0.111.0',
                'minimumCoreRelease' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01110/scientific-investigations/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01110/scientific-investigations/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01110/scientific-investigations/schema')),
                'coreInvestigationBindingPath' => '/v1/research/unified-runtime/investigation-bindings',
                'labIsUnderlyingScientificInvestigationAuthority' => true,
                'coreRecordsReferenceFirstInvestigationContext' => true,
                'automaticCoreSubmission' => false,
                'automaticExecution' => false,
                'automaticScientificCertification' => false,
                'automaticTruthDetermination' => false,
            ),
            'platformCoreV3IntegrationCertification' => array(
                'version' => '0.112.0',
                'minimumCoreRelease' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01120/integration-certification/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01120/integration-certification/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01120/integration-certification/schema')),
                'coreContract' => 'sc.research.platform-integration-certification.v1',
                'coreCertificationPath' => '/v1/research/integration-certification',
                'certificationScope' => 'platform_runtime_contract_conformance_only',
                'certifiedLayerCount' => 8,
                'conformanceCaseCount' => 18,
                'automaticCoreSubmission' => false,
                'automaticProductInvocation' => false,
                'automaticCaseExecution' => false,
                'automaticScientificCertification' => false,
                'automaticProductQualityCertification' => false,
                'automaticTruthDetermination' => false,
            ),
            'scientificVisualizationDesignSystem' => array(
                'version' => '0.114.0',
                'engineVersion' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01140/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01140/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01140/schema')),
                'profileCount' => 6,
                'semanticRoleCount' => 10,
                'uncertaintyStyleCount' => 5,
                'annotationTypeCount' => 9,
                'publicationGradeRendering' => true,
                'vectorFirst' => true,
                'responsiveComposition' => true,
                'accessibilityWithoutColor' => true,
                'automaticScientificValidityCertification' => false,
                'automaticTruthDetermination' => false,
            ),
            'advancedStatisticalUncertaintyGraphics' => array(
                'version' => '0.115.0',
                'engineVersion' => '3.1.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01150/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01150/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01150/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01150/catalog')),
                'graphicTypeCount' => 16,
                'apiRouteCount' => 18,
                'publicationDesignSystem' => '0.114.0',
                'uncertaintyEngine' => '0.82.0',
                'explicitKdeBandwidth' => true,
                'explicitIntervalSemantics' => true,
                'automaticSignificanceInference' => false,
                'automaticScientificValidityCertification' => false,
                'automaticTruthDetermination' => false,
            ),
            'interactiveScientificDashboards' => array(
                'version' => '0.116.0',
                'engineVersion' => '3.2.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01160/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01160/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01160/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01160/catalog')),
                'advanced3D4DHealthUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01170/health')),
                'advanced3D4DManifestUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01170/manifest')),
                'advanced3D4DSchemaUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01170/schema')),
                'advanced3D4DCatalogUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01170/catalog')),
                'visualResearchNarrativeHealthUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01180/health')),
                'visualResearchNarrativeManifestUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01180/manifest')),
                'visualResearchNarrativeSchemaUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01180/schema')),
                'visualResearchNarrativeCatalogUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01180/catalog')),
                'figureIntelligenceHealthUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01190/health')),
                'figureIntelligenceManifestUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01190/manifest')),
                'figureIntelligenceSchemaUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01190/schema')),
                'figureIntelligenceCatalogUrl' => esc_url_raw(rest_url('sc-lab/v1/visualization/v01190/catalog')),
                'panelLimit' => 48,
                'linkLimit' => 256,
                'controlLimit' => 64,
                'apiRouteCount' => 18,
                'linkedBrushing' => true,
                'linkedFiltering' => true,
                'declaredScaleSynchronization' => true,
                'stateSnapshots' => true,
                'publicationExportPlanning' => true,
                'automaticCrossDatasetJoin' => false,
                'automaticScientificValidityCertification' => false,
                'automaticTruthDetermination' => false,
            ),
            'exploratoryDataAnalysisStudio' => array(
                'version' => '0.120.0',
                'engineVersion' => '4.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01200/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01200/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01200/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01200/catalog')),
                'apiRouteCount' => 20,
                'analysisFamilyCount' => 9,
                'sourceRowsImmutable' => true,
                'exploratoryNotConfirmatory' => true,
                'automaticSourceMutation' => false,
                'automaticHypothesisConfirmation' => false,
                'automaticSignificanceClaims' => false,
                'automaticCausalInference' => false,
                'automaticScientificValidityCertification' => false,
            ),
            'platformCoreV3ProductionRuntime' => array(
                'version' => '0.113.0',
                'minimumCoreRelease' => '3.0.0',
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01130/production-runtime/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01130/production-runtime/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/platform-core-v3/v01130/production-runtime/schema')),
                'coreRuntimeContract' => 'sc.research.unified-research-scientific-investigation-runtime.v1',
                'coreCertificationContract' => 'sc.research.platform-integration-certification.v1',
                'integrationComponentCount' => 9,
                'operationTypeCount' => 14,
                'explicitSubmissionPlansOnly' => true,
                'automaticCoreSubmission' => false,
                'automaticRetry' => false,
                'automaticRecovery' => false,
                'automaticScientificExecution' => false,
                'automaticScientificCertification' => false,
                'automaticProductQualityCertification' => false,
                'automaticTruthDetermination' => false,
                'statusCodeSuccessInference' => false,
            ),
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
        wp_localize_script('sc-lab-app', 'SCLabStatisticalModelingDiagnosticsV01210Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01210/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01210/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01210/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01210/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabBayesianAnalysisWorkbenchV01220Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01220/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01220/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01220/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01220/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabSimulationMonteCarloV01230Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01230/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01230/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01230/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01230/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabSensitivityGlobalUncertaintyV01240Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01240/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01240/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01240/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01240/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabCausalResearchStudioV01250Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01250/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01250/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01250/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01250/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabSpatialSpatiotemporalResearchStudioV01260Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01260/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01260/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01260/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01260/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabScientificTimeSeriesLaboratoryV01270Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01270/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01270/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01270/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01270/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabExperimentalDesignPowerAnalysisV01280Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01280/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01280/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01280/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01280/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabResearchReproductionReplicationStudioV01290Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01290/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01290/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01290/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01290/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabScientificResearchProjectStudioV01300Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01300/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01300/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01300/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01300/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabResearchQuestionHypothesisWorkspaceV01310Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01310/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01310/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01310/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01310/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabMethodSelectionIntelligenceV01320Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01320/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01320/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01320/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01320/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabStatisticalAssumptionDiagnosticIntelligenceV01330Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01330/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01330/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01330/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01330/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabEvidenceSynthesisIntelligenceIIV01340Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01340/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01340/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01340/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01340/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabCompetingModelHypothesisAnalysisV01350Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01350/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01350/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01350/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01350/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabScientificVisualizationExperienceV01351Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01351/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01351/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01351/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01351/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabModelArchitectureProvenanceGraphsV01352Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01352/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01352/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01352/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01352/catalog')),
        ));
        wp_localize_script('sc-lab-app', 'SCLabMultiViewScientificAnalysisCanvasV01353Config', array(
                'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01353/health')),
                'manifestUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01353/manifest')),
                'schemaUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01353/schema')),
                'catalogUrl' => esc_url_raw(rest_url('sc-lab/v1/analysis/v01353/catalog')),
        ));
        wp_enqueue_script('sc-lab-release-console-v0821', SC_LAB_URL . 'assets/js/modules/release-console-v0821.js', array('sc-lab-app'), $this->asset_version('assets/js/modules/release-console-v0821.js'), true);
        wp_localize_script('sc-lab-release-console-v0821', 'SCLabReleaseConsoleConfigV0821', array(
            'version' => SC_LAB_RELEASE_VERSION,
            'releaseVersion' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'platformCompatibilityVersion' => defined('SC_LAB_PLATFORM_COMPAT_VERSION') ? SC_LAB_PLATFORM_COMPAT_VERSION : null,
            'restBase' => esc_url_raw(rest_url('sc-lab/v1/')),
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
            'sc_lab_model_studio' => 'model-studio',
            'sc_lab_graph_studio' => 'graph-studio',
            'sc_lab_project_workspace' => 'project-workspace',
            'sc_lab_reproducible_runs' => 'reproducible-runs',
            'sc_lab_research_provenance' => 'research-provenance',
            'sc_lab_method_review' => 'method-review',
            'sc_lab_dataset_registry' => 'dataset-registry',
            'sc_lab_materials' => 'materials',
            'sc_lab_earth_systems' => 'earth-systems',
            'sc_lab_soil_organic_carbon' => 'soil-organic-carbon',
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
