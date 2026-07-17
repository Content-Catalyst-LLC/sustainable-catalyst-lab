<?php
/** Sustainable Catalyst Lab v0.32.2 Scheduled and Event-Driven Research Runs. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Workflow_Automation_V0322 {
    const VERSION = '0.32.2';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_workflow_automation', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_scheduled_research_runs', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('workflow-automation','scheduled-runs','event-driven-runs','workflow-schedules','research-automation') as $alias) {
            $aliases[$alias] = 'workflow-automation';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="workflow-automation"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/workflow-automation/v0322/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/workflow-automation/v0322/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'scheduleSchema'=>'sc-lab-workflow-schedule/0.32.2',
            'eventSchema'=>'sc-lab-workflow-trigger-event/0.32.2',
            'firingSchema'=>'sc-lab-workflow-schedule-firing/0.32.2',
            'intervalSchedules'=>true,'cronUtc'=>true,'oneTimeSchedules'=>true,
            'authenticatedEvents'=>true,'eventDeduplication'=>true,
            'misfireRecovery'=>true,'concurrencyControls'=>true,
            'arbitraryCallbacks'=>false,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/workflow-automation-v0322.js',
            'assets/css/sc-lab-workflow-automation-v0322.css',
            'contracts/workflow-schedule-v0322.schema.json',
            'contracts/workflow-trigger-event-v0322.schema.json',
            'contracts/workflow-schedule-firing-v0322.schema.json',
            'contracts/workflow-scheduling-policy-v0322.json',
            'includes/class-sc-lab-workflow-automation-v0322.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'durable-scheduled-and-event-driven-workflow-automation',
            'intervalSchedules'=>true,'cronUtc'=>true,'authenticatedEvents'=>true,
            'eventDeduplication'=>true,'misfireRecovery'=>true,'concurrencyControls'=>true,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
