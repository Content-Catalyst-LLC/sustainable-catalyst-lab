<?php
$root=dirname(__DIR__);$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');$class=file_get_contents($root.'/includes/class-sc-lab-scientific-theory-v0690.php');$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$plugclass=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array(
'WordPress plugin header reports v0.69.0'=>strpos($plugin,'Version: 0.69.0')!==false,
'Release constant reports v0.69.0'=>strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.69.0")!==false,
'Platform compatibility remains v1.0.0'=>strpos($plugin,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
'Bootstrap initializes v0.69 scientific theory'=>strpos($plugin,'SC_Lab_Scientific_Theory_V0690::init()')!==false,
'v0.68 hierarchical modeling remains initialized'=>strpos($plugin,'SC_Lab_Hierarchical_Modeling_V0680::init()')!==false,
'Scientific theory UI contextual'=>strpos($tpl,'data-scientific-theory-v0690')!==false,
'Three application row preserved'=>strpos($tpl,'Prototyping Workbench')!==false&&strpos($tpl,'Decision Studio')!==false&&strpos($tpl,'Site Intelligence')!==false,
'Six destination rail preserved'=>substr_count($tpl,'data-v0483-primary=')===6,
'Health disables automatic theory proof'=>strpos($class,"'automaticTheoryProof'=>false")!==false,
'Health disables automatic causal certification'=>strpos($class,"'automaticCausalCertification'=>false")!==false,
'Health disables universal generalization'=>strpos($class,"'automaticUniversalGeneralization'=>false")!==false,
'Health rejects raw scientific data'=>strpos($class,"'rawScientificDataAccepted'=>false")!==false,
'Health rejects participant-level data'=>strpos($class,"'participantLevelDataAccepted'=>false")!==false,
'Scientific theory evaluate proxy route'=>strpos($core,'/compute/core/scientific-theory/v0690/evaluate')!==false,
'Scientific theory graph proxy route'=>strpos($core,'/compute/core/scientific-theory/v0690/graph')!==false,
'v0.69 stylesheet enqueued'=>strpos($plugclass,'sc-lab-scientific-theory-v0690')!==false,
'v0.69 JS module registered'=>strpos($plugclass,"'scientific-theory-v0690'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
