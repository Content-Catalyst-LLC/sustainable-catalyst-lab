<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-simulation-monte-carlo-research-studio-v01230.php','assets/js/modules/simulation-monte-carlo-research-studio-v01230.js','assets/css/sc-lab-simulation-monte-carlo-research-studio-v01230.css','contracts/simulation-monte-carlo-research-studio-v01230.schema.json','contracts/simulation-monte-carlo-research-studio-policy-v01230.json');
foreach($files as $f){if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f
");exit(1);}}
$php=file_get_contents($root.'/includes/class-sc-lab-simulation-monte-carlo-research-studio-v01230.php');
foreach(array("const VERSION='0.123.0'","apiRouteCount'=>22","simulationOutputsAreModeledNotObserved'=>true","automaticConvergenceCertification'=>false","automaticScenarioSelection'=>false","automaticEvidencePromotion'=>false","automaticScientificValidityCertification'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle
");exit(1);}}
echo "PASS - Lab v0.123.0 WordPress Simulation & Monte Carlo Research Studio assertions
";
