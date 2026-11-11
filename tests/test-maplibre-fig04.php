<?php
// SC-FIG-04 MapLibre views: WordPress loader contract (stubbed WordPress), including fail-closed vendor checks.
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

$tampered = getenv('FIG04_TAMPERED_DIR');
define('SC_LAB_DIR', $tampered ? rtrim($tampered, '/') . '/' : $root . '/');
require $root . '/includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php';
require $root . '/includes/class-sc-lab-graph-studio-figure-bundle-renderer.php';
$F = 'SC_Lab_Graph_Studio_Plotly_Preview_FIG02A';
$G = 'SC_Lab_Graph_Studio_Figure_Bundle_Renderer';
$F::init(); $G::init();
$reset = function () use ($F, $G) {
    $GLOBALS['enqueued'] = array(); $GLOBALS['inline'] = array();
    foreach (array(array($F, 'vendor_verified'), array($G, 'vega_verified'), array($G, 'maplibre_verified')) as $c) {
        $p = new ReflectionProperty($c[0], $c[1]); $p->setAccessible(true); $p->setValue(null, null);
    }
};
$run = function () { foreach ($GLOBALS['actions']['wp_enqueue_scripts'] as $cb) { call_user_func($cb); } };
$cfg = function () { return $GLOBALS['inline']['sc-lab-graph-studio-figure-bundle-renderer']['before'][0]; };
$ml = array('sc-lab-maplibre-gl-5240', 'sc-lab-graph-studio-maplibre-fig03a', 'sc-lab-graph-studio-maplibre-fig04', 'style:sc-lab-maplibre-gl-5240', 'style:sc-lab-graph-studio-maplibre-fig04');

// Pins agree with the vendored SOURCE.json written by scripts/package_maplibre_vendor.py.
$meta = json_decode(file_get_contents($root . '/assets/lib/maplibre-gl-5.24.0/SOURCE.json'), true);
foreach ($G::MAPLIBRE as $role => $lib) {
    $assert($meta['files'][basename($lib[0])]['sha256'] === $lib[1], "$role pin agrees with SOURCE.json");
}
$assert($meta['version'] === $G::MAPLIBRE_VERSION, 'MapLibre version agrees with SOURCE.json');

// FIG-04 alone does nothing: it needs the renderer on.
$GLOBALS['options'][$G::FIG04_OPTION] = '1';
$reset(); $run();
$assert($GLOBALS['enqueued'] === array() && $G::fig04_enabled() === false, 'FIG-04 without the renderer enqueues nothing');

// Renderer on, FIG-04 off (default).
$GLOBALS['options'][$G::OPTION] = '1';
unset($GLOBALS['options'][$G::FIG04_OPTION]);
$reset(); $run();
foreach ($ml as $h) { $assert(!isset($GLOBALS['enqueued'][$h]), "default off: $h not enqueued"); }
$assert(strpos($cfg(), '"maplibre":false') !== false, 'default off: renderer config maplibre false');
$GLOBALS['filters']['sc_lab_fig04_maplibre_enabled'] = function () { return 1; };
$assert($G::fig04_enabled() === false, 'only boolean true from the filter enables FIG-04');
unset($GLOBALS['filters']['sc_lab_fig04_maplibre_enabled']);

$GLOBALS['options'][$G::FIG04_OPTION] = '1';
if ($tampered) {
    $reset(); $run();
    foreach ($ml as $h) { $assert(!isset($GLOBALS['enqueued'][$h]), "modified MapLibre file: $h never served (fail closed)"); }
    $assert(isset($GLOBALS['enqueued']['sc-lab-graph-studio-figure-bundle-renderer'], $GLOBALS['enqueued']['sc-lab-plotly-js-331']), 'Plotly rendering unaffected by a bad MapLibre file');
    $assert(strpos($cfg(), '"maplibre":false') !== false, 'renderer told MapLibre is unavailable');
    $G::routes(); $h = $G::health();
    $assert($h['fig04']['maplibreSha256Verified'] === false && $h['fig04']['served'] === false && !isset($h['renderers']['application/vnd.sc.maplibre-view.v1+json']), 'health reports MapLibre unverified');
    echo "PASS - FIG-04 loader refuses a modified vendored MapLibre file\n";
    exit(0);
}

// Both on.
$reset(); $run();
$e = $GLOBALS['enqueued'];
foreach ($ml as $h) { $assert(isset($e[$h]), "$h enqueued"); }
$assert($e['sc-lab-maplibre-gl-5240'][0] === SC_LAB_URL . $G::MAPLIBRE['js'][0] && $e['sc-lab-maplibre-gl-5240'][2] === '5.24.0', 'MapLibre CSP build served from the plugin at its pinned version');
$assert(!isset($e['sc-lab-maplibre-worker']) && strpos(json_encode($e), 'csp-worker') === false, 'worker is not enqueued as a page script');
$assert(in_array('sc-lab-maplibre-gl-5240', $e['sc-lab-graph-studio-maplibre-fig04'][1], true) && in_array('sc-lab-graph-studio-maplibre-fig03a', $e['sc-lab-graph-studio-maplibre-fig04'][1], true), 'renderer module loads after MapLibre and the contract');
$assert(in_array('sc-lab-graph-studio-maplibre-fig04', $e['sc-lab-graph-studio-figure-bundle-renderer'][1], true), 'generic renderer loads after FIG-04');
foreach ($e as $h => $v) { $assert(strpos($v[0], SC_LAB_URL) === 0, "$h is served from the plugin (no CDN)"); }
$assert(strpos($cfg(), '"maplibre":true') !== false, 'renderer config maplibre true');
$wcfg = $GLOBALS['inline']['sc-lab-graph-studio-maplibre-fig04']['before'][0];
$expect = 'sha384-' . base64_encode(hash_file('sha384', $root . '/assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js', true));
$assert(strpos($wcfg, json_encode($expect)) !== false && strpos($wcfg, 'maplibre-gl-csp-worker.js') !== false, 'worker URL and SHA-384 handed to the browser');

$G::routes();
$h = $G::health();
$assert($h['fig04']['enabled'] === true && $h['fig04']['defaultEnabled'] === false && $h['fig04']['maplibreSha256Verified'] === true && $h['fig04']['evalUsed'] === false, 'health reports FIG-04 state');
$assert($h['fig04']['approvedTileProviders'] === array() && $h['fig04']['earthObservation'] === 'adapter-prepared-no-provider-approved', 'health states no tile or EO provider is approved');
$assert(isset($h['renderers']['application/vnd.sc.maplibre-view.v1+json']), 'health lists the MapLibre renderer');
echo "PASS - SC-FIG-04 MapLibre WordPress loader contract\n";
