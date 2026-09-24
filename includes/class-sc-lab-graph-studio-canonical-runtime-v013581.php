<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Canonical_Runtime_V013581 {
    const VERSION='0.135.8.1';
    const CANONICAL_ENGINE='2.6.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/analysis/v013581';
        foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); }
    }
    private static function state($rel){$p=SC_LAB_DIR.$rel;return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function health(){
        $req=array('assets/js/modules/graph-studio-canonical-runtime-v013581.js','assets/css/sc-lab-graph-studio-canonical-runtime-v013581.css','includes/class-sc-lab-graph-studio-canonical-runtime-v013581.php');
        $files=array();$ok=true;foreach($req as $rel){$files[$rel]=self::state($rel);if(empty($files[$rel]['exists']))$ok=false;}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'graph-studio-canonical-runtime-ready':'incomplete','version'=>self::VERSION,'canonicalEngineVersion'=>self::CANONICAL_ENGINE,'canonicalViewCount'=>8,'isolatedCapabilityPanelCount'=>13,'singleActiveResearchView'=>true,'legacyCapabilityAdaptersQuarantined'=>true,'presentationStateSeparated'=>true,'scientificMutationFromNavigation'=>false,'automaticScientificInference'=>false,'files'=>$files));
    }
    public static function manifest(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'canonicalOwner'=>'graph-studio-canonical-runtime','canonicalViews'=>array('figure','analysis','provenance','scene','compare','session','narrative','review'),'capabilityAdapters'=>array('binding','adaptive','scene-engine','state','linked','spatial','markup','uncertainty','provenance','gpu','webgl2','webgpu','advanced3d'),'v01351ToV01358Retained'=>true,'historicalControlsDefaultCollapsed'=>true));}
    public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'schema'=>'sc-lab-graph-studio-canonical-runtime/0.135.8.1','viewState'=>'presentation-only','scientificObjects'=>'reference-first'));}
    public static function catalog(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'viewCount'=>8,'capabilityPanelCount'=>13,'defaultView'=>'figure','rendererOwner'=>'canonical-runtime','legacyRendererPanels'=>'isolated-adapters'));}
}
SC_Lab_Graph_Studio_Canonical_Runtime_V013581::init();
