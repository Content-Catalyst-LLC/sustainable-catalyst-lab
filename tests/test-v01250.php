<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-causal-research-studio-v01250.php','assets/js/modules/causal-research-studio-v01250.js','assets/css/sc-lab-causal-research-studio-v01250.css','contracts/causal-research-studio-v01250.schema.json','contracts/causal-research-studio-policy-v01250.json');
foreach($files as $f){if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);}}
$php=file_get_contents($root.'/includes/class-sc-lab-causal-research-studio-v01250.php');
foreach(array("const VERSION='0.125.0'","apiRouteCount'=>28","humanCausalReviewRequired'=>true","automaticCausalProof'=>false","automaticAssumptionSatisfaction'=>false","automaticMethodSelection'=>false","automaticScientificValidityCertification'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle\n");exit(1);}}
echo "PASS - Lab v0.125.0 WordPress Causal Research Studio II assertions\n";
