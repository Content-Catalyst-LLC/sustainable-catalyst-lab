<?php
$root=dirname(__DIR__);
$checks=array(
  'Graph Studio v0.47 class'=>is_file($root.'/includes/class-sc-lab-graph-studio-v0470.php'),
  'Graph Studio policy'=>is_file($root.'/contracts/graph-studio-policy-v0470.json'),
  'Scientific figure schema'=>is_file($root.'/contracts/scientific-figure-v0470.schema.json'),
  'Figure workspace schema'=>is_file($root.'/contracts/figure-workspace-v0470.schema.json'),
  'Graph Studio backend'=>is_file($root.'/backend/app/graph_studio.py'),
  'Graph Studio regression test'=>is_file($root.'/backend/tests/test_graph_studio_v0470.py'),
  'Graph Studio browser module'=>is_file($root.'/assets/js/modules/graph-studio-v0470.js'),
  'Interface reorganization browser module'=>is_file($root.'/assets/js/modules/interface-reorganization-v0470.js'),
  'Graph Studio CSS'=>is_file($root.'/assets/css/sc-lab-graph-studio-v0470.css'),
  'Interface v0.47 CSS'=>is_file($root.'/assets/css/sc-lab-interface-v0470.css'),
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$class=file_get_contents($root.'/includes/class-sc-lab-graph-studio-v0470.php');
$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks['WordPress plugin header reports v0.47.0']=preg_match('/^\s*\*\s*Version:\s*0\.47\.0\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.47.0']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.47.0')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes Graph Studio v0.47']=strpos($bootstrap,'SC_Lab_Graph_Studio_V0470::init()')!==false;
$checks['v0.46 Model Studio remains initialized']=strpos($bootstrap,'SC_Lab_Model_Studio_V0460::init()')!==false;
$checks['Graph Studio shortcode exposed']=strpos($plugin,"'sc_lab_graph_studio' => 'graph-studio'")!==false;
$checks['Graph Studio browser module loaded']=strpos($plugin,"'graph-studio-v0470'")!==false;
$checks['Interface reorganization module loaded']=strpos($plugin,"'interface-reorganization-v0470'")!==false;
$checks['Shared v0.44 graph engine remains loaded']=strpos($plugin,"'scientific-visualization-engine-v0440'")!==false;
$checks['Dedicated Graph Studio panel present']=strpos($template,'Scientific Figure Workspace')!==false;
$checks['Model navigation group present']=strpos($template,"'Model' => array(")!==false;
$checks['Visualize navigation group present']=strpos($template,"'Visualize' => array(")!==false;
$checks['Health declares dedicated graph workspace']=strpos($class,"'dedicatedGraphWorkspace'=>true")!==false;
$checks['Compute core proxies figure normalization']=strpos($compute,"/compute/core/graph-studio/figures/normalize")!==false;
$checks['Compute core proxies figure workspace build']=strpos($compute,"/compute/core/graph-studio/workspaces/build")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
