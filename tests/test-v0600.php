<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-integrated-research-beta-v0600.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.60.0 integrated beta PHP class'=>is_file($root.'/includes/class-sc-lab-integrated-research-beta-v0600.php'),
 'v0.60.0 backend module'=>is_file($root.'/backend/app/integrated_research_beta_v0600.py'),
 'v0.60.0 JS module'=>is_file($root.'/assets/js/modules/integrated-research-beta-v0600.js'),
 'v0.60.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-integrated-research-beta-v0600.css'),
 'Integrated research journey schema'=>is_file($root.'/contracts/integrated-research-journey-v0600.schema.json'),
 'Integrated beta readiness schema'=>is_file($root.'/contracts/integrated-beta-readiness-v0600.schema.json'),
 'Integrated beta packet schema'=>is_file($root.'/contracts/integrated-research-beta-packet-v0600.schema.json'),
 'Integrated beta policy'=>is_file($root.'/contracts/integrated-research-beta-policy-v0600.json'),
 'WordPress plugin header reports v0.60.0'=>preg_match('/^\s*\*\s*Version:\s*0\.60\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.60.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.60.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes integrated beta'=>strpos($bootstrap,'SC_Lab_Integrated_Research_Beta_V0600::init()')!==false,
 'Integrated beta remains contextual in workflow workspace'=>strpos($template,'data-integrated-research-beta-v0600')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health requires human review'=>strpos($class,"'humanReviewRequired'=>true")!==false,
 'Health disables automatic scientific certification'=>strpos($class,"'automaticScientificCertification'=>false")!==false,
 'Health excludes raw sensitive data'=>strpos($class,"'rawSensitiveDataInBetaPacket'=>false")!==false,
 'Integrated readiness proxy route'=>strpos($compute,"/compute/core/integrated-research/v0600/readiness")!==false,
 'Integrated packet proxy route'=>strpos($compute,"/compute/core/integrated-research/v0600/packet")!==false,
 'v0.60 stylesheet enqueued'=>strpos($plugin,'sc-lab-integrated-research-beta-v0600')!==false,
 'v0.60 JS module registered'=>strpos($plugin,"'integrated-research-beta-v0600'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
