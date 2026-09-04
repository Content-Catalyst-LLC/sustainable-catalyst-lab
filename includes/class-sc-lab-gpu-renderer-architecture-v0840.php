<?php
/** Sustainable Catalyst Lab v0.84.0 — GPU Renderer Architecture. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_GPU_Renderer_Architecture_V0840 {
    const VERSION='0.84.0';
    const ENGINE_VERSION='2.11.0';
    private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/visualization/v0840/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/visualization/v0840/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'architecture'=>'gpu-renderer-architecture',
        'registrySchema'=>'sc-lab-renderer-registry/0.84.0','negotiationSchema'=>'sc-lab-renderer-negotiation/0.84.0','bufferSchema'=>'sc-lab-gpu-buffer-plan/0.84.0','shaderSchema'=>'sc-lab-shader-descriptor/0.84.0','pickingSchema'=>'sc-lab-picking-contract/0.84.0','workspaceSchema'=>'sc-lab-gpu-renderer-workspace/0.84.0',
        'capabilities'=>array('rendererCapabilityRegistry'=>true,'browserFeatureDetection'=>true,'safeRendererNegotiation'=>true,'explicitFallbackRecording'=>true,'gpuBufferContracts'=>true,'shaderRegistryContracts'=>true,'pickingContracts'=>true,'memoryBudgets'=>true,'rendererDiagnostics'=>true,'webgl2CapabilityDetection'=>true,'webgpuCapabilityDetection'=>true,'webgl2ProductionRendererReady'=>false,'webgpuProductionRendererReady'=>false),
        'boundaries'=>array('gpuRequiredForScientificCorrectness'=>false,'serverAssumesBrowserGPU'=>false,'silentRendererFallback'=>false,'automaticScientificSemanticsChange'=>false,'arbitraryShaderSource'=>false)
    ));}
    public static function health(){
        $required=array('backend/app/gpu_renderer_architecture_v0840.py','backend/tests/test_gpu_renderer_architecture_v0840.py','assets/js/modules/gpu-renderer-architecture-v0840.js','assets/js/modules/graph-studio-v0840.js','assets/css/sc-lab-gpu-v0840.css','contracts/renderer-registry-v0840.schema.json','contracts/renderer-negotiation-v0840.schema.json','contracts/gpu-buffer-plan-v0840.schema.json','contracts/shader-descriptor-v0840.schema.json','contracts/picking-contract-v0840.schema.json','contracts/gpu-renderer-workspace-v0840.schema.json','contracts/gpu-renderer-policy-v0840.json');
        $files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,'status'=>$ok?'gpu-renderer-architecture-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'architecture'=>'gpu-renderer-architecture',
            'rendererCapabilityRegistry'=>true,'browserFeatureDetection'=>true,'safeRendererNegotiation'=>true,'explicitFallbackRecording'=>true,'gpuBufferContracts'=>true,'shaderRegistryContracts'=>true,'pickingContracts'=>true,'memoryBudgets'=>true,'rendererDiagnostics'=>true,'webgl2CapabilityDetection'=>true,'webgpuCapabilityDetection'=>true,'webgl2ProductionRendererReady'=>false,'webgpuProductionRendererReady'=>false,
            'v0830ProvenanceCompatibility'=>true,'v0820UncertaintyCompatibility'=>true,'v0810MarkupCompatibility'=>true,'v0800SpatialCompatibility'=>true,'v0790LinkedViewsCompatibility'=>true,'v0780TimeParameterCompatibility'=>true,'v0770SceneCompatibility'=>true,'v0760AdaptiveCompatibility'=>true,'v0750DataBindingCompatibility'=>true,
            'gpuRequiredForScientificCorrectness'=>false,'serverAssumesBrowserGPU'=>false,'silentRendererFallback'=>false,'automaticScientificSemanticsChange'=>false,'arbitraryShaderSource'=>false,'files'=>$files
        ));
    }
}
