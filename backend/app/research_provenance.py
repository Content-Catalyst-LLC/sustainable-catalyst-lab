from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any
VERSION = "0.29.0"
SOURCE_SCHEMA = "sc-lab-research-source/0.29.0"
EVIDENCE_SCHEMA = "sc-lab-evidence-record/0.29.0"
PROVENANCE_SCHEMA = "sc-lab-research-provenance/0.29.0"
class ProvenanceError(ValueError): pass
def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()
def health() -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"schemas":[SOURCE_SCHEMA,EVIDENCE_SCHEMA,PROVENANCE_SCHEMA],"citationStyle":"harvard-author-date","arbitraryRemoteFetch":False,"serverBackedRegistry":False}
def normalize_source(payload: dict[str, Any]) -> dict[str, Any]:
    title=str(payload.get("title") or "").strip()
    if not title: raise ProvenanceError("Source title is required.")
    source={
      "schema":SOURCE_SCHEMA,"version":VERSION,"recordType":"research-source",
      "id":str(payload.get("id") or f"src-{_hash(payload)[:16]}"),"title":title,
      "authors":[str(x).strip() for x in payload.get("authors",[]) if str(x).strip()],
      "year":payload.get("year"),"sourceType":str(payload.get("sourceType") or "other"),
      "publisher":str(payload.get("publisher") or ""),"containerTitle":str(payload.get("containerTitle") or ""),
      "doi":str(payload.get("doi") or ""),"url":str(payload.get("url") or ""),
      "license":str(payload.get("license") or ""),"retrievedAt":payload.get("retrievedAt"),
      "knowledgeLibraryId":payload.get("knowledgeLibraryId"),"researchLibrarianHandoff":payload.get("researchLibrarianHandoff"),
      "createdAt":payload.get("createdAt") or datetime.now(timezone.utc).isoformat(),
    }
    author=(source["authors"][0] if source["authors"] else source["publisher"] or source["title"])
    surname=author.split(",")[0].split()[-1] if author else source["title"]
    year=str(source["year"] or "n.d.")
    source["citation"]={"style":"harvard-author-date","inText":f"({surname}, {year})","bibliography":f"{', '.join(source['authors']) or source['publisher'] or source['title']} ({year}) {source['title']}."}
    source["sha256"]=_hash({k:v for k,v in source.items() if k!="sha256"})
    return source
def normalize_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    source_id=str(payload.get("sourceId") or "").strip(); excerpt=str(payload.get("excerpt") or "").strip()
    if not source_id or not excerpt: raise ProvenanceError("sourceId and excerpt are required.")
    rec={"schema":EVIDENCE_SCHEMA,"version":VERSION,"recordType":"evidence-record","id":str(payload.get("id") or f"ev-{_hash(payload)[:16]}"),"sourceId":source_id,"excerpt":excerpt[:12000],"locator":str(payload.get("locator") or ""),"claim":str(payload.get("claim") or ""),"strength":str(payload.get("strength") or "supporting"),"notes":str(payload.get("notes") or ""),"createdAt":payload.get("createdAt") or datetime.now(timezone.utc).isoformat()}
    rec["sha256"]=_hash({k:v for k,v in rec.items() if k!="sha256"}); return rec
def verify_record(payload: dict[str, Any]) -> dict[str, Any]:
    record=payload.get("record") or payload
    expected=str(record.get("sha256") or "")
    actual=_hash({k:v for k,v in record.items() if k!="sha256"})
    return {"ok":bool(expected) and expected==actual,"expected":expected,"actual":actual,"recordType":record.get("recordType")}
def build_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    links=payload.get("links") or []
    out={"schema":PROVENANCE_SCHEMA,"version":VERSION,"recordType":"research-provenance","id":str(payload.get("id") or f"prov-{_hash(payload)[:16]}"),"projectId":payload.get("projectId"),"subjectId":payload.get("subjectId"),"subjectType":payload.get("subjectType"),"sourceIds":list(dict.fromkeys(payload.get("sourceIds") or [])),"evidenceIds":list(dict.fromkeys(payload.get("evidenceIds") or [])),"assumptions":payload.get("assumptions") or [],"limitations":payload.get("limitations") or [],"methodology":payload.get("methodology") or [],"links":links,"createdAt":payload.get("createdAt") or datetime.now(timezone.utc).isoformat()}
    out["sha256"]=_hash({k:v for k,v in out.items() if k!="sha256"}); return out
