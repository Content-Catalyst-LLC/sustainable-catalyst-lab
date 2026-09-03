<?php
/** Sustainable Catalyst Lab v0.78.0 — 4D, Time & Parameter-Space Visualization. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Time_Parameter_Space_V0780 {
    const VERSION = '0.78.0';
    const ENGINE_VERSION = '2.5.0';
    const RENDERER = 'canvas4d';
    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/visualization/v0780/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/visualization/v0780/schema', array(
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
            'stateSpaceSchema' => 'sc-lab-4d-state-space/0.78.0',
            'axisSchema' => 'sc-lab-state-axis/0.78.0',
            'projectionSchema' => 'sc-lab-4d-projection/0.78.0',
            'specSchema' => 'sc-lab-scientific-visualization/0.78.0',
            'figureSchema' => 'sc-lab-scientific-figure/0.78.0',
            'workspaceSchema' => 'sc-lab-figure-workspace/0.78.0',
            'modes' => array('4d-points', 'time-sequence', 'parameter-sweep'),
            'axisKinds' => array('dimension', 'parameter', 'time'),
            'timeScales' => array('index', 'elapsed', 'timestamp'),
            'rotationPlanes' => array('xw', 'yw', 'zw'),
            'limits' => array('backendSourceRows' => 250000, 'browserInlineRows' => 5000, 'renderPoints' => 5000, 'defaultRenderPoints' => 2000, 'observedStates' => 2000),
            'capabilities' => array(
                'fourDimensionalProjection' => true,
                'timeStatePlayback' => true,
                'parameterSweep' => true,
                'hyperslicing' => true,
                'discreteScrubbing' => true,
                'observedStatePlayback' => true,
                'v0770SceneCompatibility' => true,
                'v0760AdaptiveCompatibility' => true,
                'v0750TransformationCompatibility' => true,
            ),
            'boundaries' => array(
                'syntheticFrames' => false,
                'temporalInterpolation' => false,
                'parameterInterpolation' => false,
                'automaticTrajectories' => false,
                'surfaceInterpolation' => false,
                'forecasting' => false,
                'arbitraryCode' => false,
            ),
        ));
    }

    public static function health() {
        $required = array(
            'backend/app/time_parameter_space_v0780.py',
            'backend/tests/test_time_parameter_space_v0780.py',
            'assets/js/modules/time-parameter-space-v0780.js',
            'assets/js/modules/graph-studio-v0780.js',
            'assets/css/sc-lab-time-parameter-space-v0780.css',
            'contracts/4d-state-space-v0780.schema.json',
            'contracts/state-axis-v0780.schema.json',
            'contracts/4d-projection-v0780.schema.json',
            'contracts/scientific-visualization-v0780.schema.json',
            'contracts/scientific-figure-v0780.schema.json',
            'contracts/figure-workspace-v0780.schema.json'
        );
        $files = array(); $ok = true;
        foreach ($required as $relative) {
            $files[$relative] = self::file_state($relative);
            if (empty($files[$relative]['exists'])) { $ok = false; }
        }
        return rest_ensure_response(array(
            'ok' => $ok,
            'status' => $ok ? '4d-time-parameter-space-ready' : 'incomplete',
            'version' => self::VERSION,
            'release' => defined('SC_LAB_RELEASE_VERSION') ? SC_LAB_RELEASE_VERSION : null,
            'platformVersion' => defined('SC_LAB_PLATFORM_VERSION') ? SC_LAB_PLATFORM_VERSION : null,
            'engineVersion' => self::ENGINE_VERSION,
            'renderer' => self::RENDERER,
            'rendererRegistry' => array('svg2d', 'canvas3d', 'canvas4d'),
            'fourDimensionalProjection' => true,
            'timeStatePlayback' => true,
            'parameterSweep' => true,
            'hyperslicing' => true,
            'discreteScrubbing' => true,
            'observedStatePlayback' => true,
            'v0770SceneCompatibility' => true,
            'v0760AdaptiveCompatibility' => true,
            'v0750DataBindingCompatibility' => true,
            'advanced2dCompatibility' => true,
            'canvas3dCompatibility' => true,
            'syntheticFrames' => false,
            'temporalInterpolation' => false,
            'parameterInterpolation' => false,
            'surfaceInterpolation' => false,
            'forecasting' => false,
            'arbitraryCode' => false,
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}
