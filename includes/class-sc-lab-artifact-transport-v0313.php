<?php
/** Sustainable Catalyst Lab v0.31.3 Distributed Artifact Transport. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Artifact_Transport_V0313 {
    const VERSION = '0.31.3';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_artifact_transport', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('artifact-transport','artifacts','result-artifacts','checkpoint-transport','distributed-artifacts') as $alias) {
            $aliases[$alias] = 'artifact-transport';
        }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="artifact-transport"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/artifact-transport/v0313/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/artifact-transport/v0313/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . $relative;
        return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'artifactSchema'=>'sc-lab-artifact-record/0.31.3',
            'uploadSchema'=>'sc-lab-artifact-upload-session/0.31.3',
            'manifestSchema'=>'sc-lab-artifact-manifest/0.31.3',
            'contentAddressed'=>true,'resumable'=>true,'sha256Verification'=>true,
            'workerScopedUploads'=>true,'leaseBoundInputAccess'=>true,'retentionControls'=>true,
        ));
    }
    public static function health() {
        $required = array(
            'assets/js/modules/artifact-transport-v0313.js',
            'assets/css/sc-lab-artifact-transport-v0313.css',
            'contracts/artifact-record-v0313.schema.json',
            'contracts/artifact-upload-session-v0313.schema.json',
            'contracts/artifact-manifest-v0313.schema.json',
            'contracts/artifact-transport-policy-v0313.json',
            'includes/class-sc-lab-artifact-transport-v0313.php',
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,
            'architecture'=>'content-addressed-resumable-artifact-transport',
            'resultArtifacts'=>true,'checkpointArtifacts'=>true,'inputMaterialization'=>true,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
