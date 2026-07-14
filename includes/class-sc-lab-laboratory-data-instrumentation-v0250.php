<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Laboratory_Data_Instrumentation_V0250 {
 const VERSION='0.25.0'; const SHORTCODE='sc_lab_laboratory_data_instrumentation';
 const SCRIPT='sc-lab-laboratory-data-instrumentation-v0250'; const STYLE='sc-lab-laboratory-data-instrumentation-v0250-style';
 public static function boot(){add_action('wp_enqueue_scripts',array(__CLASS__,'enqueue'),60100);if(function_exists('add_shortcode'))add_shortcode(self::SHORTCODE,array(__CLASS__,'shortcode'));}
 private static function url($r){return defined('SC_LAB_URL')?trailingslashit((string)SC_LAB_URL).'assets/'.ltrim($r,'/'):plugin_dir_url(dirname(__DIR__).'/sustainable-catalyst-lab.php').'assets/'.ltrim($r,'/');}
 private static function ver($r){$p=dirname(__DIR__).'/assets/'.ltrim($r,'/');return is_file($p)?self::VERSION.'.'.filemtime($p):self::VERSION;}
 public static function enqueue(){if(function_exists('is_admin')&&is_admin())return;$css='css/sc-lab-laboratory-data-instrumentation-v0250.css';$js='js/modules/laboratory-data-instrumentation-v0250.js';wp_enqueue_style(self::STYLE,self::url($css),array(),self::ver($css));wp_enqueue_script(self::SCRIPT,self::url($js),array(),self::ver($js),true);}
 public static function shortcode(){self::enqueue();return '<div class="sc-lab-instrumentation-shortcode" data-laboratory-instrumentation-root></div>';}
}
SC_Lab_Laboratory_Data_Instrumentation_V0250::boot();
