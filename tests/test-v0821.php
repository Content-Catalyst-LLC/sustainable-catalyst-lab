<?php
function must0821($c,$m){if(!$c){fwrite(STDERR,"FAIL - $m\n");exit(1);}echo "PASS - $m\n";}
$r=dirname(__DIR__);
$main=file_get_contents($r.'/sustainable-catalyst-lab.php');
$integrity=file_get_contents($r.'/includes/class-sc-lab-integrity-v02632.php');
$template=file_get_contents($r.'/templates/lab-app.php');
$plugin=file_get_contents($r.'/includes/class-sc-lab-plugin.php');
$runtime=file_get_contents($r.'/includes/class-sc-lab-runtime-repair-v0263.php');
must0821(strpos($main,'Version: 0.82.1')!==false,'plugin header v0.82.1');
must0821(strpos($main,"sc_lab_read_release_manifest(__DIR__)")!==false,'manifest loaded during plugin bootstrap');
must0821(strpos($main,"SC_LAB_RELEASE_VERSION', sc_lab_manifest_semver")!==false,'release constant derives from manifest');
must0821(strpos($main,"SC_LAB_PLATFORM_COMPAT_VERSION")!==false,'platform compatibility explicitly named');
must0821(strpos($main,'Deprecated compatibility alias')!==false,'generic SC_LAB_VERSION marked deprecated');
must0821(strpos($integrity,"'releaseVersion' => \$release_version")!==false,'runtime health exposes releaseVersion');
must0821(strpos($integrity,"'componentVersions' => \$component_versions")!==false,'runtime health exposes componentVersions');
must0821(strpos($integrity,"'releaseConsoleVersionConsistent' => \$console_consistent")!==false,'runtime health certifies Release Console consistency');
must0821(strpos($template,'data-sc-lab-release-console')!==false,'Release Console rendered in System Status');
must0821(strpos($template,"SC_LAB_RELEASE_VERSION")!==false,'server Release Console fallback uses release constant');
must0821(strpos($plugin,'release-console-v0821.js')!==false,'Release Console browser runtime enqueued');
must0821(strpos($runtime,"'releaseVersion' => defined('SC_LAB_RELEASE_VERSION')")!==false,'legacy runtime no longer labels platform alias pluginVersion');
require_once $r.'/includes/sc-lab-release-bootstrap.php';
$tmp=sys_get_temp_dir().'/sc-lab-v0821-'.bin2hex(random_bytes(5));mkdir($tmp.'/build',0777,true);
file_put_contents($tmp.'/build/sc-lab-release-manifest.json',json_encode(array('releaseVersion'=>'0.83.0','featureVersion'=>'0.83.0','platformVersion'=>'1.0.0')));
$m=sc_lab_read_release_manifest($tmp);
must0821(sc_lab_manifest_semver($m,'releaseVersion','0.82.1')==='0.83.0','manifest bootstrap follows next release without console code edit');
unlink($tmp.'/build/sc-lab-release-manifest.json');rmdir($tmp.'/build');rmdir($tmp);
