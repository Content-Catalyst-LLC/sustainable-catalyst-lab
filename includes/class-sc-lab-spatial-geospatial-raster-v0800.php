<?php
/** Sustainable Catalyst Lab v0.80.0 — Spatial, Geospatial & Raster Visualization. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Spatial_Geospatial_Raster_V0800 {
    const VERSION='0.80.0'; const ENGINE_VERSION='2.7.0'; private static $initialized=false;
    public static function init(){ if(self::$initialized){return;} self::$initialized=true; add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
      register_rest_route('sc-lab/v1','/visualization/v0800/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
      register_rest_route('sc-lab/v1','/visualization/v0800/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){return rest_ensure_response(array(
      'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'renderer'=>'canvas-spatial',
      'crsSchema'=>'sc-lab-spatial-crs/0.80.0','vectorSchema'=>'sc-lab-spatial-vector-layer/0.80.0','rasterSchema'=>'sc-lab-spatial-raster/0.80.0','viewportSchema'=>'sc-lab-spatial-viewport/0.80.0','figureSchema'=>'sc-lab-spatial-figure/0.80.0','workspaceSchema'=>'sc-lab-figure-workspace/0.80.0',
      'geometryTypes'=>array('Point','MultiPoint','LineString','MultiLineString','Polygon','MultiPolygon'),
      'renderers'=>array('svg2d','canvas3d','canvas4d','canvas-spatial'),
      'limits'=>array('features'=>50000,'coordinatePairs'=>500000,'rasterCells'=>1048576,'layers'=>32),
      'capabilities'=>array('spatialVisualization'=>true,'geospatialVisualization'=>true,'vectorGeometry'=>true,'rasterVisualization'=>true,'coordinateReferenceMetadata'=>true,'explicitViewport'=>true,'bboxSelection'=>true,'mixedRendererComposition'=>true),
      'boundaries'=>array('automaticCRSInference'=>false,'automaticReprojection'=>false,'automaticGeocoding'=>false,'automaticSpatialJoin'=>false,'topologyRepair'=>false,'rasterInterpolation'=>false,'rasterResampling'=>false,'nodataImputation'=>false,'networkBasemaps'=>false,'webgl'=>false,'arbitraryCode'=>false)
    ));}
    public static function health(){
      $required=array('backend/app/spatial_geospatial_raster_v0800.py','backend/tests/test_spatial_geospatial_raster_v0800.py','assets/js/modules/spatial-geospatial-raster-v0800.js','assets/js/modules/graph-studio-v0800.js','assets/css/sc-lab-spatial-geospatial-raster-v0800.css','contracts/spatial-crs-v0800.schema.json','contracts/spatial-vector-layer-v0800.schema.json','contracts/spatial-raster-v0800.schema.json','contracts/spatial-viewport-v0800.schema.json','contracts/spatial-figure-v0800.schema.json','contracts/figure-workspace-v0800.schema.json');$files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
      return rest_ensure_response(array(
        'ok'=>$ok,'status'=>$ok?'spatial-geospatial-raster-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'renderer'=>'canvas-spatial','rendererRegistry'=>array('svg2d','canvas3d','canvas4d','canvas-spatial'),
        'spatialVisualization'=>true,'geospatialVisualization'=>true,'vectorGeometry'=>true,'rasterVisualization'=>true,'coordinateReferenceMetadata'=>true,'explicitViewport'=>true,'bboxSelection'=>true,'mixedRendererComposition'=>true,
        'v0790LinkedViewsCompatibility'=>true,'v0780TimeParameterCompatibility'=>true,'v0770SceneCompatibility'=>true,'v0760AdaptiveCompatibility'=>true,'v0750DataBindingCompatibility'=>true,
        'automaticCRSInference'=>false,'automaticReprojection'=>false,'automaticGeocoding'=>false,'automaticSpatialJoin'=>false,'topologyRepair'=>false,'rasterInterpolation'=>false,'rasterResampling'=>false,'nodataImputation'=>false,'networkBasemaps'=>false,'webgl'=>false,'arbitraryCode'=>false,'files'=>$files,'time'=>gmdate('c')
      ));
    }
}
