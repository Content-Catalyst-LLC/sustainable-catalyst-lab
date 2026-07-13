<?php
$root = dirname(__DIR__);
$template_path = $root . '/templates/lab-app.php';
$template = file_get_contents($template_path);

function civil_route_fail($message) {
    fwrite(STDERR, "FAIL: {$message}\n");
    exit(1);
}

$pattern = '/<section\b'
    . '(?=[^>]*\bdata-lab-module="civil-infrastructure")'
    . '(?=[^>]*\bdata-module-panel="civil-infrastructure")'
    . '[^>]*>/i';

if (preg_match_all($pattern, $template, $matches) !== 1) {
    civil_route_fail(
        'Exactly one canonical Civil panel opening tag is required.'
    );
}

$tag = $matches[0][0];

if (strpos($tag, 'sc-lab-panel') === false) {
    civil_route_fail('Civil panel class is missing.');
}

if (strpos($tag, 'sc-lab-module') === false) {
    civil_route_fail('Civil module class is missing.');
}

if (strpos($tag, 'hidden') === false) {
    civil_route_fail('Civil panel must start hidden.');
}

$app = file_get_contents(
    $root . '/assets/js/sc-lab-app.js'
);

if (
    strpos($app, "'[data-lab-module]'") === false
    && strpos($app, '"[data-lab-module]"') === false
) {
    civil_route_fail(
        'Core Lab router no longer targets data-lab-module.'
    );
}

if (
    strpos($app, "'[data-lab-module-button]'") === false
    && strpos($app, '"[data-lab-module-button]"') === false
) {
    civil_route_fail(
        'Core Lab navigation buttons are not detected.'
    );
}

echo "Civil canonical-route tests passed.\n";
