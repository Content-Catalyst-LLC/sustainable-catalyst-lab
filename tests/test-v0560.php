<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-advanced-experimental-design-v0560.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.56.0 advanced design PHP class'=>is_file($root.'/includes/class-sc-lab-advanced-experimental-design-v0560.php'),
 'v0.56.0 backend module'=>is_file($root.'/backend/app/advanced_experimental_design.py'),
 'v0.56.0 JS module'=>is_file($root.'/assets/js/modules/advanced-experimental-design-v0560.js'),
 'v0.56.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-advanced-experimental-design-v0560.css'),
 'Advanced design schema'=>is_file($root.'/contracts/advanced-experimental-design-v0560.schema.json'),
 'Sequential plan schema'=>is_file($root.'/contracts/sequential-experiment-plan-v0560.schema.json'),
 'Optimality diagnostics schema'=>is_file($root.'/contracts/design-optimality-diagnostics-v0560.schema.json'),
 'Advanced design policy'=>is_file($root.'/contracts/advanced-experimental-design-policy-v0560.json'),
 'WordPress plugin header reports v0.56.0'=>preg_match('/^\s*\*\s*Version:\s*0\.56\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.56.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.56.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.56 advanced design'=>strpos($bootstrap,'SC_Lab_Advanced_Experimental_Design_V0560::init()')!==false,
 'Advanced design UI remains contextual'=>strpos($template,'data-advanced-design-v0560')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares D-optimal support'=>strpos($class,"'dOptimalDesign'=>true")!==false,
 'Health disables automatic experiment execution'=>strpos($class,"'automaticExperimentExecution'=>false")!==false,
 'Health disables automatic stopping'=>strpos($class,"'automaticStopping'=>false")!==false,
 'Compute proxy v0.56 optimal route'=>strpos($compute,"/compute/core/design-studies/v0560/optimal-design")!==false,
 'Compute proxy v0.56 sequential route'=>strpos($compute,"/compute/core/design-studies/v0560/sequential-plan")!==false,
 'v0.56 stylesheet enqueued'=>strpos($plugin,'sc-lab-advanced-experimental-design-v0560')!==false,
 'v0.56 JS module registered'=>strpos($plugin,"'advanced-experimental-design-v0560'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
