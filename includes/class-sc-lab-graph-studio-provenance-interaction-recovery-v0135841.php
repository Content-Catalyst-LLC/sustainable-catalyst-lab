<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Provenance_Interaction_Recovery_V0135841 {
    const VERSION='0.135.8.4.1';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-provenance-interaction/v0135841/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-provenance-interaction/v0135841/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    private static function exists($p){ return is_file(SC_LAB_DIR.$p); }
    public static function health(){ return rest_ensure_response(array('ok'=>self::exists('assets/js/modules/graph-studio-provenance-interaction-recovery-v0135841.js')&&self::exists('assets/css/sc-lab-graph-studio-provenance-interaction-recovery-v0135841.css'),'version'=>self::VERSION,'delegatedInteraction'=>true,'programmaticLayoutClick'=>false,'recursiveRedrawGuard'=>true,'presentationStateOnly'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'renderer31Hosts'=>1,'primaryViewports'=>1,'provenanceExplorers'=>1,'layoutControls'=>3,'nodeSelectionDelegated'=>true,'layoutSwitchWithoutRedrawLoop'=>true,'legacyPrimaryOwners'=>0)); }
}
SC_Lab_Graph_Studio_Provenance_Interaction_Recovery_V0135841::init();
