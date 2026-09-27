
<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Research_Program_Intelligence_V01380 {
    const VERSION='0.138.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/research-program-intelligence/v01380/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/research-program-intelligence/v01380/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'crossStudyResearchProgramIntelligence'=>true,'programLivingAnalysis'=>true,'sharedResearchObjectIndex'=>true,'backwardCompatibleV01370'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'declaredStudyRelationshipsOnly'=>true,'declaredDependenciesOnly'=>true,'automaticScientificValidity'=>false,'automaticConsensus'=>false,'truthRanking'=>false)); }
}
SC_Lab_Research_Program_Intelligence_V01380::init();
