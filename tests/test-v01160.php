<?php
$root=dirname(__DIR__);
$required=array(
 'includes/class-sc-lab-interactive-scientific-dashboards-v01160.php',
 'assets/js/modules/interactive-scientific-dashboards-v01160.js',
 'assets/css/sc-lab-interactive-scientific-dashboards-v01160.css',
 'contracts/interactive-scientific-dashboards-v01160.schema.json',
 'contracts/interactive-scientific-dashboards-policy-v01160.json',
);
foreach($required as $rel){ if(!is_file($root.'/'.$rel)){fwrite(STDERR,"FAIL missing $rel\n");exit(1);} }
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
if(strpos($main,'Version: 0.116.0')===false || strpos($main,'class-sc-lab-interactive-scientific-dashboards-v01160.php')===false){fwrite(STDERR,"FAIL v0.116 plugin identity/wiring\n");exit(1);}
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
foreach(array('interactive-scientific-dashboards-v01160','sc-lab-interactive-scientific-dashboards-v01160.css','interactiveScientificDashboards') as $needle){ if(strpos($plugin,$needle)===false){fwrite(STDERR,"FAIL missing plugin wiring: $needle\n");exit(1);} }
echo "PASS - Lab v0.116.0 WordPress interactive scientific dashboards assertions\n";
