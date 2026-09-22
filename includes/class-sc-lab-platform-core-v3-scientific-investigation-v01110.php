<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Platform_Core_V3_Scientific_Investigation_V01110 {
    const VERSION='0.111.0';
    const MINIMUM_CORE_RELEASE='3.0.0';
    const PRODUCT_REF='product:sustainable-catalyst-lab';
    const BRIDGE_SCHEMA='sc-lab-platform-core-v3-scientific-investigation-runtime/0.111.0';
    const CORE_CONTRACT='sc.research.unified-research-scientific-investigation-runtime.v1';
    const CORE_INVESTIGATION_BINDING_PATH='/v1/research/unified-runtime/investigation-bindings';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/platform-core-v3/v01110/scientific-investigations';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=plugin_dir_path(dirname(__FILE__)).$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'bridgeSchema'=>self::BRIDGE_SCHEMA,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'coreContract'=>self::CORE_CONTRACT,'coreInvestigationBindingPath'=>self::CORE_INVESTIGATION_BINDING_PATH,'automaticCoreSubmission'=>false,'automaticExecution'=>false,'automaticScientificCertification'=>false,'automaticTruthDetermination'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'scientific-investigation-runtime-integration-ready','version'=>self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'productRef'=>self::PRODUCT_REF,'coreInvestigationBindingPath'=>self::CORE_INVESTIGATION_BINDING_PATH,'labIsUnderlyingScientificInvestigationAuthority'=>true,'coreRecordsReferenceFirstInvestigationContext'=>true,'automaticCoreSubmission'=>false,'coreRunsScientificInvestigation'=>false,'coreInfersFindings'=>false,'coreRanksEvidence'=>false,'coreResolvesContradictions'=>false,'coreSelectsHypotheses'=>false,'coreInfersCausality'=>false,'coreCertifiesScientificValidity'=>false,'coreDeterminesTruth'=>false,'integrationCertificationDeferredTo'=>'0.112.0')); }
    public static function health(){
        $required=array('contracts/platform-core-v3-scientific-investigation-v01110.schema.json','contracts/platform-core-v3-scientific-investigation-policy-v01110.json','includes/class-sc-lab-platform-core-v3-scientific-investigation-v01110.php');
        $files=array();$ok=true; foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-investigation-runtime-integration-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'minimumCoreRelease'=>self::MINIMUM_CORE_RELEASE,'productRef'=>self::PRODUCT_REF,'coreInvestigationBindingPath'=>self::CORE_INVESTIGATION_BINDING_PATH,'automaticCoreSubmission'=>false,'automaticExecution'=>false,'automaticScientificCertification'=>false,'automaticTruthDetermination'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Platform_Core_V3_Scientific_Investigation_V01110::init();
