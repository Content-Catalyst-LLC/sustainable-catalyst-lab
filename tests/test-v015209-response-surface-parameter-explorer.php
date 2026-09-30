<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$runtime=file_get_contents($root.'/includes/class-sc-lab-response-surface-parameter-explorer-v015209.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
 'release header'=>strpos($main,'Version: 0.152.0.9')!==false,
 'runtime loaded'=>strpos($main,'class-sc-lab-response-surface-parameter-explorer-v015209.php')!==false,
 'safe bootstrap'=>strpos($runtime,'sc-lab-safe-bootstrap-v015209.js')!==false,
 'explorer runtime'=>strpos($runtime,'sc-lab-response-surface-parameter-explorer-v015209.js')!==false,
 'compute health'=>strpos($runtime,'compute/core/health')!==false,
 'compute capabilities'=>strpos($runtime,'compute/core/capabilities')!==false,
 'compute run'=>strpos($runtime,'compute/core/run')!==false,
 'method contract'=>strpos($runtime,'simulation.parameter_sweep')!==false,
 'model selector'=>strpos($template,'data-v015209-model')!==false,
 'x axis selector'=>strpos($template,'data-v015209-axis="x"')!==false,
 'y axis selector'=>strpos($template,'data-v015209-axis="y"')!==false,
 'w axis selector'=>strpos($template,'data-v015209-axis="w"')!==false,
 'run surface'=>strpos($template,'data-v015209-run-surface')!==false,
 'baseline'=>strpos($template,'data-v015209-set-baseline')!==false,
 'saved configs'=>strpos($template,'data-v015209-saved-configs')!==false,
 'csv export'=>strpos($template,'data-v015209-export="csv"')!==false,
 'manifest flag'=>!empty($manifest['v015209InteractiveResponseSurfaceParameterExplorer']),
 'output gate'=>!empty($manifest['v015209PHPOutputSafetyGateRetained']),
 'backend unchanged'=>isset($manifest['v015209BackendBehaviorChanged']) && $manifest['v015209BackendBehaviorChanged']===false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}}
echo "PASS - v0.152.0.9 PHP/runtime contract\n";
