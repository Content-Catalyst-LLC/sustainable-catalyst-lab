<?php
$root = dirname(__DIR__);

function rp_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$main = file_get_contents($root . '/sustainable-catalyst-lab.php');
$template = file_get_contents($root . '/templates/lab-app.php');
$integration = file_get_contents(
    $root . '/includes/class-sc-lab-rocket-propulsion-spaceflight.php'
);
$rest = file_get_contents(
    $root . '/includes/class-sc-lab-rocket-propulsion-spaceflight-rest.php'
);
$module = file_get_contents(
    $root . '/assets/js/modules/rocket-propulsion-spaceflight-lab.js'
);
$catalog = json_decode(
    file_get_contents(
        $root . '/contracts/rocket-propulsion-spaceflight-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents($root . '/contracts/project.schema.json'),
    true
);

rp_assert(
    preg_match(
        '/Version:\s*\d+\.\d+\.\d+/',
        $main
    ) === 1,
    'Plugin header'
);

foreach (
    array(
        'class-sc-lab-rocket-propulsion-spaceflight.php',
        'class-sc-lab-rocket-propulsion-spaceflight-rest.php'
    )
    as $include
) {
    rp_assert(
        strpos($main, $include) !== false,
        "Missing bootstrap include {$include}"
    );
}

rp_assert(
    strpos(
        $integration,
        'sc_lab_rocket_propulsion_spaceflight'
    ) !== false,
    'Focused shortcode'
);

rp_assert(
    strpos(
        $integration,
        'rocket-propulsion-spaceflight-lab.js'
    ) !== false,
    'Browser module enqueue'
);

rp_assert(
    strpos(
        $template,
        'data-lab-module="rocket-propulsion-spaceflight"'
    ) !== false,
    'Main Lab module'
);

rp_assert(
    strpos(
        $template,
        'data-rocket-propulsion-spaceflight-root'
    ) !== false,
    'Main Lab mount'
);

rp_assert(
    strpos(
        $rest,
        '/compute/rocket-spaceflight/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/rocket-spaceflight/run'
    ) !== false,
    'WordPress REST routes'
);

rp_assert(
    strpos(
        $module,
        'RocketPropulsionSpaceflightLab'
    ) !== false
    && strpos(
        $module,
        'Rocket-propulsion or spaceflight formula'
    ) !== false
    && strpos(
        $module,
        'Executable output expressions'
    ) !== false,
    'Formula-visible browser interface'
);

rp_assert(
    ($catalog['version'] ?? '') === '0.19.0',
    'Catalog version'
);

rp_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

foreach (($catalog['methods'] ?? array()) as $method) {
    rp_assert(
        isset($method['equation'])
        && trim((string) $method['equation']) !== '',
        'Missing formula for '
            . ($method['id'] ?? 'unknown method')
    );
}

rp_assert(
    isset(
        $project_schema['properties']['schemaVersion']['const']
    )
    && preg_match(
        '/^\d+\.\d+\.\d+$/',
        (string) $project_schema['properties']['schemaVersion']['const']
    ) === 1
    && version_compare(
        (string) $project_schema['properties']['schemaVersion']['const'],
        '0.19.0',
        '>='
    ),
    'Project schema version'
);

foreach (
    array(
        'rocketPropulsionSpaceflightAnalyses',
        'spaceflightSystemsRecords',
        'rocketSpaceflightValidationRecords',
        'propulsionFundamentalsRecords',
        'nozzleEngineRecords',
        'launchVehicleStagingRecords',
        'ascentDynamicsRecords',
        'orbitalMechanicsRecords',
        'spacecraftMissionRecords',
        'spaceflightReliabilityRecords',
        'missionDeltaVRecords'
    )
    as $collection
) {
    rp_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Rocket propulsion/spaceflight PHP structural tests passed.\n";
