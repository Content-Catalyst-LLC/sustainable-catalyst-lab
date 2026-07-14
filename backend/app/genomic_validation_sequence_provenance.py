from __future__ import annotations
import hashlib,json,math,re,secrets
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

VERSION="0.24.3"
CONTRACT_PATH=Path(__file__).resolve().parents[2]/"contracts"/"genomic-validation-sequence-provenance-v0243.json"

class GenomicValidationError(ValueError):pass
def contract():return json.loads(CONTRACT_PATH.read_text())
def canonical_json(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False)
def fingerprint(value):return hashlib.sha256(canonical_json(value).encode()).hexdigest()
def norm(v):return re.sub(r"\s+","",str(v or "")).upper()
def finite(v,l):
 try:n=float(v)
 except (TypeError,ValueError) as exc:raise GenomicValidationError(f"{l} must be numerical.") from exc
 if not math.isfinite(n):raise GenomicValidationError(f"{l} must be finite.")
 return n
def profile(pid):
 for p in contract()["profiles"]:
  if p["id"]==pid:return p
 raise GenomicValidationError(f"Unknown validation profile: {pid}")
def check(cid,label,value,operator,limit,passed,unit=""):
 return {"id":cid,"label":label,"value":value,"operator":operator,"limit":limit,"unit":unit,"passed":bool(passed),"status":"pass" if passed else "fail"}

def evaluate(profile_id:str,rows:list[dict[str,Any]],thresholds:dict[str,Any]|None=None)->dict[str,Any]:
 p=profile(profile_id);limits={**p["thresholds"],**(thresholds or {})}
 if not rows:raise GenomicValidationError("Validation requires at least one row.")
 for idx,row in enumerate(rows):
  for key in p["required"]:
   if key not in row:raise GenomicValidationError(f"Required field {key} is missing from row {idx+1}.")
 metrics={};checks=[]
 if profile_id=="sequence-record-integrity":
  ids=[];invalid=0
  for row in rows:
   sid=str(row.get("sequenceId") or "").strip();seq=norm(row.get("sequence"));alphabet=str(row.get("alphabet") or "").upper()
   ids.append(sid)
   allowed="ACGTN" if alphabet in {"DNA","DNA-IUPAC"} else "ACGUN" if alphabet in {"RNA","RNA-IUPAC"} else ""
   if not sid or not seq or not allowed or any(c not in allowed for c in seq):invalid+=1
  duplicates=len(ids)-len(set(ids));metrics={"recordCount":len(rows),"invalidRecordCount":invalid,"duplicateIdCount":duplicates}
  checks=[check("invalid-records","Invalid sequence records",invalid,"<=",limits["maximumInvalidRecords"],invalid<=limits["maximumInvalidRecords"]),
          check("duplicate-identifiers","Duplicate sequence identifiers",duplicates,"<=",limits["maximumDuplicateIds"],duplicates<=limits["maximumDuplicateIds"])]
 elif profile_id=="metadata-linkage":
  sequence_ids={str(r["sequenceId"]) for r in rows};metadata_ids=[str(r["metadataId"]) for r in rows if str(r.get("metadataId") or "").strip()]
  missing=sum(not str(r.get("metadataId") or "").strip() for r in rows);unmatched=sum(mid not in sequence_ids for mid in metadata_ids)
  metrics={"sequenceRecordCount":len(rows),"missingMetadataCount":missing,"unmatchedMetadataCount":unmatched}
  checks=[check("missing-metadata","Missing metadata links",missing,"<=",limits["maximumMissingMetadata"],missing<=limits["maximumMissingMetadata"]),
          check("unmatched-metadata","Unmatched metadata identifiers",unmatched,"<=",limits["maximumUnmatchedMetadata"],unmatched<=limits["maximumUnmatchedMetadata"])]
 elif profile_id=="reference-coordinate-context":
  missing=0;invalid_positions=0
  for r in rows:
   if any(not str(r.get(k) or "").strip() for k in ("referenceBuild","coordinateSystem","contig")):missing+=1
   if finite(r.get("position"),"position")<finite(limits["minimumPosition"],"minimumPosition"):invalid_positions+=1
  metrics={"recordCount":len(rows),"missingContextCount":missing,"invalidPositionCount":invalid_positions}
  checks=[check("missing-context","Missing reference context",missing,"<=",limits["maximumMissingContext"],missing<=limits["maximumMissingContext"]),
          check("minimum-position","Positions below minimum",invalid_positions,"=",0,invalid_positions==0)]
 elif profile_id=="sequence-quality":
  failures=0;summaries=[]
  for r in rows:
   seq=norm(r["sequence"]);valid=sum(c in "ACGTUN" for c in seq);amb=sum(c not in "ACGTU" for c in seq)
   valid_pct=valid/len(seq)*100 if seq else 0;amb_pct=amb/len(seq)*100 if seq else 100
   passed=len(seq)>=limits["minimumLength"] and valid_pct>=limits["minimumValidBasePercent"] and amb_pct<=limits["maximumAmbiguousPercent"]
   failures+=not passed;summaries.append({"sequenceId":r["sequenceId"],"length":len(seq),"validBasePercent":valid_pct,"ambiguousPercent":amb_pct,"passed":passed})
  metrics={"recordCount":len(rows),"failureCount":failures,"sequences":summaries}
  checks=[check("sequence-quality-failures","Sequences failing quality criteria",failures,"=",0,failures==0)]
 elif profile_id=="variant-record-integrity":
  invalid=0;summaries=[]
  for r in rows:
   ref=norm(r["referenceBase"]);alt=norm(r["alternateBase"]);pos=finite(r["position"],"position");depth=finite(r["readDepth"],"readDepth");ad=finite(r["alternateDepth"],"alternateDepth")
   passed=len(ref)==1 and len(alt)==1 and ref in "ACGT" and alt in "ACGT" and ref!=alt and pos>=1 and depth>=limits["minimumReadDepth"] and 0<=ad<=depth
   invalid+=not passed;summaries.append({"variantId":r["variantId"],"passed":passed,"alleleFraction":ad/depth if depth else None})
  metrics={"variantCount":len(rows),"invalidVariantCount":invalid,"variants":summaries}
  checks=[check("invalid-variants","Invalid variant records",invalid,"<=",limits["maximumInvalidVariants"],invalid<=limits["maximumInvalidVariants"])]
 elif profile_id=="analysis-reproducibility":
  incomplete=0
  for r in rows:
   if any(not str(r.get(k) or "").strip() for k in p["required"]):incomplete+=1
  metrics={"stepCount":len(rows),"incompleteStepCount":incomplete}
  checks=[check("incomplete-steps","Incomplete reproducibility records",incomplete,"<=",limits["maximumIncompleteSteps"],incomplete<=limits["maximumIncompleteSteps"])]
 elif profile_id=="annotation-evidence":
  invalid=0;evidence=0
  for r in rows:
   start=finite(r["start"],"start");end=finite(r["end"],"end");has=bool(str(r.get("evidence") or "").strip());evidence+=has
   if not str(r.get("annotationId") or "").strip() or not str(r.get("type") or "").strip() or start<0 or end<start or not has:invalid+=1
  coverage=evidence/len(rows)*100;metrics={"annotationCount":len(rows),"invalidAnnotationCount":invalid,"evidenceCoveragePercent":coverage}
  checks=[check("invalid-annotations","Invalid annotations",invalid,"<=",limits["maximumInvalidAnnotations"],invalid<=limits["maximumInvalidAnnotations"]),
          check("annotation-evidence","Annotation evidence coverage",coverage,">=",limits["minimumEvidenceCoveragePercent"],coverage>=limits["minimumEvidenceCoveragePercent"],"%")]
 elif profile_id=="release-readiness":
  failed=0;evidence=0
  for r in rows:
   status=str(r["status"]).lower();critical=str(r["critical"]).lower() in {"1","true","yes","critical"};complete=status in {"pass","passed","closed","complete","accepted"};failed+=critical and not complete;evidence+=bool(str(r.get("evidence") or "").strip())
  coverage=evidence/len(rows)*100;metrics={"checkCount":len(rows),"failedCriticalCheckCount":failed,"evidenceCoveragePercent":coverage}
  checks=[check("failed-critical","Failed critical checks",failed,"<=",limits["maximumFailedCriticalChecks"],failed<=limits["maximumFailedCriticalChecks"]),
          check("release-evidence","Release evidence coverage",coverage,">=",limits["minimumEvidenceCoveragePercent"],coverage>=limits["minimumEvidenceCoveragePercent"],"%")]
 else:raise GenomicValidationError("Unsupported profile.")
 failed=[c for c in checks if not c["passed"]]
 return {"schema":"sc-lab-genomic-validation-result/1.0","version":VERSION,"profile":p,"thresholds":limits,"metrics":metrics,"checks":checks,"decision":"fail" if failed else "pass","failedCheckCount":len(failed),"releaseRecommendation":"hold" if failed else "release"}

def create_manifest(sequences=None,metadata=None,reference=None,pipeline=None,variants=None,annotations=None):
 components={"sequences":sequences or [],"metadata":metadata or [],"reference":reference or {},"pipeline":pipeline or [],"variants":variants or [],"annotations":annotations or []}
 manifest={"schema":"sc-lab-genomic-dataset-manifest/1.0","version":VERSION,"createdAt":datetime.now(timezone.utc).isoformat(),"components":{}}
 for key,value in components.items():manifest["components"][key]={"count":len(value) if isinstance(value,list) else (1 if value else 0),"hash":fingerprint(value)}
 manifest["manifestHash"]=fingerprint(manifest);return manifest

def create_record(payload,metadata=None,previous_hash=None):
 metadata=dict(metadata or {});event=metadata.get("eventType") or contract()["defaults"]["eventType"];allowed={x["id"] for x in contract()["eventTypes"]}
 if event not in allowed:raise GenomicValidationError(f"Unknown event type: {event}")
 record={"schema":"sc-lab-genomic-sequence-provenance/1.0","version":VERSION,"recordId":metadata.get("recordId") or "scgen-"+datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")+"-"+secrets.token_hex(5),"eventType":event,"timestamp":metadata.get("timestamp") or datetime.now(timezone.utc).isoformat(),"datasetId":metadata.get("datasetId"),"sequenceId":metadata.get("sequenceId"),"variantId":metadata.get("variantId"),"referenceBuild":metadata.get("referenceBuild"),"coordinateSystem":metadata.get("coordinateSystem"),"pipelineVersion":metadata.get("pipelineVersion"),"analyst":metadata.get("analyst"),"reviewer":metadata.get("reviewer"),"organization":metadata.get("organization") or contract()["defaults"]["organization"],"sourceRecordIds":list(metadata.get("sourceRecordIds") or []),"evidenceLinks":list(metadata.get("evidenceLinks") or []),"disposition":metadata.get("disposition") or contract()["defaults"]["disposition"],"notes":metadata.get("notes"),"previousHash":previous_hash,"payloadHash":fingerprint(payload),"payload":payload,"engine":{"genomicsRelease":"0.24.0","productionRelease":"0.24.1","visualizationRelease":"0.24.2","validationRelease":VERSION}}
 record["recordHash"]=fingerprint(record);return record

def verify_ledger(records):
 results=[];previous=None
 for record in records:
  copy=dict(record);stored=str(copy.pop("recordHash",""));calculated=fingerprint(copy);payload_valid=record.get("payloadHash")==fingerprint(record.get("payload"));hash_valid=secrets.compare_digest(stored,calculated);chain_valid=record.get("previousHash")==previous
  results.append({"recordId":record.get("recordId"),"payloadValid":payload_valid,"hashValid":hash_valid,"chainValid":chain_valid,"valid":payload_valid and hash_valid and chain_valid,"storedHash":stored,"calculatedHash":calculated});previous=stored
 return {"schema":"sc-lab-genomic-ledger-verification/1.0","version":VERSION,"valid":all(r["valid"] for r in results),"recordCount":len(records),"results":results}

def create_dossier(validation_results,manifest,records,disposition=None):
 failed=[r for r in validation_results if r.get("decision")!="pass"];ledger=verify_ledger(records);resolved=disposition or ("hold" if failed or not ledger["valid"] else "release")
 dossier={"schema":"sc-lab-genomic-validation-dossier/1.0","version":VERSION,"createdAt":datetime.now(timezone.utc).isoformat(),"summary":{"validationResultCount":len(validation_results),"failedValidationCount":len(failed),"recordCount":len(records),"ledgerValid":ledger["valid"],"manifestValid":manifest.get("manifestHash")==fingerprint({k:v for k,v in manifest.items() if k!="manifestHash"}),"disposition":resolved},"manifest":manifest,"validationResults":validation_results,"provenanceLedger":records,"ledgerVerification":ledger,"responsibleUse":contract()["responsibleUse"]}
 dossier["summary"]["releaseReady"]=dossier["summary"]["failedValidationCount"]==0 and dossier["summary"]["ledgerValid"] and dossier["summary"]["manifestValid"] and resolved=="release";dossier["dossierHash"]=fingerprint(dossier);return dossier
