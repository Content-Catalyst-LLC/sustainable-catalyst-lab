<?php
/** Sustainable Catalyst Lab v0.155.0 — Batch Experiment, Sweep & Ensemble Orchestration. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Batch_Experiment_Sweep_Ensemble_V01550 {
    const VERSION = '0.155.0';
    private static $initialized = false;
    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('wp_print_footer_scripts', array(__CLASS__, 'enqueue'), PHP_INT_MAX);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }
    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if ($post instanceof WP_Post && has_shortcode((string)$post->post_content, 'sc_lab_app')) { return true; }
        if (function_exists('is_page') && is_page('lab')) { return true; }
        $path = isset($_SERVER['REQUEST_URI']) ? (string)parse_url((string)$_SERVER['REQUEST_URI'], PHP_URL_PATH) : '';
        return (bool)preg_match('~/(?:lab)/?$~', $path);
    }
    private static function asset_token($relative) {
        $path = SC_LAB_DIR . ltrim((string)$relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 16) : 'missing');
    }
    public static function enqueue() {
        if (!self::is_lab_request()) { return; }
        $css = 'assets/css/sc-lab-batch-experiment-sweep-ensemble-v01550.css';
        $js = 'assets/js/sc-lab-batch-experiment-sweep-ensemble-v01550.js';
        wp_enqueue_style('sc-lab-batch-campaign-v01550', SC_LAB_URL . $css, array('sc-lab-protocol-notebook-v01540'), self::asset_token($css));
        wp_enqueue_script('sc-lab-batch-campaign-v01550', SC_LAB_URL . $js, array('sc-lab-protocol-notebook-v01540'), self::asset_token($js), true);
        wp_localize_script('sc-lab-batch-campaign-v01550', 'SCLabBatchCampaignV01550', array(
            'version' => self::VERSION,
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/batch-campaigns/v01550/health')),
            'campaignsUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/batch-campaigns/v01550/campaigns')),
            'verifyUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/batch-campaigns/v01550/manifests/verify')),
            'defaultProjectId' => is_user_logged_in() ? 'project:wp-user-' . get_current_user_id() : '',
            'nonce' => wp_create_nonce('wp_rest'),
        ));
    }
    public static function operations_permission() { return is_user_logged_in(); }
    private static function settings() { return wp_parse_args((array)get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults()); }
    private static function clean_id($value) { return substr(preg_replace('/[^A-Za-z0-9._:-]/', '', (string)$value), 0, 180); }
    private static function clean_tree($value, $depth = 0, &$nodes = 0) {
        $nodes++;
        if ($nodes > 25000 || $depth > 20) { return null; }
        if (is_null($value) || is_bool($value) || is_int($value) || is_float($value)) { return $value; }
        if (is_string($value)) { return substr(wp_check_invalid_utf8($value, true), 0, 100000); }
        if (!is_array($value)) { return null; }
        $out = array(); $count = 0;
        foreach ($value as $k => $v) {
            if (++$count > 5000) { break; }
            $key = is_int($k) ? $k : substr(preg_replace('/[^A-Za-z0-9._:-]/', '', (string)$k), 0, 128);
            if ($key === '' && !is_int($k)) { continue; }
            $out[$key] = self::clean_tree($v, $depth + 1, $nodes);
        }
        return $out;
    }
    private static function body(WP_REST_Request $r) { $b = $r->get_json_params(); $n = 0; return self::clean_tree(is_array($b) ? $b : array(), 0, $n); }
    private static function proxy($path, $method = 'GET', $payload = null, $limit = 4194304) {
        $settings = self::settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return new WP_Error('compute_disabled', 'The Python Compute Core is not enabled or configured.', array('status' => 503)); }
        if (!class_exists('SC_Lab_Python_Compute_Core_V0261')) { return new WP_Error('compute_proxy_unavailable', 'The Python Compute Core signing bridge is unavailable.', array('status' => 503)); }
        $body = null === $payload ? '' : wp_json_encode($payload);
        $url = untrailingslashit($settings['compute_backend_url']) . $path;
        $args = array('method' => $method, 'timeout' => max(5, min(120, absint($settings['compute_timeout_seconds']))), 'redirection' => 2, 'sslverify' => !empty($settings['compute_verify_ssl']), 'headers' => SC_Lab_Python_Compute_Core_V0261::signed_headers($path, $method, $body, $settings), 'limit_response_size' => max(262144, min(8388608, absint($limit))));
        if (null !== $payload) { $args['body'] = $body; }
        $response = wp_safe_remote_request($url, $args);
        if (is_wp_error($response)) { return new WP_Error('batch_campaign_backend_unavailable', $response->get_error_message(), array('status' => 502)); }
        $status = wp_remote_retrieve_response_code($response); $decoded = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($decoded)) { $decoded = array('detail' => 'The batch campaign backend returned invalid JSON.'); $status = 502; }
        return new WP_REST_Response($decoded, $status);
    }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/health', array('methods' => 'GET', 'callback' => array(__CLASS__, 'health'), 'permission_callback' => '__return_true'));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns', array(array('methods' => 'GET', 'callback' => array(__CLASS__, 'campaigns_list'), 'permission_callback' => array(__CLASS__, 'operations_permission')), array('methods' => 'POST', 'callback' => array(__CLASS__, 'campaign_create'), 'permission_callback' => array(__CLASS__, 'operations_permission'))));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})', array('methods' => 'GET', 'callback' => array(__CLASS__, 'campaign_get'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/execution-batch', array('methods' => 'GET', 'callback' => array(__CLASS__, 'execution_batch'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/trials/(?P<trial>[A-Za-z0-9._:-]{1,180})/state', array('methods' => 'POST', 'callback' => array(__CLASS__, 'trial_state'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/retry-failed', array('methods' => 'POST', 'callback' => array(__CLASS__, 'retry_failed'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/aggregate', array('methods' => 'GET', 'callback' => array(__CLASS__, 'aggregate'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/manifest', array('methods' => 'GET', 'callback' => array(__CLASS__, 'manifest'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/timeline', array('methods' => 'GET', 'callback' => array(__CLASS__, 'timeline'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/campaigns/(?P<id>[A-Za-z0-9._:-]{1,180})/archive', array('methods' => 'POST', 'callback' => array(__CLASS__, 'archive'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/batch-campaigns/v01550/manifests/verify', array('methods' => 'POST', 'callback' => array(__CLASS__, 'verify_manifest'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
    }
    public static function health() { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/health'); }
    public static function campaigns_list(WP_REST_Request $r) { $p = self::clean_id($r->get_param('project_id')); $q = '?project_id=' . rawurlencode($p) . '&limit=' . max(1, min(500, absint($r->get_param('limit') ?: 100))); return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns' . $q); }
    public static function campaign_create(WP_REST_Request $r) { $b = self::body($r); $p = self::clean_id(isset($b['project_id']) ? $b['project_id'] : ''); unset($b['project_id']); return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/projects/' . rawurlencode($p) . '/campaigns', 'POST', $b); }
    public static function campaign_get(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '?include_trials=true'); }
    public static function execution_batch(WP_REST_Request $r) { $q = '?limit=' . max(1, min(1000, absint($r->get_param('limit') ?: 100))) . '&status=' . rawurlencode(sanitize_key($r->get_param('status') ?: 'planned')); return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/execution-batch' . $q); }
    public static function trial_state(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/trials/' . rawurlencode(self::clean_id($r['trial'])) . '/state', 'POST', self::body($r)); }
    public static function retry_failed(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/retry-failed', 'POST', self::body($r)); }
    public static function aggregate(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/aggregate'); }
    public static function manifest(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/manifest'); }
    public static function timeline(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/timeline'); }
    public static function archive(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/campaigns/' . rawurlencode(self::clean_id($r['id'])) . '/archive', 'POST', array()); }
    public static function verify_manifest(WP_REST_Request $r) { return self::proxy('/v1/batch-experiment-sweep-ensemble/v01550/manifests/verify', 'POST', self::body($r)); }
}
