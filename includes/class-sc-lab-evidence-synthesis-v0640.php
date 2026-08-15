<?php
/** Sustainable Catalyst Lab v0.64.0 — Replication, Systematic Evidence Synthesis & Meta-Analysis. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Evidence_Synthesis_V0640 {
    const VERSION='0.64.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/evidence-synthesis/v0640/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/evidence-synthesis/v0640/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'protocolSchema'=>'sc-lab-systematic-evidence-synthesis-protocol/0.64.0','effectSchema'=>'sc-lab-study-effect-estimate/0.64.0','replicationSchema'=>'sc-lab-replication-assessment/0.64.0','metaSchema'=>'sc-lab-meta-analysis-result/0.64.0','packetSchema'=>'sc-lab-systematic-evidence-synthesis-packet/0.64.0'));}
    public static function health(){
        $required=array('backend/app/systematic_evidence_synthesis_v0640.py','backend/tests/test_systematic_evidence_synthesis_v0640.py','assets/js/modules/evidence-synthesis-v0640.js','assets/css/sc-lab-evidence-synthesis-v0640.css','contracts/systematic-evidence-synthesis-protocol-v0640.schema.json','contracts/study-effect-estimate-v0640.schema.json','contracts/replication-assessment-v0640.schema.json','contracts/meta-analysis-result-v0640.schema.json','contracts/systematic-evidence-synthesis-packet-v0640.schema.json','contracts/systematic-evidence-synthesis-policy-v0640.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'systematic-evidence-synthesis-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'systematicEvidenceSynthesis'=>true,'fixedEffectMetaAnalysis'=>true,'randomEffectsMetaAnalysis'=>true,'heterogeneityDiagnostics'=>true,'leaveOneOutSensitivity'=>true,'replicationAssessment'=>true,'humanSynthesisReviewRequired'=>true,'rawParticipantDataAccepted'=>false,'automaticTruthInference'=>false,'automaticCausalCertification'=>false,'publicationBiasCorrection'=>false,'networkFetchDuringSynthesis'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
