<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Multi_View_Scientific_Analysis_Canvas_V01353 {
    const VERSION='0.135.3';
    const ENGINE_VERSION='16.3.0';
    const SCHEMA='sc-lab-multi-view-scientific-analysis-canvas/0.135.3';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01353'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'panelTypeCount'=>10,'layoutModeCount'=>5,'interactionChannelCount'=>8,'apiRouteCount'=>41)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'panelTypeCount'=>10,'layoutModeCount'=>5,'interactionChannelCount'=>8,'selectionIsPresentationState'=>true,'filtersMutateSourceData'=>false,'automaticJoinInference'=>false,'automaticScientificInterpretation'=>false,'automaticEvidenceWeighting'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'multi-view-scientific-analysis-canvas-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'coordinatedMultiViewCanvas'=>true,'linkedSelections'=>true,'sharedFilters'=>true,'synchronizedDomains'=>true,'diagnosticContext'=>true,'uncertaintyContext'=>true,'evidenceContext'=>true,'provenanceContext'=>true,'modelGraphContext'=>true,'v01352GraphBridge'=>true,'v01351VisualExperienceBridge'=>true,'platformCoreReferenceBridge'=>true,'selectionMutatesScientificRecord'=>false,'automaticJoinInference'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array('contracts/multi-view-scientific-analysis-canvas-v01353.schema.json','contracts/multi-view-scientific-analysis-canvas-policy-v01353.json','includes/class-sc-lab-multi-view-scientific-analysis-canvas-v01353.php','assets/js/modules/multi-view-scientific-analysis-canvas-v01353.js','assets/css/sc-lab-multi-view-scientific-analysis-canvas-v01353.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'multi-view-scientific-analysis-canvas-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'panelTypeCount'=>10,'layoutModeCount'=>5,'interactionChannelCount'=>8,'apiRouteCount'=>41,'selectionMutatesScientificRecord'=>false,'filtersMutateSourceData'=>false,'automaticJoinInference'=>false,'automaticCoreSubmission'=>false,'files'=>$files));
    }
}
SC_Lab_Multi_View_Scientific_Analysis_Canvas_V01353::init();
