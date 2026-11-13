<?php
// SC-FIG-01 generic sc.figure-bundle.v1 renderer: WordPress loader contract (stubbed WordPress).
$root = dirname(__DIR__);
define('ABSPATH', '/');
define('SC_LAB_URL', 'https://example.test/wp-content/plugins/sustainable-catalyst-lab/');
$assert = function ($cond, $msg) { if (!$cond) { fwrite(STDERR, "FAIL - $msg\n"); exit(1); } };

$GLOBALS['options'] = array();
$GLOBALS['enqueued'] = array();
$GLOBALS['inline'] = array();
$GLOBALS['routes'] = array();
$GLOBALS['filters'] = array();
$GLOBALS['actions'] = array();
class WP_Post { public $post_content = '[sc_lab_app module="graph-studio"]'; }
class WP_REST_Server { const READABLE = 'GET'; }
function add_action($tag, $cb) { $GLOBALS['actions'][$tag][] = $cb; }
function is_admin() { return false; }
function is_page($slug) { return false; }
function has_shortcode($content, $tag) { return strpos($content, '[' . $tag) !== false; }
function get_option($k, $d = false) { return array_key_exists($k, $GLOBALS['options']) ? $GLOBALS['options'][$k] : $d; }
function apply_filters($tag, $value) { return isset($GLOBALS['filters'][$tag]) ? $GLOBALS['filters'][$tag]($value) : $value; }
function wp_script_is($h) { return isset($GLOBALS['enqueued'][$h]); }
function wp_style_is($h) { return isset($GLOBALS['enqueued']['style:' . $h]); }
function wp_enqueue_script($h, $src, $deps = array(), $ver = false) { $GLOBALS['enqueued'][$h] = array($src, $deps, $ver); }
function wp_enqueue_style($h, $src, $deps = array(), $ver = false) { $GLOBALS['enqueued']['style:' . $h] = array($src, $deps, $ver); }
function wp_add_inline_script($h, $js, $pos = 'after') { $GLOBALS['inline'][$h][$pos][] = $js; }
function wp_json_encode($v) { return json_encode($v); }
function register_rest_route($ns, $route, $args) { $GLOBALS['routes'][$ns . $route] = $args; }
function rest_ensure_response($v) { return $v; }
$GLOBALS['post'] = new WP_Post();

$plugin = file_get_contents($root . '/sustainable-catalyst-lab.php');
$fig = strpos($plugin, 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A::init();');
$gen = strpos($plugin, 'SC_Lab_Graph_Studio_Figure_Bundle_Renderer::init();');
$assert($fig !== false && $gen !== false && $gen > $fig, 'plugin initializes the generic renderer after FIG-02A');

$tampered = getenv('FIG02A_TAMPERED_DIR');
define('SC_LAB_DIR', $tampered ? rtrim($tampered, '/') . '/' : $root . '/');
require $root . '/includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php';
require $root . '/includes/class-sc-lab-graph-studio-figure-bundle-renderer.php';
$F = 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A';
$G = 'SC_Lab_Graph_Studio_Figure_Bundle_Renderer';
$F::init(); $G::init();
$reset = function () use ($F) {
    $GLOBALS['enqueued'] = array(); $GLOBALS['inline'] = array();
    $p = new ReflectionProperty($F, 'vendor_verified'); $p->setAccessible(true); $p->setValue(null, null);
};
$run = function () { foreach ($GLOBALS['actions']['wp_enqueue_scripts'] as $cb) { call_user_func($cb); } };

// Default off.
$reset(); $run();
$assert($GLOBALS['enqueued'] === array(), 'default off enqueues nothing');
$GLOBALS['filters']['sc_lab_figure_bundle_renderer_enabled'] = function () { return 1; };
$assert($G::is_enabled() === false, 'only boolean true from the filter enables it');
unset($GLOBALS['filters']['sc_lab_figure_bundle_renderer_enabled']);

$GLOBALS['options'][$G::OPTION] = '1';
if ($tampered) {
    $reset(); $run();
    $assert($GLOBALS['enqueued'] === array(), 'modified plotly.js is never served by the generic renderer (fail closed)');
    echo "PASS - generic renderer loader refuses a modified vendored plotly.js\n";
    exit(0);
}

// Generic on, FIG-02A off: libraries load, only the generic panel gets a config.
$reset(); $run();
$e = $GLOBALS['enqueued'];
$assert(isset($e['sc-lab-plotly-js-331'], $e['sc-lab-graph-studio-plotly-preview-fig02a'], $e['sc-lab-graph-studio-figure-bundle-renderer']), 'plotly, FIG-02A library and renderer enqueued');
$assert($e['sc-lab-graph-studio-figure-bundle-renderer'][1] === array('sc-lab-graph-studio-plotly-preview-fig02a'), 'renderer depends on the FIG-02A primitives');
$assert(strpos($e['sc-lab-plotly-js-331'][0], 'assets/lib/plotly-3.3.1/plotly.min.js') !== false, 'vendored plotly.js, no CDN');
$assert(!isset($GLOBALS['inline']['sc-lab-graph-studio-plotly-preview-fig02a']), 'FIG-02A panel stays off');
$cfg = $GLOBALS['inline']['sc-lab-graph-studio-figure-bundle-renderer']['before'][0];
$assert(strpos($cfg, '"enabled":true') !== false && strpos($cfg, 'SCLabFigureBundleRendererConfig') !== false, 'typed boolean config');

// Both on: FIG-02A keeps its own config (it enqueues first).
$GLOBALS['options'][$F::OPTION] = '1';
$reset(); $run();
$assert(isset($GLOBALS['inline']['sc-lab-graph-studio-plotly-preview-fig02a']['before'][0]), 'FIG-02A config kept when both are on');
$assert(isset($GLOBALS['inline']['sc-lab-graph-studio-figure-bundle-renderer']['before'][0]), 'renderer config emitted when both are on');

// Not a Lab page: nothing.
$GLOBALS['post'] = null; $_SERVER['REQUEST_URI'] = '/about/';
$reset(); $run();
$assert($GLOBALS['enqueued'] === array(), 'non-Lab pages load nothing');

$G::routes();
$h = $G::health();
$assert(isset($GLOBALS['routes']['sc-lab/v1/graph-studio/figure-bundle-renderer/health']), 'health route registered');
$assert($h['defaultEnabled'] === false && $h['publicationPerformed'] === false && $h['uploadPerformed'] === false && $h['cdnUsed'] === false, 'health states boundaries');
$assert($h['plotlyJsSha256Verified'] === true, 'health reports verified plotly.js');
echo "PASS - SC-FIG-01 generic figure-bundle renderer WordPress loader contract\n";
