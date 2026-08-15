<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-scientific-workflow-composer-v0570.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.57.0 workflow composer PHP class'=>is_file($root.'/includes/class-sc-lab-scientific-workflow-composer-v0570.php'),
 'v0.57.0 backend module'=>is_file($root.'/backend/app/scientific_workflow_composer.py'),
 'v0.57.0 JS module'=>is_file($root.'/assets/js/modules/scientific-workflow-composer-v0570.js'),
 'v0.57.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-scientific-workflow-composer-v0570.css'),
 'Workflow schema'=>is_file($root.'/contracts/scientific-workflow-composer-v0570.schema.json'),
 'Workflow run schema'=>is_file($root.'/contracts/scientific-workflow-run-v0570.schema.json'),
 'Stage result schema'=>is_file($root.'/contracts/scientific-workflow-stage-result-v0570.schema.json'),
 'Workflow policy'=>is_file($root.'/contracts/scientific-workflow-composer-policy-v0570.json'),
 'WordPress plugin header reports v0.57.0'=>preg_match('/^\s*\*\s*Version:\s*0\.57\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.57.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.57.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes workflow composer'=>strpos($bootstrap,'SC_Lab_Scientific_Workflow_Composer_V0570::init()')!==false,
 'Composer remains contextual in workflow workspace'=>strpos($template,'data-scientific-workflow-v0570')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health declares rerunnable workflows'=>strpos($class,"'rerunnableWorkflows'=>true")!==false,
 'Health disables automatic experiment execution'=>strpos($class,"'automaticExperimentExecution'=>false")!==false,
 'Health disables automatic registry promotion'=>strpos($class,"'automaticRegistryPromotion'=>false")!==false,
 'Compute proxy v0.57 run route'=>strpos($compute,"/compute/core/workflows/v0570/run")!==false,
 'Compute proxy v0.57 compare route'=>strpos($compute,"/compute/core/workflows/v0570/compare")!==false,
 'v0.57 stylesheet enqueued'=>strpos($plugin,'sc-lab-scientific-workflow-composer-v0570')!==false,
 'v0.57 JS module registered'=>strpos($plugin,"'scientific-workflow-composer-v0570'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
