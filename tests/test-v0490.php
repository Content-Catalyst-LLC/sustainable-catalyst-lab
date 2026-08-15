<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-shared-model-handoff-v0490.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.49.0 model handoff PHP class'=>is_file($root.'/includes/class-sc-lab-shared-model-handoff-v0490.php'),
 'v0.49.0 browser handoff'=>is_file($root.'/assets/js/modules/shared-model-handoff-v0490.js'),
 'v0.49.0 handoff stylesheet'=>is_file($root.'/assets/css/sc-lab-shared-model-handoff-v0490.css'),
 'shared computational model contract'=>is_file($root.'/contracts/computational-model-v0490.schema.json'),
 'shared handoff contract'=>is_file($root.'/contracts/model-handoff-v0490.schema.json'),
 'WordPress plugin header reports v0.49.0'=>preg_match('/^\s*\*\s*Version:\s*0\.49\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.49.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.49.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.49 handoff'=>strpos($bootstrap,'SC_Lab_Shared_Model_Handoff_V0490::init()')!==false,
 'Model exchange UI rendered'=>strpos($template,'data-model-handoff-v0490')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares bidirectional exchange'=>strpos($class,"'labToWorkbench'=>true")!==false&&strpos($class,"'workbenchToLab'=>true")!==false,
 'Health declares no arbitrary code'=>strpos($class,"'arbitraryCode'=>false")!==false,
 'Compute proxy outbound route'=>strpos($compute,"/compute/core/model-handoff/outbound/workbench")!==false,
 'Compute proxy inbound route'=>strpos($compute,"/compute/core/model-handoff/inbound/workbench")!==false,
 'v0.49 browser module enqueued'=>strpos($plugin,"'shared-model-handoff-v0490'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
