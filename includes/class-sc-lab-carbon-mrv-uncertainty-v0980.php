<?php
/** Lab v0.98.0 — Carbon & Nature Intelligence v0.15.0 MRV Uncertainty & Detection Engine. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Carbon_MRV_Uncertainty_V0980 {
    const LAB_VERSION='0.98.0';
    const DOMAIN_VERSION='0.15.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){register_rest_route('sc-lab/v1','/carbon-nature/mrv/v1500/uncertainty/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));}
    private static function file_state($rel){$p=SC_LAB_DIR.ltrim((string)$rel,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function manifest(){
        $required=array(
            'assets/js/modules/carbon-mrv-uncertainty-v0980.js','assets/css/sc-lab-carbon-mrv-uncertainty-v0980.css',
            'contracts/carbon-mrv-uncertainty-budget-v1500.schema.json','contracts/carbon-mrv-change-detection-v1500.schema.json',
            'contracts/carbon-mrv-detection-sample-size-v1500.schema.json','contracts/carbon-mrv-uncertainty-assessment-v1500.schema.json',
            'contracts/carbon-mrv-uncertainty-assessment-validation-v1500.schema.json','contracts/carbon-mrv-uncertainty-policy-v1500.json'
        );
        $files=array();$ok=true;foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'mrv-uncertainty-detection-engine-ready':'incomplete','domain'=>'Carbon & Nature Intelligence','domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'MRV Uncertainty & Detection Engine',
            'capabilities'=>array('explicitUncertaintyBudget'=>true,'expandedUncertainty'=>true,'pairedDetection'=>true,'independentDetection'=>true,'detectionSampleSizePlanning'=>true,'monitoringPlanLinkage'=>true,'carbonProjectModelRunHandoff'=>true),
            'guardrails'=>array('hiddenConfidenceDefaults'=>false,'automaticCorrelationAssumption'=>false,'detectionEqualsVerification'=>false,'automaticDeductionFactor'=>false,'methodologyEligibilityDetermination'=>false,'verificationDetermination'=>false,'creditEligibilityDetermination'=>false),
            'files'=>$files
        ));
    }
}
