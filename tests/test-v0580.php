<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-scientific-compute-hardening-v0580.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.58.0 compute hardening PHP class'=>is_file($root.'/includes/class-sc-lab-scientific-compute-hardening-v0580.php'),
 'v0.58.0 backend module'=>is_file($root.'/backend/app/scientific_compute_hardening.py'),
 'v0.58.0 JS module'=>is_file($root.'/assets/js/modules/scientific-compute-hardening-v0580.js'),
 'v0.58.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-scientific-compute-hardening-v0580.css'),
 'Compute job schema'=>is_file($root.'/contracts/scientific-compute-job-v0580.schema.json'),
 'Workload assessment schema'=>is_file($root.'/contracts/workload-assessment-v0580.schema.json'),
 'Result cache schema'=>is_file($root.'/contracts/scientific-result-cache-v0580.schema.json'),
 'Compute policy'=>is_file($root.'/contracts/scientific-compute-hardening-policy-v0580.json'),
 'WordPress plugin header reports v0.58.0'=>preg_match('/^\s*\*\s*Version:\s*0\.58\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.58.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.58.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes compute hardening'=>strpos($bootstrap,'SC_Lab_Scientific_Compute_Hardening_V0580::init()')!==false,
 'Compute hardening remains contextual in workflow workspace'=>strpos($template,'data-compute-hardening-v0580')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares bounded async execution'=>strpos($class,"'boundedAsyncExecution'=>true")!==false,
 'Health disables force termination'=>strpos($class,"'forceTermination'=>false")!==false,
 'Health disables arbitrary code'=>strpos($class,"'arbitraryCode'=>false")!==false,
 'Compute proxy v0.58 jobs route'=>strpos($compute,"/compute/core/compute-hardening/v0580/jobs")!==false,
 'Compute proxy v0.58 assess route'=>strpos($compute,"/compute/core/compute-hardening/v0580/assess")!==false,
 'v0.58 stylesheet enqueued'=>strpos($plugin,'sc-lab-scientific-compute-hardening-v0580')!==false,
 'v0.58 JS module registered'=>strpos($plugin,"'scientific-compute-hardening-v0580'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
