<?php
$source = dirname(__DIR__);
$tmp = sys_get_temp_dir() . '/sc-lab-v0700-r1-repository-' . getmypid() . '-' . bin2hex(random_bytes(4));
@mkdir($tmp, 0777, true);
$link = $tmp . '/sustainable-catalyst-lab-repository';
if (!@symlink($source, $link)) { fwrite(STDERR, "FAIL - unable to create repository-validation symlink\n"); exit(1); }
$decoy = $tmp . '/sustainable-catalyst-lab-repo';
@mkdir($decoy, 0777, true);
file_put_contents($decoy . '/sustainable-catalyst-lab.php', "<?php\n/*\nPlugin Name: Sustainable Catalyst Lab\nVersion: 1.0.0\n*/\n");
register_shutdown_function(function() use ($link,$decoy,$tmp){ @unlink($link); @unlink($decoy.'/sustainable-catalyst-lab.php'); @rmdir($decoy); @rmdir($tmp); });

define('ABSPATH', $link . '/');
define('WP_PLUGIN_DIR', $tmp);
define('SC_LAB_FILE', $link . '/sustainable-catalyst-lab.php');
define('SC_LAB_DIR', $link . '/');
define('SC_LAB_PLUGIN_BASENAME', 'sustainable-catalyst-lab/sustainable-catalyst-lab.php');
define('SC_LAB_PLUGIN_SLUG', 'sustainable-catalyst-lab');
define('SC_LAB_RELEASE_VERSION', '0.70.0');
define('SC_LAB_FEATURE_VERSION', SC_LAB_RELEASE_VERSION);
define('SC_LAB_PLATFORM_VERSION', '1.0.0');
define('SC_LAB_VERSION', SC_LAB_PLATFORM_VERSION);
define('SC_LAB_INTEGRITY_CONTEXT', 'repository-validation');
function trailingslashit($value){return rtrim((string)$value,'/\\').'/';}
function plugin_basename($file){return basename(dirname($file)).'/'.basename($file);}
function get_option($name,$default=false){return $default;}
function is_multisite(){return false;}
function sanitize_key($value){return strtolower(preg_replace('/[^a-z0-9_\-]/','',(string)$value));}
function rest_ensure_response($value){return $value;}
require_once $source . '/includes/class-sc-lab-integrity-v02632.php';
$health=SC_Lab_Integrity_V02632::health();
$routeChecks=$health['routeChecks']??array();
$checks=array(
 'repository checkout with noncanonical folder verifies'=>!empty($health['ok'])&&($health['state']??null)==='verified',
 'repository context explicit'=>($health['runtimeContext']??null)==='repository-validation',
 'repository folder not required'=>empty($health['identity']['folderRequired']),
 'repository folder mismatch accepted'=>($health['identity']['actualFolder']??null)==='sustainable-catalyst-lab-repository'&&!empty($health['identity']['folderMatches'])&&!empty($health['identity']['sourceCheckoutFolderAccepted']),
 'sibling checkout excluded from duplicate detection'=>empty($health['duplicatePluginRisk'])&&count($health['pluginCandidates']??array())===1,
 'repository candidate scope is current checkout'=>($health['pluginCandidateScope']??null)==='current-source-checkout'&&(($health['pluginCandidates'][0]['scope']??null)==='current-source-checkout'),
 'all canonical route aliases verify'=>!empty($health['routeIntegrityVerified'])&&count(array_filter($routeChecks,fn($row)=>!empty($row['ok'])))===4,
 'route fallback is self sufficient'=>count(array_filter($routeChecks,fn($row)=>($row['resolver']??null)==='integrity-contract-fallback'))===4,
 'manifest remains verified'=>!empty($health['manifest']['verification']['ok']),
 'R1 repair line reported'=>($health['repairLine']??null)==='0.70.0-r1'
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n".json_encode($health,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");exit(1);}echo "PASS - $label\n";}
