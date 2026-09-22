<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Platform_Core_V3_Scholarly_Package_V01100 {
    const VERSION='0.110.0';
    const MINIMUM_CORE_RELEASE='3.0.0';
    const PRODUCT_REF='product:sustainable-catalyst-lab';
    const BRIDGE_SCHEMA='sc-lab-platform-core-v3-reproducibility-scholarly-package/0.110.0';
    const CORE_UNIFIED_CONTRACT='sc.research.unified-research-scientific-investigation-runtime.v1';
    const CORE_SCHOLARLY_CONTRACT='sc.research.scholarly-interoperability-packaging.v1';
    const CORE_PACKAGE_BINDING_PATH='/v1/research/unified-runtime/package-bindings';
    const CORE_SCHOLARLY_BASE_PATH='/v1/research/scholarly-packages';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/platform-core-v3/v01100/scholarly-packages';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=plugin_dir_path(dirname(__FILE__)).$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'bridgeSchema'=>self::BRIDGE_SCHEMA,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'coreUnifiedRuntimeContract'=>self::CORE_UNIFIED_CONTRACT,'coreScholarlyContract'=>self::CORE_SCHOLARLY_CONTRACT,'corePackageBindingPath'=>self::CORE_PACKAGE_BINDING_PATH,'coreScholarlyBasePath'=>self::CORE_SCHOLARLY_BASE_PATH,'automaticCoreSubmission'=>false,'automaticPublication'=>false,'automaticReproducibilityCertification'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'reproducibility-scholarly-package-bridge-ready','version'=>self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'productRef'=>self::PRODUCT_REF,'corePackageBindingPath'=>self::CORE_PACKAGE_BINDING_PATH,'coreScholarlyContract'=>self::CORE_SCHOLARLY_CONTRACT,'labIsUnderlyingPackageAuthority'=>true,'coreRecordsPackageRefsAndInteroperabilityMetadata'=>true,'automaticCoreSubmission'=>false,'coreMintsIdentifiers'=>false,'corePublishesPackages'=>false,'coreResolvesCitations'=>false,'coreExecutesNotebooks'=>false,'coreTransformsDatasets'=>false,'coreCertifiesReproducibility'=>false,'coreValidatesScientificContent'=>false,'scientificInvestigationRuntimeIntegrationDeferredTo'=>'0.111.0')); }
    public static function health(){
        $required=array('contracts/platform-core-v3-scholarly-package-v01100.schema.json','contracts/platform-core-v3-scholarly-package-policy-v01100.json','includes/class-sc-lab-platform-core-v3-scholarly-package-v01100.php');
        $files=array();$ok=true; foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'platform-core-v3-reproducibility-scholarly-package-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'productRef'=>self::PRODUCT_REF,'corePackageBindingPath'=>self::CORE_PACKAGE_BINDING_PATH,'coreScholarlyContract'=>self::CORE_SCHOLARLY_CONTRACT,'labIsUnderlyingPackageAuthority'=>true,'automaticCoreSubmission'=>false,'automaticPublication'=>false,'automaticReproducibilityCertification'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Platform_Core_V3_Scholarly_Package_V01100::init();
