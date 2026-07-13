<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

$root = dirname(__DIR__);

function v0221_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$main = file_get_contents(
    $root . '/sustainable-catalyst-lab.php'
);
$template = file_get_contents(
    $root . '/templates/lab-app.php'
);
$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'bioprocess-production-v0221.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-bioprocess-production-v0221.css'
);
$production = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-bioprocess-production-v0221.php'
);
$engine_runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'biotechnology-bioprocess-engineering-v0220.js'
);
$engine_rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biotechnology-bioprocess-rest-v0220.php'
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'biotechnology-bioprocess-methods-v0220.json'
    ),
    true
);

v0221_assert(
    preg_match(
        '/Version:\s*0\.22\.1/',
        $main
    ) === 1,
    'Plugin header'
);

v0221_assert(
    strpos(
        $main,
        "define('SC_LAB_VERSION', '0.22.1')"
    ) !== false,
    'Plugin version constant'
);

v0221_assert(
    strpos(
        $main,
        'class-sc-lab-bioprocess-production-v0221.php'
    ) !== false,
    'Production bootstrap include'
);

v0221_assert(
    strpos(
        $production,
        "const VERSION = '0.22.1';"
    ) !== false,
    'Production PHP layer version'
);

v0221_assert(
    strpos(
        $runtime,
        "const VERSION = '0.22.1';"
    ) !== false,
    'Production browser runtime version'
);

v0221_assert(
    strpos(
        $runtime,
        "const ENGINE_VERSION = '0.22.0';"
    ) !== false,
    'Production engine contract version'
);

v0221_assert(
    strpos(
        $engine_runtime,
        "const VERSION = '0.22.0';"
    ) !== false,
    'Preserved browser engine version'
);

v0221_assert(
    strpos(
        $engine_rest,
        "const VERSION = '0.22.0';"
    ) !== false,
    'Preserved REST engine version'
);

v0221_assert(
    is_array($catalog)
    && $catalog['version'] === '0.22.0'
    && count($catalog['methods']) === 48
    && count($catalog['benchmarks']) === 48
    && count($catalog['categories']) === 8,
    'Preserved v0.22.0 calculation contract'
);

v0221_assert(
    strpos(
        $template,
        'data-lab-module="biotechnology-bioprocess-engineering"'
    ) !== false
    && strpos(
        $template,
        'data-module-panel="biotechnology-bioprocess-engineering"'
    ) !== false
    && strpos(
        $template,
        'data-biotechnology-bioprocess-root'
    ) !== false,
    'Canonical bioprocess panel and mount'
);

foreach (
    array(
        'duplicateRootsRemoved',
        'staleMarkersCleared',
        'MutationObserver',
        'navigation-click',
        'pageshow',
        'hashchange',
        'repair-required',
        'scheduleRepair',
    )
    as $marker
) {
    v0221_assert(
        strpos($runtime, $marker) !== false,
        'Runtime reliability marker: ' . $marker
    );
}

v0221_assert(
    strpos(
        $production,
        '/compute/bioprocess/production-health'
    ) !== false,
    'Production health route'
);

v0221_assert(
    strpos(
        $style,
        '@media (max-width: 760px)'
    ) !== false
    && strpos(
        $style,
        'min-height: 44px'
    ) !== false
    && strpos(
        $style,
        'overflow-x: auto'
    ) !== false,
    'Mobile and overflow reliability styles'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biotechnology-bioprocess-rest-v0220.php'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-bioprocess-production-v0221.php'
);

$health =
    SC_Lab_Bioprocess_Production_V0221::
        health_payload();

v0221_assert(
    $health['ok'] === true
    && $health['status'] === 'ready'
    && $health['release'] === '0.22.1'
    && $health['engineRelease'] === '0.22.0',
    'Production health status'
);

v0221_assert(
    $health['methodCount'] === 48
    && $health['benchmarkCount'] === 48
    && $health['categoryCount'] === 8,
    'Production health catalog counts'
);

v0221_assert(
    $health['assets']['engineScript'] === true
    && $health['assets']['productionScript'] === true
    && $health['assets']['productionStyle'] === true,
    'Production health asset checks'
);

echo "Lab v0.22.1 PHP structural tests passed: "
    . "production health ready, "
    . $health['methodCount']
    . " methods, "
    . $health['benchmarkCount']
    . " benchmarks.\n";
