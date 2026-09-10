<?php
function must0870($ok,$m){if(!$ok){fwrite(STDERR,"FAIL - $m\n");exit(1);}echo "PASS - $m\n";}
$root=dirname(__DIR__);$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$console=file_get_contents($root.'/assets/js/modules/release-console-v0821.js');$integrity=file_get_contents($root.'/includes/class-sc-lab-integrity-v02632.php');$browser=file_get_contents($root.'/assets/js/modules/webgpu-scientific-renderer-v0870.js');
must0870(strpos($main,'Version: 0.87.0')!==false,'plugin header v0.87.0');
must0870(strpos($main,'class-sc-lab-webgpu-scientific-renderer-v0870.php')!==false,'v0.87 WordPress module wired');
must0870(strpos($plugin,"'webgpu-scientific-renderer-v0870'")!==false,'WebGPU renderer enqueued');
must0870(strpos($plugin,"'graph-studio-v0870'")!==false,'Graph Studio v0.87 integration enqueued');
must0870(strpos($tpl,'data-gs-v0870-canvas')!==false,'Graph Studio WebGPU canvas present');
must0870(strpos($console,"visualization/v0870/health")!==false,'Release Console reports v0.87 visualization engine');
must0870(strpos($integrity,'SC_Lab_WebGPU_Scientific_Renderer_V0870::ENGINE_VERSION')!==false,'runtime integrity reports v0.87 visualization engine');
must0870(strpos($browser,'navigator.gpu.requestAdapter')!==false,'browser runtime requests real WebGPU adapter');
must0870(strpos($browser,'createRenderPipeline')!==false && strpos($browser,'queue.submit')!==false,'browser runtime creates and submits WebGPU render pipeline');
must0870(strpos($browser,'createComputePipeline')!==false,'browser runtime creates governed WebGPU compute pipeline');
must0870(strpos($browser,'arbitraryWGSLSource:false')!==false,'browser runtime refuses arbitrary WGSL semantics');
