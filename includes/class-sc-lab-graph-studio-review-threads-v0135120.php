<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Review_Threads_V0135120 {
    const VERSION='0.135.12.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-review-threads/v0135120/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-review-threads/v0135120/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'reviewThread'=>true,'pathAnnotations'=>true,'explicitClaimLinkage'=>true,'projectPersistenceExplicit'=>true,'crossWorkspaceReviewHandoff'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'fullGraphRedrawForAnnotation'=>false,'truthRanking'=>false,'causalInference'=>false,'evidenceWeightInference'=>false,'browserAcceptanceRequired'=>true)); }
}
SC_Lab_Graph_Studio_Review_Threads_V0135120::init();
