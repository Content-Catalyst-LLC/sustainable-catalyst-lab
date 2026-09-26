<?php
$root=dirname(__DIR__); function req($v,$m){if(!$v){fwrite(STDERR,"FAIL: $m\n");exit(1);}}
$boot=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');
req(strpos($boot,'Version: 0.135.9.0')!==false,'plugin version');
req(strpos($boot,'class-sc-lab-graph-studio-object-explorer-v013590.php')!==false,'object explorer PHP require');
req(strpos($plugin,'sc-lab-graph-studio-object-explorer-v013590.css')!==false,'object explorer CSS enqueue');
req(strpos($plugin,"'graph-studio-object-explorer-v013590'")!==false,'object explorer JS module enqueue');
req(strpos($template,'OBJECT EXPLORER v0.135.9.0')!==false,'template identity');
echo "PASS - Lab v0.135.9.0 PHP integration contract\n";
