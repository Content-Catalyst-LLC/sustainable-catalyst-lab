<?php
$root = dirname(__DIR__);
$required = array(
 'includes/class-sc-lab-global-science-v0280.php',
 'assets/js/modules/global-science-lab-v0280.js',
 'assets/css/sc-lab-global-science-v0280.css',
 'contracts/global-science-laboratory-v0280.json',
 'backend/app/global_science_v0280.py',
);
foreach ($required as $file) { if (!is_file($root . '/' . $file)) { fwrite(STDERR, "Missing $file\n"); exit(1); } }
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
if (!preg_match('/Version:\s*0\.28\.0/', $main)) { fwrite(STDERR,"Plugin header is not 0.28.0\n"); exit(1); }
if (strpos($main,'class-sc-lab-global-science-v0280.php')===false) { fwrite(STDERR,"Bootstrap include missing\n"); exit(1); }
$contract=json_decode(file_get_contents($root.'/contracts/global-science-laboratory-v0280.json'),true);
if (($contract['version']??'')!=='0.28.0' || empty($contract['freeSourceOnly'])) { fwrite(STDERR,"Contract invalid\n"); exit(1); }
echo "Lab v0.28.0 PHP contract passed.\n";
