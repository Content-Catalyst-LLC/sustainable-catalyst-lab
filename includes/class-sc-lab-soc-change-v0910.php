<?php
/** Lab v0.91.0 — Carbon & Nature Intelligence v0.8.0 SOC Change & Sequestration Model. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_SOC_Change_V0910 {
    const LAB_VERSION = '0.91.0';
    const DOMAIN_VERSION = '0.8.0';
    const ENGINE_VERSION = '1.0.0';
    private static $initialized = false;
    public static function init() { if (self::$initialized) { return; } self::$initialized=true; add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes() { register_rest_route('sc-lab/v1','/carbon-nature/soc/v0800/change/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true')); }
    private static function file_state($relative) { $p=SC_LAB_DIR.ltrim((string)$relative,'/'); return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function manifest() {
        $required=array(
            'backend/app/soil_carbon_change_v0910.py','backend/tests/test_soil_carbon_change_v0910.py',
            'assets/js/modules/soil-carbon-change-v0910.js','assets/css/sc-lab-soil-carbon-change-v0910.css',
            'contracts/soc-stock-change-v0800.schema.json','contracts/soc-change-series-v0800.schema.json','contracts/soc-change-policy-v0800.json'
        );
        $files=array(); $ok=true; foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'soc-stock-change-model-ready':'incomplete','domain'=>'Carbon & Nature Intelligence',
            'domainVersion'=>self::DOMAIN_VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,
            'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'SOC Change & Sequestration Model',
            'capabilities'=>array('matchedFixedDepthComparison'=>true,'annualizedStockChange'=>true,'relativeStockChange'=>true,'multiDateChangeSeries'=>true,'parcelAreaScaling'=>true,'carbonProjectPacketHandoff'=>true,'deterministicFingerprints'=>true,'attributedSequestrationClaim'=>false),
            'guardrails'=>array('exactDepthIntervalMatchingRequired'=>true,'equivalentSoilMassNotImplemented'=>true,'positiveStockChangeNotTreatedAsAttributedSequestration'=>true,'counterfactualNotEstablished'=>true,'uncertaintyNotInferred'=>true,'co2eNotInferred'=>true,'additionalityNotDetermined'=>true,'permanenceNotDetermined'=>true,'creditEligibilityNotDetermined'=>true,'verificationNotPerformed'=>true),
            'files'=>$files,
        ));
    }
}
