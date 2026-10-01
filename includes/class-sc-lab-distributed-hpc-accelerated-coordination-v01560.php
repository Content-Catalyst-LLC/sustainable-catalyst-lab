<?php
/** Sustainable Catalyst Lab v0.156.0 — Distributed, HPC & Accelerated Research Coordination. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Distributed_HPC_Accelerated_Coordination_V01560 {
    const VERSION = '0.156.0';
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
        $css = 'assets/css/sc-lab-distributed-hpc-accelerated-coordination-v01560.css';
        $js = 'assets/js/sc-lab-distributed-hpc-accelerated-coordination-v01560.js';
        wp_enqueue_style('sc-lab-distributed-coordination-v01560', SC_LAB_URL . $css, array('sc-lab-batch-campaign-v01550'), self::asset_token($css));
        wp_enqueue_script('sc-lab-distributed-coordination-v01560', SC_LAB_URL . $js, array('sc-lab-batch-campaign-v01550'), self::asset_token($js), true);
        wp_localize_script('sc-lab-distributed-coordination-v01560', 'SCLabDistributedCoordinationV01560', array(
            'version' => self::VERSION,
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/distributed/v01560/health')),
            'targetsUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/distributed/v01560/targets')),
            'plansUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/distributed/v01560/plans')),
            'verifyUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/distributed/v01560/manifests/verify')),
            'defaultProjectId' => is_user_logged_in() ? 'project:wp-user-' . get_current_user_id() : '',
            'nonce' => wp_create_nonce('wp_rest'),
        ));
    }
    public static function operations_permission() { return is_user_logged_in(); }
    private static function settings() { return wp_parse_args((array)get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults()); }
    private static function clean_id($value) { return substr(preg_replace('/[^A-Za-z0-9._:-]/', '', (string)$value), 0, 180); }
    private static function clean_tree($value, $depth = 0, &$nodes = 0) {
        $nodes++;
        if ($nodes > 30000 || $depth > 24) { return null; }
        if (is_null($value) || is_bool($value) || is_int($value) || is_float($value)) { return $value; }
        if (is_string($value)) { return substr(wp_check_invalid_utf8($value, true), 0, 150000); }
        if (!is_array($value)) { return null; }
        $out = array(); $count = 0;
        foreach ($value as $k => $v) {
            if (++$count > 10000) { break; }
            $key = is_int($k) ? $k : substr(preg_replace('/[^A-Za-z0-9._:-]/', '', (string)$k), 0, 128);
            if ($key === '' && !is_int($k)) { continue; }
            $out[$key] = self::clean_tree($v, $depth + 1, $nodes);
        }
        return $out;
    }
    private static function body(WP_REST_Request $r) { $b = $r->get_json_params(); $n = 0; return self::clean_tree(is_array($b) ? $b : array(), 0, $n); }
    private static function proxy($path, $method = 'GET', $payload = null, $limit = 8388608) {
        $settings = self::settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return new WP_Error('compute_disabled', 'The Python Compute Core is not enabled or configured.', array('status' => 503)); }
        if (!class_exists('SC_Lab_Python_Compute_Core_V0261')) { return new WP_Error('compute_proxy_unavailable', 'The Python Compute Core signing bridge is unavailable.', array('status' => 503)); }
        $body = null === $payload ? '' : wp_json_encode($payload);
        $url = untrailingslashit($settings['compute_backend_url']) . $path;
        $args = array('method' => $method, 'timeout' => max(5, min(120, absint($settings['compute_timeout_seconds']))), 'redirection' => 2, 'sslverify' => !empty($settings['compute_verify_ssl']), 'headers' => SC_Lab_Python_Compute_Core_V0261::signed_headers($path, $method, $body, $settings), 'limit_response_size' => max(262144, min(16777216, absint($limit))));
        if (null !== $payload) { $args['body'] = $body; }
        $response = wp_safe_remote_request($url, $args);
        if (is_wp_error($response)) { return new WP_Error('distributed_coordination_backend_unavailable', $response->get_error_message(), array('status' => 502)); }
        $status = wp_remote_retrieve_response_code($response); $decoded = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($decoded)) { $decoded = array('detail' => 'The distributed coordination backend returned invalid JSON.'); $status = 502; }
        return new WP_REST_Response($decoded, $status);
    }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/health', array('methods' => 'GET', 'callback' => array(__CLASS__, 'health'), 'permission_callback' => '__return_true'));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/targets', array(array('methods' => 'GET', 'callback' => array(__CLASS__, 'targets_list'), 'permission_callback' => array(__CLASS__, 'operations_permission')), array('methods' => 'POST', 'callback' => array(__CLASS__, 'target_create'), 'permission_callback' => array(__CLASS__, 'operations_permission'))));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/targets/(?P<id>[A-Za-z0-9._:-]{1,180})', array('methods' => 'GET', 'callback' => array(__CLASS__, 'target_get'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/targets/(?P<id>[A-Za-z0-9._:-]{1,180})/archive', array('methods' => 'POST', 'callback' => array(__CLASS__, 'target_archive'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans', array(array('methods' => 'GET', 'callback' => array(__CLASS__, 'plans_list'), 'permission_callback' => array(__CLASS__, 'operations_permission')), array('methods' => 'POST', 'callback' => array(__CLASS__, 'plan_create'), 'permission_callback' => array(__CLASS__, 'operations_permission'))));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})', array('methods' => 'GET', 'callback' => array(__CLASS__, 'plan_get'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/waves', array('methods' => 'GET', 'callback' => array(__CLASS__, 'waves'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/scheduler-bundle', array('methods' => 'GET', 'callback' => array(__CLASS__, 'scheduler_bundle'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/receipts', array('methods' => 'POST', 'callback' => array(__CLASS__, 'receipt'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/reconcile', array('methods' => 'POST', 'callback' => array(__CLASS__, 'reconcile'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/replan-failed', array('methods' => 'GET', 'callback' => array(__CLASS__, 'replan_failed'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/manifest', array('methods' => 'GET', 'callback' => array(__CLASS__, 'manifest'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/timeline', array('methods' => 'GET', 'callback' => array(__CLASS__, 'timeline'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/plans/(?P<id>[A-Za-z0-9._:-]{1,180})/archive', array('methods' => 'POST', 'callback' => array(__CLASS__, 'plan_archive'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/distributed/v01560/manifests/verify', array('methods' => 'POST', 'callback' => array(__CLASS__, 'verify_manifest'), 'permission_callback' => array(__CLASS__, 'operations_permission')));
    }
    public static function health() { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/health'); }
    private static function project_query(WP_REST_Request $r) { return '?project_id=' . rawurlencode(self::clean_id($r->get_param('project_id'))) . '&limit=' . max(1, min(1000, absint($r->get_param('limit') ?: 100))); }
    public static function targets_list(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/targets' . self::project_query($r)); }
    public static function target_create(WP_REST_Request $r) { $b=self::body($r);$p=self::clean_id(isset($b['project_id'])?$b['project_id']:'');unset($b['project_id']);return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/projects/'.rawurlencode($p).'/targets','POST',$b); }
    public static function target_get(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/targets/'.rawurlencode(self::clean_id($r['id']))); }
    public static function target_archive(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/targets/'.rawurlencode(self::clean_id($r['id'])).'/archive','POST',array()); }
    public static function plans_list(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans' . self::project_query($r)); }
    public static function plan_create(WP_REST_Request $r) { $b=self::body($r);$p=self::clean_id(isset($b['project_id'])?$b['project_id']:'');unset($b['project_id']);return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/projects/'.rawurlencode($p).'/plans','POST',$b); }
    public static function plan_get(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id']))); }
    public static function waves(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/waves'); }
    public static function scheduler_bundle(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/scheduler-bundle'); }
    public static function receipt(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/receipts','POST',self::body($r)); }
    public static function reconcile(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/reconcile','POST',array()); }
    public static function replan_failed(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/replan-failed'); }
    public static function manifest(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/manifest'); }
    public static function timeline(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/timeline'); }
    public static function plan_archive(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/plans/'.rawurlencode(self::clean_id($r['id'])).'/archive','POST',array()); }
    public static function verify_manifest(WP_REST_Request $r) { return self::proxy('/v1/distributed-hpc-accelerated-coordination/v01560/manifests/verify','POST',self::body($r)); }
}
