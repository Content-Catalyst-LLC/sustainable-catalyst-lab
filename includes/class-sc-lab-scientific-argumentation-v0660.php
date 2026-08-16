<?php
/** Sustainable Catalyst Lab v0.66.0 — Competing Hypotheses & Scientific Argumentation. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Argumentation_V0660 {
    const VERSION='0.66.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-argumentation/v0660/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-argumentation/v0660/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'caseSchema'=>'sc-lab-scientific-argumentation-case/0.66.0',
        'hypothesisSchema'=>'sc-lab-scientific-hypothesis/0.66.0',
        'evidenceLinkSchema'=>'sc-lab-hypothesis-evidence-link/0.66.0',
        'discriminatingTestSchema'=>'sc-lab-discriminating-test/0.66.0',
        'packetSchema'=>'sc-lab-scientific-argumentation-packet/0.66.0'
    ));}
    public static function health(){
        $required=array(
            'backend/app/scientific_argumentation_v0660.py','backend/tests/test_scientific_argumentation_v0660.py',
            'assets/js/modules/scientific-argumentation-v0660.js','assets/css/sc-lab-scientific-argumentation-v0660.css',
            'contracts/scientific-argumentation-case-v0660.schema.json','contracts/scientific-hypothesis-v0660.schema.json',
            'contracts/hypothesis-evidence-link-v0660.schema.json','contracts/discriminating-test-v0660.schema.json',
            'contracts/scientific-argumentation-packet-v0660.schema.json','contracts/scientific-argumentation-policy-v0660.json','templates/lab-app.php'
        );
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'scientific-argumentation-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'competingHypotheses'=>true,'predictionsExplicit'=>true,'falsifyingEvidencePreserved'=>true,'discriminatingTestsExplicit'=>true,
            'unresolvedAlternativesPreserved'=>true,'humanHypothesisReviewRequired'=>true,'humanArgumentReviewRequired'=>true,
            'automaticHypothesisProof'=>false,'automaticWinnerSelection'=>false,'automaticFalsification'=>false,'numericTruthScore'=>false,
            'rawScientificDataAccepted'=>false,'networkFetchDuringEvaluation'=>false,'arbitraryCode'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
