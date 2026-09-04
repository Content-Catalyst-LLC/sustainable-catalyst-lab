<?php
/** Sustainable Catalyst Lab v0.85.0 — WebGL2 Scientific Renderer. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_WebGL2_Scientific_Renderer_V0850 {
    const VERSION='0.85.0';
    const ENGINE_VERSION='2.12.0';
    const RENDERER='webgl2';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/visualization/v0850/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/visualization/v0850/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'renderer'=>self::RENDERER,'productionRendererReady'=>true,
        'renderPlanSchema'=>'sc-lab-webgl2-render-plan/0.85.0','rendererSchema'=>'sc-lab-webgl2-renderer/0.85.0','pickingSchema'=>'sc-lab-webgl2-picking/0.85.0','workspaceSchema'=>'sc-lab-webgl2-workspace/0.85.0',
        'capabilities'=>array('depthBuffered3D'=>true,'gpuPointClouds'=>true,'gpuLineSegments'=>true,'gpuTriangleMeshes'=>true,'instancedGeometry'=>true,'rasterTextures'=>true,'clippingPlanes'=>true,'alphaBlending'=>true,'framebufferObjectPicking'=>true,'explicitRendererFallback'=>true,'approvedInternalShadersOnly'=>true,'webgpuProductionRendererReady'=>false),
        'boundaries'=>array('gpuRequiredForScientificCorrectness'=>false,'silentRendererFallback'=>false,'arbitraryShaderSource'=>false,'automaticSurfaceGeneration'=>false,'automaticSpatialInterpolation'=>false,'automaticTemporalInterpolation'=>false,'automaticScientificSemanticsChange'=>false)
    ));}
    public static function health(){
        $required=array('backend/app/webgl2_scientific_renderer_v0850.py','backend/tests/test_webgl2_scientific_renderer_v0850.py','assets/js/modules/webgl2-scientific-renderer-v0850.js','assets/js/modules/graph-studio-v0850.js','assets/css/sc-lab-webgl2-v0850.css','contracts/webgl2-renderer-v0850.schema.json','contracts/webgl2-render-plan-v0850.schema.json','contracts/webgl2-picking-v0850.schema.json','contracts/webgl2-workspace-v0850.schema.json','contracts/webgl2-renderer-policy-v0850.json');
        $files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'webgl2-scientific-renderer-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'renderer'=>self::RENDERER,'productionRendererReady'=>true,
            'depthBuffered3D'=>true,'gpuPointClouds'=>true,'gpuLineSegments'=>true,'gpuTriangleMeshes'=>true,'instancedGeometry'=>true,'rasterTextures'=>true,'clippingPlanes'=>true,'alphaBlending'=>true,'framebufferObjectPicking'=>true,'explicitRendererFallback'=>true,'approvedInternalShadersOnly'=>true,
            'v0840GPUArchitectureCompatibility'=>true,'v0830ProvenanceCompatibility'=>true,'v0820UncertaintyCompatibility'=>true,'v0810MarkupCompatibility'=>true,'v0800SpatialCompatibility'=>true,'v0790LinkedViewsCompatibility'=>true,'v0780TimeParameterCompatibility'=>true,'v0770SceneCompatibility'=>true,'v0760AdaptiveCompatibility'=>true,'v0750DataBindingCompatibility'=>true,
            'gpuRequiredForScientificCorrectness'=>false,'silentRendererFallback'=>false,'arbitraryShaderSource'=>false,'automaticSurfaceGeneration'=>false,'automaticSpatialInterpolation'=>false,'automaticTemporalInterpolation'=>false,'automaticScientificSemanticsChange'=>false,'webgpuProductionRendererReady'=>false,'files'=>$files
        ));
    }
}
