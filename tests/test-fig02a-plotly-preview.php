<?php
// SC-FIG-01 / FIG-02A Graph Studio Plotly preview: WordPress loader contract (stubbed WordPress).
$root = dirname(__DIR__);
define('ABSPATH', '/');
define('SC_LAB_URL', 'https://example.test/wp-content/plugins/sustainable-catalyst-lab/');
$assert = function ($cond, $msg) { if (!$cond) { fwrite(STDERR, "FAIL - $msg\n"); exit(1); } };

$GLOBALS['options'] = array();
$GLOBALS['enqueued'] = array();
$GLOBALS['localized'] = array();
$GLOBALS['routes'] = array();
$GLOBALS['filters'] = array();
class WP_Post { public $post_content = '[sc_lab_app module="graph-studio"]'; }
class WP_REST_Server { const READABLE = 'GET'; }
function add_action() {}
function is_admin() { return false; }
function is_page($slug) { return false; }
function has_shortcode($content, $tag) { return strpos($content, '[' . $tag) !== false; }
function get_option($k, $d = false) { return array_key_exists($k, $GLOBALS['options']) ? $GLOBALS['options'][$k] : $d; }
function apply_filters($tag, $value) { return isset($GLOBALS['filters'][$tag]) ? $GLOBALS['filters'][$tag]($value) : $value; }
function wp_script_is($h) { return isset($GLOBALS['enqueued'][$h]); }
function wp_style_is($h) { return isset($GLOBALS['enqueued']['style:' . $h]); }
function wp_enqueue_script($h, $src, $deps = array(), $ver = false) { $GLOBALS['enqueued'][$h] = array($src, $deps, $ver); }
function wp_enqueue_style($h, $src, $deps = array(), $ver = false) { $GLOBALS['enqueued']['style:' . $h] = array($src, $deps, $ver); }
function wp_localize_script($h, $name, $data) { $GLOBALS['localized'][$name] = $data; }
function register_rest_route($ns, $route, $args) { $GLOBALS['routes'][$ns . $route] = $args; }
function rest_ensure_response($v) { return $v; }
$GLOBALS['post'] = new WP_Post();

$plugin = file_get_contents($root . '/sustainable-catalyst-lab.php');
$assert(strpos($plugin, "includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php") !== false, 'plugin requires loader');
$assert(strpos($plugin, 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A::init();') !== false, 'plugin initializes loader');

// Runs against the real plugin directory, or (FIG02A_TAMPERED_DIR) a copy with a modified plotly.js.
$tampered = getenv('FIG02A_TAMPERED_DIR');
define('SC_LAB_DIR', $tampered ? rtrim($tampered, '/') . '/' : $root . '/');
require $root . '/includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php';
$C = 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A';
$reset = function () use ($C) {
    $GLOBALS['enqueued'] = array(); $GLOBALS['localized'] = array();
    $p = new ReflectionProperty($C, 'vendor_verified'); $p->setAccessible(true); $p->setValue(null, null);
};

// 1. Default off: nothing is enqueued, not even plotly.js.
$reset(); $C::enqueue();
$assert($GLOBALS['enqueued'] === array(), 'default off enqueues nothing');
$assert($C::is_enabled() === false, 'default disabled');
$GLOBALS['filters']['sc_lab_fig02a_plotly_preview_enabled'] = function () { return 'yes'; };
$assert($C::is_enabled() === false, 'only boolean true from the filter enables it');
unset($GLOBALS['filters']['sc_lab_fig02a_plotly_preview_enabled']);

if ($tampered) {
    $GLOBALS['options'][$C::OPTION] = '1';
    $reset(); $C::enqueue();
    $assert($C::vendor_verified() === false && $GLOBALS['enqueued'] === array(), 'modified plotly.js is never served (fail closed)');
    echo "PASS - FIG-02A loader refuses a modified vendored plotly.js\n";
    exit(0);
}

// 2. Enabled: vendored plotly.js 3.3.1, then the module that depends on it.
$GLOBALS['options'][$C::OPTION] = '1';
$reset(); $C::enqueue();
$assert($C::vendor_verified() === true, 'vendored plotly.js sha256 verified');
$plotly = $GLOBALS['enqueued']['sc-lab-plotly-js-331'] ?? null;
$assert($plotly && $plotly[0] === SC_LAB_URL . 'assets/lib/plotly-3.3.1/plotly.min.js' && $plotly[2] === '3.3.1', 'local plotly.js 3.3.1 enqueued');
$module = $GLOBALS['enqueued']['sc-lab-graph-studio-plotly-preview-fig02a'] ?? null;
$assert($module && $module[1] === array('sc-lab-plotly-js-331'), 'module depends on vendored plotly.js');
$assert(isset($GLOBALS['enqueued']['style:sc-lab-graph-studio-plotly-preview-fig02a']), 'module stylesheet enqueued');
$assert(($GLOBALS['localized']['SCLabFig02aPlotlyPreviewConfig']['enabled'] ?? null) === true, 'module config enabled');
foreach ($GLOBALS['enqueued'] as $h => $e) { $assert(strpos($e[0], SC_LAB_URL) === 0, "$h served from the plugin, not a CDN"); }

// 3. Non-Lab page: nothing even when enabled.
$GLOBALS['post'] = null; $_SERVER['REQUEST_URI'] = '/about/';
$reset(); $C::enqueue();
$assert($GLOBALS['enqueued'] === array(), 'non-Lab request enqueues nothing');
$_SERVER['REQUEST_URI'] = '/lab/';
$reset(); $C::enqueue();
$assert(isset($GLOBALS['enqueued']['sc-lab-plotly-js-331']), '/lab/ path enqueues when enabled');

// 4. Health route.
$C::routes();
$route = $GLOBALS['routes']['sc-lab/v1/graph-studio-plotly-preview/fig02a/health'] ?? null;
$assert($route && $route['methods'] === 'GET', 'health route registered');
$h = $C::health();
$assert($h['enabled'] === true && $h['defaultEnabled'] === false && $h['plotlyJsVersion'] === '3.3.1', 'health versions');
$assert($h['plotlyJsSha256Verified'] === true && $h['cdnUsed'] === false && $h['publicationPerformed'] === false && $h['secondGraphStudio'] === false, 'health boundaries');

echo "PASS - FIG-02A Graph Studio Plotly preview WordPress loader contract\n";
