<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

if (!function_exists('add_shortcode')) {
    function add_shortcode() {}
}

$root = dirname(__DIR__);

function v0252_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$contract = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'instrumentation-live-visualization-v0252.json'
    ),
    true
);
$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'instrumentation-live-visualization-v0252.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-instrumentation-live-visualization-v0252.css'
);
$interface = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-instrumentation-live-visualization-v0252.php'
);
$rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-instrumentation-live-rest-v0252.php'
);

v0252_assert(
    $contract['version'] === '0.25.2',
    'Contract version'
);
v0252_assert(
    count($contract['modes']) === 8
    && count($contract['analysisMethods']) === 16
    && count($contract['benchmarks']) === 16,
    'Visualization and analysis counts'
);
v0252_assert(
    count($contract['channelTemplates']) === 8
    && count($contract['connectionStates']) === 8
    && count($contract['eventTypes']) === 8,
    'Channel, connection, and event counts'
);
v0252_assert(
    $contract['preservedEngine']['methodCount'] === 48
    && $contract['preservedEngine']['benchmarkCount'] === 48
    && $contract['preservedEngine']['categoryCount'] === 8
    && $contract['preservedEngine']['recordTypeCount'] === 9
    && $contract['preservedEngine']['connectionProfileCount'] === 8
    && $contract['preservedEngine']['qualityFlagCount'] === 8,
    'Preserved v0.25.0 instrumentation contract'
);
v0252_assert(
    strpos(
        $runtime,
        "const VERSION = '0.25.2';"
    ) !== false
    && strpos(
        $runtime,
        'class StreamBuffer'
    ) !== false
    && strpos(
        $runtime,
        'startDemo'
    ) !== false
    && strpos(
        $runtime,
        'replay'
    ) !== false
    && strpos(
        $runtime,
        'MutationObserver'
    ) !== false,
    'Browser live workflow'
);
v0252_assert(
    strpos(
        $interface,
        'sc_lab_live_sensor_instrument_visualization'
    ) !== false,
    'Focused shortcode'
);
v0252_assert(
    strpos(
        $rest,
        '/compute/instrumentation/live/snapshot'
    ) !== false
    && strpos(
        $rest,
        '/compute/instrumentation/live/replay'
    ) !== false,
    'WordPress live routes'
);
v0252_assert(
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
        'min-width: 680px'
    ) !== false,
    'Mobile chart fallback'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-instrumentation-live-rest-v0252.php'
);

foreach ($contract['benchmarks'] as $benchmark) {
    $result =
        SC_Lab_Instrumentation_Live_REST_V0252::
            execute(
                $benchmark['methodId'],
                $benchmark['inputs']
            );

    v0252_assert(
        $result['value'] == $benchmark['expected'],
        'Benchmark: ' . $benchmark['methodId']
    );
}

$snapshot =
    SC_Lab_Instrumentation_Live_REST_V0252::
        build_snapshot(
            array(
                array(
                    'timestamp' => 1,
                    'channel' => 'temperature',
                    'value' => 20,
                ),
                array(
                    'timestamp' => 2,
                    'channel' => 'temperature',
                    'value' => 26,
                ),
                array(
                    'timestamp' => 9,
                    'channel' => 'temperature',
                    'value' => 21,
                ),
            ),
            array(
                'temperature' => array(
                    'warningLow' => 10,
                    'warningHigh' => 20,
                    'actionLow' => 5,
                    'actionHigh' => 25,
                ),
            ),
            3,
            'online'
        );

$types = array_unique(
    array_column(
        $snapshot['events'],
        'type'
    )
);
sort($types);

v0252_assert(
    $snapshot['summary']['channelCount'] === 1
    && $types === array(
        'action',
        'gap',
        'warning',
    ),
    'Snapshot threshold and gap events'
);

$health =
    SC_Lab_Instrumentation_Live_REST_V0252::
        health_payload();

v0252_assert(
    $health['ok'] === true
    && $health['release'] === '0.25.2'
    && $health['modeCount'] === 8
    && $health['analysisMethodCount'] === 16
    && $health['benchmarkCount'] === 16
    && $health['channelTemplateCount'] === 8
    && $health['connectionStateCount'] === 8
    && $health['eventTypeCount'] === 8,
    'Health contract'
);
v0252_assert(
    $health['boundaries']['automaticLocalDeviceAccess']
        === false
    && $health['boundaries']['clinicalMonitoring']
        === false
    && $health['boundaries']['alarmAuthority']
        === false
    && $health['boundaries']['regulatedControl']
        === false
    && $health['boundaries']['localFirstReplay']
        === true,
    'Responsible-use boundaries'
);

echo "Lab v0.25.2 PHP tests passed: "
    . "8 modes, 16 methods/benchmarks, "
    . "8 channels/states/events, snapshots and boundaries.\n";
