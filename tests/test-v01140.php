<?php
$root=dirname(__DIR__);
$required=array('includes/class-sc-lab-scientific-visualization-design-system-v01140.php','contracts/scientific-visualization-design-system-v01140.schema.json','contracts/scientific-visualization-design-system-policy-v01140.json','assets/js/modules/scientific-visualization-design-system-v01140.js','assets/css/sc-lab-scientific-visualization-design-system-v01140.css');
foreach($required as $r){if(!is_file($root.'/'.$r)){fwrite(STDERR,"MISSING $r\n");exit(1);}}
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php'); if(strpos($plugin,'Version: 0.114.0')===false){fwrite(STDERR,"release version mismatch\n");exit(1);} 
$cls=file_get_contents($root.'/includes/class-sc-lab-scientific-visualization-design-system-v01140.php'); foreach(array('publicationGradeRendering','vectorFirst','accessibilityWithoutColor') as $needle){if(strpos($cls,$needle)===false){fwrite(STDERR,"missing $needle\n");exit(1);}}
echo "PASS - Lab v0.114.0 WordPress design-system assertions\n";
