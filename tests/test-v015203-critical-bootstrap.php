<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$app=file_get_contents($root.'/assets/js/sc-lab-app.js');
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(!preg_match('/Version:\s+0\.152\.0\.[3-9]/',$main)) exit(1);
if(version_compare(($manifest['releaseVersion']??'0.0.0'),'0.152.0.3','<')) exit(2);
if(strpos($plugin, "$" . "critical_modules = array('core','projects','workspace','feeds','project-workspace-v0280');")===false) exit(3);
if(strpos($app,'function workspaceApi()')===false) exit(4);
if(strpos($app,"Scientific signals are still loading. Core Lab navigation is ready.")===false) exit(5);
if(!preg_match("/root\.dataset\.scLabBootstrapVersion = '0\.152\.0\.[3-9]'/",$app)) exit(6);
echo "PASS - v0.152.0.3 critical bootstrap dependencies and graceful fallbacks\n";
