<?php
$root=dirname(__DIR__);
function must($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL: $msg\n");exit(1);}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
must((bool)preg_match('/^ \* Version: 0\\.89\\.0$/m',$main),'plugin header is v0.89.0');
must(strpos($main,'SC_Lab_Soil_Organic_Carbon_V0890::init();')!==false,'SOC module initialized');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
must(strpos($plugin,"'sc_lab_soil_organic_carbon'")!==false,'SOC focused shortcode registered');
must(strpos($plugin,"'sc_lab_soil_organic_carbon' => 'soil-organic-carbon'")!==false,'SOC focused shortcode routes to module');
must(strpos($plugin,"'soilOrganicCarbon' => array(")!==false,'SOC browser config exists');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php');
foreach(array('/carbon-nature/soc/v0600/health','/carbon-nature/soc/v0600/schema','/carbon-nature/soc/v0600/policies','/carbon-nature/soc/v0600/layer-stock','/carbon-nature/soc/v0600/profile-stock','/carbon-nature/soc/v0600/project-packet') as $route){must(strpos($rest,$route)!==false,"REST route $route exists");}
$template=file_get_contents($root.'/templates/lab-app.php');
must(strpos($template,"'Carbon & Nature' => array(")!==false,'Carbon & Nature nav group exists');
must(strpos($template,'data-lab-module="soil-organic-carbon"')!==false,'SOC panel exists');
$class=file_get_contents($root.'/includes/class-sc-lab-soil-organic-carbon-v0890.php');
must(strpos($class,"const DOMAIN_VERSION = '0.6.0'")!==false,'domain identity is 0.6.0');
must(strpos($class,'stockChangeNotInferred')!==false,'stock-change guardrail present');
echo "PASS - Lab v0.89.0 / Carbon & Nature v0.6.0 PHP contracts\n";
