<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$klass=file_get_contents($root.'/includes/class-sc-lab-advanced-3d-4d-scientific-visualization-v01170.php');
$js=file_get_contents($root.'/assets/js/modules/advanced-3d-4d-scientific-visualization-v01170.js');
$css=file_get_contents($root.'/assets/css/sc-lab-advanced-3d-4d-scientific-visualization-v01170.css');
$checks=array(strpos($plugin,'Version: 0.117.0')!==false,strpos($plugin,'class-sc-lab-advanced-3d-4d-scientific-visualization-v01170.php')!==false,strpos($klass,"const VERSION='0.117.0'")!==false,strpos($klass,'automaticGeometryInference')!==false,strpos($klass,'automaticTriangulation')!==false,strpos($js,"VERSION='0.117.0'")!==false,strpos($css,'.sc-advanced-scene1170')!==false);
foreach($checks as $i=>$ok){if(!$ok){fwrite(STDERR,"FAIL v0.117 WP assertion $i\n");exit(1);}}
echo "PASS - v0.117.0 WordPress assertions\n";
