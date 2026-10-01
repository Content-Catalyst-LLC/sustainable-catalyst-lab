<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$tpl=file_get_contents($root.'/templates/lab-app.php');
$cls=file_get_contents($root.'/includes/class-sc-lab-reproducible-protocol-notebook-v01540.php');
$css=file_get_contents($root.'/assets/css/sc-lab-reproducible-protocol-notebook-v01540.css');
$checks=array(
 'release header'=>strpos($main,'Version: 0.154.0')!==false,
 'release fallback'=>strpos($main,"'releaseVersion', '0.154.0'")!==false,
 'authority class'=>strpos($main,'SC_Lab_Reproducible_Protocol_Notebook_V01540::init()')!==false,
 'workspace panel'=>strpos($tpl,'data-v01540-workspace')!==false,
 'protocol controls'=>strpos($tpl,'data-v01540-protocol-create')!==false && strpos($tpl,'data-v01540-protocol-revise')!==false,
 'notebook controls'=>strpos($tpl,'data-v01540-notebook-create')!==false && strpos($tpl,'data-v01540-add-cell')!==false,
 'manifest controls'=>strpos($tpl,'data-v01540-manifest')!==false && strpos($tpl,'data-v01540-export-manifest')!==false,
 'outside compact rail'=>strpos(substr($tpl,strpos($tpl,'<aside class="sc-lab-v0710-controls"'),strpos($tpl,'</aside>',strpos($tpl,'<aside class="sc-lab-v0710-controls"'))-strpos($tpl,'<aside class="sc-lab-v0710-controls"')),'data-v01540-workspace')===false,
 'frontend health route'=>strpos($cls,'frontend-runtime/v01540/health')!==false,
 'protocol proxy route'=>strpos($cls,'workspace/reproducible/v01540/protocols')!==false,
 'notebook proxy route'=>strpos($cls,'workspace/reproducible/v01540/notebooks')!==false,
 'manifest verify proxy'=>strpos($cls,'workspace/reproducible/v01540/manifests/verify')!==false,
 'arbitrary code disabled'=>strpos($cls,"'arbitraryCodeExecution'=>false")!==false,
 'visual recovery retained'=>strpos($cls,"'v015213VisualRecoveryBaselineRetained'=>true")!==false,
 '4d workspace retained'=>strpos($cls,"'v01530FourDWorkspaceRetained'=>true")!==false,
 'responsive notebook css'=>strpos($css,'.sc-lab-v01540-workspace')!==false && strpos($css,'@media(max-width:900px)')!==false
);
foreach($checks as $name=>$ok){echo ($ok?'PASS':'FAIL').' - '.$name.PHP_EOL;if(!$ok)exit(1);}
