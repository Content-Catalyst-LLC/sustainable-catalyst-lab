<?php
/** Sustainable Catalyst Lab v0.88.0 — Advanced 3D Scientific Scene Engine II. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Advanced_Scientific_Scene_V0880 {
    const VERSION='0.88.0'; const ENGINE_VERSION='2.14.0'; const ENGINE='advanced-3d-scene'; private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){
        register_rest_route('sc-lab/v1','/visualization/v0880/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/visualization/v0880/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){return rest_ensure_response(array(
        'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'engine'=>self::ENGINE,
        'nativeWebGPUSceneRendererReady'=>true,'threeJSAdapterReady'=>true,'threeJSRuntimeBundled'=>false,'externalCDNRequired'=>false,
        'sceneSchema'=>'sc-lab-advanced-scientific-scene/0.88.0','renderPlanSchema'=>'sc-lab-advanced-scientific-scene-plan/0.88.0','workspaceSchema'=>'sc-lab-advanced-scientific-scene-workspace/0.88.0',
        'capabilities'=>array('sceneGraphs'=>true,'perspectiveCamera'=>true,'orthographicCamera'=>true,'ambientLighting'=>true,'directionalLighting'=>true,'pointLighting'=>true,'instancedGeometry'=>true,'pointClouds'=>true,'lineGeometry'=>true,'triangleMeshes'=>true,'orbitInteraction'=>true,'panInteraction'=>true,'zoomInteraction'=>true,'threeJSCompatibilityAdapter'=>true,'nativeWebGPUExecution'=>true),
        'boundaries'=>array('automaticGeometryGeneration'=>false,'automaticTriangulation'=>false,'automaticSurfaceInterpolation'=>false,'automaticScientificInterpretation'=>false,'automaticUnitConversion'=>false,'automaticLightingFromData'=>false,'automaticNormalGeneration'=>false,'lightingChangesScientificValues'=>false,'materialChangesScientificValues'=>false,'interactionCreatesObservation'=>false,'arbitraryShaderSource'=>false,'silentRendererFallback'=>false,'threeJSRequiredForScientificCorrectness'=>false,'webgpuRequiredForScientificCorrectness'=>false)
    ));}
    public static function health(){
        $required=array('backend/app/advanced_scientific_scene_v0880.py','backend/tests/test_advanced_scientific_scene_v0880.py','assets/js/modules/advanced-scientific-scene-v0880.js','assets/js/modules/graph-studio-v0880.js','assets/css/sc-lab-advanced-3d-v0880.css','contracts/advanced-scientific-scene-v0880.schema.json','contracts/advanced-scientific-scene-plan-v0880.schema.json','contracts/advanced-scientific-scene-workspace-v0880.schema.json','contracts/advanced-scientific-scene-policy-v0880.json');
        $files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'advanced-3d-scientific-scene-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'engine'=>self::ENGINE,'nativeWebGPUSceneRendererReady'=>true,'threeJSAdapterReady'=>true,'threeJSRuntimeBundled'=>false,'externalCDNRequired'=>false,'sceneGraphs'=>true,'lighting'=>true,'instancing'=>true,'scientific3DInteraction'=>true,'v0870WebGPUCompatibility'=>true,'v0850WebGL2Compatibility'=>true,'v0830ProvenanceCompatibility'=>true,'v0770SceneSemanticsCompatibility'=>true,'automaticGeometryGeneration'=>false,'automaticTriangulation'=>false,'automaticSurfaceInterpolation'=>false,'automaticScientificInterpretation'=>false,'automaticUnitConversion'=>false,'automaticLightingFromData'=>false,'automaticNormalGeneration'=>false,'lightingChangesScientificValues'=>false,'materialChangesScientificValues'=>false,'interactionCreatesObservation'=>false,'arbitraryShaderSource'=>false,'silentRendererFallback'=>false,'threeJSRequiredForScientificCorrectness'=>false,'webgpuRequiredForScientificCorrectness'=>false,'files'=>$files));
    }
}
