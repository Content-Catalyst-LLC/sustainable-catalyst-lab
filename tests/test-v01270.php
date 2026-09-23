<?php
$root=dirname(__DIR__);
$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??null)!=='0.127.0') { fwrite(STDERR,"FAIL releaseVersion\n"); exit(1); }
if(($m['scientificTimeSeriesLaboratoryVersion']??null)!=='0.127.0') { fwrite(STDERR,"FAIL feature version\n"); exit(1); }
if(($m['v01270RequiredRouteCount']??null)!==31) { fwrite(STDERR,"FAIL route count\n"); exit(1); }
if(($m['v01270MethodFamilyCount']??null)!==15) { fwrite(STDERR,"FAIL method count\n"); exit(1); }
echo "PASS - Lab v0.127.0 WordPress time-series contract\n";
