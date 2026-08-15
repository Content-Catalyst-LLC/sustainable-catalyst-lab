<?php
$root=dirname(__DIR__);
$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$class=file_get_contents($root.'/includes/class-sc-lab-presentation-runtime-v0482.php');
$checks=array(
 'v0.48.2 runtime PHP class'=>is_file($root.'/includes/class-sc-lab-presentation-runtime-v0482.php'),
 'v0.48.2 browser runtime'=>is_file($root.'/assets/js/modules/presentation-runtime-v0482.js'),
 'WordPress plugin header reports v0.48.2'=>preg_match('/^\s*\*\s*Version:\s*0\.48\.2\s*$/m',$bootstrap)===1,
 'Release constant reports v0.48.2'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.48.2')")!==false,
 'GA platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.48.2 runtime'=>strpos($bootstrap,'SC_Lab_Presentation_Runtime_V0482::init()')!==false,
 'v0.48.2 runtime is enqueued'=>strpos($plugin,"'presentation-runtime-v0482'")!==false,
 'v0.48.1 presentation script is not enqueued'=>strpos($plugin,"'presentation-repair-v0481'")===false,
 'Health declares MutationObserver repair'=>strpos($class,"'documentWideMutationObserver'=>false")!==false,
 'Three application card row preserved'=>strpos($class,"'threeApplicationCardRowPreserved'=>true")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
