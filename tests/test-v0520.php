<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-bayesian-inference-v0520.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$pkg=file_get_contents($root.'/assets/js/modules/reproducible-model-package-v0500.js');
$checks=array(
 'v0.52.0 Bayesian PHP class'=>is_file($root.'/includes/class-sc-lab-bayesian-inference-v0520.php'),
 'v0.52.0 browser Bayesian module'=>is_file($root.'/assets/js/modules/bayesian-inference-v0520.js'),
 'v0.52.0 Bayesian stylesheet'=>is_file($root.'/assets/css/sc-lab-bayesian-inference-v0520.css'),
 'Bayesian study contract'=>is_file($root.'/contracts/bayesian-study-v0520.schema.json'),
 'Bayesian result contract'=>is_file($root.'/contracts/bayesian-result-v0520.schema.json'),
 'Bayesian policy contract'=>is_file($root.'/contracts/bayesian-policy-v0520.json'),
 'WordPress plugin header reports v0.52.0'=>preg_match('/^\s*\*\s*Version:\s*0\.52\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.52.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.52.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.52 Bayesian layer'=>strpos($bootstrap,'SC_Lab_Bayesian_Inference_V0520::init()')!==false,
 'Bayesian UI rendered contextually'=>strpos($template,'data-bayesian-inference-v0520')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares posterior diagnostics'=>strpos($class,"'posteriorDiagnostics'=>true")!==false,
 'Health rejects automatic convergence certification'=>strpos($class,"'automaticConvergenceCertification'=>false")!==false,
 'Compute proxy Bayesian fit route'=>strpos($compute,"/compute/core/model-studio/bayesian/fit")!==false,
 'Compute proxy posterior predictive route'=>strpos($compute,"/compute/core/model-studio/bayesian/posterior-predictive")!==false,
 'v0.52 browser module enqueued'=>strpos($plugin,"'bayesian-inference-v0520'")!==false,
 'v0.50 research package captures analysis packets'=>strpos($pkg,"'analysisPackets'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
