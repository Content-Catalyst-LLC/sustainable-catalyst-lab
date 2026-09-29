<?php
$root=dirname(__DIR__); $m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=[];
$checks['releaseVersion']=($m['releaseVersion']??'')==='0.141.1';
$checks['featureVersion']=($m['featureVersion']??'')==='0.141.1';
$checks['predecessor retained']=($m['machineLearningExperimentWorkspaceVersion']??'')==='0.141.0';
$checks['repair baseline retained']=($m['v014001WordPressInstalledRuntimeScope']??false)===true;
$checks['new feature marker']=($m['neuralArchitectureTrainingConfigurationVersion']??'')==='0.141.1';
$files=$m['wordpressCriticalFiles']??[]; $bad=[];
foreach($files as $rel=>$sha){ if(preg_match('~^(backend|data|tests|scripts|sdk|examples|docs)/~',$rel)){$bad[]=$rel;continue;} $path=$root.'/'.$rel; if(!is_file($path)||hash_file('sha256',$path)!==$sha)$bad[]=$rel; }
$checks['runtime manifest scope/hashes']=count($files)>100 && count($bad)===0;
foreach($checks as $k=>$v){echo ($v?'PASS':'FAIL').": $k\n"; if(!$v) exit(1);} 
