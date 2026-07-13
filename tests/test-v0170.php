<?php
$root = dirname(__DIR__);

function de_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$main = file_get_contents($root . '/sustainable-catalyst-lab.php');
$template = file_get_contents($root . '/templates/lab-app.php');
$integration = file_get_contents($root . '/includes/class-sc-lab-comparative-economics-development-systems.php');
$rest = file_get_contents($root . '/includes/class-sc-lab-comparative-economics-development-systems-rest.php');
$module = file_get_contents($root . '/assets/js/modules/comparative-economics-development-systems-lab.js');
$catalog = json_decode(file_get_contents($root . '/contracts/comparative-economics-development-systems-methods.json'), true);
$project_schema = json_decode(file_get_contents($root . '/contracts/project.schema.json'), true);

de_assert(
    preg_match(
        '/Version:\s*\d+\.\d+\.\d+/',
        $main
    ) === 1,
    'Plugin header'
);
foreach (array('class-sc-lab-comparative-economics-development-systems.php','class-sc-lab-comparative-economics-development-systems-rest.php') as $include) {
    de_assert(strpos($main, $include) !== false, "Missing bootstrap include {$include}");
}
de_assert(strpos($integration, 'sc_lab_comparative_economics_development_systems') !== false, 'Focused shortcode');
de_assert(strpos($integration, 'comparative-economics-development-systems-lab.js') !== false, 'Browser module enqueue');
de_assert(strpos($template, 'data-lab-module="comparative-economics-development-systems"') !== false, 'Main Lab module');
de_assert(strpos($template, 'data-comparative-economics-development-systems-root') !== false, 'Main Lab mount');
de_assert(strpos($rest, '/compute/development-economics/methods') !== false && strpos($rest, '/compute/development-economics/run') !== false, 'WordPress REST routes');
de_assert(strpos($module, 'ComparativeEconomicsDevelopmentSystemsLab') !== false && strpos($module, 'Economic or development-systems formula') !== false && strpos($module, 'Executable output expressions') !== false, 'Formula-visible browser interface');
de_assert(($catalog['version'] ?? '') === '0.17.0', 'Catalog version');
de_assert((int) ($catalog['methodCount'] ?? 0) === 48, 'Catalog method count');
foreach (($catalog['methods'] ?? array()) as $method) {
    de_assert(isset($method['equation']) && trim((string) $method['equation']) !== '', 'Missing formula for ' . ($method['id'] ?? 'unknown method'));
}
de_assert(
    isset(
        $project_schema['properties']['schemaVersion']['const']
    )
    && preg_match(
        '/^\d+\.\d+\.\d+$/',
        (string) $project_schema['properties']['schemaVersion']['const']
    ) === 1
    && version_compare(
        (string) $project_schema['properties']['schemaVersion']['const'],
        '0.17.0',
        '>='
    ),
    'Project schema version'
);
foreach (array('comparativeEconomicsDevelopmentAnalyses','developmentEconomicsRecords','developmentSystemsValidationRecords','nationalAccountsRecords','growthProductivityRecords','tradeTransformationRecords','laborInequalityRecords','humanDevelopmentRecords','publicFinanceRecords','developmentFinanceRecords','developmentScenarioRecords') as $collection) {
    de_assert(isset($project_schema['properties'][$collection]), "Missing project collection {$collection}");
}
echo "Comparative economics/development systems PHP structural tests passed.\n";
