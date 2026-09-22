<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$class=file_get_contents($root.'/includes/class-sc-lab-advanced-statistical-uncertainty-graphics-v01150.php');
$js=file_get_contents($root.'/assets/js/modules/advanced-statistical-uncertainty-graphics-v01150.js');
$css=file_get_contents($root.'/assets/css/sc-lab-advanced-statistical-uncertainty-graphics-v01150.css');
$checks=array(
  strpos($plugin,'Version: 0.115.0')!==false,
  strpos($plugin,'class-sc-lab-advanced-statistical-uncertainty-graphics-v01150.php')!==false,
  strpos($class,"const VERSION='0.115.0'")!==false,
  strpos($class,"graphicTypeCount'=>16")!==false,
  strpos($class,"automaticScientificValidityCertification'=>false")!==false,
  strpos($js,"VERSION='0.115.0'")!==false,
  strpos($js,'scientificValidityCertified:false')!==false,
  strpos($css,'.sc-stat1150-host')!==false
);
foreach($checks as $i=>$ok){ if(!$ok){fwrite(STDERR,'FAIL v0.115 PHP assertion '.($i+1)."\n");exit(1);} }
echo "PASS - v0.115.0 WordPress statistical graphics assertions\n";
