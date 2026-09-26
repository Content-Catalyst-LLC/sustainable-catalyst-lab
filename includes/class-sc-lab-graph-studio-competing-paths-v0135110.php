<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Competing_Paths_V0135110 {
    const VERSION='0.135.11.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-competing-paths/v0135110/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-competing-paths/v0135110/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'multipleDeclaredPaths'=>true,'declaredEvidenceContextOnly'=>true,'competingPathComparison'=>true,'crossWorkspaceComparisonHandoff'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'fullGraphRedrawForPathSelection'=>false,'truthRanking'=>false,'causalInference'=>false,'scientificPreference'=>false,'browserAcceptanceRequired'=>true)); }
}
SC_Lab_Graph_Studio_Competing_Paths_V0135110::init();
