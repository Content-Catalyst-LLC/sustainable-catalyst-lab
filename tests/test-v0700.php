<?php
$root=dirname(__DIR__);$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');$class=file_get_contents($root.'/includes/class-sc-lab-preregistration-v0700.php');$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$plugclass=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array(
'WordPress plugin header reports v0.70.0'=>strpos($plugin,'Version: 0.70.0')!==false,
'Release constant reports v0.70.0'=>strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.70.0")!==false,
'Platform compatibility remains v1.0.0'=>strpos($plugin,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
'Bootstrap initializes v0.70 preregistration'=>strpos($plugin,'SC_Lab_Preregistration_V0700::init()')!==false,
'v0.69 scientific theory remains initialized'=>strpos($plugin,'SC_Lab_Scientific_Theory_V0690::init()')!==false,
'Preregistration UI contextual'=>strpos($tpl,'data-preregistration-v0700')!==false,
'Three application row preserved'=>strpos($tpl,'Prototyping Workbench')!==false&&strpos($tpl,'Decision Studio')!==false&&strpos($tpl,'Site Intelligence')!==false,
'Six destination rail preserved'=>substr_count($tpl,'data-v0483-primary=')===6,
'Health requires pre-result freeze'=>strpos($class,"'preResultFreezeRequired'=>true")!==false,
'Health marks frozen snapshot immutable'=>strpos($class,"'frozenSnapshotImmutable'=>true")!==false,
'Health requires timestamped deviation log'=>strpos($class,"'timestampedDeviationLogRequired'=>true")!==false,
'Health disables automatic hypothesis validation'=>strpos($class,"'automaticHypothesisValidation'=>false")!==false,
'Health disables automatic post-hoc preregistration'=>strpos($class,"'automaticPostHocPreregistration'=>false")!==false,
'Health rejects raw scientific data'=>strpos($class,"'rawScientificDataAccepted'=>false")!==false,
'Health rejects participant-level data'=>strpos($class,"'participantLevelDataAccepted'=>false")!==false,
'Preregistration freeze proxy route'=>strpos($core,'/compute/core/preregistration/v0700/freeze')!==false,
'Preregistration evaluate proxy route'=>strpos($core,'/compute/core/preregistration/v0700/evaluate')!==false,
'v0.70 stylesheet enqueued'=>strpos($plugclass,'sc-lab-preregistration-v0700')!==false,
'v0.70 JS module registered'=>strpos($plugclass,"'preregistration-v0700'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
