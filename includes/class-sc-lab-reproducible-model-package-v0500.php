<?php
/** Sustainable Catalyst Lab v0.50.0 — Reproducible Model Packages, Registry & Research Bundles. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Reproducible_Model_Package_V0500 {
    const VERSION='0.50.0';
    private static $initialized=false;
    public static function init(){
        if(self::$initialized){return;}
        self::$initialized=true;
        add_action('rest_api_init',array(__CLASS__,'routes'));
    }
    public static function routes(){
        register_rest_route('sc-lab/v1','/model-packages/v0500/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/model-packages/v0500/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function schema(){
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,
            'packageSchema'=>'sc-lab-reproducible-model-package/0.50.0',
            'researchBundleSchema'=>'sc-lab-model-research-bundle/0.50.0',
            'registryProjectionSchema'=>'sc-lab-model-package-registry-projection/0.50.0',
            'sharedModelSchema'=>'sc-catalyst-computational-model/0.49.0',
            'exports'=>array('json','zip'),'registryIntegration'=>true,'arbitraryCode'=>false,
        ));
    }
    public static function health(){
        $required=array(
            'backend/app/reproducible_model_package.py',
            'backend/tests/test_reproducible_model_package_v0500.py',
            'assets/js/modules/reproducible-model-package-v0500.js',
            'assets/css/sc-lab-reproducible-model-package-v0500.css',
            'contracts/reproducible-model-package-v0500.schema.json',
            'contracts/model-research-bundle-v0500.schema.json',
            'contracts/model-package-policy-v0500.json',
            'templates/lab-app.php',
        );
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'reproducible-model-packages-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'reproduciblePackage'=>true,'portableResearchZip'=>true,'registryProjection'=>true,
            'componentHashVerification'=>true,'sharedModelContract'=>'0.49.0',
            'arbitraryCode'=>false,'automaticPublication'=>false,'automaticRegistryPromotion'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,
            'files'=>$files,'time'=>gmdate('c'),
        ));
    }
}
