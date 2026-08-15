<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-reproducible-model-package-v0500.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.50.0 package PHP class'=>is_file($root.'/includes/class-sc-lab-reproducible-model-package-v0500.php'),
 'v0.50.0 browser package module'=>is_file($root.'/assets/js/modules/reproducible-model-package-v0500.js'),
 'v0.50.0 package stylesheet'=>is_file($root.'/assets/css/sc-lab-reproducible-model-package-v0500.css'),
 'reproducible model package contract'=>is_file($root.'/contracts/reproducible-model-package-v0500.schema.json'),
 'research bundle contract'=>is_file($root.'/contracts/model-research-bundle-v0500.schema.json'),
 'WordPress plugin header reports v0.50.0'=>preg_match('/^\s*\*\s*Version:\s*0\.50\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.50.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.50.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes v0.50 package layer'=>strpos($bootstrap,'SC_Lab_Reproducible_Model_Package_V0500::init()')!==false,
 'Model package UI rendered'=>strpos($template,'data-reproducible-model-package-v0500')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares research ZIP'=>strpos($class,"'portableResearchZip'=>true")!==false,
 'Health declares no arbitrary code'=>strpos($class,"'arbitraryCode'=>false")!==false,
 'Compute proxy package build route'=>strpos($compute,"/compute/core/model-packages/build")!==false,
 'Compute proxy research bundle route'=>strpos($compute,"/compute/core/model-packages/research-bundle")!==false,
 'Compute proxy register route'=>strpos($compute,"/compute/core/model-packages/register")!==false,
 'v0.50 browser module enqueued'=>strpos($plugin,"'reproducible-model-package-v0500'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
