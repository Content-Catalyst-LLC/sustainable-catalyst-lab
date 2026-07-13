<?php
/**
 * Biosignal production activation and interface reliability.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biosignal_Production_V0231 {
    const VERSION = '0.23.1';
    const ENGINE_VERSION = '0.23.0';
    const NAMESPACE = 'sc-lab/v1';
    const ENGINE_SCRIPT =
        'sc-lab-biomedical-biosignals-v0230';
    const ENGINE_STYLE =
        'sc-lab-biomedical-biosignals-v0230-style';
    const PRODUCTION_SCRIPT =
        'sc-lab-biosignal-production-v0231';
    const PRODUCTION_STYLE =
        'sc-lab-biosignal-production-v0231-style';

    public static function boot() {
        add_action(
            'wp_enqueue_scripts',
            array(__CLASS__, 'enqueue'),
            60090
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

    private static function asset_version(
        $relative,
        $release
    ) {
        $path = self::asset_path($relative);

        return is_file($path)
            ? $release . '.' . filemtime($path)
            : $release;
    }

    public static function enqueue() {
        if (function_exists('is_admin') && is_admin()) {
            return;
        }

        if (
            class_exists(
                'SC_Lab_Biomedical_Engineering_Biosignals_V0230'
            )
            && is_callable(
                array(
                    'SC_Lab_Biomedical_Engineering_Biosignals_V0230',
                    'enqueue',
                )
            )
        ) {
            SC_Lab_Biomedical_Engineering_Biosignals_V0230::
                enqueue();
        } else {
            $engine_style =
                'css/'
                . 'sc-lab-biomedical-engineering-biosignals-v0230.css';
            $engine_script =
                'js/modules/'
                . 'biomedical-engineering-biosignals-v0230.js';

            wp_enqueue_style(
                self::ENGINE_STYLE,
                self::asset_url($engine_style),
                array(),
                self::asset_version(
                    $engine_style,
                    self::ENGINE_VERSION
                )
            );

            wp_enqueue_script(
                self::ENGINE_SCRIPT,
                self::asset_url($engine_script),
                array(),
                self::asset_version(
                    $engine_script,
                    self::ENGINE_VERSION
                ),
                true
            );
        }

        $production_style =
            'css/'
            . 'sc-lab-biosignal-production-v0231.css';
        $production_script =
            'js/modules/'
            . 'biosignal-production-v0231.js';

        wp_enqueue_style(
            self::PRODUCTION_STYLE,
            self::asset_url($production_style),
            array(self::ENGINE_STYLE),
            self::asset_version(
                $production_style,
                self::VERSION
            )
        );

        wp_enqueue_script(
            self::PRODUCTION_SCRIPT,
            self::asset_url($production_script),
            array(self::ENGINE_SCRIPT),
            self::asset_version(
                $production_script,
                self::VERSION
            ),
            true
        );
    }

    private static function catalog() {
        if (
            class_exists(
                'SC_Lab_Biomedical_Biosignals_REST_V0230'
            )
            && is_callable(
                array(
                    'SC_Lab_Biomedical_Biosignals_REST_V0230',
                    'catalog',
                )
            )
        ) {
            return
                SC_Lab_Biomedical_Biosignals_REST_V0230::
                    catalog();
        }

        $path = dirname(__DIR__)
            . '/contracts/'
            . 'biomedical-engineering-biosignals-v0230.json';

        if (!is_file($path)) {
            return array();
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        return is_array($decoded)
            ? $decoded
            : array();
    }

    public static function health_payload() {
        $catalog = self::catalog();
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
            ($catalog['version'] ?? null)
                === self::ENGINE_VERSION
            && $method_count === 48
            && $benchmark_count === 48
            && $category_count === 8
        );

        return array(
            'ok' => $ready,
            'status' => $ready
                ? 'ready'
                : 'contract-incomplete',
            'release' => self::VERSION,
            'engineRelease' => self::ENGINE_VERSION,
            'methodCount' => $method_count,
            'benchmarkCount' => $benchmark_count,
            'categoryCount' => $category_count,
            'interfaceClassLoaded' =>
                class_exists(
                    'SC_Lab_Biomedical_Engineering_Biosignals_V0230'
                ),
            'restClassLoaded' =>
                class_exists(
                    'SC_Lab_Biomedical_Biosignals_REST_V0230'
                ),
            'productionClassLoaded' => true,
            'assets' => array(
                'contract' => is_file(
                    dirname(__DIR__)
                    . '/contracts/'
                    . 'biomedical-engineering-biosignals-v0230.json'
                ),
                'engineScript' => is_file(
                    self::asset_path(
                        'js/modules/'
                        . 'biomedical-engineering-biosignals-v0230.js'
                    )
                ),
                'engineStyle' => is_file(
                    self::asset_path(
                        'css/'
                        . 'sc-lab-biomedical-engineering-biosignals-v0230.css'
                    )
                ),
                'productionScript' => is_file(
                    self::asset_path(
                        'js/modules/'
                        . 'biosignal-production-v0231.js'
                    )
                ),
                'productionStyle' => is_file(
                    self::asset_path(
                        'css/'
                        . 'sc-lab-biosignal-production-v0231.css'
                    )
                ),
            ),
            'responsibleUse' => array(
                'clinicalUse' => false,
                'diagnosticUse' => false,
                'patientMonitoring' => false,
            ),
        );
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/biomedical/biosignals/production-health',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'health_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function health_response() {
        return rest_ensure_response(
            self::health_payload()
        );
    }
}

SC_Lab_Biosignal_Production_V0231::boot();
