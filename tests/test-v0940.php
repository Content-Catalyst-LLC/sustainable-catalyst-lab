<?php
$root=dirname(__DIR__); function must0940($v,$m){if(!$v){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
must0940((bool)preg_match('/^ \* Version: 0\.94\.0$/m',$main),'plugin header v0.94.0');
must0940(strpos($main,'SC_Lab_Whole_Farm_GHG_V0940::init();')!==false,'Whole-Farm GHG module initialized');
$class=file_get_contents($root.'/includes/class-sc-lab-whole-farm-ghg-v0940.php');
must0940(strpos($class,"const DOMAIN_VERSION='0.11.0'")!==false,'domain v0.11.0');
must0940(strpos($class,'wholeFarmBalanceIsNotVerification')!==false,'verification guardrail');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php');
foreach(array('/carbon-nature/ghg/v1100/balance/health','/carbon-nature/ghg/v1100/balance/schema','/carbon-nature/ghg/v1100/balance/policies','/carbon-nature/ghg/v1100/balance/entry','/carbon-nature/ghg/v1100/balance/calculate','/carbon-nature/ghg/v1100/balance/project-packet') as $route){must0940(strpos($rest,$route)!==false,"REST route $route exists");}
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
must0940(strpos($plugin,"'wholeFarmGhg' => array(")!==false,'localized Whole-Farm GHG config');
must0940(strpos($plugin,"'whole-farm-ghg-v0940'")!==false,'browser GHG module enqueue');
must0940(strpos($plugin,"'sc-lab-whole-farm-ghg-v0940'")!==false,'GHG stylesheet enqueue');
$template=file_get_contents($root.'/templates/lab-app.php');
must0940(strpos($template,'data-ghg-v1100-root')!==false,'Whole-Farm GHG workspace');
must0940(strpos($template,'Sustainable Catalyst supplies no default non-CO₂ GWP')!==false,'explicit GWP boundary visible');
must0940(strpos($template,'Whole-farm balance ≠ verification')!==false,'verification boundary visible');
echo "PASS - Lab v0.94.0 / Carbon & Nature v0.11.0 PHP contracts\n";
