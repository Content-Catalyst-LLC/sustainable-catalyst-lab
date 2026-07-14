<?php
if(!defined('ABSPATH'))exit;
final class SC_Lab_Genomics_Production_V0241{
 const VERSION='0.24.1';const ENGINE_VERSION='0.24.0';const NAMESPACE='sc-lab/v1';
 public static function boot(){add_action('wp_enqueue_scripts',array(__CLASS__,'enqueue'),60110);add_action('rest_api_init',array(__CLASS__,'routes'));}
 private static function url($r){return defined('SC_LAB_URL')?trailingslashit((string)SC_LAB_URL).'assets/'.ltrim($r,'/'):plugin_dir_url(dirname(__DIR__).'/sustainable-catalyst-lab.php').'assets/'.ltrim($r,'/');}
 public static function enqueue(){if(function_exists('is_admin')&&is_admin())return;if(class_exists('SC_Lab_Genetics_Genomics_V0240'))SC_Lab_Genetics_Genomics_V0240::enqueue();wp_enqueue_style('sc-lab-genomics-production-v0241',self::url('css/sc-lab-genomics-production-v0241.css'),array(),self::VERSION);wp_enqueue_script('sc-lab-genomics-production-v0241',self::url('js/modules/genomics-production-v0241.js'),array('sc-lab-genomics-v0240'),self::VERSION,true);}
 public static function health_payload(){$c=SC_Lab_Genetics_Genomics_REST_V0240::catalog();$ok=($c['version']??null)==='0.24.0'&&count($c['methods']??array())===48&&count($c['benchmarks']??array())===48&&count($c['categories']??array())===8;return array('ok'=>$ok,'status'=>$ok?'ready':'contract-incomplete','release'=>self::VERSION,'engineRelease'=>self::ENGINE_VERSION,'methodCount'=>count($c['methods']??array()),'benchmarkCount'=>count($c['benchmarks']??array()),'categoryCount'=>count($c['categories']??array()),'clinicalUse'=>false);}
 public static function routes(){register_rest_route(self::NAMESPACE,'/compute/genomics/production-health',array('methods'=>'GET','callback'=>fn()=>rest_ensure_response(self::health_payload()),'permission_callback'=>'__return_true'));}
}
SC_Lab_Genomics_Production_V0241::boot();
