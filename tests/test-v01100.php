<?php
$root=dirname(__DIR__);$fail=0;
function ok($c,$m){global $fail;if(!$c){fwrite(STDERR,"FAIL: $m\n");$fail=1;}else{echo "PASS: $m\n";}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');$bridge=file_get_contents($root.'/includes/class-sc-lab-platform-core-v3-scholarly-package-v01100.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
ok(strpos($main,'Version: 0.110.0')!==false,'plugin header is v0.110.0');
ok(strpos($main,'class-sc-lab-platform-core-v3-scholarly-package-v01100.php')!==false,'v0.110 scholarly package class is loaded');
ok(strpos($bridge,"const VERSION='0.110.0'")!==false,'v0.110 WordPress bridge version');
ok(strpos($bridge,"coreCertifiesReproducibility'=>false")!==false,'WordPress bridge does not certify reproducibility');
ok(strpos($bridge,"corePublishesPackages'=>false")!==false,'WordPress bridge does not publish packages');
ok(strpos($plugin,"'platformCoreV3ScholarlyPackage'")!==false,'release console exposes v0.110 scholarly package surface');
exit($fail);
