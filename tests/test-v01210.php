<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-statistical-modeling-diagnostics-studio-v01210.php','assets/js/modules/statistical-modeling-diagnostics-studio-v01210.js','assets/css/sc-lab-statistical-modeling-diagnostics-studio-v01210.css','contracts/statistical-modeling-diagnostics-studio-v01210.schema.json','contracts/statistical-modeling-diagnostics-studio-policy-v01210.json');
foreach($files as $f){ if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);} }
$php=file_get_contents($root.'/includes/class-sc-lab-statistical-modeling-diagnostics-studio-v01210.php');
foreach(array("const VERSION='0.121.0'","apiRouteCount'=>18","automaticModelSelection'=>false","automaticSignificanceLabels'=>false","automaticCausalInference'=>false","automaticScientificValidityCertification'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle\n");exit(1);}}
echo "PASS - Lab v0.121.0 WordPress Statistical Modeling & Model Diagnostics Studio assertions\n";
