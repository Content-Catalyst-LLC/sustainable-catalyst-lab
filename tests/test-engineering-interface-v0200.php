<?php
$root = dirname(__DIR__);

function engineering_repair_assert($condition, $message) {
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
$repair_class = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-engineering-interface-repair-v0200.php'
);
$repair_js = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'engineering-interface-repair-v0200.js'
);

engineering_repair_assert(
    strpos(
        $main,
        'class-sc-lab-engineering-interface-repair-v0200.php'
    ) !== false,
    'Repair bootstrap include'
);

foreach (
    array(
        'data-electrical-embedded-root',
        'data-mechanical-thermal-root',
        'data-civil-infrastructure-root',
        'data-module-panel="electrical-embedded"',
        'data-module-panel="mechanical-thermal"',
        'data-module-panel="civil-infrastructure"',
        'data-lab-module="electrical-embedded"',
        'data-lab-module="mechanical-thermal"',
        'data-lab-module="civil-infrastructure"'
    )
    as $marker
) {
    engineering_repair_assert(
        strpos($template, $marker) !== false,
        "Template marker {$marker}"
    );
}

engineering_repair_assert(
    strpos(
        $repair_class,
        'sc-lab-civil-infrastructure-v0150'
    ) !== false,
    'Civil repair dependency'
);

engineering_repair_assert(
    strpos($repair_js, 'Lab.ElectricalEmbedded') !== false,
    'Electrical initializer'
);

engineering_repair_assert(
    strpos($repair_js, 'Lab.MechanicalThermalLab') !== false,
    'Mechanical initializer'
);

engineering_repair_assert(
    strpos($repair_js, 'Lab.CivilInfrastructureLab') !== false,
    'Civil initializer'
);

engineering_repair_assert(
    strpos($repair_js, "minimumVersion: '0.15.0'") !== false,
    'Civil repaired-interface version guard'
);

echo "Engineering interface repair structural tests passed.\n";
