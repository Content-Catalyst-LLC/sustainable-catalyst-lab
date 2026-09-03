<?php
function must($cond,$message){if(!$cond){fwrite(STDERR,"FAIL - $message\n");exit(1);}echo "PASS - $message\n";}
$root=dirname(__DIR__);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$runtime=file_get_contents($root.'/includes/class-sc-lab-scientific-data-binding-v0750.php');
$template=file_get_contents($root.'/templates/lab-app.php');
must(strpos($bootstrap,'Version: 0.75.0')!==false,'plugin header is v0.75.0');
must(strpos($bootstrap,"SC_LAB_RELEASE_VERSION', '0.75.0")!==false,'release marker is v0.75.0');
must(strpos($bootstrap,'SC_Lab_Scientific_Data_Binding_V0750::init();')!==false,'v0.75 WordPress runtime is initialized');
must(strpos($runtime,"/visualization/v0750/health")!==false && strpos($runtime,"/visualization/v0750/schema")!==false,'v0.75 health/schema routes are registered');
must(strpos($runtime,"scientific-data-binding-ready")!==false,'v0.75 health state is explicit');
must(strpos($runtime,"surfaceInterpolation'=>false")!==false && strpos($runtime,"arbitraryCode'=>false")!==false,'scientific binding boundaries are explicit');
must(strpos($plugin,"scientific-data-binding-v0750")!==false && strpos($plugin,"graph-studio-v0750")!==false,'v0.75 assets are wired');
must(strpos($plugin,"engineVersion'=>'2.2.0'")!==false && strpos($plugin,"surface4dProjectDataBinding'=>true")!==false,'localized engine identity is v0.75');
must(strpos($template,'DATASET → TRANSFORM → BIND')!==false && strpos($template,'data-gs-v0750-pipeline')!==false,'Graph Studio exposes data-binding pipeline controls');
must(strpos($template,'Project dataset · point projection')!==false,'Graph Studio exposes project-data 4D mode');
