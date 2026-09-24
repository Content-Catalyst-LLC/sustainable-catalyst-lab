<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__.'/');
if (!function_exists('add_action')) { function add_action(...$args){} function register_rest_route(...$args){} function rest_ensure_response($x){return $x;} }
if (!defined('SC_LAB_DIR')) define('SC_LAB_DIR', dirname(__DIR__).'/');
require_once dirname(__DIR__).'/includes/class-sc-lab-graph-studio-renderer-replacement-v013582.php';
$h=SC_Lab_Graph_Studio_Renderer_Replacement_V013582::health();
if (!$h['ok'] || $h['version']!=='0.135.8.2' || $h['engineVersion']!=='3.0.0' || $h['requiredBackendRouteCount']!==24 || $h['primaryRendererOwner']!=='graph-studio-renderer-v013582' || $h['legacyGraphStudioRuntimeExecuted']!==false || $h['singlePrimaryViewport']!==true) { fwrite(STDERR,"v0.135.8.2 renderer health failed\n"); exit(1); }
$template=file_get_contents(dirname(__DIR__).'/templates/lab-app.php');
if (strpos($template,'RENDERER v0.135.8.2')===false) { fwrite(STDERR,"v0.135.8.2 template identity missing\n"); exit(1); }
$plugin=file_get_contents(dirname(__DIR__).'/includes/class-sc-lab-plugin.php');
foreach (array('graph-studio-renderer-replacement-v013582','graph-studio-v0790','graph-studio-v0880') as $marker) if (strpos($plugin,$marker)===false) { fwrite(STDERR,"missing marker $marker\n"); exit(1); }
if (substr_count($plugin,"if (in_array(\$module, array('graph-studio-v0790'")!==1) { fwrite(STDERR,"legacy Graph Studio quarantine missing\n"); exit(1); }
echo "PASS - Lab v0.135.8.2 Graph Studio renderer replacement contract\n";
