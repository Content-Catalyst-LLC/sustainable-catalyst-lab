<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) { function add_action() {} }
if (!function_exists('add_shortcode')) { function add_shortcode() {} }

$root = dirname(__DIR__);
function v0251_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$main = file_get_contents($root . '/sustainable-catalyst-lab.php');
$template = file_get_contents($root . '/templates/lab-app.php');
$runtime = file_get_contents($root . '/assets/js/modules/instrumentation-production-v0251.js');
$style = file_get_contents($root . '/assets/css/sc-lab-instrumentation-production-v0251.css');
$production = file_get_contents($root . '/includes/class-sc-lab-instrumentation-production-v0251.php');
$engine_runtime = file_get_contents($root . '/assets/js/modules/laboratory-data-instrumentation-v0250.js');
$engine_rest = file_get_contents($root . '/includes/class-sc-lab-laboratory-instrumentation-rest-v0250.php');
$catalog = json_decode(file_get_contents($root . '/contracts/laboratory-data-instrumentation-v0250.json'), true);

v0251_assert(strpos($main, 'class-sc-lab-instrumentation-production-v0251.php') !== false, 'Production bootstrap include');
v0251_assert(strpos($production, "const VERSION = '0.25.1';") !== false, 'Production PHP version');
v0251_assert(strpos($production, "const ENGINE_VERSION = '0.25.0';") !== false, 'Production engine version');
v0251_assert(strpos($runtime, "const VERSION = '0.25.1';") !== false, 'Production browser version');
v0251_assert(strpos($runtime, "const ENGINE_VERSION = '0.25.0';") !== false, 'Browser engine version');
v0251_assert(strpos($engine_runtime, "VERSION='0.25.0'") !== false || strpos($engine_runtime, "VERSION = '0.25.0'") !== false, 'Preserved browser engine');
v0251_assert(strpos($engine_rest, "const VERSION='0.25.0'") !== false || strpos($engine_rest, "const VERSION = '0.25.0'") !== false, 'Preserved REST engine');

v0251_assert(
    is_array($catalog)
    && $catalog['version'] === '0.25.0'
    && count($catalog['methods']) === 48
    && count($catalog['benchmarks']) === 48
    && count($catalog['categories']) === 8
    && count($catalog['recordTypes']) === 9
    && count($catalog['connectionProfiles']) === 8
    && count($catalog['qualityFlags']) === 8,
    'Preserved v0.25.0 instrumentation contract'
);

v0251_assert(
    substr_count($template, 'data-lab-module="laboratory-data-instrumentation"') === 1
    && substr_count($template, 'data-module-panel="laboratory-data-instrumentation"') === 1
    && substr_count($template, 'data-laboratory-instrumentation-root') === 1,
    'Canonical instrumentation panel and root'
);

foreach (array(
    'duplicateRootsRemoved', 'staleMarkersCleared', 'MutationObserver',
    'navigation-click', 'module-opened', 'pageshow', 'window-focus',
    'popstate', 'visibility-restored', 'online', 'resize',
    'orientationchange', 'hashchange', 'repair-required',
    'scheduleRepair', 'contractReady'
) as $marker) {
    v0251_assert(strpos($runtime, $marker) !== false, 'Runtime reliability marker: ' . $marker);
}

v0251_assert(
    strpos($production, '/compute/instrumentation/production-health') !== false,
    'WordPress production health route'
);
v0251_assert(
    strpos($style, '@media (max-width: 760px)') !== false
    && strpos($style, 'min-height: 44px') !== false
    && strpos($style, 'overflow-x: auto') !== false
    && strpos($style, 'white-space: pre-wrap') !== false
    && strpos($style, 'width: max-content') !== false,
    'Mobile, output, and long-table reliability styles'
);

require_once($root . '/includes/class-sc-lab-laboratory-instrumentation-rest-v0250.php');
require_once($root . '/includes/class-sc-lab-instrumentation-production-v0251.php');
$health = SC_Lab_Instrumentation_Production_V0251::health_payload();

v0251_assert(
    $health['ok'] === true
    && $health['status'] === 'ready'
    && $health['release'] === '0.25.1'
    && $health['engineRelease'] === '0.25.0',
    'Production health status'
);
v0251_assert(
    $health['methodCount'] === 48
    && $health['benchmarkCount'] === 48
    && $health['categoryCount'] === 8
    && $health['recordTypeCount'] === 9
    && $health['connectionProfileCount'] === 8
    && $health['qualityFlagCount'] === 8,
    'Production health contract counts'
);
v0251_assert(!in_array(false, $health['assets'], true), 'Production health asset checks');
v0251_assert(
    $health['boundaries']['automaticLocalDeviceAccess'] === false
    && $health['boundaries']['clinicalInstrumentation'] === false
    && $health['boundaries']['regulatedReleaseAuthority'] === false
    && $health['boundaries']['localFirstManualOperation'] === true,
    'Instrumentation production boundaries'
);

echo "Lab v0.25.1 PHP structural tests passed: production health ready, 48 methods, 48 benchmarks, 8 categories, 9 records, 8 connections, 8 quality flags.\n";
