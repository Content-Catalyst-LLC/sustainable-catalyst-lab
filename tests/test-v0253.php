<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

if (!function_exists('add_shortcode')) {
    function add_shortcode() {}
}

if (!function_exists('wp_json_encode')) {
    function wp_json_encode($value, $flags = 0) {
        return json_encode($value, $flags);
    }
}

$root = dirname(__DIR__);

function v0253_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

function v0253_equal($actual, $expected) {
    if (
        is_float($actual)
        || is_float($expected)
    ) {
        return abs(
            (float) $actual
            - (float) $expected
        ) <= max(
            1.0e-10,
            abs((float) $expected) * 1.0e-9
        );
    }

    if (
        is_array($actual)
        && is_array($expected)
    ) {
        if (
            array_keys($actual)
            !== array_keys($expected)
        ) {
            return false;
        }

        foreach ($actual as $key => $value) {
            if (
                !v0253_equal(
                    $value,
                    $expected[$key]
                )
            ) {
                return false;
            }
        }

        return true;
    }

    return $actual === $expected;
}

$contract = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'instrumentation-validation-custody-v0253.json'
    ),
    true
);
$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'instrumentation-validation-custody-v0253.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-instrumentation-validation-custody-v0253.css'
);
$interface = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-instrumentation-validation-custody-v0253.php'
);
$rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-instrumentation-validation-rest-v0253.php'
);

v0253_assert(
    $contract['version'] === '0.25.3',
    'Contract version'
);
v0253_assert(
    count($contract['validationProfiles']) === 8
    && count($contract['acceptanceStates']) === 8
    && count($contract['provenanceEventTypes']) === 8
    && count($contract['deviationTypes']) === 8,
    'Validation contract counts'
);
v0253_assert(
    count($contract['analysisMethods']) === 16
    && count($contract['benchmarks']) === 16,
    'Method and benchmark counts'
);
v0253_assert(
    $contract['preservedInstrumentation']['methodCount']
        === 48
    && $contract['preservedInstrumentation']['benchmarkCount']
        === 48
    && $contract['liveLayer']['modeCount']
        === 8
    && $contract['liveLayer']['analysisMethodCount']
        === 16,
    'Preserved instrumentation stack'
);
v0253_assert(
    strpos(
        $runtime,
        'createManifest'
    ) !== false
    && strpos(
        $runtime,
        'createCustodyEvent'
    ) !== false
    && strpos(
        $runtime,
        'verifyCustodyChain'
    ) !== false
    && strpos(
        $runtime,
        'createDossier'
    ) !== false,
    'Browser provenance workflow'
);
v0253_assert(
    strpos(
        $interface,
        'sc_lab_instrumentation_validation_custody'
    ) !== false,
    'Focused shortcode'
);
v0253_assert(
    strpos(
        $rest,
        '/compute/instrumentation/validation/dossier'
    ) !== false
    && strpos(
        $rest,
        '/compute/instrumentation/custody/verify'
    ) !== false,
    'REST routes'
);
v0253_assert(
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
        'white-space: pre-wrap'
    ) !== false,
    'Mobile validation styles'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-instrumentation-validation-rest-v0253.php'
);

foreach ($contract['benchmarks'] as $benchmark) {
    $result =
        SC_Lab_Instrumentation_Validation_REST_V0253::
            execute(
                $benchmark['methodId'],
                $benchmark['inputs']
            );

    v0253_assert(
        v0253_equal(
            $result['value'],
            $benchmark['expected']
        ),
        'Benchmark: '
        . $benchmark['methodId']
    );
}

$manifest =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        create_manifest(
            array(
                'instrument' => array(
                    'id' => 'INST-1',
                    'model' => 'SC-100',
                ),
                'calibration' => array(
                    'status' => 'accepted',
                ),
            ),
            array(
                'projectId' => 'PROJECT-1',
            )
        );

v0253_assert(
    strlen($manifest['manifestHash']) === 64
    && count(
        $manifest['componentHashes']
    ) === 2,
    'SHA-256 component manifest'
);

$first =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        create_custody_event(
            'SAMPLE-1',
            'received',
            'analyst-a',
            'intake',
            1
        );
$second =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        create_custody_event(
            'SAMPLE-1',
            'transferred',
            'analyst-b',
            'lab',
            2,
            $first['eventHash']
        );

$valid =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        verify_custody_chain(
            array($first, $second)
        );

v0253_assert(
    $valid['valid'] === true,
    'Valid custody chain'
);

$tampered = $second;
$tampered['location'] = 'unknown';

$invalid =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        verify_custody_chain(
            array($first, $tampered)
        );

v0253_assert(
    $invalid['valid'] === false
    && in_array(
        'event-2-hash',
        $invalid['problems'],
        true
    ),
    'Custody tamper detection'
);

$dossier =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        create_dossier(
            array(
                'instrument-identity' => array(
                    'score' => 100,
                ),
                'calibration-acceptance' => array(
                    'score' => 95,
                ),
                'measurement-quality' => array(
                    'score' => 92,
                ),
                'custody-chain-integrity' => array(
                    'score' => 100,
                ),
            ),
            $manifest,
            array($first, $second),
            array(
                array(
                    'type' =>
                        'review-incomplete',
                    'closed' => false,
                ),
            ),
            array(
                'reviewer' => 'QA',
            )
        );

v0253_assert(
    $dossier['disposition']
        === 'conditionally-accepted'
    && strlen(
        $dossier['dossierHash']
    ) === 64,
    'Validation dossier'
);

$health =
    SC_Lab_Instrumentation_Validation_REST_V0253::
        health_payload();

v0253_assert(
    $health['ok'] === true
    && $health['release'] === '0.25.3'
    && $health['validationProfileCount'] === 8
    && $health['acceptanceStateCount'] === 8
    && $health['eventTypeCount'] === 8
    && $health['deviationTypeCount'] === 8
    && $health['analysisMethodCount'] === 16
    && $health['benchmarkCount'] === 16,
    'Health contract'
);

v0253_assert(
    $health['boundaries']['gmpCertification']
        === false
    && $health['boundaries']['clinicalReleaseAuthority']
        === false
    && $health['boundaries']['tamperEvidence']
        === true,
    'Responsible-use boundaries'
);

echo "Lab v0.25.3 PHP tests passed: "
    . "8 profiles/states/events/deviations, "
    . "16 methods/benchmarks, SHA-256 manifest, "
    . "custody tamper detection, dossier.\n";
