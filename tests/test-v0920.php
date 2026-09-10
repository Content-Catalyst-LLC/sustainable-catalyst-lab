<?php
$root=dirname(__DIR__); function must($v,$m){if(!$v){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$main=file_get_contents($root.'/sustainable-catalyst-lab.php'); must((bool)preg_match('/^ \* Version: 0\.92\.0$/m',$main),'plugin header v0.92.0'); must(strpos($main,'SC_Lab_SOC_Uncertainty_V0920::init();')!==false,'uncertainty module initialized');
$rest=file_get_contents($root.'/includes/class-sc-lab-rest.php'); must(strpos($rest,'/carbon-nature/soc/v0900/uncertainty/replicates')!==false,'replicate proxy route'); must(strpos($rest,'/carbon-nature/soc/v0900/uncertainty/change')!==false,'change uncertainty proxy route');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php'); must(strpos($plugin,"'socUncertainty' => array(")!==false,'localized uncertainty config'); must(strpos($plugin,"'soil-carbon-uncertainty-v0920'")!==false,'browser module enqueue');
$template=file_get_contents($root.'/templates/lab-app.php'); must(strpos($template,'data-soc-v0900-root')!==false,'uncertainty workspace'); must(strpos($template,'sample variability is not total project uncertainty')!==false,'uncertainty boundary visible');
echo "PASS - Lab v0.92.0 / Carbon & Nature v0.9.0 PHP contracts\n";
