<?php
if (!defined('ABSPATH')) { define('ABSPATH', __DIR__ . '/'); }
function add_action($a,$b){}
function register_rest_route($a,$b,$c){}
function __return_true(){return true;}
function rest_ensure_response($x){return $x;}
function plugin_dir_path($p){return dirname($p).'/';}
require_once __DIR__.'/../includes/class-sc-lab-platform-core-v3-scientific-investigation-v01110.php';
$schema=SC_Lab_Platform_Core_V3_Scientific_Investigation_V01110::schema();
$manifest=SC_Lab_Platform_Core_V3_Scientific_Investigation_V01110::manifest();
if ($schema['version']!=='0.111.0') { throw new Exception('version mismatch'); }
if ($schema['automaticCoreSubmission']!==false || $schema['automaticExecution']!==false) { throw new Exception('boundary mismatch'); }
if ($manifest['coreRunsScientificInvestigation']!==false || $manifest['coreDeterminesTruth']!==false) { throw new Exception('authority boundary mismatch'); }
echo "PASS - v0.111.0 WordPress scientific investigation bridge assertions\n";
