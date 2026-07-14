from __future__ import annotations
import json, math, re
from pathlib import Path
from typing import Any

VERSION="0.24.0"
CONTRACT_PATH=Path(__file__).resolve().parents[2]/"contracts"/"genetics-genomics-sequence-analysis-v0240.json"
CODON_TABLE={'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*', 'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W', 'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L', 'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P', 'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q', 'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M', 'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T', 'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V', 'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A', 'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E', 'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'}

class GenomicError(ValueError):
    pass

def catalog()->dict[str,Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

def norm(value:Any)->str:
    return re.sub(r"\s+","",str(value or "")).upper()

def finite(value:Any,label:str)->float:
    try:number=float(value)
    except (TypeError,ValueError) as exc:raise GenomicError(f"{label} must be numerical.") from exc
    if not math.isfinite(number):raise GenomicError(f"{label} must be finite.")
    return number

def positive(value:Any,label:str)->float:
    number=finite(value,label)
    if number<=0:raise GenomicError(f"{label} must be greater than zero.")
    return number

def vals(value:Any,label:str,minimum:int=1)->list[float]:
    if not isinstance(value,list):raise GenomicError(f"{label} must be an array.")
    out=[finite(item,f"{label}[{idx}]") for idx,item in enumerate(value)]
    if len(out)<minimum:raise GenomicError(f"{label} requires at least {minimum} values.")
    return out

def complement(s:str)->str:
    table=str.maketrans({"A":"T","T":"A","U":"A","C":"G","G":"C","N":"N"})
    return s.translate(table)

def kmers(s:str,k:int)->list[str]:
    return [s[i:i+k] for i in range(max(0,len(s)-k+1))]

def motif_positions(s:str,motif:str)->list[int]:
    if not motif:raise GenomicError("motif must not be empty.")
    out=[];start=0
    while True:
        idx=s.find(motif,start)
        if idx<0:return out
        out.append(idx);start=idx+1

def orfs(s:str)->list[tuple[int,int,int]]:
    stops={"TAA","TAG","TGA"};out=[]
    for frame in range(3):
        i=frame
        while i+2<len(s):
            if s[i:i+3]=="ATG":
                j=i+3
                while j+2<len(s):
                    if s[j:j+3] in stops:
                        out.append((frame,i,j+3));i=j;break
                    j+=3
            i+=3
    return out

def levenshtein(a:str,b:str)->int:
    previous=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        current=[i]
        for j,cb in enumerate(b,1):
            current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(ca!=cb)))
        previous=current
    return previous[-1]

def execute(method_id:str,inputs:dict[str,Any])->dict[str,Any]:
    definitions={m["id"]:m for m in catalog()["methods"]}
    if method_id not in definitions:raise GenomicError(f"Unknown genomic method: {method_id}")
    m=definitions[method_id];op=m["operation"];i=inputs or {}
    s=norm(i.get("sequence"))
    if op=="sequence_length":value=len(s)
    elif op=="gc_content":
        valid=[c for c in s if c in "ACGT"];value=(sum(c in "GC" for c in valid)/len(valid)*100) if valid else 0.0
    elif op=="at_content":
        valid=[c for c in s if c in "ACGT"];value=(sum(c in "AT" for c in valid)/len(valid)*100) if valid else 0.0
    elif op=="ambiguous_percent":value=(sum(c not in "ACGTU" for c in s)/len(s)*100) if s else 0.0
    elif op=="gc_skew":
        g=s.count("G");c=s.count("C");value=(g-c)/(g+c) if g+c else 0.0
    elif op=="sequence_entropy":
        value=0.0
        if s:
            for symbol in set(s):
                p=s.count(symbol)/len(s);value-=p*math.log2(p)
    elif op=="normalize_sequence":value=s
    elif op=="complement":value=complement(s)
    elif op=="reverse_complement":value=complement(s)[::-1]
    elif op=="transcribe":value=s.replace("T","U")
    elif op=="reverse_transcribe":value=s.replace("U","T")
    elif op=="base_counts":
        value={b:s.count(b) for b in "ACGTUN"};value["other"]=sum(c not in "ACGTUN" for c in s)
    elif op=="translate":
        frame=int(finite(i.get("frame",0),"frame"));dna=s.replace("U","T")
        value="".join(CODON_TABLE.get(dna[j:j+3],"X") for j in range(frame,len(dna)-2,3))
    elif op=="codon_count":
        frame=int(finite(i.get("frame",0),"frame"));value=max(0,(len(s)-frame)//3)
    elif op=="start_codon_count":value=sum(1 for j in range(0,len(s)-2) if s[j:j+3]=="ATG")
    elif op=="stop_codon_count":value=sum(1 for j in range(0,len(s)-2) if s[j:j+3] in {"TAA","TAG","TGA"})
    elif op=="longest_orf_length":
        found=orfs(s.replace("U","T"));value=max((end-start for _,start,end in found),default=0)
    elif op=="orf_count":value=len(orfs(s.replace("U","T")))
    elif op=="motif_count":
        value=len(motif_positions(s,norm(i.get("motif"))))
    elif op=="motif_positions":value=motif_positions(s,norm(i.get("motif")))
    elif op=="kmer_count":
        k=int(positive(i.get("k"),"k"));value=max(0,len(s)-k+1)
    elif op=="unique_kmer_count":
        k=int(positive(i.get("k"),"k"));value=len(set(kmers(s,k)))
    elif op=="kmer_frequency":
        kmer=norm(i.get("kmer"));all_k=kmers(s,len(kmer))
        if not kmer:raise GenomicError("kmer must not be empty.")
        value=(all_k.count(kmer)/len(all_k)*100) if all_k else 0.0
    elif op=="palindromic_kmer_count":
        k=int(positive(i.get("k"),"k"));value=sum(x==complement(x)[::-1] for x in kmers(s,k))
    elif op in {"hamming_distance","levenshtein_distance","percent_identity","simple_alignment_score","jaccard_kmers","longest_common_prefix"}:
        a=norm(i.get("reference"));b=norm(i.get("query"))
        if op=="hamming_distance":
            if len(a)!=len(b):raise GenomicError("Hamming distance requires equal sequence lengths.")
            value=sum(x!=y for x,y in zip(a,b))
        elif op=="levenshtein_distance":value=levenshtein(a,b)
        elif op=="percent_identity":
            n=max(len(a),len(b));value=(sum(x==y for x,y in zip(a,b))/n*100) if n else 100.0
        elif op=="simple_alignment_score":
            match=finite(i.get("matchScore"),"matchScore");mismatch=finite(i.get("mismatchScore"),"mismatchScore");gap=finite(i.get("gapScore"),"gapScore")
            n=max(len(a),len(b));value=sum(match if j<len(a) and j<len(b) and a[j]==b[j] else mismatch if j<len(a) and j<len(b) else gap for j in range(n))
        elif op=="jaccard_kmers":
            k=int(positive(i.get("k"),"k"));sa=set(kmers(a,k));sb=set(kmers(b,k));u=sa|sb;value=len(sa&sb)/len(u) if u else 1.0
        else:
            value=0
            for x,y in zip(a,b):
                if x!=y:break
                value+=1
    elif op=="variant_allele_frequency":value=finite(i.get("alternateDepth"),"alternateDepth")/positive(i.get("readDepth"),"readDepth")*100
    elif op=="reference_allele_frequency":value=finite(i.get("referenceDepth"),"referenceDepth")/positive(i.get("readDepth"),"readDepth")*100
    elif op=="allele_balance":
        alt=finite(i.get("alternateDepth"),"alternateDepth");ref=finite(i.get("referenceDepth"),"referenceDepth")
        value=alt/(alt+ref)*100 if alt+ref else 0.0
    elif op=="variant_density":value=finite(i.get("variantCount"),"variantCount")/positive(i.get("sequenceLength"),"sequenceLength")*positive(i.get("scaleBases"),"scaleBases")
    elif op=="transition_transversion":
        ref=norm(i.get("referenceBase"));alt=norm(i.get("alternateBase"))
        if len(ref)!=1 or len(alt)!=1 or ref not in "ACGT" or alt not in "ACGT":value="invalid"
        elif ref==alt:value="same"
        elif {ref,alt} in ({"A","G"},{"C","T"}):value="transition"
        else:value="transversion"
    elif op=="genotype_quality":
        p=positive(i.get("errorProbability"),"errorProbability")
        if p>1:raise GenomicError("errorProbability must not exceed 1.")
        value=-10*math.log10(p)
    elif op=="allele_frequency":value=finite(i.get("alleleCount"),"alleleCount")/positive(i.get("totalAlleles"),"totalAlleles")
    elif op in {"expected_heterozygosity","nucleotide_diversity"}:
        p=finite(i.get("alleleFrequency"),"alleleFrequency")
        if not 0<=p<=1:raise GenomicError("alleleFrequency must be between 0 and 1.")
        value=2*p*(1-p)
    elif op=="observed_heterozygosity":value=finite(i.get("heterozygoteCount"),"heterozygoteCount")/positive(i.get("individualCount"),"individualCount")
    elif op=="hardy_weinberg":
        p=finite(i.get("alleleFrequency"),"alleleFrequency");q=1-p
        if not 0<=p<=1:raise GenomicError("alleleFrequency must be between 0 and 1.")
        value={"p2":p*p,"twoPq":2*p*q,"q2":q*q}
    elif op=="fst_simple":
        ht=positive(i.get("totalHeterozygosity"),"totalHeterozygosity");hs=finite(i.get("subpopulationHeterozygosity"),"subpopulationHeterozygosity");value=(ht-hs)/ht
    elif op=="valid_base_percent":value=(sum(c in "ACGTUN" for c in s)/len(s)*100) if s else 0.0
    elif op=="assembly_n50":
        lengths=sorted(vals(i.get("lengths"),"lengths"),reverse=True);half=sum(lengths)/2;cum=0;value=0
        for length in lengths:
            cum+=length
            if cum>=half:value=length;break
    elif op=="mean_sequence_length":value=sum(vals(i.get("lengths"),"lengths"))/len(vals(i.get("lengths"),"lengths"))
    elif op=="sequence_length_cv":
        lengths=vals(i.get("lengths"),"lengths",2);mean=sum(lengths)/len(lengths);sd=math.sqrt(sum((x-mean)**2 for x in lengths)/(len(lengths)-1));value=sd/mean*100 if mean else 0.0
    elif op=="metadata_coverage":value=finite(i.get("recordsWithMetadata"),"recordsWithMetadata")/positive(i.get("totalRecords"),"totalRecords")*100
    elif op=="duplicate_id_count":
        ids=[str(x) for x in i.get("identifiers") or []]
        if not ids:raise GenomicError("identifiers requires at least one value.")
        value=len(ids)-len(set(ids))
    else:raise GenomicError(f"Unsupported genomic operation: {op}")
    return {"schema":"sc-lab-genomic-result/1.0","version":VERSION,"method":m,"inputs":inputs,"value":value,"unit":m["output"]["unit"]}

def batch_execute(rows:list[dict[str,Any]])->dict[str,Any]:
    results=[]
    for idx,row in enumerate(rows):
        try:results.append({"row":idx+1,"ok":True,"result":execute(str(row.get("methodId") or ""),row.get("inputs") or {})})
        except Exception as exc:results.append({"row":idx+1,"ok":False,"error":str(exc)})
    return {"schema":"sc-lab-genomic-batch/1.0","version":VERSION,"rowCount":len(rows),"successCount":sum(r["ok"] for r in results),"errorCount":sum(not r["ok"] for r in results),"results":results}
