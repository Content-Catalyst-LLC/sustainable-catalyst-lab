<?php
$root=dirname(__DIR__); $m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??'')!=='0.133.0') exit(1);
if(($m['statisticalAssumptionDiagnosticIntelligenceVersion']??'')!=='0.133.0') exit(1);
if(($m['v01330RequiredRouteCount']??0)!==45) exit(1);
foreach(array('contracts/statistical-assumption-diagnostic-intelligence-v01330.schema.json','contracts/statistical-assumption-diagnostic-intelligence-policy-v01330.json','includes/class-sc-lab-statistical-assumption-diagnostic-intelligence-v01330.php','assets/js/modules/statistical-assumption-diagnostic-intelligence-v01330.js','assets/css/sc-lab-statistical-assumption-diagnostic-intelligence-v01330.css') as $p){if(!is_file($root.'/'.$p))exit(1);} echo "PASS - Lab v0.133.0 WordPress Statistical Assumption & Diagnostic Intelligence contract\n";
