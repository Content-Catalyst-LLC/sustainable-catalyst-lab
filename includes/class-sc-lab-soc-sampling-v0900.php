<?php
/** Lab v0.90.0 — Carbon & Nature Intelligence v0.7.0 SOC Sampling & Field Measurement Studio. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_SOC_Sampling_V0900 {
    const LAB_VERSION = '0.90.0';
    const DOMAIN_VERSION = '0.7.0';
    const ENGINE_VERSION = '1.0.0';
    private static $initialized = false;
    public static function init() { if (self::$initialized) { return; } self::$initialized=true; add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes() { register_rest_route('sc-lab/v1','/carbon-nature/soc/v0700/sampling/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true')); }
    private static function file_state($relative) { $p=SC_LAB_DIR.ltrim((string)$relative,'/'); return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function manifest() {
        $required=array(
            'backend/app/soil_carbon_sampling_v0900.py','backend/tests/test_soil_carbon_sampling_v0900.py',
            'assets/js/modules/soil-carbon-sampling-v0900.js','assets/css/sc-lab-soil-carbon-sampling-v0900.css',
            'contracts/soc-field-sample-v0700.schema.json','contracts/soc-sampling-design-v0700.schema.json',
            'contracts/soc-field-packet-v0700.schema.json','contracts/soc-profile-handoff-v0700.schema.json','contracts/soc-sampling-policy-v0700.json'
        );
        $files=array(); $ok=true; foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'soc-sampling-field-measurement-ready':'incomplete','domain'=>'Carbon & Nature Intelligence',
            'domainVersion'=>self::DOMAIN_VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,
            'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'SOC Sampling & Field Measurement Studio',
            'capabilities'=>array('sampleRegistry'=>true,'samplingPlanRegistry'=>true,'bulkDensityCoreCalculation'=>true,'wgs84FieldCoordinates'=>true,'chainOfCustodyMetadata'=>true,'socV0600ProfileHandoff'=>true,'carbonProjectPacketHandoff'=>true,'deterministicFingerprints'=>true),
            'guardrails'=>array('fieldMeasurementsNotTreatedAsVerified'=>true,'sampleSizeAdequacyNotDetermined'=>true,'spatialRandomizationNotInferred'=>true,'coordinatesNotGenerated'=>true,'replicateAggregationNotInferred'=>true,'stockChangeNotInferred'=>true,'sequestrationRateNotInferred'=>true,'uncertaintyNotInferred'=>true,'creditEligibilityNotDetermined'=>true,'chainOfCustodyNotDigitallySigned'=>true),
            'files'=>$files,
        ));
    }
}
