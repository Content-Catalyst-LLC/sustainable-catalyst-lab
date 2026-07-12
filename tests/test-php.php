<?php
$root = dirname(__DIR__);
function ok($condition, $message) { if (!$condition) { fwrite(STDERR, "FAIL: $message\n"); exit(1); } }
$required = array(
 'sustainable-catalyst-lab.php','includes/class-sc-lab-plugin.php','includes/class-sc-lab-feeds.php','includes/class-sc-lab-rest.php','templates/lab-app.php','assets/css/sc-lab-app.css','assets/js/sc-lab-app.js','assets/data/elements.json'
);
foreach ($required as $file) { ok(is_file($root . '/' . $file), "Missing $file"); }
$main = file_get_contents($root . '/sustainable-catalyst-lab.php');
ok(strpos($main, 'Version: 0.1.0') !== false, 'Version marker missing');
$elements = json_decode(file_get_contents($root . '/assets/data/elements.json'), true);
ok(is_array($elements) && count($elements) === 118, 'Periodic table must contain 118 elements');
$feeds = file_get_contents($root . '/includes/class-sc-lab-feeds.php');
foreach (array('usgs-earthquakes','nasa-eonet','nasa-space-telescopes','obis-marine','pubmed-science','arxiv-physics') as $source) { ok(strpos($feeds, "'$source'") !== false, "Missing source $source"); }
$template = file_get_contents($root . '/templates/lab-app.php');
foreach (array('Scientific signal board','Climate and Earth observation map','Space telescope observations','Marine biodiversity observations','Chemistry workspace','Science and engineering tools','Experiment registry','Data-connected documentation') as $heading) { ok(strpos($template, $heading) !== false, "Missing interface heading $heading"); }
ok(substr_count($template, 'data-lab-module=') >= 12, 'Expected at least 12 module panels');
echo "PHP structural tests passed.\n";
