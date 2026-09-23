<?php
$root=dirname(__DIR__);
$files=array("contracts/competing-model-hypothesis-analysis-v01350.schema.json","contracts/competing-model-hypothesis-analysis-policy-v01350.json","includes/class-sc-lab-competing-model-hypothesis-analysis-v01350.php","assets/js/modules/competing-model-hypothesis-analysis-v01350.js","assets/css/sc-lab-competing-model-hypothesis-analysis-v01350.css");
foreach($files as $f){if(!is_file($root."/".$f)){fwrite(STDERR,"MISSING $f\n");exit(1);}}
$php=file_get_contents($root."/includes/class-sc-lab-competing-model-hypothesis-analysis-v01350.php");
foreach(array("const VERSION='0.135.0'","apiRouteCount'=>49","automaticWinnerSelection'=>false","determineTruth'=>false") as $n){if(strpos($php,$n)===false){fwrite(STDERR,"ASSERT $n\n");exit(1);}}
echo "PASS - v0.135 WordPress assertions\n";
