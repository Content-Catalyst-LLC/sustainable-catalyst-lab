<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__ . '/');
function add_action($a,$b){} function register_rest_route($a,$b,$c){} function rest_ensure_response($x){return $x;}
define('SC_LAB_DIR', dirname(__DIR__) . '/'); define('SC_LAB_RELEASE_VERSION','0.135.3');
require_once dirname(__DIR__) . '/includes/class-sc-lab-multi-view-scientific-analysis-canvas-v01353.php';
$h=SC_Lab_Multi_View_Scientific_Analysis_Canvas_V01353::health();
if (!$h['ok'] || $h['version']!=='0.135.3' || $h['apiRouteCount']!==41 || $h['panelTypeCount']!==10 || $h['layoutModeCount']!==5 || $h['interactionChannelCount']!==8) { fwrite(STDERR,"v0.135.3 health contract failed\n"); exit(1); }
$c=SC_Lab_Multi_View_Scientific_Analysis_Canvas_V01353::catalog();
if ($c['selectionIsPresentationState']!==true || $c['filtersMutateSourceData']!==false || $c['automaticJoinInference']!==false || $c['automaticCoreSubmission']!==false) { fwrite(STDERR,"v0.135.3 policy contract failed\n"); exit(1); }
echo "PASS - Lab v0.135.3 WordPress multi-view scientific analysis canvas contract\n";
