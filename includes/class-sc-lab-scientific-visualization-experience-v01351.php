<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Visualization_Experience_V01351 {
    const VERSION='0.135.1';
    const ENGINE_VERSION='16.1.0';
    const SCHEMA='sc-lab-scientific-visualization-experience/0.135.1';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){ $ns='sc-lab/v1/analysis/v01351'; foreach(array('health','manifest','schema','catalog') as $r){ register_rest_route($ns,'/'.$r,array('methods'=>'GET','callback'=>array(__CLASS__,$r),'permission_callback'=>'__return_true')); } }
    private static function state($r){ $p=SC_LAB_DIR.$r; return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null); }
    public static function schema(){ return rest_ensure_response(array('ok'=>true,'schema'=>self::SCHEMA,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'viewModeCount'=>4,'apiRouteCount'=>32)); }
    public static function catalog(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'panelFamilyCount'=>12,'capabilityFamilyCount'=>12,'presentationProfileCount'=>5,'fabricatedScientificValues'=>false,'automaticScientificInterpretation'=>false,'automaticCoreSubmission'=>false)); }
    public static function manifest(){ return rest_ensure_response(array('ok'=>true,'status'=>'scientific-visualization-experience-ready','version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'graphStudioOverhaul'=>true,'multiPanelAnalysisCanvas'=>true,'underTheHoodGraphics'=>true,'dataAwarePanels'=>true,'missingScientificObjectsRemainExplicit'=>true,'v01140DesignSystemBridge'=>true,'v01160LinkedViewsBridge'=>true,'v01190LayoutIntelligenceBridge'=>true,'v01330DiagnosticReferenceBridge'=>true,'v01340EvidenceReferenceBridge'=>true,'v01350CompetingModelReferenceBridge'=>true,'automaticScientificInterpretation'=>false,'automaticEvidencePromotion'=>false,'automaticCoreSubmission'=>false)); }
    public static function health(){
        $req=array(
            'contracts/scientific-visualization-experience-v01351.schema.json',
            'contracts/scientific-visualization-experience-policy-v01351.json',
            'includes/class-sc-lab-scientific-visualization-experience-v01351.php',
            'assets/js/modules/scientific-visualization-experience-v01351.js',
            'assets/css/sc-lab-scientific-visualization-experience-v01351.css'
        );
        $files=array(); $ok=true;
        foreach($req as $r){ $files[$r]=self::state($r); if(empty($files[$r]['exists']))$ok=false; }
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'scientific-visualization-experience-ready':'incomplete','version'=>self::VERSION,'labReleaseVersion'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:self::VERSION,'engineVersion'=>self::ENGINE_VERSION,'panelFamilyCount'=>12,'capabilityFamilyCount'=>12,'presentationProfileCount'=>5,'apiRouteCount'=>32,'files'=>$files,'fabricatedScientificValues'=>false,'automaticScientificInterpretation'=>false,'automaticScientificValidityCertification'=>false,'automaticCoreSubmission'=>false,'time'=>gmdate('c')));
    }
}
SC_Lab_Scientific_Visualization_Experience_V01351::init();
