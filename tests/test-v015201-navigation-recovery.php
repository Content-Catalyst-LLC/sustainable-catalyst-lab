<?php
$root=dirname(__DIR__);
$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(version_compare(($m['releaseVersion']??'0.0.0'),'0.152.0.1','<')) exit(1);
$p=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
foreach(array('sc-lab-navigation-recovery-v015201','critical_modules','optional Lab modules must not form a 247-script cumulative dependency chain') as $x){if(strpos($p,$x)===false)exit(2);}
$j=$root.'/assets/js/sc-lab-navigation-recovery-v015201.js'; if(!is_file($j))exit(3);
$b=file_get_contents($root.'/sustainable-catalyst-lab.php'); if(strpos($b,'0.152.0.')===false)exit(4);
echo "PASS - v0.152.0.1 navigation recovery PHP integrity\n";
