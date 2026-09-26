<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Path_Analysis_V0135100 {
    const VERSION='0.135.10.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-path-analysis/v0135100/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-path-analysis/v0135100/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'directedPathMode'=>true,'structuralPathMode'=>true,'boundedShortestPath'=>true,'multiObjectComparison'=>true,'researchContextHandoff'=>true,'declaredRelationshipsOnly'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'fullGraphRedrawForPath'=>false,'scientificMutation'=>false,'causalInference'=>false,'semanticInference'=>false,'browserAcceptanceRequired'=>true)); }
}
SC_Lab_Graph_Studio_Path_Analysis_V0135100::init();
