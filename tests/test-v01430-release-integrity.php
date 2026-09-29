<?php
$root=dirname(__DIR__);$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$fail=function($x){fwrite(STDERR,"FAIL: $x\n");exit(1);};
(($m['releaseVersion']??'')==='0.143.0')||$fail('releaseVersion');
(($m['featureVersion']??'')==='0.143.0')||$fail('featureVersion');
(($m['computationalLinguisticsResearchWorkspaceVersion']??'')==='0.143.0')||$fail('feature marker');
(($m['v01430RequiredRouteCount']??0)===48)||$fail('route count');
(($m['v01430OriginalLanguageFirst']??false)===true)||$fail('original language');
(($m['v01430TranslationAsDerivedRepresentation']??false)===true)||$fail('translation derivation');
(($m['v01430AutomaticSemanticEquivalence']??true)===false)||$fail('semantic equivalence boundary');
(($m['v01430AutomaticScientificValidity']??true)===false)||$fail('scientific validity boundary');
(($m['v014001WordPressInstalledRuntimeScope']??false)===true)||$fail('runtime scope');
echo "PASS: Lab v0.143.0 release integrity\n";
