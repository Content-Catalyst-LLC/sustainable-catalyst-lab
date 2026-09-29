<?php
$root=dirname(__DIR__);$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$fail=function($x){fwrite(STDERR,"FAIL: $x\n");exit(1);};
(($m['releaseVersion']??'')==='0.141.8')||$fail('releaseVersion');
(($m['featureVersion']??'')==='0.141.8')||$fail('featureVersion');
(($m['reproducibleNeuralResearchPackageVersion']??'')==='0.141.8')||$fail('feature marker');
(($m['v01418RequiredRouteCount']??0)===36)||$fail('route count');
(($m['v01418PackageCompletenessIsScientificValidity']??true)===false)||$fail('validity boundary');
(($m['v01418AutomaticReproductionCertification']??true)===false)||$fail('reproduction boundary');
(($m['v01418AutomaticReplicationCertification']??true)===false)||$fail('replication boundary');
(($m['v014001WordPressInstalledRuntimeScope']??false)===true)||$fail('runtime scope');
echo "PASS: Lab v0.141.8 release integrity\n";
