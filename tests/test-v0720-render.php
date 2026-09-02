<?php
define('ABSPATH', __DIR__);
define('SC_LAB_DIR', dirname(__DIR__) . '/');
define('SC_LAB_URL', 'https://example.test/wp-content/plugins/sustainable-catalyst-lab/');
define('SC_LAB_RELEASE_VERSION', '0.72.0');
$GLOBALS['sc_lab_v0720_styles']=array();
$GLOBALS['sc_lab_v0720_scripts']=array();
function add_shortcode($tag,$cb){}
function add_action($tag,$cb){}
function register_rest_route($ns,$route,$args){}
function shortcode_atts($defaults,$atts,$tag=''){return array_merge($defaults,(array)$atts);}
function wp_unique_id($prefix=''){static $i=0;$i++;return $prefix.$i;}
function esc_attr($v){return htmlspecialchars((string)$v,ENT_QUOTES,'UTF-8');}
function esc_html($v){return htmlspecialchars((string)$v,ENT_QUOTES,'UTF-8');}
function esc_url($v){return (string)$v;}
function wp_enqueue_style($handle,$src,$deps=array(),$ver=false){$GLOBALS['sc_lab_v0720_styles'][$handle]=array($src,$deps,$ver);}
function wp_enqueue_script($handle,$src,$deps=array(),$ver=false,$footer=false){$GLOBALS['sc_lab_v0720_scripts'][$handle]=array($src,$deps,$ver,$footer);}
require_once dirname(__DIR__).'/includes/class-sc-lab-homepage-biodiversity-v0720.php';
$html=SC_Lab_Homepage_Biodiversity_V0720::shortcode(array());
$checks=array(
 'section rendered'=>strpos($html,'data-sc-lab-home-v0720')!==false,
 'biodiversity profile rendered'=>strpos($html,'data-v0710-profile="biodiversity"')!==false,
 '4D canvas rendered'=>strpos($html,'data-v0710-canvas')!==false,
 'time slider rendered'=>strpos($html,'data-v0710-w type="range" min="0" max="1"')!==false,
 'XW control rendered'=>strpos($html,'data-v0710-xw')!==false,
 'YW control rendered'=>strpos($html,'data-v0710-yw')!==false,
 'synthetic boundary rendered'=>strpos($html,'not measurements, species estimates, forecasts, or conservation conclusions')!==false,
 'Lab link rendered'=>strpos($html,'Enter the Lab')!==false,
 'Graph Studio link rendered'=>strpos($html,'Open Graph Studio')!==false,
 'shared renderer script enqueued'=>isset($GLOBALS['sc_lab_v0720_scripts']['sc-lab-advanced-visualization-front-door-v0710']),
 'homepage stylesheet enqueued'=>isset($GLOBALS['sc_lab_v0720_styles']['sc-lab-homepage-biodiversity-v0720'])
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
