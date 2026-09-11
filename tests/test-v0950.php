<?php
$root=dirname(__DIR__); function must0950($v,$m){if(!$v){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
must0950((bool)preg_match('/^ \* Version: 0\.95\.0$/m',$main),'plugin header v0.95.0');
must0950(strpos($main,'SC_Lab_Carbon_MRV_Registry_V0950::init();')!==false,'Carbon MRV registry initialized');
$class=file_get_contents($root.'/includes/class-sc-lab-carbon-mrv-registry-v0950.php');
must0950(strpos($class,"const DOMAIN_VERSION='0.12.0'")!==false,'domain v0.12.0');
must0950(strpos($class,'registryIsNotExternalProtocol')!==false,'external protocol boundary');
must0950(strpos($class,"'automaticMethodSelection'=>false")!==false,'automatic method selection disabled');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php');
foreach(array('/carbon-nature/mrv/v1200/registry/health','/carbon-nature/mrv/v1200/registry/schema','/carbon-nature/mrv/v1200/registry/policies','/carbon-nature/mrv/v1200/registry/methods','/carbon-nature/mrv/v1200/registry/compare','/carbon-nature/mrv/v1200/registry/readiness','/carbon-nature/mrv/v1200/registry/project-packet') as $route){must0950(strpos($rest,$route)!==false,"REST route $route exists");}
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
must0950(strpos($plugin,"'carbonMrvRegistry' => array(")!==false,'localized Carbon MRV config');
must0950(strpos($plugin,"'carbon-mrv-registry-v0950'")!==false,'browser MRV module enqueue');
must0950(strpos($plugin,"'sc-lab-carbon-mrv-registry-v0950'")!==false,'MRV stylesheet enqueue');
$template=file_get_contents($root.'/templates/lab-app.php');
must0950(strpos($template,'data-mrv-v1200-root')!==false,'Carbon MRV workspace');
must0950(strpos($template,'Registry profile ≠ external protocol')!==false,'external protocol boundary visible');
must0950(strpos($template,'Documentation readiness ≠ methodology eligibility')!==false,'readiness boundary visible');
echo "PASS - Lab v0.95.0 / Carbon & Nature v0.12.0 PHP contracts\n";
