<?php
/** Sustainable Catalyst Lab v0.57.0 — Scientific Workflow Composer. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Workflow_Composer_V0570 {
    const VERSION='0.57.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); add_filter('sc_lab_module_aliases_v02631',array(__CLASS__,'aliases')); add_filter('sc_lab_panel_aliases_v02631',array(__CLASS__,'aliases')); }
    public static function aliases($aliases){$aliases=is_array($aliases)?$aliases:array();foreach(array('workflow-composer','scientific-workflow-composer','research-pipeline','scientific-pipeline') as $a){$aliases[$a]='workflow-orchestration';}return $aliases;}
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-workflows/v0570/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-workflows/v0570/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'workflowSchema'=>'sc-lab-scientific-workflow-composer/0.57.0','runSchema'=>'sc-lab-scientific-workflow-run/0.57.0','stageResultSchema'=>'sc-lab-scientific-workflow-stage-result/0.57.0','maximumStages'=>24));}
    public static function health(){
        $required=array('backend/app/scientific_workflow_composer.py','backend/tests/test_scientific_workflow_composer_v0570.py','assets/js/modules/scientific-workflow-composer-v0570.js','assets/css/sc-lab-scientific-workflow-composer-v0570.css','contracts/scientific-workflow-composer-v0570.schema.json','contracts/scientific-workflow-run-v0570.schema.json','contracts/scientific-workflow-stage-result-v0570.schema.json','contracts/scientific-workflow-composer-policy-v0570.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-workflow-composer-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'savedWorkflows'=>true,'rerunnableWorkflows'=>true,'deterministicRunHash'=>true,'explicitBindings'=>true,'legacyOperationalOrchestrator'=>'0.32.1','automaticExperimentExecution'=>false,'automaticRegistryPromotion'=>false,'automaticPublication'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
