<?php
$root=dirname(__DIR__);
$checks=array(
  'v0.48 probabilistic PHP class'=>is_file($root.'/includes/class-sc-lab-probabilistic-analysis-v0480.php'),
  'v0.48 probabilistic backend'=>is_file($root.'/backend/app/probabilistic_analysis.py'),
  'v0.48 probabilistic regression test'=>is_file($root.'/backend/tests/test_probabilistic_analysis_v0480.py'),
  'v0.48 probabilistic browser module'=>is_file($root.'/assets/js/modules/probabilistic-analysis-v0480.js'),
  'v0.48 probabilistic CSS'=>is_file($root.'/assets/css/sc-lab-probabilistic-analysis-v0480.css'),
  'v0.48 study schema'=>is_file($root.'/contracts/probabilistic-study-v0480.schema.json'),
  'v0.48 result schema'=>is_file($root.'/contracts/probabilistic-analysis-v0480.schema.json'),
  'v0.48 policy contract'=>is_file($root.'/contracts/probabilistic-policy-v0480.json'),
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$class=file_get_contents($root.'/includes/class-sc-lab-probabilistic-analysis-v0480.php');
$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks['WordPress plugin header reports v0.48.0']=preg_match('/^\s*\*\s*Version:\s*0\.48\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.48.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.48.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes v0.48 probabilistic layer']=strpos($bootstrap,'SC_Lab_Probabilistic_Analysis_V0480::init()')!==false;
$checks['Graph Studio v0.47 remains initialized']=strpos($bootstrap,'SC_Lab_Graph_Studio_V0470::init()')!==false;
$checks['Model Studio v0.46 remains initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0460::init()')!==false;
$checks['v0.48 shortcode exposed']=strpos($plugin,"'sc_lab_probabilistic_analysis'")!==false;
$checks['v0.48 browser module loaded']=strpos($plugin,"'probabilistic-analysis-v0480'")!==false;
$checks['Dedicated probabilistic panel present']=strpos($template,'Integrated Uncertainty, Sensitivity &amp; Probabilistic Visualization')!==false;
$checks['Health declares Graph Studio handoff']=strpos($class,"'graphStudioHandoff'=>true")!==false;
$checks['Health preserves legacy registered-model ensembles']=strpos($class,"'legacyRegisteredModelEnsembles'=>'0.34.1'")!==false;
$checks['Compute core proxies probabilistic analysis']=strpos($compute,"/compute/core/model-studio/probabilistic/analyze")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
