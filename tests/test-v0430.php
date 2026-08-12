<?php
$root=dirname(__DIR__);
$checks=array(
  'Model Studio v0.43 class'=>is_file($root.'/includes/class-sc-lab-model-studio-v0430.php'),
  'Model Studio v0.43 policy'=>is_file($root.'/contracts/model-studio-policy-v0430.json'),
  'Model schema v0.43'=>is_file($root.'/contracts/model-studio-model-v0430.schema.json'),
  'Diagnostics schema v0.43'=>is_file($root.'/contracts/model-diagnostics-v0430.schema.json'),
  'Cross-validation schema v0.43'=>is_file($root.'/contracts/cross-validation-v0430.schema.json'),
  'Comparison schema v0.43'=>is_file($root.'/contracts/model-comparison-v0430.schema.json'),
  'Graph schema v0.43'=>is_file($root.'/contracts/scientific-graph-v0430.schema.json'),
  'Diagnostics backend'=>is_file($root.'/backend/app/model_diagnostics.py'),
  'Shared visualization engine'=>is_file($root.'/assets/js/modules/scientific-visualization-engine-v0410.js')
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$checks['WordPress plugin header reports v0.43.0']=preg_match('/^\s*\*\s*Version:\s*0\.43\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.43.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.43.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Model Studio v0.43']=strpos($bootstrap,'SC_Lab_Model_Studio_V0430::init()')!==false;
$checks['v0.42 Model Studio is not initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0420::init()')===false;
$checks['v0.43 browser module loaded']=strpos($plugin,"'model-studio-v0430'")!==false;
$checks['Model Studio navigation retained']=strpos($template,"'model-studio' => 'Model Studio'")!==false;
$checks['Diagnostics heading is present']=strpos($template,'Model Diagnostics, Cross-Validation &amp; Scientific Model Comparison')!==false;
$checks['Cross-validation button present']=strpos($template,'data-ms-v0430-run-cv')!==false;
$checks['Comparison selector present']=strpos($template,'data-ms-v0430-comparison-models')!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
