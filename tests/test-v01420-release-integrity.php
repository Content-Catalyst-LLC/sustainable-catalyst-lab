<?php
$root=dirname(__DIR__);$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$fail=function($x){fwrite(STDERR,"FAIL: $x\n");exit(1);};
(($m['releaseVersion']??'')==='0.142.0')||$fail('releaseVersion');
(($m['featureVersion']??'')==='0.142.0')||$fail('featureVersion');
(($m['integratedNeuralResearchWorkspaceVersion']??'')==='0.142.0')||$fail('feature marker');
(($m['v01420RequiredRouteCount']??0)===39)||$fail('route count');
(($m['v01420PanelCount']??0)===9)||$fail('panel count');
(($m['v01420AutomaticScientificValidity']??true)===false)||$fail('scientific validity boundary');
(($m['v01420AutomaticModelPromotion']??true)===false)||$fail('model promotion boundary');
(($m['v014001WordPressInstalledRuntimeScope']??false)===true)||$fail('runtime scope');
echo "PASS: Lab v0.142.0 release integrity\n";
