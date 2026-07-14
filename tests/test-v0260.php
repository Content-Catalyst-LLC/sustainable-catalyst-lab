<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$admin=file_get_contents($root.'/includes/class-sc-lab-admin.php');
$core0260=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0260.php');
$coreCurrent=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'current version retains 0.26 series'=>strpos($main,'Version: 0.26.1')!==false,
 'historical v0260 class retained'=>strpos($core0260,'SC_Lab_Python_Compute_Core_V0260')!==false,
 'HMAC signing retained'=>strpos($coreCurrent,'hash_hmac')!==false,
 'core run route retained'=>strpos($coreCurrent,'/compute/core/run')!==false,
 'signing setting retained'=>strpos($admin,'compute_signing_secret')!==false,
 'backend main'=>is_file($root.'/backend/app/main.py'),
 'compute schema'=>is_file($root.'/contracts/compute-request-v0260.schema.json'),
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}echo "PASS: $label\n";}
