<?php
/** Lab v0.93.0 — Carbon & Nature Intelligence v0.10.0 SOC Management Scenario Studio. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_SOC_Scenarios_V0930 {
    const LAB_VERSION='0.93.0';
    const DOMAIN_VERSION='0.10.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;

    public static function init(){
        if(self::$initialized){return;}
        self::$initialized=true;
        add_action('rest_api_init',array(__CLASS__,'routes'));
    }

    public static function routes(){
        register_rest_route('sc-lab/v1','/carbon-nature/soc/v1000/scenarios/module',array(
            'methods'=>WP_REST_Server::READABLE,
            'callback'=>array(__CLASS__,'manifest'),
            'permission_callback'=>'__return_true'
        ));
    }

    private static function file_state($rel){
        $p=SC_LAB_DIR.ltrim((string)$rel,'/');
        return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);
    }

    public static function manifest(){
        $required=array(
            'backend/app/soil_carbon_scenarios_v0930.py',
            'backend/tests/test_soil_carbon_scenarios_v0930.py',
            'assets/js/modules/soil-carbon-scenarios-v0930.js',
            'assets/css/sc-lab-soil-carbon-scenarios-v0930.css',
            'contracts/soc-management-scenario-v1000.schema.json',
            'contracts/soc-management-scenario-comparison-v1000.schema.json',
            'contracts/soc-management-sensitivity-v1000.schema.json',
            'contracts/soc-management-scenario-policy-v1000.json'
        );
        $files=array();$ok=true;
        foreach($required as $rel){
            $files[$rel]=self::file_state($rel);
            if(empty($files[$rel]['exists'])){$ok=false;}
        }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'soc-management-scenario-studio-ready':'incomplete',
            'domain'=>'Carbon & Nature Intelligence',
            'domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,
            'computeCoreVersion'=>self::ENGINE_VERSION,
            'release'=>'SOC Management Scenario Studio',
            'capabilities'=>array(
                'constantAnnualChange'=>true,
                'compoundRelativeChange'=>true,
                'annualChangeSchedules'=>true,
                'multiScenarioComparison'=>true,
                'userSuppliedAssumptionEnvelope'=>true,
                'userSuppliedSensitivitySweep'=>true,
                'parcelScaleProjection'=>true,
                'graphStudioHandoff'=>true,
                'carbonProjectPacketHandoff'=>true
            ),
            'guardrails'=>array(
                'noDefaultSocChangeRate'=>true,
                'measureRefsDoNotInjectRates'=>true,
                'scenarioProjectionIsNotForecast'=>true,
                'projectedIncreaseIsNotVerifiedSequestration'=>true,
                'soilCapacityOrSaturationNotInferred'=>true,
                'wholeFarmGhgBalance'=>false,
                'causalAttribution'=>false,
                'verification'=>false,
                'creditEligibility'=>false
            ),
            'files'=>$files
        ));
    }
}
