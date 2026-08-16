<?php
$root=dirname(__DIR__);$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');$class=file_get_contents($root.'/includes/class-sc-lab-evidence-grading-v0650.php');$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$plugclass=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array(
'WordPress plugin header reports v0.65.0'=>strpos($plugin,'Version: 0.65.0')!==false,
'Release constant reports v0.65.0'=>strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.65.0")!==false,
'Platform compatibility remains v1.0.0'=>strpos($plugin,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
'Bootstrap initializes v0.65 evidence grading'=>strpos($plugin,'SC_Lab_Evidence_Grading_V0650::init()')!==false,
'v0.64 synthesis remains initialized'=>strpos($plugin,'SC_Lab_Evidence_Synthesis_V0640::init()')!==false,
'Evidence grading UI contextual'=>strpos($tpl,'data-evidence-grading-v0650')!==false,
'Three application row preserved'=>strpos($tpl,'Prototyping Workbench')!==false&&strpos($tpl,'Decision Studio')!==false&&strpos($tpl,'Site Intelligence')!==false,
'Six destination rail preserved'=>substr_count($tpl,'data-v0483-primary=')===6,
'Health disables numeric truth score'=>strpos($class,"'numericTruthScore'=>false")!==false,
'Health disables automatic consensus certification'=>strpos($class,"'automaticConsensusCertification'=>false")!==false,
'Health disables study-quality scoring'=>strpos($class,"'automaticStudyQualityScoring'=>false")!==false,
'Health disables citation-count authority scoring'=>strpos($class,"'citationCountAuthorityScoring'=>false")!==false,
'Evidence grading evaluate proxy route'=>strpos($core,'/compute/core/evidence-grading/v0650/evaluate')!==false,
'v0.65 stylesheet enqueued'=>strpos($plugclass,'sc-lab-evidence-grading-v0650')!==false,
'v0.65 JS module registered'=>strpos($plugclass,"'evidence-grading-v0650'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
