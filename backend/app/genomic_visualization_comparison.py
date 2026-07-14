from __future__ import annotations
import json,re
from pathlib import Path
from typing import Any
VERSION="0.24.2";CONTRACT_PATH=Path(__file__).resolve().parents[2]/"contracts"/"genomic-visualization-comparison-v0242.json"
def contract():return json.loads(CONTRACT_PATH.read_text())
def norm(v):return re.sub(r"\s+","",str(v or "")).upper()
def execute(method_id:str,inputs:dict[str,Any]):
 i=inputs or {};s=norm(i.get("sequence"))
 if method_id=="mismatch-positions":
  a=norm(i.get("reference"));b=norm(i.get("query"));value=[j for j in range(max(len(a),len(b))) if (a[j] if j<len(a) else "-")!=(b[j] if j<len(b) else "-")]
 elif method_id=="windowed-gc":
  w=int(i.get("windowSize"));step=int(i.get("stepSize"));value=[]
  for start in range(0,len(s),step):
   part=s[start:start+w];valid=[c for c in part if c in "ACGT"];gc=(sum(c in "GC" for c in valid)/len(valid)*100) if valid else 0.0
   value.append({"start":start,"end":min(start+w,len(s)),"gcPercent":gc})
 elif method_id=="motif-hits":
  m=norm(i.get("motif"));value=[];p=0
  while m:
   j=s.find(m,p)
   if j<0:break
   value.append(j);p=j+1
 elif method_id=="kmer-spectrum":
  k=int(i.get("k"));value={}
  for j in range(max(0,len(s)-k+1)):value[s[j:j+k]]=value.get(s[j:j+k],0)+1
 elif method_id=="variant-track":
  length=float(i.get("sequenceLength"));value=[{**v,"fraction":float(v["position"])/length} for v in i.get("variants",[])]
 elif method_id=="alignment-padding":
  a=norm(i.get("reference"));b=norm(i.get("query"));n=max(len(a),len(b));value={"reference":a.ljust(n,"-"),"query":b.ljust(n,"-")}
 elif method_id=="sequence-summary":
  valid=[c for c in s if c in "ACGT"];value={"length":len(s),"gcPercent":(sum(c in "GC" for c in valid)/len(valid)*100 if valid else 0.0),"ambiguousCount":sum(c not in "ACGTU" for c in s)}
 elif method_id=="comparison-summary":
  a=norm(i.get("reference"));b=norm(i.get("query"));n=max(len(a),len(b));m=sum((a[j] if j<len(a) else "-")!=(b[j] if j<len(b) else "-") for j in range(n));value={"referenceLength":len(a),"queryLength":len(b),"mismatchCount":m,"identityPercent":((n-m)/n*100 if n else 100.0)}
 else:raise ValueError("Unknown visualization method")
 return {"version":VERSION,"methodId":method_id,"value":value}
