<?php
/** Sustainable Catalyst Lab v0.34.1 Ensemble Simulation, Global Sensitivity, and Uncertainty. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Ensemble_Uncertainty_V0341 {
    const VERSION = '0.34.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_ensemble_simulation', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_uncertainty_analysis', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_global_sensitivity', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('ensemble-uncertainty','ensemble-simulation','uncertainty-analysis','global-sensitivity','model-ensembles','sensitivity-uncertainty') as $alias) {
            $aliases[$alias] = 'ensemble-uncertainty';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="ensemble-uncertainty"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/ensemble-uncertainty/v0341/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/ensemble-uncertainty/v0341/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'studySchema'=>'sc-lab-ensemble-study/0.34.1',
            'evaluationSchema'=>'sc-lab-ensemble-evaluation/0.34.1',
            'analysisSchema'=>'sc-lab-ensemble-analysis/0.34.1',
            'designs'=>array('monte-carlo','latin-hypercube','sobol','saltelli-sobol'),
            'distributions'=>array('uniform','normal','lognormal','triangular','discrete'),
            'registeredModelsOnly'=>true,'weightedEnsembles'=>true,
            'globalSensitivity'=>true,'uncertaintyIntervals'=>true,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/ensemble-uncertainty-v0341.js',
            'assets/css/sc-lab-ensemble-uncertainty-v0341.css',
            'contracts/ensemble-study-v0341.schema.json',
            'contracts/ensemble-evaluation-v0341.schema.json',
            'contracts/ensemble-analysis-v0341.schema.json',
            'contracts/ensemble-event-v0341.schema.json',
            'contracts/ensemble-policy-v0341.json',
            'includes/class-sc-lab-ensemble-uncertainty-v0341.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'ensemble-simulation-global-sensitivity-uncertainty',
            'databaseSchemaVersion'=>1,'registeredModelsOnly'=>true,
            'weightedEnsembles'=>true,'dispatcherBacked'=>true,
            'arbitraryCode'=>false,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
