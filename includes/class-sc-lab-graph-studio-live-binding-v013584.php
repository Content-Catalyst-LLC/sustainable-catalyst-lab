<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Live_Binding_V013584 {
    const VERSION='0.135.8.4';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-live-binding/v013584/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-live-binding/v013584/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    private static function exists($p){ return is_file(SC_LAB_DIR.$p); }
    public static function health(){ return rest_ensure_response(array('ok'=>self::exists('assets/js/modules/graph-studio-live-binding-v013584.js')&&self::exists('assets/css/sc-lab-graph-studio-live-binding-v013584.css'),'version'=>self::VERSION,'liveProjectBinding'=>true,'projectStatePersistence'=>true,'advancedProvenanceExploration'=>true,'presentationStateOnly'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'renderer31Hosts'=>1,'primaryViewports'=>1,'liveBindingBars'=>1,'legacyPrimaryOwners'=>0,'projectStoreSubscription'=>true)); }
}
SC_Lab_Graph_Studio_Live_Binding_V013584::init();
