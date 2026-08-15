<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-data-transformations-v0550.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.55.0 data transformation PHP class'=>is_file($root.'/includes/class-sc-lab-data-transformations-v0550.php'),
 'v0.55.0 backend module'=>is_file($root.'/backend/app/data_transformations.py'),
 'v0.55.0 JS module'=>is_file($root.'/assets/js/modules/data-transformations-v0550.js'),
 'v0.55.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-data-transformations-v0550.css'),
 'Transformation plan schema'=>is_file($root.'/contracts/scientific-data-transformation-plan-v0550.schema.json'),
 'Transformation result schema'=>is_file($root.'/contracts/scientific-data-transformation-result-v0550.schema.json'),
 'Scientific join schema'=>is_file($root.'/contracts/scientific-data-join-v0550.schema.json'),
 'Transformation policy'=>is_file($root.'/contracts/scientific-data-transformation-policy-v0550.json'),
 'WordPress plugin header reports v0.55.0'=>preg_match('/^\s*\*\s*Version:\s*0\.55\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.55.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.55.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.55 data layer'=>strpos($bootstrap,'SC_Lab_Data_Transformations_V0550::init()')!==false,
 'Transformation UI remains contextual'=>strpos($template,'data-data-transform-v0550')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares safe derived variables'=>strpos($class,"'safeDerivedVariables'=>true")!==false,
 'Health disables automatic imputation'=>strpos($class,"'automaticImputation'=>false")!==false,
 'Compute proxy v0.55 transformation route'=>strpos($compute,"/compute/core/datasets/v0550/transform")!==false,
 'Compute proxy v0.55 join route'=>strpos($compute,"/compute/core/datasets/v0550/join")!==false,
 'v0.55 stylesheet enqueued'=>strpos($plugin,'sc-lab-data-transformations-v0550')!==false,
 'v0.55 JS module registered'=>strpos($plugin,"'data-transformations-v0550'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
