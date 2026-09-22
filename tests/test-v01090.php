<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$bridge=file_get_contents($root.'/includes/class-sc-lab-platform-core-v3-visual-scene-v01090.php');
function ok($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL: $msg\n");exit(1);}echo "PASS: $msg\n";}
ok(strpos($main,'Version: 0.109.0')!==false,'plugin header identifies 0.109.0');
ok(strpos($main,'class-sc-lab-platform-core-v3-visual-scene-v01090.php')!==false,'v0.109 visual-scene class is loaded');
ok(strpos($bridge,"MINIMUM_CORE_RELEASE = '3.0.0'")!==false,'minimum Core release remains 3.0.0');
ok(strpos($bridge,'labIsScientificRenderingAuthority')!==false,'Lab rendering authority boundary is explicit');
ok(strpos($bridge,'coreIsRendererNeutral')!==false,'Core renderer-neutral boundary is explicit');
ok(strpos($bridge,'automaticVisualTruthInference')!==false,'automatic visual truth inference remains disabled');
ok(strpos($bridge,'automaticUncertaintyInference')!==false,'automatic uncertainty inference remains disabled');
ok(strpos($plugin,'platformCoreV3VisualScene')!==false,'release console exposes v0.109 visual-scene health');
