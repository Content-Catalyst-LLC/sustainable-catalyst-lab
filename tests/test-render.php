<?php
$root = dirname(__DIR__);
define('ABSPATH', $root);
define('SC_LAB_VERSION', '0.1.1');
function esc_attr($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
function esc_html($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
$sc_lab_initial_module = 'overview';
$sc_lab_initial_project = 'default';
ob_start();
include $root . '/templates/lab-app.php';
$html = ob_get_clean();
function ok_render($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }
ok_render(substr_count($html, 'data-lab-module=') >= 13, 'Expected 13 module panels');
ok_render(substr_count($html, 'data-lab-module-button=') >= 13, 'Expected grouped module buttons');
ok_render(substr_count($html, 'data-quick-tool=') >= 8, 'Expected quick scientific tools');
ok_render(substr_count($html, 'data-lab-command-input') === 1, 'Expected one command input');
ok_render(substr_count($html, 'data-record-dialog') === 1, 'Expected one record dialog');
ok_render(strpos($html, '>Project<') < strpos($html, '>Observe<') && strpos($html, '>Observe<') < strpos($html, '>Analyze<') && strpos($html, '>Analyze<') < strpos($html, '>Record<'), 'Navigation groups are out of order');
ok_render(substr_count($html, '<section') === substr_count($html, '</section>'), 'Section tags are unbalanced');
ok_render(substr_count($html, '<div') === substr_count($html, '</div>'), 'Div tags are unbalanced');
ok_render(strpos($html, 'v0.1.1') !== false, 'Rendered version is incorrect');
echo "Template render tests passed.\n";
