<?php
function must($cond,$message){if(!$cond){fwrite(STDERR,"FAIL - $message\n");exit(1);}echo "PASS - $message\n";}
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$runtime=file_get_contents($root.'/includes/class-sc-lab-time-parameter-space-v0780.php');$template=file_get_contents($root.'/templates/lab-app.php');
must(strpos($bootstrap,'Version: 0.78.0')!==false,'plugin header is v0.78.0');
must(strpos($bootstrap,"SC_LAB_RELEASE_VERSION', '0.78.0")!==false,'release marker is v0.78.0');
must(strpos($bootstrap,'SC_Lab_Time_Parameter_Space_V0780::init();')!==false,'v0.78 WordPress runtime is initialized');
must(strpos($runtime,'/visualization/v0780/health')!==false && strpos($runtime,'/visualization/v0780/schema')!==false,'v0.78 health/schema routes are registered');
must(strpos($runtime,'4d-time-parameter-space-ready')!==false,'v0.78 health state is explicit');
must(strpos($runtime,"'syntheticFrames' => false")!==false && strpos($runtime,"'temporalInterpolation' => false")!==false && strpos($runtime,"'parameterInterpolation' => false")!==false && strpos($runtime,"'surfaceInterpolation' => false")!==false,'4D/time/parameter scientific boundaries are explicit');
must(strpos($plugin,'time-parameter-space-v0780')!==false && strpos($plugin,'graph-studio-v0780')!==false && strpos($plugin,'sc-lab-time-parameter-space-v0780')!==false,'v0.78 assets are wired');
must(strpos($plugin,"'engineVersion'=>'2.5.0'")!==false && strpos($plugin,"'timeStatePlayback'=>true")!==false && strpos($plugin,"'parameterSweep'=>true")!==false,'localized engine identity is v0.78');
must(strpos($template,'4D / TIME / PARAMETER SPACE')!==false && strpos($template,'data-gs-v0780-mode')!==false && strpos($template,'data-gs-v0780-xw')!==false && strpos($template,'data-gs-v0780-example-state')!==false,'Graph Studio exposes governed 4D state-space controls');
