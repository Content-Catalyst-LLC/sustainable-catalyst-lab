<?php
function must01050($condition, $message) {
    if (!$condition) { fwrite(STDERR, "FAIL - $message\n"); exit(1); }
}
$main = file_get_contents(__DIR__ . '/../sustainable-catalyst-lab.php');
$plugin = file_get_contents(__DIR__ . '/../includes/class-sc-lab-plugin.php');
$mapping = file_get_contents(__DIR__ . '/../includes/class-sc-lab-platform-core-v3-object-mapping-v01050.php');
must01050((bool)preg_match('/^ \* Version: 0\.105\.0$/m', $main), 'plugin header v0.105.0');
must01050(strpos($main, 'class-sc-lab-platform-core-v3-object-mapping-v01050.php') !== false, 'mapping class loaded');
must01050(strpos($plugin, 'platformCoreV3ObjectMapping') !== false, 'frontend config exposed');
must01050(strpos($mapping, "const VERSION = '0.105.0'") !== false, 'mapping class version');
must01050(strpos($mapping, "const CORE_REQUIRED_VERSION = '3.0.0'") !== false, 'Core 3.0.0 requirement');
must01050(strpos($mapping, "'evidence-record' => 'evidence'") !== false, 'evidence canonical mapping');
must01050(strpos($mapping, "'scientific-figure' => 'scientific-figure'") !== false, 'scientific figure mapping');
echo "PASS - Lab v0.105.0 canonical research object mapping PHP contracts\n";
