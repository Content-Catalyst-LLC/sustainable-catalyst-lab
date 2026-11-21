<?php
/**
 * SC-LAB-UI-03: isolated WordPress action-hook acceptance.
 * This tests Lab-only legacy gate suppression without loading WordPress,
 * contacting Bluehost, or accessing any site/user records.
 */
declare(strict_types=1);
define('ABSPATH', __DIR__ . '/');
$GLOBALS['wp_filter'] = array();
$GLOBALS['test_is_lab'] = false;

final class WP_Hook {
    public $callbacks = array();
}
function test_hook_key($fn): string {
    if (is_string($fn)) { return 'fn:' . $fn; }
    if (is_array($fn)) {
        $owner = is_object($fn[0]) ? get_class($fn[0]) : (string) $fn[0];
        return 'method:' . $owner . '::' . (string) $fn[1];
    }
    return 'unknown';
}
function add_action($hook, $fn, $priority = 10, $accepted_args = 1) {
    global $wp_filter;
    if (!isset($wp_filter[$hook])) { $wp_filter[$hook] = new WP_Hook(); }
    $wp_filter[$hook]->callbacks[$priority][test_hook_key($fn)] =
        array('function' => $fn, 'accepted_args' => $accepted_args);
    return true;
}
function remove_action($hook, $fn, $priority = 10) {
    global $wp_filter;
    $key = test_hook_key($fn);
    if (!isset($wp_filter[$hook]->callbacks[$priority][$key])) { return false; }
    unset($wp_filter[$hook]->callbacks[$priority][$key]);
    return true;
}
function has_action($hook, $fn) {
    global $wp_filter;
    if (empty($wp_filter[$hook])) { return false; }
    foreach ($wp_filter[$hook]->callbacks as $priority => $list) {
        if (isset($list[test_hook_key($fn)])) { return $priority; }
    }
    return false;
}
function is_admin() { return false; }
function is_page($slug) { return $GLOBALS['test_is_lab'] && $slug === 'lab'; }

require_once __DIR__ . '/../includes/class-sc-lab-production-safe-boot-v015206.php';
$c = 'SC_Lab_Production_Safe_Boot_V015206';
$c::init();
$early = array('SC_Lab_Production_Safe_Boot_V015205', 'gate_frontend_assets');
$late = array('SC_Lab_Reproducible_Protocol_Notebook_V01540', 'gate_frontend_assets');
$footer = array('SC_Lab_Reproducible_Protocol_Notebook_V01540', 'gate_footer_scripts');
$footer_new = array('SC_Lab_4D_Front_Door_Visual_Polish_V016313', 'enqueue_after_front_door_repair');
$ordinary = array('SC_Lab_Unified_Workspace_Shell_V016312', 'enqueue_after_legacy_gate');
$other = array('Other_Plugin', 'gate_frontend_assets');
$core = '_wp_footer_scripts';
add_action('wp_enqueue_scripts', $early, PHP_INT_MAX);
add_action('wp_enqueue_scripts', $late, PHP_INT_MAX);
add_action('wp_enqueue_scripts', $ordinary, PHP_INT_MAX);
add_action('wp_enqueue_scripts', $other, PHP_INT_MAX);
add_action('wp_print_footer_scripts', $core, 10);
add_action('wp_print_footer_scripts', $footer, PHP_INT_MAX);
add_action('wp_print_footer_scripts', $footer_new, PHP_INT_MAX);

function verify($condition, string $name) {
    if (!$condition) { fwrite(STDERR, "FAIL - $name\n"); exit(1); }
}
$c::retire_legacy_asset_gates();
verify(has_action('wp_enqueue_scripts', $early) === PHP_INT_MAX,
    'non-Lab request must retain older gates');
verify(has_action('wp_print_footer_scripts', $footer) === PHP_INT_MAX,
    'non-Lab request must retain legacy footer callbacks');

$GLOBALS['test_is_lab'] = true;
$_SERVER['REQUEST_URI'] = '/lab/';
$c::retire_legacy_asset_gates();
verify(has_action('wp_enqueue_scripts', $early) === false, 'old safe gate removed');
verify(has_action('wp_enqueue_scripts', $late) === false, '0.154.0 gate removed');
verify(has_action('wp_print_footer_scripts', $footer) === false, '0.154.0 footer gate removed');
verify(has_action('wp_print_footer_scripts', $footer_new) === false, 'later footer enqueue removed');
verify(has_action('wp_enqueue_scripts', $ordinary) === PHP_INT_MAX, 'ordinary Lab enqueue preserved');
verify(has_action('wp_enqueue_scripts', $other) === PHP_INT_MAX, 'other plugins preserved');
verify(has_action('wp_print_footer_scripts', $core) === 10, 'WordPress core footer printer preserved');
verify(has_action('wp_enqueue_scripts', array($c, 'gate_frontend_assets')) === PHP_INT_MAX,
    'canonical Lab enqueue gate preserved');
verify(has_action('wp_print_footer_scripts', array($c, 'gate_footer_scripts')) === 9,
    'canonical Lab footer gate runs before core');
echo "PASS - SC-LAB-UI-03 canonical safe gate owns Lab-only queue; preserves WordPress and other plugins\n";
