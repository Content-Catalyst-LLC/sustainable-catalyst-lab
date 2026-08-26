<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$feature=file_get_contents($root.'/includes/class-sc-lab-advanced-visualization-front-door-v0710.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$recovery=file_get_contents($root.'/assets/js/sc-lab-production-stability-v0266.js');
$checks=array(
 'Plugin header reports v0.71.0'=>strpos($main,'Version: 0.71.0')!==false,
 'Release constant reports v0.71.0'=>strpos($main,"SC_LAB_RELEASE_VERSION', '0.71.0")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($main,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
 'v0.71 feature class initialized'=>strpos($main,'SC_Lab_Advanced_Visualization_Front_Door_V0710::init()')!==false,
 'v0.71 stylesheet enqueued'=>strpos($plugin,'sc-lab-advanced-visualization-front-door-v0710')!==false,
 'v0.71 browser module enqueued'=>strpos($plugin,"'advanced-visualization-front-door-v0710'")!==false,
 '4D visualization front door present'=>strpos($template,'data-v0710-visualizer')!==false,
 'W hyperslice control present'=>strpos($template,'data-v0710-w')!==false,
 'XW rotation control present'=>strpos($template,'data-v0710-xw')!==false,
 'YW rotation control present'=>strpos($template,'data-v0710-yw')!==false,
 'Illustrative boundary visible'=>strpos($template,'This front-door visualization is an illustrative scientific interface demonstration.')!==false,
 'Front door does not require compute'=>strpos($template,'No compute required')!==false,
 'Transient compute title is reconnecting'=>strpos($recovery,"kind==='compute'?'Compute reconnecting'")!==false,
 'Retry backoff starts at five seconds'=>strpos($recovery,'const delays=[5000,10000,20000,40000,60000]')!==false,
 'Persistent compute failure escalates'=>strpos($recovery,"state.backendFailures<3")!==false,
 'Health declares browser rendering'=>strpos($feature,"'browserRendered'=>true")!==false,
 'Health declares 4 represented dimensions'=>strpos($feature,"'dimensionsRepresented'=>4")!==false,
 'Health preserves scientific boundary'=>strpos($feature,"'scientificBoundary'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
