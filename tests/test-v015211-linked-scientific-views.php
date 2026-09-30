<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$runtime=file_get_contents($root.'/includes/class-sc-lab-linked-scientific-views-v015211.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
 'release header'=>strpos($main,'Version: 0.152.0.11')!==false,
 'runtime loaded'=>strpos($main,'class-sc-lab-linked-scientific-views-v015211.php')!==false,
 'safe bootstrap'=>strpos($runtime,'sc-lab-safe-bootstrap-v015211.js')!==false,
 'linked runtime'=>strpos($runtime,'sc-lab-linked-scientific-views-v015211.js')!==false,
 'health route'=>strpos($runtime,'frontend-runtime/v015211/health')!==false,
 'linked selection schema'=>strpos($runtime,'sc-lab-linked-selection/1.0')!==false,
 'selection event'=>strpos($runtime,'sc-lab:linked-selection')!==false,
 'graph handoff schema'=>strpos($runtime,'sc-lab-graph-studio-selection-handoff/1.0')!==false,
 'linked panel'=>strpos($template,'data-v015211-linked')!==false,
 'selection inspector'=>strpos($template,'data-v015211-field="source"')!==false,
 'parameter table'=>strpos($template,'data-v015211-table')!==false,
 'history'=>strpos($template,'data-v015211-history')!==false,
 'graph studio action'=>strpos($template,'data-v015211-graph')!==false,
 'manifest flag'=>!empty($manifest['v015211LinkedScientificViews']),
 'cross-view flag'=>!empty($manifest['v015211CrossViewSelection']),
 'output gate'=>!empty($manifest['v015211PHPOutputSafetyGateRetained']),
 'backend unchanged'=>isset($manifest['v015211BackendBehaviorChanged']) && $manifest['v015211BackendBehaviorChanged']===false,
 'automatic cross-model inference false'=>isset($manifest['v015211AutomaticCrossModelInference']) && $manifest['v015211AutomaticCrossModelInference']===false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}}
echo "PASS - v0.152.0.11 PHP/runtime contract\n";
