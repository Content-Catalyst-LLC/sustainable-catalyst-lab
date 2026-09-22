<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Platform_Core_V3_Integration_Certification_V01120 {
    const VERSION='0.112.0';
    const MINIMUM_CORE_RELEASE='3.0.0';
    const PRODUCT_REF='product:sustainable-catalyst-lab';
    const BRIDGE_SCHEMA='sc-lab-platform-core-v3-integration-certification/0.112.0';
    const CORE_CONTRACT='sc.research.platform-integration-certification.v1';
    const CORE_CERTIFICATION_PATH='/v1/research/integration-certification';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/platform-core-v3/v01120/integration-certification';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=plugin_dir_path(dirname(__FILE__)).$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'bridgeSchema'=>self::BRIDGE_SCHEMA,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
        'coreContract'=>self::CORE_CONTRACT,'coreCertificationPath'=>self::CORE_CERTIFICATION_PATH,
        'certificationScope'=>'platform_runtime_contract_conformance_only','certifiedLayerCount'=>8,'conformanceCaseCount'=>18,
        'automaticCoreSubmission'=>false,'automaticProductInvocation'=>false,'automaticCaseExecution'=>false,
        'automaticScientificCertification'=>false,'automaticProductQualityCertification'=>false,'automaticTruthDetermination'=>false
    )); }
    public static function manifest(){ return rest_ensure_response(array(
        'ok'=>true,'status'=>'platform-core-integration-certification-ready','version'=>self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
        'productRef'=>self::PRODUCT_REF,'coreContract'=>self::CORE_CONTRACT,'coreCertificationPath'=>self::CORE_CERTIFICATION_PATH,
        'certifiedLayerCount'=>8,'conformanceCaseCount'=>18,'certificationScope'=>'platform_runtime_contract_conformance_only',
        'coversVersions'=>array('0.104.0','0.105.0','0.106.0','0.107.0','0.108.0','0.109.0','0.110.0','0.111.0'),
        'coreRecordsCertificationEvidence'=>true,'labConstructsConformancePlans'=>true,
        'automaticCoreSubmission'=>false,'coreInvokesLabProduct'=>false,'coreExecutesConformanceCases'=>false,
        'coreCertifiesScientificValidity'=>false,'coreCertifiesProductQuality'=>false,'coreRanksProducts'=>false,
        'coreInfersReproducibility'=>false,'coreResolvesFailures'=>false,'coreDeterminesTruth'=>false
    )); }
    public static function health(){
        $required=array('contracts/platform-core-v3-integration-certification-v01120.schema.json','contracts/platform-core-v3-integration-certification-policy-v01120.json','includes/class-sc-lab-platform-core-v3-integration-certification-v01120.php');
        $files=array();$ok=true; foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'platform-core-integration-certification-ready':'incomplete','version'=>self::VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,
            'productRef'=>self::PRODUCT_REF,'coreContract'=>self::CORE_CONTRACT,'certifiedLayerCount'=>8,'conformanceCaseCount'=>18,
            'automaticCoreSubmission'=>false,'automaticProductInvocation'=>false,'automaticCaseExecution'=>false,'automaticScientificCertification'=>false,'automaticTruthDetermination'=>false,
            'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Platform_Core_V3_Integration_Certification_V01120::init();
