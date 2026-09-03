<?php
/** Sustainable Catalyst Lab v0.75.0 Scientific Data Binding & Transformation Pipeline. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Data_Binding_V0750 {
    const VERSION = '0.75.0';
    const ENGINE_VERSION = '2.2.0';
    private static $initialized = false;
    public static function init() { if (self::$initialized) { return; } self::$initialized = true; add_action('rest_api_init', array(__CLASS__, 'routes')); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/visualization/v0750/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/visualization/v0750/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) { $path = SC_LAB_DIR . ltrim((string)$relative, '/'); return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,
            'datasetSchema'=>'sc-lab-scientific-dataset/0.75.0','pipelineSchema'=>'sc-lab-data-transformation-pipeline/0.75.0','pipelineResultSchema'=>'sc-lab-data-transformation-result/0.75.0','bindingSchema'=>'sc-lab-visualization-data-binding/0.75.0',
            'specSchema'=>'sc-lab-scientific-visualization/0.75.0','figureSchema'=>'sc-lab-scientific-figure/0.75.0','workspaceSchema'=>'sc-lab-figure-workspace/0.75.0',
            'transforms'=>array('derive','filter','rename','select','drop','scale','unit-convert','cast','impute','sort','aggregate','bin','drop-missing'),
            'bindingRoles'=>array('x','y','z','w','yLow','yHigh','xLow','xHigh','group','label','size','weight','value','level'),
            'renderers'=>array('svg2d'=>array('advanced2d'=>true,'version'=>'0.74.0'),'canvas4d'=>array('syntheticCompatibility'=>'0.71.0','projectDataPointProjection'=>'0.75.0')),
            'capabilities'=>array('datasetFingerprinting'=>true,'pipelineFingerprinting'=>true,'bindingFingerprinting'=>true,'transformationLineage'=>true,'unitAware'=>true,'unitConversionViaV0550'=>true,'realProjectData2d'=>true,'realProjectData4dPointProjection'=>true),
            'boundaries'=>array('arbitraryCode'=>false,'arbitrarySql'=>false,'network'=>false,'filesystem'=>false,'automaticUnitInference'=>false,'automaticImputation'=>false,'surfaceInterpolation'=>false,'surfaceForecasting'=>false,'polarRadar'=>false,'dualAxis'=>false),
        ));
    }
    public static function health() {
        $required=array('backend/app/scientific_data_binding_v0750.py','backend/tests/test_scientific_data_binding_v0750.py','assets/js/modules/scientific-data-binding-v0750.js','assets/js/modules/graph-studio-v0750.js','assets/css/sc-lab-scientific-data-binding-v0750.css','contracts/scientific-dataset-v0750.schema.json','contracts/data-transformation-pipeline-v0750.schema.json','contracts/visualization-data-binding-v0750.schema.json','contracts/scientific-visualization-v0750.schema.json','contracts/scientific-figure-v0750.schema.json','contracts/figure-workspace-v0750.schema.json','assets/js/modules/scientific-visualization-engine-v0740.js');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-data-binding-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'datasetBinding'=>true,'transformationPipeline'=>true,'transformationLineage'=>true,'unitAware'=>true,'realProjectData2d'=>true,'realProjectData4dPointProjection'=>true,'surfaceInterpolation'=>false,'legacyV0550TransformCompatibility'=>true,'advanced2dCompatibility'=>true,'canvas4dCompatibility'=>true,'arbitraryCode'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
