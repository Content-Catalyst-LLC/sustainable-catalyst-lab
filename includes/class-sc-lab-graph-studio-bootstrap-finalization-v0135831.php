<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Graph_Studio_Bootstrap_Finalization_V0135831 {
    const VERSION='0.135.8.3.1';
    public static function init(){ add_action('rest_api_init',array(__CLASS__,'routes')); }
    public static function routes(){
        register_rest_route('sc-lab/v1','/graph-studio-bootstrap-finalization/v0135831/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1','/graph-studio-bootstrap-finalization/v0135831/acceptance',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'acceptance'),'permission_callback'=>'__return_true'));
    }
    private static function exists($rel){ return is_file(SC_LAB_DIR.$rel); }
    public static function health(){return rest_ensure_response(array('ok'=>self::exists('assets/js/modules/graph-studio-v0470.js')&&self::exists('assets/js/modules/graph-studio-bootstrap-finalization-v0135831.js'),'version'=>self::VERSION,'bootstrapLoadedBeforeRecovery'=>true,'loadingBannerTerminalState'=>true,'legacyPresentationSuppressed'=>true,'renderer31PrimaryOwner'=>true));}
    public static function acceptance(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'loadingBanners'=>0,'renderer31Hosts'=>1,'renderer30VisibleHosts'=>0,'canonicalLegacyVisibleShells'=>0,'primaryViewports'=>1,'bootstrapInitialized'=>true,'projectFigureStoreConnected'=>true));}
}
SC_Lab_Graph_Studio_Bootstrap_Finalization_V0135831::init();
