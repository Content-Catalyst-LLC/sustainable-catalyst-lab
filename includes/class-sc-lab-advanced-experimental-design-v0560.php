<?php
/** Sustainable Catalyst Lab v0.56.0 — Advanced Experimental Design & Sequential Experimentation. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Advanced_Experimental_Design_V0560 {
    const VERSION='0.56.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); add_filter('sc_lab_module_aliases_v02631',array(__CLASS__,'aliases')); }
    public static function aliases($aliases){$aliases=is_array($aliases)?$aliases:array();foreach(array('advanced-design','optimal-design','sequential-experimentation','adaptive-design') as $a){$aliases[$a]='design-studies';}return $aliases;}
    public static function routes(){
        register_rest_route('sc-lab/v1','/advanced-experimental-design/v0560/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/advanced-experimental-design/v0560/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'designSchema'=>'sc-lab-advanced-experimental-design/0.56.0','sequentialSchema'=>'sc-lab-sequential-experiment-plan/0.56.0','diagnosticSchema'=>'sc-lab-design-optimality-diagnostics/0.56.0'));}
    public static function health(){
        $required=array('backend/app/advanced_experimental_design.py','backend/tests/test_advanced_experimental_design_v0560.py','assets/js/modules/advanced-experimental-design-v0560.js','assets/css/sc-lab-advanced-experimental-design-v0560.css','contracts/advanced-experimental-design-v0560.schema.json','contracts/sequential-experiment-plan-v0560.schema.json','contracts/design-optimality-diagnostics-v0560.schema.json','contracts/advanced-experimental-design-policy-v0560.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'advanced-experimental-design-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'dOptimalDesign'=>true,'maximinDesign'=>true,'sequentialInformationGain'=>true,'responseGuidedProposal'=>true,'automaticExperimentExecution'=>false,'automaticStopping'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
