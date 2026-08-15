<?php
/** Sustainable Catalyst Lab v0.49.0 — Lab ↔ Workbench Model Handoff & Shared Computational Contract. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Shared_Model_Handoff_V0490 {
    const VERSION='0.49.0';
    private static $initialized=false;
    public static function init(){
        if(self::$initialized){return;}
        self::$initialized=true;
        add_action('rest_api_init',array(__CLASS__,'routes'));
    }
    public static function routes(){
        register_rest_route('sc-lab/v1','/model-handoff/v0490/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/model-handoff/v0490/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function schema(){
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'sharedModelSchema'=>'sc-catalyst-computational-model/0.49.0',
            'handoffSchema'=>'sc-catalyst-model-handoff/0.49.0',
            'typedResearchContract'=>'sc-research-model/1.0',
            'storageKey'=>'sc_catalyst_model_handoff_v0490',
            'legacyStorageKey'=>'sc_workbench_handoff',
            'legacyEvent'=>'sc:workbench-handoff',
            'arbitraryCode'=>false,'automaticRemoteDelivery'=>false,
        ));
    }
    public static function health(){
        $required=array(
            'backend/app/shared_model_handoff.py',
            'backend/tests/test_shared_model_handoff_v0490.py',
            'assets/js/modules/shared-model-handoff-v0490.js',
            'assets/css/sc-lab-shared-model-handoff-v0490.css',
            'contracts/computational-model-v0490.schema.json',
            'contracts/model-handoff-v0490.schema.json',
            'contracts/model-handoff-policy-v0490.json',
            'templates/lab-app.php',
        );
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'bidirectional-model-handoff-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'labToWorkbench'=>true,'workbenchToLab'=>true,'sharedComputationalContract'=>true,
            'sameOriginTransport'=>true,'legacyWorkbenchCompatibility'=>true,
            'modelStudioRevalidation'=>true,'packetIntegrityVerification'=>true,
            'arbitraryCode'=>false,'arbitraryPython'=>false,'arbitraryJavaScript'=>false,'shellExecution'=>false,
            'automaticRemoteDelivery'=>false,'threeApplicationCardRowPreserved'=>true,'contextualNavigationPreserved'=>true,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
