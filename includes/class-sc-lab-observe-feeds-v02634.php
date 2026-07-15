<?php
/**
 * Sustainable Catalyst Lab v0.26.3.4 scientific feed rendering and Observe reliability.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Observe_Feeds_V02634 {
    const VERSION = '0.26.3.4';
    private static $initialized = false;
    private static $enqueued = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue'), 3);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim((string) $relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }

    public static function maybe_enqueue() {
        if (!self::is_lab_request() || self::$enqueued) { return; }
        self::$enqueued = true;

        $style = 'assets/css/sc-lab-observe-feeds-v02634.css';
        $script = 'assets/js/sc-lab-observe-feeds-v02634.js';
        wp_enqueue_style(
            'sc-lab-observe-feeds-v02634',
            SC_LAB_URL . $style,
            array('sc-lab-app'),
            self::asset_version($style)
        );
        wp_enqueue_script(
            'sc-lab-observe-feeds-v02634',
            SC_LAB_URL . $script,
            array('sc-lab-core', 'sc-lab-projects', 'sc-lab-feeds', 'sc-lab-datasets', 'sc-lab-observations', 'sc-lab-runtime-v02631'),
            self::asset_version($script),
            true
        );
        wp_localize_script('sc-lab-observe-feeds-v02634', 'SCLabObserveFeedsConfigV02634', array(
            'version' => self::VERSION,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'proxyBase' => esc_url_raw(rest_url('sc-lab/v1/observe/v02634/source/')),
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/observe/v02634/health')),
            'nonce' => wp_create_nonce('wp_rest'),
            'timeoutMs' => 18000,
            'autoLoad' => true,
        ));
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/observe/v02634/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-lab/v1', '/observe/v02634/source/(?P<source>[a-z0-9-]+)', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'source'),
            'permission_callback' => '__return_true',
            'args' => array(
                'source' => array('sanitize_callback' => 'sanitize_key'),
                'limit' => array('sanitize_callback' => 'absint'),
                'q' => array('sanitize_callback' => 'sanitize_text_field'),
                'scientificName' => array('sanitize_callback' => 'sanitize_text_field'),
                'force' => array('sanitize_callback' => 'rest_sanitize_boolean'),
            ),
        ));
    }

    private static function settings() {
        return wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
    }

    private static function source_url($source, $params) {
        if ($source === 'nasa-space-telescopes') {
            $query = isset($params['q']) ? (string) $params['q'] : 'JWST Hubble nebula galaxy';
            return add_query_arg(array('q' => $query, 'media_type' => 'image'), 'https://images-api.nasa.gov/search');
        }
        if ($source === 'obis-marine') {
            $name = isset($params['scientificName']) ? (string) $params['scientificName'] : 'Cetacea';
            return add_query_arg(array('scientificname' => $name, 'size' => max(1, min(30, isset($params['limit']) ? absint($params['limit']) : 25))), 'https://api.obis.org/v3/occurrence');
        }
        return null;
    }

    public static function source(WP_REST_Request $request) {
        $source = sanitize_key((string) $request['source']);
        $registry = SC_Lab_Feeds::registry();
        if (!isset($registry[$source])) {
            return new WP_Error('unknown_source', 'Unknown scientific source.', array('status' => 404));
        }

        $settings = self::settings();
        $params = $request->get_params();
        unset($params['source']);
        $params['limit'] = max(1, min(30, isset($params['limit']) ? absint($params['limit']) : 12));
        $force = !empty($params['force']);
        unset($params['force']);

        $base = array(
            'source' => $source,
            'sourceMeta' => $registry[$source],
            'sourceUrl' => self::source_url($source, $params),
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'connectorRuntime' => self::VERSION,
            'retrievedAt' => gmdate('c'),
        );

        if (empty($settings['enable_feeds'])) {
            return rest_ensure_response(array_merge($base, array(
                'ok' => false,
                'mode' => 'disabled',
                'records' => array(),
                'message' => 'Scientific feeds are disabled in the Lab settings.',
                'retryable' => false,
            )));
        }

        $cache_key = 'sc_lab_v02634_' . md5($source . wp_json_encode($params));
        if (!$force) {
            $cached = get_transient($cache_key);
            if (is_array($cached)) {
                return rest_ensure_response(array_merge($base, array(
                    'ok' => true,
                    'mode' => 'wordpress-cache',
                    'records' => $cached,
                    'message' => count($cached) . ' cached records returned.',
                    'retryable' => true,
                )));
            }
        }

        $started = microtime(true);
        $records = SC_Lab_Feeds::fetch($source, $params);
        $elapsed = round((microtime(true) - $started) * 1000);
        if (is_wp_error($records)) {
            $diagnostic = array(
                'code' => $records->get_error_code(),
                'message' => $records->get_error_message(),
                'elapsedMs' => $elapsed,
                'wordpressHttpAvailable' => function_exists('wp_safe_remote_get'),
            );
            set_transient('sc_lab_health_' . md5($source), array(
                'status' => 'error',
                'lastChecked' => gmdate('c'),
                'message' => $diagnostic['message'],
                'runtime' => self::VERSION,
            ), DAY_IN_SECONDS);
            return rest_ensure_response(array_merge($base, array(
                'ok' => false,
                'mode' => 'wordpress-proxy-error',
                'records' => array(),
                'message' => $diagnostic['message'],
                'diagnostic' => $diagnostic,
                'retryable' => true,
                'browserDirectEligible' => in_array($source, array('nasa-space-telescopes', 'obis-marine'), true),
            )));
        }

        $records = is_array($records) ? array_values($records) : array();
        set_transient('sc_lab_health_' . md5($source), array(
            'status' => $records ? 'ready' : 'empty',
            'lastChecked' => gmdate('c'),
            'message' => $records ? count($records) . ' records returned' : 'The source returned zero records.',
            'runtime' => self::VERSION,
        ), DAY_IN_SECONDS);
        set_transient($cache_key, $records, max(5, absint($settings['cache_minutes'])) * MINUTE_IN_SECONDS);

        return rest_ensure_response(array_merge($base, array(
            'ok' => true,
            'mode' => $records ? 'wordpress-live' : 'wordpress-empty',
            'records' => $records,
            'message' => $records ? count($records) . ' live records returned.' : 'The source returned zero records for this query.',
            'elapsedMs' => $elapsed,
            'retryable' => true,
        )));
    }

    public static function health() {
        $settings = self::settings();
        $sources = array();
        foreach (array('nasa-space-telescopes', 'obis-marine') as $source) {
            $meta = SC_Lab_Feeds::registry()[$source];
            $stored = get_transient('sc_lab_health_' . md5($source));
            $sources[$source] = array_merge($meta, is_array($stored) ? $stored : array(
                'status' => 'not_checked',
                'lastChecked' => null,
                'message' => 'Open the Observe panel or run a query to check this connector.',
            ));
        }
        return rest_ensure_response(array(
            'ok' => true,
            'release' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'connectorRuntime' => self::VERSION,
            'feedsEnabled' => !empty($settings['enable_feeds']),
            'wordpressHttpAvailable' => function_exists('wp_safe_remote_get'),
            'jsonAvailable' => function_exists('json_decode'),
            'sources' => $sources,
            'fallbackOrder' => array('wordpress-proxy', 'browser-direct', 'explicit-diagnostic'),
            'blankPanelsAllowed' => false,
            'autoLoad' => true,
            'time' => gmdate('c'),
        ));
    }
}
