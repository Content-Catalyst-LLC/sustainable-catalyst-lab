<?php
$root = dirname(__DIR__);

function civil_render_assert($condition, $message) {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'civil-infrastructure-runtime-v0200.js'
);

$module = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'civil-infrastructure-lab-v0150.js'
);

$clear = strpos(
    $runtime,
    'mount.replaceChildren();'
);

$reset_a = strpos(
    $runtime,
    'delete mount.dataset.scCivilRepairVersion;'
);

$reset_b = strpos(
    $runtime,
    'delete mount.dataset.scFormulaInterfaceInitialized;'
);

$init = strpos(
    $runtime,
    'module.init(document, Lab.Projects);'
);

civil_render_assert(
    $clear !== false,
    'Civil mount clear'
);

civil_render_assert(
    $reset_a !== false,
    'Civil render-marker reset'
);

civil_render_assert(
    $reset_b !== false,
    'Civil initialization-marker reset'
);

civil_render_assert(
    $init !== false,
    'Civil module initialization'
);

civil_render_assert(
    $clear < $reset_a
    && $reset_a < $init,
    'Render-marker reset order'
);

civil_render_assert(
    $clear < $reset_b
    && $reset_b < $init,
    'Initialization-marker reset order'
);

civil_render_assert(
    strpos(
        $runtime,
        "const VERSION = '0.20.0-civil-runtime.2';"
    ) !== false,
    'Civil runtime version'
);

civil_render_assert(
    strpos(
        $module,
        "mount.dataset.scCivilRepairVersion === '0.15.0'"
    ) !== false,
    'v0.15 render guard'
);

civil_render_assert(
    strpos(
        $module,
        'scFormulaInterfaceInitialized'
    ) !== false,
    'v0.15 initialization guard'
);

civil_render_assert(
    strpos(
        $module,
        'data-ci-inputs'
    ) !== false,
    'Civil calculator input workspace'
);

civil_render_assert(
    strpos(
        $module,
        'data-ci-run'
    ) !== false,
    'Civil calculator run control'
);

echo "Civil calculator-render regression tests passed.\n";
