<?php
if(!defined('ABSPATH'))exit;
final class SC_Lab_Genomic_Visualization_V0242{
 const VERSION='0.24.2';const SHORTCODE='sc_lab_genomic_visualization_comparison';
 public static function boot(){add_action('wp_enqueue_scripts',array(__CLASS__,'enqueue'),60120);if(function_exists('add_shortcode'))add_shortcode(self::SHORTCODE,array(__CLASS__,'shortcode'));}
 private static function url($r){return defined('SC_LAB_URL')?trailingslashit((string)SC_LAB_URL).'assets/'.ltrim($r,'/'):plugin_dir_url(dirname(__DIR__).'/sustainable-catalyst-lab.php').'assets/'.ltrim($r,'/');}
 public static function enqueue(){if(function_exists('is_admin')&&is_admin())return;wp_enqueue_style('sc-lab-genomic-visualization-v0242',self::url('css/sc-lab-genomic-visualization-v0242.css'),array(),self::VERSION);wp_enqueue_script('sc-lab-genomic-visualization-v0242',self::url('js/modules/genomic-visualization-comparison-v0242.js'),array(),self::VERSION,true);}
 public static function shortcode(){self::enqueue();return '<div data-genomic-visualization-root></div>';}
}
SC_Lab_Genomic_Visualization_V0242::boot();
