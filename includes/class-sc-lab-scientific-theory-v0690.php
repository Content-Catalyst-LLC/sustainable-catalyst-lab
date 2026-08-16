<?php
/** Sustainable Catalyst Lab v0.69.0 — Scientific Theory & Conceptual Model Workspace. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Theory_V0690 {
    const VERSION='0.69.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-theory/v0690/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-theory/v0690/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'theorySchema'=>'sc-lab-scientific-theory/0.69.0','constructSchema'=>'sc-lab-theory-construct/0.69.0','relationSchema'=>'sc-lab-theory-relation/0.69.0','predictionSchema'=>'sc-lab-theory-prediction/0.69.0','packetSchema'=>'sc-lab-scientific-theory-packet/0.69.0'));}
    public static function health(){
        $required=array('backend/app/scientific_theory_v0690.py','backend/tests/test_scientific_theory_v0690.py','assets/js/modules/scientific-theory-v0690.js','assets/css/sc-lab-scientific-theory-v0690.css','contracts/scientific-theory-v0690.schema.json','contracts/theory-construct-v0690.schema.json','contracts/theory-relation-v0690.schema.json','contracts/theory-prediction-v0690.schema.json','contracts/scientific-theory-packet-v0690.schema.json','contracts/scientific-theory-policy-v0690.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-theory-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'conceptualModels'=>true,'mechanisticTheories'=>true,'constructDefinitionsExplicit'=>true,'theoryRelationsExplicit'=>true,'testablePredictionsRequired'=>true,'falsificationBoundariesRequired'=>true,'humanTheoryReviewRequired'=>true,'automaticTheoryProof'=>false,'automaticCausalCertification'=>false,'automaticUniversalGeneralization'=>false,'rawScientificDataAccepted'=>false,'participantLevelDataAccepted'=>false,'networkFetchDuringEvaluation'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
