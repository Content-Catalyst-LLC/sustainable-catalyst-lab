<?php
function must($cond,$message){if(!$cond){fwrite(STDERR,"FAIL - $message\n");exit(1);}echo "PASS - $message\n";}
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$runtime=file_get_contents($root.'/includes/class-sc-lab-large-data-visualization-v0760.php');$template=file_get_contents($root.'/templates/lab-app.php');
must(strpos($bootstrap,'Version: 0.76.0')!==false,'plugin header is v0.76.0');
must(strpos($bootstrap,"SC_LAB_RELEASE_VERSION', '0.76.0")!==false,'release marker is v0.76.0');
must(strpos($bootstrap,'SC_Lab_Large_Data_Visualization_V0760::init();')!==false,'v0.76 WordPress runtime is initialized');
must(strpos($runtime,'/visualization/v0760/health')!==false && strpos($runtime,'/visualization/v0760/schema')!==false,'v0.76 health/schema routes are registered');
must(strpos($runtime,'large-data-adaptive-rendering-ready')!==false,'v0.76 health state is explicit');
must(strpos($runtime,"'streaming'=>false")!==false && strpos($runtime,"'webgl'=>false")!==false && strpos($runtime,"'silentDataMutation'=>false")!==false,'large-data scientific boundaries are explicit');
must(strpos($plugin,'large-data-visualization-v0760')!==false && strpos($plugin,'graph-studio-v0760')!==false,'v0.76 assets are wired');
must(strpos($plugin,"engineVersion'=>'2.3.0'")!==false && strpos($plugin,"adaptiveRendering'=>true")!==false,'localized engine identity is v0.76');
must(strpos($template,'LARGE-DATA ADAPTIVE RENDERING')!==false && strpos($template,'data-gs-v0760-budget')!==false,'Graph Studio exposes adaptive rendering controls');
