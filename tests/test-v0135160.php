<?php
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$checks=array('Version: 0.135.16.0','class-sc-lab-graph-studio-revision-impact-v0135160.php','0.135.16.0');foreach($checks as $x){if(strpos($main,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}
foreach(array('graph-studio-revision-impact-v0135160','project-workspace-revision-impact-v0135160','sc-lab-graph-studio-revision-impact-v0135160') as $x){if(strpos($plugin,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}echo "PASS - v0.135.16.0 PHP integration\n";
