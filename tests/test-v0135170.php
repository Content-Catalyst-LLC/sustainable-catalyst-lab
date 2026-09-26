<?php
$f=file_get_contents(__DIR__.'/../includes/class-sc-lab-graph-studio-review-reproduction-v0135170.php');foreach(array("0.135.17.0","reviewToReproductionBridge","automaticExecution'=>false","automaticVerificationOutcome'=>false","truthRanking'=>false") as $x){if(strpos($f,$x)===false){fwrite(STDERR,"missing $x\n");exit(1);}}echo "PASS - v0.135.17.0 PHP integration contract\n";
