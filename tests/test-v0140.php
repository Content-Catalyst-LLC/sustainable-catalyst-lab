<?php
$root = dirname(__DIR__);

function up_assert($condition, $message) {
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
    $root . '/includes/class-sc-lab-urban-planning-spatial.php'
);
$rest = file_get_contents(
    $root . '/includes/class-sc-lab-urban-planning-spatial-rest.php'
);
$module = file_get_contents(
    $root . '/assets/js/modules/urban-planning-spatial-lab.js'
);
$catalog = json_decode(
    file_get_contents(
        $root . '/contracts/urban-planning-spatial-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents(
        $root . '/contracts/project.schema.json'
    ),
    true
);

up_assert(
    preg_match(
        '/Version:\s*\d+\.\d+\.\d+/',
        $main
    ) === 1,
    'Plugin header'
);

up_assert(
    strpos(
        $main,
        'class-sc-lab-urban-planning-spatial.php'
    ) !== false,
    'Urban planning integration include'
);

up_assert(
    strpos(
        $main,
        'class-sc-lab-urban-planning-spatial-rest.php'
    ) !== false,
    'Urban planning REST include'
);

up_assert(
    strpos(
        $integration,
        'sc_lab_urban_planning_spatial'
    ) !== false,
    'Focused shortcode'
);

up_assert(
    strpos(
        $integration,
        'urban-planning-spatial-lab.js'
    ) !== false,
    'Browser module enqueue'
);

up_assert(
    strpos(
        $integration,
        'sc-lab-v0140.css'
    ) !== false,
    'Stylesheet enqueue'
);

up_assert(
    strpos(
        $template,
        'data-lab-module="urban-planning-spatial"'
    ) !== false,
    'Main Lab module'
);

up_assert(
    strpos(
        $template,
        'data-urban-planning-spatial-root'
    ) !== false,
    'Urban planning mount'
);

up_assert(
    strpos(
        $rest,
        '/compute/urban-planning/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/urban-planning/run'
    ) !== false,
    'WordPress REST routes'
);

up_assert(
    strpos(
        $module,
        'UrbanPlanningSpatialLab'
    ) !== false,
    'JavaScript export'
);

up_assert(
    ($catalog['version'] ?? '') === '0.14.0',
    'Catalog version'
);

up_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

up_assert(
    isset(
        $project_schema['properties']['schemaVersion']['const']
    )
    && preg_match(
        '/^\d+\.\d+\.\d+$/',
        (string) $project_schema['properties']['schemaVersion']['const']
    ) === 1
    && version_compare(
        (string) $project_schema['properties']['schemaVersion']['const'],
        '0.14.0',
        '>='
    ),
    'Project schema version'
);

foreach (
    array(
        'urbanPlanningSpatialAnalyses',
        'urbanSpatialRecords',
        'urbanPlanningValidationRecords',
        'landUseRecords',
        'accessibilityRecords',
        'mobilityRecords',
        'spatialNetworkRecords',
        'gisAnalysisRecords',
        'publicServiceRecords',
        'urbanResilienceRecords',
        'spatialScenarioRecords'
    )
    as $collection
) {
    up_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Urban planning/spatial PHP structural tests passed.\n";
