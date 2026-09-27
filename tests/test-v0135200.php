<?php
define('ABSPATH', __DIR__); class WP_REST_Server { const READABLE='GET'; }
function add_action($a,$b){} function register_rest_route($a,$b,$c){} function __return_true(){return true;} function rest_ensure_response($x){return $x;}
require __DIR__.'/../includes/class-sc-lab-graph-studio-review-closure-v0135200.php';
$h=SC_Lab_Graph_Studio_Review_Closure_V0135200::health();$a=SC_Lab_Graph_Studio_Review_Closure_V0135200::acceptance();
if(($h['version']??'')!=='0.135.20.0'||empty($h['reviewClosurePackages'])){fwrite(STDERR,"health failed\n");exit(1);}if(($a['automaticScientificValidity']??true)!==false||($a['automaticPublicationAcceptance']??true)!==false||($a['fullGraphRedraw']??true)!==false){fwrite(STDERR,"acceptance failed\n");exit(1);}echo "PASS: v0.135.20.0 PHP integration\n";
