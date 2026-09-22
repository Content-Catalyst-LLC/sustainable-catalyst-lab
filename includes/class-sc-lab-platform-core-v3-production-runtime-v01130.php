<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Platform_Core_V3_Production_Runtime_V01130 {
    const VERSION='0.113.0';
    const MINIMUM_CORE_RELEASE='3.0.0';
    const PRODUCT_REF='product:sustainable-catalyst-lab';
    const BRIDGE_SCHEMA='sc-lab-unified-research-session-production-runtime/0.113.0';
    const CORE_RUNTIME_CONTRACT='sc.research.unified-research-scientific-investigation-runtime.v1';
    const CORE_CERTIFICATION_CONTRACT='sc.research.platform-integration-certification.v1';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/platform-core-v3/v01130/production-runtime';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=plugin_dir_path(dirname(__FILE__)).$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'bridgeSchema'=>self::BRIDGE_SCHEMA,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
        'coreRuntimeContract'=>self::CORE_RUNTIME_CONTRACT,'coreCertificationContract'=>self::CORE_CERTIFICATION_CONTRACT,
        'integrationComponentCount'=>9,'operationTypeCount'=>14,'explicitSubmissionPlansOnly'=>true,
        'automaticCoreSubmission'=>false,'automaticRetry'=>false,'automaticRecovery'=>false,'automaticScientificExecution'=>false,
        'automaticScientificCertification'=>false,'automaticProductQualityCertification'=>false,'automaticTruthDetermination'=>false,
        'statusCodeSuccessInference'=>false
    )); }
    public static function manifest(){ return rest_ensure_response(array(
        'ok'=>true,'status'=>'unified-research-session-production-runtime-ready','version'=>self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
        'productRef'=>self::PRODUCT_REF,'coreRuntimeContract'=>self::CORE_RUNTIME_CONTRACT,'coreCertificationContract'=>self::CORE_CERTIFICATION_CONTRACT,
        'integrationComponentCount'=>9,'operationTypeCount'=>14,
        'coversVersions'=>array('0.104.0','0.105.0','0.106.0','0.107.0','0.108.0','0.109.0','0.110.0','0.111.0','0.112.0'),
        'deterministicRequestHashes'=>true,'deterministicDefaultIdempotencyKeys'=>true,'explicitReceipts'=>true,'declaredOutcomesOnly'=>true,
        'contextContinuityChecks'=>true,'componentReadinessChecks'=>true,'explicitRetryPlans'=>true,'explicitRecoveryPlans'=>true,'checkpointEnvelopes'=>true,
        'coreRemainsSessionReferenceAuthority'=>true,'labRemainsScientificExecutionAuthority'=>true,
        'automaticCoreSubmission'=>false,'automaticRetry'=>false,'automaticRecovery'=>false,'automaticCoreMutation'=>false,'automaticScientificExecution'=>false,
        'automaticScientificCertification'=>false,'automaticProductQualityCertification'=>false,'automaticTruthDetermination'=>false,'statusCodeSuccessInference'=>false
    )); }
    public static function health(){
        $required=array('contracts/platform-core-v3-production-runtime-v01130.schema.json','contracts/platform-core-v3-production-runtime-policy-v01130.json','includes/class-sc-lab-platform-core-v3-production-runtime-v01130.php');
        $files=array();$ok=true; foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'unified-research-session-production-runtime-ready':'incomplete','version'=>self::VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,'coreRuntimeContract'=>self::CORE_RUNTIME_CONTRACT,'integrationComponentCount'=>9,'operationTypeCount'=>14,
            'automaticCoreSubmission'=>false,'automaticRetry'=>false,'automaticRecovery'=>false,'automaticScientificExecution'=>false,
            'automaticScientificCertification'=>false,'automaticTruthDetermination'=>false,'statusCodeSuccessInference'=>false,
            'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Platform_Core_V3_Production_Runtime_V01130::init();
