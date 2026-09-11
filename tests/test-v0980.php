<?php
function must0980($cond,$message){if(!$cond){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$rest=file_get_contents(__DIR__.'/../includes/class-sc-lab-rest.php');
$template=file_get_contents(__DIR__.'/../templates/lab-app.php');
$module=file_get_contents(__DIR__.'/../includes/class-sc-lab-carbon-mrv-uncertainty-v0980.php');
must0980((bool)preg_match('/^ \* Version: 0\.98\.0$/m',$main),'plugin header v0.98.0');
must0980(strpos($main,'SC_Lab_Carbon_MRV_Uncertainty_V0980::init();')!==false,'uncertainty module initialized');
must0980(strpos($plugin,"sc-lab-carbon-mrv-uncertainty-v0980.css")!==false,'uncertainty CSS enqueued');
must0980(strpos($plugin,"'carbonMrvUncertainty'")!==false,'uncertainty browser config');
must0980(strpos($rest,'/carbon-nature/mrv/v1500/uncertainty/budget')!==false,'uncertainty budget proxy route');
must0980(strpos($rest,'/carbon-nature/mrv/v1500/uncertainty/change-detection')!==false,'detection proxy route');
must0980(strpos($rest,'/carbon-nature/mrv/v1500/uncertainty/detection-sample-size')!==false,'detection sample-size proxy route');
must0980(strpos($rest,'/carbon-nature/mrv/v1500/uncertainty/project-packet')!==false,'uncertainty project packet proxy route');
must0980(strpos($template,'data-mrv-v1500-root')!==false,'MRV Uncertainty & Detection workspace');
must0980(strpos($template,'Observed-change detection')!==false,'detection UI');
must0980(strpos($module,"const DOMAIN_VERSION='0.15.0';")!==false,'domain version');
must0980(strpos($module,'detectionEqualsVerification')!==false,'verification guardrail');
echo "PASS - Lab v0.98.0 / Carbon & Nature v0.15.0 PHP contracts\n";
