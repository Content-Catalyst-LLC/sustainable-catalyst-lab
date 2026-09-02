<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$feature=file_get_contents($root.'/includes/class-sc-lab-homepage-biodiversity-v0720.php');
$renderer=file_get_contents($root.'/assets/js/modules/advanced-visualization-front-door-v0710.js');
$css=file_get_contents($root.'/assets/css/sc-lab-homepage-biodiversity-v0720.css');
$checks=array(
 'Plugin header reports v0.72.0'=>strpos($main,'Version: 0.72.0')!==false,
 'Release constant reports v0.72.0'=>strpos($main,"SC_LAB_RELEASE_VERSION', '0.72.0")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($main,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
 'v0.72 homepage class initialized'=>strpos($main,'SC_Lab_Homepage_Biodiversity_V0720::init()')!==false,
 'Homepage preview shortcode registered'=>strpos($feature,"add_shortcode('sc_lab_home_preview'")!==false,
 'Homepage biodiversity alias registered'=>strpos($feature,"add_shortcode('sc_lab_home_biodiversity'")!==false,
 'Homepage health route registered'=>strpos($feature,"'/homepage/v0720/health'")!==false,
 'Homepage reuses v0.71 renderer'=>strpos($feature,"'renderer' => 'advanced-visualization-front-door-v0710'")!==false,
 'Homepage loads v0.71 renderer JS'=>strpos($feature,"advanced-visualization-front-door-v0710.js")!==false,
 'Homepage loads dedicated v0.72 CSS'=>strpos($feature,"sc-lab-homepage-biodiversity-v0720.css")!==false,
 'Biodiversity profile markup present'=>strpos($feature,'data-v0710-profile="biodiversity"')!==false,
 'Time slice begins at 0.60'=>strpos($feature,'data-v0710-initial-w="0.60"')!==false,
 'Time control bounded 0 to 1'=>strpos($feature,'data-v0710-w type="range" min="0" max="1"')!==false,
 'XW 4D control retained'=>strpos($feature,'data-v0710-xw')!==false,
 'YW 4D control retained'=>strpos($feature,'data-v0710-yw')!==false,
 'Biodiversity four dimensions declared'=>strpos($feature,"'habitat-quality', 'climate-stress', 'biodiversity-response', 'time-disturbance-progression'")!==false,
 'Scientific boundary excludes forecasts'=>strpos($feature,'They are not measurements, species estimates, forecasts, or conservation conclusions.')!==false,
 'Renderer supports biodiversity response'=>strpos($renderer,'function biodiversityResponse(x,y,t)')!==false,
 'Homepage CSS exists'=>strpos($css,'.sc-lab-home-v0720')!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
