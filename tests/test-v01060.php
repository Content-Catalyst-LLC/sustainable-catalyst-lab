<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$ctx=file_get_contents($root.'/includes/class-sc-lab-platform-core-v3-research-context-v01060.php');
function ok($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL: $msg\n");exit(1);}echo "PASS: $msg\n";}
ok(strpos($main,'Version: 0.106.0')!==false,'plugin header identifies 0.106.0');
ok(strpos($main,'class-sc-lab-platform-core-v3-research-context-v01060.php')!==false,'v0.106 context class is loaded');
ok(strpos($ctx,"MINIMUM_CORE_RELEASE = '3.0.0'")!==false,'minimum Core release remains 3.0.0');
ok(strpos($ctx,'coreOwnsSessionRegistry')!==false,'Core session-registry ownership is explicit');
ok(strpos($ctx,'automaticCoreSubmission')!==false,'automatic Core submission remains disabled');
ok(strpos($plugin,'platformCoreV3ResearchContext')!==false,'release console exposes v0.106 context health');
