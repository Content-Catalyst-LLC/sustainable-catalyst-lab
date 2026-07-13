<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

if (!function_exists('add_shortcode')) {
    function add_shortcode() {}
}

$root = dirname(__DIR__);

function v0231_assert($condition, $message) {
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
    . 'biosignal-production-v0231.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-biosignal-production-v0231.css'
);
$production = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biosignal-production-v0231.php'
);
$engine_runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'biomedical-engineering-biosignals-v0230.js'
);
$engine_rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biomedical-biosignals-rest-v0230.php'
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'biomedical-engineering-biosignals-v0230.json'
    ),
    true
);

v0231_assert(
    strpos(
        $main,
        'class-sc-lab-biosignal-production-v0231.php'
    ) !== false,
    'Production bootstrap include'
);

v0231_assert(
    strpos(
        $production,
        "const VERSION = '0.23.1';"
    ) !== false,
    'Production PHP layer version'
);

v0231_assert(
    strpos(
        $production,
        "const ENGINE_VERSION = '0.23.0';"
    ) !== false,
    'Production PHP engine version'
);

v0231_assert(
    strpos(
        $runtime,
        "const VERSION = '0.23.1';"
    ) !== false,
    'Production browser runtime version'
);

v0231_assert(
    strpos(
        $runtime,
        "const ENGINE_VERSION = '0.23.0';"
    ) !== false,
    'Production browser engine version'
);

v0231_assert(
    strpos(
        $engine_runtime,
        "const VERSION = '0.23.0';"
    ) !== false,
    'Preserved browser engine version'
);

v0231_assert(
    strpos(
        $engine_rest,
        "const VERSION = '0.23.0';"
    ) !== false,
    'Preserved REST engine version'
);

v0231_assert(
    is_array($catalog)
    && $catalog['version'] === '0.23.0'
    && count($catalog['methods']) === 48
    && count($catalog['benchmarks']) === 48
    && count($catalog['categories']) === 8,
    'Preserved v0.23.0 biomedical contract'
);

v0231_assert(
    substr_count(
        $template,
        'data-lab-module="biomedical-engineering-biosignals"'
    ) === 1
    && substr_count(
        $template,
        'data-module-panel="biomedical-engineering-biosignals"'
    ) === 1
    && substr_count(
        $template,
        'data-biomedical-biosignals-root'
    ) === 1,
    'Canonical biomedical panel and mount'
);

foreach (
    array(
        'duplicateRootsRemoved',
        'staleMarkersCleared',
        'MutationObserver',
        'navigation-click',
        'module-opened',
        'pageshow',
        'window-focus',
        'popstate',
        'visibility-restored',
        'hashchange',
        'repair-required',
        'scheduleRepair',
        'contractReady',
    )
    as $marker
) {
    v0231_assert(
        strpos($runtime, $marker) !== false,
        'Runtime reliability marker: ' . $marker
    );
}

v0231_assert(
    strpos(
        $production,
        '/compute/biomedical/biosignals/production-health'
    ) !== false,
    'WordPress production health route'
);

v0231_assert(
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
    ) !== false
    && strpos(
        $style,
        'white-space: pre-wrap'
    ) !== false,
    'Mobile and overflow reliability styles'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biomedical-biosignals-rest-v0230.php'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biosignal-production-v0231.php'
);

$health =
    SC_Lab_Biosignal_Production_V0231::
        health_payload();

v0231_assert(
    $health['ok'] === true
    && $health['status'] === 'ready'
    && $health['release'] === '0.23.1'
    && $health['engineRelease'] === '0.23.0',
    'Production health status'
);

v0231_assert(
    $health['methodCount'] === 48
    && $health['benchmarkCount'] === 48
    && $health['categoryCount'] === 8,
    'Production health contract counts'
);

v0231_assert(
    $health['assets']['contract'] === true
    && $health['assets']['engineScript'] === true
    && $health['assets']['engineStyle'] === true
    && $health['assets']['productionScript'] === true
    && $health['assets']['productionStyle'] === true,
    'Production health asset checks'
);

v0231_assert(
    $health['responsibleUse']['clinicalUse']
        === false
    && $health['responsibleUse']['diagnosticUse']
        === false
    && $health['responsibleUse']['patientMonitoring']
        === false,
    'Non-clinical production boundary'
);

echo "Lab v0.23.1 PHP structural tests passed: "
    . "production health ready, "
    . $health['methodCount']
    . " methods, "
    . $health['benchmarkCount']
    . " benchmarks, "
    . $health['categoryCount']
    . " categories.\n";
