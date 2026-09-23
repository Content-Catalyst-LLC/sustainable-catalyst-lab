<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__.'/');
if (!defined('SC_LAB_DIR')) define('SC_LAB_DIR', dirname(__DIR__).'/');
if (!defined('SC_LAB_RELEASE_VERSION')) define('SC_LAB_RELEASE_VERSION','0.135.6');
function add_action($a,$b){} function register_rest_route($a,$b,$c){} function rest_ensure_response($x){return $x;}
require_once dirname(__DIR__).'/includes/class-sc-lab-reproducible-visual-analysis-sessions-v01356.php';
$h=SC_Lab_Reproducible_Visual_Analysis_Sessions_V01356::health(); $c=SC_Lab_Reproducible_Visual_Analysis_Sessions_V01356::catalog();
if (!$h['ok'] || $h['version']!=='0.135.6' || $h['apiRouteCount']!==52 || $h['eventTypeCount']!==12 || $h['sessionStateCount']!==4 || $h['checkpointKindCount']!==5 || $h['replayModeCount']!==3) { fwrite(STDERR,"v0.135.6 health contract failed\n"); exit(1); }
if ($c['interactionLineageIsNotScientificEvidence']!==true || $c['replayRequiresDeclaredReferences']!==true || $c['automaticScientificInference']!==false || $c['automaticEvidenceWeighting']!==false || $c['automaticCoreSubmission']!==false) { fwrite(STDERR,"v0.135.6 policy contract failed\n"); exit(1); }
echo "PASS - Lab v0.135.6 WordPress reproducible visual analysis sessions and interaction lineage contract\n";
