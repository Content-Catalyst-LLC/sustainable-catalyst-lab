<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Visualization_Design_System_V01140 {
    const VERSION='0.114.0';
    const ENGINE_VERSION='3.0.0';
    const SCHEMA='sc-lab-scientific-visualization-design-system/0.114.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/visualization/v01140';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/tokens',array('methods'=>'GET','callback'=>array(__CLASS__,'tokens'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=SC_LAB_DIR.$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'schema'=>self::SCHEMA,'engineVersion'=>self::ENGINE_VERSION,'profileCount'=>6,'semanticRoleCount'=>10,'uncertaintyStyleCount'=>5,'annotationTypeCount'=>9,'vectorFirst'=>true,'responsiveComposition'=>true,'accessibilityWithoutColor'=>true)); }
    public static function tokens(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'typography'=>array('titlePx'=>18,'subtitlePx'=>12,'axisTitlePx'=>11,'tickPx'=>10,'legendPx'=>10,'annotationPx'=>10,'captionPx'=>10,'sourcePx'=>9),'geometry'=>array('seriesStrokePx'=>2,'focusStrokePx'=>3,'markerPx'=>5),'principles'=>array('data-first','vector-first','semantic-encoding','uncertainty-first','annotation-with-evidence','small-multiple-consistency','responsive-composition','accessible-without-color','provenance-visible','publication-exportable'))); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'scientific-visualization-design-system-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'publicationGradeRendering'=>true,'vectorFirstExports'=>true,'semanticEncoding'=>true,'uncertaintyFirst'=>true,'smallMultiples'=>true,'responsiveComposition'=>true,'accessibilityWithoutColor'=>true,'provenanceVisible'=>true,'coreVisualBridgeCompatible'=>'0.109.0','automaticCoreSubmission'=>false,'automaticScientificValidityCertification'=>false,'automaticClaimInference'=>false,'automaticUncertaintyInference'=>false,'automaticTruthDetermination'=>false)); }
    public static function health(){
        $required=array('contracts/scientific-visualization-design-system-v01140.schema.json','contracts/scientific-visualization-design-system-policy-v01140.json','includes/class-sc-lab-scientific-visualization-design-system-v01140.php','assets/js/modules/scientific-visualization-design-system-v01140.js','assets/css/sc-lab-scientific-visualization-design-system-v01140.css');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-visualization-design-system-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'publicationGradeRendering'=>true,'vectorFirst'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Scientific_Visualization_Design_System_V01140::init();
