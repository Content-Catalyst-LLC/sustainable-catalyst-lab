<?php
$root=dirname(__DIR__);$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array('Version: 0.135.15.0','class-sc-lab-graph-studio-verification-artifacts-v0135150.php','0.135.15.0');foreach($checks as $x){if(strpos($main,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}
foreach(array('graph-studio-verification-artifacts-v0135150','project-workspace-verification-artifacts-v0135150','sc-lab-graph-studio-verification-artifacts-v0135150') as $x){if(strpos($plugin,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}echo "PASS - v0.135.15.0 PHP integration\n";
