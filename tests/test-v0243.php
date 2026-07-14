<?php
define('ABSPATH',__DIR__);if (!function_exists('add_action')) { function add_action() {} }
$root=dirname(__DIR__);require_once $root.'/includes/class-sc-lab-genomic-validation-rest-v0243.php';$c=SC_Lab_Genomic_Validation_REST_V0243::contract();if(count($c['profiles'])!==8||count($c['eventTypes'])!==6)exit(1);
$v=SC_Lab_Genomic_Validation_REST_V0243::evaluate('sequence-record-integrity',array(array('sequenceId'=>'s1','sequence'=>'ACGTN','alphabet'=>'DNA')));if($v['decision']!=='pass')exit(1);
$m=SC_Lab_Genomic_Validation_REST_V0243::create_manifest(array(array('id'=>'s1','sequence'=>'ACGT')),array(array('sequenceId'=>'s1')),array('build'=>'GRCh38'),array(array('step'=>'align')),array(),array());
$f=SC_Lab_Genomic_Validation_REST_V0243::create_record($m,array('recordId'=>'r1','timestamp'=>'2026-07-14T00:00:00+00:00','eventType'=>'sequence-import','datasetId'=>'d1'));
$s=SC_Lab_Genomic_Validation_REST_V0243::create_record(array('decision'=>'pass'),array('recordId'=>'r2','timestamp'=>'2026-07-14T00:01:00+00:00','eventType'=>'validation-decision','datasetId'=>'d1'),$f['recordHash']);
if(!SC_Lab_Genomic_Validation_REST_V0243::verify_ledger(array($f,$s))['valid'])exit(1);$t=array($f,$s);$t[1]['payload']['decision']='fail';if(SC_Lab_Genomic_Validation_REST_V0243::verify_ledger($t)['valid'])exit(1);
$d=SC_Lab_Genomic_Validation_REST_V0243::create_dossier(array($v),$m,array($f,$s),'release');if(!$d['summary']['releaseReady']||strlen($d['dossierHash'])!==64)exit(1);
echo "Lab v0.24.3 PHP tests passed: 8 profiles, 6 events, manifests, ledger verification, tamper detection, dossier.\n";
