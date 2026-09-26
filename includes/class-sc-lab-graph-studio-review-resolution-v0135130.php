<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Review_Resolution_V0135130 {
    const VERSION='0.135.13.0';
    public static function init(){ add_action('rest_api_init', array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-review-resolution/v0135130/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-review-resolution/v0135130/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    public static function health(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'reviewResolution'=>true,'appendOnlyDecisionLineage'=>true,'revisionActionsExplicit'=>true,'projectPersistenceExplicit'=>true,'crossWorkspaceResolutionHandoff'=>true)); }
    public static function acceptance(){ return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'fullGraphRedrawForResolution'=>false,'annotationMutation'=>false,'truthRanking'=>false,'causalInference'=>false,'evidenceWeightInference'=>false,'scientificPreference'=>false,'browserAcceptanceRequired'=>true)); }
}
SC_Lab_Graph_Studio_Review_Resolution_V0135130::init();
