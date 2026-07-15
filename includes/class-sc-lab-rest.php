<?php
if (!defined('ABSPATH')) { exit; }

class SC_Lab_REST {
    public function __construct() { add_action('rest_api_init', array($this, 'routes')); }

    public function routes() {
        register_rest_route('sc-lab/v1', '/status', array('methods'=>'GET','callback'=>array($this,'status'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/sources/status', array('methods'=>'GET','callback'=>array($this,'source_status'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/sources', array('methods'=>'GET','callback'=>array($this,'sources'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/feeds/(?P<source>[a-z0-9-]+)', array('methods'=>'GET','callback'=>array($this,'feed'),'permission_callback'=>'__return_true','args'=>array('source'=>array('sanitize_callback'=>'sanitize_key'))));

        register_rest_route('sc-lab/v1', '/compute/status', array('methods'=>'GET','callback'=>array($this,'compute_status'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/languages', array('methods'=>'GET','callback'=>array($this,'compute_languages'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/methods', array('methods'=>'GET','callback'=>array($this,'compute_methods'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/execute', array('methods'=>'POST','callback'=>array($this,'compute_execute'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/compare', array('methods'=>'POST','callback'=>array($this,'compute_compare'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/reports/validate', array('methods'=>'POST','callback'=>array($this,'compute_report_validate'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/reports/pdf', array('methods'=>'POST','callback'=>array($this,'compute_report_pdf'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/handoffs/decision-studio/validate', array('methods'=>'POST','callback'=>array($this,'compute_handoff_validate'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/jobs', array(
            array('methods'=>'GET','callback'=>array($this,'compute_jobs_list'),'permission_callback'=>'__return_true'),
            array('methods'=>'POST','callback'=>array($this,'compute_jobs'),'permission_callback'=>'__return_true'),
        ));
        register_rest_route('sc-lab/v1', '/compute/jobs/(?P<job>[a-zA-Z0-9-]{8,64})', array(
            array('methods'=>'GET','callback'=>array($this,'compute_job_status'),'permission_callback'=>'__return_true'),
            array('methods'=>'DELETE','callback'=>array($this,'compute_job_cancel'),'permission_callback'=>'__return_true'),
        ));
        register_rest_route('sc-lab/v1', '/compute/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/cancel', array('methods'=>'POST','callback'=>array($this,'compute_job_cancel_post'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/retry', array('methods'=>'POST','callback'=>array($this,'compute_job_retry'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/pause', array('methods'=>'POST','callback'=>array($this,'compute_job_pause'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/resume', array('methods'=>'POST','callback'=>array($this,'compute_job_resume'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/jobs/(?P<job>[a-zA-Z0-9-]{8,64})/checkpoints', array('methods'=>'GET','callback'=>array($this,'compute_job_checkpoints'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/queue/status', array('methods'=>'GET','callback'=>array($this,'compute_queue_status'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/compute/workers', array('methods'=>'GET','callback'=>array($this,'compute_workers'),'permission_callback'=>'__return_true'));


        register_rest_route(
            'sc-lab/v1',
            '/compute/civil/methods',
            array(
                'methods'             => 'GET',
                'callback'            => array($this, 'compute_civil_methods'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            'sc-lab/v1',
            '/compute/civil/run',
            array(
                'methods'             => 'POST',
                'callback'            => array($this, 'compute_civil_run'),
                'permission_callback' => '__return_true',
            )
        );

}

    private function settings() { return wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults()); }

    public function status() {
        $settings = $this->settings();
        return rest_ensure_response(array(
            'ok'=>true,
            'version'=>SC_LAB_VERSION,
            'time'=>gmdate('c'),
            'compute'=>array('enabled'=>!empty($settings['enable_remote_compute']),'configured'=>!empty($settings['compute_backend_url'])),
            'modules'=>array('scientificFeeds','climateMaps','spaceTelescopes','marineBiology','chemistry','spectrometry','calculators','experiments','evidence','notebook','documentation','commandSearch','interactiveTraceability','projectActivity','datasetInspector','observationBoard','sourceRegistry','mapViews','universalVisualization','dimensionalScenes','workspaceDataManagement','methodContracts','codeSwitcher','stablePluginIdentity','renderComputeDispatcher','multiLanguageWorkers','crossLanguageValidation','pdfReports','decisionStudioReportHandoff','reportPacketValidation','reportComposer','visualizationAccessibility','restoreValidation','migrationValidation','pythonComputeCore','registeredMethodRegistry','computeProvenance','hmacRequestSigning','persistentJobQueue','isolatedComputeWorkers','jobRetryPolicy','jobCancellation','workerHealthMonitoring')
        ));
    }

    public function source_status() {
        $registry = SC_Lab_Feeds::registry(); $rows = array();
        foreach ($registry as $id => $meta) { $health = get_transient('sc_lab_health_' . md5($id)); $rows[$id] = array_merge($meta, is_array($health) ? $health : array('status'=>'not_checked','lastChecked'=>null,'message'=>'Run a query to test this connector.')); }
        return rest_ensure_response(array('sources'=>$rows,'retrievedAt'=>gmdate('c')));
    }
    public function sources() { return rest_ensure_response(array('sources'=>SC_Lab_Feeds::registry(),'retrievedAt'=>gmdate('c'))); }

    public function feed(WP_REST_Request $request) {
        $source = $request['source'];
        if (!isset(SC_Lab_Feeds::registry()[$source])) { return new WP_Error('unknown_source','Unknown scientific source.',array('status'=>404)); }
        $settings = $this->settings();
        if (empty($settings['enable_feeds'])) { return new WP_Error('feeds_disabled','Scientific feeds are disabled.',array('status'=>503)); }
        $params = $request->get_params(); unset($params['source']);
        $cache_key = 'sc_lab_' . md5($source . wp_json_encode($params)); $cached = get_transient($cache_key);
        if (false !== $cached) { return rest_ensure_response(array('source'=>$source,'cached'=>true,'records'=>$cached,'retrievedAt'=>gmdate('c'))); }
        $records = SC_Lab_Feeds::fetch($source, $params);
        if (is_wp_error($records)) { set_transient('sc_lab_health_' . md5($source), array('status'=>'error','lastChecked'=>gmdate('c'),'message'=>$records->get_error_message()), DAY_IN_SECONDS); return $records; }
        set_transient('sc_lab_health_' . md5($source), array('status'=>'ready','lastChecked'=>gmdate('c'),'message'=>count($records) . ' records returned'), DAY_IN_SECONDS);
        set_transient($cache_key, $records, max(5, absint($settings['cache_minutes'])) * MINUTE_IN_SECONDS);
        return rest_ensure_response(array('source'=>$source,'cached'=>false,'records'=>$records,'retrievedAt'=>gmdate('c')));
    }

    private function compute_rate_limit() {
        $ip = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : 'unknown';
        $key = 'sc_lab_compute_rate_' . md5($ip . gmdate('YmdHi'));
        $count = (int) get_transient($key);
        if ($count >= 120) { return new WP_Error('compute_rate_limited','Too many compute requests. Try again in a minute.',array('status'=>429)); }
        set_transient($key, $count + 1, 2 * MINUTE_IN_SECONDS);
        return true;
    }

    private function compute_ready() {
        $settings = $this->settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return new WP_Error('compute_disabled','The Python Compute Core is not enabled or configured.',array('status'=>503)); }
        return $settings;
    }

    private function clean_identifier($value, $lowercase = false) {
        $text = sanitize_text_field((string) $value);
        $text = preg_replace('/[^A-Za-z0-9._-]/', '', $text);
        if ($lowercase) { $text = strtolower($text); }
        return substr($text, 0, 96);
    }

    private function clean_inputs($inputs) {
        if (!is_array($inputs) || count($inputs) > 64) { return new WP_Error('invalid_inputs','Inputs must be a numerical object with no more than 64 fields.',array('status'=>422)); }
        $clean = array();
        foreach ($inputs as $key => $value) {
            $name = $this->clean_identifier($key, false);
            if ($name === '' || !is_numeric($value) || !is_finite((float) $value)) { return new WP_Error('invalid_inputs','Every compute input must have a valid key and finite numerical value.',array('status'=>422)); }
            $clean[$name] = (float) $value;
        }
        return $clean;
    }

    private function clean_execute_payload($body) {
        if (!is_array($body)) { return new WP_Error('invalid_payload','A JSON object is required.',array('status'=>422)); }
        $method = isset($body['methodId']) ? $this->clean_identifier($body['methodId'], true) : '';
        $language = isset($body['language']) ? sanitize_key($body['language']) : '';
        $allowed = array('python','r','julia','javascript','typescript','sql','c','cpp','fortran','rust','go','haskell');
        if ($method === '' || !in_array($language, $allowed, true)) { return new WP_Error('invalid_payload','A valid methodId and language are required.',array('status'=>422)); }
        $inputs = $this->clean_inputs(isset($body['inputs']) ? $body['inputs'] : array()); if (is_wp_error($inputs)) { return $inputs; }
        return array('methodId'=>$method,'language'=>$language,'inputs'=>$inputs,'timeoutSeconds'=>max(1,min(20,absint(isset($body['timeoutSeconds'])?$body['timeoutSeconds']:8))),'includeSource'=>!empty($body['includeSource']));
    }

    private function clean_compare_payload($body) {
        if (!is_array($body)) { return new WP_Error('invalid_payload','A JSON object is required.',array('status'=>422)); }
        $method = isset($body['methodId']) ? $this->clean_identifier($body['methodId'], true) : '';
        $allowed = array('python','r','julia','javascript','typescript','sql','c','cpp','fortran','rust','go','haskell');
        $languages = array(); foreach ((array) (isset($body['languages']) ? $body['languages'] : array()) as $language) { $language = sanitize_key($language); if (in_array($language,$allowed,true) && !in_array($language,$languages,true)) { $languages[]=$language; } }
        $languages = array_slice($languages,0,8);
        if ($method === '' || !$languages) { return new WP_Error('invalid_payload','A valid methodId and one to eight languages are required.',array('status'=>422)); }
        $inputs = $this->clean_inputs(isset($body['inputs']) ? $body['inputs'] : array()); if (is_wp_error($inputs)) { return $inputs; }
        return array('methodId'=>$method,'languages'=>$languages,'inputs'=>$inputs,'timeoutSeconds'=>max(1,min(20,absint(isset($body['timeoutSeconds'])?$body['timeoutSeconds']:8))),'includeSource'=>!empty($body['includeSource']),'absoluteTolerance'=>isset($body['absoluteTolerance'])?(float)$body['absoluteTolerance']:1e-10,'relativeTolerance'=>isset($body['relativeTolerance'])?(float)$body['relativeTolerance']:1e-9);
    }

    private function clean_report_value($value, $depth = 0, &$nodes = 0) {
        $nodes++;
        if ($nodes > 2400 || $depth > 8) { return new WP_Error('report_too_complex','The report payload is too complex.',array('status'=>422)); }
        if (is_null($value) || is_bool($value)) { return $value; }
        if (is_int($value) || is_float($value)) { return is_finite((float) $value) ? $value : null; }
        if (is_string($value)) { return substr(wp_strip_all_tags($value, true), 0, 12000); }
        if (!is_array($value)) { return null; }
        $clean = array();
        foreach ($value as $key => $item) {
            $clean_key = is_int($key) ? $key : substr(preg_replace('/[^A-Za-z0-9._-]/', '', (string) $key), 0, 96);
            if ($clean_key === '') { continue; }
            $clean_item = $this->clean_report_value($item, $depth + 1, $nodes);
            if (is_wp_error($clean_item)) { return $clean_item; }
            $clean[$clean_key] = $clean_item;
        }
        return $clean;
    }

    private function clean_report_payload($body) {
        if (!is_array($body)) { return new WP_Error('invalid_report','A report JSON object is required.',array('status'=>422)); }
        $nodes = 0;
        $clean = $this->clean_report_value($body, 0, $nodes);
        if (is_wp_error($clean)) { return $clean; }
        $title = isset($clean['title']) ? sanitize_text_field($clean['title']) : '';
        $analyses = isset($clean['analyses']) && is_array($clean['analyses']) ? array_values($clean['analyses']) : array();
        if ($title === '' || !$analyses || count($analyses) > 12) { return new WP_Error('invalid_report','A title and one to twelve analyses are required.',array('status'=>422)); }
        $types = array('technical-report','decision-brief','evidence-packet','executive-summary');
        $clean['title'] = substr($title, 0, 240);
        $clean['reportType'] = in_array(isset($clean['reportType']) ? $clean['reportType'] : '', $types, true) ? $clean['reportType'] : 'technical-report';
        $clean['pageSize'] = (isset($clean['pageSize']) && $clean['pageSize'] === 'A4') ? 'A4' : 'LETTER';
        $clean['analyses'] = $analyses;
        $clean['includeAudit'] = !isset($clean['includeAudit']) || !empty($clean['includeAudit']);
        return $clean;
    }

    private function clean_handoff_payload($body) {
        if (!is_array($body) || !isset($body['packet']) || !is_array($body['packet'])) { return new WP_Error('invalid_handoff','A Decision Studio packet is required.',array('status'=>422)); }
        $nodes = 0;
        $packet = $this->clean_report_value($body['packet'], 0, $nodes);
        if (is_wp_error($packet)) { return $packet; }
        return array('packet'=>$packet);
    }

    private function proxy($path, $method='GET', $payload=null, $response_limit=262144) {
        $limited = $this->compute_rate_limit(); if (is_wp_error($limited)) { return $limited; }
        $settings = $this->compute_ready(); if (is_wp_error($settings)) { return $settings; }
        $url = untrailingslashit($settings['compute_backend_url']) . '/' . ltrim($path,'/');
        $raw_body = null === $payload ? '' : wp_json_encode($payload);
        $signature_path = '/' . ltrim((string) strtok($path, '?'), '/');
        $headers = class_exists('SC_Lab_Python_Compute_Core_V0261') ? SC_Lab_Python_Compute_Core_V0261::signed_headers($signature_path, $method, $raw_body, $settings) : array('Accept'=>'application/json','Content-Type'=>'application/json');
        if (!empty($settings['compute_api_key']) && empty($headers['X-SC-Lab-Key'])) { $headers['X-SC-Lab-Key'] = $settings['compute_api_key']; }
        $args = array('method'=>$method,'timeout'=>max(5,min(60,absint($settings['compute_timeout_seconds']))),'redirection'=>2,'sslverify'=>!empty($settings['compute_verify_ssl']),'headers'=>$headers,'limit_response_size'=>max(262144,min(8388608,absint($response_limit))));
        if (null !== $payload) { $args['body'] = $raw_body; }
        $response = wp_safe_remote_request($url,$args);
        if (is_wp_error($response)) { return new WP_Error('compute_unavailable',$response->get_error_message(),array('status'=>502)); }
        $status = wp_remote_retrieve_response_code($response); $raw = wp_remote_retrieve_body($response); $decoded = json_decode($raw,true);
        if (!is_array($decoded)) { $decoded = array('error'=>array('code'=>'invalid_backend_response','message'=>'The compute service returned an invalid response.')); }
        return new WP_REST_Response($decoded,$status);
    }

    public function compute_status() {
        $settings = $this->settings();
        if (empty($settings['enable_remote_compute']) || empty($settings['compute_backend_url'])) { return rest_ensure_response(array('ok'=>false,'configured'=>false,'enabled'=>!empty($settings['enable_remote_compute']),'message'=>'Configure the Python Compute Core under Settings → Sustainable Catalyst Lab.')); }
        return $this->proxy('/health');
    }
    public function compute_languages() { return $this->proxy('/v1/languages'); }
    public function compute_methods() { return $this->proxy('/v1/methods'); }
    public function compute_execute(WP_REST_Request $request) { $payload=$this->clean_execute_payload($request->get_json_params()); return is_wp_error($payload)?$payload:$this->proxy('/v1/execute','POST',$payload); }
    public function compute_compare(WP_REST_Request $request) { $payload=$this->clean_compare_payload($request->get_json_params()); return is_wp_error($payload)?$payload:$this->proxy('/v1/compare','POST',$payload); }
    public function compute_report_validate(WP_REST_Request $request) { $payload=$this->clean_report_payload($request->get_json_params()); return is_wp_error($payload)?$payload:$this->proxy('/v1/reports/validate','POST',$payload,1048576); }
    public function compute_report_pdf(WP_REST_Request $request) { $payload=$this->clean_report_payload($request->get_json_params()); return is_wp_error($payload)?$payload:$this->proxy('/v1/reports/pdf','POST',$payload,8388608); }
    public function compute_handoff_validate(WP_REST_Request $request) { $payload=$this->clean_handoff_payload($request->get_json_params()); return is_wp_error($payload)?$payload:$this->proxy('/v1/handoffs/decision-studio/validate','POST',$payload,1048576); }
    public function compute_jobs(WP_REST_Request $request) {
        $body=$request->get_json_params(); $operation=isset($body['operation'])?sanitize_key($body['operation']):'';
        $options=array();
        if(isset($body['idempotencyKey'])){$options['idempotencyKey']=substr(sanitize_text_field($body['idempotencyKey']),0,128);}
        if(isset($body['timeoutSeconds'])){$options['timeoutSeconds']=max(1,min(900,absint($body['timeoutSeconds'])));}
        if(isset($body['maxAttempts'])){$options['maxAttempts']=max(1,min(5,absint($body['maxAttempts'])));}
        if(isset($body['priority'])){$options['priority']=max(0,min(100,absint($body['priority'])));}
        if(isset($body['cacheMode'])){$mode=sanitize_key($body['cacheMode']);$options['cacheMode']=in_array($mode,array('use','refresh','bypass'),true)?$mode:'use';}
        if ($operation==='execute') { $payload=$this->clean_execute_payload(isset($body['execute'])?$body['execute']:array()); if(is_wp_error($payload)){return $payload;} return $this->proxy('/v1/jobs','POST',array_merge(array('operation'=>'execute','execute'=>$payload),$options)); }
        if ($operation==='compare') { $payload=$this->clean_compare_payload(isset($body['compare'])?$body['compare']:array()); if(is_wp_error($payload)){return $payload;} return $this->proxy('/v1/jobs','POST',array_merge(array('operation'=>'compare','compare'=>$payload),$options)); }
        if ($operation==='core_run') { return SC_Lab_Python_Compute_Core_V0261::job_create($request); }
        return new WP_Error('invalid_job','Job operation must be execute, compare, or core_run.',array('status'=>422));
    }
    public function compute_jobs_list(WP_REST_Request $request) {
        $query=array('limit'=>max(1,min(200,absint($request->get_param('limit')?:50))),'offset'=>max(0,absint($request->get_param('offset')?:0)));
        if($request->get_param('status')){$query['status']=sanitize_key($request->get_param('status'));}
        if($request->get_param('project_id')){$query['project_id']=sanitize_text_field($request->get_param('project_id'));}
        return $this->proxy('/v1/jobs?' . http_build_query($query,'','&'));
    }
    public function compute_job_status(WP_REST_Request $request) { return $this->proxy('/v1/jobs/' . rawurlencode($request['job'])); }
    public function compute_job_cancel(WP_REST_Request $request) { return $this->proxy('/v1/jobs/' . rawurlencode($request['job']),'DELETE'); }
    public function compute_job_cancel_post(WP_REST_Request $request) { return $this->proxy('/v1/jobs/' . rawurlencode($request['job']) . '/cancel','POST',array()); }
    public function compute_job_retry(WP_REST_Request $request) { return $this->proxy('/v1/jobs/' . rawurlencode($request['job']) . '/retry','POST',array()); }
    public function compute_job_pause(WP_REST_Request $request) { return $this->proxy('/v1/jobs/' . rawurlencode($request['job']) . '/pause','POST',array()); }
    public function compute_job_resume(WP_REST_Request $request) { return $this->proxy('/v1/jobs/' . rawurlencode($request['job']) . '/resume','POST',array()); }
    public function compute_job_checkpoints(WP_REST_Request $request) { $limit=max(1,min(200,absint($request->get_param('limit')?:20))); return $this->proxy('/v1/jobs/' . rawurlencode($request['job']) . '/checkpoints?limit=' . $limit); }
    public function compute_queue_status() { return $this->proxy('/v1/queue/status'); }
    public function compute_workers() { return $this->proxy('/v1/workers'); }


    /**
     * Proxy the v0.12.0 civil and infrastructure method catalog.
     *
     * @return mixed
     */
    public function compute_civil_methods() {
        if (method_exists($this, 'proxy')) {
            return $this->proxy('/v1/civil/methods');
        }

        return new WP_Error(
            'sc_lab_backend_proxy_unavailable',
            'The Lab backend proxy is unavailable.',
            array('status' => 503)
        );
    }

    /**
     * Proxy one v0.12.0 civil and infrastructure calculation.
     *
     * @param mixed $request REST request.
     * @return mixed
     */
    public function compute_civil_run($request) {
        $body = is_object($request) && method_exists($request, 'get_json_params')
            ? $request->get_json_params()
            : array();

        if (!is_array($body)) {
            return new WP_Error(
                'sc_lab_invalid_payload',
                'A JSON object is required.',
                array('status' => 422)
            );
        }

        $method_id = isset($body['methodId'])
            ? sanitize_text_field((string) $body['methodId'])
            : '';

        if ($method_id === '' || strpos($method_id, 'ci.') !== 0) {
            return new WP_Error(
                'sc_lab_invalid_civil_method',
                'A valid civil methodId beginning with ci. is required.',
                array('status' => 422)
            );
        }

        $raw_inputs = isset($body['inputs']) && is_array($body['inputs'])
            ? $body['inputs']
            : array();

        $inputs = array();

        foreach ($raw_inputs as $key => $value) {
            if (!is_numeric($value)) {
                return new WP_Error(
                    'sc_lab_invalid_civil_input',
                    'Civil and infrastructure inputs must be numeric.',
                    array('status' => 422)
                );
            }

            $inputs[sanitize_key((string) $key)] = (float) $value;
        }

        if (method_exists($this, 'proxy')) {
            return $this->proxy(
                '/v1/civil/run',
                'POST',
                array(
                    'methodId' => $method_id,
                    'inputs'   => $inputs,
                )
            );
        }

        return new WP_Error(
            'sc_lab_backend_proxy_unavailable',
            'The Lab backend proxy is unavailable.',
            array('status' => 503)
        );
    }

}
