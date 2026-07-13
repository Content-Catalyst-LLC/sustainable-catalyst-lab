<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

if (!function_exists('wp_json_encode')) {
    function wp_json_encode($value, $flags = 0) {
        return json_encode($value, $flags);
    }
}

$root = dirname(__DIR__);

function v0213_assert($condition, $message) {
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
    . 'molecular-analysis-validation-provenance-v0213.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-molecular-analysis-validation-provenance-v0213.css'
);
$interface_php = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-molecular-validation-provenance-v0213.php'
);
$rest_php = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-molecular-validation-rest-v0213.php'
);
$profiles = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'molecular-analysis-validation-profiles-v0213.json'
    ),
    true
);
$visualization = json_decode(
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

v0213_assert(
    strpos(
        $runtime,
        "const VERSION = '0.21.3';"
    ) !== false,
    'Validation browser runtime version'
);

v0213_assert(
    strpos(
        $interface_php,
        "const VERSION = '0.21.3';"
    ) !== false,
    'Validation interface version'
);

v0213_assert(
    strpos(
        $rest_php,
        "const VERSION = '0.21.3';"
    ) !== false,
    'Validation REST engine version'
);

v0213_assert(
    strpos(
        $main,
        'class-sc-lab-molecular-validation-provenance-v0213.php'
    ) !== false,
    'Validation interface bootstrap'
);

v0213_assert(
    strpos(
        $main,
        'class-sc-lab-molecular-validation-rest-v0213.php'
    ) !== false,
    'Validation REST bootstrap'
);

v0213_assert(
    strpos(
        $template,
        'data-molecular-validation-provenance-root'
    ) !== false,
    'Validation and provenance mount'
);

v0213_assert(
    is_array($profiles)
    && $profiles['version'] === '0.21.3'
    && count($profiles['profiles']) === 8,
    'Eight validation profiles'
);

v0213_assert(
    is_array($visualization)
    && $visualization['version'] === '0.21.2'
    && count($visualization['presets']) === 7,
    'Preserved v0.21.2 visualization contract'
);

v0213_assert(
    is_array($catalog)
    && $catalog['version'] === '0.21.0'
    && count($catalog['methods']) === 48
    && count($catalog['benchmarks']) === 48,
    'Preserved v0.21.0 analysis contract'
);

foreach (
    array(
        'validateProfile',
        'createProvenanceRecord',
        'verifyLedger',
        'SHA-256',
        'Research-use boundary',
        'MutationObserver',
    )
    as $marker
) {
    v0213_assert(
        strpos($runtime, $marker) !== false,
        'Runtime marker: ' . $marker
    );
}

v0213_assert(
    strpos($style, '.sc-mvp-ledger-record')
        !== false
    && strpos($style, '@media (max-width: 760px)')
        !== false,
    'Provenance and mobile styles'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-molecular-validation-rest-v0213.php'
);

$precision =
    SC_Lab_Molecular_Validation_REST_V0213::
        validate(
            'precision-repeatability',
            array(
                array('value' => 100.1),
                array('value' => 99.8),
                array('value' => 100.4),
                array('value' => 100.0),
                array('value' => 99.9),
            ),
            array(
                'minimumReplicates' => 3,
                'maximumCvPercent' => 10,
            )
        );

v0213_assert(
    $precision['decision'] === 'pass'
    && $precision['metrics']['n'] === 5,
    'Precision reference validation'
);

$calibration =
    SC_Lab_Molecular_Validation_REST_V0213::
        validate(
            'calibration-linearity',
            array(
                array(
                    'concentration' => 0,
                    'signal' => 1,
                ),
                array(
                    'concentration' => 1,
                    'signal' => 3,
                ),
                array(
                    'concentration' => 2,
                    'signal' => 5,
                ),
                array(
                    'concentration' => 3,
                    'signal' => 7,
                ),
                array(
                    'concentration' => 4,
                    'signal' => 9,
                ),
            ),
            array(
                'minimumLevels' => 5,
                'minimumRSquared' => 0.99,
                'requirePositiveSlope' => 1,
            )
        );

v0213_assert(
    $calibration['decision'] === 'pass'
    && abs(
        $calibration['metrics']['slope'] - 2
    ) < 1.0e-12
    && abs(
        $calibration['metrics']['rSquared'] - 1
    ) < 1.0e-12,
    'Calibration reference validation'
);

$payload = array(
    'methodId' => 'bc.michaelis_menten',
    'validation' => $precision,
);

$first =
    SC_Lab_Molecular_Validation_REST_V0213::
        provenance_record(
            $payload,
            array(
                'recordId' => 'record-1',
                'timestamp' =>
                    '2026-07-13T18:00:00Z',
                'methodId' =>
                    'bc.michaelis_menten',
                'profileId' =>
                    'precision-repeatability',
            )
        );

$second =
    SC_Lab_Molecular_Validation_REST_V0213::
        provenance_record(
            array(
                'methodId' =>
                    'bc.michaelis_menten',
                'validation' => $calibration,
            ),
            array(
                'recordId' => 'record-2',
                'timestamp' =>
                    '2026-07-13T18:05:00Z',
                'methodId' =>
                    'bc.michaelis_menten',
                'profileId' =>
                    'calibration-linearity',
            ),
            $first['recordHash']
        );

v0213_assert(
    strlen($first['payloadHash']) === 64
    && strlen($first['recordHash']) === 64,
    'SHA-256 fingerprints'
);

$verification =
    SC_Lab_Molecular_Validation_REST_V0213::
        verify_ledger(
            array($first, $second)
        );

v0213_assert(
    $verification['valid'] === true
    && $verification['recordCount'] === 2,
    'Valid provenance chain'
);

$tampered = array($first, $second);
$tampered[0]['payload']['methodId'] =
    'tampered';

$tamper_check =
    SC_Lab_Molecular_Validation_REST_V0213::
        verify_ledger($tampered);

v0213_assert(
    $tamper_check['valid'] === false
    && $tamper_check['results'][0]['hashValid']
        === false,
    'Provenance tamper detection'
);

echo "Lab v0.21.3 PHP tests passed: "
    . count($profiles['profiles'])
    . " validation profiles, "
    . "SHA-256 ledger tamper detection.\n";
