<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Python_Compute_Core_V0260 {
    const VERSION = '0.26.0';
    const NAMESPACE = 'sc-lab/v1';

    public static function init() {
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function routes() {
        register_rest_route(self::NAMESPACE, '/compute/core/health', array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/capabilities', array('methods'=>'GET','callback'=>array(__CLASS__,'capabilities'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/methods', array('methods'=>'GET','callback'=>array(__CLASS__,'methods'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/methods/(?P<method>[A-Za-z0-9._-]{1,128})', array('methods'=>'GET','callback'=>array(__CLASS__,'method'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/run', array('methods'=>'POST','callback'=>array(__CLASS__,'run'),'permission_callback'=>'__return_true'));
    }

    private static function settings() {
        return wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
    }

    private static function rate_limit() {
        $ip = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : 'unknown';
        $key = 'sc_lab_core_rate_' . md5($ip . gmdate('YmdHi'));
        $count = (int) get_transient($key);
        if ($count >= 30) { return new WP_Error('compute_rate_limited','Too many Python Compute Core requests. Try again in a minute.',array('status'=>429)); }
        set_transient($key, $count + 1, 2 * MINUTE_IN_SECONDS);
        return true;
    }

    public static function signed_headers($path, $method, $body, $settings = null) {
        $settings = is_array($settings) ? $settings : self::settings();
        $headers = array('Accept'=>'application/json','Content-Type'=>'application/json','X-SC-Lab-Client'=>isset($settings['compute_client_id']) ? $settings['compute_client_id'] : 'sustainable-catalyst-wordpress');
        if (!empty($settings['compute_api_key'])) { $headers['X-SC-Lab-Key'] = $settings['compute_api_key']; }
        if (!empty($settings['compute_signing_secret'])) {
            $timestamp = (string) time();
            $digest = hash('sha256', (string) $body);
            $canonical = $timestamp . "\n" . strtoupper($method) . "\n" . $path . "\n" . $digest;
            $headers['X-SC-Lab-Timestamp'] = $timestamp;
            $headers['X-SC-Lab-Signature'] = hash_hmac('sha256', $canonical, $settings['compute_signing_secret']);
        }
        return $headers;
    }

    private static function proxy($path, $method = 'GET', $payload = null, $limit = 2097152) {
        $limited = self::rate_limit(); if (is_wp_error($limited)) { return $limited; }
        $settings = self::settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return new WP_Error('compute_disabled','The Python Compute Core is not enabled or configured.',array('status'=>503)); }
        $body = null === $payload ? '' : wp_json_encode($payload);
        $url = untrailingslashit($settings['compute_backend_url']) . $path;
        $args = array('method'=>$method,'timeout'=>max(5,min(120,absint($settings['compute_timeout_seconds']))),'redirection'=>2,'sslverify'=>!empty($settings['compute_verify_ssl']),'headers'=>self::signed_headers($path,$method,$body,$settings),'limit_response_size'=>max(262144,min(8388608,absint($limit))));
        if (null !== $payload) { $args['body']=$body; }
        $response = wp_safe_remote_request($url,$args);
        if (is_wp_error($response)) { return new WP_Error('python_compute_unavailable',$response->get_error_message(),array('status'=>502)); }
        $status=wp_remote_retrieve_response_code($response); $decoded=json_decode(wp_remote_retrieve_body($response),true);
        if (!is_array($decoded)) { $decoded=array('detail'=>'The Python Compute Core returned an invalid JSON response.'); $status=502; }
        return new WP_REST_Response($decoded,$status);
    }

    private static function sanitize_tree($value, $depth = 0, &$nodes = 0) {
        $nodes++;
        if ($nodes > 5000 || $depth > 10) { return new WP_Error('compute_payload_too_complex','The compute payload is too complex.',array('status'=>422)); }
        if (is_null($value) || is_bool($value)) { return $value; }
        if (is_int($value) || is_float($value)) { return is_finite((float)$value) ? $value : null; }
        if (is_string($value)) { return substr(wp_strip_all_tags($value,true),0,2048); }
        if (!is_array($value)) { return null; }
        if (count($value) > 100000) { return new WP_Error('compute_array_too_large','A compute array exceeds the 100,000-item foundation limit.',array('status'=>422)); }
        $clean=array();
        foreach ($value as $key=>$item) {
            $clean_key=is_int($key)?$key:substr(preg_replace('/[^A-Za-z0-9._-]/','',(string)$key),0,128);
            if ($clean_key==='') { continue; }
            $child=self::sanitize_tree($item,$depth+1,$nodes); if(is_wp_error($child)){return $child;} $clean[$clean_key]=$child;
        }
        return $clean;
    }

    public static function health() { return self::proxy('/health'); }
    public static function capabilities() { return self::proxy('/v1/capabilities'); }
    public static function methods() { return self::proxy('/v1/methods'); }
    public static function method(WP_REST_Request $request) { return self::proxy('/v1/methods/' . rawurlencode(sanitize_text_field($request['method']))); }
    public static function run(WP_REST_Request $request) {
        $body=$request->get_json_params(); if(!is_array($body)){return new WP_Error('invalid_compute_request','A JSON compute request is required.',array('status'=>422));}
        $method=isset($body['method'])?preg_replace('/[^A-Za-z0-9._-]/','',(string)$body['method']):'';
        if($method===''){return new WP_Error('invalid_compute_method','A registered method identifier is required.',array('status'=>422));}
        $nodes=0; $inputs=self::sanitize_tree(isset($body['inputs'])?$body['inputs']:array(),0,$nodes); if(is_wp_error($inputs)){return $inputs;}
        $nodes=0; $parameters=self::sanitize_tree(isset($body['parameters'])?$body['parameters']:array(),0,$nodes); if(is_wp_error($parameters)){return $parameters;}
        $payload=array('method'=>$method,'inputs'=>$inputs,'parameters'=>$parameters,'units'=>isset($body['units'])&&is_array($body['units'])?array_map('sanitize_text_field',$body['units']):array(),'project_id'=>isset($body['project_id'])?sanitize_text_field($body['project_id']):null,'requested_outputs'=>isset($body['requested_outputs'])&&is_array($body['requested_outputs'])?array_slice(array_map('sanitize_key',$body['requested_outputs']),0,16):array('summary','values'),'execution_target'=>'automatic');
        if(isset($body['version'])){$payload['version']=sanitize_text_field($body['version']);}
        if(isset($body['random_seed'])&&is_numeric($body['random_seed'])){$payload['random_seed']=(int)$body['random_seed'];}
        return self::proxy('/v1/compute/run','POST',$payload,4194304);
    }
}
