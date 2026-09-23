<?php
$root=dirname(__DIR__); $m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??'')!=='0.130.0') exit(1);
if(($m['scientificResearchProjectStudioVersion']??'')!=='0.130.0') exit(1);
if(($m['v01300RequiredRouteCount']??0)!==32) exit(1);
foreach(array('contracts/scientific-research-project-studio-v01300.schema.json','contracts/scientific-research-project-studio-policy-v01300.json','includes/class-sc-lab-scientific-research-project-studio-v01300.php','assets/js/modules/scientific-research-project-studio-v01300.js','assets/css/sc-lab-scientific-research-project-studio-v01300.css') as $p){if(!is_file($root.'/'.$p))exit(1);} echo "PASS - Lab v0.130.0 WordPress project-studio contract\n";
