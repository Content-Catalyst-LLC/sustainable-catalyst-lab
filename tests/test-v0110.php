<?php
$root=dirname(__DIR__);
function mt_assert($c,$m){if(!$c){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$class=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$app=file_get_contents($root.'/assets/js/sc-lab-app.js');
mt_assert(strpos($plugin,'Version: 0.11.0')!==false,'Plugin header');
mt_assert(strpos($class,'sc_lab_mechanical_thermal')!==false,'Shortcode');
mt_assert(strpos($class,'mechanical-thermal-lab')!==false,'Module enqueue');
mt_assert(strpos($class,'sc-lab-v0110')!==false,'Style enqueue');
mt_assert(strpos($template,'data-lab-module="mechanical-thermal"')!==false,'Panel');
mt_assert(strpos($template,'data-mechanical-thermal-root')!==false,'Mount');
mt_assert(strpos($app,'MechanicalThermalLab?.init')!==false,'Initializer');
echo "Mechanical/thermal PHP structural tests passed.\n";
