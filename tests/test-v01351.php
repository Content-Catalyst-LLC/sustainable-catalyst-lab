<?php
$root=dirname(__DIR__);
function must($cond,$msg){if(!$cond){fwrite(STDERR,"FAIL: $msg\n");exit(1);}echo "PASS: $msg\n";}
$plugin=file_get_contents($root.'/sustainable-catalyst-lab.php');
$main=file_get_contents($root.'/includes/class-sc-lab-plugin.php');
$template=file_get_contents($root.'/templates/lab-app.php');
$js=file_get_contents($root.'/assets/js/modules/scientific-visualization-experience-v01351.js');
$css=file_get_contents($root.'/assets/css/sc-lab-scientific-visualization-experience-v01351.css');
preg_match('/Version:\s+([0-9.]+)/',$plugin,$vm); must(!empty($vm[1]) && version_compare($vm[1],'0.135.1','>='),'plugin release retains v0.135.1 visualization experience');
must(strpos($plugin,'class-sc-lab-scientific-visualization-experience-v01351.php')!==false,'plugin loads v0.135.1 REST contract');
must(strpos($main,"scientific-visualization-experience-v01351")!==false,'visual experience JS module is enqueued');
must(strpos($main,"sc-lab-scientific-visualization-experience-v01351.css")!==false,'visual experience stylesheet is enqueued');
must(strpos($template,'data-viz1351-experience-root')!==false,'Graph Studio contains the v0.135.1 analysis experience root');
must(strpos($template,'EXPERIENCE v0.135.')!==false,'Graph Studio header exposes the v0.135 visualization experience line');
must(strpos($js,'fabricateMissingScientificValues:false')!==false,'client boundary forbids fabricated scientific values');
must(strpos($js,'Empirical response distribution')!==false,'empirical distribution panel is present');
must(strpos($js,'Residual structure')!==false,'residual diagnostics panel is present');
must(strpos($js,'Data → method → figure pipeline')!==false,'under-the-hood provenance pipeline is present');
must(strpos($js,'Visualization capability stack')!==false,'renderer capability stack is present');
must(strpos($css,'.sc-viz1351-analysis-grid')!==false,'multi-panel analysis layout CSS is present');
echo "PASS - Lab v0.135.1 WordPress scientific visualization experience contract\n";
