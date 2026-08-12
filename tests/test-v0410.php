<?php
$root=dirname(__DIR__);
$checks=array(
  'Model Studio class'=>is_file($root.'/includes/class-sc-lab-model-studio-v0410.php'),
  'Model Studio policy'=>is_file($root.'/contracts/model-studio-policy-v0410.json'),
  'Model schema'=>is_file($root.'/contracts/model-studio-model-v0410.schema.json'),
  'Graph schema'=>is_file($root.'/contracts/scientific-graph-v0410.schema.json'),
  'Result schema'=>is_file($root.'/contracts/model-studio-result-v0410.schema.json'),
  'Backend module'=>is_file($root.'/backend/app/model_studio.py'),
  'Shared visualization engine'=>is_file($root.'/assets/js/modules/scientific-visualization-engine-v0410.js')
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$checks['WordPress plugin header reports v0.41.0']=preg_match('/^\s*\*\s*Version:\s*0\.41\.0\s*$/m',$bootstrap)===1;
$checks['Feature release constant reports v0.41.0']=strpos($bootstrap,"define('SC_LAB_FEATURE_VERSION', '0.41.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Model Studio']=strpos($bootstrap,'SC_Lab_Model_Studio_V0410::init()')!==false;
$checks['Model Studio shortcode registered']=strpos($plugin,"add_shortcode('sc_lab_model_studio'")!==false;
$checks['Model Studio navigation registered']=strpos($template,"'model-studio' => 'Model Studio'")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
