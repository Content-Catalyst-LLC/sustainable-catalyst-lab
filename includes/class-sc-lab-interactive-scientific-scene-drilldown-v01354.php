<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Interactive_Scientific_Scene_DrillDown_V01354 {
    const VERSION='0.135.4';
    const ENGINE_VERSION='16.4.0';
    const SCHEMA='sc-lab-interactive-scientific-scene-drilldown/0.135.4';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01354'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'layerTypeCount'=>12,'drillTargetTypeCount'=>8,'viewModeCount'=>6,'navigationModeCount'=>5,'lodModeCount'=>4,'apiRouteCount'=>45)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'layerTypeCount'=>12,'drillTargetTypeCount'=>8,'viewModeCount'=>6,'navigationModeCount'=>5,'lodModeCount'=>4,'drillHierarchyMustBeExplicit'=>true,'cameraIsPresentationState'=>true,'viewportIsPresentationState'=>true,'automaticHierarchyInference'=>false,'automaticJoinInference'=>false,'automaticScientificInterpretation'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'interactive-scientific-scene-drilldown-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'interactiveScene'=>true,'visualDrillDown'=>true,'explicitHierarchyNavigation'=>true,'crossLayerInspection'=>true,'lodPlanning'=>true,'spatialTemporalDrillDown'=>true,'evidenceProvenanceTrace'=>true,'v01353CanvasBridge'=>true,'v01352GraphBridge'=>true,'v01351VisualExperienceBridge'=>true,'platformCoreReferenceBridge'=>true,'drillDownMutatesScientificRecord'=>false,'automaticHierarchyInference'=>false,'automaticJoinInference'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array('contracts/interactive-scientific-scene-drilldown-v01354.schema.json','contracts/interactive-scientific-scene-drilldown-policy-v01354.json','includes/class-sc-lab-interactive-scientific-scene-drilldown-v01354.php','assets/js/modules/interactive-scientific-scene-drilldown-v01354.js','assets/css/sc-lab-interactive-scientific-scene-drilldown-v01354.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'interactive-scientific-scene-drilldown-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'layerTypeCount'=>12,'drillTargetTypeCount'=>8,'viewModeCount'=>6,'navigationModeCount'=>5,'lodModeCount'=>4,'apiRouteCount'=>45,'drillDownMutatesScientificRecord'=>false,'cameraMutatesScientificRecord'=>false,'automaticHierarchyInference'=>false,'automaticJoinInference'=>false,'automaticCoreSubmission'=>false,'files'=>$files));
    }
}
SC_Lab_Interactive_Scientific_Scene_DrillDown_V01354::init();
