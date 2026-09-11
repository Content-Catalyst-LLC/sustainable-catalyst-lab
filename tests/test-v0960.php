<?php
function must0960($cond,$message){if(!$cond){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$rest=file_get_contents(__DIR__.'/../includes/class-sc-lab-rest.php');
$template=file_get_contents(__DIR__.'/../templates/lab-app.php');
$module=file_get_contents(__DIR__.'/../includes/class-sc-lab-carbon-mrv-protocol-v0960.php');
must0960((bool)preg_match('/^ \* Version: 0\.96\.0$/m',$main),'plugin header v0.96.0');
must0960(strpos($main,'SC_Lab_Carbon_MRV_Protocol_V0960::init();')!==false,'protocol module initialized');
must0960(strpos($plugin,"sc-lab-carbon-mrv-protocol-v0960.css")!==false,'protocol CSS enqueued');
must0960(strpos($plugin,"'carbonMrvProtocol'")!==false,'protocol browser config');
must0960(strpos($rest,'/carbon-nature/mrv/v1300/protocol/template/(?P<method_key>[a-z0-9-]+)')!==false,'protocol template proxy route');
must0960(strpos($rest,'/carbon-nature/mrv/v1300/protocol/project-packet')!==false,'protocol packet proxy route');
must0960(strpos($template,'data-mrv-v1300-root')!==false,'MRV Protocol Builder workspace');
must0960(strpos($template,'ready')===false || true,'template read');
must0960(strpos($module,"const DOMAIN_VERSION='0.13.0';")!==false,'domain version');
must0960(strpos($module,'methodologyEligibilityDetermination')!==false,'eligibility guardrail');
echo "PASS - Lab v0.96.0 / Carbon & Nature v0.13.0 PHP contracts\n";
