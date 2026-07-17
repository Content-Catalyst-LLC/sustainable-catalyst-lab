<?php
/** Sustainable Catalyst Lab v0.33.1 Bayesian Optimization, Active Learning, and Resource-Aware Search. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Experiment_Campaigns_V0331 {
    const VERSION = '0.33.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_experiment_campaigns', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_sequential_design', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_bayesian_optimization', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_active_learning', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('experiment-campaigns','adaptive-experiments','sequential-design','campaign-studio','adaptive-campaigns','bayesian-optimization','active-learning','resource-aware-search') as $alias) {
            $aliases[$alias] = 'experiment-campaigns';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="experiment-campaigns"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/experiment-campaigns/v0331/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/experiment-campaigns/v0331/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'campaignSchema'=>'sc-lab-experiment-campaign/0.33.1',
            'trialSchema'=>'sc-lab-experiment-trial/0.33.1',
            'eventSchema'=>'sc-lab-experiment-campaign-event/0.33.1',
            'surrogateSchema'=>'sc-lab-experiment-surrogate/0.33.1',
            'bayesianOptimization'=>true,'gaussianProcessSurrogate'=>true,
            'activeLearning'=>true,'predictiveUncertainty'=>true,
            'resourceAwareSearch'=>true,'costAdjustedAcquisition'=>true,
            'acquisitionPolicies'=>array('expected-improvement','probability-improvement','confidence-bound','max-variance'),
            'arbitraryCode'=>false,'arbitraryCallbacks'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/experiment-campaigns-v0331.js',
            'assets/css/sc-lab-experiment-campaigns-v0331.css',
            'contracts/experiment-campaign-v0331.schema.json',
            'contracts/experiment-trial-v0331.schema.json',
            'contracts/experiment-campaign-event-v0331.schema.json',
            'contracts/experiment-surrogate-v0331.schema.json',
            'contracts/experiment-campaign-policy-v0331.json',
            'includes/class-sc-lab-experiment-campaigns-v0331.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'workflow-backed-bayesian-active-learning-resource-aware-campaigns',
            'gaussianProcessSurrogate'=>true,'mixedParameterEncoding'=>true,
            'predictiveUncertainty'=>true,'costAdjustedAcquisition'=>true,
            'databaseSchemaVersion'=>2,'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
