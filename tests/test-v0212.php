<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

$root = dirname(__DIR__);

function v0212_assert($condition, $message) {
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
    . 'biochemistry-visualization-batch-v0212.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-biochemistry-visualization-batch-v0212.css'
);
$presets = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'biochemistry-visualization-presets-v0212.json'
    ),
    true
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'biochemistry-molecular-analysis-methods.json'
    ),
    true
);

v0212_assert(
    preg_match(
        '/Version:\s*0\.21\.2/',
        $main
    ) === 1,
    'Plugin header'
);

v0212_assert(
    strpos(
        $main,
        "define('SC_LAB_VERSION', '0.21.2')"
    ) !== false,
    'Plugin version constant'
);

v0212_assert(
    strpos(
        $main,
        'class-sc-lab-biochemistry-visualization-batch-v0212.php'
    ) !== false,
    'Visualization bootstrap'
);

v0212_assert(
    strpos(
        $main,
        'class-sc-lab-biochemistry-batch-rest-v0212.php'
    ) !== false,
    'Batch REST bootstrap'
);

v0212_assert(
    strpos(
        $template,
        'data-biochemistry-visualization-batch-root'
    ) !== false,
    'Visualization and batch mount'
);

v0212_assert(
    is_array($presets)
    && $presets['version'] === '0.21.2'
    && count($presets['presets']) === 7,
    'Seven visualization presets'
);

v0212_assert(
    is_array($catalog)
    && $catalog['version'] === '0.21.0'
    && count($catalog['methods']) === 48
    && count($catalog['benchmarks']) === 48,
    'Preserved Biochemistry analysis contract'
);

foreach (
    array(
        'linearRegression',
        'generatePresetData',
        'batchRun',
        'coefficientOfVariationPercent',
        'Export results CSV',
        'MutationObserver',
    )
    as $marker
) {
    v0212_assert(
        strpos($runtime, $marker) !== false,
        'Runtime marker: ' . $marker
    );
}

v0212_assert(
    strpos($style, '.sc-bvb-chart')
        !== false
    && strpos($style, '@media (max-width: 760px)')
        !== false,
    'Visualization and mobile styles'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biochemistry-molecular-analysis-rest.php'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biochemistry-batch-rest-v0212.php'
);

$batch =
    SC_Lab_Biochemistry_Batch_REST_V0212::
        batch_calculate(
            'bc.michaelis_menten',
            array(
                array(
                    'sample' => 'sample-1',
                    'vmax' => 100,
                    'substrate' => 2,
                    'km' => 0.5,
                ),
                array(
                    'sample' => 'sample-2',
                    'vmax' => 100,
                    'substrate' => 3,
                    'km' => 0.5,
                ),
                array(
                    'sample' => 'sample-3',
                    'vmax' => 100,
                    'substrate' => 1,
                    'km' => 0.5,
                ),
            )
        );

v0212_assert(
    $batch['version'] === '0.21.2',
    'Batch schema version'
);

v0212_assert(
    $batch['analysisEngineVersion'] === '0.21.0',
    'Preserved analysis engine version'
);

v0212_assert(
    $batch['rowCount'] === 3
    && $batch['successCount'] === 3
    && $batch['errorCount'] === 0,
    'Batch row accounting'
);

v0212_assert(
    isset($batch['statistics']['velocity'])
    && $batch['statistics']['velocity']['n'] === 3,
    'Batch output statistics'
);

echo "Lab v0.21.2 PHP tests passed: "
    . count($presets['presets'])
    . " visualization presets, "
    . $batch['rowCount']
    . " batch rows.\n";
