<?php
define('ABSPATH',__DIR__);if (!function_exists('add_action')) { function add_action() {} }
$root=dirname(__DIR__);require_once $root.'/includes/class-sc-lab-genetics-genomics-rest-v0240.php';require_once $root.'/includes/class-sc-lab-genomics-production-v0241.php';
$h=SC_Lab_Genomics_Production_V0241::health_payload();if(!$h['ok']||$h['methodCount']!==48||$h['benchmarkCount']!==48||$h['categoryCount']!==8)exit(1);
echo "Lab v0.24.1 PHP tests passed: production health ready and 48/48/8 contract preserved.\n";
