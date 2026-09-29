<?php
$root=dirname(__DIR__);
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
  ($manifest['releaseVersion']??'')==='0.140.0',
  ($manifest['scientificResearchOperatingSystemVersion']??'')==='0.140.0',
  ($manifest['v01400RequiredRouteCount']??0)===25,
  ($manifest['v01400LifecycleOrchestration']??false)===true,
  ($manifest['v01400BackwardCompatibleV01390']??false)===true,
  ($manifest['v01400AutomaticScientificValidity']??true)===false,
  strpos(file_get_contents($root.'/sustainable-catalyst-lab.php'),'Version: 0.140.0')!==false,
  is_file($root.'/backend/app/scientific_research_operating_system_v01400.py'),
  is_file($root.'/includes/class-sc-lab-scientific-research-operating-system-v01400.php'),
);
foreach($checks as $i=>$ok){ if(!$ok){fwrite(STDERR,"FAIL v0.140.0 release integrity check $i\n"); exit(1);} }
echo "PASS: Lab v0.140.0 release integrity\n";
