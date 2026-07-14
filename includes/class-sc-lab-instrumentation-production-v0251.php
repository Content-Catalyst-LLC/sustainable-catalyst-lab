<?php
/**
 * Instrumentation production activation and interface reliability.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Instrumentation_Production_V0251 {
    const VERSION = '0.25.1';
    const ENGINE_VERSION = '0.25.0';
    const NAMESPACE = 'sc-lab/v1';
    const ENGINE_SCRIPT = 'sc-lab-laboratory-instrumentation-v0250';
    const ENGINE_STYLE = 'sc-lab-laboratory-instrumentation-v0250-style';
    const PRODUCTION_SCRIPT = 'sc-lab-instrumentation-production-v0251';
    const PRODUCTION_STYLE = 'sc-lab-instrumentation-production-v0251-style';

    public static function boot() {
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), 60110);
        add_action('rest_api_init', array(__CLASS__, 'register_routes'));
    }

    private static function asset_url($relative) {
        if (defined('SC_LAB_URL')) {
            return trailingslashit((string) constant('SC_LAB_URL'))
                . 'assets/' . ltrim((string) $relative, '/');
        }

        return plugin_dir_url(dirname(__DIR__) . '/sustainable-catalyst-lab.php')
            . 'assets/' . ltrim((string) $relative, '/');
    }

    private static function asset_path($relative) {
        return dirname(__DIR__) . '/assets/' . ltrim((string) $relative, '/');
    }

    private static function asset_version($relative, $release) {
        $path = self::asset_path($relative);
        return is_file($path) ? $release . '.' . filemtime($path) : $release;
    }

    public static function enqueue() {
        if (function_exists('is_admin') && is_admin()) {
            return;
        }

        if (
            class_exists('SC_Lab_Laboratory_Data_Instrumentation_V0250')
            && is_callable(array('SC_Lab_Laboratory_Data_Instrumentation_V0250', 'enqueue'))
        ) {
            SC_Lab_Laboratory_Data_Instrumentation_V0250::enqueue();
        } else {
            $engine_style = 'css/sc-lab-laboratory-data-instrumentation-v0250.css';
            $engine_script = 'js/modules/laboratory-data-instrumentation-v0250.js';
            wp_enqueue_style(
                self::ENGINE_STYLE,
                self::asset_url($engine_style),
                array(),
                self::asset_version($engine_style, self::ENGINE_VERSION)
            );
            wp_enqueue_script(
                self::ENGINE_SCRIPT,
                self::asset_url($engine_script),
                array(),
                self::asset_version($engine_script, self::ENGINE_VERSION),
                true
            );
        }

        $style = 'css/sc-lab-instrumentation-production-v0251.css';
        $script = 'js/modules/instrumentation-production-v0251.js';
        wp_enqueue_style(
            self::PRODUCTION_STYLE,
            self::asset_url($style),
            array(self::ENGINE_STYLE),
            self::asset_version($style, self::VERSION)
        );
        wp_enqueue_script(
            self::PRODUCTION_SCRIPT,
            self::asset_url($script),
            array(self::ENGINE_SCRIPT),
            self::asset_version($script, self::VERSION),
            true
        );
    }

    private static function catalog() {
        if (
            class_exists('SC_Lab_Laboratory_Instrumentation_REST_V0250')
            && is_callable(array('SC_Lab_Laboratory_Instrumentation_REST_V0250', 'catalog'))
        ) {
            return SC_Lab_Laboratory_Instrumentation_REST_V0250::catalog();
        }

        $path = dirname(__DIR__) . '/contracts/laboratory-data-instrumentation-v0250.json';
        if (!is_file($path)) {
            return array();
        }
        $decoded = json_decode(file_get_contents($path), true);
        return is_array($decoded) ? $decoded : array();
    }

    public static function health_payload() {
        $catalog = self::catalog();
        $counts = array(
            'methodCount' => count($catalog['methods'] ?? array()),
            'benchmarkCount' => count($catalog['benchmarks'] ?? array()),
            'categoryCount' => count($catalog['categories'] ?? array()),
            'recordTypeCount' => count($catalog['recordTypes'] ?? array()),
            'connectionProfileCount' => count($catalog['connectionProfiles'] ?? array()),
            'qualityFlagCount' => count($catalog['qualityFlags'] ?? array()),
        );
        $ready = (
            ($catalog['version'] ?? null) === self::ENGINE_VERSION
            && $counts['methodCount'] === 48
            && $counts['benchmarkCount'] === 48
            && $counts['categoryCount'] === 8
            && $counts['recordTypeCount'] === 9
            && $counts['connectionProfileCount'] === 8
            && $counts['qualityFlagCount'] === 8
        );

        return array_merge(
            array(
                'ok' => $ready,
                'status' => $ready ? 'ready' : 'contract-incomplete',
                'release' => self::VERSION,
                'engineRelease' => self::ENGINE_VERSION,
                'interfaceClassLoaded' => class_exists('SC_Lab_Laboratory_Data_Instrumentation_V0250'),
                'restClassLoaded' => class_exists('SC_Lab_Laboratory_Instrumentation_REST_V0250'),
                'productionClassLoaded' => true,
                'assets' => array(
                    'contract' => is_file(dirname(__DIR__) . '/contracts/laboratory-data-instrumentation-v0250.json'),
                    'engineScript' => is_file(self::asset_path('js/modules/laboratory-data-instrumentation-v0250.js')),
                    'engineStyle' => is_file(self::asset_path('css/sc-lab-laboratory-data-instrumentation-v0250.css')),
                    'productionScript' => is_file(self::asset_path('js/modules/instrumentation-production-v0251.js')),
                    'productionStyle' => is_file(self::asset_path('css/sc-lab-instrumentation-production-v0251.css')),
                ),
                'boundaries' => array(
                    'automaticLocalDeviceAccess' => false,
                    'clinicalInstrumentation' => false,
                    'regulatedReleaseAuthority' => false,
                    'localFirstManualOperation' => true,
                ),
            ),
            $counts
        );
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/production-health',
            array(
                'methods' => 'GET',
                'callback' => array(__CLASS__, 'health_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function health_response() {
        return rest_ensure_response(self::health_payload());
    }
}

SC_Lab_Instrumentation_Production_V0251::boot();
