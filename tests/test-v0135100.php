<?php
$root=dirname(__DIR__); $main=file_get_contents($root.'/sustainable-catalyst-lab.php'); $plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php'); $cls=file_get_contents($root.'/includes/class-sc-lab-graph-studio-path-analysis-v0135100.php');
$checks=array('Version: 0.135.10.0','class-sc-lab-graph-studio-path-analysis-v0135100.php','graph-studio-path-analysis-v0135100','project-workspace-research-context-v0135100','0.135.10.0');
foreach($checks as $c){ if(strpos($main.$plugin.$cls,$c)===false){fwrite(STDERR,"MISSING $c\n"); exit(1);} }
echo "PASS - v0.135.10.0 PHP integration\n";
