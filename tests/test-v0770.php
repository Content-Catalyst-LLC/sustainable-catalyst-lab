<?php
function must($cond,$message){if(!$cond){fwrite(STDERR,"FAIL - $message\n");exit(1);}echo "PASS - $message\n";}
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$runtime=file_get_contents($root.'/includes/class-sc-lab-scientific-scene-v0770.php');$template=file_get_contents($root.'/templates/lab-app.php');
must(strpos($bootstrap,'Version: 0.77.0')!==false,'plugin header is v0.77.0');
must(strpos($bootstrap,"SC_LAB_RELEASE_VERSION', '0.77.0")!==false,'release marker is v0.77.0');
must(strpos($bootstrap,'SC_Lab_Scientific_Scene_V0770::init();')!==false,'v0.77 WordPress runtime is initialized');
must(strpos($runtime,'/visualization/v0770/health')!==false && strpos($runtime,'/visualization/v0770/schema')!==false,'v0.77 health/schema routes are registered');
must(strpos($runtime,'scientific-3d-scene-ready')!==false,'v0.77 health state is explicit');
must(strpos($runtime,"'webgl' => false")!==false && strpos($runtime,"'automaticTriangulation' => false")!==false && strpos($runtime,"'surfaceInterpolation' => false")!==false,'3D scientific boundaries are explicit');
must(strpos($plugin,'scientific-scene-engine-v0770')!==false && strpos($plugin,'graph-studio-v0770')!==false && strpos($plugin,'sc-lab-scientific-scene-v0770')!==false,'v0.77 assets are wired');
must(strpos($plugin,"'engineVersion'=>'2.4.0'")!==false && strpos($plugin,"'canvas3d'")!==false && strpos($plugin,"'scientificScene3d'=>true")!==false,'localized engine identity is v0.77');
must(strpos($template,'3D SCIENTIFIC SCENE')!==false && strpos($template,'data-gs-v0770-projection')!==false && strpos($template,'data-gs-v0770-faces')!==false && strpos($template,'data-gs-v0770-example-3d')!==false,'Graph Studio exposes governed 3D scene controls');
