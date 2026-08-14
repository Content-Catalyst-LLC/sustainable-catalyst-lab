<?php
$root=dirname(__DIR__);
$checks=array(
  'Model Studio v0.44 class'=>is_file($root.'/includes/class-sc-lab-model-studio-v0440.php'),
  'Model Studio v0.44 policy'=>is_file($root.'/contracts/model-studio-policy-v0440.json'),
  'Model schema v0.44'=>is_file($root.'/contracts/model-studio-model-v0440.schema.json'),
  'Scientific graph schema v0.44'=>is_file($root.'/contracts/scientific-graph-v0440.schema.json'),
  'Publication figure schema v0.44'=>is_file($root.'/contracts/publication-figure-v0440.schema.json'),
  'Interactive visualization engine'=>is_file($root.'/assets/js/modules/scientific-visualization-engine-v0440.js'),
  'Interactive visualization CSS'=>is_file($root.'/assets/css/sc-lab-scientific-visualization-engine-v0440.css'),
  'Model Studio browser module'=>is_file($root.'/assets/js/modules/model-studio-v0440.js'),
  'Model Studio CSS'=>is_file($root.'/assets/css/sc-lab-model-studio-v0440.css'),
  'Backend v0.44 regression test'=>is_file($root.'/backend/tests/test_model_studio_v0440.py'),
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$class=file_get_contents($root.'/includes/class-sc-lab-model-studio-v0440.php');
$checks['WordPress plugin header reports v0.44.0']=preg_match('/^\s*\*\s*Version:\s*0\.44\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.44.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.44.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Model Studio v0.44']=strpos($bootstrap,'SC_Lab_Model_Studio_V0440::init()')!==false;
$checks['v0.43 Model Studio is not initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0430::init()')===false;
$checks['v0.44 engine browser module loaded']=strpos($plugin,"'scientific-visualization-engine-v0440'")!==false;
$checks['v0.44 Model Studio browser module loaded']=strpos($plugin,"'model-studio-v0440'")!==false;
$checks['Interactive graph heading present']=strpos($template,'Interactive Scientific Graph Engine &amp; Publication Graphics')!==false;
$checks['Publication figure controls present']=strpos($template,'data-ms-v0440-publication-apply')!==false;
$checks['Health declares zoom']=strpos($class,"'interactiveZoom'=>true")!==false;
$checks['Health declares publication exports']=strpos($class,"'publicationExports'=>array('svg','png','csv','json')")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
