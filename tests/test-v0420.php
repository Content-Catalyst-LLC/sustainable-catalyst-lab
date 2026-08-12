<?php
$root=dirname(__DIR__);
$checks=array(
  'Model Studio v0.42 class'=>is_file($root.'/includes/class-sc-lab-model-studio-v0420.php'),
  'Model Studio v0.42 policy'=>is_file($root.'/contracts/model-studio-policy-v0420.json'),
  'Model schema v0.42'=>is_file($root.'/contracts/model-studio-model-v0420.schema.json'),
  'Equation schema v0.42'=>is_file($root.'/contracts/scientific-equation-v0420.schema.json'),
  'Graph schema v0.42'=>is_file($root.'/contracts/scientific-graph-v0420.schema.json'),
  'Equation backend'=>is_file($root.'/backend/app/equation_builder.py'),
  'Shared visualization engine'=>is_file($root.'/assets/js/modules/scientific-visualization-engine-v0410.js')
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$checks['WordPress plugin header reports v0.42.0']=preg_match('/^\s*\*\s*Version:\s*0\.42\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.42.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.42.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Model Studio v0.42']=strpos($bootstrap,'SC_Lab_Model_Studio_V0420::init()')!==false;
$checks['v0.41 Model Studio is not initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0410::init()')===false;
$checks['v0.42 browser module loaded']=strpos($plugin,"'model-studio-v0420'")!==false;
$checks['Model Studio navigation retained']=strpos($template,"'model-studio' => 'Model Studio'")!==false;
$checks['Equation Builder label is present']=strpos($template,'Scientific Equation Builder')!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
