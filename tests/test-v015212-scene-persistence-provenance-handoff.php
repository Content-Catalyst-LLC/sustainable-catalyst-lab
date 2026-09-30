<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$runtime=file_get_contents($root.'/includes/class-sc-lab-scene-persistence-provenance-handoff-v015212.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
 'release header'=>strpos($main,'Version: 0.152.0.12')!==false,
 'runtime loaded'=>strpos($main,'class-sc-lab-scene-persistence-provenance-handoff-v015212.php')!==false,
 'safe bootstrap'=>strpos($runtime,'sc-lab-safe-bootstrap-v015212.js')!==false,
 'linked runtime'=>strpos($runtime,'sc-lab-linked-scientific-views-v015212.js')!==false,
 'persistence runtime'=>strpos($runtime,'sc-lab-scene-persistence-provenance-handoff-v015212.js')!==false,
 'health route'=>strpos($runtime,'frontend-runtime/v015212/health')!==false,
 'scene schema'=>strpos($runtime,'sc-lab-persisted-4d-scene/1.0')!==false,
 'provenance schema'=>strpos($runtime,'sc-lab-4d-scene-provenance/1.0')!==false,
 'handoff schema'=>strpos($runtime,'sc-lab-research-object-handoff/1.0')!==false,
 'canonical object schema'=>strpos($runtime,'sc-lab-canonical-research-object/0.105.0')!==false,
 'workspace snapshot'=>strpos($runtime,"'researchObjectType'=>'workspace-snapshot'")!==false,
 'scene panel'=>strpos($template,'data-v015212-persistence')!==false,
 'save scene'=>strpos($template,'data-v015212-save')!==false,
 'prepare research object'=>strpos($template,'data-v015212-prepare')!==false,
 'graph handoff'=>strpos($template,'data-v015212-handoff="graph-studio"')!==false,
 'notebook handoff'=>strpos($template,'data-v015212-handoff="notebook"')!==false,
 'experiments handoff'=>strpos($template,'data-v015212-handoff="experiments"')!==false,
 'manifest persistence'=>!empty($manifest['v015212FourDScenePersistence']),
 'manifest handoff'=>!empty($manifest['v015212ResearchObjectHandoff']),
 'reference first'=>!empty($manifest['v015212ReferenceFirst']),
 'automatic core submission false'=>isset($manifest['v015212AutomaticCoreSubmission']) && $manifest['v015212AutomaticCoreSubmission']===false,
 'restore no rerun'=>isset($manifest['v015212RestoringSceneRerunsCompute']) && $manifest['v015212RestoringSceneRerunsCompute']===false,
 'backend unchanged'=>isset($manifest['v015212BackendBehaviorChanged']) && $manifest['v015212BackendBehaviorChanged']===false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}}
echo "PASS - v0.152.0.12 PHP/runtime contract\n";
