<?php
if (!defined('ABSPATH')) { exit; }

class SC_Lab_REST {
    public function __construct() { add_action('rest_api_init', array($this, 'routes')); }

    public function routes() {
        register_rest_route('sc-lab/v1', '/status', array('methods'=>'GET','callback'=>array($this,'status'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/sources/status', array('methods'=>'GET','callback'=>array($this,'source_status'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/sources', array('methods'=>'GET','callback'=>array($this,'sources'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/feeds/(?P<source>[a-z0-9-]+)', array('methods'=>'GET','callback'=>array($this,'feed'),'permission_callback'=>'__return_true','args'=>array('source'=>array('sanitize_callback'=>'sanitize_key'))));
    }

    public function status() {
        return rest_ensure_response(array('ok'=>true,'version'=>SC_LAB_VERSION,'time'=>gmdate('c'),'modules'=>array('scientificFeeds','climateMaps','spaceTelescopes','marineBiology','chemistry','spectrometry','calculators','experiments','evidence','notebook','documentation','commandSearch','interactiveTraceability','projectActivity','datasetInspector','observationBoard','sourceRegistry','mapViews')));
    }

    public function source_status() {
        $registry = SC_Lab_Feeds::registry();
        $rows = array();
        foreach ($registry as $id => $meta) {
            $health = get_transient('sc_lab_health_' . md5($id));
            $rows[$id] = array_merge($meta, is_array($health) ? $health : array('status'=>'not_checked','lastChecked'=>null,'message'=>'Run a query to test this connector.'));
        }
        return rest_ensure_response(array('sources'=>$rows,'retrievedAt'=>gmdate('c')));
    }

    public function sources() { return rest_ensure_response(array('sources'=>SC_Lab_Feeds::registry(),'retrievedAt'=>gmdate('c'))); }

    public function feed(WP_REST_Request $request) {
        $source = $request['source'];
        if (!isset(SC_Lab_Feeds::registry()[$source])) { return new WP_Error('unknown_source','Unknown scientific source.',array('status'=>404)); }
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        if (empty($settings['enable_feeds'])) { return new WP_Error('feeds_disabled','Scientific feeds are disabled.',array('status'=>503)); }
        $params = $request->get_params(); unset($params['source']);
        $cache_key = 'sc_lab_' . md5($source . wp_json_encode($params));
        $cached = get_transient($cache_key);
        if (false !== $cached) { return rest_ensure_response(array('source'=>$source,'cached'=>true,'records'=>$cached,'retrievedAt'=>gmdate('c'))); }
        $records = SC_Lab_Feeds::fetch($source, $params);
        if (is_wp_error($records)) { set_transient('sc_lab_health_' . md5($source), array('status'=>'error','lastChecked'=>gmdate('c'),'message'=>$records->get_error_message()), DAY_IN_SECONDS); return $records; }
        set_transient('sc_lab_health_' . md5($source), array('status'=>'ready','lastChecked'=>gmdate('c'),'message'=>count($records) . ' records returned'), DAY_IN_SECONDS);
        set_transient($cache_key, $records, max(5, absint($settings['cache_minutes'])) * MINUTE_IN_SECONDS);
        return rest_ensure_response(array('source'=>$source,'cached'=>false,'records'=>$records,'retrievedAt'=>gmdate('c')));
    }
}
