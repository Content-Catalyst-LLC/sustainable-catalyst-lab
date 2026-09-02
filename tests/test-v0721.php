<?php
$root=dirname(__DIR__);
$main=file_get_contents($root.'/sustainable-catalyst-lab.php');
$feature=file_get_contents($root.'/includes/class-sc-lab-homepage-biodiversity-v0720.php');
$loop=file_get_contents($root.'/assets/js/modules/homepage-biodiversity-loop-v0721.js');
$checks=array(
 'Plugin header reports v0.72.1'=>strpos($main,'Version: 0.72.1')!==false,
 'Release constant reports v0.72.1'=>strpos($main,"SC_LAB_RELEASE_VERSION', '0.72.1")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($main,"SC_LAB_PLATFORM_VERSION', '1.0.0")!==false,
 'Homepage feature reports v0.72.1'=>strpos($feature,"const VERSION = '0.72.1'")!==false,
 'Autoplay defaults true'=>strpos($feature,"'autoplay' => 'true'")!==false,
 'Autoplay can be disabled'=>strpos($feature,"'false', 'no', 'off'")!==false,
 'Autoplay data contract rendered'=>strpos($feature,'data-v0721-autoplay-loop=')!==false,
 'Loop JS enqueued'=>strpos($feature,'homepage-biodiversity-loop-v0721.js')!==false,
 'Loop JS depends on v0.71 renderer'=>strpos($feature,"array('sc-lab-advanced-visualization-front-door-v0710')")!==false,
 'Health declares time sweep loop'=>strpos($feature,"'timeSweepLoop' => true")!==false,
 'Health declares reduced motion'=>strpos($feature,"'reducedMotionHonored' => true")!==false,
 'Loop module present'=>strpos($loop,"HomepageBiodiversityLoopV0721")!==false
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
