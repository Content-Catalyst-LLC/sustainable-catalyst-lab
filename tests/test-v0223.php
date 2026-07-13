<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

if (!function_exists('add_shortcode')) {
    function add_shortcode() {}
}

$root = dirname(__DIR__);

function v0223_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$contract = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'bioprocess-validation-provenance-v0223.json'
    ),
    true
);
$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'bioprocess-validation-provenance-v0223.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-bioprocess-validation-provenance-v0223.css'
);
$ui = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-bioprocess-validation-provenance-v0223.php'
);
$rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-bioprocess-validation-rest-v0223.php'
);

v0223_assert(
    $contract['version'] === '0.22.3',
    'Validation contract version'
);
v0223_assert(
    count($contract['profiles']) === 8,
    'Eight validation profiles'
);
v0223_assert(
    count($contract['eventTypes']) === 5,
    'Five provenance event types'
);
v0223_assert(
    strpos(
        $runtime,
        "const VERSION = '0.22.3';"
    ) !== false,
    'Browser version'
);
v0223_assert(
    strpos(
        $ui,
        "const VERSION = '0.22.3';"
    ) !== false,
    'Interface version'
);
v0223_assert(
    strpos(
        $rest,
        "const VERSION = '0.22.3';"
    ) !== false,
    'REST engine version'
);
v0223_assert(
    strpos(
        $runtime,
        'MutationObserver'
    ) !== false
    && strpos(
        $runtime,
        'verifyLedger'
    ) !== false
    && strpos(
        $runtime,
        'createDossier'
    ) !== false,
    'Runtime validation and provenance integration'
);
v0223_assert(
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
v0223_assert(
    strpos(
        $ui,
        'sc_lab_bioprocess_validation_provenance'
    ) !== false,
    'Focused shortcode'
);
v0223_assert(
    strpos(
        $rest,
        '/compute/bioprocess/validation/dossier'
    ) !== false,
    'Dossier REST route'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-bioprocess-validation-rest-v0223.php'
);

$consistency =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        evaluate(
            'cross-batch-consistency',
            array(
                array(
                    'batchId' => 'B-001',
                    'yield' => 82,
                    'titer' => 3.9,
                    'cycleTime' => 72,
                ),
                array(
                    'batchId' => 'B-002',
                    'yield' => 84,
                    'titer' => 4.0,
                    'cycleTime' => 70,
                ),
                array(
                    'batchId' => 'B-003',
                    'yield' => 83,
                    'titer' => 4.1,
                    'cycleTime' => 71,
                ),
            )
        );

v0223_assert(
    $consistency['decision'] === 'pass'
    && $consistency['failedCheckCount'] === 0,
    'Cross-batch consistency reference'
);

$cpp =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        evaluate(
            'cpp-conformance',
            array(
                array(
                    'parameter' => 'temperature',
                    'value' => 37,
                    'low' => 35,
                    'high' => 39,
                ),
                array(
                    'parameter' => 'pH',
                    'value' => 6.2,
                    'low' => 6.8,
                    'high' => 7.2,
                ),
            )
        );

v0223_assert(
    $cpp['decision'] === 'fail'
    && $cpp['metrics']['actionExcursionCount'] === 1,
    'CPP failure reference'
);

$first =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        create_record(
            array('status' => 'normal'),
            array(
                'recordId' => 'record-1',
                'timestamp' =>
                    '2026-07-13T20:00:00+00:00',
                'eventType' =>
                    'monitoring-analysis',
                'batchId' => 'B-001',
            )
        );

$second =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        create_record(
            $consistency,
            array(
                'recordId' => 'record-2',
                'timestamp' =>
                    '2026-07-13T20:05:00+00:00',
                'eventType' =>
                    'validation-decision',
                'batchId' => 'B-001',
            ),
            $first['recordHash']
        );

$valid =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        verify_ledger(
            array($first, $second)
        );

v0223_assert(
    $valid['valid'] === true
    && $valid['recordCount'] === 2,
    'Valid provenance chain'
);

$tampered = array($first, $second);
$tampered[1]['payload']['decision'] = 'fail';

$invalid =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        verify_ledger($tampered);

v0223_assert(
    $invalid['valid'] === false
    && $invalid['results'][1]['payloadValid']
        === false,
    'Tamper detection'
);

$dossier =
    SC_Lab_Bioprocess_Validation_REST_V0223::
        create_dossier(
            array($consistency),
            array('batchId' => 'B-001'),
            array($first, $second),
            'release'
        );

v0223_assert(
    $dossier['summary']['releaseReady']
        === true
    && strlen($dossier['dossierHash']) === 64,
    'Release dossier'
);

echo "Lab v0.22.3 PHP tests passed: "
    . "8 profiles, 5 event types, "
    . "validation, provenance, tamper detection, dossier.\n";
