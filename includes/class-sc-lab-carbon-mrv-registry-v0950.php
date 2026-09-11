<?php
/** Lab v0.95.0 — Carbon & Nature Intelligence v0.12.0 Carbon MRV Method Registry. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Carbon_MRV_Registry_V0950 {
    const LAB_VERSION='0.95.0';
    const DOMAIN_VERSION='0.12.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){register_rest_route('sc-lab/v1','/carbon-nature/mrv/v1200/registry/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));}
    private static function file_state($rel){$p=SC_LAB_DIR.ltrim((string)$rel,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function manifest(){
        $required=array(
            'assets/js/modules/carbon-mrv-registry-v0950.js','assets/css/sc-lab-carbon-mrv-registry-v0950.css',
            'contracts/carbon-mrv-method-v1200.schema.json','contracts/carbon-mrv-readiness-v1200.schema.json','contracts/carbon-mrv-registry-policy-v1200.json'
        );
        $files=array();$ok=true;foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'carbon-mrv-method-registry-ready':'incomplete','domain'=>'Carbon & Nature Intelligence','domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'Carbon MRV Method Registry',
            'capabilities'=>array('governedMethodRegistry'=>true,'methodDetail'=>true,'methodFiltering'=>true,'methodComparison'=>true,'documentationReadiness'=>true,'libraryMethodologyCrosswalk'=>true,'carbonProjectMonitoringRecordHandoff'=>true),
            'guardrails'=>array('registryIsNotExternalProtocol'=>true,'automaticMethodSelection'=>false,'methodologyEligibilityDetermination'=>false,'verificationDetermination'=>false,'creditEligibilityDetermination'=>false,'currentProgramRuleAssertion'=>false,'automaticRecommendation'=>false),
            'files'=>$files
        ));
    }
}
