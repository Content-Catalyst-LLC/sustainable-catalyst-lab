<?php
if(!defined('ABSPATH'))exit;
final class SC_Lab_Genomic_Validation_V0243{
 const VERSION='0.24.3';const SHORTCODE='sc_lab_genomic_validation_sequence_provenance';
 public static function boot(){add_action('wp_enqueue_scripts',array(__CLASS__,'enqueue'),60130);if(function_exists('add_shortcode'))add_shortcode(self::SHORTCODE,array(__CLASS__,'shortcode'));}
 private static function url($r){return defined('SC_LAB_URL')?trailingslashit((string)SC_LAB_URL).'assets/'.ltrim($r,'/'):plugin_dir_url(dirname(__DIR__).'/sustainable-catalyst-lab.php').'assets/'.ltrim($r,'/');}
 public static function enqueue(){if(function_exists('is_admin')&&is_admin())return;if(class_exists('SC_Lab_Genomics_Production_V0241'))SC_Lab_Genomics_Production_V0241::enqueue();wp_enqueue_style('sc-lab-genomic-validation-v0243',self::url('css/sc-lab-genomic-validation-v0243.css'),array(),self::VERSION);wp_enqueue_script('sc-lab-genomic-validation-v0243',self::url('js/modules/genomic-validation-sequence-provenance-v0243.js'),array(),self::VERSION,true);}
 public static function shortcode(){self::enqueue();return '<div data-genomic-validation-root></div>';}
}
SC_Lab_Genomic_Validation_V0243::boot();
