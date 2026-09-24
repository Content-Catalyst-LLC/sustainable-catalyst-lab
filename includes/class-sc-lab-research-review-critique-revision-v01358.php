<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Research_Review_Critique_Revision_V01358 {
    const VERSION='0.135.8'; const ENGINE_VERSION='16.8.0'; const SCHEMA='sc-lab-research-review-critique-revision-lineage/0.135.8';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01358'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'reviewStateCount'=>6,'critiqueTypeCount'=>8,'responseStateCount'=>5,'decisionStateCount'=>5,'revisionKindCount'=>5,'handoffTargetCount'=>5,'apiRouteCount'=>60)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'reviewStateCount'=>6,'critiqueTypeCount'=>8,'responseStateCount'=>5,'decisionStateCount'=>5,'revisionKindCount'=>5,'handoffTargetCount'=>5,'reviewIsNotScientificCertification'=>true,'reviewerCommentsAreNotEvidence'=>true,'revisionDoesNotUpgradeClaimStatus'=>true,'automaticAcceptance'=>false,'automaticEvidenceWeighting'=>false,'automaticTruthDetermination'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'research-review-critique-revision-lineage-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'governedReviewPackages'=>true,'critiqueResponseLineage'=>true,'revisionDiffLineage'=>true,'replicationReferenceBridge'=>true,'v01357NarrativeBridge'=>true,'v01356SessionBridge'=>true,'workspaceReviewBridge'=>true,'replicationStudioBridge'=>true,'platformCoreReferenceBridge'=>true,'publicationStudioBridge'=>true,'knowledgeLibraryBridge'=>true,'reviewCreatesScientificCertification'=>false,'automaticAcceptance'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array('contracts/research-review-critique-revision-v01358.schema.json','contracts/research-review-critique-revision-policy-v01358.json','includes/class-sc-lab-research-review-critique-revision-v01358.php','assets/js/modules/research-review-critique-revision-v01358.js','assets/css/sc-lab-research-review-critique-revision-v01358.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'research-review-critique-revision-lineage-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'reviewStateCount'=>6,'critiqueTypeCount'=>8,'responseStateCount'=>5,'decisionStateCount'=>5,'revisionKindCount'=>5,'handoffTargetCount'=>5,'apiRouteCount'=>60,'reviewCreatesScientificCertification'=>false,'automaticAcceptance'=>false,'automaticCoreSubmission'=>false,'files'=>$files));
    }
}
SC_Lab_Research_Review_Critique_Revision_V01358::init();
