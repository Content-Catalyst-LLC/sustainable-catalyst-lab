<?php
/** Lab v0.94.0 — Carbon & Nature Intelligence v0.11.0 Whole-Farm GHG Balance. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Whole_Farm_GHG_V0940 {
    const LAB_VERSION='0.94.0';
    const DOMAIN_VERSION='0.11.0';
    const ENGINE_VERSION='1.0.0';
    private static $initialized=false;

    public static function init(){
        if(self::$initialized){return;}
        self::$initialized=true;
        add_action('rest_api_init',array(__CLASS__,'routes'));
    }

    public static function routes(){
        register_rest_route('sc-lab/v1','/carbon-nature/ghg/v1100/balance/module',array(
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
            'backend/app/whole_farm_ghg_v0940.py',
            'backend/tests/test_whole_farm_ghg_v0940.py',
            'assets/js/modules/whole-farm-ghg-v0940.js',
            'assets/css/sc-lab-whole-farm-ghg-v0940.css',
            'contracts/whole-farm-ghg-entry-v1100.schema.json',
            'contracts/whole-farm-ghg-balance-v1100.schema.json',
            'contracts/whole-farm-ghg-policy-v1100.json'
        );
        $files=array();$ok=true;
        foreach($required as $rel){
            $files[$rel]=self::file_state($rel);
            if(empty($files[$rel]['exists'])){$ok=false;}
        }
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'whole-farm-ghg-balance-ready':'incomplete',
            'domain'=>'Carbon & Nature Intelligence',
            'domainVersion'=>self::DOMAIN_VERSION,
            'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,
            'computeCoreVersion'=>self::ENGINE_VERSION,
            'release'=>'Whole-Farm GHG Balance',
            'capabilities'=>array(
                'directCo2eRecords'=>true,
                'gasMassWithExplicitGwp'=>true,
                'activityFactorAccounting'=>true,
                'emissionsAndRemovals'=>true,
                'categoryAggregation'=>true,
                'gasAggregation'=>true,
                'socStockChangeIntegration'=>true,
                'periodAnnualization'=>true,
                'farmAreaIntensity'=>true,
                'carbonProjectPacketHandoff'=>true
            ),
            'guardrails'=>array(
                'noDefaultNonCo2GwpFactors'=>true,
                'noDefaultActivityEmissionFactors'=>true,
                'activityFactorSourceRequired'=>true,
                'socInclusionExplicit'=>true,
                'wholeFarmBalanceIsNotVerification'=>true,
                'inventoryCompletenessNotInferred'=>true,
                'causalAttribution'=>false,
                'additionality'=>false,
                'leakage'=>false,
                'permanence'=>false,
                'creditEligibility'=>false,
                'automaticRecommendation'=>false
            ),
            'files'=>$files
        ));
    }
}
