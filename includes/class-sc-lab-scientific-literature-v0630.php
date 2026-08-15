<?php
/** Sustainable Catalyst Lab v0.63.0 — Scientific Literature, Citation Graph & Source-to-Claim Provenance. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Literature_V0630 {
    const VERSION='0.63.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/scientific-literature/v0630/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/scientific-literature/v0630/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'sourceSchema'=>'sc-lab-scientific-literature-source/0.63.0','sourceReviewSchema'=>'sc-lab-scientific-literature-review/0.63.0','claimLinkSchema'=>'sc-lab-source-claim-provenance/0.63.0','citationGraphSchema'=>'sc-lab-scientific-citation-graph/0.63.0','packetSchema'=>'sc-lab-scientific-literature-provenance-packet/0.63.0'));}
    public static function health(){
        $required=array('backend/app/scientific_literature_provenance_v0630.py','backend/tests/test_scientific_literature_provenance_v0630.py','assets/js/modules/scientific-literature-v0630.js','assets/css/sc-lab-scientific-literature-v0630.css','contracts/scientific-literature-source-v0630.schema.json','contracts/scientific-literature-review-v0630.schema.json','contracts/source-claim-provenance-v0630.schema.json','contracts/scientific-citation-graph-v0630.schema.json','contracts/scientific-literature-provenance-packet-v0630.schema.json','contracts/scientific-literature-policy-v0630.json','templates/lab-app.php');
        $files=array();$ok=true;foreach($required as $rel){$present=is_file(SC_LAB_DIR.$rel);$files[$rel]=$present;if(!$present){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-literature-provenance-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'literatureSourceRegistry'=>true,'citationGraph'=>true,'sourceToClaimProvenance'=>true,'humanSourceReviewRequired'=>true,'automaticTruthScoring'=>false,'automaticAuthorityRanking'=>false,'automaticRetractionVerification'=>false,'networkFetchDuringEvaluation'=>false,'rawFullTextAccepted'=>false,'automaticPublication'=>false,'contextualNavigationPreserved'=>true,'threeApplicationCardRowPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
