<?php
$root = dirname(__DIR__);

function mb_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$main = file_get_contents($root . '/sustainable-catalyst-lab.php');
$template = file_get_contents($root . '/templates/lab-app.php');
$integration = file_get_contents(
    $root . '/includes/class-sc-lab-microbiology-laboratory.php'
);
$rest = file_get_contents(
    $root . '/includes/class-sc-lab-microbiology-laboratory-rest.php'
);
$module = file_get_contents(
    $root . '/assets/js/modules/microbiology-laboratory.js'
);
$catalog = json_decode(
    file_get_contents(
        $root . '/contracts/microbiology-laboratory-methods.json'
    ),
    true
);
$project_schema = json_decode(
    file_get_contents($root . '/contracts/project.schema.json'),
    true
);

mb_assert(
    preg_match('/Version:\s*0\.20\.0/', $main) === 1,
    'Plugin header'
);

foreach (
    array(
        'class-sc-lab-microbiology-laboratory.php',
        'class-sc-lab-microbiology-laboratory-rest.php'
    )
    as $include
) {
    mb_assert(
        strpos($main, $include) !== false,
        "Missing bootstrap include {$include}"
    );
}

mb_assert(
    strpos(
        $integration,
        'sc_lab_microbiology_laboratory'
    ) !== false,
    'Focused shortcode'
);

mb_assert(
    strpos(
        $integration,
        'microbiology-laboratory.js'
    ) !== false,
    'Browser module enqueue'
);

mb_assert(
    strpos(
        $template,
        'data-lab-module="microbiology-laboratory"'
    ) !== false,
    'Main Lab module'
);

mb_assert(
    strpos(
        $template,
        'data-microbiology-laboratory-root'
    ) !== false,
    'Main Lab mount'
);

mb_assert(
    strpos(
        $rest,
        '/compute/microbiology/methods'
    ) !== false
    && strpos(
        $rest,
        '/compute/microbiology/run'
    ) !== false,
    'WordPress REST routes'
);

mb_assert(
    strpos(
        $module,
        'MicrobiologyLaboratory'
    ) !== false
    && strpos(
        $module,
        'Microbiology or laboratory formula'
    ) !== false
    && strpos(
        $module,
        'Executable output expressions'
    ) !== false,
    'Formula-visible browser interface'
);

mb_assert(
    ($catalog['version'] ?? '') === '0.20.0',
    'Catalog version'
);

mb_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Catalog method count'
);

foreach (($catalog['methods'] ?? array()) as $method) {
    mb_assert(
        isset($method['equation'])
        && trim((string) $method['equation']) !== '',
        'Missing formula for '
            . ($method['id'] ?? 'unknown method')
    );
}

mb_assert(
    (
        $project_schema['properties']['schemaVersion']['const']
        ?? ''
    ) === '0.20.0',
    'Project schema version'
);

foreach (
    array(
        'microbiologyAnalyses',
        'microbiologyRecords',
        'microbiologyValidationRecords',
        'microbialGrowthRecords',
        'cultureKineticsRecords',
        'enumerationMicroscopyRecords',
        'environmentalMicrobiologyRecords',
        'antimicrobialScreeningRecords',
        'microbialEcologyRecords',
        'microbiologyAssayRecords',
        'microbiologyQcRecords'
    )
    as $collection
) {
    mb_assert(
        isset($project_schema['properties'][$collection]),
        "Missing project collection {$collection}"
    );
}

echo "Microbiology laboratory PHP structural tests passed.\n";
