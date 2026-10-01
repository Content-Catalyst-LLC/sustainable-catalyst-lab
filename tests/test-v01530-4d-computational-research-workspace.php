<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$tpl=file_get_contents($root.'/templates/lab-app.php');
$cls=file_get_contents($root.'/includes/class-sc-lab-4d-computational-research-workspace-v01530.php');
$css=file_get_contents($root.'/assets/css/sc-lab-4d-computational-research-workspace-v01530.css');
$checks=array(
 'release header'=>strpos($main,'Version: 0.153.0')!==false,
 'authority class'=>strpos($main,'SC_Lab_4D_Computational_Research_Workspace_V01530::init()')!==false,
 'workspace panel'=>strpos($tpl,'data-v01530-workspace')!==false,
 'runtime chip current'=>strpos($tpl,'v0.153.0 4D computational research workspace runtime')!==false,
 'scene release current'=>strpos($tpl,'<dt>Release</dt><dd>v0.153.0</dd>')!==false,
 'workspace outside compact rail'=>strpos(substr($tpl,strpos($tpl,'<aside class="sc-lab-v0710-controls"'),strpos($tpl,'</aside>',strpos($tpl,'<aside class="sc-lab-v0710-controls"'))-strpos($tpl,'<aside class="sc-lab-v0710-controls"')),'data-v01530-workspace')===false,
 'backend proxy route'=>strpos($cls,'workspace/4d/v01530/assets')!==false,
 'frontend health route'=>strpos($cls,'frontend-runtime/v01530/health')!==false,
 'server assets health'=>strpos($cls,"'serverBackedProjectAssets'=>true")!==false,
 'backend changed flag'=>strpos($cls,"'backendBehaviorChanged'=>true")!==false,
 'scientific methods unchanged'=>strpos($cls,"'scientificComputeMethodsChanged'=>false")!==false,
 'responsive workspace css'=>strpos($css,'.sc-lab-v01530-workspace')!==false && strpos($css,'@media(max-width:980px)')!==false,
 'visual recovery css retained'=>strpos($cls,'sc-lab-front-door-layout-render-recovery-v015213.css')!==false
);
foreach($checks as $name=>$ok){echo ($ok?'PASS':'FAIL').' - '.$name.PHP_EOL;if(!$ok)exit(1);} 
