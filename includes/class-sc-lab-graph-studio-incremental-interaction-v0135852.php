<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Incremental_Interaction_V0135852 {
    const VERSION='0.135.8.5.2';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-incremental-interaction/v0135852/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-incremental-interaction/v0135852/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'incrementalRendering'=>true,'relationshipFiltering'=>true,'selectorStable'=>true,'projectPersistenceDebounceMs'=>220)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'fullRedrawForOrdinaryInteraction'=>false,'layoutGeometryOnly'=>true,'traversalVisibilityOnly'=>true,'selectionInspectorOnly'=>true,'relationshipSelectorStable'=>true)); }
}
SC_Lab_Graph_Studio_Incremental_Interaction_V0135852::init();
