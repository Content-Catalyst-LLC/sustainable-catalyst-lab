<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$klass=file_get_contents($root.'/includes/class-sc-lab-visual-research-narrative-figure-composer-v01180.php');
$js=file_get_contents($root.'/assets/js/modules/visual-research-narrative-figure-composer-v01180.js');
$css=file_get_contents($root.'/assets/css/sc-lab-visual-research-narrative-figure-composer-v01180.css');
$checks=array(
 strpos($plugin,'Version: 0.118.0')!==false,
 strpos($plugin,'class-sc-lab-visual-research-narrative-figure-composer-v01180.php')!==false,
 strpos($klass,"const VERSION='0.118.0'")!==false,
 strpos($klass,'automaticScientificConclusionGeneration')!==false,
 strpos($klass,'automaticFigureMutation')!==false,
 strpos($klass,'automaticCaptionInference')!==false,
 strpos($js,"VERSION='0.118.0'")!==false,
 strpos($css,'.sc-narrative1180')!==false
);
foreach($checks as $i=>$ok){if(!$ok){fwrite(STDERR,"FAIL v0.118 WP assertion $i\n");exit(1);}}
echo "PASS - v0.118.0 WordPress assertions\n";
