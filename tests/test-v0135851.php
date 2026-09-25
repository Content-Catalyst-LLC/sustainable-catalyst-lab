<?php
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$binding=file_get_contents(__DIR__.'/../assets/js/modules/graph-studio-live-binding-v013584.js');
$native=file_get_contents(__DIR__.'/../assets/js/modules/graph-studio-native-provenance-v013585.js');
if(strpos($plugin,"'graph-studio-provenance-authority-v0135851'")===false){fwrite(STDERR,"authority module missing\n");exit(1);}
if(strpos($plugin,'if ($module === \'graph-studio-provenance-interaction-recovery-v0135841\')')===false){fwrite(STDERR,"legacy recovery skip missing\n");exit(1);}
if(strpos($main,'class-sc-lab-graph-studio-provenance-authority-v0135851.php')===false){fwrite(STDERR,"authority REST class missing\n");exit(1);}
if(strpos($binding,'yieldProvenanceAuthority')===false || strpos($binding,'legacyObserverAttached')===false){fwrite(STDERR,"live binding authority yield missing\n");exit(1);}
if(strpos($native,"authorityRelease:'0.135.8.5.1'")===false){fwrite(STDERR,"native authority release marker missing\n");exit(1);}
echo "PASS Lab v0.135.8.5.1 provenance runtime authority contract\n";
