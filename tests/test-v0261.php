<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$admin=file_get_contents($root.'/includes/class-sc-lab-admin.php');
$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php');
$client=file_get_contents($root.'/assets/js/modules/compute-client.js');
$checks=array(
 'version header'=>strpos($main,'Version: 0.26.1')!==false,
 'version constant'=>strpos($main,"SC_LAB_VERSION', '0.26.1")!==false,
 'python queue class'=>strpos($main,'SC_Lab_Python_Compute_Core_V0261::init')!==false,
 'queue create route'=>strpos($core,"/compute/core/jobs'")!==false,
 'queue list gateway'=>strpos($core,'jobs_list')!==false,
 'cancel route'=>strpos($core,"/cancel'")!==false,
 'retry route'=>strpos($core,"/retry'")!==false,
 'worker route'=>strpos($core,"/compute/core/workers")!==false,
 'queue status route'=>strpos($core,"/compute/core/queue/status")!==false,
 'HMAC query path safety'=>strpos($rest,'strtok($path')!==false,
 'queue monitor'=>strpos($admin,'Compute queue monitor')!==false,
 'default job timeout'=>strpos($admin,'compute_job_timeout_seconds')!==false,
 'browser retry client'=>strpos($client,'retry(jobId)')!==false,
 'job contract'=>is_file($root.'/contracts/compute-job-v0261.schema.json'),
 'backend queue'=>is_file($root.'/backend/app/jobs.py'),
 'queue documentation'=>is_file($root.'/docs/JOB_QUEUE_WORKER_RELIABILITY_V0261.md'),
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL: $label\n");exit(1);}echo "PASS: $label\n";}
