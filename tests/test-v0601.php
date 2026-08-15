<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-beta-field-diagnostics-v0601.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.60.1 beta diagnostics PHP class'=>is_file($root.'/includes/class-sc-lab-beta-field-diagnostics-v0601.php'),
 'v0.60.1 backend module'=>is_file($root.'/backend/app/beta_field_diagnostics_v0601.py'),
 'v0.60.1 backend regression test'=>is_file($root.'/backend/tests/test_beta_field_diagnostics_v0601.py'),
 'v0.60.1 JS module'=>is_file($root.'/assets/js/modules/beta-field-diagnostics-v0601.js'),
 'v0.60.1 stylesheet'=>is_file($root.'/assets/css/sc-lab-beta-field-diagnostics-v0601.css'),
 'Runtime snapshot schema'=>is_file($root.'/contracts/beta-runtime-snapshot-v0601.schema.json'),
 'Integration soak schema'=>is_file($root.'/contracts/beta-integration-soak-v0601.schema.json'),
 'Diagnostic packet schema'=>is_file($root.'/contracts/beta-field-diagnostic-packet-v0601.schema.json'),
 'Diagnostics policy contract'=>is_file($root.'/contracts/beta-field-diagnostics-policy-v0601.json'),
 'WordPress plugin header reports v0.60.1'=>preg_match('/^\s*\*\s*Version:\s*0\.60\.1\s*$/m',$bootstrap)===1,
 'Release constant reports v0.60.1'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.60.1')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes beta diagnostics'=>strpos($bootstrap,'SC_Lab_Beta_Field_Diagnostics_V0601::init()')!==false,
 'Integrated beta v0.60.0 remains initialized'=>strpos($bootstrap,'SC_Lab_Integrated_Research_Beta_V0600::init()')!==false,
 'Beta diagnostics remains contextual in workflow workspace'=>strpos($template,'data-beta-field-diagnostics-v0601')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health disables automatic repair'=>strpos($class,"'automaticRepair'=>false")!==false,
 'Health disables external telemetry'=>strpos($class,"'externalTelemetry'=>false")!==false,
 'Health declares bounded user initiated soak'=>strpos($class,"'boundedUserInitiatedSoak'=>true")!==false,
 'Diagnostic probe proxy route'=>strpos($compute,"/compute/core/beta-diagnostics/v0601/probe")!==false,
 'Diagnostic soak proxy route'=>strpos($compute,"/compute/core/beta-diagnostics/v0601/soak")!==false,
 'v0.60.1 stylesheet enqueued'=>strpos($plugin,'sc-lab-beta-field-diagnostics-v0601')!==false,
 'v0.60.1 JS module registered'=>strpos($plugin,"'beta-field-diagnostics-v0601'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
