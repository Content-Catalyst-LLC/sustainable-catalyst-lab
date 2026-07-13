<?php
$root = dirname(__DIR__);

function scr_assert($condition, $message) {
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
    . '/includes/class-sc-lab-sustainable-cities-resilience.php'
);
$rest = file_get_contents(
    $root
    . '/includes/class-sc-lab-sustainable-cities-resilience-rest.php'
);
$module = file_get_contents(
    $root
    . '/assets/js/modules/sustainable-cities-resilience-lab.js'
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/sustainable-cities-resilience-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents(
        $root . '/contracts/project.schema.json'
    ),
    true
);

scr_assert(
    preg_match(
        '/Version:\s*\d+\.\d+\.\d+/',
        $main
    ) === 1,
    'Plugin header'
);

foreach (
    array(
        'class-sc-lab-sustainable-cities-resilience.php',
        'class-sc-lab-sustainable-cities-resilience-rest.php',
        'class-sc-lab-civil-infrastructure-interface-repair.php'
    )
    as $include
) {
    scr_assert(
        strpos($main, $include) !== false,
        "Missing bootstrap include {$include}"
    );
}

scr_assert(
    strpos(
        $integration,
        'sc_lab_sustainable_cities_resilience'
    ) !== false,
    'Focused shortcode'
);

scr_assert(
    strpos(
        $integration,
        'sustainable-cities-resilience-lab.js'
    ) !== false,
    'Browser module enqueue'
);

scr_assert(
    strpos(
        $template,
        'data-lab-module="sustainable-cities-resilience"'
    ) !== false,
    'Main Lab module'
);

scr_assert(
    strpos(
        $template,
        'data-sustainable-cities-resilience-root'
    ) !== false,
    'Main Lab mount'
);

scr_assert(
    strpos(
        $rest,
        '/compute/sustainable-cities/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/sustainable-cities/run'
    ) !== false,
    'WordPress REST routes'
);

scr_assert(
    strpos(
        $module,
        'SustainableCitiesResilienceLab'
    ) !== false,
    'JavaScript export'
);

scr_assert(
    ($catalog['version'] ?? '') === '0.15.0',
    'Catalog version'
);

scr_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

scr_assert(
    isset(
        $project_schema['properties']['schemaVersion']['const']
    )
    && preg_match(
        '/^\d+\.\d+\.\d+$/',
        (string) $project_schema['properties']['schemaVersion']['const']
    ) === 1
    && version_compare(
        (string) $project_schema['properties']['schemaVersion']['const'],
        '0.15.0',
        '>='
    ),
    'Project schema version'
);

foreach (
    array(
        'sustainableCitiesResilienceAnalyses',
        'sustainableCityResilienceRecords',
        'sustainableCitiesValidationRecords',
        'urbanMetabolismRecords',
        'decarbonizationRecords',
        'climateAdaptationRecords',
        'infrastructureContinuityRecords',
        'socialResilienceRecords',
        'cityScenarioRecords'
    )
    as $collection
) {
    scr_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Sustainable cities/resilience PHP structural tests passed.\n";
