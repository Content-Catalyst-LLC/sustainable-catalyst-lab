<?php
$root=dirname(__DIR__);
$files=array('includes/class-sc-lab-scientific-figure-intelligence-automatic-layout-v01190.php','assets/js/modules/scientific-figure-intelligence-automatic-layout-v01190.js','assets/css/sc-lab-scientific-figure-intelligence-automatic-layout-v01190.css','contracts/scientific-figure-intelligence-automatic-layout-v01190.schema.json','contracts/scientific-figure-intelligence-automatic-layout-policy-v01190.json');
foreach($files as $f){ if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);} }
$php=file_get_contents($root.'/includes/class-sc-lab-scientific-figure-intelligence-automatic-layout-v01190.php');
foreach(array("const VERSION='0.119.0'","apiRouteCount'=>21","automaticScientificEncodingChanges'=>false","scientificValidityCertified'=>false") as $needle){if(strpos($php,$needle)===false){fwrite(STDERR,"ASSERT $needle\n");exit(1);}}
echo "PASS - Lab v0.119.0 WordPress scientific figure intelligence assertions\n";
