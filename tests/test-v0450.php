<?php
$root=dirname(__DIR__);
$checks=array(
  'Model Studio v0.45 class'=>is_file($root.'/includes/class-sc-lab-model-studio-v0450.php'),
  'Model Studio v0.45 policy'=>is_file($root.'/contracts/model-studio-policy-v0450.json'),
  'Model schema v0.45'=>is_file($root.'/contracts/model-studio-model-v0450.schema.json'),
  'Scientific graph schema v0.45'=>is_file($root.'/contracts/scientific-graph-v0450.schema.json'),
  'Dynamic system schema'=>is_file($root.'/contracts/dynamic-system-v0450.schema.json'),
  'Dynamic simulation schema'=>is_file($root.'/contracts/dynamic-system-simulation-v0450.schema.json'),
  'Parameter estimation schema'=>is_file($root.'/contracts/dynamic-parameter-estimation-v0450.schema.json'),
  'Dynamic systems backend'=>is_file($root.'/backend/app/dynamic_systems.py'),
  'Dynamic systems regression test'=>is_file($root.'/backend/tests/test_dynamic_systems_v0450.py'),
  'Model Studio browser module'=>is_file($root.'/assets/js/modules/model-studio-v0450.js'),
  'Model Studio CSS'=>is_file($root.'/assets/css/sc-lab-model-studio-v0450.css'),
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$class=file_get_contents($root.'/includes/class-sc-lab-model-studio-v0450.php');
$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks['WordPress plugin header reports v0.45.0']=preg_match('/^\s*\*\s*Version:\s*0\.45\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.45.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.45.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Model Studio v0.45']=strpos($bootstrap,'SC_Lab_Model_Studio_V0450::init()')!==false;
$checks['v0.44 Model Studio is not initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0440::init()')===false;
$checks['v0.45 Model Studio browser module loaded']=strpos($plugin,"'model-studio-v0450'")!==false;
$checks['Shared v0.44 graph engine remains loaded']=strpos($plugin,"'scientific-visualization-engine-v0440'")!==false;
$checks['Dynamic system heading present']=strpos($template,'Dynamic Systems, ODE Models &amp; Parameter Estimation')!==false;
$checks['Health declares coupled ODEs']=strpos($class,"'coupledODEs'=>true")!==false;
$checks['Health declares bounded parameter estimation']=strpos($class,"'boundedParameterEstimation'=>true")!==false;
$checks['Compute core proxies ODE simulation']=strpos($compute,"/compute/core/model-studio/dynamic-systems/simulate")!==false;
$checks['Compute core proxies parameter estimation']=strpos($compute,"/compute/core/model-studio/dynamic-systems/estimate")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
