<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__ . '/');
if (!function_exists('sanitize_key')) { function sanitize_key($v){ $v=strtolower((string)$v); return preg_replace('/[^a-z0-9_-]/','',$v); } }
if (!function_exists('apply_filters')) { function apply_filters($tag,$value){ return $value; } }
if (!function_exists('esc_attr')) { function esc_attr($v){ return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); } }
if (!function_exists('esc_html')) { function esc_html($v){ return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); } }
if (!function_exists('wp_json_encode')) { function wp_json_encode($v,$flags=0){ return json_encode($v,$flags); } }
require_once dirname(__DIR__) . '/includes/class-sc-lab-runtime-repair-v02631.php';
$rm = new ReflectionMethod('SC_Lab_Runtime_Repair_V02631','single_module_shell');
$rm->setAccessible(true);
$html='<div class="sc-lab-app" data-initial-module="overview"><section data-lab-module="overview">O</section><section data-lab-module="graph-studio" hidden>G</section><section data-lab-module="experiments" hidden>E</section></div>';
$out=$rm->invoke(null,$html,'overview');
if(substr_count($out,'data-lab-module=')!==3) exit(1);
if(!preg_match('/<section(?=[^>]*data-lab-module="overview")(?![^>]*\\shidden(?:\\s|=|>))[^>]*>/i',$out)) exit(2);
if(!preg_match('/<section(?=[^>]*data-lab-module="graph-studio")(?=[^>]*\\shidden(?:\\s|=|>))[^>]*>/i',$out)) exit(3);
$out2=$rm->invoke(null,$html,'graph-studio');
if(substr_count($out2,'data-lab-module=')!==3) exit(4);
if(!preg_match('/<section(?=[^>]*data-lab-module="graph-studio")(?![^>]*\\shidden(?:\\s|=|>))[^>]*>/i',$out2)) exit(5);
if(!preg_match('/<section(?=[^>]*data-lab-module="overview")(?=[^>]*\\shidden(?:\\s|=|>))[^>]*>/i',$out2)) exit(6);
echo "PASS - v0.152.0.2 full-panel navigation shell preserves all modules\n";
