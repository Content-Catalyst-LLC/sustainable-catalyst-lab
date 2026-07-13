<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

if (!function_exists('add_shortcode')) {
    function add_shortcode() {}
}

$root = dirname(__DIR__);

function v0230_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$contract = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'biomedical-engineering-biosignals-v0230.json'
    ),
    true
);
$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'biomedical-engineering-biosignals-v0230.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-biomedical-engineering-biosignals-v0230.css'
);
$ui = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biomedical-engineering-biosignals-v0230.php'
);
$rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biomedical-biosignals-rest-v0230.php'
);

v0230_assert(
    $contract['version'] === '0.23.0',
    'Contract version'
);
v0230_assert(
    count($contract['categories']) === 8,
    'Eight biosignal categories'
);
v0230_assert(
    count($contract['methods']) === 48,
    'Forty-eight biosignal methods'
);
v0230_assert(
    count($contract['benchmarks']) === 48,
    'Forty-eight deterministic benchmarks'
);
v0230_assert(
    strpos(
        $runtime,
        "const VERSION = '0.23.0';"
    ) !== false,
    'Browser engine version'
);
v0230_assert(
    strpos(
        $runtime,
        'analyzeSignal'
    ) !== false
    && strpos(
        $runtime,
        'batchExecute'
    ) !== false
    && strpos(
        $runtime,
        'BioprocessValidationProvenance'
    ) !== false,
    'Browser workflow integration'
);
v0230_assert(
    strpos(
        $style,
        '@media (max-width: 760px)'
    ) !== false
    && strpos(
        $style,
        'min-height: 44px'
    ) !== false,
    'Mobile reliability styles'
);
v0230_assert(
    strpos(
        $ui,
        'sc_lab_biomedical_engineering_biosignals'
    ) !== false,
    'Focused shortcode'
);
v0230_assert(
    strpos(
        $rest,
        '/compute/biomedical/biosignals/batch'
    ) !== false,
    'Batch REST route'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biomedical-biosignals-rest-v0230.php'
);

foreach ($contract['benchmarks'] as $benchmark) {
    $result =
        SC_Lab_Biomedical_Biosignals_REST_V0230::
            execute(
                $benchmark['methodId'],
                $benchmark['inputs']
            );
    $delta = abs(
        (float) $result['value']
        - (float) $benchmark['expected']
    );
    $allowed = max(
        (float) $benchmark['tolerance'],
        abs(
            (float) $benchmark['expected']
        ) * 1.0e-8
    );

    v0230_assert(
        $delta <= $allowed,
        'Benchmark: '
        . $benchmark['methodId']
        . ' got '
        . $result['value']
        . ' expected '
        . $benchmark['expected']
    );
}

$waveform =
    SC_Lab_Biomedical_Biosignals_REST_V0230::
        analyze_signal(
            array(-1, 1, -1, 1),
            100
        );

v0230_assert(
    $waveform['sampleCount'] === 4,
    'Waveform sample count'
);
v0230_assert(
    abs(
        $waveform['durationSeconds'] - 0.03
    ) < 1.0e-12,
    'Waveform duration'
);
v0230_assert(
    $waveform['rms'] === 1.0,
    'Waveform RMS'
);
v0230_assert(
    $waveform['peakToPeak'] === 2.0,
    'Waveform peak-to-peak'
);
v0230_assert(
    $waveform['zeroCrossingCount'] === 3,
    'Waveform crossing count'
);
v0230_assert(
    $waveform['zeroCrossingRate'] === 100.0,
    'Waveform crossing rate'
);

$batch =
    SC_Lab_Biomedical_Biosignals_REST_V0230::
        batch_execute(
            array(
                array(
                    'methodId' =>
                        'heart-rate-from-rr',
                    'inputs' => array(
                        'rrSeconds' => 0.8,
                    ),
                ),
                array(
                    'methodId' =>
                        'heart-rate-from-rr',
                    'inputs' => array(
                        'rrSeconds' => 0,
                    ),
                ),
                array(
                    'methodId' =>
                        'signal-quality-index',
                    'inputs' => array(
                        'snrDb' => 20,
                        'missingPercent' => 2,
                        'clippingPercent' => 1,
                    ),
                ),
            )
        );

v0230_assert(
    $batch['rowCount'] === 3
    && $batch['successCount'] === 2
    && $batch['errorCount'] === 1,
    'Batch row isolation'
);

$health =
    SC_Lab_Biomedical_Biosignals_REST_V0230::
        health_payload();

v0230_assert(
    $health['ok'] === true
    && $health['methodCount'] === 48
    && $health['benchmarkCount'] === 48
    && $health['categoryCount'] === 8,
    'Health contract'
);

echo "Lab v0.23.0 PHP tests passed: "
    . "48 methods, 48 benchmarks, "
    . "8 categories, waveform analysis, batch isolation.\n";
