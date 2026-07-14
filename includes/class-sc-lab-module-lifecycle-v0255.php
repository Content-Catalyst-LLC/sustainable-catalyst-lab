<?php
/**
 * Sustainable Catalyst Lab v0.25.5 module lifecycle and memory manager.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Module_Lifecycle_V0255 {
    const VERSION = '0.25.5';
    const ROOT_ID = 'sc-lab-v0255-root';
    private static $initialized = false;
    private static $assets = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue'), 1);
        add_action('wp_enqueue_scripts', array(__CLASS__, 'gate_assets'), PHP_INT_MAX);
        add_filter('do_shortcode_tag', array(__CLASS__, 'filter_app'), PHP_INT_MAX, 4);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string)$post->post_content, 'sc_lab_app');
    }

    public static function maybe_enqueue() {
        if (!self::is_lab_request() || self::$assets) { return; }
        self::$assets = true;
        wp_enqueue_style('sc-lab-lifecycle-v0255', SC_LAB_URL.'assets/css/sc-lab-lifecycle-v0255.css', array(), self::VERSION);
        wp_enqueue_script('sc-lab-lifecycle-v0255', SC_LAB_URL.'assets/js/sc-lab-lifecycle-v0255.js', array(), self::VERSION, true);
        wp_localize_script('sc-lab-lifecycle-v0255', 'SCLabLifecycleConfigV0255', array(
            'version'=>self::VERSION,
            'module'=>self::requested_module(),
            'safeStart'=>isset($_GET['sc_lab_safe']),
            'nodeBudget'=>6500,
            'warningBudget'=>5000,
            'healthUrl'=>esc_url_raw(rest_url('sc-lab/v1/runtime/v0255/health')),
        ));
    }

    public static function gate_assets() {
        if (!self::is_lab_request()) { return; }
        $module = self::requested_module();
        $allowed = self::allowed_advanced_files($module);
        $scripts = wp_scripts();
        if ($scripts) {
            foreach ((array)$scripts->queue as $handle) {
                $item = isset($scripts->registered[$handle]) ? $scripts->registered[$handle] : null;
                if (!$item || empty($item->src)) { continue; }
                $base = basename((string)parse_url($item->src, PHP_URL_PATH));
                if (self::is_advanced_script($base) && !in_array($base, $allowed, true)) {
                    wp_dequeue_script($handle);
                }
            }
        }
        $styles = wp_styles();
        if ($styles) {
            foreach ((array)$styles->queue as $handle) {
                $item = isset($styles->registered[$handle]) ? $styles->registered[$handle] : null;
                if (!$item || empty($item->src)) { continue; }
                $base = basename((string)parse_url($item->src, PHP_URL_PATH));
                if (self::is_advanced_style($base) && !in_array($base, $allowed, true)) {
                    wp_dequeue_style($handle);
                }
            }
        }
    }

    private static function is_advanced_script($base) {
        return (bool)preg_match('/(?:architecture-building|urban-planning|sustainable-cities|comparative-economics|aerospace-engineering|rocket-propulsion|microbiology-laboratory|circular-economy|biochemistry-|molecular-analysis|biotechnology-bioprocess|bioprocess-|biomedical-engineering|biosignal-|genetics-genomics|genomics-production|genomic-|laboratory-data-instrumentation|instrumentation-|civil-.*v0200|engineering-interface-repair)/', $base);
    }
    private static function is_advanced_style($base) {
        return (bool)preg_match('/(?:v0130|v0140|v0150|v0160|v0170|v0180|v0190|v0200|v0210|biochemistry-|molecular-analysis|biotechnology-|bioprocess-|biomedical-|biosignal-|genetics-|genomic-|genomics-|laboratory-data-|instrumentation-)/', $base);
    }

    private static function allowed_advanced_files($module) {
        $map = array(
            'architecture-building'=>array('architecture-building-lab.js','sc-lab-v0130.css'),
            'urban-planning-spatial'=>array('urban-planning-spatial-lab.js','sc-lab-v0140.css'),
            'sustainable-cities-resilience'=>array('sustainable-cities-resilience-lab.js','sc-lab-v0160.css'),
            'comparative-economics-development-systems'=>array('comparative-economics-development-systems-lab.js','sc-lab-v0170.css'),
            'aerospace-engineering-flight-systems'=>array('aerospace-engineering-flight-systems-lab.js','sc-lab-v0180.css'),
            'rocket-propulsion-spaceflight'=>array('rocket-propulsion-spaceflight-lab.js','sc-lab-v0190.css'),
            'microbiology-laboratory'=>array('microbiology-laboratory.js','sc-lab-v0200.css'),
            'circular-economy-industrial-ecology'=>array('circular-economy-industrial-ecology-lab.js','sc-lab-v0160.css'),
            'civil-infrastructure'=>array('civil-infrastructure-lab-v0150.js','civil-infrastructure-runtime-v0200.js','civil-infrastructure-direct-loader-v0200.js','civil-panel-router-v0200.js','engineering-interface-repair-v0200.js','sc-lab-v0150.css'),
            'biochemistry-molecular-analysis'=>array('biochemistry-molecular-analysis.js','biochemistry-production-v0211.js','biochemistry-visualization-batch-v0212.js','molecular-analysis-validation-provenance-v0213.js','sc-lab-v0210.css','sc-lab-biochemistry-production-v0211.css','sc-lab-biochemistry-visualization-batch-v0212.css','sc-lab-molecular-analysis-validation-provenance-v0213.css'),
            'biotechnology-bioprocess-engineering'=>array('biotechnology-bioprocess-engineering-v0220.js','bioprocess-production-v0221.js','bioprocess-monitoring-control-v0222.js','bioprocess-validation-provenance-v0223.js','sc-lab-biotechnology-bioprocess-engineering-v0220.css','sc-lab-bioprocess-production-v0221.css','sc-lab-bioprocess-monitoring-control-v0222.css','sc-lab-bioprocess-validation-provenance-v0223.css'),
            'biomedical-engineering-biosignals'=>array('biomedical-engineering-biosignals-v0230.js','biosignal-production-v0231.js','biosignal-visualization-comparison-v0232.js','sc-lab-biomedical-engineering-biosignals-v0230.css','sc-lab-biosignal-production-v0231.css','sc-lab-biosignal-visualization-comparison-v0232.css'),
            'genetics-genomics-sequence-analysis'=>array('genetics-genomics-sequence-analysis-v0240.js','genomics-production-v0241.js','genomic-visualization-comparison-v0242.js','genomic-validation-sequence-provenance-v0243.js','sc-lab-genetics-genomics-v0240.css','sc-lab-genomics-production-v0241.css','sc-lab-genomic-visualization-v0242.css','sc-lab-genomic-validation-v0243.css'),
            'laboratory-data-instrumentation'=>array('laboratory-data-instrumentation-v0250.js','instrumentation-production-v0251.js','instrumentation-live-visualization-v0252.js','instrumentation-validation-custody-v0253.js','sc-lab-laboratory-data-instrumentation-v0250.css','sc-lab-instrumentation-production-v0251.css','sc-lab-instrumentation-live-visualization-v0252.css','sc-lab-instrumentation-validation-custody-v0253.css'),
        );
        return isset($map[$module]) ? $map[$module] : array();
    }

    public static function filter_app($output, $tag, $attr, $match) {
        unset($attr,$match);
        if ($tag !== 'sc_lab_app' || is_admin()) { return $output; }
        self::maybe_enqueue();
        return self::single_module_shell((string)$output, self::requested_module());
    }

    private static function requested_module() {
        if (isset($_GET['sc_lab_safe'])) { return 'overview'; }
        $module = isset($_GET['sc_lab_module']) ? sanitize_key(wp_unslash($_GET['sc_lab_module'])) : 'overview';
        return preg_match('/^[a-z0-9][a-z0-9-]{0,79}$/', $module) ? $module : 'overview';
    }

    private static function single_module_shell($html, $requested) {
        $panels = self::scan_panels($html);
        if (!$panels) { return self::fallback(); }
        $selected = isset($panels[$requested]) ? $requested : (isset($panels['overview']) ? 'overview' : array_key_first($panels));
        uasort($panels, function($a,$b){ return $a['start'] <=> $b['start']; });
        $cursor=0; $body='';
        foreach ($panels as $slug=>$panel) {
            $body .= substr($html,$cursor,$panel['start']-$cursor);
            if ($slug === $selected) { $body .= self::activate($panel['html']); }
            $cursor=$panel['end'];
        }
        $body .= substr($html,$cursor);
        $body = preg_replace('/data-initial-module=("|\')[^"\']*\1/', 'data-initial-module="'.esc_attr($selected).'"', $body, 1);
        return '<div id="'.esc_attr(self::ROOT_ID).'" data-sc-lab-lifecycle="0.25.5" data-sc-lab-active-module="'.esc_attr($selected).'" data-sc-lab-panel-total="'.count($panels).'">'.self::bar($selected).$body.'</div>';
    }

    private static function scan_panels($html) {
        $pattern='~<([a-z][a-z0-9:-]*)\\b[^>]*\\bdata-lab-module\\s*=\\s*(["\\\'])([^"\\\']+)\\2[^>]*>~i';
        if (!preg_match_all($pattern,$html,$m,PREG_OFFSET_CAPTURE)) { return array(); }
        $out=array();
        foreach ($m[0] as $i=>$hit) {
            $slug=sanitize_key($m[3][$i][0]); if (!$slug || isset($out[$slug])) { continue; }
            $tag=strtolower($m[1][$i][0]); $start=(int)$hit[1]; $end=self::matching_end($html,$tag,$start,strlen($hit[0]));
            if ($end===null) { continue; }
            $out[$slug]=array('start'=>$start,'end'=>$end,'html'=>substr($html,$start,$end-$start));
        }
        return $out;
    }

    private static function matching_end($html,$tag,$start,$open_len) {
        $pattern='~</?'.preg_quote($tag,'~').'\\b[^>]*>~i'; $offset=$start+$open_len; $depth=1;
        while (preg_match($pattern,$html,$m,PREG_OFFSET_CAPTURE,$offset)) {
            $token=$m[0][0]; $pos=(int)$m[0][1]; $offset=$pos+strlen($token);
            if (preg_match('~^</~',$token)) { $depth--; if ($depth===0) { return $offset; } }
            elseif (!preg_match('~/\\s*>$~',$token)) { $depth++; }
        }
        return null;
    }

    private static function activate($html) {
        $html=preg_replace('/\\s+hidden(?:=(?:"hidden"|\'hidden\'|hidden))?/i','',$html,1);
        $html=preg_replace('/\\s+aria-hidden=("|\')true\\1/i','',$html,1);
        if (strpos($html,'data-module-panel=')===false) {
            $html=preg_replace('/^<([a-z][a-z0-9:-]*)(\\s|>)/i','<$1 data-module-panel="'.esc_attr(self::requested_module()).'"$2',$html,1);
        }
        return $html;
    }

    private static function bar($module) {
        return '<aside class="sc-lab-lifecycle-bar-v0255" data-sc-lab-lifecycle-bar role="status"><div><strong>Stable lifecycle mode</strong><span>v0.25.5 · '.esc_html($module).' · one laboratory per browser lifecycle</span></div><div><button type="button" data-sc-lab-lifecycle-action="overview">Overview</button><button type="button" data-sc-lab-lifecycle-action="reload">Reload laboratory</button><button type="button" data-sc-lab-lifecycle-action="diagnostics">Diagnostics</button></div><pre data-sc-lab-lifecycle-diagnostics hidden></pre></aside>';
    }
    private static function fallback() { return '<div class="sc-lab-runtime-fallback"><h2>Lab safe start</h2><p>The application panel parser stopped a potentially unsafe full-page startup. Reload the page with <code>?sc_lab_safe=1</code>.</p></div>'; }

    public static function routes() {
        register_rest_route('sc-lab/v1','/runtime/v0255/health',array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
    }
    public static function health() { return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'mode'=>'isolated-module-lifecycle','fullTeardownNavigation'=>true,'assetGate'=>true,'memoryDiagnostics'=>true,'duplicateGuard'=>true)); }
}
