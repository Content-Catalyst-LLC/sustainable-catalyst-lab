<?php
$root = dirname(__DIR__);
$plugin = file_get_contents($root . '/sustainable-catalyst-lab.php');
$class = file_get_contents($root . '/includes/class-sc-lab-unified-workspace-shell-v01631.php');
$js = file_get_contents($root . '/assets/js/sc-lab-unified-workspace-shell-v01631.js');
$css = file_get_contents($root . '/assets/css/sc-lab-unified-workspace-shell-v01631.css');
$manifest = json_decode(file_get_contents($root . '/build/sc-lab-release-manifest.json'), true);
$assert = function ($cond, $msg) { if (!$cond) { fwrite(STDERR, "FAIL - $msg\n"); exit(1); } };
$assert(strpos($plugin, 'Version: 0.163.1') !== false, 'plugin version');
$assert(strpos($plugin, 'SC_Lab_Unified_Workspace_Shell_V01631::init();') !== false, 'shell initialized');
$assert(strpos($class, "const VERSION = '0.163.1'") !== false, 'class version');
$assert(strpos($class, "'sc-lab-institutional-governance-v01630'") !== false, 'shell loads after governance module');
$assert(strpos($class, 'specialistWorkspaceCount') !== false, 'specialist workspace contract localized');
$assert(strpos($js, 'MutationObserver') !== false, 'progressive module observer');
$assert(strpos($js, 'data-sc-lab-shell-module') !== false, 'single-workspace stage contract');
$assert(strpos($js, "id: 'overview'") === false, 'overview remains shell state rather than duplicated specialist module');
foreach (array('four-d','notebook','batch','compute','cross-study','replication','review','research-os','programs','resources','governance') as $id) { $assert(strpos($js, "id: '$id'") !== false, "module $id"); }
$assert(strpos($js, 'sessionStorage') !== false, 'session workspace preservation');
$assert(strpos($js, 'Methods &amp; governance') !== false, 'governance drawer');
$assert(strpos($css, 'grid-template-columns:250px minmax(0,1fr)') !== false, 'desktop app-shell layout');
$assert(strpos($css, '.sc-lab-v01631-managed[hidden]') !== false, 'inactive workspace hidden');
$assert(($manifest['releaseVersion'] ?? '') === '0.163.1', 'manifest release version');
$assert(!empty($manifest['v01631UnifiedWorkspaceShell']), 'manifest shell flag');
echo "PASS - v0.163.1 WordPress unified workspace shell contract\n";
