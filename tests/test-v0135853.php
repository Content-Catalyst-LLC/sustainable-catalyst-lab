<?php
$root=dirname(__DIR__);
function req($v,$m){ if(!$v){fwrite(STDERR,"FAIL: $m\n"); exit(1);} }
$boot=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
req(strpos($boot,'Version: 0.135.8.5.3')!==false,'plugin version');
req(strpos($boot,'class-sc-lab-graph-studio-context-relationships-v0135853.php')!==false,'context PHP require');
req(strpos($plugin,'sc-lab-graph-studio-context-relationships-v0135853.css')!==false,'context CSS enqueue');
req(strpos($template,'CONTEXT-AWARE PROVENANCE v0.135.8.5.3')!==false,'template identity');
echo "PASS - Lab v0.135.8.5.3 PHP integration contract\n";
