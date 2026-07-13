<?php
$root = dirname(__DIR__);

function v0211_assert($condition, $message) {
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
$production = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-biochemistry-production-v0211.php'
);
$runtime = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'biochemistry-production-v0211.js'
);
$style = file_get_contents(
    $root
    . '/assets/css/'
    . 'sc-lab-biochemistry-production-v0211.css'
);
$current_suite = file_get_contents(
    $root
    . '/scripts/'
    . 'test_release_current.sh'
);

v0211_assert(
    strpos(
        $production,
        "const VERSION = '0.21.1';"
    ) !== false,
    'Production PHP layer version'
);

v0211_assert(
    strpos(
        $runtime,
        "const VERSION = '0.21.1';"
    ) !== false,
    'Production browser runtime version'
);

v0211_assert(
    strpos(
        $main,
        'class-sc-lab-biochemistry-production-v0211.php'
    ) !== false,
    'Production bootstrap include'
);

v0211_assert(
    strpos(
        $template,
        "'biochemistry-molecular-analysis'"
    ) !== false,
    'Navigation route'
);

v0211_assert(
    strpos(
        $template,
        'data-lab-module="biochemistry-molecular-analysis"'
    ) !== false,
    'Canonical panel route'
);

v0211_assert(
    strpos(
        $template,
        'data-biochemistry-molecular-analysis-root'
    ) !== false,
    'Calculator mount'
);

foreach (
    array(
        'wp_enqueue_scripts',
        '50000',
        'wp_localize_script',
        '/compute/biochemistry/health',
        'methodCount',
        'benchmarkCount',
    )
    as $marker
) {
    v0211_assert(
        strpos($production, $marker) !== false,
        'Production PHP marker: ' . $marker
    );
}

foreach (
    array(
        'MutationObserver',
        'sc-lab:module-opened',
        'clearStaleMarker',
        'BiochemistryProduction',
        'renderedMounts',
        'navigation-click',
    )
    as $marker
) {
    v0211_assert(
        strpos($runtime, $marker) !== false,
        'Production runtime marker: ' . $marker
    );
}

v0211_assert(
    strpos($style, '@media (max-width: 760px)')
        !== false,
    'Mobile reliability styles'
);

v0211_assert(
    strpos(
        $current_suite,
        'CURRENT_VERSION'
    ) !== false,
    'Version-aware release suite'
);

echo "Lab v0.21.1 PHP structural tests passed.\n";
