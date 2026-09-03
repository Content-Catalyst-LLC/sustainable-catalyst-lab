<?php
$root=dirname(__DIR__);
function need($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL - $msg\n");exit(1);}echo "PASS - $msg\n";}
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$wp=file_get_contents($root.'/includes/class-sc-lab-scientific-visualization-engine-v0740.php');
$template=file_get_contents($root.'/templates/lab-app.php');
need(strpos($bootstrap,'Version: 0.74.0')!==false,'plugin header is v0.74.0');
need(strpos($bootstrap,"SC_LAB_RELEASE_VERSION', '0.74.0'")!==false,'release marker is v0.74.0');
need(strpos($bootstrap,'SC_Lab_Scientific_Visualization_Engine_V0740::init()')!==false,'v0.74 WordPress runtime is initialized');
need(strpos($wp,"'/visualization/v0740/health'")!==false && strpos($wp,"'/visualization/v0740/schema'")!==false,'v0.74 health/schema routes are registered');
need(strpos($wp,"'advanced-2d-plot-grammar-ready'")!==false,'v0.74 health state is explicit');
need(strpos($wp,"'polarRadar'=>false")!==false && strpos($wp,"'dualAxis'=>false")!==false,'coordinate-system boundaries are explicit');
need(strpos($plugin,"'scientific-visualization-engine-v0740'")!==false && strpos($plugin,"'graph-studio-v0740'")!==false,'v0.74 assets are wired');
need(strpos($template,'VISUALIZE / GRAPH STUDIO / v0.74.0')!==false,'Graph Studio interface identity upgraded');
