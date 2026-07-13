<?php
$root = dirname(__DIR__);

function civil_authority_assert($condition, $message) {
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
$authority = file_get_contents(
    $root
    . '/includes/'
    . 'class-sc-lab-civil-interface-authority-v0200.php'
);
$repaired_module = file_get_contents(
    $root
    . '/assets/js/modules/'
    . 'civil-infrastructure-lab-v0150.js'
);

civil_authority_assert(
    strpos(
        $main,
        'class-sc-lab-civil-interface-authority-v0200.php'
    ) !== false,
    'Civil authority bootstrap include'
);

civil_authority_assert(
    strpos(
        $template,
        'data-civil-infrastructure-root'
    ) !== false,
    'Civil mount'
);

civil_authority_assert(
    strpos(
        $authority,
        '/civil-infrastructure-lab.js'
    ) !== false,
    'Original Civil source suppression'
);

civil_authority_assert(
    strpos(
        $authority,
        'civil-infrastructure-lab-v0150.js'
    ) !== false,
    'Repaired Civil source enqueue'
);

civil_authority_assert(
    strpos(
        $authority,
        'wp_deregister_script'
    ) !== false,
    'Original Civil handle deregistration'
);

civil_authority_assert(
    strpos(
        $authority,
        'mount.replaceChildren()'
    ) !== false,
    'Civil mount reset before authoritative render'
);

civil_authority_assert(
    strpos(
        $repaired_module,
        'Lab.CivilInfrastructureLab'
    ) !== false,
    'Repaired Civil global export'
);

civil_authority_assert(
    strpos(
        $repaired_module,
        'const VERSION = "0.15.0"'
    ) !== false,
    'Repaired Civil version'
);

echo "Civil interface authority tests passed.\n";
