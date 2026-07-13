<?php
$root = dirname(__DIR__);

function ab_assert($condition, $message) {
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
    $root . '/includes/class-sc-lab-architecture-building.php'
);
$rest = file_get_contents(
    $root . '/includes/class-sc-lab-architecture-building-rest.php'
);
$module = file_get_contents(
    $root . '/assets/js/modules/architecture-building-lab.js'
);
$catalog = json_decode(
    file_get_contents(
        $root . '/contracts/architecture-building-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents(
        $root . '/contracts/project.schema.json'
    ),
    true
);

ab_assert(
    preg_match(
        '/Version:\s*\d+\.\d+\.\d+/',
        $main
    ) === 1,
    'Plugin header'
);

ab_assert(
    strpos(
        $main,
        'class-sc-lab-architecture-building.php'
    ) !== false,
    'Architecture integration include'
);

ab_assert(
    strpos(
        $main,
        'class-sc-lab-architecture-building-rest.php'
    ) !== false,
    'Architecture REST include'
);

ab_assert(
    strpos(
        $integration,
        'sc_lab_architecture_building'
    ) !== false,
    'Focused shortcode'
);

ab_assert(
    strpos(
        $integration,
        'architecture-building-lab.js'
    ) !== false,
    'Browser module enqueue'
);

ab_assert(
    strpos(
        $integration,
        'sc-lab-v0130.css'
    ) !== false,
    'Stylesheet enqueue'
);

ab_assert(
    strpos(
        $template,
        'data-lab-module="architecture-building"'
    ) !== false,
    'Main Lab module'
);

ab_assert(
    strpos(
        $template,
        'data-architecture-building-root'
    ) !== false,
    'Architecture mount'
);

ab_assert(
    strpos(
        $rest,
        '/compute/architecture/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/architecture/run'
    ) !== false,
    'WordPress REST routes'
);

ab_assert(
    strpos(
        $module,
        'ArchitectureBuildingLab'
    ) !== false,
    'JavaScript export'
);

ab_assert(
    ($catalog['version'] ?? '') === '0.13.0',
    'Catalog version'
);

ab_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

ab_assert(
    isset(
        $project_schema['properties']['schemaVersion']['const']
    )
    && preg_match(
        '/^\d+\.\d+\.\d+$/',
        (string) $project_schema['properties']['schemaVersion']['const']
    ) === 1
    && version_compare(
        (string) $project_schema['properties']['schemaVersion']['const'],
        '0.13.0',
        '>='
    ),
    'Project schema version'
);

foreach (
    array(
        'architectureBuildingAnalyses',
        'buildingPerformanceRecords',
        'buildingPerformanceValidationRecords',
        'buildingEnvelopeRecords',
        'daylightRecords',
        'indoorEnvironmentalQualityRecords',
        'buildingEnergyRecords',
    )
    as $collection
) {
    ab_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Architecture/building PHP structural tests passed.\n";
