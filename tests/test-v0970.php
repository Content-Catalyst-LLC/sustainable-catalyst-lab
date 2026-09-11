<?php
function must0970($cond,$message){if(!$cond){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$rest=file_get_contents(__DIR__.'/../includes/class-sc-lab-rest.php');
$template=file_get_contents(__DIR__.'/../templates/lab-app.php');
$module=file_get_contents(__DIR__.'/../includes/class-sc-lab-carbon-mrv-monitoring-v0970.php');
must0970((bool)preg_match('/^ \* Version: 0\.97\.0$/m',$main),'plugin header v0.97.0');
must0970(strpos($main,'SC_Lab_Carbon_MRV_Monitoring_V0970::init();')!==false,'monitoring module initialized');
must0970(strpos($plugin,"sc-lab-carbon-mrv-monitoring-v0970.css")!==false,'monitoring CSS enqueued');
must0970(strpos($plugin,"'carbonMrvMonitoring'")!==false,'monitoring browser config');
must0970(strpos($rest,'/carbon-nature/mrv/v1400/monitoring/sample-size')!==false,'sample-size proxy route');
must0970(strpos($rest,'/carbon-nature/mrv/v1400/monitoring/strata-allocation')!==false,'allocation proxy route');
must0970(strpos($rest,'/carbon-nature/mrv/v1400/monitoring/project-packet')!==false,'monitoring packet proxy route');
must0970(strpos($template,'data-mrv-v1400-root')!==false,'Monitoring Plan & Sampling Designer workspace');
must0970(strpos($template,'Precision-based sample-size planning')!==false,'sample-size UI');
must0970(strpos($module,"const DOMAIN_VERSION='0.14.0';")!==false,'domain version');
must0970(strpos($module,'automaticCoordinateGeneration')!==false,'coordinate guardrail');
echo "PASS - Lab v0.97.0 / Carbon & Nature v0.14.0 PHP contracts\n";
