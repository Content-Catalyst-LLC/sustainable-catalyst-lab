<?php
$root=dirname(__DIR__);
$checks=array(
  'Model Studio v0.46 class'=>is_file($root.'/includes/class-sc-lab-model-studio-v0460.php'),
  'Model Studio v0.46 policy'=>is_file($root.'/contracts/model-studio-policy-v0460.json'),
  'Model schema v0.46'=>is_file($root.'/contracts/model-studio-model-v0460.schema.json'),
  'Scientific graph schema v0.46'=>is_file($root.'/contracts/scientific-graph-v0460.schema.json'),
  'Response surface study schema'=>is_file($root.'/contracts/response-surface-study-v0460.schema.json'),
  'Response surface result schema'=>is_file($root.'/contracts/response-surface-result-v0460.schema.json'),
  'Design-space exploration schema'=>is_file($root.'/contracts/design-space-exploration-v0460.schema.json'),
  'Design-space optimization schema'=>is_file($root.'/contracts/design-space-optimization-v0460.schema.json'),
  'Response surfaces backend'=>is_file($root.'/backend/app/response_surfaces.py'),
  'Response surfaces regression test'=>is_file($root.'/backend/tests/test_response_surfaces_v0460.py'),
  'Model Studio browser module'=>is_file($root.'/assets/js/modules/model-studio-v0460.js'),
  'Model Studio CSS'=>is_file($root.'/assets/css/sc-lab-model-studio-v0460.css'),
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$class=file_get_contents($root.'/includes/class-sc-lab-model-studio-v0460.php');
$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks['WordPress plugin header reports v0.46.0']=preg_match('/^\s*\*\s*Version:\s*0\.46\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.46.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.46.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Model Studio v0.46']=strpos($bootstrap,'SC_Lab_Model_Studio_V0460::init()')!==false;
$checks['v0.45 Model Studio is not initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0450::init()')===false;
$checks['v0.46 Model Studio browser module loaded']=strpos($plugin,"'model-studio-v0460'")!==false;
$checks['Shared v0.44 graph engine remains loaded']=strpos($plugin,"'scientific-visualization-engine-v0440'")!==false;
$checks['Response-surface heading present']=strpos($template,'Response Surfaces, Optimization &amp; Design-Space Exploration')!==false;
$checks['Health declares bounded optimization']=strpos($class,"'boundedOptimization'=>true")!==false;
$checks['Health blocks design-space extrapolation']=strpos($class,"'extrapolationBeyondFactorBounds'=>false")!==false;
$checks['Compute core proxies surface fitting']=strpos($compute,"/compute/core/model-studio/response-surfaces/fit")!==false;
$checks['Compute core proxies design-space exploration']=strpos($compute,"/compute/core/model-studio/response-surfaces/explore")!==false;
$checks['Compute core proxies bounded optimization']=strpos($compute,"/compute/core/model-studio/response-surfaces/optimize")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
