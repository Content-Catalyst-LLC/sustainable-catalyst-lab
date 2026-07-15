<?php
/**
 * Sustainable Catalyst Lab v0.27.2 long-running jobs and checkpoint recovery.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Long_Jobs_V0272 {
    const VERSION = '0.27.2';

    private static $initialized = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('rest_api_init', array(__CLASS__, 'routes'));
        add_filter('sc_lab_module_aliases_v02631', array(__CLASS__, 'aliases'));
    }

    public static function aliases($aliases) {
        $aliases = is_array($aliases) ? $aliases : array();
        $aliases['long-jobs'] = 'long-running-jobs';
        $aliases['checkpoints'] = 'long-running-jobs';
        $aliases['job-recovery'] = 'long-running-jobs';
        $aliases['compute-queue'] = 'long-running-jobs';
        return $aliases;
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/numerical/v0272/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    public static function health() {
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        $required = array(
            'assets/js/modules/long-running-jobs-studio.js',
            'assets/css/sc-lab-long-jobs-v0272.css',
            'contracts/long-running-job-v0272.schema.json',
            'includes/class-sc-lab-long-jobs-v0272.php',
        );
        $files = array();
        foreach ($required as $relative) {
            $path = SC_LAB_DIR . $relative;
            $files[$relative] = array(
                'exists' => is_file($path),
                'sha256' => is_file($path) ? hash_file('sha256', $path) : null,
            );
        }
        $all_present = !in_array(false, array_map(function($row){ return !empty($row['exists']); }, $files), true);
        return rest_ensure_response(array(
            'ok' => $all_present,
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'architecture' => 'wordpress-control-plane-checkpointed-python-jobs',
            'remoteComputeEnabled' => !empty($settings['enable_remote_compute']),
            'remoteComputeConfigured' => !empty($settings['compute_backend_url']),
            'capabilities' => array(
                'checkpointHistory' => true,
                'pauseResume' => true,
                'partialResults' => true,
                'priorityScheduling' => true,
                'resultCaching' => true,
                'projectLimits' => true,
            ),
            'files' => $files,
            'time' => gmdate('c'),
        ));
    }
}
