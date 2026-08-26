<?php
/** Sustainable Catalyst Lab v0.71.0 Advanced Scientific Visualization Front Door & 4D Projection. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Advanced_Visualization_Front_Door_V0710 {
    const VERSION = '0.71.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/visualization/v0710/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }
    private static function file_state($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return array('exists'=>is_file($path), 'sha256'=>is_file($path)?hash_file('sha256',$path):null);
    }
    public static function health() {
        $required = array(
            'assets/js/modules/advanced-visualization-front-door-v0710.js',
            'assets/css/sc-lab-advanced-visualization-front-door-v0710.css',
            'templates/lab-app.php',
            'assets/js/sc-lab-production-stability-v0266.js',
        );
        $files=array();$ok=true;
        foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array(
            'ok'=>$ok,
            'status'=>$ok?'advanced-visualization-ready':'incomplete',
            'version'=>self::VERSION,
            'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,
            'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,
            'browserRendered'=>true,
            'computeRequiredForFrontDoor'=>false,
            'dimensionsRepresented'=>4,
            'projection'=>'4D-to-3D projected response field',
            'layers'=>array('response-surface','vector-field','uncertainty-envelope','contours','tesseract-projection'),
            'interactiveControls'=>array('w-hyperslice','xw-rotation','yw-rotation','4d-sweep'),
            'transientComputeRecoveryNonBlocking'=>true,
            'scientificBoundary'=>'Illustrative landing visualization only; it is not presented as measured or model-derived project data.',
            'files'=>$files,
            'time'=>gmdate('c'),
        ));
    }
}
