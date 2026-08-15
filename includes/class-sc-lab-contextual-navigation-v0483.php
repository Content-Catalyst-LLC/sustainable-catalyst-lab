<?php
/** Sustainable Catalyst Lab v0.48.3 Contextual Navigation & Scientific Workspace Rail Reduction. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Contextual_Navigation_V0483 {
    const VERSION='0.48.3'; private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){register_rest_route('sc-lab/v1','/navigation/v0483/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));}
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function health(){
        $required=array('assets/js/modules/contextual-navigation-v0483.js','assets/css/sc-lab-contextual-navigation-v0483.css','templates/lab-app.php','assets/js/modules/presentation-runtime-v0482.js');$files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'contextual-navigation-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'primaryRailDestinations'=>6,'searchableToolsLauncher'=>true,'contextualSubnavigation'=>true,'desktopCollapsibleRail'=>true,'mobileDrawer'=>true,'documentWideMutationObserver'=>false,'threeApplicationCardRowPreserved'=>true,'graphStudioFrontDoorPreserved'=>true,'files'=>$files,'time'=>gmdate('c')));
    }
}
