<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$safe=file_get_contents($root.'/includes/class-sc-lab-production-safe-boot-v015205.php');
$integrity=file_get_contents($root.'/includes/class-sc-lab-integrity-v02632.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
    'plugin header'=>strpos($main,'Version: 0.152.0.5')!==false,
    'manifest release'=>($manifest['releaseVersion']??null)==='0.152.0.5',
    'feature line retained'=>($manifest['featureVersion']??null)==='0.152.0',
    'safe boot flag'=>!empty($manifest['v015205ProductionSafeBoot']),
    'legacy eager disabled'=>!empty($manifest['v015205LegacyModuleEagerExecutionDisabled']),
    'optional eager disabled'=>!empty($manifest['v015205OptionalRuntimeEagerExecutionDisabled']),
    'backend unchanged'=>isset($manifest['v015205BackendBehaviorChanged']) && $manifest['v015205BackendBehaviorChanged']===false,
    'safe class loaded'=>strpos($main,'class-sc-lab-production-safe-boot-v015205.php')!==false,
    'late queue gate'=>strpos($safe,"PHP_INT_MAX")!==false,
    'safe JS enqueued'=>strpos($safe,'sc-lab-safe-bootstrap-v015205.js')!==false,
    'main old critical bundle not enqueued'=>strpos($plugin,"wp_enqueue_script('sc-lab-app', SC_LAB_URL . 'assets/js/sc-lab-bootstrap-v015204.js'")===false,
    'main optional bundle not enqueued'=>strpos($plugin,"wp_enqueue_script('sc-lab-optional-bundle-v015204'")===false,
    'patch matcher exists'=>strpos($integrity,'feature_release_matches')!==false,
    'feature compatibility exposed'=>strpos($integrity,"'featureReleaseCompatible' => \$feature_release_compatible")!==false,
);
foreach($checks as $name=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $name\n");exit(1);}}
echo "PASS - v0.152.0.5 production safe boot and patch-aware integrity contract\n";
