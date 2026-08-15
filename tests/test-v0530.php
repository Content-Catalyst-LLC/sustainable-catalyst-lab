<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-correlated-uncertainty-v0530.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.53.0 correlated uncertainty PHP class'=>is_file($root.'/includes/class-sc-lab-correlated-uncertainty-v0530.php'),
 'v0.53.0 backend module'=>is_file($root.'/backend/app/correlated_uncertainty.py'),
 'v0.53.0 dependency stylesheet'=>is_file($root.'/assets/css/sc-lab-correlated-uncertainty-v0530.css'),
 'Dependency schema'=>is_file($root.'/contracts/probabilistic-dependency-v0530.schema.json'),
 'Dependent study schema'=>is_file($root.'/contracts/dependent-probabilistic-study-v0530.schema.json'),
 'Dependent result schema'=>is_file($root.'/contracts/dependent-probabilistic-analysis-v0530.schema.json'),
 'WordPress plugin header reports v0.53.0'=>preg_match('/^\s*\*\s*Version:\s*0\.53\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.53.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.53.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.53 dependency layer'=>strpos($bootstrap,'SC_Lab_Correlated_Uncertainty_V0530::init()')!==false,
 'Dependency UI remains contextual'=>strpos($template,'data-pa-v0530-dependency-method')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares Gaussian copula'=>strpos($class,"'gaussianCopula'=>true")!==false,
 'Health rejects causal interpretation'=>strpos($class,"'automaticCausalInterpretation'=>false")!==false,
 'Compute proxy v0.53 analyze route'=>strpos($compute,"/compute/core/model-studio/probabilistic/v0530/analyze")!==false,
 'Compute proxy dependency estimator route'=>strpos($compute,"/compute/core/model-studio/probabilistic/v0530/estimate-dependency")!==false,
 'v0.53 stylesheet enqueued'=>strpos($plugin,'sc-lab-correlated-uncertainty-v0530')!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
