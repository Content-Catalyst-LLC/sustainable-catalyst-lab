<?php
/** Sustainable Catalyst Lab v0.39.2 Multi-Instance Operations, Backup, Migration, and Disaster Recovery. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Multi_Instance_Operations_V0392 {
    const VERSION = '0.39.2';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
        add_filter('sc_lab_panel_aliases_v02631', array(__CLASS__, 'aliases'));
        add_shortcode('sc_lab_multi_instance_operations', array(__CLASS__, 'shortcode'));
        add_shortcode('sc_lab_disaster_recovery', array(__CLASS__, 'shortcode'));
    }
    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        foreach (array('multi-instance-operations','instance-operations','backup-restore','migration-operations','disaster-recovery','recovery-drills') as $alias) { $aliases[$alias] = 'multi-instance-operations-v0392'; }
        return $aliases;
    }
    public static function shortcode() { return do_shortcode('[sc_lab_app module="multi-instance-operations-v0392"]'); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/multi-instance-operations/v0392/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
    }
    private static function state($relative) { $path=SC_LAB_DIR.$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function health() {
        $required=array('backend/app/multi_instance_operations.py','backend/tests/test_multi_instance_operations_v0392.py','assets/js/modules/multi-instance-operations-v0392.js','assets/css/sc-lab-multi-instance-operations-v0392.css','contracts/instance-manifest-v0392.schema.json','contracts/backup-manifest-v0392.schema.json','contracts/migration-plan-v0392.schema.json','contracts/instance-transfer-envelope-v0392.schema.json','contracts/recovery-drill-v0392.schema.json','contracts/multi-instance-operations-policy-v0392.json');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'stableInstanceIdentity'=>true,'consistentSqliteSnapshots'=>true,'signedBackupManifests'=>true,'stagedNonDestructiveRestore'=>true,'idempotentMigrations'=>true,'signedCrossInstanceTransfers'=>true,'rpoRtoRecoveryDrills'=>true,'activeFileOverwriteByApi'=>false,'remoteObjectStorage'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Multi_Instance_Operations_V0392::init();
