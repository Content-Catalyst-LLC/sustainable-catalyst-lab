<?php
$root=dirname(__DIR__);
$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??null)!=='0.128.0') { fwrite(STDERR,"FAIL releaseVersion\n"); exit(1); }
if(($m['experimentalDesignPowerAnalysisVersion']??null)!=='0.128.0') { fwrite(STDERR,"FAIL feature version\n"); exit(1); }
if(($m['v01280RequiredRouteCount']??null)!==30) { fwrite(STDERR,"FAIL route count\n"); exit(1); }
if(($m['v01280MethodFamilyCount']??null)!==15) { fwrite(STDERR,"FAIL method count\n"); exit(1); }
echo "PASS - Lab v0.128.0 WordPress experimental-design contract\n";
