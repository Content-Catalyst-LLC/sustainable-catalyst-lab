<?php
define('ABSPATH',__DIR__);if (!function_exists('add_action')) { function add_action() {} }
$root=dirname(__DIR__);require_once $root.'/includes/class-sc-lab-genomic-visualization-rest-v0242.php';$c=SC_Lab_Genomic_Visualization_REST_V0242::contract();
if(count($c['modes'])!==8||count($c['analysisMethods'])!==8||count($c['benchmarks'])!==8)exit(1);
foreach($c['benchmarks'] as $b)if(SC_Lab_Genomic_Visualization_REST_V0242::execute($b['methodId'],$b['inputs'])['value']!==$b['expected']){fwrite(STDERR,"FAIL ".$b['methodId']."\n");exit(1);}
echo "Lab v0.24.2 PHP tests passed: 8 modes, 8 methods, 8 benchmarks.\n";
