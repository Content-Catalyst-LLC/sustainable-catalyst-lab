<?php
$root=dirname(__DIR__); $main=file_get_contents($root.'/sustainable-catalyst-lab.php'); $plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array('Version: 0.135.13.0','class-sc-lab-graph-studio-review-resolution-v0135130.php','graph-studio-review-resolution-v0135130','project-workspace-review-resolution-v0135130','0.135.13.0');
foreach($checks as $c){ if(strpos($main.$plugin,$c)===false){fwrite(STDERR,"FAIL: $c\n"); exit(1);} }
echo "PASS - v0.135.13.0 PHP integration\n";
