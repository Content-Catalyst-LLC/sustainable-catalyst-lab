<?php
$root=dirname(__DIR__);$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');$class=file_get_contents($root.'/includes/class-sc-lab-scientific-argumentation-v0660.php');$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$plugclass=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array(
'WordPress plugin header reports v0.66.0'=>strpos($plugin,'Version: 0.66.0')!==false,
'Release constant reports v0.66.0'=>strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.66.0")!==false,
'Platform compatibility remains v1.0.0'=>strpos($plugin,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
'Bootstrap initializes v0.66 scientific argumentation'=>strpos($plugin,'SC_Lab_Scientific_Argumentation_V0660::init()')!==false,
'v0.65 evidence grading remains initialized'=>strpos($plugin,'SC_Lab_Evidence_Grading_V0650::init()')!==false,
'Scientific argumentation UI contextual'=>strpos($tpl,'data-scientific-argumentation-v0660')!==false,
'Three application row preserved'=>strpos($tpl,'Prototyping Workbench')!==false&&strpos($tpl,'Decision Studio')!==false&&strpos($tpl,'Site Intelligence')!==false,
'Six destination rail preserved'=>substr_count($tpl,'data-v0483-primary=')===6,
'Health disables automatic hypothesis proof'=>strpos($class,"'automaticHypothesisProof'=>false")!==false,
'Health disables automatic winner selection'=>strpos($class,"'automaticWinnerSelection'=>false")!==false,
'Health disables automatic falsification'=>strpos($class,"'automaticFalsification'=>false")!==false,
'Health disables numeric truth score'=>strpos($class,"'numericTruthScore'=>false")!==false,
'Scientific argumentation evaluate proxy route'=>strpos($core,'/compute/core/scientific-argumentation/v0660/evaluate')!==false,
'v0.66 stylesheet enqueued'=>strpos($plugclass,'sc-lab-scientific-argumentation-v0660')!==false,
'v0.66 JS module registered'=>strpos($plugclass,"'scientific-argumentation-v0660'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
