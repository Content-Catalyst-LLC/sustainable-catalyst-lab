<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Interactive_Scientific_Dashboards_V01160 {
    const VERSION='0.116.0';
    const ENGINE_VERSION='3.2.0';
    const SCHEMA='sc-lab-interactive-scientific-dashboards/0.116.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/visualization/v01160';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/catalog',array('methods'=>'GET','callback'=>array(__CLASS__,'catalog'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=SC_LAB_DIR.$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'schema'=>self::SCHEMA,'engineVersion'=>self::ENGINE_VERSION,'panelLimit'=>48,'linkLimit'=>256,'controlLimit'=>64,'apiRouteCount'=>18,'publicationDesignSystem'=>'0.114.0','statisticalGraphics'=>'0.115.0','linkedViewsEngine'=>'0.79.0')); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'interactionChannels'=>array('selection','brush','filter','cursor','state-axis','parameter','time-window'),'controlTypes'=>array('category-filter','range-filter','time-window','parameter','toggle','search'),'renderers'=>array('svg2d','canvas3d','canvas4d','webgl2','webgpu'),'exportModes'=>array('dashboard-view','figure-set','publication-sheet','state-bundle'))); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'interactive-scientific-dashboards-small-multiples-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'responsiveDashboards'=>true,'scientificSmallMultiples'=>true,'linkedBrushing'=>true,'linkedSelection'=>true,'linkedFiltering'=>true,'declaredScaleSynchronization'=>true,'stateSnapshots'=>true,'restorePlans'=>true,'provenanceTracing'=>true,'accessibilityAuditing'=>true,'publicationExportPlanning'=>true,'automaticLinkInference'=>false,'automaticScaleDomainInference'=>false,'automaticCrossDatasetJoin'=>false,'automaticQueryExecution'=>false,'automaticStatePersistence'=>false,'automaticCoreSubmission'=>false,'automaticScientificValidityCertification'=>false,'automaticTruthDetermination'=>false)); }
    public static function health(){
        $required=array('contracts/interactive-scientific-dashboards-v01160.schema.json','contracts/interactive-scientific-dashboards-policy-v01160.json','includes/class-sc-lab-interactive-scientific-dashboards-v01160.php','assets/js/modules/interactive-scientific-dashboards-v01160.js','assets/css/sc-lab-interactive-scientific-dashboards-v01160.css');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'interactive-scientific-dashboards-small-multiples-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'panelLimit'=>48,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Interactive_Scientific_Dashboards_V01160::init();
