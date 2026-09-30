<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$runtime=file_get_contents($root.'/includes/class-sc-lab-interactive-4d-front-door-v015207.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
 'release header'=>strpos($main,'Version: 0.152.0.7')!==false,
 'new runtime loaded'=>strpos($main,'class-sc-lab-interactive-4d-front-door-v015207.php')!==false,
 'safe script allowed'=>strpos($runtime,'sc-lab-safe-bootstrap-v015207.js')!==false,
 '4d script allowed'=>strpos($runtime,'sc-lab-4d-front-door-v015207.js')!==false,
 'compute health route'=>strpos($runtime,'compute/core/health')!==false,
 'compute capabilities route'=>strpos($runtime,'compute/core/capabilities')!==false,
 'compute run route'=>strpos($runtime,'compute/core/run')!==false,
 'parameter sweep contract'=>strpos($runtime,"simulation.parameter_sweep")!==false,
 'old optional bundle not allowlisted'=>strpos($runtime,"sc-lab-optional-modules-v015204.js")===false,
 'old presentation runtime not allowlisted'=>strpos($runtime,"presentation-runtime-v0482.js")===false,
 'old production monitor not allowlisted'=>strpos($runtime,"sc-lab-production-stability-v0266.js")===false,
 'demo selector'=>strpos($template,'data-v015207-demo')!==false,
 'compute action'=>strpos($template,'data-v015207-run-compute')!==false,
 'png export'=>strpos($template,'data-v015207-export="png"')!==false,
 'json export'=>strpos($template,'data-v015207-export="json"')!==false,
 'manifest flag'=>!empty($manifest['v015207Interactive4DFrontDoor']),
 'backend unchanged'=>isset($manifest['v015207BackendBehaviorChanged']) && $manifest['v015207BackendBehaviorChanged']===false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}}
echo "PASS - v0.152.0.7 PHP/runtime contract\n";
