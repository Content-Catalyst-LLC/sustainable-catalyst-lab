<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$binding=file_get_contents($root.'/assets/js/modules/graph-studio-live-binding-v013584.js');
if (strpos($plugin,"'graph-studio-live-binding-v013584'")===false) {fwrite(STDERR,"v0.135.8.4 module not enqueued\n");exit(1);}
if (strpos($main,'class-sc-lab-graph-studio-live-binding-v013584.php')===false) {fwrite(STDERR,"v0.135.8.4 REST class not loaded\n");exit(1);}
foreach (array('scLabGraphStudioBindingV013584','LIVE PROJECT BINDING','PROVENANCE EXPLORER','presentationStateOnly:true') as $needle) if (strpos($binding,$needle)===false) {fwrite(STDERR,"missing binding contract: $needle\n");exit(1);}
if (strpos($binding,"relationFilter")===false || strpos($binding,"upstream")===false || strpos($binding,"downstream")===false) {fwrite(STDERR,"provenance exploration contract incomplete\n");exit(1);}
echo "PASS - Lab v0.135.8.4 live binding / persistence / provenance exploration contract\n";
