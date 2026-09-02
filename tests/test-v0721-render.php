<?php
define('ABSPATH', __DIR__);
define('SC_LAB_DIR', dirname(__DIR__) . '/');
define('SC_LAB_URL', 'https://example.test/wp-content/plugins/sustainable-catalyst-lab/');
define('SC_LAB_RELEASE_VERSION', '0.72.1');
$GLOBALS['styles']=array();$GLOBALS['scripts']=array();
function add_shortcode($tag,$cb){} function add_action($tag,$cb){} function register_rest_route($ns,$route,$args){}
function shortcode_atts($defaults,$atts,$tag=''){return array_merge($defaults,(array)$atts);} function wp_unique_id($prefix=''){static $i=0;return $prefix.(++$i);}
function esc_attr($v){return htmlspecialchars((string)$v,ENT_QUOTES,'UTF-8');} function esc_html($v){return htmlspecialchars((string)$v,ENT_QUOTES,'UTF-8');} function esc_url($v){return (string)$v;}
function wp_enqueue_style($h,$s,$d=array(),$v=false){$GLOBALS['styles'][$h]=array($s,$d,$v);} function wp_enqueue_script($h,$s,$d=array(),$v=false,$f=false){$GLOBALS['scripts'][$h]=array($s,$d,$v,$f);}
require_once dirname(__DIR__).'/includes/class-sc-lab-homepage-biodiversity-v0720.php';
$html=SC_Lab_Homepage_Biodiversity_V0720::shortcode(array());
$static=SC_Lab_Homepage_Biodiversity_V0720::shortcode(array('autoplay'=>'false'));
$checks=array(
 'default homepage loop enabled'=>strpos($html,'data-v0721-autoplay-loop="1"')!==false,
 'explicit autoplay false honored'=>strpos($static,'data-v0721-autoplay-loop="0"')!==false,
 'existing animate button retained'=>strpos($html,'data-v0710-animate')!==false,
 'shared renderer script enqueued'=>isset($GLOBALS['scripts']['sc-lab-advanced-visualization-front-door-v0710']),
 'loop controller enqueued'=>isset($GLOBALS['scripts']['sc-lab-homepage-biodiversity-loop-v0721']),
 'loop controller depends on renderer'=>in_array('sc-lab-advanced-visualization-front-door-v0710',$GLOBALS['scripts']['sc-lab-homepage-biodiversity-loop-v0721'][1],true)
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
