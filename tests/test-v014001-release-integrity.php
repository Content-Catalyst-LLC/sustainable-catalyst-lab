<?php
$root=dirname(__DIR__);
$m=json_decode(file_get_contents($root.'/build/sc-lab-release-manifest.json'),true);
$checks=[];
$checks['releaseVersion 0.140.0.1']=($m['releaseVersion']??null)==='0.140.0.1';
$checks['featureVersion 0.140.0.1']=($m['featureVersion']??null)==='0.140.0.1';
$checks['OS feature preserved']=($m['scientificResearchOperatingSystemVersion']??null)==='0.140.0';
$files=$m['wordpressCriticalFiles']??[];
$checks['runtime manifest populated']=count($files)>100;
$bad=[];
foreach($files as $rel=>$sha){
  if(preg_match('~^(backend|data|tests|scripts|sdk|examples|docs)/~',$rel)){$bad[]=$rel;continue;}
  $path=$root.'/'.$rel;
  if(!is_file($path)||hash_file('sha256',$path)!==$sha){$bad[]=$rel;}
}
$checks['runtime manifest scope/hashes valid']=count($bad)===0;
$checks['route count preserved']=($m['v01400RequiredRouteCount']??null)===25 && ($m['v014001RequiredRouteCount']??null)===25;
$failed=[]; foreach($checks as $k=>$v){echo ($v?'PASS':'FAIL').": $k\n"; if(!$v)$failed[]=$k;}
if($failed){fwrite(STDERR,'Failed: '.implode(', ',$failed)."\n");exit(1);} 
