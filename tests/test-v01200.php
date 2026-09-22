<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-exploratory-data-analysis-studio-v01200.php','assets/js/modules/exploratory-data-analysis-studio-v01200.js','assets/css/sc-lab-exploratory-data-analysis-studio-v01200.css','contracts/exploratory-data-analysis-studio-v01200.schema.json','contracts/exploratory-data-analysis-studio-policy-v01200.json');
foreach($files as $f){ if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);} }
$php=file_get_contents($root.'/includes/class-sc-lab-exploratory-data-analysis-studio-v01200.php');
foreach(array("const VERSION='0.120.0'","apiRouteCount'=>20","automaticSourceMutation'=>false","automaticHypothesisConfirmation'=>false","automaticScientificValidityCertification'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle\n");exit(1);}}
echo "PASS - Lab v0.120.0 WordPress Exploratory Data Analysis Studio assertions\n";
