<?php
// SC-FIG-04.1: Lab 0.163.1.8 refuses a Research bridge paired with another Lab release (stubbed WordPress).
define('ABSPATH', '/');
define('SC_LAB_RELEASE_VERSION', '0.163.1.8');
$plugins = sys_get_temp_dir() . '/sc-fig041-plugins-' . getmypid();
define('WP_PLUGIN_DIR', $plugins);
$assert = function ($cond, $msg) { if (!$cond) { fwrite(STDERR, "FAIL - $msg\n"); exit(1); } };

$GLOBALS['options'] = array('active_plugins' => array());
$GLOBALS['hooks'] = array();
$GLOBALS['can'] = true;
class WPDie extends Exception {}
function add_action($tag, $cb, $prio = 10, $args = 1) { $GLOBALS['hooks'][$tag][] = $cb; }
function register_activation_hook($file, $cb) { $GLOBALS['hooks']['activate:' . $file][] = $cb; }
function get_option($k, $d = false) { return array_key_exists($k, $GLOBALS['options']) ? $GLOBALS['options'][$k] : $d; }
function is_multisite() { return false; }
function current_user_can($cap) { return $GLOBALS['can']; }
function esc_html($s) { return htmlspecialchars($s, ENT_QUOTES); }
function wp_die($msg, $title = '', $args = array()) { throw new WPDie($msg . ' [' . $args['response'] . ']'); }
function get_file_data($file, $headers) {
    $text = file_get_contents($file, false, null, 0, 8192);
    $out = array();
    foreach ($headers as $k => $label) { $out[$k] = preg_match('/^[ \t\/*#@]*' . preg_quote($label, '/') . ':(.*)$/mi', $text, $m) ? trim($m[1]) : ''; }
    return $out;
}
function plugin($rel, $name, $version) {
    @mkdir(dirname(WP_PLUGIN_DIR . '/' . $rel), 0700, true);
    file_put_contents(WP_PLUGIN_DIR . '/' . $rel, "<?php\n/**\n * Plugin Name: $name\n * Version: $version\n */\n");
}
function reset_cache() { $r = new ReflectionProperty('SC_Lab_Plugin_Compatibility_FIG041', 'incompatible'); $r->setAccessible(true); $r->setValue(null, false); }

require dirname(__DIR__) . '/includes/class-sc-lab-plugin-compatibility-fig041.php';
$C = 'SC_Lab_Plugin_Compatibility_FIG041';
$C::init('/plugins/sustainable-catalyst-lab/sustainable-catalyst-lab.php');
$assert(count($GLOBALS['hooks']['activate:/plugins/sustainable-catalyst-lab/sustainable-catalyst-lab.php']) === 1 && isset($GLOBALS['hooks']['activate_plugin']), 'hooks registered');

$dies = function ($fn) { try { $fn(); return null; } catch (WPDie $e) { return $e->getMessage(); } };
$checks = 0;

// 1. No bridge, bridge 0.4.0 or an older bridge 0.2.4: Lab activates; renderer not blocked.
foreach (array(null, '0.4.0', '0.2.4') as $v) {
    $GLOBALS['options']['active_plugins'] = array();
    if ($v) { plugin('sc-research-bridge/sc-research-bridge.php', 'Sustainable Catalyst Research Bridge', $v); $GLOBALS['options']['active_plugins'] = array('sc-research-bridge/sc-research-bridge.php'); }
    reset_cache();
    $assert($dies(array($C, 'on_activate')) === null && $C::incompatible_bridge() === null, 'Lab activates beside bridge ' . var_export($v, true)); $checks++;
}

// 2. Bridge 0.3.0 active (any directory name): Lab activation refused with 409 and both versions named.
plugin('research-bridge-copy/main.php', 'Sustainable Catalyst Research Bridge', '0.3.0');
$GLOBALS['options']['active_plugins'] = array('akismet/akismet.php', 'research-bridge-copy/main.php');
reset_cache();
$msg = $dies(array($C, 'on_activate'));
$assert($msg !== null && strpos($msg, 'Lab 0.163.1.8 cannot run with Sustainable Catalyst Research Bridge 0.3.0') !== false && strpos($msg, '[409]') !== false, 'Lab activation refused beside bridge 0.3.0: ' . $msg); $checks++;
$assert($C::incompatible_bridge() === '0.3.0', 'renderer fail-closed signal set'); $checks++;

// 3. Lab active: activating bridge 0.3.x is refused; 0.4.0 and unrelated plugins are not.
$GLOBALS['options']['active_plugins'] = array();
reset_cache();
plugin('sc-research-bridge/sc-research-bridge.php', 'Sustainable Catalyst Research Bridge', '0.3.1');
$assert(strpos((string) $dies(function () use ($C) { $C::on_plugin_activation('sc-research-bridge/sc-research-bridge.php'); }), 'Bridge 0.3.1') !== false, 'bridge 0.3.1 activation refused'); $checks++;
plugin('sc-research-bridge/sc-research-bridge.php', 'Sustainable Catalyst Research Bridge', '0.4.0');
$assert($dies(function () use ($C) { $C::on_plugin_activation('sc-research-bridge/sc-research-bridge.php'); }) === null, 'bridge 0.4.0 activation allowed'); $checks++;
plugin('other/other.php', 'Some Other Plugin', '0.3.0');
$assert($dies(function () use ($C) { $C::on_plugin_activation('other/other.php'); }) === null, 'unrelated 0.3.0 plugin allowed'); $checks++;
$assert($dies(function () use ($C) { $C::on_plugin_activation('missing/missing.php'); }) === null, 'missing plugin file ignored'); $checks++;

// 4. Admin notice only for users who can activate plugins.
$GLOBALS['options']['active_plugins'] = array('research-bridge-copy/main.php');
reset_cache();
ob_start(); $C::notice(); $out = ob_get_clean();
$assert(strpos($out, 'notice-error') !== false && strpos($out, 'Figure rendering is off') !== false, 'admin notice shown'); $checks++;
$GLOBALS['can'] = false;
ob_start(); $C::notice(); $assert(ob_get_clean() === '', 'no notice for other users'); $checks++;

// 5. The figure-bundle renderer fails closed while the mismatch stands.
$src = file_get_contents(dirname(__DIR__) . '/includes/class-sc-lab-graph-studio-figure-bundle-renderer.php');
$assert(preg_match("/function is_enabled\(\) \{\s*\/\/[^\n]*\n\s*if \(class_exists\('SC_Lab_Plugin_Compatibility_FIG041'\) && SC_Lab_Plugin_Compatibility_FIG041::incompatible_bridge\(\) !== null\) \{ return false; \}/", $src) === 1, 'renderer is_enabled checks the pairing first'); $checks++;
$main = file_get_contents(dirname(__DIR__) . '/sustainable-catalyst-lab.php');
$assert(strpos($main, "SC_Lab_Plugin_Compatibility_FIG041::init(__FILE__);") < strpos($main, "register_activation_hook(__FILE__, array('SC_Lab_Plugin', 'activate'));"), 'guard registered before the Lab activation hook'); $checks++;

array_map('unlink', array_merge(glob($plugins . '/*/*.php')));
array_map('rmdir', glob($plugins . '/*'));
rmdir($plugins);
echo "PASS - SC-FIG-04.1 Lab/bridge pairing guard ($checks checks)\n";
