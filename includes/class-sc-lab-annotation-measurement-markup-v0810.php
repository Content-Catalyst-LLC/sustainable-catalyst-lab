<?php
/** Sustainable Catalyst Lab v0.81.0 — Annotation, Measurement & Scientific Markup. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Annotation_Measurement_Markup_V0810 {
    const VERSION='0.81.0'; const ENGINE_VERSION='2.8.0'; private static $initialized=false;
    public static function init(){ if(self::$initialized){return;} self::$initialized=true; add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
      register_rest_route('sc-lab/v1','/visualization/v0810/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
      register_rest_route('sc-lab/v1','/visualization/v0810/schema',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($r){$p=SC_LAB_DIR.ltrim((string)$r,'/');return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
    public static function schema(){return rest_ensure_response(array(
      'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'rendererOverlay'=>'scientific-markup',
      'annotationSchema'=>'sc-lab-scientific-annotation/0.81.0','measurementSchema'=>'sc-lab-scientific-measurement/0.81.0','markupLayerSchema'=>'sc-lab-scientific-markup-layer/0.81.0','figureSchema'=>'sc-lab-marked-scientific-figure/0.81.0','workspaceSchema'=>'sc-lab-figure-workspace/0.81.0',
      'annotationTypes'=>array('point','label','arrow','line','polyline','region','threshold-x','threshold-y'),'measurementTypes'=>array('coordinate','distance','polyline-length','angle','area'),
      'coordinateSpaces'=>array('screen-normalized','data-2d','data-3d','state-4d','projected','geographic'),
      'renderers'=>array('svg2d','canvas3d','canvas4d','canvas-spatial'),'overlays'=>array('scientific-markup'),
      'limits'=>array('annotationsPerLayer'=>2000,'measurementsPerLayer'=>2000,'markupLayers'=>32,'pointsPerMark'=>2000),
      'capabilities'=>array('scientificAnnotation'=>true,'scientificMeasurement'=>true,'scientificMarkupLayers'=>true,'coordinateMeasurement'=>true,'distanceMeasurement'=>true,'polylineLengthMeasurement'=>true,'angleMeasurement'=>true,'areaMeasurement'=>true,'annotationProvenance'=>true,'baseFigurePreservation'=>true),
      'boundaries'=>array('annotationIsObservation'=>false,'automaticObservationCreation'=>false,'automaticScientificInterpretation'=>false,'automaticUnitConversion'=>false,'automaticGeodesicMeasurement'=>false,'automaticGeometrySnapping'=>false,'automaticUncertaintyInference'=>false,'arbitraryCode'=>false)
    ));}
    public static function health(){
      $required=array('backend/app/annotation_measurement_markup_v0810.py','backend/tests/test_annotation_measurement_markup_v0810.py','assets/js/modules/scientific-markup-v0810.js','assets/js/modules/graph-studio-v0810.js','assets/css/sc-lab-scientific-markup-v0810.css','contracts/scientific-annotation-v0810.schema.json','contracts/scientific-measurement-v0810.schema.json','contracts/scientific-markup-layer-v0810.schema.json','contracts/marked-scientific-figure-v0810.schema.json','contracts/figure-workspace-v0810.schema.json');$files=array();$ok=true;foreach($required as $r){$files[$r]=self::file_state($r);if(empty($files[$r]['exists'])){$ok=false;}}
      return rest_ensure_response(array(
        'ok'=>$ok,'status'=>$ok?'annotation-measurement-scientific-markup-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_VERSION')?SC_LAB_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'rendererOverlay'=>'scientific-markup',
        'scientificAnnotation'=>true,'scientificMeasurement'=>true,'scientificMarkupLayers'=>true,'pointAnnotation'=>true,'lineAnnotation'=>true,'regionAnnotation'=>true,'thresholdAnnotation'=>true,'coordinateMeasurement'=>true,'distanceMeasurement'=>true,'polylineLengthMeasurement'=>true,'angleMeasurement'=>true,'areaMeasurement'=>true,'declaredUnits'=>true,'annotationProvenance'=>true,'baseFigurePreservation'=>true,
        'v0800SpatialCompatibility'=>true,'v0790LinkedViewsCompatibility'=>true,'v0780TimeParameterCompatibility'=>true,'v0770SceneCompatibility'=>true,'v0760AdaptiveCompatibility'=>true,'v0750DataBindingCompatibility'=>true,
        'annotationIsObservation'=>false,'automaticObservationCreation'=>false,'automaticScientificInterpretation'=>false,'automaticUnitConversion'=>false,'automaticGeodesicMeasurement'=>false,'automaticGeometrySnapping'=>false,'automaticUncertaintyInference'=>false,'arbitraryCode'=>false,'files'=>$files
      ));
    }
}
