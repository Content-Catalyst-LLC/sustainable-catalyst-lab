<?php
/** Sustainable Catalyst Lab v0.54.0 — Dynamic Systems II. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Dynamic_Systems_V0540 {
    const VERSION='0.54.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/dynamic-systems/v0540/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/dynamic-systems/v0540/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){ return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'studySchema'=>'sc-lab-dynamic-systems-advanced-study/0.54.0',
        'simulationSchema'=>'sc-lab-dynamic-systems-advanced-simulation/0.54.0',
        'bifurcationSchema'=>'sc-lab-dynamic-systems-bifurcation/0.54.0',
        'phaseSchema'=>'sc-lab-dynamic-systems-phase-analysis/0.54.0',
    )); }
    public static function health(){
        $required=array(
            'backend/app/dynamic_systems_v0540.py','backend/tests/test_dynamic_systems_v0540.py',
            'assets/js/modules/dynamic-systems-v0540.js','assets/css/sc-lab-dynamic-systems-v0540.css',
            'contracts/dynamic-systems-advanced-study-v0540.schema.json','contracts/dynamic-systems-advanced-simulation-v0540.schema.json',
            'contracts/dynamic-systems-bifurcation-v0540.schema.json','contracts/dynamic-systems-phase-analysis-v0540.schema.json',
            'contracts/dynamic-systems-policy-v0540.json','templates/lab-app.php'
        );
        $files=array();$ok=true;
        foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'dynamic-systems-ii-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'events'=>true,'regimeChanges'=>true,'bifurcationScans'=>true,'advancedPhaseAnalysis'=>true,
            'formalBifurcationProof'=>false,'automaticRegimeInference'=>false,'arbitraryCode'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
