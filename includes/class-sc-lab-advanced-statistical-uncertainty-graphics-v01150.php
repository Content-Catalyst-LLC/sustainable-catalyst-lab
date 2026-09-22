<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Advanced_Statistical_Uncertainty_Graphics_V01150 {
    const VERSION='0.115.0';
    const ENGINE_VERSION='3.1.0';
    const SCHEMA='sc-lab-advanced-statistical-uncertainty-graphics/0.115.0';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        $ns='sc-lab/v1/visualization/v01150';
        register_rest_route($ns,'/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/manifest',array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
        register_rest_route($ns,'/catalog',array('methods'=>'GET','callback'=>array(__CLASS__,'catalog'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative){ $path=SC_LAB_DIR.$relative; return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'schema'=>self::SCHEMA,'engineVersion'=>self::ENGINE_VERSION,'graphicTypeCount'=>16,'apiRouteCount'=>18,'publicationDesignSystem'=>'0.114.0','uncertaintyEngine'=>'0.82.0','explicitKdeBandwidth'=>true,'explicitIntervalSemantics'=>true,'explicitQqReferenceDistribution'=>true)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'graphics'=>array('histogram','ecdf','box','violin','raincloud','ridge','interval-ribbon','fan-chart','posterior-density','coefficient-forest','calibration-reliability','residual-diagnostics','qq','sensitivity','uncertainty-decomposition','coverage'),'sensitivityMethods'=>array('sobol','morris','tornado','ranked-effect'),'intervalSemantics'=>array('confidence','credible','prediction','bootstrap','custom'))); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'advanced-statistical-uncertainty-graphics-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'publicationDesignSystem'=>'0.114.0','uncertaintyEngine'=>'0.82.0','distributionGraphics'=>true,'fanCharts'=>true,'posteriorGraphics'=>true,'coefficientForests'=>true,'calibrationReliability'=>true,'residualDiagnostics'=>true,'qqPlots'=>true,'sensitivityGraphics'=>true,'uncertaintyDecomposition'=>true,'coverageGraphics'=>true,'statisticalSmallMultiples'=>true,'automaticKdeBandwidth'=>false,'automaticDistributionSelection'=>false,'automaticIntervalSemantics'=>false,'automaticSignificanceInference'=>false,'automaticCausalInference'=>false,'automaticScientificValidityCertification'=>false,'automaticTruthDetermination'=>false)); }
    public static function health(){
        $required=array('contracts/advanced-statistical-uncertainty-graphics-v01150.schema.json','contracts/advanced-statistical-uncertainty-graphics-policy-v01150.json','includes/class-sc-lab-advanced-statistical-uncertainty-graphics-v01150.php','assets/js/modules/advanced-statistical-uncertainty-graphics-v01150.js','assets/css/sc-lab-advanced-statistical-uncertainty-graphics-v01150.css');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'advanced-statistical-uncertainty-graphics-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'graphicTypeCount'=>16,'files'=>$files,'time'=>gmdate('c')));
    }
}
SC_Lab_Advanced_Statistical_Uncertainty_Graphics_V01150::init();
