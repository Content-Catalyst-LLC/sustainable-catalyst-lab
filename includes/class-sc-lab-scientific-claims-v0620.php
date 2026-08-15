<?php
/** Sustainable Catalyst Lab v0.62.0 — Scientific Claims, Evidence Matrix & Conclusion Traceability. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Claims_V0620 {
    const VERSION='0.62.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-claims/v0620/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-claims/v0620/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'claimSchema'=>'sc-lab-scientific-claim/0.62.0','conclusionSchema'=>'sc-lab-scientific-conclusion/0.62.0','matrixSchema'=>'sc-lab-scientific-evidence-matrix/0.62.0','reviewSchema'=>'sc-lab-scientific-claim-review/0.62.0','packetSchema'=>'sc-lab-conclusion-traceability-packet/0.62.0'));}
    public static function health(){
        $required=array('backend/app/scientific_claims_traceability_v0620.py','backend/tests/test_scientific_claims_traceability_v0620.py','assets/js/modules/scientific-claims-v0620.js','assets/css/sc-lab-scientific-claims-v0620.css','contracts/scientific-claim-v0620.schema.json','contracts/scientific-conclusion-v0620.schema.json','contracts/scientific-evidence-matrix-v0620.schema.json','contracts/scientific-claim-review-v0620.schema.json','contracts/conclusion-traceability-packet-v0620.schema.json','contracts/scientific-claims-policy-v0620.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-claims-traceability-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'scientificClaimsEvidenceMatrix'=>true,'conclusionTraceability'=>true,'humanClaimReviewRequired'=>true,'humanConclusionReviewRequired'=>true,'automaticClaimInference'=>false,'automaticScientificCertification'=>false,'automaticCausalClaim'=>false,'automaticConclusionGeneration'=>false,'automaticPublication'=>false,'rawScientificDataAccepted'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
