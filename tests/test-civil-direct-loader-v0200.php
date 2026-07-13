<?php
$root = dirname(__DIR__);

function civil_direct_assert($condition, $message) {
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
$class = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-civil-direct-loader-v0200.php'
);
$loader = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'civil-infrastructure-direct-loader-v0200.js'
);
$template = file_get_contents(
    $root . '/templates/lab-app.php'
);

civil_direct_assert(
    strpos(
        $main,
        'class-sc-lab-civil-direct-loader-v0200.php'
    ) !== false,
    'Direct-loader bootstrap include'
);

civil_direct_assert(
    preg_match(
        '/\$modules\s*=\s*array\s*\((.*?)\)\s*;/s',
        $plugin,
        $matches
    ) === 1,
    'Central module array'
);

civil_direct_assert(
    strpos(
        $matches[1],
        "'civil-infrastructure-lab'"
    ) !== false,
    'Legacy Civil module key retained for compatibility'
);

civil_direct_assert(
    strpos(
        $plugin,
        'SC_LAB_CIVIL_DIRECT_LOADER_SKIP'
    ) !== false
    && strpos(
        $plugin,
        "if (\$module === 'civil-infrastructure-lab')"
    ) !== false,
    'Original Civil implementation skipped during enqueue'
);

civil_direct_assert(
    strpos(
        $class,
        'civil-infrastructure-direct-loader-v0200.js'
    ) !== false,
    'Direct loader enqueue'
);

civil_direct_assert(
    strpos(
        $loader,
        'civil-infrastructure-lab-v0150.js'
    ) !== false,
    'Authoritative Civil source'
);

civil_direct_assert(
    strpos(
        $loader,
        "mount.replaceChildren()"
    ) !== false,
    'Civil mount reset'
);

civil_direct_assert(
    strpos(
        $loader,
        "minimumVersion = '0.15.0'"
    ) !== false,
    'Repaired Civil minimum version'
);

civil_direct_assert(
    strpos(
        $template,
        'data-civil-infrastructure-root'
    ) !== false,
    'Civil mount'
);

echo "Civil direct-loader structural tests passed.\n";
