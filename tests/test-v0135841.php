<?php
$root=dirname(__DIR__);
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$binding=file_get_contents($root.'/assets/js/modules/graph-studio-live-binding-v013584.js');
$guard=file_get_contents($root.'/assets/js/modules/graph-studio-provenance-interaction-recovery-v0135841.js');
if (strpos($plugin,"'graph-studio-provenance-interaction-recovery-v0135841'")===false) {fwrite(STDERR,"v0.135.8.4.1 module not enqueued\n");exit(1);}
if (strpos($main,'class-sc-lab-graph-studio-provenance-interaction-recovery-v0135841.php')===false) {fwrite(STDERR,"v0.135.8.4.1 REST class not loaded\n");exit(1);}
if (strpos($binding,'layoutButton?.click()')!==false) {fwrite(STDERR,"programmatic layout click regression remains\n");exit(1);}
foreach (array('bindProvenanceDelegation','applyProvenanceLayout','setProvenanceLayout','selectProvenanceNode','programmaticLayoutClick:false') as $needle) if (strpos($binding,$needle)===false) {fwrite(STDERR,"missing interaction repair: $needle\n");exit(1);}
foreach (array('delegatedInteraction:true','programmaticLayoutClick:false','sc-lab:provenance-interaction-recovered') as $needle) if (strpos($guard,$needle)===false) {fwrite(STDERR,"missing v0.135.8.4.1 guard: $needle\n");exit(1);}
echo "PASS - Lab v0.135.8.4.1 provenance interaction lifecycle contract\n";
