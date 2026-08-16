<?php
$root=dirname(__DIR__);
$integrity=file_get_contents($root.'/includes/class-sc-lab-integrity-v02632.php');
$runtimeTest=file_get_contents($root.'/tests/test-v0700-integrity-runtime.php');
$notes=file_get_contents($root.'/RELEASE_NOTES_0.70.0_R1_RUNTIME_HEALTH_REPAIR.md');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
 'R1 release notes present'=>is_file($root.'/RELEASE_NOTES_0.70.0_R1_RUNTIME_HEALTH_REPAIR.md')&&is_file($root.'/docs/RELEASE_NOTES_0.70.0_R1_RUNTIME_HEALTH_REPAIR.md'),
 'repair line marker exposed'=>strpos($integrity,"const REPAIR_LINE = '0.70.0-r1'")!==false,
 'repository validation context implemented'=>strpos($integrity,"'repository-validation'")!==false&&strpos($integrity,"'current-source-checkout'")!==false,
 'live WordPress candidate scope preserved'=>strpos($integrity,"'wordpress-plugin-directory'")!==false,
 'route integrity promoted into health'=>strpos($integrity,"'routeIntegrityVerified'")!==false&&strpos($integrity,"'integrity-contract-fallback'")!==false,
 'repository runtime test selects repository context'=>strpos($runtimeTest,"SC_LAB_INTEGRITY_CONTEXT', 'repository-validation'")!==false,
 'R1 manifest repair identity'=>($manifest['repairLine']??null)==='R1'&&($manifest['repairRelease']??null)==='0.70.0-r1',
 'WordPress release remains 0.70.0'=>($manifest['releaseVersion']??null)==='0.70.0'&&($manifest['featureVersion']??null)==='0.70.0',
 'platform compatibility remains 1.0.0'=>($manifest['platformVersion']??null)==='1.0.0',
 'scientific regression assertion count preserved'=>($manifest['routeAssertions']??null)===393,
 'R1 scope states scientific semantics unchanged'=>strpos($notes,'does not change preregistration semantics')!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
