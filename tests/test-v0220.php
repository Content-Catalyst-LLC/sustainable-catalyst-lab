<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

$root = dirname(__DIR__);

function v0220_assert($condition, $message) {
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
    . 'biotechnology-bioprocess-engineering-v0220.js'
);
$interface_php = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biotechnology-bioprocess-engineering-v0220.php'
);
$rest_php = file_get_contents(
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

v0220_assert(
    strpos(
        $runtime,
        "const VERSION = '0.22.0';"
    ) !== false,
    'Browser engine version'
);

v0220_assert(
    strpos(
        $interface_php,
        "const VERSION = '0.22.0';"
    ) !== false,
    'Interface version'
);

v0220_assert(
    strpos(
        $rest_php,
        "const VERSION = '0.22.0';"
    ) !== false,
    'REST engine version'
);

v0220_assert(
    strpos(
        $main,
        'class-sc-lab-biotechnology-bioprocess-engineering-v0220.php'
    ) !== false,
    'Interface bootstrap'
);

v0220_assert(
    strpos(
        $main,
        'class-sc-lab-biotechnology-bioprocess-rest-v0220.php'
    ) !== false,
    'REST bootstrap'
);

v0220_assert(
    strpos(
        $template,
        "'biotechnology-bioprocess-engineering'"
    ) !== false,
    'Bioprocess navigation entry'
);

v0220_assert(
    strpos(
        $template,
        'data-biotechnology-bioprocess-root'
    ) !== false,
    'Bioprocess panel mount'
);

v0220_assert(
    is_array($catalog)
    && $catalog['version'] === '0.22.0'
    && count($catalog['methods']) === 48
    && count($catalog['benchmarks']) === 48
    && count($catalog['categories']) === 8,
    'Catalog structure'
);

foreach (
    array(
        'simulateBatch',
        'simulateFedBatch',
        'simulateContinuous',
        'batchRun',
        'Create provenance record',
        'Engineering-use boundary',
        'MutationObserver',
    )
    as $marker
) {
    v0220_assert(
        strpos($runtime, $marker) !== false,
        'Runtime marker: ' . $marker
    );
}

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biotechnology-bioprocess-rest-v0220.php'
);

foreach ($catalog['benchmarks'] as $benchmark) {
    $analysis =
        SC_Lab_Biotechnology_Bioprocess_REST_V0220::
            calculate(
                $benchmark['methodId'],
                $benchmark['inputs']
            );
    $actual = $analysis['outputs']['result'];
    $expected = $benchmark['expected']['result'];
    $tolerance = $benchmark['tolerance']
        * max(1.0, abs($expected));

    v0220_assert(
        abs($actual - $expected) <= $tolerance,
        'Benchmark: ' . $benchmark['methodId']
    );
}

$batch =
    SC_Lab_Biotechnology_Bioprocess_REST_V0220::
        batch_calculate(
            'bp.batch_productivity',
            array(
                array(
                    'sample' => 'run-1',
                    'product_concentration' => 18,
                    'batch_time' => 36,
                ),
                array(
                    'sample' => 'run-2',
                    'product_concentration' => 19,
                    'batch_time' => 36,
                ),
                array(
                    'sample' => 'run-3',
                    'product_concentration' => 17,
                    'batch_time' => 36,
                ),
            )
        );

v0220_assert(
    $batch['rowCount'] === 3
    && $batch['successCount'] === 3
    && $batch['errorCount'] === 0,
    'Batch execution'
);

$simulation =
    SC_Lab_Biotechnology_Bioprocess_REST_V0220::
        simulate(
            'continuous',
            array(
                'volume' => 10,
                'flowRate' => 1.5,
                'muMax' => 0.5,
                'ks' => 0.5,
                'feedSubstrate' => 20,
                'yieldXs' => 0.5,
                'productConcentration' => 12,
            )
        );

v0220_assert(
    $simulation['mode'] === 'continuous'
    && $simulation['summary']['washout'] === false
    && $simulation['summary']['biomass'] > 0,
    'Continuous simulation'
);

echo "Lab v0.22.0 PHP tests passed: "
    . count($catalog['methods'])
    . " methods, "
    . count($catalog['benchmarks'])
    . " benchmarks, 3 reactor modes.\n";
