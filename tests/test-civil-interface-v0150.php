<?php
$root = dirname(__DIR__);

function ci_repair_assert($condition, $message) {
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
    . '/includes/class-sc-lab-civil-infrastructure-interface-repair.php'
);
$module = file_get_contents(
    $root
    . '/assets/js/modules/civil-infrastructure-lab-v0150.js'
);
$catalog = json_decode(
    file_get_contents(
        $root . '/contracts/civil-infrastructure-methods.json'
    ),
    true
);

ci_repair_assert(
    strpos(
        $main,
        'class-sc-lab-civil-infrastructure-interface-repair.php'
    ) !== false,
    'Civil repair bootstrap include'
);

ci_repair_assert(
    strpos(
        $integration,
        'sc_lab_civil_infrastructure'
    ) !== false,
    'Civil focused-shortcode override'
);

ci_repair_assert(
    strpos(
        $integration,
        'civil-infrastructure-lab-v0150.js'
    ) !== false,
    'Civil repair script enqueue'
);

ci_repair_assert(
    strpos(
        $template,
        'data-civil-infrastructure-root'
    ) !== false,
    'Civil mount'
);

ci_repair_assert(
    strpos(
        $module,
        'Engineering formula'
    ) !== false
    && strpos(
        $module,
        'Executable formula expressions'
    ) !== false
    && strpos(
        $module,
        "querySelectorAll('[data-civil-infrastructure-root]')"
    ) !== false
    && strpos(
        $module,
        'autoInit'
    ) !== false,
    'Civil formula-rendering and auto-initialization markers'
);

ci_repair_assert(
    (int) ($catalog['methodCount'] ?? 0) === 48,
    'Civil catalog method count'
);

foreach (($catalog['methods'] ?? array()) as $method) {
    ci_repair_assert(
        isset($method['equation'])
        && trim((string) $method['equation']) !== '',
        'Civil formula missing for '
            . ($method['id'] ?? 'unknown method')
    );

    ci_repair_assert(
        isset($method['outputs'])
        && is_array($method['outputs'])
        && count($method['outputs']) > 0,
        'Civil output expression missing for '
            . ($method['id'] ?? 'unknown method')
    );
}

echo "Civil formula-interface repair PHP tests passed: 48 formulas.\n";
