<?php
function must0880($ok,$m){if(!$ok){fwrite(STDERR,"FAIL - $m\n");exit(1);}echo "PASS - $m\n";}
$root=dirname(__DIR__);$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$console=file_get_contents($root.'/assets/js/modules/release-console-v0821.js');$integrity=file_get_contents($root.'/includes/class-sc-lab-integrity-v02632.php');$browser=file_get_contents($root.'/assets/js/modules/advanced-scientific-scene-v0880.js');
must0880(strpos($main,'Version: 0.88.0')!==false,'plugin header v0.88.0');
must0880(strpos($main,'class-sc-lab-advanced-scientific-scene-v0880.php')!==false,'v0.88 WordPress module wired');
must0880(strpos($plugin,"'advanced-scientific-scene-v0880'")!==false,'Advanced 3D scene engine enqueued');
must0880(strpos($plugin,"'graph-studio-v0880'")!==false,'Graph Studio v0.88 integration enqueued');
must0880(strpos($tpl,'data-gs-v0880-canvas')!==false,'Graph Studio Advanced 3D canvas present');
must0880(strpos($console,"visualization/v0880/health")!==false,'Release Console reports v0.88 visualization engine');
must0880(strpos($integrity,'SC_Lab_Advanced_Scientific_Scene_V0880::ENGINE_VERSION')!==false,'runtime integrity reports v0.88 visualization engine');
must0880(strpos($browser,"createRenderPipeline")!==false && strpos($browser,"triangle-list")!==false && strpos($browser,"line-list")!==false && strpos($browser,"point-list")!==false,'browser runtime contains Advanced 3D GPU pipelines');
must0880(strpos($browser,'createThreeJSAdapter')!==false && strpos($browser,'Three.js runtime is not present')!==false,'Three.js adapter is explicit and local-runtime gated');
must0880(strpos($browser,'interactionCreatesObservation:false')!==false && strpos($browser,'arbitraryShaderSource:false')!==false,'scientific interaction and shader boundaries preserved');
