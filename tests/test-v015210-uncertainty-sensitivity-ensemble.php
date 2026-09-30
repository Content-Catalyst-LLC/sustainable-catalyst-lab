<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$runtime=file_get_contents($root.'/includes/class-sc-lab-uncertainty-sensitivity-ensemble-explorer-v015210.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
 'release header'=>strpos($main,'Version: 0.152.0.10')!==false,
 'runtime loaded'=>strpos($main,'class-sc-lab-uncertainty-sensitivity-ensemble-explorer-v015210.php')!==false,
 'safe bootstrap'=>strpos($runtime,'sc-lab-safe-bootstrap-v015210.js')!==false,
 'analysis runtime'=>strpos($runtime,'sc-lab-uncertainty-sensitivity-ensemble-v015210.js')!==false,
 'health route'=>strpos($runtime,'frontend-runtime/v015210/health')!==false,
 'mc method'=>strpos($runtime,'uncertainty.monte_carlo_propagation')!==false,
 'sensitivity method'=>strpos($runtime,'sensitivity.local_finite_difference')!==false,
 'analysis panel'=>strpos($template,'data-v015210-analysis')!==false,
 'run mc'=>strpos($template,'data-v015210-run-uncertainty')!==false,
 'run sensitivity'=>strpos($template,'data-v015210-run-sensitivity')!==false,
 'run ensemble'=>strpos($template,'data-v015210-run-ensemble')!==false,
 'analysis canvas'=>strpos($template,'data-v015210-analysis-canvas')!==false,
 'manifest flag'=>!empty($manifest['v015210FourDUncertaintySensitivityEnsembleExplorer']),
 'output gate'=>!empty($manifest['v015210PHPOutputSafetyGateRetained']),
 'backend unchanged'=>isset($manifest['v015210BackendBehaviorChanged']) && $manifest['v015210BackendBehaviorChanged']===false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}}
echo "PASS - v0.152.0.10 PHP/runtime contract\n";
