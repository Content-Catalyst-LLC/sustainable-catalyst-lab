<?php
// SC-FIG-02B Vega-Lite views: WordPress loader contract (stubbed WordPress), including fail-closed vendor checks.
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

$tampered = getenv('FIG02B_TAMPERED_DIR');
define('SC_LAB_DIR', $tampered ? rtrim($tampered, '/') . '/' : $root . '/');
require $root . '/includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php';
require $root . '/includes/class-sc-lab-graph-studio-figure-bundle-renderer.php';
$F = 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A';
$G = 'SC_Lab_Graph_Studio_Figure_Bundle_Renderer';
$F::init(); $G::init();
$reset = function () use ($F, $G) {
    $GLOBALS['enqueued'] = array(); $GLOBALS['inline'] = array();
    foreach (array(array($F, 'vendor_verified'), array($G, 'vega_verified')) as $c) {
        $p = new ReflectionProperty($c[0], $c[1]); $p->setAccessible(true); $p->setValue(null, null);
    }
};
$run = function () { foreach ($GLOBALS['actions']['wp_enqueue_scripts'] as $cb) { call_user_func($cb); } };
$cfg = function () { return $GLOBALS['inline']['sc-lab-graph-studio-figure-bundle-renderer']['before'][0]; };
$vega = array('sc-lab-vega-640', 'sc-lab-vega-lite-650', 'sc-lab-vega-interpreter-232', 'sc-lab-graph-studio-vega-lite-fig02b');

// The pins in PHP and in the JS module are the same, and match the vendored files' SOURCE.json.
$js = file_get_contents($root . '/' . $G::FIG02B_JS);
foreach ($G::VEGA as $lib) {
    $assert(strpos($js, "'" . $lib[1] . "'") !== false, $lib[0] . ' pinned identically in PHP and JS');
    $meta = json_decode(file_get_contents($root . '/' . dirname($lib[0]) . '/SOURCE.json'), true);
    $assert($meta['sha256'] === $lib[1] && $meta['version'] === $lib[2], $lib[0] . ' pin agrees with SOURCE.json');
}

// FIG-02B alone does nothing: it needs the renderer on.
$GLOBALS['options'][$G::FIG02B_OPTION] = '1';
$reset(); $run();
$assert($GLOBALS['enqueued'] === array() && $G::fig02b_enabled() === false, 'FIG-02B without the renderer enqueues nothing');

// Renderer on, FIG-02B off (default): no Vega served, config says so.
$GLOBALS['options'][$G::OPTION] = '1';
unset($GLOBALS['options'][$G::FIG02B_OPTION]);
$reset(); $run();
foreach ($vega as $h) { $assert(!isset($GLOBALS['enqueued'][$h]), "default off: $h not enqueued"); }
$assert(strpos($cfg(), '"vegaLite":false') !== false, 'default off: renderer config vegaLite false');
$GLOBALS['filters']['sc_lab_fig02b_vega_lite_enabled'] = function () { return 1; };
$assert($G::fig02b_enabled() === false, 'only boolean true from the filter enables FIG-02B');
unset($GLOBALS['filters']['sc_lab_fig02b_vega_lite_enabled']);

$GLOBALS['options'][$G::FIG02B_OPTION] = '1';
if ($tampered) {
    $reset(); $run();
    foreach ($vega as $h) { $assert(!isset($GLOBALS['enqueued'][$h]), "modified Vega file: $h never served (fail closed)"); }
    $assert(isset($GLOBALS['enqueued']['sc-lab-graph-studio-figure-bundle-renderer'], $GLOBALS['enqueued']['sc-lab-plotly-js-331']), 'Plotly rendering unaffected by a bad Vega file');
    $assert(strpos($cfg(), '"vegaLite":false') !== false, 'renderer told Vega-Lite is unavailable');
    $G::routes(); $h = $G::health();
    $assert($h['fig02b']['vegaSha256Verified'] === false && $h['fig02b']['served'] === false && !isset($h['renderers']['image/svg+xml']), 'health reports the Vega files unverified');
    echo "PASS - FIG-02B loader refuses a modified vendored Vega file\n";
    exit(0);
}

// Both on: vendored Vega in order, FIG-02B module before the renderer, no CDN.
$reset(); $run();
$e = $GLOBALS['enqueued'];
foreach ($vega as $h) { $assert(isset($e[$h]), "$h enqueued"); }
foreach ($G::VEGA as $handle => $lib) {
    $assert($e[$handle][0] === SC_LAB_URL . $lib[0] && $e[$handle][2] === $lib[2], "$handle served from the plugin at its pinned version");
}
$assert($e['sc-lab-vega-lite-650'][1] === array('sc-lab-vega-640') && $e['sc-lab-vega-interpreter-232'][1] === array('sc-lab-vega-640'), 'Vega loads before Vega-Lite and the interpreter');
$assert(in_array('sc-lab-vega-interpreter-232', $e['sc-lab-graph-studio-vega-lite-fig02b'][1], true) && in_array('sc-lab-graph-studio-plotly-preview-fig02a', $e['sc-lab-graph-studio-vega-lite-fig02b'][1], true), 'FIG-02B module needs the interpreter and FIG-02A primitives');
$assert(in_array('sc-lab-graph-studio-vega-lite-fig02b', $e['sc-lab-graph-studio-figure-bundle-renderer'][1], true), 'renderer loads after FIG-02B');
foreach ($e as $h => $v) { $assert(strpos($v[0], SC_LAB_URL) === 0, "$h is served from the plugin (no CDN)"); }
$assert(strpos($cfg(), '"vegaLite":true') !== false, 'renderer config vegaLite true');

$G::routes();
$h = $G::health();
$assert($h['fig02b']['enabled'] === true && $h['fig02b']['defaultEnabled'] === false && $h['fig02b']['vegaSha256Verified'] === true && $h['fig02b']['evalUsed'] === false, 'health reports FIG-02B state');
$assert(isset($h['renderers']['application/vnd.vegalite.v5+json'], $h['renderers']['image/svg+xml']), 'health lists the Vega-Lite and SVG renderers');
$assert($h['publicationPerformed'] === false && $h['uploadPerformed'] === false && $h['cdnUsed'] === false && $h['secondGraphStudio'] === false, 'health keeps the renderer boundaries');
echo "PASS - SC-FIG-02B Vega-Lite WordPress loader contract\n";
