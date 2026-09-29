<?php
$root=dirname(__DIR__);$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$fail=function($x){fwrite(STDERR,"FAIL: $x\n");exit(1);};
(($m['releaseVersion']??'')==='0.144.0')||$fail('releaseVersion');
(($m['featureVersion']??'')==='0.144.0')||$fail('featureVersion');
(($m['statisticalEconometricResearchWorkspaceVersion']??'')==='0.144.0')||$fail('feature marker');
(($m['computationalLinguisticsResearchWorkspaceVersion']??'')==='0.143.0')||$fail('predecessor marker');
(($m['v01440RequiredRouteCount']??0)===52)||$fail('route count');
(($m['v01440ExplicitEstimandModelSeparation']??false)===true)||$fail('estimand separation');
(($m['v01440LabExecutesStatisticalEstimation']??true)===false)||$fail('execution boundary');
(($m['v01440AutomaticCausalInference']??true)===false)||$fail('causal boundary');
(($m['v01440AutomaticWinnerSelection']??true)===false)||$fail('winner boundary');
(($m['v01440AutomaticScientificValidity']??true)===false)||$fail('validity boundary');
(($m['v014001WordPressInstalledRuntimeScope']??false)===true)||$fail('runtime scope');
echo "PASS: Lab v0.144.0 release integrity\n";
