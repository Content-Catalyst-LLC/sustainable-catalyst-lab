<?php
/** Lab v0.96.0 — Carbon & Nature Intelligence v0.13.0 MRV Protocol Builder. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Carbon_MRV_Protocol_V0960 {
    const LAB_VERSION='0.96.0';
    const DOMAIN_VERSION='0.13.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){register_rest_route('sc-lab/v1','/carbon-nature/mrv/v1300/protocol/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));}
    private static function file_state($rel){$p=SC_LAB_DIR.ltrim((string)$rel,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function manifest(){
        $required=array(
            'assets/js/modules/carbon-mrv-protocol-v0960.js','assets/css/sc-lab-carbon-mrv-protocol-v0960.css',
            'contracts/carbon-mrv-protocol-v1300.schema.json','contracts/carbon-mrv-protocol-validation-v1300.schema.json','contracts/carbon-mrv-protocol-policy-v1300.json'
        );
        $files=array();$ok=true;foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'mrv-protocol-builder-ready':'incomplete','domain'=>'Carbon & Nature Intelligence','domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'MRV Protocol Builder',
            'capabilities'=>array('methodDerivedTemplates'=>true,'draftProtocolBuilder'=>true,'structuralValidation'=>true,'methodDocumentationGapAnalysis'=>true,'responsibilityAssignment'=>true,'monitoringPeriodAndFrequency'=>true,'libraryMethodologyCrosswalk'=>true,'carbonProjectMonitoringRecordHandoff'=>true),
            'guardrails'=>array('protocolIsNotExternalMethodology'=>true,'automaticMethodSelection'=>false,'methodologyEligibilityDetermination'=>false,'verificationDetermination'=>false,'creditEligibilityDetermination'=>false,'currentProgramRuleAssertion'=>false,'hiddenMeasurementDefaults'=>false),
            'files'=>$files
        ));
    }
}
