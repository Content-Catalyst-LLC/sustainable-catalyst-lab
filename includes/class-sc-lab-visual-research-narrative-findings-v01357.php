<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Visual_Research_Narrative_Findings_V01357 {
    const VERSION='0.135.7'; const ENGINE_VERSION='16.7.0'; const SCHEMA='sc-lab-visual-research-narrative-findings/0.135.7';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01357'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'blockTypeCount'=>12,'findingStateCount'=>5,'handoffTargetCount'=>4,'citationModeCount'=>3,'apiRouteCount'=>56)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'blockTypeCount'=>12,'findingStateCount'=>5,'handoffTargetCount'=>4,'citationModeCount'=>3,'narrativeIsNotScientificClaim'=>true,'findingStatusIsDeclaredNotCertified'=>true,'presentationCannotUpgradeClaimStatus'=>true,'automaticEvidenceWeighting'=>false,'automaticTruthDetermination'=>false,'automaticCoreSubmission'=>false,'automaticPublication'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'visual-research-narrative-findings-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'governedVisualNarratives'=>true,'findingReferenceObjects'=>true,'citationBinding'=>true,'publicationHandoff'=>true,'reproducibleSessionBridge'=>true,'v01356SessionBridge'=>true,'v01355ContextBridge'=>true,'v01354SceneBridge'=>true,'v01353CanvasBridge'=>true,'v01352GraphBridge'=>true,'platformCoreReferenceBridge'=>true,'publicationStudioBridge'=>true,'knowledgeLibraryBridge'=>true,'workspaceBridge'=>true,'presentationCreatesScientificClaims'=>false,'automaticCoreSubmission'=>false,'automaticPublication'=>false)); }
    public static function health(){
        $req=array('contracts/visual-research-narrative-findings-v01357.schema.json','contracts/visual-research-narrative-findings-policy-v01357.json','includes/class-sc-lab-visual-research-narrative-findings-v01357.php','assets/js/modules/visual-research-narrative-findings-v01357.js','assets/css/sc-lab-visual-research-narrative-findings-v01357.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'visual-research-narrative-findings-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'blockTypeCount'=>12,'findingStateCount'=>5,'handoffTargetCount'=>4,'citationModeCount'=>3,'apiRouteCount'=>56,'presentationCreatesScientificClaims'=>false,'automaticCoreSubmission'=>false,'automaticPublication'=>false,'files'=>$files));
    }
}
SC_Lab_Visual_Research_Narrative_Findings_V01357::init();
