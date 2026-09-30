<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$bundle=json_decode(file_get_contents($root.'/build/sc-lab-frontend-bundle-v015204.json'),true);
$release=(string)($manifest['releaseVersion']??'');
if(!preg_match('/^0\.152\.0\.(?:4|[5-9]|[1-9][0-9]+)$/',$release)) exit(1);
if(empty($manifest['v015204FrontendRequestConsolidation'])) exit(2);
if(strpos($plugin,"sc-lab-ui-bundle-v015204.css")===false) exit(3);
if(!is_file($root.'/assets/js/sc-lab-bootstrap-v015204.js')) exit(4);
if(!is_file($root.'/assets/js/sc-lab-optional-modules-v015204.js')) exit(5);
if(($bundle['styleSourceCount']??0)<180) exit(6);
if(($bundle['optionalBundledModuleCount']??0)<200) exit(7);
foreach(['assets/css/sc-lab-ui-bundle-v015204.css','assets/js/sc-lab-bootstrap-v015204.js','assets/js/sc-lab-optional-modules-v015204.js'] as $f){if(!is_file($root.'/'.$f)||filesize($root.'/'.$f)<1000) exit(8);}
if($release==='0.152.0.4'){
    if(strpos($plugin,"sc-lab-bootstrap-v015204.js")===false) exit(9);
    if(strpos($plugin,"sc-lab-optional-modules-v015204.js")===false) exit(10);
} else {
    // v0.152.0.5+ retains the v0.152.0.4 bundle artifacts for rollback and
    // reproducibility but intentionally removes them from the eager front door.
    if(strpos($plugin,"wp_enqueue_script('sc-lab-app', SC_LAB_URL . 'assets/js/sc-lab-bootstrap-v015204.js'")!==false) exit(11);
    if(strpos($plugin,"wp_enqueue_script('sc-lab-optional-bundle-v015204'")!==false) exit(12);
}
echo "PASS - v0.152.0.4 bundle artifacts retained with patch-aware delivery contract\n";
