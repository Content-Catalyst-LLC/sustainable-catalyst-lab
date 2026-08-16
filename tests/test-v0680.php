<?php
$root=dirname(__DIR__);$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');$class=file_get_contents($root.'/includes/class-sc-lab-hierarchical-modeling-v0680.php');$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$plugclass=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array(
'WordPress plugin header reports v0.68.0'=>strpos($plugin,'Version: 0.68.0')!==false,
'Release constant reports v0.68.0'=>strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.68.0")!==false,
'Platform compatibility remains v1.0.0'=>strpos($plugin,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
'Bootstrap initializes v0.68 hierarchical modeling'=>strpos($plugin,'SC_Lab_Hierarchical_Modeling_V0680::init()')!==false,
'v0.67 causal inference remains initialized'=>strpos($plugin,'SC_Lab_Causal_Inference_V0670::init()')!==false,
'Hierarchical modeling UI contextual'=>strpos($tpl,'data-hierarchical-modeling-v0680')!==false,
'Three application row preserved'=>strpos($tpl,'Prototyping Workbench')!==false&&strpos($tpl,'Decision Studio')!==false&&strpos($tpl,'Site Intelligence')!==false,
'Six destination rail preserved'=>substr_count($tpl,'data-v0483-primary=')===6,
'Health disables automatic generalizability'=>strpos($class,"'automaticGeneralizability'=>false")!==false,
'Health disables automatic ecological inference'=>strpos($class,"'automaticEcologicalInference'=>false")!==false,
'Health disables automatic causal proof'=>strpos($class,"'automaticCausalProof'=>false")!==false,
'Health rejects raw scientific data'=>strpos($class,"'rawScientificDataAccepted'=>false")!==false,
'Health rejects participant-level data'=>strpos($class,"'participantLevelDataAccepted'=>false")!==false,
'Hierarchical modeling evaluate proxy route'=>strpos($core,'/compute/core/hierarchical-modeling/v0680/evaluate')!==false,
'Hierarchical modeling fit proxy route'=>strpos($core,'/compute/core/hierarchical-modeling/v0680/fit')!==false,
'v0.68 stylesheet enqueued'=>strpos($plugclass,'sc-lab-hierarchical-modeling-v0680')!==false,
'v0.68 JS module registered'=>strpos($plugclass,"'hierarchical-modeling-v0680'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
