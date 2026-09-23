<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__ . '/');
function add_action($a,$b){} function register_rest_route($a,$b,$c){} function rest_ensure_response($x){return $x;}
define('SC_LAB_DIR', dirname(__DIR__) . '/'); define('SC_LAB_RELEASE_VERSION','0.135.2');
require_once dirname(__DIR__) . '/includes/class-sc-lab-model-architecture-provenance-graphs-v01352.php';
$h=SC_Lab_Model_Architecture_Provenance_Graphs_V01352::health();
if (!$h['ok'] || $h['version']!=='0.135.2' || $h['apiRouteCount']!==40 || $h['nodeTypeCount']!==20 || $h['edgeTypeCount']!==18) { fwrite(STDERR,"v0.135.2 health contract failed\n"); exit(1); }
$c=SC_Lab_Model_Architecture_Provenance_Graphs_V01352::catalog();
if ($c['fabricatedScientificValues']!==false || $c['automaticModelInference']!==false || $c['automaticCoreSubmission']!==false) { fwrite(STDERR,"v0.135.2 policy contract failed\n"); exit(1); }
echo "PASS - Lab v0.135.2 WordPress model architecture/provenance contract\n";
