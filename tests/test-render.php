<?php
$root = dirname(__DIR__);
define('ABSPATH', $root);
define('SC_LAB_VERSION', '0.5.0');
function esc_attr($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
function esc_html($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
$sc_lab_initial_module = 'overview';
$sc_lab_initial_project = 'default';
ob_start();
include $root . '/templates/lab-app.php';
$html = ob_get_clean();
function ok_render($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }
ok_render(substr_count($html, 'data-lab-module=') >= 17, 'Expected 17 module panels');
ok_render(substr_count($html, 'data-lab-module-button=') >= 17, 'Expected grouped module buttons');
ok_render(substr_count($html, 'data-quick-tool=') >= 14, 'Expected quick scientific tools');
ok_render(substr_count($html, 'data-lab-command-input') === 1, 'Expected one command input');
ok_render(substr_count($html, 'data-record-dialog') === 1, 'Expected one record dialog');
ok_render(strpos($html, '>Project<') < strpos($html, '>Observe<') && strpos($html, '>Observe<') < strpos($html, '>Analyze<') && strpos($html, '>Analyze<') < strpos($html, '>Record<'), 'Navigation groups are out of order');
ok_render(strpos($html, 'Physics, electromagnetism, and particle physics laboratory') !== false, 'Physics laboratory missing');
ok_render(strpos($html, 'Biology and computational biology laboratory') !== false, 'Biology laboratory missing');
ok_render(substr_count($html, 'data-physics-tool=') >= 27, 'Expected substantive physics tools');
ok_render(strpos($html, 'data-physics-run-benchmarks') !== false, 'Physics validation controls missing');
ok_render(strpos($html, 'data-biology-run-benchmarks') !== false, 'Biology validation controls missing');
ok_render(substr_count($html, 'data-biology-tool-grid=') === 9, 'Expected nine biology work areas');
ok_render(strpos($html, 'data-biology-benchmark-table') !== false, 'Biology benchmark table missing');
ok_render(substr_count($html, '<section') === substr_count($html, '</section>'), 'Section tags are unbalanced');
ok_render(substr_count($html, '<div') === substr_count($html, '</div>'), 'Div tags are unbalanced');
ok_render(strpos($html, 'v0.5.0') !== false, 'Rendered version is incorrect');
echo "Template render tests passed.\n";
