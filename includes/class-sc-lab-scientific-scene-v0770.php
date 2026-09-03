<?php
/** Sustainable Catalyst Lab v0.77.0 3D Scientific Scene Engine. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Scene_V0770 {
    const VERSION = '0.77.0';
    const ENGINE_VERSION = '2.4.0';
    const RENDERER = 'canvas3d';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/visualization/v0770/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/visualization/v0770/schema', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'schema'),
            'permission_callback' => '__return_true',
        ));
    }

    private static function file_state($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return array('exists' => is_file($path), 'sha256' => is_file($path) ? hash_file('sha256', $path) : null);
    }

    public static function schema() {
        return rest_ensure_response(array(
            'ok' => true,
            'version' => self::VERSION,
            'engineVersion' => self::ENGINE_VERSION,
            'renderer' => self::RENDERER,
            'sceneSchema' => 'sc-lab-scientific-scene/0.77.0',
            'cameraSchema' => 'sc-lab-scientific-scene-camera/0.77.0',
            'objectSchema' => 'sc-lab-scientific-scene-object/0.77.0',
            'specSchema' => 'sc-lab-scientific-visualization/0.77.0',
            'figureSchema' => 'sc-lab-scientific-figure/0.77.0',
            'workspaceSchema' => 'sc-lab-figure-workspace/0.77.0',
            'objectTypes' => array('point-cloud', 'polyline', 'line-segments', 'mesh', 'vectors'),
            'cameraProjections' => array('perspective', 'orthographic'),
            'limits' => array('sceneObjects' => 32, 'verticesPerObject' => 20000, 'totalCoordinates' => 25000, 'trianglesPerMesh' => 30000, 'datasetRenderRows' => 5000),
            'renderers' => array(
                'svg2d' => array('compatibility' => '0.74.0'),
                'canvas3d' => array('version' => '0.77.0', 'native3d' => true),
                'canvas4d' => array('compatibility' => '0.75.0'),
            ),
            'capabilities' => array(
                'scientificScene3d' => true,
                'pointCloud3d' => true,
                'polyline3d' => true,
                'mesh3d' => true,
                'vectorField3d' => true,
                'perspectiveCamera' => true,
                'orthographicCamera' => true,
                'orbitInteraction' => true,
                'depthSorting' => true,
                'clippingIntent' => true,
                'v0760AdaptiveCompatibility' => true,
                'v0750TransformationCompatibility' => true,
            ),
            'boundaries' => array(
                'webgl' => false,
                'depthBuffer' => false,
                'automaticTriangulation' => false,
                'surfaceInterpolation' => false,
                'hiddenSurfaceGuarantee' => false,
                'arbitraryCode' => false,
            ),
        ));
    }

    public static function health() {
        $required = array(
            'backend/app/scientific_scene_v0770.py',
            'backend/tests/test_scientific_scene_v0770.py',
            'assets/js/modules/scientific-scene-engine-v0770.js',
            'assets/js/modules/graph-studio-v0770.js',
            'assets/css/sc-lab-scientific-scene-v0770.css',
            'contracts/scientific-scene-v0770.schema.json',
            'contracts/scientific-scene-camera-v0770.schema.json',
            'contracts/scientific-scene-object-v0770.schema.json',
            'contracts/scientific-visualization-v0770.schema.json',
            'contracts/scientific-figure-v0770.schema.json',
            'contracts/figure-workspace-v0770.schema.json'
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? 'scientific-3d-scene-ready' : 'incomplete',
            'version' => self::VERSION,
            'release' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'platformVersion' => defined('SC_LAB_PLATFORM_VERSION') ? SC_LAB_PLATFORM_VERSION : null,
            'engineVersion' => self::ENGINE_VERSION,
            'renderer' => self::RENDERER,
            'rendererRegistry' => array('svg2d', 'canvas3d', 'canvas4d'),
            'scientificScene3d' => true,
            'pointCloud3d' => true,
            'polyline3d' => true,
            'mesh3d' => true,
            'vectorField3d' => true,
            'perspectiveCamera' => true,
            'orthographicCamera' => true,
            'orbitInteraction' => true,
            'depthSorting' => true,
            'clippingIntent' => true,
            'v0760AdaptiveCompatibility' => true,
            'v0750DataBindingCompatibility' => true,
            'advanced2dCompatibility' => true,
            'canvas4dCompatibility' => true,
            'webgl' => false,
            'automaticTriangulation' => false,
            'surfaceInterpolation' => false,
            'arbitraryCode' => false,
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}
