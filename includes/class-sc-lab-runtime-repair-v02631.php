<?php
/**
 * Sustainable Catalyst Lab v0.26.3.1 panel alias and compatibility routing repair.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Runtime_Repair_V02631 {
    const VERSION = '0.26.3.1';
    const ROOT_ID = 'sc-lab-v02631-root';
    private static $initialized = false;
    private static $assets = false;

    public static function init() {
        if (self::$initialized) { return; }
        self::$initialized = true;
        add_action('template_redirect', array(__CLASS__, 'canonical_redirect'), 1);
        add_action('wp_enqueue_scripts', array(__CLASS__, 'maybe_enqueue'), 1);
        add_action('wp_enqueue_scripts', array(__CLASS__, 'gate_assets'), PHP_INT_MAX);
        add_filter('do_shortcode_tag', array(__CLASS__, 'filter_app'), PHP_INT_MAX, 4);
        add_action('rest_api_init', array(__CLASS__, 'routes'));
    }

    public static function alias_map() {
        $aliases = array(
            'marine' => 'marine-biology',
            'marine-science' => 'marine-biology',
            'ocean-biology' => 'marine-biology',
            'climate' => 'climate-maps',
            'climate-map' => 'climate-maps',
            'evidence' => 'evidence-decisions',
            'decisions' => 'evidence-decisions',
            'earth' => 'earth-systems',
            'energy' => 'energy-engineering',
            'electrical' => 'electrical-embedded',
            'mechanical' => 'mechanical-thermal',
            'civil' => 'civil-infrastructure',
            'reports' => 'report-studio',
            'report' => 'report-studio',
            'visualization' => 'visualization-studio',
            'code' => 'code-studio',
            'workspace' => 'workspace-data',
            'sources' => 'source-registry',
            'datasets' => 'dataset-inspector',
            'status' => 'system-status',
        );
        return apply_filters('sc_lab_module_aliases_v02631', $aliases);
    }

    public static function canonical_module($module) {
        $module = sanitize_key((string) $module);
        if (!$module || !preg_match('/^[a-z0-9][a-z0-9-]{0,79}$/', $module)) { return 'overview'; }
        $aliases = self::alias_map();
        $seen = array();
        while (isset($aliases[$module]) && !isset($seen[$module])) {
            $seen[$module] = true;
            $module = sanitize_key((string) $aliases[$module]);
        }
        return $module ?: 'overview';
    }

    private static function raw_requested_module($html = '') {
        if (isset($_GET['sc_lab_safe'])) { return 'overview'; }
        if (isset($_GET['sc_lab_module'])) { return sanitize_key(wp_unslash($_GET['sc_lab_module'])); }
        if ($html && preg_match('/data-initial-module=("|\')([^"\']+)\1/i', $html, $m)) { return sanitize_key($m[2]); }
        return 'overview';
    }

    private static function requested_module($html = '') {
        return self::canonical_module(self::raw_requested_module($html));
    }

    private static function is_lab_request() {
        if (is_admin()) { return false; }
        global $post;
        if (isset($_GET['sc_lab_module']) || isset($_GET['sc_lab_safe'])) { return true; }
        return $post instanceof WP_Post && has_shortcode((string) $post->post_content, 'sc_lab_app');
    }

    public static function canonical_redirect() {
        if (!self::is_lab_request() || !isset($_GET['sc_lab_module']) || headers_sent()) { return; }
        $raw = sanitize_key(wp_unslash($_GET['sc_lab_module']));
        $canonical = self::canonical_module($raw);
        if (!$raw || $canonical === $raw) { return; }
        $url = remove_query_arg('sc_lab_module');
        $url = add_query_arg('sc_lab_module', $canonical, $url);
        wp_safe_redirect($url, 302, 'Sustainable Catalyst Lab v0.26.3.1');
        exit;
    }

    private static function asset_version($relative) {
        $path = SC_LAB_DIR . ltrim($relative, '/');
        return self::VERSION . '.' . (is_file($path) ? substr(hash_file('sha256', $path), 0, 12) : '0');
    }

    public static function maybe_enqueue() {
        if (!self::is_lab_request() || self::$assets) { return; }
        self::$assets = true;
        $style = 'assets/css/sc-lab-runtime-v02631.css';
        $script = 'assets/js/sc-lab-runtime-v02631.js';
        wp_enqueue_style('sc-lab-runtime-v02631', SC_LAB_URL . $style, array(), self::asset_version($style));
        wp_enqueue_script('sc-lab-runtime-v02631', SC_LAB_URL . $script, array(), self::asset_version($script), true);
        wp_localize_script('sc-lab-runtime-v02631', 'SCLabRuntimeConfigV02631', array(
            'version' => self::VERSION,
            'pluginVersion' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : self::VERSION,
            'requestedModule' => self::raw_requested_module(),
            'module' => self::requested_module(),
            'aliases' => self::alias_map(),
            'safeStart' => isset($_GET['sc_lab_safe']),
            'nodeBudget' => 6500,
            'warningBudget' => 5000,
            'healthUrl' => esc_url_raw(rest_url('sc-lab/v1/runtime/v02631/health')),
        ));
    }

    public static function gate_assets() {
        if (!self::is_lab_request()) { return; }
        $module = self::requested_module();
        $allowed = self::allowed_advanced_files($module);
        $scripts = wp_scripts();
        if ($scripts) {
            foreach ((array) $scripts->queue as $handle) {
                $item = isset($scripts->registered[$handle]) ? $scripts->registered[$handle] : null;
                if (!$item || empty($item->src)) { continue; }
                $base = basename((string) parse_url($item->src, PHP_URL_PATH));
                if (self::is_advanced_script($base) && !in_array($base, $allowed, true)) { wp_dequeue_script($handle); }
            }
        }
        $styles = wp_styles();
        if ($styles) {
            foreach ((array) $styles->queue as $handle) {
                $item = isset($styles->registered[$handle]) ? $styles->registered[$handle] : null;
                if (!$item || empty($item->src)) { continue; }
                $base = basename((string) parse_url($item->src, PHP_URL_PATH));
                if (self::is_advanced_style($base) && !in_array($base, $allowed, true)) { wp_dequeue_style($handle); }
            }
        }
    }

    private static function is_advanced_script($base) {
        return (bool) preg_match('/(?:architecture-building|urban-planning|sustainable-cities|comparative-economics|aerospace-engineering|rocket-propulsion|microbiology-laboratory|circular-economy|biochemistry-|molecular-analysis|biotechnology-bioprocess|bioprocess-|biomedical-engineering|biosignal-|genetics-genomics|genomics-production|genomic-|laboratory-data-instrumentation|instrumentation-|civil-.*v0200|engineering-interface-repair)/', $base);
    }

    private static function is_advanced_style($base) {
        return (bool) preg_match('/(?:v0130|v0140|v0150|v0160|v0170|v0180|v0190|v0200|v0210|biochemistry-|molecular-analysis|biotechnology-|bioprocess-|biomedical-|biosignal-|genetics-|genomic-|genomics-|laboratory-data-|instrumentation-)/', $base);
    }

    private static function allowed_advanced_files($module) {
        $map = array(
            'architecture-building' => array('architecture-building-lab.js', 'sc-lab-v0130.css'),
            'urban-planning-spatial' => array('urban-planning-spatial-lab.js', 'sc-lab-v0140.css'),
            'sustainable-cities-resilience' => array('sustainable-cities-resilience-lab.js', 'sc-lab-v0160.css'),
            'comparative-economics-development-systems' => array('comparative-economics-development-systems-lab.js', 'sc-lab-v0170.css'),
            'aerospace-engineering-flight-systems' => array('aerospace-engineering-flight-systems-lab.js', 'sc-lab-v0180.css'),
            'rocket-propulsion-spaceflight' => array('rocket-propulsion-spaceflight-lab.js', 'sc-lab-v0190.css'),
            'microbiology-laboratory' => array('microbiology-laboratory.js', 'sc-lab-v0200.css'),
            'circular-economy-industrial-ecology' => array('circular-economy-industrial-ecology-lab.js', 'sc-lab-v0160.css'),
            'civil-infrastructure' => array('civil-infrastructure-lab-v0150.js', 'civil-infrastructure-runtime-v0200.js', 'civil-infrastructure-direct-loader-v0200.js', 'civil-panel-router-v0200.js', 'engineering-interface-repair-v0200.js', 'sc-lab-v0150.css'),
            'biochemistry-molecular-analysis' => array('biochemistry-molecular-analysis.js', 'biochemistry-production-v0211.js', 'biochemistry-visualization-batch-v0212.js', 'molecular-analysis-validation-provenance-v0213.js', 'sc-lab-v0210.css', 'sc-lab-biochemistry-production-v0211.css', 'sc-lab-biochemistry-visualization-batch-v0212.css', 'sc-lab-molecular-analysis-validation-provenance-v0213.css'),
            'biotechnology-bioprocess-engineering' => array('biotechnology-bioprocess-engineering-v0220.js', 'bioprocess-production-v0221.js', 'bioprocess-monitoring-control-v0222.js', 'bioprocess-validation-provenance-v0223.js', 'sc-lab-biotechnology-bioprocess-engineering-v0220.css', 'sc-lab-bioprocess-production-v0221.css', 'sc-lab-bioprocess-monitoring-control-v0222.css', 'sc-lab-bioprocess-validation-provenance-v0223.css'),
            'biomedical-engineering-biosignals' => array('biomedical-engineering-biosignals-v0230.js', 'biosignal-production-v0231.js', 'biosignal-visualization-comparison-v0232.js', 'sc-lab-biomedical-engineering-biosignals-v0230.css', 'sc-lab-biosignal-production-v0231.css', 'sc-lab-biosignal-visualization-comparison-v0232.css'),
            'genetics-genomics-sequence-analysis' => array('genetics-genomics-sequence-analysis-v0240.js', 'genomics-production-v0241.js', 'genomic-visualization-comparison-v0242.js', 'genomic-validation-sequence-provenance-v0243.js', 'sc-lab-genetics-genomics-v0240.css', 'sc-lab-genomics-production-v0241.css', 'sc-lab-genomic-visualization-v0242.css', 'sc-lab-genomic-validation-v0243.css'),
            'laboratory-data-instrumentation' => array('laboratory-data-instrumentation-v0250.js', 'instrumentation-production-v0251.js', 'instrumentation-live-visualization-v0252.js', 'instrumentation-validation-custody-v0253.js', 'sc-lab-laboratory-data-instrumentation-v0250.css', 'sc-lab-instrumentation-production-v0251.css', 'sc-lab-instrumentation-live-visualization-v0252.css', 'sc-lab-instrumentation-validation-custody-v0253.css'),
        );
        return isset($map[$module]) ? $map[$module] : array();
    }

    public static function filter_app($output, $tag, $attr, $match) {
        unset($attr, $match);
        if ($tag !== 'sc_lab_app' || is_admin()) { return $output; }
        self::maybe_enqueue();
        return self::single_module_shell((string) $output, self::raw_requested_module((string) $output));
    }

    private static function single_module_shell($html, $requested_raw) {
        $panels = self::scan_panels($html);
        if (!$panels) { return self::fallback(); }
        $requested = self::canonical_module($requested_raw);
        $selected = isset($panels[$requested]) ? $requested : (isset($panels['overview']) ? 'overview' : array_key_first($panels));
        $resolution = $requested_raw !== $requested && isset($panels[$requested]) ? 'alias' : (isset($panels[$requested]) ? 'canonical' : 'missing');
        uasort($panels, function($a, $b) { return $a['start'] <=> $b['start']; });
        $cursor = 0;
        $body = '';
        foreach ($panels as $slug => $panel) {
            $body .= substr($html, $cursor, $panel['start'] - $cursor);
            if ($slug === $selected) { $body .= self::activate($panel['html'], $selected); }
            $cursor = $panel['end'];
        }
        $body .= substr($html, $cursor);
        $body = preg_replace('/data-initial-module=("|\')[^"\']*\1/', 'data-initial-module="' . esc_attr($selected) . '"', $body, 1);
        $body = preg_replace('/data-sc-lab-runtime-version=("|\')[^"\']*\1/', 'data-sc-lab-runtime-version="' . esc_attr(self::VERSION) . '"', $body, 1);
        $manifest = array('modules' => array_keys($panels), 'aliases' => self::alias_map());
        $json = wp_json_encode($manifest, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $json = str_replace('</', '<\\/', (string) $json);
        return '<div id="' . esc_attr(self::ROOT_ID) . '" data-sc-lab-runtime="0.26.3.1" data-sc-lab-active-module="' . esc_attr($selected) . '" data-sc-lab-requested-module="' . esc_attr($requested_raw) . '" data-sc-lab-module-resolution="' . esc_attr($resolution) . '" data-sc-lab-panel-total="' . count($panels) . '">' . self::bar($selected, $requested_raw, $resolution) . '<script type="application/json" data-sc-lab-module-manifest>' . $json . '</script>' . $body . '</div>';
    }

    private static function scan_panels($html) {
        $pattern = '~<([a-z][a-z0-9:-]*)\\b[^>]*\\bdata-lab-module\\s*=\\s*(["\'])([^"\']+)\\2[^>]*>~i';
        if (!preg_match_all($pattern, $html, $matches, PREG_OFFSET_CAPTURE)) { return array(); }
        $out = array();
        foreach ($matches[0] as $index => $hit) {
            $slug = sanitize_key($matches[3][$index][0]);
            if (!$slug || isset($out[$slug])) { continue; }
            $tag = strtolower($matches[1][$index][0]);
            $start = (int) $hit[1];
            $end = self::matching_end($html, $tag, $start, strlen($hit[0]));
            if ($end === null) { continue; }
            $out[$slug] = array('start' => $start, 'end' => $end, 'html' => substr($html, $start, $end - $start));
        }
        return $out;
    }

    private static function matching_end($html, $tag, $start, $open_len) {
        $pattern = '~</?' . preg_quote($tag, '~') . '\\b[^>]*>~i';
        $offset = $start + $open_len;
        $depth = 1;
        while (preg_match($pattern, $html, $match, PREG_OFFSET_CAPTURE, $offset)) {
            $token = $match[0][0];
            $position = (int) $match[0][1];
            $offset = $position + strlen($token);
            if (preg_match('~^</~', $token)) {
                $depth--;
                if ($depth === 0) { return $offset; }
            } elseif (!preg_match('~/\\s*>$~', $token)) { $depth++; }
        }
        return null;
    }

    private static function activate($html, $module) {
        $html = preg_replace('/\\s+hidden(?:=(?:"hidden"|\'hidden\'|hidden))?/i', '', $html, 1);
        $html = preg_replace('/\\s+aria-hidden=("|\')true\\1/i', '', $html, 1);
        if (strpos($html, 'data-module-panel=') === false) {
            $html = preg_replace('/^<([a-z][a-z0-9:-]*)(\\s|>)/i', '<$1 data-module-panel="' . esc_attr($module) . '"$2', $html, 1);
        }
        return $html;
    }

    private static function bar($module, $requested, $resolution) {
        $detail = self::VERSION . ' · ' . $module . ' · canonical panel routing';
        if ($resolution === 'alias') { $detail .= ' · resolved ' . sanitize_key($requested) . ' → ' . $module; }
        return '<aside class="sc-lab-runtime-bar-v02631" data-sc-lab-runtime-bar role="status"><div><strong>Panel routing repair active</strong><span>' . esc_html($detail) . '</span></div><div><button type="button" data-sc-lab-runtime-action="overview">Overview</button><button type="button" data-sc-lab-runtime-action="reload">Reload laboratory</button><button type="button" data-sc-lab-runtime-action="diagnostics">Diagnostics</button></div><pre data-sc-lab-runtime-diagnostics hidden></pre></aside>';
    }

    private static function fallback() {
        return '<div class="sc-lab-runtime-fallback"><h2>Lab safe start</h2><p>The application panel parser stopped an unsafe full-page startup. Reload with <code>?sc_lab_safe=1</code>.</p></div>';
    }

    public static function routes() {
        register_rest_route('sc-lab/v1', '/runtime/v02631/health', array(
            'methods' => WP_REST_Server::READABLE,
            'callback' => array(__CLASS__, 'health'),
            'permission_callback' => '__return_true',
        ));
    }

    private static function duplicate_plugin_candidates() {
        if (!defined('WP_PLUGIN_DIR') || !is_dir(WP_PLUGIN_DIR)) { return array(); }
        $found = array();
        foreach ((array) glob(WP_PLUGIN_DIR . '/*/sustainable-catalyst-lab.php') as $file) {
            $found[] = str_replace(WP_PLUGIN_DIR . '/', '', $file);
        }
        sort($found);
        return $found;
    }

    public static function health() {
        $asset_paths = array(
            'app' => 'assets/js/sc-lab-app.js',
            'runtime' => 'assets/js/sc-lab-runtime-v02631.js',
            'calculators' => 'assets/js/modules/calculators.js',
            'astronomy' => 'assets/js/modules/astronomy-lab.js',
            'earth' => 'assets/js/modules/earth-lab.js',
        );
        $assets = array();
        foreach ($asset_paths as $key => $relative) {
            $path = SC_LAB_DIR . $relative;
            $assets[$key] = array('version' => self::asset_version($relative), 'sha256' => is_file($path) ? hash_file('sha256', $path) : null);
        }
        $duplicates = self::duplicate_plugin_candidates();
        return rest_ensure_response(array(
            'ok' => true,
            'pluginVersion' => defined('SC_LAB_VERSION') ? SC_LAB_VERSION : null,
            'runtimeVersion' => self::VERSION,
            'mode' => 'canonical-panel-alias-routing',
            'singlePanel' => true,
            'aliases' => self::alias_map(),
            'aliasRouting' => true,
            'falseWarningSuppression' => true,
            'assetHashCacheBust' => true,
            'pluginBasename' => defined('SC_LAB_PLUGIN_BASENAME') ? SC_LAB_PLUGIN_BASENAME : null,
            'pluginCandidates' => $duplicates,
            'duplicatePluginRisk' => count($duplicates) > 1,
            'assets' => $assets,
        ));
    }
}
