<?php
/** Lab v0.92.0 — Carbon & Nature Intelligence v0.9.0 SOC Spatial Variability & Uncertainty. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_SOC_Uncertainty_V0920 {
    const LAB_VERSION='0.92.0'; const DOMAIN_VERSION='0.9.0'; const ENGINE_VERSION='1.0.0'; private static $initialized=false;
    public static function init(){ if(self::$initialized){return;} self::$initialized=true; add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ register_rest_route('sc-lab/v1','/carbon-nature/soc/v0900/uncertainty/module',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true')); }
    private static function file_state($rel){$p=SC_LAB_DIR.ltrim((string)$rel,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function manifest(){
      $required=array('backend/app/soil_carbon_uncertainty_v0920.py','backend/tests/test_soil_carbon_uncertainty_v0920.py','assets/js/modules/soil-carbon-uncertainty-v0920.js','assets/css/sc-lab-soil-carbon-uncertainty-v0920.css','contracts/soc-spatial-uncertainty-v0900.schema.json','contracts/soc-stratified-estimate-v0900.schema.json','contracts/soc-change-uncertainty-v0900.schema.json','contracts/soc-input-uncertainty-v0900.schema.json','contracts/soc-uncertainty-policy-v0900.json');
      $files=array();$ok=true;foreach($required as $rel){$files[$rel]=self::file_state($rel);if(empty($files[$rel]['exists'])){$ok=false;}}
      return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'soc-spatial-variability-uncertainty-ready':'incomplete','domain'=>'Carbon & Nature Intelligence','domainVersion'=>self::DOMAIN_VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::LAB_VERSION,'computeCoreVersion'=>self::ENGINE_VERSION,'release'=>'SOC Spatial Variability & Uncertainty','capabilities'=>array('replicateStockSummary'=>true,'studentTIntervals'=>true,'coordinateCoverageDiagnostics'=>true,'stratifiedAreaWeightedEstimate'=>true,'pairedChangeUncertainty'=>true,'independentChangeUncertainty'=>true,'firstOrderInputUncertaintyPropagation'=>true,'carbonProjectPacketHandoff'=>true),'guardrails'=>array('sampleUncertaintyIsNotTotalUncertainty'=>true,'spatialRepresentativenessNotDetermined'=>true,'automaticOutlierRemoval'=>false,'kriging'=>false,'variogramInference'=>false,'causalAttribution'=>false,'verification'=>false,'creditEligibility'=>false),'files'=>$files));
    }
}
