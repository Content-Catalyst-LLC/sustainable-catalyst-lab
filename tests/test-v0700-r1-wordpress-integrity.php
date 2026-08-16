<?php
$source = dirname(__DIR__);
$tmp = sys_get_temp_dir() . '/sc-lab-v0700-r1-wordpress-' . getmypid() . '-' . bin2hex(random_bytes(4));
@mkdir($tmp, 0777, true);
$current = $tmp . '/sustainable-catalyst-lab';
if (!@symlink($source, $current)) { fwrite(STDERR, "FAIL - unable to create WordPress-plugin symlink\n"); exit(1); }
$duplicate = $tmp . '/sustainable-catalyst-lab-old';
@mkdir($duplicate, 0777, true);
file_put_contents($duplicate . '/sustainable-catalyst-lab.php', "<?php\n/*\nPlugin Name: Sustainable Catalyst Lab\nVersion: 0.69.0\n*/\n");
register_shutdown_function(function() use ($current,$duplicate,$tmp){ @unlink($current); @unlink($duplicate.'/sustainable-catalyst-lab.php'); @rmdir($duplicate); @rmdir($tmp); });

define('ABSPATH', $current . '/');
define('WP_PLUGIN_DIR', $tmp);
define('SC_LAB_FILE', $current . '/sustainable-catalyst-lab.php');
define('SC_LAB_DIR', $current . '/');
define('SC_LAB_PLUGIN_BASENAME', 'sustainable-catalyst-lab/sustainable-catalyst-lab.php');
define('SC_LAB_PLUGIN_SLUG', 'sustainable-catalyst-lab');
define('SC_LAB_RELEASE_VERSION', '0.70.0');
define('SC_LAB_FEATURE_VERSION', SC_LAB_RELEASE_VERSION);
define('SC_LAB_PLATFORM_VERSION', '1.0.0');
define('SC_LAB_VERSION', SC_LAB_PLATFORM_VERSION);
define('SC_LAB_INTEGRITY_CONTEXT', 'wordpress-plugin');
function trailingslashit($value){return rtrim((string)$value,'/\\').'/';}
function plugin_basename($file){return basename(dirname($file)).'/'.basename($file);}
function get_option($name,$default=false){if($name==='active_plugins')return array('sustainable-catalyst-lab/sustainable-catalyst-lab.php');return $default;}
function is_multisite(){return false;}
function sanitize_key($value){return strtolower(preg_replace('/[^a-z0-9_\-]/','',(string)$value));}
function rest_ensure_response($value){return $value;}
require_once $source . '/includes/class-sc-lab-integrity-v02632.php';
$health=SC_Lab_Integrity_V02632::health();
$checks=array(
 'live WordPress context remains strict'=>empty($health['ok'])&&($health['state']??null)==='duplicate-plugin-risk',
 'live folder identity required'=>!empty($health['identity']['folderRequired'])&&!empty($health['identity']['folderMatches']),
 'duplicate plugin risk retained'=>!empty($health['duplicatePluginRisk'])&&count($health['pluginCandidates']??array())===2,
 'WordPress candidate scope retained'=>($health['pluginCandidateScope']??null)==='wordpress-plugin-directory',
 'duplicate does not masquerade as partial install'=>empty($health['partialInstallRisk']),
 'route aliases still verify in strict context'=>!empty($health['routeIntegrityVerified']),
 'manifest remains verified'=>!empty($health['manifest']['verification']['ok'])
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n".json_encode($health,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");exit(1);}echo "PASS - $label\n";}
