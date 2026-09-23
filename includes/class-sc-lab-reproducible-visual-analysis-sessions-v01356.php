<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Reproducible_Visual_Analysis_Sessions_V01356 {
    const VERSION='0.135.6'; const ENGINE_VERSION='16.6.0'; const SCHEMA='sc-lab-reproducible-visual-analysis-sessions/0.135.6';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01356'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'eventTypeCount'=>12,'sessionStateCount'=>4,'checkpointKindCount'=>5,'replayModeCount'=>3,'apiRouteCount'=>52)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'eventTypeCount'=>12,'sessionStateCount'=>4,'checkpointKindCount'=>5,'replayModeCount'=>3,'interactionLineageIsNotScientificEvidence'=>true,'replayRequiresDeclaredReferences'=>true,'presentationEventsNonAuthoritative'=>true,'automaticScientificInference'=>false,'automaticEvidenceWeighting'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'reproducible-visual-analysis-sessions-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'sessionCapture'=>true,'orderedInteractionLineage'=>true,'checkpoints'=>true,'deterministicReplayPlans'=>true,'contextPreservation'=>true,'v01355ContextBridge'=>true,'v01354SceneBridge'=>true,'v01353CanvasBridge'=>true,'v01352GraphBridge'=>true,'platformCoreReferenceBridge'=>true,'uiHistoryBecomesScientificEvidence'=>false,'replayMutatesSourceScience'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array('contracts/reproducible-visual-analysis-sessions-v01356.schema.json','contracts/reproducible-visual-analysis-sessions-policy-v01356.json','includes/class-sc-lab-reproducible-visual-analysis-sessions-v01356.php','assets/js/modules/reproducible-visual-analysis-sessions-v01356.js','assets/css/sc-lab-reproducible-visual-analysis-sessions-v01356.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'reproducible-visual-analysis-sessions-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'eventTypeCount'=>12,'sessionStateCount'=>4,'checkpointKindCount'=>5,'replayModeCount'=>3,'apiRouteCount'=>52,'uiHistoryBecomesScientificEvidence'=>false,'replayMutatesSourceScience'=>false,'automaticCoreSubmission'=>false,'files'=>$files));
    }
}
SC_Lab_Reproducible_Visual_Analysis_Sessions_V01356::init();
