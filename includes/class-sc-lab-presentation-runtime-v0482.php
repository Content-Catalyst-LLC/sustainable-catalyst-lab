<?php
/** Sustainable Catalyst Lab v0.48.2 UI Runtime Responsiveness & Event Loop Repair. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Presentation_Runtime_V0482 {
    const VERSION='0.48.2'; private static $initialized=false;
    public static function init(){if(self::$initialized){return;}self::$initialized=true;add_action('rest_api_init',array(__CLASS__,'routes'));}
    public static function routes(){register_rest_route('sc-lab/v1','/presentation/v0482/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));}
    private static function file_state($relative){$path=SC_LAB_DIR.$relative;return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null);}
    public static function health(){
        $required=array('assets/js/modules/presentation-runtime-v0482.js','assets/css/sc-lab-presentation-v0481.css','templates/lab-app.php','assets/js/modules/graph-studio-v0470.js','assets/js/modules/scientific-visualization-engine-v0440.js');$files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'runtime-responsive':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'documentWideMutationObserver'=>false,'idempotentOuterVersionSync'=>true,'renderScheduling'=>'requestAnimationFrame','projectRendering'=>'overview-only','threeApplicationCardRowPreserved'=>true,'graphStudioFrontDoor'=>true,'sharedVisualizationEngine'=>'0.44.0','files'=>$files,'time'=>gmdate('c')));
    }
}
