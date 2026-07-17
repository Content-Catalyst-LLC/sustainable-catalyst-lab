<?php
/** Sustainable Catalyst Lab v0.36.0 Scientific Artifact Repository and Data Federation. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Artifact_Repository_V0360 {
    const VERSION = '0.36.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_artifact_repository', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_data_federation', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('artifact-repository','scientific-artifacts','data-federation','federated-artifacts','artifact-collections') as $alias) { $aliases[$alias] = 'artifact-repository'; }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="artifact-repository"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/artifact-repository/v0360/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/artifact-repository/v0360/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'collectionSchema'=>'sc-lab-artifact-collection/0.36.0',
            'artifactSchema'=>'sc-lab-repository-artifact/0.36.0',
            'sourceSchema'=>'sc-lab-federated-source/0.36.0',
            'manifestSchema'=>'sc-lab-federation-manifest/0.36.0',
            'syncSchema'=>'sc-lab-federation-sync/0.36.0',
            'conflictSchema'=>'sc-lab-federation-conflict/0.36.0',
            'eventSchema'=>'sc-lab-artifact-repository-event/0.36.0',
            'workspaceGovernance'=>true,'contentAddressedReferences'=>true,
            'manifestFederation'=>true,'automaticRemoteCallbacks'=>false,
            'tombstones'=>true,'conflictResolution'=>true,'hardDelete'=>false,'arbitraryCode'=>false,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/artifact-repository-v0360.js',
            'assets/css/sc-lab-artifact-repository-v0360.css',
            'contracts/artifact-repository-policy-v0360.json',
            'contracts/artifact-collection-v0360.schema.json',
            'contracts/repository-artifact-v0360.schema.json',
            'contracts/federated-source-v0360.schema.json',
            'contracts/federation-manifest-v0360.schema.json',
            'contracts/federation-sync-v0360.schema.json',
            'contracts/federation-conflict-v0360.schema.json',
            'contracts/artifact-repository-event-v0360.schema.json',
            'includes/class-sc-lab-artifact-repository-v0360.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) { $files[$relative]=self::state($relative); if (empty($files[$relative]['exists'])) { $ok=false; } }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'workspace-governed-artifact-collections-and-manifest-federation',
            'databaseSchemaVersion'=>1,'contentAddressedReferences'=>true,
            'manifestFederation'=>true,'automaticRemoteCallbacks'=>false,
            'tombstones'=>true,'conflictResolution'=>true,'hardDelete'=>false,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
