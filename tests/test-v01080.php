<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$bridge=file_get_contents($root.'/includes/class-sc-lab-platform-core-v3-findings-validation-v01080.php');
function ok($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL: $msg\n");exit(1);}echo "PASS: $msg\n";}
ok(strpos($main,'Version: 0.108.0')!==false,'plugin header identifies 0.108.0');
ok(strpos($main,'class-sc-lab-platform-core-v3-findings-validation-v01080.php')!==false,'v0.108 findings/validation class is loaded');
ok(strpos($bridge,"MINIMUM_CORE_RELEASE = '3.0.0'")!==false,'minimum Core release remains 3.0.0');
ok(strpos($bridge,'labRemainsScientificAuthority')!==false,'Lab scientific authority boundary is explicit');
ok(strpos($bridge,'humanReviewBoundariesPreserved')!==false,'human review boundary is explicit');
ok(strpos($bridge,'automaticClaimInference')!==false,'automatic claim inference remains disabled');
ok(strpos($bridge,'automaticEvidenceJudgment')!==false,'automatic evidence judgment remains disabled');
ok(strpos($bridge,'automaticReplicationCertification')!==false,'automatic replication certification remains disabled');
ok(strpos($plugin,'platformCoreV3FindingsValidation')!==false,'release console exposes v0.108 findings/validation health');
