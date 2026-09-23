<?php
$root=dirname(__DIR__); $m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??'')!=='0.132.0') exit(1);
if(($m['methodSelectionIntelligenceVersion']??'')!=='0.132.0') exit(1);
if(($m['v01320RequiredRouteCount']??0)!==37) exit(1);
foreach(array('contracts/method-selection-intelligence-v01320.schema.json','contracts/method-selection-intelligence-policy-v01320.json','includes/class-sc-lab-method-selection-intelligence-v01320.php','assets/js/modules/method-selection-intelligence-v01320.js','assets/css/sc-lab-method-selection-intelligence-v01320.css') as $p){if(!is_file($root.'/'.$p))exit(1);} echo "PASS - Lab v0.132.0 WordPress Method Selection Intelligence contract\n";
