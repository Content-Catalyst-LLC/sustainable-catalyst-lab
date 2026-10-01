<?php
$root=dirname(__DIR__);
$php=file_get_contents($root.'/includes/class-sc-lab-research-program-portfolio-orchestration-v01610.php');
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$repair=file_get_contents($root.'/assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js');
$checks=array(
 strpos($php,"const VERSION='0.161.0'")!==false,
 substr_count($php,'research-program-portfolio-orchestration/v01610')>=8,
 strpos($php,'operations_permission')!==false,
 strpos($php,"return is_user_logged_in();")!==false,
 strpos($php,'signed_headers')!==false,
 strpos($plugin,'Version: 0.161.0')!==false,
 strpos($plugin,'SC_Lab_Research_Program_Portfolio_Orchestration_V01610::init();')!==false,
 strpos($repair,'program-portfolio/v01610')!==false,
 strpos($repair,'data-v01610-workspace')!==false,
);
foreach($checks as $i=>$ok){if(!$ok){fwrite(STDERR,"FAIL v0.161.0 PHP contract #$i\n");exit(1);}}
echo "PASS - v0.161.0 PHP/authorization contract\n";
