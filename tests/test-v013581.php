<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__.'/');
if (!function_exists('add_action')) { function add_action(...$args){} function register_rest_route(...$args){} function rest_ensure_response($x){return $x;} }
if (!defined('SC_LAB_DIR')) define('SC_LAB_DIR', dirname(__DIR__).'/');
require_once dirname(__DIR__).'/includes/class-sc-lab-graph-studio-canonical-runtime-v013581.php';
$h=SC_Lab_Graph_Studio_Canonical_Runtime_V013581::health();
if (!$h['ok'] || $h['version']!=='0.135.8.1' || $h['canonicalViewCount']!==8 || $h['isolatedCapabilityPanelCount']!==13 || $h['singleActiveResearchView']!==true || $h['scientificMutationFromNavigation']!==false) { fwrite(STDERR,"v0.135.8.1 canonical runtime health failed\n"); exit(1); }
$template=file_get_contents(dirname(__DIR__).'/templates/lab-app.php');
if (strpos($template,'EXPERIENCE v0.135.8.1')===false || strpos($template,'data-viz13581-canonical-runtime')===false) { fwrite(STDERR,"v0.135.8.1 template marker missing\n"); exit(1); }
$plugin=file_get_contents(dirname(__DIR__).'/includes/class-sc-lab-plugin.php');
if (strpos($plugin,'graph-studio-canonical-runtime-v013581')===false) { fwrite(STDERR,"v0.135.8.1 asset enqueue missing\n"); exit(1); }
echo "PASS - Lab v0.135.8.1 Graph Studio canonical runtime contract\n";
