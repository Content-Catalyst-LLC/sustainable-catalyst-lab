<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Python_Compute_Core_V0261 {
    const VERSION = '0.26.1';
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
        register_rest_route(self::NAMESPACE, '/compute/core/jobs', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'jobs_list'),'permission_callback'=>'__return_true'),
            array('methods'=>'POST','callback'=>array(__CLASS__,'job_create'),'permission_callback'=>'__return_true'),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})', array(
            array('methods'=>'GET','callback'=>array(__CLASS__,'job_status'),'permission_callback'=>'__return_true'),
            array('methods'=>'DELETE','callback'=>array(__CLASS__,'job_cancel'),'permission_callback'=>'__return_true'),
        ));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/cancel', array('methods'=>'POST','callback'=>array(__CLASS__,'job_cancel_post'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/retry', array('methods'=>'POST','callback'=>array(__CLASS__,'job_retry'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/workers', array('methods'=>'GET','callback'=>array(__CLASS__,'workers'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/queue/status', array('methods'=>'GET','callback'=>array(__CLASS__,'queue_status'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks', array('methods'=>'GET','callback'=>array(__CLASS__,'benchmarks'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/(?P<benchmark>[A-Za-z0-9._-]{1,128})', array('methods'=>'GET','callback'=>array(__CLASS__,'benchmark'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/run', array('methods'=>'POST','callback'=>array(__CLASS__,'benchmark_run'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/run-suite', array('methods'=>'POST','callback'=>array(__CLASS__,'benchmark_suite'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE, '/compute/core/benchmarks/convergence', array('methods'=>'POST','callback'=>array(__CLASS__,'benchmark_convergence'),'permission_callback'=>'__return_true'));
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

    private static function proxy($path, $method = 'GET', $payload = null, $limit = 2097152, $signature_path = null) {
        $limited = self::rate_limit(); if (is_wp_error($limited)) { return $limited; }
        $settings = self::settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return new WP_Error('compute_disabled','The Python Compute Core is not enabled or configured.',array('status'=>503)); }
        $body = null === $payload ? '' : wp_json_encode($payload);
        $url = untrailingslashit($settings['compute_backend_url']) . $path;
        $args = array('method'=>$method,'timeout'=>max(5,min(120,absint($settings['compute_timeout_seconds']))),'redirection'=>2,'sslverify'=>!empty($settings['compute_verify_ssl']),'headers'=>self::signed_headers($signature_path ? $signature_path : $path,$method,$body,$settings),'limit_response_size'=>max(262144,min(8388608,absint($limit))));
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

    private static function clean_job_request($body) {
        if (!is_array($body)) { return new WP_Error('invalid_compute_job','A JSON compute job request is required.',array('status'=>422)); }
        $source = isset($body['request']) && is_array($body['request']) ? $body['request'] : (isset($body['execute']) && is_array($body['execute']) ? $body['execute'] : $body);
        $method = isset($source['method']) ? preg_replace('/[^A-Za-z0-9._-]/','',(string)$source['method']) : (isset($source['methodId']) ? preg_replace('/[^A-Za-z0-9._-]/','',(string)$source['methodId']) : '');
        if ($method === '') { return new WP_Error('invalid_compute_method','A registered method identifier is required.',array('status'=>422)); }
        $nodes=0; $inputs=self::sanitize_tree(isset($source['inputs'])?$source['inputs']:array(),0,$nodes); if(is_wp_error($inputs)){return $inputs;}
        $nodes=0; $parameters=self::sanitize_tree(isset($source['parameters'])?$source['parameters']:array(),0,$nodes); if(is_wp_error($parameters)){return $parameters;}
        $request=array(
            'method'=>$method,
            'inputs'=>$inputs,
            'parameters'=>$parameters,
            'units'=>isset($source['units'])&&is_array($source['units'])?array_map('sanitize_text_field',$source['units']):array(),
            'project_id'=>isset($source['project_id'])?sanitize_text_field($source['project_id']):(isset($source['projectId'])?sanitize_text_field($source['projectId']):null),
            'requested_outputs'=>isset($source['requested_outputs'])&&is_array($source['requested_outputs'])?array_slice(array_map('sanitize_key',$source['requested_outputs']),0,16):array('summary','values'),
            'execution_target'=>'automatic',
        );
        if(isset($source['version'])){$request['version']=sanitize_text_field($source['version']);}
        if(isset($source['random_seed'])&&is_numeric($source['random_seed'])){$request['random_seed']=(int)$source['random_seed'];}
        if(isset($source['randomSeed'])&&is_numeric($source['randomSeed'])){$request['random_seed']=(int)$source['randomSeed'];}
        $payload=array('operation'=>'core_run','request'=>$request);
        if(isset($body['idempotencyKey'])){$payload['idempotencyKey']=substr(sanitize_text_field($body['idempotencyKey']),0,128);}
        if(isset($body['timeoutSeconds'])){$payload['timeoutSeconds']=max(1,min(900,absint($body['timeoutSeconds'])));}
        if(isset($body['maxAttempts'])){$payload['maxAttempts']=max(1,min(5,absint($body['maxAttempts'])));}
        return $payload;
    }

    public static function jobs_list(WP_REST_Request $request) {
        $query=array();
        if($request->get_param('status')){$query['status']=sanitize_key($request->get_param('status'));}
        if($request->get_param('project_id')){$query['project_id']=sanitize_text_field($request->get_param('project_id'));}
        $query['limit']=max(1,min(200,absint($request->get_param('limit')?:50)));
        $query['offset']=max(0,absint($request->get_param('offset')?:0));
        return self::proxy('/v1/jobs?' . http_build_query($query,'','&'),'GET',null,4194304,'/v1/jobs');
    }
    public static function job_create(WP_REST_Request $request) {
        $payload=self::clean_job_request($request->get_json_params());
        return is_wp_error($payload)?$payload:self::proxy('/v1/jobs','POST',$payload,4194304);
    }
    public static function job_status(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job'])); }
    public static function job_cancel(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']),'DELETE'); }
    public static function job_cancel_post(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/cancel','POST',array()); }
    public static function job_retry(WP_REST_Request $request) { return self::proxy('/v1/jobs/' . rawurlencode($request['job']) . '/retry','POST',array()); }
    public static function workers() { return self::proxy('/v1/workers'); }
    public static function queue_status() { return self::proxy('/v1/queue/status'); }
    public static function benchmarks() { return self::proxy('/v1/benchmarks'); }
    public static function benchmark(WP_REST_Request $request) {
        $id = preg_replace('/[^A-Za-z0-9._-]/', '', (string)$request['benchmark']);
        return self::proxy('/v1/benchmarks/' . rawurlencode($id));
    }
    private static function benchmark_payload(WP_REST_Request $request, $suite = false) {
        $body = $request->get_json_params();
        $body = is_array($body) ? $body : array();
        if ($suite) {
            $ids = isset($body['benchmarkIds']) && is_array($body['benchmarkIds']) ? array_slice($body['benchmarkIds'], 0, 100) : array();
            return array('benchmarkIds'=>array_values(array_filter(array_map(function($id){ return preg_replace('/[^A-Za-z0-9._-]/','',(string)$id); }, $ids))));
        }
        $id = isset($body['benchmarkId']) ? preg_replace('/[^A-Za-z0-9._-]/','',(string)$body['benchmarkId']) : '';
        if ($id === '') { return new WP_Error('invalid_benchmark','A benchmarkId is required.',array('status'=>422)); }
        return array('benchmarkId'=>$id);
    }
    public static function benchmark_run(WP_REST_Request $request) {
        $payload=self::benchmark_payload($request); if(is_wp_error($payload)){return $payload;}
        return self::proxy('/v1/benchmarks/run','POST',$payload,8388608);
    }
    public static function benchmark_suite(WP_REST_Request $request) {
        $payload=self::benchmark_payload($request,true); if(is_wp_error($payload)){return $payload;}
        return self::proxy('/v1/benchmarks/run-suite','POST',$payload,8388608);
    }
    public static function benchmark_convergence(WP_REST_Request $request) {
        $payload=self::benchmark_payload($request); if(is_wp_error($payload)){return $payload;}
        return self::proxy('/v1/benchmarks/convergence','POST',$payload,8388608);
    }

}
