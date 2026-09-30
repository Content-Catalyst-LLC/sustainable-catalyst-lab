<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$safe=file_get_contents($root.'/includes/class-sc-lab-production-safe-boot-v015206.php');
$manifest=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=array(
    'plugin header'=>strpos($main,'Version: 0.152.0.6')!==false,
    'manifest release'=>($manifest['releaseVersion']??null)==='0.152.0.6',
    'feature line retained'=>($manifest['featureVersion']??null)==='0.152.0',
    'new class loaded'=>strpos($main,'class-sc-lab-production-safe-boot-v015206.php')!==false,
    'late footer gate flag'=>!empty($manifest['v015206LateFooterAssetGate']),
    'legacy presentation isolation flag'=>!empty($manifest['v015206LegacyPresentationIsolation']),
    'canonical release presentation flag'=>!empty($manifest['v015206CanonicalReleasePresentation']),
    'production budget banner disabled flag'=>!empty($manifest['v015206ProductionBudgetBannerDisabled']),
    'integrity notice authority flag'=>!empty($manifest['v015206IntegrityNoticeAuthority']),
    'backend unchanged'=>isset($manifest['v015206BackendBehaviorChanged']) && $manifest['v015206BackendBehaviorChanged']===false,
    'footer queue gate'=>strpos($safe,"'wp_print_footer_scripts'")!==false && strpos($safe,', 19)')!==false,
    'legacy integrity notice removed'=>strpos($safe,"remove_action('admin_notices', array('SC_Lab_Integrity_V02632', 'admin_notice'))")!==false,
    'health-backed integrity notice'=>strpos($safe,'SC_Lab_Integrity_V02632::health()')!==false,
    'new safe bootstrap'=>strpos($safe,'sc-lab-safe-bootstrap-v015206.js')!==false,
    'legacy production front disabled at source'=>substr_count($plugin,"version_compare(SC_LAB_RELEASE_VERSION, '0.152.0.6', '>=')")>=2,
    'old optional mega bundle still not eagerly enqueued'=>strpos($plugin,"wp_enqueue_script('sc-lab-optional-bundle-v015204'")===false,
);
foreach($checks as $name=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $name\n");exit(1);}}
echo "PASS - v0.152.0.6 safe-boot stabilization, late asset gate, canonical release presentation, and integrity notice authority\n";
