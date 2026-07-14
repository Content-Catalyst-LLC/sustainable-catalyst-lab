<?php
if(!defined('ABSPATH'))exit;
final class SC_Lab_Genomic_Visualization_REST_V0242{
 const VERSION='0.24.2';const NAMESPACE='sc-lab/v1';
 public static function boot(){add_action('rest_api_init',array(__CLASS__,'routes'));}
 public static function contract(){$p=dirname(__DIR__).'/contracts/genomic-visualization-comparison-v0242.json';$d=json_decode(file_get_contents($p),true);return is_array($d)?$d:array();}
 private static function norm($v){return strtoupper((string)preg_replace('/\s+/','',(string)($v??'')));}
 public static function execute($id,$i){
  $s=self::norm($i['sequence']??'');$value=null;
  if($id==='mismatch-positions'){$a=self::norm($i['reference']??'');$b=self::norm($i['query']??'');$value=array();for($j=0;$j<max(strlen($a),strlen($b));$j++)if(($a[$j]??'-')!==($b[$j]??'-'))$value[]=$j;}
  elseif($id==='windowed-gc'){$w=(int)$i['windowSize'];$step=(int)$i['stepSize'];$value=array();for($start=0;$start<strlen($s);$start+=$step){$part=substr($s,$start,$w);$valid=preg_replace('/[^ACGT]/','',$part);$gc=strlen($valid)?(substr_count($valid,'G')+substr_count($valid,'C'))/strlen($valid)*100:0.0;$value[]=array('start'=>$start,'end'=>min($start+$w,strlen($s)),'gcPercent'=>$gc);}}
  elseif($id==='motif-hits'){$m=self::norm($i['motif']??'');$value=array();$p=0;while($m!==''&&($j=strpos($s,$m,$p))!==false){$value[]=$j;$p=$j+1;}}
  elseif($id==='kmer-spectrum'){$k=(int)$i['k'];$value=array();for($j=0;$j+$k<=strlen($s);$j++){$x=substr($s,$j,$k);$value[$x]=($value[$x]??0)+1;}}
  elseif($id==='variant-track'){$n=(float)$i['sequenceLength'];$value=array();foreach($i['variants']??array() as $v){$v['fraction']=(float)$v['position']/$n;$value[]=$v;}}
  elseif($id==='alignment-padding'){$a=self::norm($i['reference']??'');$b=self::norm($i['query']??'');$n=max(strlen($a),strlen($b));$value=array('reference'=>str_pad($a,$n,'-'),'query'=>str_pad($b,$n,'-'));}
  elseif($id==='sequence-summary'){$valid=preg_replace('/[^ACGT]/','',$s);$value=array('length'=>strlen($s),'gcPercent'=>strlen($valid)?(substr_count($valid,'G')+substr_count($valid,'C'))/strlen($valid)*100:0.0,'ambiguousCount'=>strlen(preg_replace('/[ACGTU]/','',$s)));}
  elseif($id==='comparison-summary'){$a=self::norm($i['reference']??'');$b=self::norm($i['query']??'');$n=max(strlen($a),strlen($b));$m=0;for($j=0;$j<$n;$j++)if(($a[$j]??'-')!==($b[$j]??'-'))$m++;$value=array('referenceLength'=>strlen($a),'queryLength'=>strlen($b),'mismatchCount'=>$m,'identityPercent'=>$n?($n-$m)/$n*100:100.0);}
  else throw new InvalidArgumentException('Unknown visualization method');
  return array('version'=>self::VERSION,'methodId'=>$id,'value'=>$value);
 }
 public static function health_payload(){$c=self::contract();$ok=($c['version']??null)===self::VERSION&&count($c['modes']??array())===8&&count($c['analysisMethods']??array())===8&&count($c['benchmarks']??array())===8;return array('ok'=>$ok,'status'=>$ok?'ready':'contract-incomplete','release'=>self::VERSION,'modeCount'=>count($c['modes']??array()),'analysisMethodCount'=>count($c['analysisMethods']??array()),'benchmarkCount'=>count($c['benchmarks']??array()));}
 public static function routes(){register_rest_route(self::NAMESPACE,'/compute/genomics/visualization/methods',array('methods'=>'GET','callback'=>fn()=>rest_ensure_response(self::contract()),'permission_callback'=>'__return_true'));register_rest_route(self::NAMESPACE,'/compute/genomics/visualization/health',array('methods'=>'GET','callback'=>fn()=>rest_ensure_response(self::health_payload()),'permission_callback'=>'__return_true'));register_rest_route(self::NAMESPACE,'/compute/genomics/visualization/analyze',array('methods'=>'POST','callback'=>array(__CLASS__,'analyze'),'permission_callback'=>'__return_true'));}
 public static function analyze($r){try{$p=$r->get_json_params();return rest_ensure_response(self::execute((string)($p['methodId']??''),$p['inputs']??array()));}catch(Throwable $e){return new WP_Error('sc_lab_v0242_visualization_error',$e->getMessage(),array('status'=>422));}}
}
SC_Lab_Genomic_Visualization_REST_V0242::boot();
