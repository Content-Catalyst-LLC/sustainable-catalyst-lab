<?php
if (!defined('ABSPATH')) { exit; }

final class SC_Lab_Genetics_Genomics_REST_V0240 {
    const VERSION='0.24.0';
    const NAMESPACE='sc-lab/v1';

    public static function boot() {
        add_action('rest_api_init', array(__CLASS__, 'register_routes'));
    }

    private static function contract_path() {
        return dirname(__DIR__) . '/contracts/genetics-genomics-sequence-analysis-v0240.json';
    }

    public static function catalog() {
        $path=self::contract_path();
        if (!is_file($path)) return array('version'=>self::VERSION,'categories'=>array(),'methods'=>array(),'benchmarks'=>array());
        $decoded=json_decode(file_get_contents($path),true);
        return is_array($decoded)?$decoded:array();
    }

    private static function method($id) {
        foreach (self::catalog()['methods'] as $method) if ($method['id']===$id) return $method;
        throw new InvalidArgumentException('Unknown genomic method: '.$id);
    }

    private static function norm($value) {
        return strtoupper((string) preg_replace('/\s+/', '', (string) ($value ?? '')));
    }

    private static function finite($value,$label) {
        if (!is_numeric($value) || !is_finite((float)$value)) throw new InvalidArgumentException($label.' must be numerical and finite.');
        return (float)$value;
    }

    private static function positive($value,$label) {
        $n=self::finite($value,$label);
        if ($n<=0) throw new InvalidArgumentException($label.' must be greater than zero.');
        return $n;
    }

    private static function values($value,$label,$minimum=1) {
        if (is_string($value)) {
            $trim=trim($value);
            if (str_starts_with($trim,'[')) {
                $decoded=json_decode($trim,true);
                if (is_array($decoded)) $value=$decoded;
            } else {
                $value=preg_split('/[,\s]+/',$trim,-1,PREG_SPLIT_NO_EMPTY);
            }
        }
        if (!is_array($value)) throw new InvalidArgumentException($label.' must be an array.');
        $out=array();
        foreach ($value as $index=>$item) $out[]=self::finite($item,$label.'['.$index.']');
        if (count($out)<$minimum) throw new InvalidArgumentException($label.' requires at least '.$minimum.' values.');
        return $out;
    }

    private static function complement($sequence) {
        return strtr($sequence,array('A'=>'T','T'=>'A','U'=>'A','C'=>'G','G'=>'C','N'=>'N'));
    }

    private static function kmers($sequence,$k) {
        $out=array();
        for ($i=0;$i+$k<=strlen($sequence);$i++) $out[]=substr($sequence,$i,$k);
        return $out;
    }

    private static function motif_positions($sequence,$motif) {
        if ($motif==='') throw new InvalidArgumentException('motif must not be empty.');
        $out=array();$start=0;
        while (($position=strpos($sequence,$motif,$start))!==false) { $out[]=$position;$start=$position+1; }
        return $out;
    }

    private static function orfs($sequence) {
        $stops=array('TAA'=>true,'TAG'=>true,'TGA'=>true);$out=array();$length=strlen($sequence);
        for ($frame=0;$frame<3;$frame++) {
            for ($i=$frame;$i+2<$length;$i+=3) {
                if (substr($sequence,$i,3)==='ATG') {
                    for ($j=$i+3;$j+2<$length;$j+=3) {
                        if (isset($stops[substr($sequence,$j,3)])) { $out[]=array($frame,$i,$j+3);$i=$j;break; }
                    }
                }
            }
        }
        return $out;
    }

    private static function levenshtein_distance($a,$b) {
        return levenshtein($a,$b);
    }

    private static function codon_table() {
        return array(
            'TTT'=>'F','TTC'=>'F','TTA'=>'L','TTG'=>'L','TCT'=>'S','TCC'=>'S','TCA'=>'S','TCG'=>'S',
            'TAT'=>'Y','TAC'=>'Y','TAA'=>'*','TAG'=>'*','TGT'=>'C','TGC'=>'C','TGA'=>'*','TGG'=>'W',
            'CTT'=>'L','CTC'=>'L','CTA'=>'L','CTG'=>'L','CCT'=>'P','CCC'=>'P','CCA'=>'P','CCG'=>'P',
            'CAT'=>'H','CAC'=>'H','CAA'=>'Q','CAG'=>'Q','CGT'=>'R','CGC'=>'R','CGA'=>'R','CGG'=>'R',
            'ATT'=>'I','ATC'=>'I','ATA'=>'I','ATG'=>'M','ACT'=>'T','ACC'=>'T','ACA'=>'T','ACG'=>'T',
            'AAT'=>'N','AAC'=>'N','AAA'=>'K','AAG'=>'K','AGT'=>'S','AGC'=>'S','AGA'=>'R','AGG'=>'R',
            'GTT'=>'V','GTC'=>'V','GTA'=>'V','GTG'=>'V','GCT'=>'A','GCC'=>'A','GCA'=>'A','GCG'=>'A',
            'GAT'=>'D','GAC'=>'D','GAA'=>'E','GAG'=>'E','GGT'=>'G','GGC'=>'G','GGA'=>'G','GGG'=>'G'
        );
    }

    public static function execute($method_id,$inputs) {
        $method=self::method($method_id);$op=$method['operation'];$i=is_array($inputs)?$inputs:array();$s=self::norm($i['sequence']??'');$value=null;
        switch ($op) {
            case 'sequence_length': $value=strlen($s); break;
            case 'gc_content':
            case 'at_content':
                $valid=preg_replace('/[^ACGT]/','',$s);$length=strlen($valid);
                $count=$op==='gc_content' ? substr_count($valid,'G')+substr_count($valid,'C') : substr_count($valid,'A')+substr_count($valid,'T');
                $value=$length?$count/$length*100:0.0;break;
            case 'ambiguous_percent': $value=strlen($s)?strlen(preg_replace('/[ACGTU]/','',$s))/strlen($s)*100:0.0;break;
            case 'gc_skew': $g=substr_count($s,'G');$c=substr_count($s,'C');$value=$g+$c?($g-$c)/($g+$c):0.0;break;
            case 'sequence_entropy':
                $value=0.0;$length=strlen($s);
                if ($length) { foreach (array_count_values(str_split($s)) as $count) { $p=$count/$length;$value-=$p*log($p,2); } } break;
            case 'normalize_sequence': $value=$s;break;
            case 'complement': $value=self::complement($s);break;
            case 'reverse_complement': $value=strrev(self::complement($s));break;
            case 'transcribe': $value=str_replace('T','U',$s);break;
            case 'reverse_transcribe': $value=str_replace('U','T',$s);break;
            case 'base_counts':
                $value=array();foreach (str_split('ACGTUN') as $base) $value[$base]=substr_count($s,$base);
                $value['other']=strlen(preg_replace('/[ACGTUN]/','',$s));break;
            case 'translate':
                $frame=(int)self::finite($i['frame']??0,'frame');$dna=str_replace('U','T',$s);$table=self::codon_table();$value='';
                for ($j=$frame;$j+2<strlen($dna);$j+=3) { $codon=substr($dna,$j,3);$value.=$table[$codon]??'X'; } break;
            case 'codon_count': $frame=(int)self::finite($i['frame']??0,'frame');$value=max(0,(int)floor((strlen($s)-$frame)/3));break;
            case 'start_codon_count':
            case 'stop_codon_count':
                $value=0;
                for ($j=0;$j+2<strlen($s);$j++) { $codon=substr($s,$j,3); if ($op==='start_codon_count' ? $codon==='ATG' : in_array($codon,array('TAA','TAG','TGA'),true)) $value++; }
                break;
            case 'longest_orf_length': $found=self::orfs(str_replace('U','T',$s));$value=0;foreach($found as $orf)$value=max($value,$orf[2]-$orf[1]);break;
            case 'orf_count': $value=count(self::orfs(str_replace('U','T',$s)));break;
            case 'motif_count': $value=count(self::motif_positions($s,self::norm($i['motif']??'')));break;
            case 'motif_positions': $value=self::motif_positions($s,self::norm($i['motif']??''));break;
            case 'kmer_count': $k=(int)self::positive($i['k']??null,'k');$value=max(0,strlen($s)-$k+1);break;
            case 'unique_kmer_count': $k=(int)self::positive($i['k']??null,'k');$value=count(array_unique(self::kmers($s,$k)));break;
            case 'kmer_frequency':
                $kmer=self::norm($i['kmer']??'');if($kmer==='')throw new InvalidArgumentException('kmer must not be empty.');
                $all=self::kmers($s,strlen($kmer));$value=count($all)?count(array_filter($all,fn($x)=>$x===$kmer))/count($all)*100:0.0;break;
            case 'palindromic_kmer_count':
                $k=(int)self::positive($i['k']??null,'k');$value=0;foreach(self::kmers($s,$k) as $x)if($x===strrev(self::complement($x)))$value++;break;
            case 'hamming_distance':
            case 'levenshtein_distance':
            case 'percent_identity':
            case 'simple_alignment_score':
            case 'jaccard_kmers':
            case 'longest_common_prefix':
                $a=self::norm($i['reference']??'');$b=self::norm($i['query']??'');
                if ($op==='hamming_distance') { if(strlen($a)!==strlen($b))throw new InvalidArgumentException('Hamming distance requires equal sequence lengths.');$value=0;for($j=0;$j<strlen($a);$j++)if($a[$j]!==$b[$j])$value++; }
                elseif($op==='levenshtein_distance')$value=self::levenshtein_distance($a,$b);
                elseif($op==='percent_identity'){$n=max(strlen($a),strlen($b));$matches=0;for($j=0;$j<min(strlen($a),strlen($b));$j++)if($a[$j]===$b[$j])$matches++;$value=$n?$matches/$n*100:100.0;}
                elseif($op==='simple_alignment_score'){$match=self::finite($i['matchScore']??null,'matchScore');$mismatch=self::finite($i['mismatchScore']??null,'mismatchScore');$gap=self::finite($i['gapScore']??null,'gapScore');$value=0;$n=max(strlen($a),strlen($b));for($j=0;$j<$n;$j++)$value+=($j<strlen($a)&&$j<strlen($b))?($a[$j]===$b[$j]?$match:$mismatch):$gap;}
                elseif($op==='jaccard_kmers'){$k=(int)self::positive($i['k']??null,'k');$sa=array_unique(self::kmers($a,$k));$sb=array_unique(self::kmers($b,$k));$union=array_unique(array_merge($sa,$sb));$value=count($union)?count(array_intersect($sa,$sb))/count($union):1.0;}
                else{$value=0;$n=min(strlen($a),strlen($b));while($value<$n&&$a[$value]===$b[$value])$value++;}
                break;
            case 'variant_allele_frequency': $value=self::finite($i['alternateDepth']??null,'alternateDepth')/self::positive($i['readDepth']??null,'readDepth')*100;break;
            case 'reference_allele_frequency': $value=self::finite($i['referenceDepth']??null,'referenceDepth')/self::positive($i['readDepth']??null,'readDepth')*100;break;
            case 'allele_balance': $alt=self::finite($i['alternateDepth']??null,'alternateDepth');$ref=self::finite($i['referenceDepth']??null,'referenceDepth');$value=$alt+$ref?$alt/($alt+$ref)*100:0.0;break;
            case 'variant_density': $value=self::finite($i['variantCount']??null,'variantCount')/self::positive($i['sequenceLength']??null,'sequenceLength')*self::positive($i['scaleBases']??null,'scaleBases');break;
            case 'transition_transversion':
                $ref=self::norm($i['referenceBase']??'');$alt=self::norm($i['alternateBase']??'');
                if(strlen($ref)!==1||strlen($alt)!==1||strpos('ACGT',$ref)===false||strpos('ACGT',$alt)===false)$value='invalid';
                elseif($ref===$alt)$value='same';elseif(in_array($ref.$alt,array('AG','GA','CT','TC'),true))$value='transition';else$value='transversion';break;
            case 'genotype_quality': $p=self::positive($i['errorProbability']??null,'errorProbability');if($p>1)throw new InvalidArgumentException('errorProbability must not exceed 1.');$value=-10*log10($p);break;
            case 'allele_frequency': $value=self::finite($i['alleleCount']??null,'alleleCount')/self::positive($i['totalAlleles']??null,'totalAlleles');break;
            case 'expected_heterozygosity':
            case 'nucleotide_diversity': $p=self::finite($i['alleleFrequency']??null,'alleleFrequency');if($p<0||$p>1)throw new InvalidArgumentException('alleleFrequency must be between 0 and 1.');$value=2*$p*(1-$p);break;
            case 'observed_heterozygosity': $value=self::finite($i['heterozygoteCount']??null,'heterozygoteCount')/self::positive($i['individualCount']??null,'individualCount');break;
            case 'hardy_weinberg': $p=self::finite($i['alleleFrequency']??null,'alleleFrequency');if($p<0||$p>1)throw new InvalidArgumentException('alleleFrequency must be between 0 and 1.');$q=1-$p;$value=array('p2'=>$p*$p,'twoPq'=>2*$p*$q,'q2'=>$q*$q);break;
            case 'fst_simple': $ht=self::positive($i['totalHeterozygosity']??null,'totalHeterozygosity');$value=($ht-self::finite($i['subpopulationHeterozygosity']??null,'subpopulationHeterozygosity'))/$ht;break;
            case 'valid_base_percent': $value=strlen($s)?(strlen($s)-strlen(preg_replace('/[ACGTUN]/','',$s)))/strlen($s)*100:0.0;break;
            case 'assembly_n50': $lengths=self::values($i['lengths']??null,'lengths');rsort($lengths,SORT_NUMERIC);$half=array_sum($lengths)/2;$sum=0;$value=0;foreach($lengths as $length){$sum+=$length;if($sum>=$half){$value=$length;break;}}break;
            case 'mean_sequence_length': $lengths=self::values($i['lengths']??null,'lengths');$value=array_sum($lengths)/count($lengths);break;
            case 'sequence_length_cv': $lengths=self::values($i['lengths']??null,'lengths',2);$mean=array_sum($lengths)/count($lengths);$sum=0;foreach($lengths as $x)$sum+=($x-$mean)**2;$sd=sqrt($sum/(count($lengths)-1));$value=$mean?$sd/$mean*100:0.0;break;
            case 'metadata_coverage': $value=self::finite($i['recordsWithMetadata']??null,'recordsWithMetadata')/self::positive($i['totalRecords']??null,'totalRecords')*100;break;
            case 'duplicate_id_count': $ids=$i['identifiers']??array();if(!is_array($ids)||count($ids)===0)throw new InvalidArgumentException('identifiers requires at least one value.');$value=count($ids)-count(array_unique(array_map('strval',$ids)));break;
            default: throw new InvalidArgumentException('Unsupported genomic operation: '.$op);
        }
        return array('schema'=>'sc-lab-genomic-result/1.0','version'=>self::VERSION,'method'=>$method,'inputs'=>$inputs,'value'=>$value,'unit'=>$method['output']['unit']);
    }

    public static function batch_execute($rows) {
        $results=array();
        foreach($rows as $index=>$row){try{$results[]=array('row'=>$index+1,'ok'=>true,'result'=>self::execute((string)($row['methodId']??''),$row['inputs']??array()));}catch(Throwable $error){$results[]=array('row'=>$index+1,'ok'=>false,'error'=>$error->getMessage());}}
        $success=count(array_filter($results,fn($x)=>$x['ok']));
        return array('schema'=>'sc-lab-genomic-batch/1.0','version'=>self::VERSION,'rowCount'=>count($rows),'successCount'=>$success,'errorCount'=>count($rows)-$success,'results'=>$results);
    }

    public static function health_payload() {
        $c=self::catalog();$ready=($c['version']??null)===self::VERSION&&count($c['methods']??array())===48&&count($c['benchmarks']??array())===48&&count($c['categories']??array())===8;
        return array('ok'=>$ready,'status'=>$ready?'ready':'contract-incomplete','release'=>self::VERSION,'methodCount'=>count($c['methods']??array()),'benchmarkCount'=>count($c['benchmarks']??array()),'categoryCount'=>count($c['categories']??array()));
    }

    public static function register_routes() {
        register_rest_route(self::NAMESPACE,'/compute/genomics/methods',array('methods'=>'GET','callback'=>fn()=>rest_ensure_response(self::catalog()),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE,'/compute/genomics/health',array('methods'=>'GET','callback'=>fn()=>rest_ensure_response(self::health_payload()),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE,'/compute/genomics/run',array('methods'=>'POST','callback'=>array(__CLASS__,'run_response'),'permission_callback'=>'__return_true'));
        register_rest_route(self::NAMESPACE,'/compute/genomics/batch',array('methods'=>'POST','callback'=>array(__CLASS__,'batch_response'),'permission_callback'=>'__return_true'));
    }

    public static function run_response($request) {
        try{$p=$request->get_json_params();return rest_ensure_response(self::execute((string)($p['methodId']??''),$p['inputs']??array()));}
        catch(Throwable $error){return new WP_Error('sc_lab_v0240_genomic_error',$error->getMessage(),array('status'=>422));}
    }
    public static function batch_response($request) {$p=$request->get_json_params();return rest_ensure_response(self::batch_execute($p['rows']??array()));}
}
SC_Lab_Genetics_Genomics_REST_V0240::boot();
