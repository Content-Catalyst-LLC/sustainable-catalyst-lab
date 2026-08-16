<?php
/** Sustainable Catalyst Lab v0.68.0 — Hierarchical, Multilevel & Cross-Study Modeling. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Hierarchical_Modeling_V0680 {
    const VERSION='0.68.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/hierarchical-modeling/v0680/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/hierarchical-modeling/v0680/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'modelSchema'=>'sc-lab-hierarchical-model/0.68.0','unitSchema'=>'sc-lab-hierarchical-unit-estimate/0.68.0','fitSchema'=>'sc-lab-hierarchical-fit/0.68.0','packetSchema'=>'sc-lab-hierarchical-modeling-packet/0.68.0'));}
    public static function health(){
        $required=array('backend/app/hierarchical_modeling_v0680.py','backend/tests/test_hierarchical_modeling_v0680.py','assets/js/modules/hierarchical-modeling-v0680.js','assets/css/sc-lab-hierarchical-modeling-v0680.css','contracts/hierarchical-model-v0680.schema.json','contracts/hierarchical-unit-estimate-v0680.schema.json','contracts/hierarchical-fit-v0680.schema.json','contracts/hierarchical-modeling-packet-v0680.schema.json','contracts/hierarchical-modeling-policy-v0680.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'hierarchical-modeling-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'hierarchicalNormal'=>true,'randomIntercept'=>true,'randomSlope'=>true,'crossStudyPooling'=>true,'crossStudyMetaRegression'=>true,'aggregateUnitEstimatesOnly'=>true,'partialPoolingExplicit'=>true,'heterogeneityReported'=>true,'shrinkageDiagnosticsReported'=>true,'humanModelReviewRequired'=>true,'automaticGeneralizability'=>false,'automaticEcologicalInference'=>false,'automaticCausalProof'=>false,'rawScientificDataAccepted'=>false,'participantLevelDataAccepted'=>false,'networkFetchDuringEvaluation'=>false,'arbitraryCode'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
