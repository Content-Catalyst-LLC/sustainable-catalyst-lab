<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-contextual-navigation-v0483.php');
$checks=array(
 'v0.48.3 navigation PHP class'=>is_file($root.'/includes/class-sc-lab-contextual-navigation-v0483.php'),
 'v0.48.3 browser navigation'=>is_file($root.'/assets/js/modules/contextual-navigation-v0483.js'),
 'v0.48.3 navigation stylesheet'=>is_file($root.'/assets/css/sc-lab-contextual-navigation-v0483.css'),
 'WordPress plugin header reports v0.48.3'=>preg_match('/^\s*\*\s*Version:\s*0\.48\.3\s*$/m',$bootstrap)===1,
 'Release constant reports v0.48.3'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.48.3')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.48.3 navigation'=>strpos($bootstrap,'SC_Lab_Contextual_Navigation_V0483::init()')!==false,
 'Six primary destinations rendered'=>substr_count($template,'data-v0483-primary=')===6,
 'Scientific tools launcher rendered'=>strpos($template,'data-v0483-tools-search')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Health declares no MutationObserver'=>strpos($class,"'documentWideMutationObserver'=>false")!==false,
 'Health declares contextual navigation'=>strpos($class,"'contextualSubnavigation'=>true")!==false,
 'v0.48.3 browser module enqueued'=>strpos($plugin,"'contextual-navigation-v0483'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
