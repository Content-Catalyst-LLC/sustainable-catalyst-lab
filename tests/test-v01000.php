<?php
function must01000($cond,$message){if(!$cond){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$main=file_get_contents(__DIR__.'/../sustainable-catalyst-lab.php');
$plugin=file_get_contents(__DIR__.'/../includes/class-sc-lab-plugin.php');
$rest=file_get_contents(__DIR__.'/../includes/class-sc-lab-rest.php');
$template=file_get_contents(__DIR__.'/../templates/lab-app.php');
$module=file_get_contents(__DIR__.'/../includes/class-sc-lab-carbon-mrv-reporting-v01000.php');
must01000((bool)preg_match('/^ \* Version: 0\.100\.0$/m',$main),'plugin header v0.100.0');
must01000(strpos($main,'SC_Lab_Carbon_MRV_Reporting_V01000::init();')!==false,'reporting module initialized');
must01000(strpos($plugin,"sc-lab-carbon-mrv-reporting-v01000.css")!==false,'reporting CSS enqueued');
must01000(strpos($plugin,"'carbon-mrv-reporting-v01000'")!==false,'reporting browser module enqueued');
must01000(strpos($plugin,"'carbonMrvReporting'")!==false,'reporting browser config');
must01000(strpos($rest,'/carbon-nature/mrv/v1700/reporting/report/build')!==false,'report build proxy route');
must01000(strpos($rest,'/carbon-nature/mrv/v1700/reporting/report/validate')!==false,'report validation proxy route');
must01000(strpos($rest,'/carbon-nature/mrv/v1700/reporting/audit-packet/build')!==false,'audit packet proxy route');
must01000(strpos($rest,'/carbon-nature/mrv/v1700/reporting/project-packet')!==false,'project packet proxy route');
must01000(strpos($template,'data-mrv-v1700-root')!==false,'MRV reporting workspace');
must01000(strpos($template,'MRV Reporting &amp; Audit Packets')!==false,'MRV reporting title');
must01000(strpos($template,'data-mrv-v1700-ledger-json')!==false,'ledger JSON chain-check input');
must01000(strpos($module,"const DOMAIN_VERSION='0.17.0';")!==false,'domain version');
must01000(strpos($module,'auditPacketEqualsAuditorApproval')!==false,'auditor approval guardrail');
echo "PASS - Lab v0.100.0 / Carbon & Nature v0.17.0 PHP contracts\n";
