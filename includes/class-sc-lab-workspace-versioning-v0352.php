<?php
/** Sustainable Catalyst Lab v0.35.2 Version History, Branching, Merge, and Conflict Resolution. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Workspace_Versioning_V0352 {
    const VERSION = '0.35.2';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_workspace_versioning', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_research_branches', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('workspace-versioning','version-history','research-branches','merge-conflicts','workspace-history') as $alias) {
            $aliases[$alias] = 'workspace-versioning';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="workspace-versioning"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/workspace-versioning/v0352/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/workspace-versioning/v0352/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'branchSchema'=>'sc-lab-workspace-branch/0.35.2',
            'snapshotSchema'=>'sc-lab-workspace-snapshot/0.35.2',
            'compareSchema'=>'sc-lab-workspace-version-compare/0.35.2',
            'mergeSchema'=>'sc-lab-workspace-merge-request/0.35.2',
            'conflictSchema'=>'sc-lab-workspace-merge-conflict/0.35.2',
            'eventSchema'=>'sc-lab-workspace-version-event/0.35.2',
            'immutableSnapshots'=>true,'threeWayMerge'=>true,'pathLevelConflicts'=>true,
            'protectedBranches'=>true,'signedApprovalGate'=>true,
            'restoreCreatesNewSnapshot'=>true,'historyRewrite'=>false,'hardDelete'=>false,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/workspace-versioning-v0352.js',
            'assets/css/sc-lab-workspace-versioning-v0352.css',
            'contracts/workspace-version-policy-v0352.json',
            'contracts/workspace-branch-v0352.schema.json',
            'contracts/workspace-snapshot-v0352.schema.json',
            'contracts/workspace-version-compare-v0352.schema.json',
            'contracts/workspace-merge-request-v0352.schema.json',
            'contracts/workspace-merge-conflict-v0352.schema.json',
            'contracts/workspace-version-event-v0352.schema.json',
            'includes/class-sc-lab-workspace-versioning-v0352.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) { $files[$relative]=self::state($relative); if (empty($files[$relative]['exists'])) { $ok=false; } }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'immutable-workspace-snapshots-branches-three-way-merge-conflicts',
            'databaseSchemaVersion'=>3,'immutableSnapshots'=>true,'protectedBranches'=>true,
            'threeWayMerge'=>true,'signedApprovalGate'=>true,'historyRewrite'=>false,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
