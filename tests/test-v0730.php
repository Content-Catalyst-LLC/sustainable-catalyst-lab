<?php
$root=dirname(__DIR__);
$files=array(
 'Visualization Engine 2 PHP runtime'=>$root.'/includes/class-sc-lab-scientific-visualization-engine-v0730.php',
 'Visualization Engine 2 JS'=>$root.'/assets/js/modules/scientific-visualization-engine-v0730.js',
 'Graph Studio v0.73 runtime'=>$root.'/assets/js/modules/graph-studio-v0730.js',
 'Visualization Engine 2 CSS'=>$root.'/assets/css/sc-lab-scientific-visualization-engine-v0730.css',
 'Unified visualization schema'=>$root.'/contracts/scientific-visualization-v0730.schema.json',
 'Scientific figure v0.73 schema'=>$root.'/contracts/scientific-figure-v0730.schema.json',
 'Figure workspace v0.73 schema'=>$root.'/contracts/figure-workspace-v0730.schema.json',
 'Visualization Engine 2 backend'=>$root.'/backend/app/visualization_engine_v0730.py',
);
foreach($files as $label=>$file){if(!is_file($file)){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
if(strpos($plugin,"Version: 0.73.0")===false||strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.73.0")===false){fwrite(STDERR,"FAIL - plugin release identity\n");exit(1);}echo "PASS - plugin release identity\n";
$runtime=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
if(strpos($runtime,"scientific-visualization-engine-v0730")===false||strpos($runtime,"graph-studio-v0730")===false){fwrite(STDERR,"FAIL - runtime module wiring\n");exit(1);}echo "PASS - runtime module wiring\n";
$class=file_get_contents($root.'/includes/class-sc-lab-scientific-visualization-engine-v0730.php');
if(strpos($class,"/visualization/v0730/health")===false||strpos($class,"surface4dFirstClassFigure")===false){fwrite(STDERR,"FAIL - WordPress health/schema route contract\n");exit(1);}echo "PASS - WordPress health/schema route contract\n";
