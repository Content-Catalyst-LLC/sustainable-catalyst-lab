<?php
/** Sustainable Catalyst Lab v0.35.1 Review, Comments, Approvals, and Scientific Sign-Off. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Workspace_Review_V0351 {
    const VERSION = '0.35.1';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_workspace_review', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_scientific_signoff', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('workspace-review','scientific-review','review-signoff','scientific-signoff','approvals') as $alias) {
            $aliases[$alias] = 'workspace-review';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="workspace-review"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/workspace-review/v0351/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/workspace-review/v0351/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'threadSchema'=>'sc-lab-review-thread/0.35.1',
            'commentSchema'=>'sc-lab-review-comment/0.35.1',
            'assignmentSchema'=>'sc-lab-review-assignment/0.35.1',
            'approvalSchema'=>'sc-lab-approval-request/0.35.1',
            'decisionSchema'=>'sc-lab-approval-decision/0.35.1',
            'signoffSchema'=>'sc-lab-scientific-signoff/0.35.1',
            'appendOnlyComments'=>true,'optimisticConcurrency'=>true,
            'immutableDecisions'=>true,'immutableScientificSignoff'=>true,
            'hardDelete'=>false,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/workspace-review-v0351.js',
            'assets/css/sc-lab-workspace-review-v0351.css',
            'contracts/workspace-review-policy-v0351.json',
            'contracts/review-thread-v0351.schema.json',
            'contracts/review-comment-v0351.schema.json',
            'contracts/review-assignment-v0351.schema.json',
            'contracts/approval-request-v0351.schema.json',
            'contracts/approval-decision-v0351.schema.json',
            'contracts/scientific-signoff-v0351.schema.json',
            'contracts/review-event-v0351.schema.json',
            'includes/class-sc-lab-workspace-review-v0351.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) { $files[$relative]=self::state($relative); if (empty($files[$relative]['exists'])) { $ok=false; } }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'workspace-review-comments-approvals-scientific-signoff',
            'databaseSchemaVersion'=>2,'appendOnlyComments'=>true,'approvalGates'=>true,
            'optimisticConcurrency'=>true,'immutableDecisions'=>true,'immutableScientificSignoff'=>true,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
