<?php
/** Sustainable Catalyst Lab v0.65.0 — Scientific Evidence Grading, Contradiction Analysis & Consensus Boundaries. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Evidence_Grading_V0650 {
    const VERSION='0.65.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/evidence-grading/v0650/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/evidence-grading/v0650/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,
        'assessmentSchema'=>'sc-lab-scientific-evidence-grading-assessment/0.65.0',
        'gradeSchema'=>'sc-lab-scientific-evidence-grade/0.65.0',
        'contradictionSchema'=>'sc-lab-scientific-contradiction-analysis/0.65.0',
        'consensusSchema'=>'sc-lab-scientific-consensus-boundary/0.65.0',
        'packetSchema'=>'sc-lab-scientific-evidence-consensus-packet/0.65.0'
    ));}
    public static function health(){
        $required=array(
            'backend/app/scientific_evidence_grading_v0650.py','backend/tests/test_scientific_evidence_grading_v0650.py',
            'assets/js/modules/evidence-grading-v0650.js','assets/css/sc-lab-evidence-grading-v0650.css',
            'contracts/scientific-evidence-grading-assessment-v0650.schema.json','contracts/scientific-evidence-grade-v0650.schema.json',
            'contracts/scientific-contradiction-analysis-v0650.schema.json','contracts/scientific-consensus-boundary-v0650.schema.json',
            'contracts/scientific-evidence-consensus-packet-v0650.schema.json','contracts/scientific-evidence-grading-policy-v0650.json','templates/lab-app.php'
        );
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'scientific-evidence-grading-ready':'incomplete','version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'transparentRuleBasedEvidenceGrading'=>true,'contradictionAnalysis'=>true,'consensusBoundaryAssessment'=>true,
            'humanBoundaryReviewRequired'=>true,'numericTruthScore'=>false,'automaticConsensusCertification'=>false,
            'automaticStudyQualityScoring'=>false,'citationCountAuthorityScoring'=>false,'journalPrestigeScoring'=>false,
            'rawScientificDataAccepted'=>false,'networkFetchDuringEvaluation'=>false,'arbitraryCode'=>false,
            'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')
        ));
    }
}
