<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-sensitivity-global-uncertainty-analysis-studio-v01240.php','assets/js/modules/sensitivity-global-uncertainty-analysis-studio-v01240.js','assets/css/sc-lab-sensitivity-global-uncertainty-analysis-studio-v01240.css','contracts/sensitivity-global-uncertainty-analysis-studio-v01240.schema.json','contracts/sensitivity-global-uncertainty-analysis-policy-v01240.json');
foreach($files as $f){if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);}}
$php=file_get_contents($root.'/includes/class-sc-lab-sensitivity-global-uncertainty-analysis-studio-v01240.php');
foreach(array("const VERSION='0.124.0'","apiRouteCount'=>22","simulationOutputsAreModeledNotObserved'=>true","automaticParameterRanking'=>false","automaticSignificanceInference'=>false","automaticCausalInference'=>false","automaticScientificValidityCertification'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle\n");exit(1);}}
echo "PASS - Lab v0.124.0 WordPress Sensitivity & Global Uncertainty Analysis Studio assertions\n";
