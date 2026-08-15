<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-dynamic-systems-v0540.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.54.0 Dynamic Systems II PHP class'=>is_file($root.'/includes/class-sc-lab-dynamic-systems-v0540.php'),
 'v0.54.0 backend module'=>is_file($root.'/backend/app/dynamic_systems_v0540.py'),
 'v0.54.0 JS module'=>is_file($root.'/assets/js/modules/dynamic-systems-v0540.js'),
 'v0.54.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-dynamic-systems-v0540.css'),
 'Advanced study schema'=>is_file($root.'/contracts/dynamic-systems-advanced-study-v0540.schema.json'),
 'Advanced simulation schema'=>is_file($root.'/contracts/dynamic-systems-advanced-simulation-v0540.schema.json'),
 'Bifurcation schema'=>is_file($root.'/contracts/dynamic-systems-bifurcation-v0540.schema.json'),
 'Phase schema'=>is_file($root.'/contracts/dynamic-systems-phase-analysis-v0540.schema.json'),
 'WordPress plugin header reports v0.54.0'=>preg_match('/^\s*\*\s*Version:\s*0\.54\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.54.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.54.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.54 dynamic layer'=>strpos($bootstrap,'SC_Lab_Dynamic_Systems_V0540::init()')!==false,
 'Dynamic Systems II UI remains contextual'=>strpos($template,'data-ds-v0540-root')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares events'=>strpos($class,"'events'=>true")!==false,
 'Health rejects formal proof'=>strpos($class,"'formalBifurcationProof'=>false")!==false,
 'Compute proxy v0.54 simulation route'=>strpos($compute,"/compute/core/model-studio/dynamic-systems/v0540/simulate")!==false,
 'Compute proxy v0.54 bifurcation route'=>strpos($compute,"/compute/core/model-studio/dynamic-systems/v0540/bifurcation")!==false,
 'Compute proxy v0.54 phase route'=>strpos($compute,"/compute/core/model-studio/dynamic-systems/v0540/phase")!==false,
 'v0.54 stylesheet enqueued'=>strpos($plugin,'sc-lab-dynamic-systems-v0540')!==false,
 'v0.54 JS module registered'=>strpos($plugin,"'dynamic-systems-v0540'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
