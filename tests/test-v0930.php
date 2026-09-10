<?php
$root=dirname(__DIR__); function must0930($v,$m){if(!$v){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
must0930((bool)preg_match('/^ \* Version: 0\.93\.0$/m',$main),'plugin header v0.93.0');
must0930(strpos($main,'SC_Lab_SOC_Scenarios_V0930::init();')!==false,'scenario module initialized');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php');
must0930(strpos($rest,'/carbon-nature/soc/v1000/scenarios/project')!==false,'scenario project proxy route');
must0930(strpos($rest,'/carbon-nature/soc/v1000/scenarios/compare')!==false,'scenario compare proxy route');
must0930(strpos($rest,'/carbon-nature/soc/v1000/scenarios/sensitivity')!==false,'scenario sensitivity proxy route');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
must0930(strpos($plugin,"'socScenarios' => array(")!==false,'localized scenario config');
must0930(strpos($plugin,"'soil-carbon-scenarios-v0930'")!==false,'browser scenario module enqueue');
$template=file_get_contents($root.'/templates/lab-app.php');
must0930(strpos($template,'data-soc-v1000-root')!==false,'scenario studio workspace');
must0930(strpos($template,'Sustainable Catalyst supplies no default SOC change rate')!==false,'scenario rate boundary visible');
must0930(strpos($template,'Lab does not rank or recommend a scenario')!==false,'no recommendation boundary visible');
echo "PASS - Lab v0.93.0 / Carbon & Nature v0.10.0 PHP contracts\n";
