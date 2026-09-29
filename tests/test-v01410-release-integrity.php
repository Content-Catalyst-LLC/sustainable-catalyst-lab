<?php
$root=dirname(__DIR__);
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
  ($manifest['releaseVersion']??'')==='0.141.0',
  ($manifest['machineLearningExperimentWorkspaceVersion']??'')==='0.141.0',
  ($manifest['scientificResearchOperatingSystemVersion']??'')==='0.140.0',
  ($manifest['v01410RequiredRouteCount']??0)===27,
  ($manifest['v01410WorkspaceExecutionHandoff']??false)===true,
  ($manifest['v01410ResearchOSBridge']??false)===true,
  ($manifest['v01410BackwardCompatibleV01400']??false)===true,
  ($manifest['v01410ManifestScopeRepairRetainedV013901']??false)===true,
  ($manifest['v01410LabExecutesTraining']??true)===false,
  ($manifest['v01410PredictionIsEvidence']??true)===false,
  ($manifest['v01410AutomaticBestModelSelection']??true)===false,
  ($manifest['v01410AutomaticScientificValidity']??true)===false,
  strpos(file_get_contents($root.'/sustainable-catalyst-lab.php'),'Version: 0.141.0')!==false,
  is_file($root.'/backend/app/machine_learning_experiment_workspace_v01410.py'),
  is_file($root.'/backend/app/scientific_research_operating_system_v01400.py'),
  is_file($root.'/backend/app/release_integrity_scope_repair_v013901.py'),
  is_file($root.'/includes/class-sc-lab-machine-learning-experiment-workspace-v01410.php'),
);
foreach($checks as $i=>$ok){ if(!$ok){fwrite(STDERR,"FAIL v0.141.0 release integrity check $i\n"); exit(1);} }
echo "PASS: Lab v0.141.0 release integrity\n";
