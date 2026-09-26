<?php
$root=dirname(__DIR__); $main=file_get_contents($root.'/sustainable-catalyst-lab.php'); $plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array('Version: 0.135.11.0','class-sc-lab-graph-studio-competing-paths-v0135110.php','graph-studio-competing-paths-v0135110','project-workspace-path-comparison-v0135110','0.135.11.0');
foreach($checks as $c){ if(strpos($main.$plugin,$c)===false){fwrite(STDERR,"FAIL: $c\n"); exit(1);} }
echo "PASS - v0.135.11.0 PHP integration\n";
