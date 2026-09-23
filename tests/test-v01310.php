<?php
$root=dirname(__DIR__); $m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??'')!=='0.131.0') exit(1);
if(($m['researchQuestionHypothesisWorkspaceVersion']??'')!=='0.131.0') exit(1);
if(($m['v01310RequiredRouteCount']??0)!==33) exit(1);
foreach(array('contracts/research-question-hypothesis-workspace-v01310.schema.json','contracts/research-question-hypothesis-workspace-policy-v01310.json','includes/class-sc-lab-research-question-hypothesis-workspace-v01310.php','assets/js/modules/research-question-hypothesis-workspace-v01310.js','assets/css/sc-lab-research-question-hypothesis-workspace-v01310.css') as $p){if(!is_file($root.'/'.$p))exit(1);} echo "PASS - Lab v0.131.0 WordPress research-question/hypothesis contract\n";
