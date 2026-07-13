<?php
$root = dirname(__DIR__);

function af_assert($condition, $message) {
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
$integration = file_get_contents(
    $root
    . '/includes/class-sc-lab-aerospace-engineering-flight-systems.php'
);
$rest = file_get_contents(
    $root
    . '/includes/class-sc-lab-aerospace-engineering-flight-systems-rest.php'
);
$module = file_get_contents(
    $root
    . '/assets/js/modules/aerospace-engineering-flight-systems-lab.js'
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/aerospace-engineering-flight-systems-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents(
        $root . '/contracts/project.schema.json'
    ),
    true
);

af_assert(
    preg_match('/Version:\s*0\.18\.0/', $main) === 1,
    'Plugin header'
);

foreach (
    array(
        'class-sc-lab-aerospace-engineering-flight-systems.php',
        'class-sc-lab-aerospace-engineering-flight-systems-rest.php'
    )
    as $include
) {
    af_assert(
        strpos($main, $include) !== false,
        "Missing bootstrap include {$include}"
    );
}

af_assert(
    strpos(
        $integration,
        'sc_lab_aerospace_engineering_flight_systems'
    ) !== false,
    'Focused shortcode'
);

af_assert(
    strpos(
        $integration,
        'aerospace-engineering-flight-systems-lab.js'
    ) !== false,
    'Browser module enqueue'
);

af_assert(
    strpos(
        $template,
        'data-lab-module="aerospace-engineering-flight-systems"'
    ) !== false,
    'Main Lab module'
);

af_assert(
    strpos(
        $template,
        'data-aerospace-engineering-flight-systems-root'
    ) !== false,
    'Main Lab mount'
);

af_assert(
    strpos(
        $rest,
        '/compute/aerospace-flight/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/aerospace-flight/run'
    ) !== false,
    'WordPress REST routes'
);

af_assert(
    strpos(
        $module,
        'AerospaceEngineeringFlightSystemsLab'
    ) !== false
    && strpos(
        $module,
        'Aeronautical or flight-systems formula'
    ) !== false
    && strpos(
        $module,
        'Executable output expressions'
    ) !== false,
    'Formula-visible browser interface'
);

af_assert(
    ($catalog['version'] ?? '') === '0.18.0',
    'Catalog version'
);

af_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

foreach (($catalog['methods'] ?? array()) as $method) {
    af_assert(
        isset($method['equation'])
        && trim((string) $method['equation']) !== '',
        'Missing formula for '
            . ($method['id'] ?? 'unknown method')
    );
}

af_assert(
    (
        $project_schema['properties']['schemaVersion']['const']
        ?? ''
    ) === '0.18.0',
    'Project schema version'
);

foreach (
    array(
        'aerospaceEngineeringFlightAnalyses',
        'aerospaceFlightSystemsRecords',
        'aerospaceFlightValidationRecords',
        'aerodynamicsRecords',
        'flightPerformanceRecords',
        'flightControlsRecords',
        'propulsionEnergyRecords',
        'aerospaceStructuresRecords',
        'navigationMissionRecords',
        'flightSystemsReliabilityRecords',
        'flightMissionRecords'
    )
    as $collection
) {
    af_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Aerospace engineering/flight systems PHP structural tests passed.\n";
