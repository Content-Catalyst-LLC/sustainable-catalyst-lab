<?php
function must0990($cond,$message){if(!$cond){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$rest=file_get_contents(__DIR__.'/../includes/class-sc-lab-rest.php');
$template=file_get_contents(__DIR__.'/../templates/lab-app.php');
$module=file_get_contents(__DIR__.'/../includes/class-sc-lab-carbon-mrv-verification-ledger-v0990.php');
must0990((bool)preg_match('/^ \* Version: 0\.99\.0$/m',$main),'plugin header v0.99.0');
must0990(strpos($main,'SC_Lab_Carbon_MRV_Verification_Ledger_V0990::init();')!==false,'verification ledger initialized');
must0990(strpos($plugin,"sc-lab-carbon-mrv-verification-ledger-v0990.css")!==false,'verification ledger CSS enqueued');
must0990(strpos($plugin,"'carbonMrvVerificationLedger'")!==false,'verification ledger browser config');
must0990(strpos($rest,'/carbon-nature/mrv/v1600/verification-ledger/evidence-entry')!==false,'evidence entry proxy route');
must0990(strpos($rest,'/carbon-nature/mrv/v1600/verification-ledger/build')!==false,'ledger build proxy route');
must0990(strpos($rest,'/carbon-nature/mrv/v1600/verification-ledger/chain-check')!==false,'chain check proxy route');
must0990(strpos($rest,'/carbon-nature/mrv/v1600/verification-ledger/project-packet')!==false,'verification-record packet route');
must0990(strpos($template,'data-mrv-v1600-root')!==false,'verification evidence ledger workspace');
must0990(strpos($template,'Verification Evidence Ledger')!==false,'verification evidence title');
must0990(strpos($module,"const DOMAIN_VERSION='0.16.0';")!==false,'domain version');
must0990(strpos($module,'ledgerIntegrityEqualsExternalVerification')!==false,'external verification guardrail');
echo "PASS - Lab v0.99.0 / Carbon & Nature v0.16.0 PHP contracts\n";
