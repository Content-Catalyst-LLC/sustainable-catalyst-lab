from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone

VERSION="0.135.12.0"
ROUTE_COUNT=10
KINDS=("observation","question","limitation","claim-link","evidence-note")
SCOPES=("path","edge","node","object-a","object-b")
STATUSES=("draft","in-review","revised","archived")


def _text(value, limit=4000):
    return str(value or "").strip()[:limit]


def _iso(value):
    v=_text(value,128)
    return v or None


def normalize_annotation(raw:dict, index:int=0):
    if not isinstance(raw,dict):
        raise ValueError("annotation must be an object")
    kind=_text(raw.get("kind"),64)
    scope=_text(raw.get("scope"),64)
    note=_text(raw.get("note"),12000)
    target=_text(raw.get("targetId",raw.get("target_id")),512)
    claim_ref=_text(raw.get("claimRef",raw.get("claim_ref")),512) or None
    if kind not in KINDS: raise ValueError(f"unsupported annotation kind: {kind}")
    if scope not in SCOPES: raise ValueError(f"unsupported annotation scope: {scope}")
    if not note: raise ValueError("annotation note is required")
    if not target: raise ValueError("annotation target is required")
    if kind=="claim-link" and not claim_ref: raise ValueError("claim-link annotations require claimRef")
    try: path_index=max(0,int(raw.get("pathIndex",raw.get("path_index",0))))
    except Exception: path_index=0
    edges=[_text(x,512) for x in (raw.get("pathEdges",raw.get("path_edges")) or []) if _text(x,512)]
    return {
        "id":_text(raw.get("id"),256) or f"annotation-{index+1}",
        "kind":kind,"scope":scope,"target_id":target,"claim_ref":claim_ref,"note":note,
        "path_index":path_index,"path_edges":edges,"created_at":_iso(raw.get("createdAt",raw.get("created_at"))),
        "author":_text(raw.get("author"),256) or "user",
    }


def normalize_thread(payload:dict):
    raw=payload.get("thread") if isinstance(payload,dict) and isinstance(payload.get("thread"),dict) else payload
    if not isinstance(raw,dict): return {"ok":False,"version":VERSION,"error":"thread payload must be an object"}
    status=_text(raw.get("status"),64) or "draft"
    if status not in STATUSES: return {"ok":False,"version":VERSION,"error":f"unsupported thread status: {status}"}
    annotations=[]
    try:
        for i,a in enumerate((raw.get("annotations") or [])[:200]): annotations.append(normalize_annotation(a,i))
    except ValueError as e:
        return {"ok":False,"version":VERSION,"error":str(e)}
    out={
        "schema":"sc-lab-graph-studio-provenance-review-thread/0.135.12.0",
        "version":VERSION,
        "record_type":"graph-studio-provenance-review-thread",
        "collection":"graphStudioReviewThreads",
        "id":_text(raw.get("id"),256) or "provenance-review-thread",
        "title":_text(raw.get("title"),1024) or "Provenance review thread",
        "status":status,
        "comparison_signature":_text(raw.get("comparisonSignature",raw.get("comparison_signature")),2048) or None,
        "object_a":raw.get("objectA",raw.get("object_a")) if isinstance(raw.get("objectA",raw.get("object_a")),dict) else None,
        "object_b":raw.get("objectB",raw.get("object_b")) if isinstance(raw.get("objectB",raw.get("object_b")),dict) else None,
        "mode":_text(raw.get("mode"),64) or None,
        "max_hops":raw.get("maxHops",raw.get("max_hops")),
        "candidate_path_count":max(0,int(raw.get("candidatePathCount",raw.get("candidate_path_count",0)) or 0)),
        "selected_path_index":max(0,int(raw.get("selectedPathIndex",raw.get("selected_path_index",0)) or 0)),
        "selected_path":raw.get("selectedPath",raw.get("selected_path")) if isinstance(raw.get("selectedPath",raw.get("selected_path")),dict) else None,
        "annotations":annotations,
        "created_at":_iso(raw.get("createdAt",raw.get("created_at"))),
        "updated_at":_iso(raw.get("updatedAt",raw.get("updated_at"))),
        "boundary":"Annotations and claim links are explicit reviewer-authored records attached to declared provenance context. No truth, evidentiary weight, causation, or scientific preference is inferred.",
    }
    return {"ok":True,"version":VERSION,"thread":out,"annotation_count":len(annotations)}


def summarize_thread(payload:dict):
    n=normalize_thread(payload)
    if not n.get("ok"): return n
    anns=n["thread"]["annotations"]
    by_kind={k:0 for k in KINDS}; by_scope={s:0 for s in SCOPES}
    for a in anns:
        by_kind[a["kind"]]+=1; by_scope[a["scope"]]+=1
    return {"ok":True,"version":VERSION,"annotation_count":len(anns),"by_kind":by_kind,"by_scope":by_scope,"explicit_claim_ref_count":sum(1 for a in anns if a["claim_ref"]),"review_status":n["thread"]["status"]}


def claim_links(payload:dict):
    n=normalize_thread(payload)
    if not n.get("ok"): return n
    links=[{"annotation_id":a["id"],"claim_ref":a["claim_ref"],"scope":a["scope"],"target_id":a["target_id"],"note":a["note"]} for a in n["thread"]["annotations"] if a["kind"]=="claim-link" and a["claim_ref"]]
    return {"ok":True,"version":VERSION,"links":links,"explicit_only":True,"inferred_claim_links":False}


def review_packet(payload:dict):
    n=normalize_thread(payload)
    if not n.get("ok"): return n
    summary=summarize_thread(n["thread"]); links=claim_links(n["thread"])
    return {"ok":True,"version":VERSION,"target":"project-workspace","thread":n["thread"],"summary":summary,"claim_links":links["links"],"boundary":n["thread"]["boundary"]}


def fingerprint(payload:dict):
    n=normalize_thread(payload)
    if not n.get("ok"): return n
    canonical=json.dumps(n["thread"],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return {"ok":True,"version":VERSION,"algorithm":"sha256","fingerprint":hashlib.sha256(canonical).hexdigest(),"canonical_bytes":len(canonical)}


def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"review_thread":True,"path_annotations":True,"explicit_claim_linkage":True,"project_persistence_explicit":True,"cross_workspace_review_handoff":True}
def thread_contract(): return {"ok":True,"version":VERSION,"statuses":list(STATUSES),"max_annotations":200,"project_collection":"graphStudioReviewThreads","explicit_save":True}
def annotation_contract(): return {"ok":True,"version":VERSION,"kinds":list(KINDS),"scopes":list(SCOPES),"claim_link_requires_reference":True,"inferred_claim_links":False}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["create-thread","annotate-active-path","annotate-edge","link-explicit-claim","switch-competing-path","verify-incremental-marking","open-review-context"],"full_render_count_must_not_increase":True}
def acceptance_report(): return {"ok":True,"version":VERSION,"review_thread":True,"path_annotations":True,"claim_linkage_explicit_only":True,"full_graph_redraw_for_annotation":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"scientific_preference":False}
