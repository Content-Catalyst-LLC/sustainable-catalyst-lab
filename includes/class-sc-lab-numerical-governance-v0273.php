<?php
/** Sustainable Catalyst Lab v0.27.3 numerical precision and solver governance. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Numerical_Governance_V0273 {
    const VERSION='0.27.3'; const CATALOG='contracts/solver-governance-v0273.json'; private static $initialized=false;
    public static function init(){ if(self::$initialized){return;} self::$initialized=true; add_action('rest_api_init',array(__CLASS__,'routes')); add_filter('sc_lab_module_aliases_v02631',array(__CLASS__,'aliases')); }
    public static function aliases($aliases){$aliases=is_array($aliases)?$aliases:array(); foreach(array('solver-governance','precision-governance','numerical-governance','solver-policy') as $alias){$aliases[$alias]='numerical-governance';} return $aliases;}
    private static function catalog_data(){ $path=SC_LAB_DIR.self::CATALOG; if(!is_file($path)){return array('schema'=>'sc-lab-solver-governance-catalog/1.0','version'=>self::VERSION,'profiles'=>array());} $data=json_decode((string)file_get_contents($path),true); return is_array($data)?$data:array(); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/numerical/v0273/policies',array('methods'=>'GET','callback'=>array(__CLASS__,'policies'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/numerical/v0273/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
    }
    public static function policies(){ $data=self::catalog_data(); $data['ok']=!empty($data['profiles']); $data['release']=defined('SC_LAB_VERSION')?SC_LAB_VERSION:self::VERSION; return rest_ensure_response($data); }
    public static function health(){
        $required=array('assets/js/modules/numerical-governance-studio.js','assets/css/sc-lab-numerical-governance-v0273.css',self::CATALOG,'contracts/solver-governance-result-v0273.schema.json','includes/class-sc-lab-numerical-governance-v0273.php');
        $files=array(); foreach($required as $relative){$path=SC_LAB_DIR.$relative;$files[$relative]=array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);} $ok=!in_array(false,array_map(function($row){return !empty($row['exists']);},$files),true);
        return rest_ensure_response(array('ok'=>$ok,'version'=>self::VERSION,'release'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'architecture'=>'governed-solver-selection-and-precision','profiles'=>4,'floatingPoint'=>'IEEE-754 binary64','unitAwareValidation'=>true,'referenceMethodComparisons'=>true,'conditionDiagnostics'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
