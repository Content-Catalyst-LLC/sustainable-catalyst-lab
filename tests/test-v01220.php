<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-bayesian-analysis-workbench-v01220.php','assets/js/modules/bayesian-analysis-workbench-v01220.js','assets/css/sc-lab-bayesian-analysis-workbench-v01220.css','contracts/bayesian-analysis-workbench-v01220.schema.json','contracts/bayesian-analysis-workbench-policy-v01220.json');
foreach($files as $f){if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);}}
$php=file_get_contents($root.'/includes/class-sc-lab-bayesian-analysis-workbench-v01220.php');
foreach(array("const VERSION='0.122.0'","apiRouteCount'=>20","automaticPriorSelection'=>false","automaticConvergenceCertification'=>false","automaticModelSelection'=>false","automaticScientificValidityCertification'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle\n");exit(1);}}
echo "PASS - Lab v0.122.0 WordPress Bayesian Analysis Workbench II assertions\n";
