<?php
function must01040($cond,$message){if(!$cond){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$module=file_get_contents(__DIR__.'/../includes/class-sc-lab-platform-core-v3-adapter-v01040.php');
$backend=file_get_contents(__DIR__.'/../backend/app/platform_core_v3_adapter_v01040.py');
must01040((bool)preg_match('/^ \* Version: 0\.104\.0$/m',$main),'plugin header v0.104.0');
must01040(strpos($main,'SC_Lab_Platform_Core_V3_Adapter_V01040::init();')!==false,'Platform Core v3 adapter initialized');
must01040(strpos($plugin,"'platformCoreV3Adapter'")!==false,'release console exposes Core v3 adapter');
must01040(strpos($module,"const CORE_REQUIRED_VERSION = '3.0.0';")!==false,'Core v3.0.0 requirement');
must01040(strpos($module,"const PRODUCT_REF = 'product:sustainable-catalyst-lab';")!==false,'canonical Lab product ref');
must01040(strpos($module,'labCallsCoreAutomatically')!==false,'no automatic Core calls boundary');
must01040(strpos($backend,'sc.research.unified-runtime-contract.v1')!==false,'Core runtime contract');
must01040(strpos($backend,'sc.research.unified-research-scientific-investigation-runtime.v1')!==false,'Core v3 unified runtime contract');
must01040(strpos($backend,'automatic_submission')!==false,'explicit non-submission behavior');
echo "PASS - Lab v0.104.0 Platform Core v3 Runtime Adapter PHP/backend contracts\n";
