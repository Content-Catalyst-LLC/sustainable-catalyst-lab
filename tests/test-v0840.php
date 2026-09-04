<?php
function must0840($ok,$m){if(!$ok){fwrite(STDERR,"FAIL - $m\n");exit(1);}echo "PASS - $m\n";}
$root=dirname(__DIR__);$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$console=file_get_contents($root.'/assets/js/modules/release-console-v0821.js');$integrity=file_get_contents($root.'/includes/class-sc-lab-integrity-v02632.php');
must0840(strpos($main,'Version: 0.84.0')!==false,'plugin header v0.84.0');
must0840(strpos($main,'class-sc-lab-gpu-renderer-architecture-v0840.php')!==false,'v0.84 WordPress module wired');
must0840(strpos($plugin,"'gpu-renderer-architecture-v0840'")!==false,'GPU renderer browser architecture enqueued');
must0840(strpos($plugin,"'graph-studio-v0840'")!==false,'Graph Studio v0.84 integration enqueued');
must0840(strpos($tpl,'data-gs-v0840-detect')!==false,'Graph Studio GPU diagnostics controls present');
must0840(strpos($console,"visualization/v0840/health")!==false,'Release Console reports v0.84 visualization engine');
must0840(strpos($integrity,'SC_Lab_GPU_Renderer_Architecture_V0840::ENGINE_VERSION')!==false,'runtime integrity reports v0.84 visualization engine');
