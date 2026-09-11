<?php
/** Lab v0.97.0 — Carbon & Nature Intelligence v0.14.0 Monitoring Plan & Sampling Designer. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Carbon_MRV_Monitoring_V0970 {
    const LAB_VERSION='0.97.0';
    const DOMAIN_VERSION='0.14.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){register_rest_route('sc-lab/v1','/carbon-nature/mrv/v1400/monitoring/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));}
    private static function file_state($rel){$p=SC_LAB_DIR.ltrim((string)$rel,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function manifest(){
        $required=array(
            'assets/js/modules/carbon-mrv-monitoring-v0970.js','assets/css/sc-lab-carbon-mrv-monitoring-v0970.css',
            'contracts/carbon-mrv-monitoring-plan-v1400.schema.json','contracts/carbon-mrv-monitoring-plan-validation-v1400.schema.json',
            'contracts/carbon-mrv-sample-size-v1400.schema.json','contracts/carbon-mrv-stratified-allocation-v1400.schema.json','contracts/carbon-mrv-monitoring-plan-policy-v1400.json'
        );
        $files=array();$ok=true;foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'monitoring-plan-sampling-designer-ready':'incomplete','domain'=>'Carbon & Nature Intelligence','domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'Monitoring Plan & Sampling Designer',
            'capabilities'=>array('monitoringPlanBuilder'=>true,'campaignScheduleDesign'=>true,'samplingStrategyDocumentation'=>true,'precisionSampleSizePlanning'=>true,'finitePopulationCorrection'=>true,'stratifiedAllocation'=>true,'socDepthGovernance'=>true,'methodDocumentationGapAnalysis'=>true,'carbonProjectMonitoringRecordHandoff'=>true),
            'guardrails'=>array('samplingRepresentativenessInferred'=>false,'hiddenPrecisionDefaults'=>false,'automaticCoordinateGeneration'=>false,'methodologyEligibilityDetermination'=>false,'verificationDetermination'=>false,'creditEligibilityDetermination'=>false),
            'files'=>$files
        ));
    }
}
