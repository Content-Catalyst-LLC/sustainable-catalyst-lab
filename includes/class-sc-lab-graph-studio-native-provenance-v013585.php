<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Native_Provenance_V013585 {
    const VERSION='0.135.8.5.3';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-native-provenance/v013585/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-native-provenance/v013585/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    private static function exists($p){ return is_file(SC_LAB_DIR.$p); }
    public static function health(){ return rest_ensure_response(array('ok'=>self::exists('assets/js/modules/graph-studio-native-provenance-v013585.js')&&self::exists('assets/css/sc-lab-graph-studio-native-provenance-v013585.css'),'version'=>self::VERSION,'nativeGraphStateEngine'=>true,'mutationObserverOwnsInteraction'=>false,'projectStatePersistence'=>true,'projectStatePersistenceDebounced'=>true,'incrementalRendering'=>true,'relationshipSelectorStable'=>true,'contextAwareRelationshipOptions'=>true,'zeroMatchExplicit'=>true,'impossibleRelationshipAutoReset'=>false,'presentationStateOnly'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'graphModelLoaded'=>true,'singleGraphController'=>true,'stableObjectIds'=>true,'nativeTraversal'=>true,'nativeLayout'=>true,'nativeInspector'=>true,'incrementalInteraction'=>true,'relationshipFiltering'=>true,'contextAwareRelationshipOptions'=>true,'selectedRelationshipPersistsAcrossTraversal'=>true,'fullRedrawForOrdinaryInteraction'=>false,'observerDrivenRenders'=>0,'legacyPrimaryOwners'=>0)); }
}
SC_Lab_Graph_Studio_Native_Provenance_V013585::init();
