<?php
$root=dirname(__DIR__);$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');$class=file_get_contents($root.'/includes/class-sc-lab-causal-inference-v0670.php');$core=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');$tpl=file_get_contents($root.'/templates/lab-app.php');$plugclass=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$checks=array(
'WordPress plugin header reports v0.67.0'=>strpos($plugin,'Version: 0.67.0')!==false,
'Release constant reports v0.67.0'=>strpos($plugin,"SC_LAB_RELEASE_VERSION', '0.67.0")!==false,
'Platform compatibility remains v1.0.0'=>strpos($plugin,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
'Bootstrap initializes v0.67 causal inference'=>strpos($plugin,'SC_Lab_Causal_Inference_V0670::init()')!==false,
'v0.66 scientific argumentation remains initialized'=>strpos($plugin,'SC_Lab_Scientific_Argumentation_V0660::init()')!==false,
'Causal inference UI contextual'=>strpos($tpl,'data-causal-inference-v0670')!==false,
'Three application row preserved'=>strpos($tpl,'Prototyping Workbench')!==false&&strpos($tpl,'Decision Studio')!==false&&strpos($tpl,'Site Intelligence')!==false,
'Six destination rail preserved'=>substr_count($tpl,'data-v0483-primary=')===6,
'Health disables automatic causal proof'=>strpos($class,"'automaticCausalProof'=>false")!==false,
'Health disables automatic assumption satisfaction'=>strpos($class,"'automaticAssumptionSatisfaction'=>false")!==false,
'Health rejects raw scientific data'=>strpos($class,"'rawScientificDataAccepted'=>false")!==false,
'Health rejects participant-level data'=>strpos($class,"'participantLevelDataAccepted'=>false")!==false,
'Causal inference evaluate proxy route'=>strpos($core,'/compute/core/causal-inference/v0670/evaluate')!==false,
'v0.67 stylesheet enqueued'=>strpos($plugclass,'sc-lab-causal-inference-v0670')!==false,
'v0.67 JS module registered'=>strpos($plugclass,"'causal-inference-v0670'")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
