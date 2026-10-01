<?php
$root = dirname(__DIR__);
$plugin = file_get_contents($root . '/sustainable-catalyst-lab.php');
if (strpos($plugin, 'Version: 0.163.0.1') === false) { fwrite(STDERR, "FAIL - plugin version\n"); exit(1); }
if (strpos($plugin, "'releaseVersion', '0.163.0.1'") === false) { fwrite(STDERR, "FAIL - fallback version\n"); exit(1); }
$manifest = json_decode(file_get_contents($root . '/build/sc-lab-release-manifest.json'), true);
if (($manifest['releaseVersion'] ?? '') !== '0.163.0.1') { fwrite(STDERR, "FAIL - releaseVersion\n"); exit(1); }
if (($manifest['featureVersion'] ?? '') !== '0.163.0') { fwrite(STDERR, "FAIL - featureVersion\n"); exit(1); }
foreach (array('v016301InstitutionalGovernanceConfigurationNamespaceRepair','v016301BackendStartupRepair','v016301FederationConfigurationNamespaceIsolated','v016301LegacyInstitutionalGovernanceNamespacePreserved','v016301BackendStartupBindingValidated','v016301DeploymentRollbackOnHealthFailure') as $k) {
    if (($manifest[$k] ?? null) !== true) { fwrite(STDERR, "FAIL - $k\n"); exit(1); }
}
echo "PASS - v0.163.0.1 WordPress/release identity contract\n";
