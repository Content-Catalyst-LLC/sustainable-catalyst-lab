<?php
/**
 * Sustainable Catalyst Lab v0.28.0
 * Earth, Space, and Global Data Laboratory.
 */
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Global_Science_V0280 {
    const VERSION = '0.28.0';
    const REST_NAMESPACE = 'sc-lab/v1';
    const CACHE_GROUP = 'sc_lab_global_science_v0280';

    public static function init() {
        add_action('rest_api_init', array(__CLASS__, 'register_routes'));
        add_shortcode('sc_lab_global_science', array(__CLASS__, 'shortcode'));
        add_action('wp_enqueue_scripts', array(__CLASS__, 'register_assets'));
    }

    public static function register_assets() {
        $base = plugin_dir_url(dirname(__FILE__));
        wp_register_style(
            'sc-lab-global-science-v0280',
            $base . 'assets/css/sc-lab-global-science-v0280.css',
            array(),
            self::VERSION
        );
        wp_register_script(
            'sc-lab-global-science-v0280',
            $base . 'assets/js/modules/global-science-lab-v0280.js',
            array(),
            self::VERSION,
            true
        );
    }

    public static function shortcode($atts = array()) {
        $atts = shortcode_atts(array('embedded' => '0', 'title' => 'Earth, Space, and Global Data Laboratory'), $atts, 'sc_lab_global_science');
        wp_enqueue_style('sc-lab-global-science-v0280');
        wp_enqueue_script('sc-lab-global-science-v0280');
        $config = array(
            'restBase' => esc_url_raw(rest_url(self::REST_NAMESPACE . '/global-science/v0280')),
            'nonce' => wp_create_nonce('wp_rest'),
            'version' => self::VERSION,
            'embedded' => $atts['embedded'] === '1',
        );
        wp_add_inline_script('sc-lab-global-science-v0280', 'window.SCLabGlobalScienceV0280Config=' . wp_json_encode($config) . ';', 'before');
        ob_start();
        ?>
        <section class="sc-lab-global-science-v0280" data-global-science-v0280-root data-version="0.28.0">
            <header class="sc-gs-hero">
                <div>
                    <p class="sc-gs-kicker">Connected scientific observation</p>
                    <h2><?php echo esc_html($atts['title']); ?></h2>
                    <p>Discover Earth-observation, climate, ocean, hazard, telescope, space-weather, biodiversity, chemistry, and materials records through Sustainable Catalyst Core.</p>
                </div>
                <div class="sc-gs-status" data-gs-status>Checking Core…</div>
            </header>
            <nav class="sc-gs-tabs" aria-label="Global science work areas">
                <button type="button" data-gs-tab="discover" aria-selected="true">Discover</button>
                <button type="button" data-gs-tab="timeseries" aria-selected="false">Time series</button>
                <button type="button" data-gs-tab="compare" aria-selected="false">Compare</button>
                <button type="button" data-gs-tab="export" aria-selected="false">Export</button>
            </nav>
            <div class="sc-gs-panel" data-gs-panel="discover">
                <form class="sc-gs-filter" data-gs-search-form>
                    <label>Search <input name="q" type="search" placeholder="Mission, dataset, target, variable…"></label>
                    <label>Domain <select name="discipline"><option value="">All domains</option><option value="earth_science">Earth science</option><option value="astronomy">Astronomy</option><option value="biology">Biology</option><option value="chemistry">Chemistry</option><option value="materials_science">Materials</option></select></label>
                    <label>Record type <input name="record_type" type="text" placeholder="dataset, observation…"></label>
                    <button type="submit">Search records</button>
                </form>
                <div class="sc-gs-grid" data-gs-results><p class="sc-gs-empty">Run a search to discover official scientific records.</p></div>
            </div>
            <div class="sc-gs-panel" data-gs-panel="timeseries" hidden>
                <form class="sc-gs-filter" data-gs-series-form>
                    <label>Series ID <input name="series_id" required></label>
                    <button type="submit">Load series</button>
                </form>
                <div data-gs-series-output class="sc-gs-output"></div>
            </div>
            <div class="sc-gs-panel" data-gs-panel="compare" hidden>
                <p>Paste two comma-separated numeric series. The comparison is deterministic and keeps the supplied order.</p>
                <div class="sc-gs-compare-grid">
                    <label>Series A<textarea data-gs-series-a rows="5"></textarea></label>
                    <label>Series B<textarea data-gs-series-b rows="5"></textarea></label>
                </div>
                <button type="button" data-gs-compare>Compare series</button>
                <pre data-gs-compare-output class="sc-gs-output"></pre>
            </div>
            <div class="sc-gs-panel" data-gs-panel="export" hidden>
                <p>Create a provenance-aware notebook template or hand a selected record to Workbench. Exports never contain Core credentials.</p>
                <label>Selected record ID <input data-gs-export-record></label>
                <div class="sc-gs-actions">
                    <button type="button" data-gs-notebook>Download notebook</button>
                    <button type="button" data-gs-workbench>Send to Workbench</button>
                </div>
                <div data-gs-export-status class="sc-gs-output"></div>
            </div>
            <footer class="sc-gs-note">Free official sources only. Data freshness, licenses, attribution, and provenance remain attached to every record.</footer>
        </section>
        <?php
        return ob_get_clean();
    }

    public static function register_routes() {
        $routes = array(
            '/global-science/v0280/health' => 'health',
            '/global-science/v0280/records' => 'records',
            '/global-science/v0280/assets' => 'assets',
            '/global-science/v0280/stac' => 'stac',
            '/global-science/v0280/timeseries' => 'timeseries',
        );
        foreach ($routes as $route => $method) {
            register_rest_route(self::REST_NAMESPACE, $route, array(
                'methods' => WP_REST_Server::READABLE,
                'callback' => array(__CLASS__, $method),
                'permission_callback' => '__return_true',
            ));
        }
        register_rest_route(self::REST_NAMESPACE, '/global-science/v0280/compare', array(
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => array(__CLASS__, 'compare'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route(self::REST_NAMESPACE, '/global-science/v0280/notebook', array(
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => array(__CLASS__, 'notebook'),
            'permission_callback' => '__return_true',
        ));
    }

    private static function env($name, $default = '') {
        if (defined($name)) { return constant($name); }
        $value = getenv($name);
        return $value === false ? $default : $value;
    }

    private static function enabled() {
        return filter_var(self::env('SC_LAB_GLOBAL_SCIENCE_ENABLED', 'true'), FILTER_VALIDATE_BOOLEAN);
    }

    private static function core_url() {
        return rtrim((string) self::env('SC_LAB_PLATFORM_CORE_URL', ''), '/');
    }

    private static function core_key() {
        return (string) self::env('SC_LAB_PLATFORM_CORE_PUBLIC_API_KEY', '');
    }

    private static function state($ok, $message = '') {
        return array(
            'ok' => (bool) $ok,
            'version' => self::VERSION,
            'state' => $ok ? 'connected' : (self::enabled() ? 'unavailable' : 'disabled'),
            'message' => sanitize_text_field($message),
            'core_configured' => self::core_url() !== '' && self::core_key() !== '',
            'free_source_only' => true,
        );
    }

    public static function health() {
        if (!self::enabled()) { return rest_ensure_response(self::state(false, 'Global science integration is disabled.')); }
        if (self::core_url() === '' || self::core_key() === '') { return rest_ensure_response(self::state(false, 'Sustainable Catalyst Core is not configured.')); }
        $result = self::core_get('/api/v1/science/record-types', array());
        if (is_wp_error($result)) { return rest_ensure_response(self::state(false, $result->get_error_message())); }
        $state = self::state(true, 'Core scientific-data fabric is available.');
        $state['record_types'] = self::sanitize_payload($result);
        return rest_ensure_response($state);
    }

    public static function records(WP_REST_Request $request) {
        $args = array(
            'q' => sanitize_text_field($request->get_param('q')),
            'discipline' => sanitize_key($request->get_param('discipline')),
            'record_type' => sanitize_key($request->get_param('record_type')),
            'limit' => min(100, max(1, absint($request->get_param('limit') ?: 25))),
        );
        return self::proxy('/api/v1/science/records', $args);
    }

    public static function assets(WP_REST_Request $request) {
        $args = array(
            'dataset_id' => sanitize_text_field($request->get_param('dataset_id')),
            'format' => sanitize_key($request->get_param('format')),
            'limit' => min(100, max(1, absint($request->get_param('limit') ?: 25))),
        );
        return self::proxy('/api/v1/fabric/assets', $args);
    }

    public static function stac(WP_REST_Request $request) {
        $args = array(
            'collections' => sanitize_text_field($request->get_param('collections')),
            'bbox' => sanitize_text_field($request->get_param('bbox')),
            'datetime' => sanitize_text_field($request->get_param('datetime')),
            'limit' => min(100, max(1, absint($request->get_param('limit') ?: 25))),
        );
        return self::proxy('/api/v1/stac/search', $args);
    }

    public static function timeseries(WP_REST_Request $request) {
        $series_id = sanitize_text_field($request->get_param('series_id'));
        if ($series_id === '') { return new WP_Error('missing_series', 'series_id is required.', array('status' => 400)); }
        return self::proxy('/api/v1/fabric/timeseries/' . rawurlencode($series_id) . '/points', array('limit' => 1000));
    }

    private static function proxy($path, $args) {
        if (!self::enabled()) { return new WP_Error('disabled', 'Global science integration is disabled.', array('status' => 503)); }
        if (self::core_url() === '' || self::core_key() === '') { return new WP_Error('core_unconfigured', 'Sustainable Catalyst Core is not configured.', array('status' => 503)); }
        $result = self::core_get($path, array_filter($args, static function($value) { return $value !== '' && $value !== null; }));
        if (is_wp_error($result)) { return $result; }
        return rest_ensure_response(self::sanitize_payload($result));
    }

    private static function core_get($path, $args) {
        $url = self::core_url() . $path;
        if ($args) { $url = add_query_arg($args, $url); }
        $cache_key = 'v0280_' . md5($url);
        $cached = get_transient($cache_key);
        if ($cached !== false) { return $cached; }
        $response = wp_remote_get($url, array(
            'timeout' => min(20, max(3, absint(self::env('SC_LAB_GLOBAL_SCIENCE_TIMEOUT_SECONDS', '9')))),
            'redirection' => 2,
            'headers' => array('X-API-Key' => self::core_key(), 'Accept' => 'application/json'),
            'user-agent' => 'Sustainable-Catalyst-Lab/' . self::VERSION,
        ));
        if (is_wp_error($response)) { return $response; }
        $code = wp_remote_retrieve_response_code($response);
        if ($code < 200 || $code >= 300) { return new WP_Error('core_http_error', 'Core returned HTTP ' . $code . '.', array('status' => 502)); }
        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($body)) { return new WP_Error('core_invalid_json', 'Core returned invalid JSON.', array('status' => 502)); }
        set_transient($cache_key, $body, min(600, max(15, absint(self::env('SC_LAB_GLOBAL_SCIENCE_CACHE_TTL_SECONDS', '120')))));
        return $body;
    }

    private static function sanitize_payload($value, $depth = 0) {
        if ($depth > 8) { return null; }
        if (is_array($value)) {
            $out = array();
            $count = 0;
            foreach ($value as $key => $item) {
                if (++$count > 500) { break; }
                $safe_key = is_int($key) ? $key : sanitize_key((string) $key);
                if (!is_int($key) && preg_match('/(?:secret|token|password|api.?key|authorization|credential)/i', (string) $key)) { continue; }
                $out[$safe_key] = self::sanitize_payload($item, $depth + 1);
            }
            return $out;
        }
        if (is_bool($value) || is_int($value) || is_float($value) || $value === null) { return $value; }
        $text = (string) $value;
        if (preg_match('#^https?://#i', $text)) {
            $parts = wp_parse_url($text);
            if (!is_array($parts) || empty($parts['host'])) { return ''; }
            return esc_url_raw(($parts['scheme'] ?? 'https') . '://' . $parts['host'] . ($parts['path'] ?? ''));
        }
        return sanitize_textarea_field(wp_strip_all_tags($text));
    }

    public static function compare(WP_REST_Request $request) {
        $data = $request->get_json_params();
        $a = self::numbers($data['a'] ?? array());
        $b = self::numbers($data['b'] ?? array());
        if (!$a || !$b) { return new WP_Error('invalid_series', 'Two non-empty numeric series are required.', array('status' => 400)); }
        $n = min(count($a), count($b));
        $a = array_slice($a, 0, $n); $b = array_slice($b, 0, $n);
        $deltas = array(); $percent = array();
        for ($i = 0; $i < $n; $i++) {
            $deltas[] = $b[$i] - $a[$i];
            if ($a[$i] != 0.0) { $percent[] = (($b[$i] - $a[$i]) / abs($a[$i])) * 100.0; }
        }
        return rest_ensure_response(array(
            'schema' => 'sc-lab-series-comparison/1.0', 'version' => self::VERSION,
            'aligned_count' => $n, 'series_a' => self::summary($a), 'series_b' => self::summary($b),
            'mean_delta' => array_sum($deltas) / $n,
            'mean_percent_change' => $percent ? array_sum($percent) / count($percent) : null,
            'correlation' => self::correlation($a, $b),
        ));
    }

    private static function numbers($values) {
        if (is_string($values)) { $values = preg_split('/[\s,;]+/', $values, -1, PREG_SPLIT_NO_EMPTY); }
        if (!is_array($values)) { return array(); }
        $out = array(); foreach (array_slice($values, 0, 5000) as $v) { if (is_numeric($v) && is_finite((float) $v)) { $out[] = (float) $v; } }
        return $out;
    }

    private static function summary($values) {
        $n = count($values); $mean = array_sum($values) / $n; $variance = 0.0;
        foreach ($values as $v) { $variance += ($v - $mean) * ($v - $mean); }
        $slope = $n > 1 ? ($values[$n - 1] - $values[0]) / ($n - 1) : 0.0;
        return array('count' => $n, 'minimum' => min($values), 'maximum' => max($values), 'mean' => $mean, 'standard_deviation' => sqrt($variance / $n), 'trend_slope' => $slope);
    }

    private static function correlation($a, $b) {
        $n = min(count($a), count($b)); if ($n < 2) { return null; }
        $ma = array_sum($a) / $n; $mb = array_sum($b) / $n; $num = 0.0; $da = 0.0; $db = 0.0;
        for ($i = 0; $i < $n; $i++) { $xa = $a[$i] - $ma; $xb = $b[$i] - $mb; $num += $xa * $xb; $da += $xa * $xa; $db += $xb * $xb; }
        return ($da > 0 && $db > 0) ? $num / sqrt($da * $db) : null;
    }

    public static function notebook(WP_REST_Request $request) {
        $data = $request->get_json_params();
        $record_id = sanitize_text_field($data['record_id'] ?? '');
        $title = sanitize_text_field($data['title'] ?? 'Sustainable Catalyst global science analysis');
        $notebook = array(
            'cells' => array(
                array('cell_type' => 'markdown', 'metadata' => new stdClass(), 'source' => array('# ' . $title . "\n", "Generated by Research Lab v0.28.0.\n", 'Record ID: `' . $record_id . "`\n")),
                array('cell_type' => 'code', 'execution_count' => null, 'metadata' => new stdClass(), 'outputs' => array(), 'source' => array("# Configure the public Core URL and supply credentials through your environment.\n", "import os, requests\n", "core = os.environ.get('SC_CORE_URL', '')\n", "headers = {'X-API-Key': os.environ.get('SC_CORE_PUBLIC_API_KEY', '')}\n", "record_id = " . wp_json_encode($record_id) . "\n", "# requests.get(f'{core}/api/v1/science/records/{record_id}', headers=headers, timeout=20)\n")),
            ),
            'metadata' => array('kernelspec' => array('display_name' => 'Python 3', 'language' => 'python', 'name' => 'python3'), 'sustainable_catalyst' => array('schema' => 'sc-lab-notebook/1.0', 'release' => self::VERSION, 'record_id' => $record_id, 'credentials_embedded' => false)),
            'nbformat' => 4, 'nbformat_minor' => 5,
        );
        return rest_ensure_response($notebook);
    }
}
