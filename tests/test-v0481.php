<?php
$root=dirname(__DIR__);
$checks=array(
  'v0.48.1 presentation PHP class'=>is_file($root.'/includes/class-sc-lab-presentation-repair-v0481.php'),
  'v0.48.1 browser module'=>is_file($root.'/assets/js/modules/presentation-repair-v0481.js'),
  'v0.48.1 presentation stylesheet'=>is_file($root.'/assets/css/sc-lab-presentation-v0481.css'),
  'v0.48 probabilistic backend preserved'=>is_file($root.'/backend/app/probabilistic_analysis.py'),
  'v0.47 Graph Studio preserved'=>is_file($root.'/assets/js/modules/graph-studio-v0470.js'),
);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$class=file_get_contents($root.'/includes/class-sc-lab-presentation-repair-v0481.php');
$checks['WordPress plugin header reports v0.48.1']=preg_match('/^\s*\*\s*Version:\s*0\.48\.1\s*$/m',$bootstrap)===1;
$checks['Release constant reports v0.48.1']=strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.48.1')")!==false;
$checks['GA platform compatibility remains v1.0.0']=strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false;
$checks['Bootstrap initializes v0.48.1 presentation repair']=strpos($bootstrap,'SC_Lab_Presentation_Repair_V0481::init()')!==false;
$checks['v0.48 probabilistic layer remains initialized']=strpos($bootstrap,'SC_Lab_Probabilistic_Analysis_V0480::init()')!==false;
$checks['v0.47 Graph Studio remains initialized']=strpos($bootstrap,'SC_Lab_Graph_Studio_V0470::init()')!==false;
$checks['v0.48.1 assets loaded']=strpos($plugin,'sc-lab-presentation-v0481')!==false && strpos($plugin,"'presentation-repair-v0481'")!==false;
$checks['Graph Studio front door present']=strpos($template,'GRAPH STUDIO / PROJECT FIGURE')!==false && strpos($template,'data-v0481-overview-canvas')!==false;
$checks['Workspace switcher present']=strpos($template,'data-v0481-workspace-switcher')!==false;
$checks['Three related applications remain represented']=strpos($template,'Prototyping Workbench')!==false && strpos($template,'Decision Studio')!==false && strpos($template,'Site Intelligence')!==false;
$checks['Health explicitly preserves outer application cards']=strpos($class,"'threeApplicationCardRowPreserved'=>true")!==false;
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
