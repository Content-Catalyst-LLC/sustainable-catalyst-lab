<?php
$root=dirname(__DIR__);$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array('Version: 0.135.14.0','class-sc-lab-graph-studio-review-audit-v0135140.php','0.135.14.0');foreach($checks as $x){if(strpos($main,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}
foreach(array('graph-studio-review-audit-v0135140','project-workspace-review-audit-v0135140','sc-lab-graph-studio-review-audit-v0135140') as $x){if(strpos($plugin,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}echo "PASS - v0.135.14.0 PHP integration\n";
