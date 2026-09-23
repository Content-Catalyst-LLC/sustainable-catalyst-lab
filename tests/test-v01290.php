<?php
$root=dirname(__DIR__);
$files=array(
 'contracts/research-reproduction-replication-studio-v01290.schema.json',
 'contracts/research-reproduction-replication-studio-policy-v01290.json',
 'includes/class-sc-lab-research-reproduction-replication-studio-v01290.php',
 'assets/js/modules/research-reproduction-replication-studio-v01290.js',
 'assets/css/sc-lab-research-reproduction-replication-studio-v01290.css'
);
foreach($files as $f){ if(!is_file($root.'/'.$f)){fwrite(STDERR,"missing $f\n");exit(1);} }
$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??null)!=='0.129.0'||($m['researchReproductionReplicationStudioVersion']??null)!=='0.129.0'||($m['v01290RequiredRouteCount']??null)!==30){fwrite(STDERR,"manifest mismatch\n");exit(1);}
echo "PASS - Lab v0.129.0 WordPress reproduction/replication surface\n";
