<?php
define('ABSPATH', __DIR__);

if (!function_exists('add_action')) {
    function add_action() {}
}

$root = dirname(__DIR__);

function v0210_fail($message) {
    fwrite(STDERR, "FAIL: {$message}\n");
    exit(1);
}

function v0210_assert($condition, $message) {
    if (!$condition) {
        v0210_fail($message);
    }
}

$main = file_get_contents(
    $root . '/sustainable-catalyst-lab.php'
);
$template = file_get_contents(
    $root . '/templates/lab-app.php'
);
$analysis_js = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'biochemistry-molecular-analysis.js'
);
$analysis_rest = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biochemistry-molecular-analysis-rest.php'
);
$catalog = json_decode(
    file_get_contents(
        $root
        . '/contracts/'
        . 'biochemistry-molecular-analysis-methods.json'
    ),
    true
);

v0210_assert(
    isset($catalog['version'])
    && $catalog['version'] === '0.21.0',
    'Biochemistry catalog version'
);

v0210_assert(
    strpos(
        $analysis_js,
        "const VERSION = '0.21.0';"
    ) !== false,
    'Biochemistry browser engine version'
);

v0210_assert(
    strpos(
        $analysis_rest,
        "const VERSION = '0.21.0';"
    ) !== false,
    'Biochemistry PHP engine version'
);

v0210_assert(
    strpos(
        $main,
        'class-sc-lab-biochemistry-molecular-analysis.php'
    ) !== false,
    'Biochemistry interface bootstrap'
);

v0210_assert(
    strpos(
        $main,
        'class-sc-lab-biochemistry-molecular-analysis-rest.php'
    ) !== false,
    'Biochemistry REST bootstrap'
);

v0210_assert(
    is_array($catalog),
    'Biochemistry catalog JSON'
);

v0210_assert(
    count($catalog['methods']) === 48,
    '48 biochemistry methods'
);

v0210_assert(
    count($catalog['benchmarks']) === 48,
    '48 deterministic benchmarks'
);

v0210_assert(
    strpos(
        $template,
        "'biochemistry-molecular-analysis'"
    ) !== false,
    'Biochemistry navigation item'
);

v0210_assert(
    strpos(
        $template,
        'data-lab-module="biochemistry-molecular-analysis"'
    ) !== false,
    'Biochemistry panel route'
);

v0210_assert(
    strpos(
        $template,
        'data-biochemistry-molecular-analysis-root'
    ) !== false,
    'Biochemistry calculator mount'
);

require_once(
    $root
    . '/includes/'
    . 'class-sc-lab-biochemistry-molecular-analysis-rest.php'
);

$result =
    SC_Lab_Biochemistry_Molecular_Analysis_REST::calculate(
        'bc.michaelis_menten',
        array(
            'vmax' => 100,
            'substrate' => 2,
            'km' => 0.5,
        )
    );

v0210_assert(
    abs($result['outputs']['velocity'] - 80.0) < 1.0e-10,
    'PHP Michaelis-Menten calculation'
);

$dna =
    SC_Lab_Biochemistry_Molecular_Analysis_REST::calculate(
        'bc.dsdna_a260_concentration',
        array(
            'absorbance260' => 0.2,
            'dilutionFactor' => 10,
        )
    );

v0210_assert(
    abs(
        $dna['outputs']['dnaConcentrationUgMl']
        - 100.0
    ) < 1.0e-10,
    'PHP DNA concentration calculation'
);

foreach ($catalog['benchmarks'] as $benchmark) {
    $calculated =
        SC_Lab_Biochemistry_Molecular_Analysis_REST::calculate(
            $benchmark['methodId'],
            $benchmark['inputs']
        );

    foreach (
        $benchmark['expected']
        as $key => $expected
    ) {
        $actual = $calculated['outputs'][$key];
        $difference = abs($actual - $expected);
        $scale = max(
            abs($actual),
            abs($expected),
            1.0
        );

        $passed =
            $difference
                <= $benchmark['absoluteTolerance']
            || $difference
                <= $benchmark['relativeTolerance']
                    * $scale;

        v0210_assert(
            $passed,
            'PHP benchmark ' . $benchmark['id']
        );
    }
}

echo "Lab v0.21.0 PHP tests passed: 48 methods.\n";
