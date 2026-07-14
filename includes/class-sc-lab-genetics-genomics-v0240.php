<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Genetics_Genomics_V0240 {
 const VERSION='0.24.0';const SHORTCODE='sc_lab_genetics_genomics_sequence_analysis';
 public static function boot(){add_action('wp_enqueue_scripts',array(__CLASS__,'enqueue'),60100);if(function_exists('add_shortcode'))add_shortcode(self::SHORTCODE,array(__CLASS__,'shortcode'));}
 private static function url($r){return defined('SC_LAB_URL')?trailingslashit((string)SC_LAB_URL).'assets/'.ltrim($r,'/'):plugin_dir_url(dirname(__DIR__).'/sustainable-catalyst-lab.php').'assets/'.ltrim($r,'/');}
 public static function enqueue(){if(function_exists('is_admin')&&is_admin())return;wp_enqueue_style('sc-lab-genomics-v0240',self::url('css/sc-lab-genetics-genomics-v0240.css'),array(),self::VERSION);wp_enqueue_script('sc-lab-genomics-v0240',self::url('js/modules/genetics-genomics-sequence-analysis-v0240.js'),array(),self::VERSION,true);}
 public static function shortcode(){self::enqueue();return '<div data-genetics-genomics-root></div>';}
}
SC_Lab_Genetics_Genomics_V0240::boot();
