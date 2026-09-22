<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$exec=file_get_contents($root.'/includes/class-sc-lab-platform-core-v3-execution-lineage-v01070.php');
function ok($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL: $msg\n");exit(1);}echo "PASS: $msg\n";}
ok(strpos($main,'Version: 0.107.0')!==false,'plugin header identifies 0.107.0');
ok(strpos($main,'class-sc-lab-platform-core-v3-execution-lineage-v01070.php')!==false,'v0.107 execution-lineage class is loaded');
ok(strpos($exec,"MINIMUM_CORE_RELEASE = '3.0.0'")!==false,'minimum Core release remains 3.0.0');
ok(strpos($exec,'labIsScientificExecutionAuthority')!==false,'Lab scientific-execution authority is explicit');
ok(strpos($exec,'coreRecordsExecutionReferencesAndLineage')!==false,'Core execution-lineage role is explicit');
ok(strpos($exec,'automaticCoreSubmission')!==false,'automatic Core submission remains disabled');
ok(strpos($plugin,'platformCoreV3ExecutionLineage')!==false,'release console exposes v0.107 execution-lineage health');
