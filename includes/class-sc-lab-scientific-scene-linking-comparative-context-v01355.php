<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Scene_Linking_Comparative_Context_V01355 {
    const VERSION='0.135.5';
    const ENGINE_VERSION='16.5.0';
    const SCHEMA='sc-lab-scientific-scene-linking-comparative-context/0.135.5';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01355'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'linkTypeCount'=>10,'compareModeCount'=>6,'contextFamilyCount'=>12,'pinStateCount'=>3,'apiRouteCount'=>48)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'linkTypeCount'=>10,'compareModeCount'=>6,'contextFamilyCount'=>12,'pinStateCount'=>3,'linksMustBeExplicit'=>true,'crossObjectEquivalenceMustBeExplicit'=>true,'contextIsNonAuthoritative'=>true,'comparisonIsNotCausalInference'=>true,'automaticEquivalenceInference'=>false,'automaticJoinInference'=>false,'automaticEvidenceWeighting'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'scientific-scene-linking-comparative-context-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'crossSceneLinking'=>true,'comparativeInspection'=>true,'contextPreservation'=>true,'pinnedInspection'=>true,'contextCapsules'=>true,'v01354SceneBridge'=>true,'v01353CanvasBridge'=>true,'v01352GraphBridge'=>true,'platformCoreReferenceBridge'=>true,'presentationStateMutatesScientificRecord'=>false,'automaticEquivalenceInference'=>false,'automaticJoinInference'=>false,'automaticCausalInterpretation'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array('contracts/scientific-scene-linking-comparative-context-v01355.schema.json','contracts/scientific-scene-linking-comparative-context-policy-v01355.json','includes/class-sc-lab-scientific-scene-linking-comparative-context-v01355.php','assets/js/modules/scientific-scene-linking-comparative-context-v01355.js','assets/css/sc-lab-scientific-scene-linking-comparative-context-v01355.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-scene-linking-comparative-context-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'linkTypeCount'=>10,'compareModeCount'=>6,'contextFamilyCount'=>12,'pinStateCount'=>3,'apiRouteCount'=>48,'presentationStateMutatesScientificRecord'=>false,'automaticEquivalenceInference'=>false,'automaticJoinInference'=>false,'automaticCoreSubmission'=>false,'files'=>$files));
    }
}
SC_Lab_Scientific_Scene_Linking_Comparative_Context_V01355::init();
