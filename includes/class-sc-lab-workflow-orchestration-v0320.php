<?php
/** Sustainable Catalyst Lab v0.32.1 Workflow Checkpoints, Conditional Execution, and Partial Recovery. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Workflow_Orchestration_V0320 {
    const VERSION = '0.32.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_workflow_orchestration', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_scientific_workflows', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('workflow-orchestration','scientific-workflows','workflow-graphs','dependency-graphs','dag-orchestrator') as $alias) {
            $aliases[$alias] = 'workflow-orchestration';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="workflow-orchestration"]'); }
    public static function routes() {
        foreach (array('v0321','v0320') as $contract_version) {
            register_rest_route('sc-lab/v1', '/workflows/' . $contract_version . '/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
            register_rest_route('sc-lab/v1', '/workflows/' . $contract_version . '/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
        }
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'workflowSchema'=>'sc-lab-scientific-workflow/0.32.1',
            'runSchema'=>'sc-lab-workflow-run/0.32.1',
            'nodeRunSchema'=>'sc-lab-workflow-node-run/0.32.1',
            'checkpointSchema'=>'sc-lab-workflow-checkpoint/0.32.1',
            'recoverySchema'=>'sc-lab-workflow-recovery-plan/0.32.1',
            'typedDefinitions'=>true,'acyclicGraphsRequired'=>true,
            'dependencyAwareScheduling'=>true,'parallelReadyNodes'=>true,
            'resultBindings'=>true,'artifactHandoffs'=>true,
            'declarativeConditions'=>true,'checkpointHistory'=>true,'partialRecovery'=>true,'recoveryLineage'=>true,
            'runProvenance'=>true,'arbitraryCode'=>false,'arbitraryCallbackUrls'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/workflow-orchestration-v0321.js',
            'assets/css/sc-lab-workflow-orchestration-v0321.css',
            'contracts/scientific-workflow-v0321.schema.json',
            'contracts/workflow-run-v0321.schema.json',
            'contracts/workflow-checkpoint-v0321.schema.json',
            'contracts/workflow-recovery-plan-v0321.schema.json',
            'contracts/workflow-orchestration-policy-v0321.json',
            'includes/class-sc-lab-workflow-orchestration-v0320.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'checkpoint-aware-conditional-scientific-workflow-orchestrator',
            'dagValidation'=>true,'dependencyAwareScheduling'=>true,
            'parallelReadyNodes'=>true,'resultBindings'=>true,'artifactHandoffs'=>true,'declarativeConditions'=>true,'checkpointHistory'=>true,'partialRecovery'=>true,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
