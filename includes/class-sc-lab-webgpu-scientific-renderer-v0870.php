<?php
/** Sustainable Catalyst Lab v0.87.0 — WebGPU Scientific Renderer & GPU Compute. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_WebGPU_Scientific_Renderer_V0870 {
    const VERSION='0.87.0'; const ENGINE_VERSION='2.13.0'; const RENDERER='webgpu'; private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/visualization/v0870/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/visualization/v0870/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){
        return rest_ensure_response(array(
            'ok'=>true,
            'version'=>self::VERSION,
            'engineVersion'=>self::ENGINE_VERSION,
            'renderer'=>self::RENDERER,
            'productionRendererReady'=>true,
            'webgpuComputeReady'=>true,
            'renderPlanSchema'=>'sc-lab-webgpu-render-plan/0.87.0',
            'computePlanSchema'=>'sc-lab-webgpu-compute-plan/0.87.0',
            'workspaceSchema'=>'sc-lab-webgpu-workspace/0.87.0',
            'capabilities'=>array(
                'gpuFiltering'=>true,'gpuHistogram'=>true,'gpuReduction'=>true,
                'gpuSpatialBinning'=>true,'typedStorageBuffers'=>true,
                'approvedWGSLOnly'=>true,'explicitWebGL2Fallback'=>true
            ),
            'boundaries'=>array(
                'gpuRequiredForScientificCorrectness'=>false,
                'silentRendererFallback'=>false,
                'arbitraryWGSLSource'=>false,
                'automaticScientificSemanticsChange'=>false,
                'automaticInterpolation'=>false,
                'automaticImputation'=>false,
                'automaticForecasting'=>false,
                'computeResultCreatesObservation'=>false
            )
        ));
    }
    public static function health(){
        $required=array('backend/app/webgpu_scientific_renderer_v0870.py','backend/tests/test_webgpu_scientific_renderer_v0870.py','assets/js/modules/webgpu-scientific-renderer-v0870.js','assets/js/modules/graph-studio-v0870.js','assets/css/sc-lab-webgpu-v0870.css','contracts/webgpu-renderer-v0870.schema.json','contracts/webgpu-render-plan-v0870.schema.json','contracts/webgpu-compute-plan-v0870.schema.json','contracts/webgpu-workspace-v0870.schema.json','contracts/webgpu-renderer-policy-v0870.json');
        $files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'webgpu-scientific-renderer-compute-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'renderer'=>self::RENDERER,'productionRendererReady'=>true,'webgpuComputeReady'=>true,'gpuFiltering'=>true,'gpuHistogram'=>true,'gpuReduction'=>true,'gpuSpatialBinning'=>true,'typedStorageBuffers'=>true,'approvedWGSLOnly'=>true,'explicitWebGL2Fallback'=>true,'v0860SystemDynamicsCompatibility'=>true,'v0850WebGL2Compatibility'=>true,'v0840GPUArchitectureCompatibility'=>true,'v0830ProvenanceCompatibility'=>true,'v0820UncertaintyCompatibility'=>true,'gpuRequiredForScientificCorrectness'=>false,'silentRendererFallback'=>false,'arbitraryWGSLSource'=>false,'automaticScientificSemanticsChange'=>false,'automaticInterpolation'=>false,'automaticImputation'=>false,'automaticForecasting'=>false,'computeResultCreatesObservation'=>false,'webgl2FallbackPreservesScientificContract'=>true,'files'=>$files));
    }
}
