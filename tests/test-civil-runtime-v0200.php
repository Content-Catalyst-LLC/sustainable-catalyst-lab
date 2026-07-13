<?php
$root = dirname(__DIR__);

function civil_runtime_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$main = file_get_contents(
    $root . '/sustainable-catalyst-lab.php'
);
$plugin = file_get_contents(
    $root . '/includes/class-sc-lab-plugin.php'
);
$engineering = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'engineering-interface-repair-v0200.js'
);
$runtime_class = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-civil-runtime-v0200.php'
);
$runtime_js = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'civil-infrastructure-runtime-v0200.js'
);
$template = file_get_contents(
    $root . '/templates/lab-app.php'
);

civil_runtime_assert(
    strpos(
        $main,
        'class-sc-lab-civil-runtime-v0200.php'
    ) !== false,
    'Civil runtime bootstrap include'
);

civil_runtime_assert(
    strpos(
        $main,
        'class-sc-lab-civil-interface-authority-v0200.php'
    ) === false,
    'Old Civil authority bootstrap disabled'
);

civil_runtime_assert(
    strpos(
        $main,
        'class-sc-lab-civil-direct-loader-v0200.php'
    ) === false,
    'Old Civil direct-loader bootstrap disabled'
);

civil_runtime_assert(
    strpos(
        $plugin,
        "'civil-infrastructure-lab'"
    ) !== false,
    'Legacy Civil key retained'
);

civil_runtime_assert(
    strpos(
        $plugin,
        'SC_LAB_CIVIL_RUNTIME_SKIP_LEGACY'
    ) !== false,
    'Legacy Civil enqueue skipped'
);

civil_runtime_assert(
    strpos(
        $engineering,
        "name: 'civil-infrastructure'"
    ) === false,
    'Civil removed from general engineering initializer'
);

civil_runtime_assert(
    strpos(
        $runtime_class,
        'civil-infrastructure-lab-v0150.js'
    ) !== false,
    'Authoritative Civil module enqueue'
);

civil_runtime_assert(
    strpos(
        $runtime_class,
        'civil-infrastructure-runtime-v0200.js'
    ) !== false,
    'Authoritative Civil bootstrap enqueue'
);

civil_runtime_assert(
    strpos(
        $runtime_class,
        'remove_competing_scripts'
    ) !== false,
    'Competing Civil scripts removed'
);

civil_runtime_assert(
    strpos(
        $runtime_js,
        'MutationObserver'
    ) !== false,
    'Late-render observer'
);

civil_runtime_assert(
    strpos(
        $runtime_js,
        'Lab.CivilRuntime'
    ) !== false,
    'Civil runtime diagnostics'
);

civil_runtime_assert(
    strpos(
        $template,
        'data-civil-infrastructure-root'
    ) !== false,
    'Civil mount'
);

echo "Civil consolidated runtime structural tests passed.\n";
