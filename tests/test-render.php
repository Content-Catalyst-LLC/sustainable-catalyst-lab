<?php
$root = dirname(__DIR__);
define('ABSPATH', $root);
define('SC_LAB_VERSION', '0.8.0');
function esc_attr($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
function esc_html($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
$sc_lab_initial_module = 'overview';
$sc_lab_initial_project = 'default';
ob_start();
include $root . '/templates/lab-app.php';
$html = ob_get_clean();
function ok_render($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }
ok_render(substr_count($html, 'data-lab-module=')  >= 20, 'Expected at least 20 module panels');
ok_render(substr_count($html, 'data-lab-module-button=')  >= 20, 'Expected grouped module buttons');
ok_render(substr_count($html, 'data-quick-tool=') >= 14, 'Expected quick scientific tools');
ok_render(substr_count($html, 'data-lab-command-input') === 1, 'Expected one command input');
ok_render(substr_count($html, 'data-record-dialog') === 1, 'Expected one record dialog');
ok_render(strpos($html, '>Project<') < strpos($html, '>Observe<') && strpos($html, '>Observe<') < strpos($html, '>Analyze<') && strpos($html, '>Analyze<') < strpos($html, '>Record<'), 'Navigation groups are out of order');
ok_render(strpos($html, 'Physics, electromagnetism, and particle physics laboratory') !== false, 'Physics laboratory missing');
ok_render(strpos($html, 'Biology and computational biology laboratory') !== false, 'Biology laboratory missing');
ok_render(strpos($html, 'Astronomy and astrophysics laboratory') !== false, 'Astronomy laboratory missing');
ok_render(strpos($html, 'Materials science and characterization laboratory') !== false, 'Materials laboratory missing');
ok_render(strpos($html, 'Earth, climate, ocean, and marine systems laboratory') !== false, 'Earth systems laboratory missing');
ok_render(substr_count($html, 'data-earth-tool-grid=') === 9, 'Expected nine Earth systems tool grids');
ok_render(strpos($html, 'data-earth-benchmark-table') !== false, 'Earth systems benchmark table missing');
ok_render(substr_count($html, 'data-materials-tool-grid=') === 11, 'Expected eleven materials tool grids');
ok_render(strpos($html, 'data-materials-benchmark-table') !== false, 'Materials benchmark table missing');
ok_render(substr_count($html, 'data-astronomy-tool-grid=') === 9, 'Expected nine astronomy tool grids');
ok_render(strpos($html, 'data-astronomy-benchmark-table') !== false, 'Astronomy benchmark table missing');
ok_render(substr_count($html, 'data-physics-tool=') >= 27, 'Expected substantive physics tools');
ok_render(strpos($html, 'data-physics-run-benchmarks') !== false, 'Physics validation controls missing');
ok_render(strpos($html, 'data-biology-run-benchmarks') !== false, 'Biology validation controls missing');
ok_render(substr_count($html, 'data-biology-tool-grid=') === 9, 'Expected nine biology work areas');
ok_render(strpos($html, 'data-biology-benchmark-table') !== false, 'Biology benchmark table missing');
ok_render(substr_count($html, '<section') === substr_count($html, '</section>'), 'Section tags are unbalanced');
ok_render(substr_count($html, '<div') === substr_count($html, '</div>'), 'Div tags are unbalanced');
ok_render(strpos($html, 'v0.8.0') !== false, 'Rendered version is incorrect');
echo "Template render tests passed.\n";
