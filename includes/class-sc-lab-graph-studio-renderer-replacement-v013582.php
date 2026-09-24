<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Renderer_Replacement_V013582 {
    const VERSION='0.135.8.2';
    const ENGINE='3.0.0';
    const ROUTE_COUNT=24;
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/analysis/v013582';
        foreach(array('health','manifest','renderer-registry','view-catalog','legacy-audit','boundaries') as $r){
            register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,str_replace('-','_',$r)),'permission_callback'=>'__return_true'));
        }
    }
    private static function state($rel){$p=SC_LAB_DIR.$rel;return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function health(){
        $req=array('assets/js/modules/graph-studio-renderer-replacement-v013582.js','assets/css/sc-lab-graph-studio-renderer-replacement-v013582.css','includes/class-sc-lab-graph-studio-renderer-replacement-v013582.php');
        $files=array();$ok=true;foreach($req as $rel){$files[$rel]=self::state($rel);if(empty($files[$rel]['exists']))$ok=false;}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'advanced-renderer-ready':'incomplete','version'=>self::VERSION,'engineVersion'=>self::ENGINE,'requiredBackendRouteCount'=>self::ROUTE_COUNT,'primaryRendererOwner'=>'graph-studio-renderer-v013582','legacyGraphStudioRuntimeExecuted'=>false,'singlePrimaryViewport'=>true,'scientificMutationFromPresentation'=>false,'files'=>$files));
    }
    public static function manifest(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE,'workspaceViews'=>array('figure','analysis','provenance','scene','compare','session','narrative','review'),'rendererModes'=>array('plot','distribution','diagnostics','uncertainty','provenance','scene'),'legacyGraphStudioModulesQuarantined'=>array('v0790','v0800','v0810','v0820','v0830','v0840','v0850','v0870','v0880'),'referenceFirst'=>true));}
    public static function renderer_registry(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'registry'=>array('svg2d'=>array('status'=>'active','owner'=>'v013582'),'canvas2d'=>array('status'=>'ready','owner'=>'v013582'),'webgl2'=>array('status'=>'adapter','owner'=>'capability'),'webgpu'=>array('status'=>'adapter','owner'=>'capability'),'scene3d'=>array('status'=>'ready','owner'=>'v013582'))));}
    public static function view_catalog(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'views'=>array('figure','analysis','provenance','scene','compare','session','narrative','review'),'figureModes'=>array('plot','distribution','diagnostics','uncertainty','provenance','scene')));}
    public static function legacy_audit(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'legacyPrimaryRendererOwner'=>false,'legacyGraphStudioExecutionAllowed'=>false,'compatibilityFilesRetained'=>true));}
    public static function boundaries(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'presentationCreatesEvidence'=>false,'presentationChangesClaimStatus'=>false,'automaticCausalInference'=>false,'automaticJoinInference'=>false,'automaticCoreSubmission'=>false));}
}
SC_Lab_Graph_Studio_Renderer_Replacement_V013582::init();
