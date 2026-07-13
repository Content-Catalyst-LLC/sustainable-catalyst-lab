<?php
/**
 * Biochemistry production activation and interface reliability.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biochemistry_Production_V0211 {
    const VERSION = '0.21.1';
    const RUNTIME_HANDLE =
        'sc-lab-biochemistry-production-v0211';
    const STYLE_HANDLE =
        'sc-lab-biochemistry-production-v0211-style';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            50000
        );

        add_action(
            'rest_api_init',
            array(__CLASS__, 'register_routes')
        );
    }

    private static function asset_url($relative) {
        if (defined('SC_LAB_URL')) {
            return trailingslashit(
                (string) constant('SC_LAB_URL')
            )
                . 'assets/'
                . ltrim((string) $relative, '/');
        }

        $root_file = dirname(__DIR__)
            . '/sustainable-catalyst-lab.php';

        return plugin_dir_url($root_file)
            . 'assets/'
            . ltrim((string) $relative, '/');
    }

    private static function asset_path($relative) {
        return dirname(__DIR__)
            . '/assets/'
            . ltrim((string) $relative, '/');
    }

    private static function asset_version($relative) {
        $path = self::asset_path($relative);

        if (is_file($path)) {
            return self::VERSION . '.' . filemtime($path);
        }

        return self::VERSION;
    }

    public static function enqueue() {
        if (is_admin()) {
            return;
        }

        if (
            class_exists(
                'SC_Lab_Biochemistry_Molecular_Analysis'
            )
            && is_callable(
                array(
                    'SC_Lab_Biochemistry_Molecular_Analysis',
                    'enqueue_assets',
                )
            )
        ) {
            SC_Lab_Biochemistry_Molecular_Analysis::
                enqueue_assets();
        }

        $style =
            'css/sc-lab-biochemistry-production-v0211.css';
        $runtime =
            'js/modules/biochemistry-production-v0211.js';

        wp_enqueue_style(
            self::STYLE_HANDLE,
            self::asset_url($style),
            array(),
            self::asset_version($style)
        );

        wp_enqueue_script(
            self::RUNTIME_HANDLE,
            self::asset_url($runtime),
            array(
                'sc-lab-biochemistry-molecular-analysis-v0210',
            ),
            self::asset_version($runtime),
            true
        );

        wp_localize_script(
            self::RUNTIME_HANDLE,
            'SCLabBiochemistryProductionConfig',
            array(
                'version' => self::VERSION,
                'healthUrl' => rest_url(
                    'sc-lab/v1/compute/biochemistry/health'
                ),
                'moduleId' =>
                    'biochemistry-molecular-analysis',
                'debug' => defined('WP_DEBUG') && WP_DEBUG,
            )
        );
    }

    public static function register_routes() {
        register_rest_route(
            'sc-lab/v1',
            '/compute/biochemistry/health',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'health_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function health_response() {
        $catalog_path = dirname(__DIR__)
            . '/contracts/'
            . 'biochemistry-molecular-analysis-methods.json';

        $catalog = array();

        if (is_file($catalog_path)) {
            $decoded = json_decode(
                file_get_contents($catalog_path),
                true
            );

            if (is_array($decoded)) {
                $catalog = $decoded;
            }
        }

        $module_path = self::asset_path(
            'js/modules/biochemistry-molecular-analysis.js'
        );
        $runtime_path = self::asset_path(
            'js/modules/biochemistry-production-v0211.js'
        );
        $style_path = self::asset_path(
            'css/sc-lab-biochemistry-production-v0211.css'
        );

        $method_count = isset($catalog['methods'])
            && is_array($catalog['methods'])
            ? count($catalog['methods'])
            : 0;

        $benchmark_count = isset($catalog['benchmarks'])
            && is_array($catalog['benchmarks'])
            ? count($catalog['benchmarks'])
            : 0;

        $assets_ready = is_file($module_path)
            && is_file($runtime_path)
            && is_file($style_path);

        $ready = $assets_ready
            && $method_count === 48
            && $benchmark_count === 48;

        return rest_ensure_response(
            array(
                'ok' => $ready,
                'status' => $ready
                    ? 'ready'
                    : 'degraded',
                'release' => self::VERSION,
                'analysisEngine' => '0.21.0',
                'catalogVersion' =>
                    isset($catalog['version'])
                        ? (string) $catalog['version']
                        : null,
                'methodCount' => $method_count,
                'benchmarkCount' => $benchmark_count,
                'assets' => array(
                    'module' => is_file($module_path),
                    'runtime' => is_file($runtime_path),
                    'style' => is_file($style_path),
                ),
                'routes' => array(
                    'methods' => rest_url(
                        'sc-lab/v1/compute/biochemistry/methods'
                    ),
                    'run' => rest_url(
                        'sc-lab/v1/compute/biochemistry/run'
                    ),
                    'health' => rest_url(
                        'sc-lab/v1/compute/biochemistry/health'
                    ),
                ),
            )
        );
    }
}

SC_Lab_Biochemistry_Production_V0211::boot();
