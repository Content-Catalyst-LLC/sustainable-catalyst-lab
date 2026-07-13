<?php
$root = dirname(__DIR__);

function ce_assert($condition, $message) {
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
    . '/includes/class-sc-lab-circular-economy-industrial-ecology.php'
);
$rest = file_get_contents(
    $root
    . '/includes/class-sc-lab-circular-economy-industrial-ecology-rest.php'
);
$module = file_get_contents(
    $root
    . '/assets/js/modules/circular-economy-industrial-ecology-lab.js'
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/circular-economy-industrial-ecology-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents(
        $root . '/contracts/project.schema.json'
    ),
    true
);

ce_assert(
    preg_match(
        '/Version:\s*\d+\.\d+\.\d+/',
        $main
    ) === 1,
    'Plugin header'
);

foreach (
    array(
        'class-sc-lab-circular-economy-industrial-ecology.php',
        'class-sc-lab-circular-economy-industrial-ecology-rest.php'
    )
    as $include
) {
    ce_assert(
        strpos($main, $include) !== false,
        "Missing bootstrap include {$include}"
    );
}

ce_assert(
    strpos(
        $integration,
        'sc_lab_circular_economy_industrial_ecology'
    ) !== false,
    'Focused shortcode'
);

ce_assert(
    strpos(
        $integration,
        'circular-economy-industrial-ecology-lab.js'
    ) !== false,
    'Browser module enqueue'
);

ce_assert(
    strpos(
        $template,
        'data-lab-module="circular-economy-industrial-ecology"'
    ) !== false,
    'Main Lab module'
);

ce_assert(
    strpos(
        $template,
        'data-circular-economy-industrial-ecology-root'
    ) !== false,
    'Main Lab mount'
);

ce_assert(
    strpos(
        $rest,
        '/compute/circular-economy/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/circular-economy/run'
    ) !== false,
    'WordPress REST routes'
);

ce_assert(
    strpos(
        $module,
        'CircularEconomyIndustrialEcologyLab'
    ) !== false
    && strpos(
        $module,
        'Accounting or engineering formula'
    ) !== false
    && strpos(
        $module,
        'Executable output expressions'
    ) !== false,
    'Formula-visible browser interface'
);

ce_assert(
    ($catalog['version'] ?? '') === '0.16.0',
    'Catalog version'
);

ce_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

foreach (($catalog['methods'] ?? array()) as $method) {
    ce_assert(
        isset($method['equation'])
        && trim((string) $method['equation']) !== '',
        'Missing formula for ' . ($method['id'] ?? 'unknown method')
    );
}

ce_assert(
    isset(
        $project_schema['properties']['schemaVersion']['const']
    )
    && preg_match(
        '/^\d+\.\d+\.\d+$/',
        (string) $project_schema['properties']['schemaVersion']['const']
    ) === 1
    && version_compare(
        (string) $project_schema['properties']['schemaVersion']['const'],
        '0.16.0',
        '>='
    ),
    'Project schema version'
);

foreach (
    array(
        'circularEconomyIndustrialEcologyAnalyses',
        'circularEconomyRecords',
        'industrialEcologyRecords',
        'circularityValidationRecords',
        'materialFlowRecords',
        'circularProductRecords',
        'wasteRecoveryRecords',
        'industrialSymbiosisRecords',
        'lifecycleFootprintRecords',
        'circularTransitionRecords'
    )
    as $collection
) {
    ce_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Circular economy/industrial ecology PHP structural tests passed.\n";
