<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-advanced-statistical-modeling-v0510.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$pkg=file_get_contents($root.'/assets/js/modules/reproducible-model-package-v0500.js');
$checks=array(
 'v0.51.0 statistics PHP class'=>is_file($root.'/includes/class-sc-lab-advanced-statistical-modeling-v0510.php'),
 'v0.51.0 browser statistics module'=>is_file($root.'/assets/js/modules/advanced-statistical-modeling-v0510.js'),
 'v0.51.0 statistics stylesheet'=>is_file($root.'/assets/css/sc-lab-advanced-statistical-modeling-v0510.css'),
 'statistical result contract'=>is_file($root.'/contracts/statistical-model-result-v0510.schema.json'),
 'statistical policy contract'=>is_file($root.'/contracts/statistical-model-policy-v0510.json'),
 'WordPress plugin header reports v0.51.0'=>preg_match('/^\s*\*\s*Version:\s*0\.51\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.51.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.51.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.51 statistics layer'=>strpos($bootstrap,'SC_Lab_Advanced_Statistical_Modeling_V0510::init()')!==false,
 'Statistics UI rendered'=>strpos($template,'data-advanced-statistical-modeling-v0510')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares generalized linear models'=>strpos($class,"'generalizedLinearModels'=>true")!==false,
 'Health declares no arbitrary code'=>strpos($class,"'arbitraryCode'=>false")!==false,
 'Compute proxy statistical fit route'=>strpos($compute,"/compute/core/model-studio/statistics/fit")!==false,
 'Compute proxy statistical predict route'=>strpos($compute,"/compute/core/model-studio/statistics/predict")!==false,
 'Compute proxy statistical CV route'=>strpos($compute,"/compute/core/model-studio/statistics/cross-validate")!==false,
 'Compute proxy statistical comparison route'=>strpos($compute,"/compute/core/model-studio/statistics/compare")!==false,
 'v0.51 browser module enqueued'=>strpos($plugin,"'advanced-statistical-modeling-v0510'")!==false,
 'v0.50 research package captures analysis packets'=>strpos($pkg,"'analysisPackets'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
