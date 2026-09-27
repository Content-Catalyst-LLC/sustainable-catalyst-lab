<?php
$root = dirname(__DIR__);
$manifest = json_decode(file_get_contents($root . '/build/sc-lab-release-manifest.json'), true);
if (!is_array($manifest)) { fwrite(STDERR,"FAIL manifest parse\n"); exit(1); }
if (($manifest['releaseVersion'] ?? null) !== '0.136.0.1') { fwrite(STDERR,"FAIL release version\n"); exit(1); }
if (($manifest['featureVersion'] ?? null) !== '0.136.0.1') { fwrite(STDERR,"FAIL feature version\n"); exit(1); }
require_once $root . '/includes/sc-lab-release-bootstrap.php';
if (sc_lab_manifest_semver($manifest, 'releaseVersion', 'fallback') !== '0.136.0.1') { fwrite(STDERR,"FAIL four-part release parser\n"); exit(1); }
$files = $manifest['wordpressCriticalFiles'] ?? array();
if (!$files) { fwrite(STDERR,"FAIL WordPress integrity list missing\n"); exit(1); }
$bad = array();
foreach ($files as $relative => $expected) {
    $path = $root . '/' . $relative;
    $actual = is_file($path) ? hash_file('sha256', $path) : null;
    if (!is_string($expected) || $actual !== $expected) { $bad[] = $relative; }
}
if ($bad) { fwrite(STDERR,"FAIL hash mismatch: " . implode(',', $bad) . "\n"); exit(1); }
$plugin = file_get_contents($root . '/sustainable-catalyst-lab.php');
if (strpos($plugin, 'Version: 0.136.0.1') === false) { fwrite(STDERR,"FAIL plugin header version\n"); exit(1); }
echo "PASS - Lab v0.136.0.1 release manifest integrity synchronization repair\n";
