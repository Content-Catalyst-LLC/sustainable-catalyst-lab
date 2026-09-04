<?php
function must0850($ok,$m){if(!$ok){fwrite(STDERR,"FAIL - $m\n");exit(1);}echo "PASS - $m\n";}
$root=dirname(__DIR__);$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$console=file_get_contents($root.'/assets/js/modules/release-console-v0821.js');$integrity=file_get_contents($root.'/includes/class-sc-lab-integrity-v02632.php');$browser=file_get_contents($root.'/assets/js/modules/webgl2-scientific-renderer-v0850.js');
must0850(strpos($main,'Version: 0.85.0')!==false,'plugin header v0.85.0');
must0850(strpos($main,'class-sc-lab-webgl2-scientific-renderer-v0850.php')!==false,'v0.85 WordPress module wired');
must0850(strpos($plugin,"'webgl2-scientific-renderer-v0850'")!==false,'WebGL2 scientific renderer enqueued');
must0850(strpos($plugin,"'graph-studio-v0850'")!==false,'Graph Studio v0.85 integration enqueued');
must0850(strpos($tpl,'data-gs-v0850-canvas')!==false,'Graph Studio WebGL2 canvas present');
must0850(strpos($console,"visualization/v0850/health")!==false,'Release Console reports v0.85 visualization engine');
must0850(strpos($integrity,'SC_Lab_WebGL2_Scientific_Renderer_V0850::ENGINE_VERSION')!==false,'runtime integrity reports v0.85 visualization engine');
must0850(strpos($browser,'getContext(\'webgl2\'')!==false,'browser runtime creates real WebGL2 context');
must0850(strpos($browser,'drawElementsInstanced')!==false && strpos($browser,'drawArraysInstanced')!==false,'browser runtime contains instanced GPU draw paths');
must0850(strpos($browser,'readPixels')!==false && strpos($browser,'FRAMEBUFFER')!==false,'browser runtime contains framebuffer picking path');
