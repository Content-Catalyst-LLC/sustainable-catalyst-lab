<?php
$root=dirname(__DIR__);
function ci_assert($c,$m){if(!$c){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$class=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$app=file_get_contents($root.'/assets/js/sc-lab-app.js');
ci_assert(strpos($plugin,'Version: 0.12.0')!==false,'Plugin header');
ci_assert(strpos($class,'sc_lab_civil_infrastructure')!==false,'Shortcode');
ci_assert(strpos($class,'civil-infrastructure-lab')!==false,'Module enqueue');
ci_assert(strpos($class,'sc-lab-v0120')!==false,'Style enqueue');
ci_assert(strpos($template,'data-module-panel="civil-infrastructure"')!==false,'Panel');
ci_assert(strpos($template,'data-civil-infrastructure-root')!==false,'Mount');
ci_assert(strpos($app,'CivilInfrastructureLab?.init')!==false,'Initializer');
echo "Civil/infrastructure PHP structural tests passed.\n";
