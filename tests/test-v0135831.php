<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$final=file_get_contents($root.'/assets/js/modules/graph-studio-bootstrap-finalization-v0135831.js');
$recovery=file_get_contents($root.'/assets/js/modules/graph-studio-recovery-v013583.js');
if (strpos($plugin,"'graph-studio-v0470'")===false) {fwrite(STDERR,"v0470 bootstrap not enqueued\n");exit(1);}
if (strpos($plugin,"'graph-studio-bootstrap-finalization-v0135831'")===false) {fwrite(STDERR,"finalizer not enqueued\n");exit(1);}
if (strpos($final,'Graph Studio ready')===false || strpos($final,'data-gs13582-host')===false || strpos($final,'data-gs13581-shell')===false) {fwrite(STDERR,"finalization contract incomplete\n");exit(1);}
if (strpos($recovery,'GraphStudioV0470?.currentGraph')===false) {fwrite(STDERR,"v0470 hydration bridge missing\n");exit(1);}
echo "PASS - Lab v0.135.8.3.1 bootstrap/hydration/finalization contract\n";
