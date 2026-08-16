<?php
$root = dirname(__DIR__);
define('ABSPATH', $root . '/');
define('WP_PLUGIN_DIR', dirname($root));
define('SC_LAB_FILE', $root . '/sustainable-catalyst-lab.php');
define('SC_LAB_DIR', $root . '/');
define('SC_LAB_PLUGIN_BASENAME', 'sustainable-catalyst-lab/sustainable-catalyst-lab.php');
define('SC_LAB_PLUGIN_SLUG', 'sustainable-catalyst-lab');
define('SC_LAB_RELEASE_VERSION', '0.70.0');
define('SC_LAB_FEATURE_VERSION', SC_LAB_RELEASE_VERSION);
define('SC_LAB_PLATFORM_VERSION', '1.0.0');
define('SC_LAB_VERSION', SC_LAB_PLATFORM_VERSION);
define('SC_LAB_INTEGRITY_CONTEXT', 'repository-validation');
function trailingslashit($value){return rtrim((string)$value,'/\\').'/';}
function plugin_basename($file){return basename(dirname($file)).'/'.basename($file);}
function get_option($name,$default=false){if($name==='active_plugins')return array('sustainable-catalyst-lab/sustainable-catalyst-lab.php');return $default;}
function is_multisite(){return false;}
function sanitize_key($value){return strtolower(preg_replace('/[^a-z0-9_\-]/','',(string)$value));}
function rest_ensure_response($value){return $value;}
require_once $root . '/includes/class-sc-lab-integrity-v02632.php';
$health=SC_Lab_Integrity_V02632::health();
$checks=array(
 'runtime health verified'=>!empty($health['ok'])&&($health['state']??null)==='verified',
 'repository validation context'=>($health['runtimeContext']??null)==='repository-validation',
 'repository candidate scope bounded'=>($health['pluginCandidateScope']??null)==='current-source-checkout'&&!($health['duplicatePluginRisk']??true),
 'route aliases verified'=>!empty($health['routeIntegrityVerified'])&&count(array_filter($health['routeChecks']??array(),fn($row)=>!empty($row['ok'])))===4,
 'release version is 0.70.0'=>($health['versions']['release']??null)==='0.70.0',
 'plugin header is 0.70.0'=>($health['versions']['pluginHeader']??null)==='0.70.0',
 'manifest release is 0.70.0'=>($health['versions']['manifestRelease']??null)==='0.70.0',
 'platform compatibility is 1.0.0'=>($health['versions']['platformCompatibility']??null)==='1.0.0',
 'release and platform lines independently consistent'=>!empty($health['releaseVersionConsistent'])&&!empty($health['platformVersionConsistent']),
 'manifest hashes verify'=>!empty($health['manifest']['verification']['ok'])
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n".json_encode($health,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");exit(1);}echo "PASS - $label\n";}
