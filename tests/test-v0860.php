<?php
function must0860($c,$m){if(!$c){fwrite(STDERR,"FAIL - $m\n");exit(1);}echo "PASS - $m\n";}
$r=dirname(__DIR__);
$main=file_get_contents($r.'/sustainable-catalyst-lab.php');
$wp=file_get_contents($r.'/includes/class-sc-lab-system-dynamics-feedback-v0860.php');
$proxy=file_get_contents($r.'/includes/class-sc-lab-python-compute-core-v0261.php');
$plugin=file_get_contents($r.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($r.'/templates/lab-app.php');
$console=file_get_contents($r.'/assets/js/modules/release-console-v0821.js');
must0860(strpos($main,'Version: 0.86.0')!==false,'plugin header v0.86.0');
must0860(strpos($main,'SC_Lab_System_Dynamics_Feedback_V0860::init()')!==false,'v0.86 WordPress module initialized');
must0860(strpos($wp,"system-dynamics-feedback-stock-flow-ready")!==false,'v0.86 WordPress health identity');
must0860(strpos($proxy,'dynamic-systems/v0860/stock-flow/simulate')!==false,'WordPress proxies v0.86 stock-flow simulation');
must0860(strpos($proxy,'dynamic-systems/v0860/feedback/analyze')!==false,'WordPress proxies v0.86 feedback analysis');
must0860(strpos($plugin,"'system-dynamics-v0860'")!==false,'v0.86 browser module enqueued');
must0860(strpos($template,'data-sd-v0860-root')!==false,'v0.86 systems workspace visible in Model Studio');
must0860(strpos($console,"modeling/v0860/health")!==false,'Release Console reads systems modeling component');
must0860(strpos($console,"visualization/v0850/health")!==false,'Release Console preserves WebGL2 visualization component');
