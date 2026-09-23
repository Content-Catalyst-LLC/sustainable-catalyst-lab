<?php
$root=dirname(__DIR__);
$files=array(
 'includes/class-sc-lab-spatial-spatiotemporal-research-studio-v01260.php',
 'contracts/spatial-spatiotemporal-research-studio-v01260.schema.json',
 'contracts/spatial-spatiotemporal-research-studio-policy-v01260.json',
 'assets/js/modules/spatial-spatiotemporal-research-studio-v01260.js',
 'assets/css/sc-lab-spatial-spatiotemporal-research-studio-v01260.css'
);
foreach($files as $file){if(!is_file($root.'/'.$file)){fwrite(STDERR,"FAIL missing $file\n");exit(1);}}
$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
if(($m['releaseVersion']??null)!=='0.126.0'||($m['spatialSpatiotemporalResearchStudioVersion']??null)!=='0.126.0'||($m['v01260RequiredRouteCount']??null)!==28){fwrite(STDERR,"FAIL v0.126 manifest metadata\n");exit(1);}
echo "PASS - Lab v0.126.0 WordPress spatial/spatiotemporal research surface\n";
