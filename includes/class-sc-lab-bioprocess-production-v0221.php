<?php
/**
 * Bioprocess production activation and reliability.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Bioprocess_Production_V0221 {
    const VERSION = '0.22.1';
    const ENGINE_VERSION = '0.22.0';
    const SCRIPT_HANDLE =
        'sc-lab-bioprocess-production-v0221';
    const STYLE_HANDLE =
        'sc-lab-bioprocess-production-v0221-style';
    const NAMESPACE = 'sc-lab/v1';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            60040
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

        return plugin_dir_url(
            dirname(__DIR__)
            . '/sustainable-catalyst-lab.php'
        )
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

        return is_file($path)
            ? self::VERSION . '.' . filemtime($path)
            : self::VERSION;
    }

    public static function enqueue() {
        if (is_admin()) {
            return;
        }

        if (
            class_exists(
                'SC_Lab_Biotechnology_Bioprocess_Engineering_V0220'
            )
            && is_callable(
                array(
                    'SC_Lab_Biotechnology_Bioprocess_Engineering_V0220',
                    'enqueue',
                )
            )
        ) {
            SC_Lab_Biotechnology_Bioprocess_Engineering_V0220::
                enqueue();
        }

        $style =
            'css/'
            . 'sc-lab-bioprocess-production-v0221.css';
        $script =
            'js/modules/'
            . 'bioprocess-production-v0221.js';

        wp_enqueue_style(
            self::STYLE_HANDLE,
            self::asset_url($style),
            array(
                'sc-lab-biotechnology-bioprocess-v0220-style',
            ),
            self::asset_version($style)
        );

        wp_enqueue_script(
            self::SCRIPT_HANDLE,
            self::asset_url($script),
            array(
                'sc-lab-biotechnology-bioprocess-v0220',
            ),
            self::asset_version($script),
            true
        );
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/bioprocess/production-health',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'health_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function health_payload() {
        $catalog = array(
            'methods' => array(),
            'benchmarks' => array(),
            'categories' => array(),
        );

        if (
            class_exists(
                'SC_Lab_Biotechnology_Bioprocess_REST_V0220'
            )
            && is_callable(
                array(
                    'SC_Lab_Biotechnology_Bioprocess_REST_V0220',
                    'catalog',
                )
            )
        ) {
            $catalog =
                SC_Lab_Biotechnology_Bioprocess_REST_V0220::
                    catalog();
        }

        $method_count = isset($catalog['methods'])
            && is_array($catalog['methods'])
                ? count($catalog['methods'])
                : 0;
        $benchmark_count = isset($catalog['benchmarks'])
            && is_array($catalog['benchmarks'])
                ? count($catalog['benchmarks'])
                : 0;
        $category_count = isset($catalog['categories'])
            && is_array($catalog['categories'])
                ? count($catalog['categories'])
                : 0;
        $ready = (
            $method_count === 48
            && $benchmark_count === 48
            && $category_count === 8
        );

        return array(
            'ok' => $ready,
            'status' => $ready
                ? 'ready'
                : 'catalog-incomplete',
            'release' => self::VERSION,
            'engineRelease' => self::ENGINE_VERSION,
            'methodCount' => $method_count,
            'benchmarkCount' => $benchmark_count,
            'categoryCount' => $category_count,
            'interfaceClassLoaded' =>
                class_exists(
                    'SC_Lab_Biotechnology_Bioprocess_Engineering_V0220'
                ),
            'restClassLoaded' =>
                class_exists(
                    'SC_Lab_Biotechnology_Bioprocess_REST_V0220'
                ),
            'productionClassLoaded' => true,
            'assets' => array(
                'engineScript' => is_file(
                    self::asset_path(
                        'js/modules/'
                        . 'biotechnology-bioprocess-engineering-v0220.js'
                    )
                ),
                'productionScript' => is_file(
                    self::asset_path(
                        'js/modules/'
                        . 'bioprocess-production-v0221.js'
                    )
                ),
                'productionStyle' => is_file(
                    self::asset_path(
                        'css/'
                        . 'sc-lab-bioprocess-production-v0221.css'
                    )
                ),
            ),
        );
    }

    public static function health_response() {
        return rest_ensure_response(
            self::health_payload()
        );
    }
}

SC_Lab_Bioprocess_Production_V0221::boot();
