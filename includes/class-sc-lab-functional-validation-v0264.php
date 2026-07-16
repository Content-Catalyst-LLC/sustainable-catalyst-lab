<?php
/**
 * Sustainable Catalyst Lab v0.26.4 cross-laboratory functional validation.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Functional_Validation_V0264 {
    const VERSION = '0.26.4';
    const REPORT_OPTION = 'sc_lab_functional_health_v0264';
    private static $initialized = false;
    private static $front_assets = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue_front'), 90);
        add_action('admin_menu', array(__CLASS__, 'admin_menu'), 50);
        add_action('admin_enqueue_scripts', array(__CLASS__, 'admin_assets'));
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe']) || isset($_GET['sc_lab_validation'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    public static function modules() {
        $labels = array(
            'activity'=>'Activity','aerospace-engineering-flight-systems'=>'Aerospace Engineering and Flight Systems','architecture-building'=>'Architecture and Building Performance','astronomy'=>'Astronomy Calculations','biochemistry-molecular-analysis'=>'Biochemistry and Molecular Analysis','biology'=>'Biology','biomedical-engineering-biosignals'=>'Biomedical Engineering and Biosignals','biotechnology-bioprocess-engineering'=>'Biotechnology and Bioprocess Engineering','chemistry'=>'Chemistry','circular-economy-industrial-ecology'=>'Circular Economy and Industrial Ecology','civil-infrastructure'=>'Civil Engineering and Infrastructure','climate-maps'=>'Climate Maps','code-studio'=>'Code Studio','comparative-economics-development-systems'=>'Comparative Economics and Development Systems','dataset-inspector'=>'Dataset Inspector','dataset-registry'=>'Dataset Registry','documentation'=>'Documentation','earth-systems'=>'Earth Systems','electrical-embedded'=>'Electrical, Electronics, and Embedded Systems','energy-engineering'=>'Energy and Engineering','evidence-decisions'=>'Evidence and Decisions','experiments'=>'Experiments','genetics-genomics-sequence-analysis'=>'Genetics and Genomics','laboratory-data-instrumentation'=>'Laboratory Data and Instrumentation','marine-biology'=>'Marine Biology','materials'=>'Materials','mechanical-thermal'=>'Mechanical and Thermal Engineering','microbiology-laboratory'=>'Microbiology','notebook'=>'Notebook','numerical-methods'=>'Numerical Methods Studio','numerical-validation'=>'Numerical Validation Library','numerical-governance'=>'Precision and Solver Governance','numerical-visualization'=>'Scientific Visualization','long-running-jobs'=>'Long Jobs and Checkpoints','overview'=>'Overview','project-workspace'=>'Project Architecture','reproducible-runs'=>'Reproducible Computational Runs','research-provenance'=>'Evidence, Sources, and Research Provenance','method-review'=>'Research Quality and Method Review','scholarly-discovery'=>'External Scholarly and Data Discovery','experiment-framework'=>'Reproducible Experiment Framework','physics'=>'Physics','report-studio'=>'Report Studio','rocket-propulsion-spaceflight'=>'Rocket Propulsion and Spaceflight','science-engineering'=>'Science and Engineering','scientific-feeds'=>'Scientific Feeds','source-registry'=>'Source Registry','space-telescopes'=>'Space and Astronomy Observations','sustainable-cities-resilience'=>'Sustainable Cities and Urban Resilience','system-status'=>'System Status','urban-planning-spatial'=>'Urban Planning and Spatial Systems','visualization-studio'=>'Visualization Studio','workspace-data'=>'Workspace Data'
        );
        $priority = array('climate-maps','marine-biology','space-telescopes','numerical-methods','numerical-validation','numerical-governance','numerical-visualization','long-running-jobs','astronomy','microbiology-laboratory','chemistry','physics','biology','earth-systems','energy-engineering','materials','electrical-embedded','mechanical-thermal','civil-infrastructure','project-workspace','dataset-registry','reproducible-runs','research-provenance','method-review','scholarly-discovery','experiment-framework');
        $specs = array();
        foreach ($labels as $module => $label) {
            $specs[$module] = array(
                'module' => $module,
                'label' => $label,
                'group' => in_array($module, array('scientific-feeds','climate-maps','space-telescopes','marine-biology','source-registry','dataset-inspector','dataset-registry'), true) ? 'Observe' : 'Laboratory',
                'priority' => in_array($module, $priority, true),
                'panelSelector' => '[data-lab-module="' . $module . '"]',
                'controllerPaths' => array(),
                'actionSelector' => null,
                'outputSelector' => null,
                'actionMode' => 'structural',
                'timeoutMs' => 8000,
                'requirement' => 'browser',
            );
        }
        $overrides = array(
            'climate-maps' => array('controllerPaths'=>array('SCLab.ClimateMap'),'actionSelector'=>'[data-climate-render]','outputSelector'=>'[data-climate-image]','actionMode'=>'image-src','timeoutMs'=>16000,'requirement'=>'external-source'),
            'marine-biology' => array('controllerPaths'=>array('SCLabObserveFeedsV02634','SCLab.ObserveFeedsV02634'),'actionSelector'=>'[data-marine-load]','outputSelector'=>'[data-marine-summary]','actionMode'=>'feed','timeoutMs'=>24000,'requirement'=>'external-source'),
            'space-telescopes' => array('controllerPaths'=>array('SCLabObserveFeedsV02634','SCLab.ObserveFeedsV02634'),'actionSelector'=>'[data-space-load]','outputSelector'=>'[data-space-summary]','actionMode'=>'feed','timeoutMs'=>24000,'requirement'=>'external-source'),
            'numerical-methods' => array('controllerPaths'=>array('SCLab.NumericalMethodsStudio','SCLabNumericalMethodsV0270'),'actionSelector'=>'[data-numerical-run]','outputSelector'=>'[data-numerical-output]','actionMode'=>'calculation','timeoutMs'=>30000,'requirement'=>'backend-required'),
            'long-running-jobs' => array('controllerPaths'=>array('SCLab.LongRunningJobsStudio','SCLabLongJobsV0272'),'actionSelector'=>'[data-longjobs-refresh]','outputSelector'=>'[data-longjobs-list]','actionMode'=>'refresh','timeoutMs'=>30000,'requirement'=>'backend-required'),
            'numerical-validation' => array('controllerPaths'=>array('SCLab.NumericalValidationStudio','SCLabNumericalValidationV0271'),'actionSelector'=>'[data-benchmark-run]','outputSelector'=>'[data-benchmark-summary]','actionMode'=>'calculation','timeoutMs'=>30000,'requirement'=>'backend-required'),
            'numerical-governance' => array('controllerPaths'=>array('SCLab.NumericalGovernanceStudio','SCLabNumericalGovernanceV0273'),'actionSelector'=>'[data-governance-recommend]','outputSelector'=>'[data-governance-recommendation]','actionMode'=>'calculation','timeoutMs'=>30000,'requirement'=>'backend-required'),
            'numerical-visualization' => array('controllerPaths'=>array('SCLab.NumericalVisualizationStudio','SCLabNumericalVisualizationV0274'),'actionSelector'=>'[data-visual-heatmap-example]','outputSelector'=>'[data-visual-outputs]','actionMode'=>'interface','timeoutMs'=>30000,'requirement'=>'backend-required'),
            'project-workspace' => array('controllerPaths'=>array('SCLab.ProjectWorkspaceV0280','SCLabProjectWorkspaceV0280'),'actionSelector'=>'[data-workspace-v0280-checkpoint]','outputSelector'=>'[data-workspace-v0280-status]','actionMode'=>'interface','timeoutMs'=>10000),
            'dataset-registry' => array('controllerPaths'=>array('SCLab.DatasetRegistryV0281','SCLabDatasetRegistryV0281'),'actionSelector'=>'[data-dataset-v0281-prepare]','outputSelector'=>'[data-dataset-v0281-status]','actionMode'=>'interface','timeoutMs'=>10000),
            'reproducible-runs' => array('controllerPaths'=>array('SCLab.ReproducibleRunsV0282','SCLabReproducibleRunsV0282'),'actionSelector'=>'[data-repro-v0282-example]','outputSelector'=>'[data-repro-v0282-status]','actionMode'=>'interface','timeoutMs'=>30000,'requirement'=>'backend-required'),
            'research-provenance' => array('controllerPaths'=>array('SCLab.ResearchProvenanceV0290'),'actionSelector'=>'[data-prov-v0290-add-source]','outputSelector'=>'[data-prov-v0290-status]','actionMode'=>'interface','timeoutMs'=>10000),
            'method-review' => array('controllerPaths'=>array('SCLab.ResearchQualityV0291'),'actionSelector'=>'[data-quality-v0291-evaluate]','outputSelector'=>'[data-quality-v0291-status]','actionMode'=>'interface','timeoutMs'=>30000,'requirement'=>'backend-optional'),
            'scholarly-discovery' => array('controllerPaths'=>array('SCLab.ExternalDiscoveryV0292'),'actionSelector'=>'[data-discovery-v0292-search]','outputSelector'=>'[data-discovery-v0292-status]','actionMode'=>'interface','timeoutMs'=>65000,'requirement'=>'backend-optional'),
            'experiment-framework' => array('controllerPaths'=>array('SCLab.ExperimentFrameworkV0300'),'actionSelector'=>'[data-exp-v0300-validate]','outputSelector'=>'[data-exp-v0300-status]','actionMode'=>'interface','timeoutMs'=>20000,'requirement'=>'backend-optional'),
            'astronomy' => array('controllerPaths'=>array('SCLab.AstronomyLab'),'actionSelector'=>'[data-astronomy-run]','outputSelector'=>'[data-astronomy-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'microbiology-laboratory' => array('controllerPaths'=>array('SCLab.MicrobiologyLaboratory'),'actionSelector'=>'[data-mb-run]','outputSelector'=>'[data-mb-results]','actionMode'=>'calculation','timeoutMs'=>10000),
            'chemistry' => array('controllerPaths'=>array('SCLab.Stoichiometry','SCLab.ChemistryLab'),'actionSelector'=>'[data-percent-run]','outputSelector'=>'[data-percent-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'physics' => array('controllerPaths'=>array('SCLab.PhysicsLab'),'actionSelector'=>'[data-physics-run]','outputSelector'=>'[data-physics-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'biology' => array('controllerPaths'=>array('SCLab.BiologyLab'),'actionSelector'=>'[data-biology-run]','outputSelector'=>'[data-biology-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'earth-systems' => array('controllerPaths'=>array('SCLab.EarthLab'),'actionSelector'=>'[data-earth-run]','outputSelector'=>'[data-earth-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'energy-engineering' => array('controllerPaths'=>array('SCLab.EnergyLab'),'actionSelector'=>'[data-energy-run]','outputSelector'=>'[data-energy-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'materials' => array('controllerPaths'=>array('SCLab.MaterialsLab'),'actionSelector'=>'[data-materials-run]','outputSelector'=>'[data-materials-output]','actionMode'=>'calculation','timeoutMs'=>10000),
            'electrical-embedded' => array('controllerPaths'=>array('SCLab.ElectricalEmbedded'),'actionSelector'=>'[data-electrical-run]','outputSelector'=>'[data-electrical-result]','actionMode'=>'calculation','timeoutMs'=>10000),
            'mechanical-thermal' => array('controllerPaths'=>array('SCLab.MechanicalThermalLab'),'actionSelector'=>'[data-mt-run]','outputSelector'=>'[data-mt-results]','actionMode'=>'calculation','timeoutMs'=>10000),
            'civil-infrastructure' => array('controllerPaths'=>array('SCLab.CivilInfrastructureLab'),'actionSelector'=>'[data-ci-run]','outputSelector'=>'[data-ci-results]','actionMode'=>'calculation','timeoutMs'=>10000),
            'architecture-building' => array('controllerPaths'=>array('SCLab.ArchitectureBuilding'),'actionSelector'=>'[data-architecture-run]','outputSelector'=>'[data-architecture-results]','actionMode'=>'calculation','timeoutMs'=>10000),
            'urban-planning-spatial' => array('controllerPaths'=>array('SCLab.UrbanPlanningSpatial'),'actionMode'=>'structural'),
            'sustainable-cities-resilience' => array('controllerPaths'=>array('SCLab.SustainableCitiesResilience'),'actionMode'=>'structural'),
            'comparative-economics-development-systems' => array('controllerPaths'=>array('SCLab.ComparativeEconomicsDevelopmentSystems'),'actionMode'=>'structural'),
            'aerospace-engineering-flight-systems' => array('controllerPaths'=>array('SCLab.AerospaceEngineeringFlightSystems'),'actionMode'=>'structural'),
            'rocket-propulsion-spaceflight' => array('controllerPaths'=>array('SCLab.RocketPropulsionSpaceflight'),'actionMode'=>'structural'),
        );
        foreach ($overrides as $module => $values) { if (isset($specs[$module])) { $specs[$module] = array_merge($specs[$module], $values); } }
        return array_values($specs);
    }

    public static function maybe_enqueue_front() {
        if (!self::is_lab_request() || self::$front_assets) { return; }
        self::$front_assets = true;
        $style = 'assets/css/sc-lab-functional-validation-v0264.css';
        $script = 'assets/js/sc-lab-functional-validation-v0264.js';
        wp_enqueue_style('sc-lab-functional-validation-v0264', SC_LAB_URL . $style, array('sc-lab-app'), self::asset_version($style));
        wp_enqueue_script('sc-lab-functional-validation-v0264', SC_LAB_URL . $script, array('sc-lab-runtime-v02631'), self::asset_version($script), true);
        wp_localize_script('sc-lab-functional-validation-v0264', 'SCLabFunctionalValidationConfigV0264', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'registry' => self::modules(),
            'autoRun' => isset($_GET['sc_lab_validation']),
            'requestedModule' => isset($_GET['sc_lab_module']) ? sanitize_key(wp_unslash($_GET['sc_lab_module'])) : null,
            'serverHealthUrl' => esc_url_raw(rest_url('sc-lab/v1/functional/v0264/server-health')),
        ));
    }

    public static function admin_menu() {
        add_submenu_page('options-general.php', 'Lab Functional Health', 'Lab Functional Health', 'manage_options', 'sc-lab-functional-health', array(__CLASS__, 'admin_page'));
    }

    public static function admin_assets($hook) {
        if ($hook !== 'settings_page_sc-lab-functional-health') { return; }
        $style = 'assets/css/sc-lab-functional-validation-v0264.css';
        $script = 'assets/js/sc-lab-functional-health-admin-v0264.js';
        wp_enqueue_style('sc-lab-functional-validation-v0264-admin', SC_LAB_URL . $style, array(), self::asset_version($style));
        wp_enqueue_script('sc-lab-functional-health-admin-v0264', SC_LAB_URL . $script, array(), self::asset_version($script), true);
        wp_localize_script('sc-lab-functional-health-admin-v0264', 'SCLabFunctionalHealthAdminConfigV0264', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'registry' => self::modules(),
            'labUrl' => esc_url_raw(apply_filters('sc_lab_functional_validation_lab_url', home_url('/lab/'))),
            'saveUrl' => esc_url_raw(rest_url('sc-lab/v1/functional/v0264/reports')),
            'latestUrl' => esc_url_raw(rest_url('sc-lab/v1/functional/v0264/reports/latest')),
            'serverHealthUrl' => esc_url_raw(rest_url('sc-lab/v1/functional/v0264/server-health')),
            'nonce' => wp_create_nonce('wp_rest'),
        ));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/functional/v0264/registry', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'registry_response'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/functional/v0264/server-health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'server_health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/functional/v0264/reports', array('methods'=>WP_REST_Server::CREATABLE,'callback'=>array(__CLASS__,'save_report'),'permission_callback'=>array(__CLASS__,'can_manage')));
        register_rest_route('sc-lab/v1', '/functional/v0264/reports/latest', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'latest_report'),'permission_callback'=>array(__CLASS__,'can_manage')));
    }

    public static function can_manage() { return current_user_can('manage_options'); }
    public static function registry_response() { return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'modules'=>self::modules())); }

    private static function manifest() {
        $path = SC_LAB_DIR . 'build/sc-lab-release-manifest.json';
        if (!is_file($path)) { return array(); }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array();
    }

    public static function server_health() {
        $manifest = self::manifest();
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        $required = array('assets/js/sc-lab-functional-validation-v0264.js','assets/js/sc-lab-functional-health-admin-v0264.js','assets/css/sc-lab-functional-validation-v0264.css','includes/class-sc-lab-functional-validation-v0264.php','templates/lab-app.php');
        $files = array();
        foreach ($required as $relative) { $files[$relative] = array('exists'=>is_file(SC_LAB_DIR.$relative),'sha256'=>is_file(SC_LAB_DIR.$relative)?hash_file('sha256',SC_LAB_DIR.$relative):null); }
        $module_count = count(self::modules());
        $manifest_count = isset($manifest['moduleCount']) ? absint($manifest['moduleCount']) : null;
        $feed_health = class_exists('SC_Lab_Observe_Feeds_V02634') ? SC_Lab_Observe_Feeds_V02634::health() : null;
        $feed_data = $feed_health instanceof WP_REST_Response ? $feed_health->get_data() : null;
        $ok = !in_array(false, array_map(function($row){ return !empty($row['exists']); }, $files), true) && $module_count === 53;
        return rest_ensure_response(array(
            'ok'=>$ok,'version'=>self::VERSION,'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'moduleCount'=>$module_count,'manifestModuleCount'=>$manifest_count,'files'=>$files,
            'features'=>array('feedsEnabled'=>!empty($settings['enable_feeds']),'climateMapsEnabled'=>!empty($settings['enable_climate_maps']),'remoteComputeEnabled'=>!empty($settings['enable_remote_compute'])),
            'observe'=>$feed_data,'latestReport'=>get_option(self::REPORT_OPTION, null),'time'=>gmdate('c')
        ));
    }

    private static function sanitize_report_value($value, $depth = 0) {
        if ($depth > 8) { return null; }
        if (is_array($value)) { $out=array(); $count=0; foreach ($value as $key=>$item) { if ($count++ > 250) break; $safe_key=is_int($key)?$key:sanitize_key((string)$key); $out[$safe_key]=self::sanitize_report_value($item,$depth+1); } return $out; }
        if (is_bool($value) || is_int($value) || is_float($value) || is_null($value)) { return $value; }
        return substr(sanitize_textarea_field((string)$value), 0, 8000);
    }

    public static function save_report(WP_REST_Request $request) {
        $raw = $request->get_json_params();
        if (!is_array($raw)) { return new WP_Error('invalid_report','A JSON functional-health report is required.',array('status'=>400)); }
        $report = self::sanitize_report_value($raw);
        $report['storedAt'] = gmdate('c');
        $report['storedBy'] = get_current_user_id();
        $report['runtimeVersion'] = self::VERSION;
        update_option(self::REPORT_OPTION, $report, false);
        return rest_ensure_response(array('ok'=>true,'storedAt'=>$report['storedAt'],'summary'=>isset($report['summary'])?$report['summary']:null));
    }

    public static function latest_report() { return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'report'=>get_option(self::REPORT_OPTION, null))); }

    public static function admin_page() {
        if (!current_user_can('manage_options')) { return; }
        ?>
        <div class="wrap sc-lab-functional-admin-v0264" data-sc-lab-functional-admin-v0264>
          <h1>Sustainable Catalyst Lab Functional Health</h1>
          <p>Runs real browser checks against isolated Lab panels. Safe primary actions are triggered where available; source and backend degradation is reported separately from controller or calculation failures.</p>
          <div class="sc-lab-functional-toolbar-v0264">
            <button type="button" class="button button-primary" data-functional-run-priority>Run priority laboratories</button>
            <button type="button" class="button" data-functional-run-all>Run all 53 panels</button>
            <button type="button" class="button" data-functional-stop>Stop</button>
            <button type="button" class="button" data-functional-export>Export report</button>
            <button type="button" class="button" data-functional-refresh-server>Refresh server health</button>
          </div>
          <div class="sc-lab-functional-summary-v0264" data-functional-summary>Ready to run checks.</div>
          <div class="sc-lab-functional-progress-v0264" aria-live="polite"><progress max="53" value="0" data-functional-progress></progress><span data-functional-progress-label>0 / 0</span></div>
          <div class="sc-lab-functional-server-v0264" data-functional-server></div>
          <table class="widefat striped sc-lab-functional-table-v0264">
            <thead><tr><th>Laboratory</th><th>Panel</th><th>Controller</th><th>Primary action</th><th>Result</th><th>Errors</th><th>Status</th><th>Open</th></tr></thead>
            <tbody data-functional-rows></tbody>
          </table>
          <iframe title="Lab functional validation runner" data-functional-frame class="sc-lab-functional-frame-v0264"></iframe>
          <details><summary>Raw report</summary><pre data-functional-json>No report has been run.</pre></details>
        </div>
        <?php
    }
}
