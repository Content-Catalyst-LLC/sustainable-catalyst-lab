<?php
$root=dirname(__DIR__);$bootstrap=file_get_contents($root.'/sustainable-catalyst-lab.php');$plugin=file_get_contents($root.'/includes/class-sc-lab-plugin.php');$template=file_get_contents($root.'/templates/lab-app.php');$class=file_get_contents($root.'/includes/class-sc-lab-scientific-audit-v0590.php');$compute=file_get_contents($root.'/includes/class-sc-lab-python-compute-core-v0261.php');
$checks=array(
 'v0.59.0 scientific audit PHP class'=>is_file($root.'/includes/class-sc-lab-scientific-audit-v0590.php'),
 'v0.59.0 backend module'=>is_file($root.'/backend/app/scientific_audit_v0590.py'),
 'v0.59.0 JS module'=>is_file($root.'/assets/js/modules/scientific-audit-v0590.js'),
 'v0.59.0 stylesheet'=>is_file($root.'/assets/css/sc-lab-scientific-audit-v0590.css'),
 'Scientific audit schema'=>is_file($root.'/contracts/scientific-audit-report-v0590.schema.json'),
 'Redacted export schema'=>is_file($root.'/contracts/redacted-research-export-v0590.schema.json'),
 'Data minimization schema'=>is_file($root.'/contracts/data-minimization-review-v0590.schema.json'),
 'Scientific audit policy'=>is_file($root.'/contracts/scientific-audit-policy-v0590.json'),
 'WordPress plugin header reports v0.59.0'=>preg_match('/^\s*\*\s*Version:\s*0\.59\.0\s*$/m',$bootstrap)===1,
 'Release constant reports v0.59.0'=>strpos($bootstrap,"define('SC_LAB_RELEASE_VERSION', '0.59.0')")!==false,
 'Platform compatibility remains v1.0.0'=>strpos($bootstrap,"define('SC_LAB_PLATFORM_VERSION', '1.0.0')")!==false,
 'Bootstrap initializes scientific audit'=>strpos($bootstrap,'SC_Lab_Scientific_Audit_V0590::init()')!==false,
 'Audit remains contextual in workflow workspace'=>strpos($template,'data-scientific-audit-v0590')!==false,
 'Three application row preserved'=>strpos($template,'Prototyping Workbench')!==false&&strpos($template,'Decision Studio')!==false&&strpos($template,'Site Intelligence')!==false,
 'Six destination rail preserved'=>substr_count($template,'data-v0483-primary=')===6,
 'Health disables automatic certification'=>strpos($class,"'automaticCertification'=>false")!==false,
 'Health disables automatic high-stakes decision'=>strpos($class,"'automaticHighStakesDecision'=>false")!==false,
 'Health declares no raw sensitive values in findings'=>strpos($class,"'rawSensitiveValuesInFindings'=>false")!==false,
 'Audit proxy route'=>strpos($compute,"/compute/core/scientific-audit/v0590/audit")!==false,
 'Minimization proxy route'=>strpos($compute,"/compute/core/scientific-audit/v0590/minimize")!==false,
 'v0.59 stylesheet enqueued'=>strpos($plugin,'sc-lab-scientific-audit-v0590')!==false,
 'v0.59 JS module registered'=>strpos($plugin,"'scientific-audit-v0590'")!==false,
);
foreach($checks as $label=>$ok){if(!$ok){fwrite(STDERR,"FAIL - $label\n");exit(1);}echo "PASS - $label\n";}
