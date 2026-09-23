<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Model_Architecture_Provenance_Graphs_V01352 {
    const VERSION='0.135.2';
    const ENGINE_VERSION='16.2.0';
    const SCHEMA='sc-lab-model-architecture-computational-provenance-graphs/0.135.2';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01352'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'viewModeCount'=>4,'layoutModeCount'=>3,'apiRouteCount'=>40)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'nodeTypeCount'=>20,'edgeTypeCount'=>18,'viewModeCount'=>4,'layoutModeCount'=>3,'fabricatedScientificValues'=>false,'automaticModelInference'=>false,'automaticProvenanceInference'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'model-architecture-computational-provenance-graphs-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'interactiveArchitectureGraph'=>true,'computationalProvenanceGraph'=>true,'executionTraceGraph'=>true,'uncertaintyFlowGraph'=>true,'evidenceLineageGraph'=>true,'upstreamDownstreamTraversal'=>true,'cycleOrphanAudits'=>true,'v01351VisualExperienceBridge'=>true,'platformCoreReferenceBridge'=>true,'automaticScientificInterpretation'=>false,'automaticEvidencePromotion'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array('contracts/model-architecture-computational-provenance-graphs-v01352.schema.json','contracts/model-architecture-computational-provenance-graphs-policy-v01352.json','includes/class-sc-lab-model-architecture-provenance-graphs-v01352.php','assets/js/modules/model-architecture-provenance-graphs-v01352.js','assets/css/sc-lab-model-architecture-provenance-graphs-v01352.css');
        $files=array(); $ok=true; foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'model-architecture-computational-provenance-graphs-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'nodeTypeCount'=>20,'edgeTypeCount'=>18,'viewModeCount'=>4,'layoutModeCount'=>3,'apiRouteCount'=>40,'automaticModelInference'=>false,'automaticProvenanceInference'=>false,'automaticCoreSubmission'=>false,'files'=>$files));
    }
}
SC_Lab_Model_Architecture_Provenance_Graphs_V01352::init();
