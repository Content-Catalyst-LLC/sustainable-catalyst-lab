<?php
$root=dirname(__DIR__);
function need($cond,$msg){ if(!$cond){fwrite(STDERR,"FAIL - $msg\n"); exit(1);} }
$js=file_get_contents($root.'/assets/js/modules/graph-studio-native-provenance-v013585.js');
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
need(strpos($main,'Version: 0.135.8.5.2')!==false,'plugin version');
need(strpos($js,"VERSION='0.135.8.5.2'")!==false,'native JS version');
need(strpos($js,'function updateVisibility()')!==false,'incremental visibility updater');
need(strpos($js,'function updateLayout()')!==false,'incremental layout updater');
need(strpos($js,"addEventListener('input',relationHandler")!==false,'relationship input handler');
need(strpos($js,"addEventListener('change',relationHandler")!==false,'relationship change handler');
need(strpos($js,'projectPersistenceDebounceMs:220')!==false,'debounced project persistence');
need(strpos($js,'S.fullRenderCount++')!==false,'full render diagnostics');
need(strpos($js,'S.incrementalUpdateCount++')!==false,'incremental diagnostics');
echo "PASS - Lab v0.135.8.5.2 incremental provenance interaction contract\n";
