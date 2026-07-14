<?php
define('ABSPATH',__DIR__);
if(!function_exists('add_action')){function add_action(){}}
$root=dirname(__DIR__);
function v0240_assert($condition,$message){if(!$condition){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
require_once $root.'/includes/class-sc-lab-genetics-genomics-rest-v0240.php';
$c=SC_Lab_Genetics_Genomics_REST_V0240::catalog();
v0240_assert($c['version']==='0.24.0','version');
v0240_assert(count($c['methods'])===48,'48 methods');
v0240_assert(count($c['benchmarks'])===48,'48 benchmarks');
v0240_assert(count($c['categories'])===8,'8 categories');
foreach($c['benchmarks'] as $b){
 $got=SC_Lab_Genetics_Genomics_REST_V0240::execute($b['methodId'],$b['inputs'])['value'];$exp=$b['expected'];
 if(is_numeric($exp)){ $allowed=max((float)$b['tolerance'],abs((float)$exp)*1e-8);v0240_assert(abs((float)$got-(float)$exp)<=$allowed,'benchmark '.$b['methodId']);}
 else v0240_assert($got===$exp,'benchmark '.$b['methodId']);
}
$batch=SC_Lab_Genetics_Genomics_REST_V0240::batch_execute(array(
 array('methodId'=>'gc-content','inputs'=>array('sequence'=>'ACGT')),
 array('methodId'=>'hamming-distance','inputs'=>array('reference'=>'AC','query'=>'A'))
));
v0240_assert($batch['successCount']===1&&$batch['errorCount']===1,'batch isolation');
echo "Lab v0.24.0 PHP tests passed: 48 methods, 48 benchmarks, 8 categories, batch isolation.\n";
