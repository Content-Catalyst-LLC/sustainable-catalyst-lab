<?php
/** Sustainable Catalyst Lab v0.55.0 — Scientific Data Transformation & Derived Variables. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Data_Transformations_V0550 {
    const VERSION='0.55.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/data-transformations/v0550/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/data-transformations/v0550/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'planSchema'=>'sc-lab-scientific-data-transformation-plan/0.55.0',
        'resultSchema'=>'sc-lab-scientific-data-transformation-result/0.55.0',
        'joinSchema'=>'sc-lab-scientific-data-join/0.55.0',
    )); }
    public static function health(){
        $required=array(
            'backend/app/data_transformations.py','backend/tests/test_data_transformations_v0550.py',
            'assets/js/modules/data-transformations-v0550.js','assets/css/sc-lab-data-transformations-v0550.css',
            'contracts/scientific-data-transformation-plan-v0550.schema.json','contracts/scientific-data-transformation-result-v0550.schema.json',
            'contracts/scientific-data-join-v0550.schema.json','contracts/scientific-data-transformation-policy-v0550.json','templates/lab-app.php'
        );
        $files=array();$ok=true;
        foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'scientific-data-transformation-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'safeDerivedVariables'=>true,'unitAwareTransformations'=>true,'governedJoins'=>true,'reproducibleLineage'=>true,
            'automaticImputation'=>false,'automaticUnitInference'=>false,'arbitraryCode'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
