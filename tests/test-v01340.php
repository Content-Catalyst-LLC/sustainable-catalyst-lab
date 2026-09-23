<?php
$root=dirname(__DIR__);
$required=array(
 'includes/class-sc-lab-evidence-synthesis-intelligence-ii-v01340.php',
 'assets/js/modules/evidence-synthesis-intelligence-ii-v01340.js',
 'assets/css/sc-lab-evidence-synthesis-intelligence-ii-v01340.css',
 'contracts/evidence-synthesis-intelligence-ii-v01340.schema.json',
 'contracts/evidence-synthesis-intelligence-ii-policy-v01340.json'
);
foreach($required as $f){if(!is_file($root.'/'.$f)){fwrite(STDERR,"MISSING $f\n");exit(1);}}
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
if(strpos($plugin,'Version: 0.134.0')===false){fwrite(STDERR,"plugin version mismatch\n");exit(1);}
echo "PASS: v0.134.0 WordPress assertions\n";
