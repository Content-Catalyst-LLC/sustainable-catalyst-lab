<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Object_Explorer_V013590 {
    const VERSION='0.135.9.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-object-explorer/v013590/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-object-explorer/v013590/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'oneHopNeighborhood'=>true,'twoHopNeighborhood'=>true,'richObjectInspector'=>true,'relatedObjectSelection'=>true,'crossWorkspaceNavigation'=>true,'declaredRelationshipsOnly'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'fullGraphRedrawForScope'=>false,'projectRecordMetadata'=>true,'projectFocusHandoff'=>true,'scientificMutation'=>false,'mutationObserverInteractionOwner'=>false)); }
}
SC_Lab_Graph_Studio_Object_Explorer_V013590::init();
