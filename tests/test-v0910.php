<?php
$root=dirname(__DIR__); function must($ok,$m){if(!$ok){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php'); must((bool)preg_match('/^ \* Version: 0\.91\.0$/m',$main),'plugin header v0.91.0'); must(strpos($main,'SC_Lab_SOC_Change_V0910::init();')!==false,'SOC change module initialized');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php'); foreach(array('/carbon-nature/soc/v0800/change/health','/carbon-nature/soc/v0800/change/schema','/carbon-nature/soc/v0800/change/policies','/carbon-nature/soc/v0800/change/compare','/carbon-nature/soc/v0800/change/series','/carbon-nature/soc/v0800/change/project-packet') as $route){must(strpos($rest,$route)!==false,"REST route $route exists");}
$template=file_get_contents($root.'/templates/lab-app.php'); must(strpos($template,'data-soc-v0800-root')!==false,'SOC change workspace exists'); must(strpos($template,'SOC Change &amp; Sequestration Model')!==false,'SOC change title exists');
$class=file_get_contents($root.'/includes/class-sc-lab-soc-change-v0910.php'); must(strpos($class,"const DOMAIN_VERSION = '0.8.0'")!==false,'domain v0.8.0'); must(strpos($class,'positiveStockChangeNotTreatedAsAttributedSequestration')!==false,'attribution guardrail');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php'); must(strpos($plugin,"'socChange' => array(")!==false,'SOC change configuration localized'); must(strpos($plugin,'soil-carbon-change-v0910')!==false,'SOC change browser module enqueued');
echo "PASS - Lab v0.91.0 / Carbon & Nature v0.8.0 PHP contracts\n";
