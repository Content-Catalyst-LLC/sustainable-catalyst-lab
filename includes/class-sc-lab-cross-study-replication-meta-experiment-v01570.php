<?php
/** Sustainable Catalyst Lab v0.157.0 — Cross-Study Replication & Meta-Experiment Workspace. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Cross_Study_Replication_Meta_Experiment_V01570 {
    const VERSION = '0.157.0';
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
        $css = 'assets/css/sc-lab-cross-study-replication-meta-experiment-v01570.css';
        $js = 'assets/js/sc-lab-cross-study-replication-meta-experiment-v01570.js';
        wp_enqueue_style('sc-lab-cross-study-meta-v01570', SC_LAB_URL . $css, array('sc-lab-distributed-coordination-v01560'), self::asset_token($css));
        wp_enqueue_script('sc-lab-cross-study-meta-v01570', SC_LAB_URL . $js, array('sc-lab-distributed-coordination-v01560'), self::asset_token($js), true);
        wp_localize_script('sc-lab-cross-study-meta-v01570', 'SCLabCrossStudyMetaV01570', array(
            'version' => self::VERSION,
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/cross-study/v01570/health')),
            'studiesUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/cross-study/v01570/studies')),
            'workspacesUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/cross-study/v01570/workspaces')),
            'verifyUrl' => esc_url_raw(rest_url('sc-lab/v1/workspace/cross-study/v01570/manifests/verify')),
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
        if (is_wp_error($response)) { return new WP_Error('cross_study_backend_unavailable', $response->get_error_message(), array('status' => 502)); }
        $status = wp_remote_retrieve_response_code($response); $decoded = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($decoded)) { $decoded = array('detail' => 'The cross-study backend returned invalid JSON.'); $status = 502; }
        return new WP_REST_Response($decoded, $status);
    }
    private static function project_query(WP_REST_Request $r) {
        return '?project_id=' . rawurlencode(self::clean_id($r->get_param('project_id'))) . '&include_archived=' . ($r->get_param('include_archived') ? 'true' : 'false') . '&limit=' . max(1, min(1000, absint($r->get_param('limit') ?: 100)));
    }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/health', array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/studies', array(array('methods'=>'GET','callback'=>array(__CLASS__,'studies_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),array('methods'=>'POST','callback'=>array(__CLASS__,'study_create'),'permission_callback'=>array(__CLASS__,'operations_permission'))));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/studies/(?P<id>[A-Za-z0-9._:-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'study_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/studies/(?P<id>[A-Za-z0-9._:-]{1,180})/revisions', array('methods'=>'POST','callback'=>array(__CLASS__,'study_revise'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/studies/(?P<id>[A-Za-z0-9._:-]{1,180})/effects', array('methods'=>'POST','callback'=>array(__CLASS__,'effect_add'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces', array(array('methods'=>'GET','callback'=>array(__CLASS__,'workspaces_list'),'permission_callback'=>array(__CLASS__,'operations_permission')),array('methods'=>'POST','callback'=>array(__CLASS__,'workspace_create'),'permission_callback'=>array(__CLASS__,'operations_permission'))));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})', array('methods'=>'GET','callback'=>array(__CLASS__,'workspace_get'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/studies', array('methods'=>'POST','callback'=>array(__CLASS__,'workspace_study_add'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/freeze', array('methods'=>'POST','callback'=>array(__CLASS__,'workspace_freeze'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/studies/(?P<study>[A-Za-z0-9._:-]{1,180})/assessment', array('methods'=>'POST','callback'=>array(__CLASS__,'assessment'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/synthesis', array('methods'=>'GET','callback'=>array(__CLASS__,'synthesis'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/matrix', array('methods'=>'GET','callback'=>array(__CLASS__,'matrix'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/studies/(?P<study>[A-Za-z0-9._:-]{1,180})/replication-handoff', array('methods'=>'GET','callback'=>array(__CLASS__,'handoff'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/manifest', array('methods'=>'GET','callback'=>array(__CLASS__,'manifest'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/timeline', array('methods'=>'GET','callback'=>array(__CLASS__,'timeline'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/workspaces/(?P<id>[A-Za-z0-9._:-]{1,180})/archive', array('methods'=>'POST','callback'=>array(__CLASS__,'archive'),'permission_callback'=>array(__CLASS__,'operations_permission')));
        register_rest_route('sc-lab/v1', '/workspace/cross-study/v01570/manifests/verify', array('methods'=>'POST','callback'=>array(__CLASS__,'verify_manifest'),'permission_callback'=>array(__CLASS__,'operations_permission')));
    }
    public static function health() { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/health'); }
    public static function studies_list(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/studies'.self::project_query($r)); }
    public static function study_create(WP_REST_Request $r) { $b=self::body($r); $p=self::clean_id(isset($b['project_id'])?$b['project_id']:''); return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/projects/'.rawurlencode($p).'/studies','POST',$b); }
    public static function study_get(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/studies/'.rawurlencode(self::clean_id($r['id']))); }
    public static function study_revise(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/studies/'.rawurlencode(self::clean_id($r['id'])).'/revisions','POST',self::body($r)); }
    public static function effect_add(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/studies/'.rawurlencode(self::clean_id($r['id'])).'/effects','POST',self::body($r)); }
    public static function workspaces_list(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces'.self::project_query($r)); }
    public static function workspace_create(WP_REST_Request $r) { $b=self::body($r); $p=self::clean_id(isset($b['project_id'])?$b['project_id']:''); return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/projects/'.rawurlencode($p).'/workspaces','POST',$b); }
    public static function workspace_get(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id']))); }
    public static function workspace_study_add(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/studies','POST',self::body($r)); }
    public static function workspace_freeze(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/freeze','POST',array()); }
    public static function assessment(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/studies/'.rawurlencode(self::clean_id($r['study'])).'/assessment','POST',self::body($r)); }
    public static function synthesis(WP_REST_Request $r) { $metric=sanitize_text_field((string)$r->get_param('metric_key')); $suffix=$metric?'?metric_key='.rawurlencode($metric):''; return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/synthesis'.$suffix); }
    public static function matrix(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/matrix'); }
    public static function handoff(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/studies/'.rawurlencode(self::clean_id($r['study'])).'/replication-handoff'); }
    public static function manifest(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/manifest'); }
    public static function timeline(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/timeline'); }
    public static function archive(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/workspaces/'.rawurlencode(self::clean_id($r['id'])).'/archive','POST',array()); }
    public static function verify_manifest(WP_REST_Request $r) { return self::proxy('/v1/cross-study-replication-meta-experiment/v01570/manifests/verify','POST',self::body($r)); }
}
