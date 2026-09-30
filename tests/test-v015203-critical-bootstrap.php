<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$app=file_get_contents($root.'/assets/js/sc-lab-app.js');
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(strpos($main,'Version: 0.152.0.3')===false) exit(1);
if(($manifest['releaseVersion']??'')!=='0.152.0.3') exit(2);
if(strpos($plugin, "$" . "critical_modules = array('core','projects','workspace','feeds','project-workspace-v0280');")===false) exit(3);
if(strpos($app,'function workspaceApi()')===false) exit(4);
if(strpos($app,"Scientific signals are still loading. Core Lab navigation is ready.")===false) exit(5);
if(strpos($app,"root.dataset.scLabBootstrapVersion = '0.152.0.3'")===false) exit(6);
echo "PASS - v0.152.0.3 critical bootstrap dependencies and graceful fallbacks\n";
