<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Provenance_Authority_V0135851 {
    const VERSION='0.135.8.5.1';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-provenance-authority/v0135851/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-provenance-authority/v0135851/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'provenance_owner'=>'0.135.8.5','legacy_interaction_enabled'=>false,'legacy_recovery_enqueued'=>false,'browser_certification_required'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'single_provenance_owner'=>true,'legacy_observer_attached'=>false,'legacy_interaction_handlers'=>0,'observer_driven_renders'=>0,'chromium_acceptance_required'=>true)); }
}
SC_Lab_Graph_Studio_Provenance_Authority_V0135851::init();
