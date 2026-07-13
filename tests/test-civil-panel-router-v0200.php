<?php
$root = dirname(__DIR__);

function civil_router_assert($condition, $message) {
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
$class = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-civil-panel-router-v0200.php'
);
$router = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'civil-panel-router-v0200.js'
);

civil_router_assert(
    strpos(
        $main,
        'class-sc-lab-civil-panel-router-v0200.php'
    ) !== false,
    'Civil panel-router bootstrap include'
);

civil_router_assert(
    strpos(
        $template,
        'data-lab-module="civil-infrastructure"'
    ) !== false,
    'Civil data-lab-module route attribute'
);

civil_router_assert(
    strpos(
        $template,
        'data-module-panel="civil-infrastructure"'
    ) !== false,
    'Civil data-module-panel route attribute'
);

civil_router_assert(
    strpos(
        $class,
        'civil-panel-router-v0200.js'
    ) !== false,
    'Civil panel-router enqueue'
);

civil_router_assert(
    strpos(
        $router,
        "targetPanel.removeAttribute('hidden')"
    ) !== false,
    'Civil hidden-state removal'
);

civil_router_assert(
    strpos(
        $router,
        "event.stopPropagation()"
    ) !== false,
    'Competing route-handler suppression'
);

civil_router_assert(
    strpos(
        $router,
        'Lab.CivilPanelRouter'
    ) !== false,
    'Civil panel-router diagnostics'
);

civil_router_assert(
    strpos(
        $router,
        "new CustomEvent('sc-lab:module-opened'"
    ) !== false,
    'Civil module-open event'
);

echo "Civil panel-routing structural tests passed.\n";
