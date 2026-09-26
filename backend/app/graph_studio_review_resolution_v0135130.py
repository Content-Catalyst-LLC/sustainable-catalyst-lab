from __future__ import annotations
import hashlib, json

VERSION="0.135.13.0"
ROUTE_COUNT=11
DISPOSITIONS=("addressed","deferred","withdrawn","superseded")
ACTIONS=("none","revise-method","revise-data","revise-figure","add-evidence","clarify-claim","rerun-analysis","follow-up")
REVISION_REF_ACTIONS={"revise-method","revise-data","revise-figure","rerun-analysis"}


def _text(value, limit=12000):
    return str(value or "").strip()[:limit]


def normalize_resolution(raw:dict, index:int=0):
    if not isinstance(raw,dict): raise ValueError("resolution must be an object")
    disposition=_text(raw.get("disposition"),64)
    action=_text(raw.get("action"),64) or "none"
    annotation_id=_text(raw.get("annotationId",raw.get("annotation_id")),512)
    response=_text(raw.get("response"),12000)
    revision_ref=_text(raw.get("revisionRef",raw.get("revision_ref")),1024) or None
    if disposition not in DISPOSITIONS: raise ValueError(f"unsupported disposition: {disposition}")
    if action not in ACTIONS: raise ValueError(f"unsupported action: {action}")
    if not annotation_id: raise ValueError("annotationId is required")
    if not response: raise ValueError("response is required")
    if action in REVISION_REF_ACTIONS and not revision_ref: raise ValueError(f"{action} requires revisionRef")
    return {
        "id":_text(raw.get("id"),256) or f"resolution-{index+1}",
        "annotation_id":annotation_id,
        "disposition":disposition,
        "action":action,
        "response":response,
        "revision_ref":revision_ref,
        "created_at":_text(raw.get("createdAt",raw.get("created_at")),128) or None,
        "author":_text(raw.get("author"),256) or "user",
    }


def normalize_record(payload:dict):
    raw=payload.get("resolutionRecord") if isinstance(payload,dict) and isinstance(payload.get("resolutionRecord"),dict) else payload.get("record") if isinstance(payload,dict) and isinstance(payload.get("record"),dict) else payload
    if not isinstance(raw,dict): return {"ok":False,"version":VERSION,"error":"resolution record must be an object"}
    thread_id=_text(raw.get("threadId",raw.get("thread_id")),512)
    if not thread_id: return {"ok":False,"version":VERSION,"error":"threadId is required"}
    resolutions=[]
    try:
        for i,item in enumerate((raw.get("resolutions") or [])[:200]): resolutions.append(normalize_resolution(item,i))
    except ValueError as e:
        return {"ok":False,"version":VERSION,"error":str(e)}
    record={
        "schema":"sc-lab-graph-studio-review-resolution/0.135.13.0",
        "version":VERSION,
        "record_type":"graph-studio-review-resolution",
        "collection":"graphStudioReviewResolutions",
        "id":_text(raw.get("id"),256) or "provenance-review-resolution",
        "thread_id":thread_id,
        "thread_title":_text(raw.get("threadTitle",raw.get("thread_title")),1024) or "Provenance review thread",
        "comparison_signature":_text(raw.get("comparisonSignature",raw.get("comparison_signature")),2048) or None,
        "resolutions":resolutions,
        "created_at":_text(raw.get("createdAt",raw.get("created_at")),128) or None,
        "updated_at":_text(raw.get("updatedAt",raw.get("updated_at")),128) or None,
        "boundary":"Review dispositions, responses, and revision actions are explicit workflow records. No truth, causal validity, evidentiary weight, or scientific preference is inferred.",
    }
    return {"ok":True,"version":VERSION,"record":record,"resolution_event_count":len(resolutions)}


def _annotation_ids(payload:dict):
    thread=payload.get("thread") if isinstance(payload,dict) and isinstance(payload.get("thread"),dict) else {}
    out=[]
    for a in (thread.get("annotations") or [])[:200]:
        if isinstance(a,dict):
            x=_text(a.get("id"),512)
            if x: out.append(x)
    return out


def latest_dispositions(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    latest={}
    for r in n["record"]["resolutions"]: latest[r["annotation_id"]]=r
    return latest


def summarize(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    latest={}
    for r in n["record"]["resolutions"]: latest[r["annotation_id"]]=r
    by_disposition={k:0 for k in DISPOSITIONS}; by_action={k:0 for k in ACTIONS}
    for r in latest.values():
        by_disposition[r["disposition"]]+=1; by_action[r["action"]]+=1
    ids=_annotation_ids(payload)
    return {"ok":True,"version":VERSION,"resolution_event_count":len(n["record"]["resolutions"]),"latest_disposition_count":len(latest),"annotation_count":len(ids),"pending_count":sum(1 for x in ids if x not in latest),"by_disposition":by_disposition,"by_action":by_action}


def pending(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    latest=latest_dispositions(payload); ids=_annotation_ids(payload)
    pending_ids=[x for x in ids if x not in latest]
    return {"ok":True,"version":VERSION,"pending_annotation_ids":pending_ids,"pending_count":len(pending_ids),"term":"pending means no explicit disposition event has been recorded"}


def revision_actions(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    actions=[r for r in n["record"]["resolutions"] if r["action"]!="none"]
    return {"ok":True,"version":VERSION,"actions":actions,"action_count":len(actions),"explicit_only":True}


def decision_lineage(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    grouped={}
    for i,r in enumerate(n["record"]["resolutions"],1): grouped.setdefault(r["annotation_id"],[]).append({**r,"event_index":i})
    return {"ok":True,"version":VERSION,"by_annotation":grouped,"annotation_lineage_count":len(grouped),"append_only":True}


def resolution_packet(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    return {"ok":True,"version":VERSION,"target":"project-workspace","record":n["record"],"summary":summarize(payload),"pending":pending(payload),"revision_actions":revision_actions(payload)["actions"],"decision_lineage":decision_lineage(payload)["by_annotation"],"boundary":n["record"]["boundary"]}


def fingerprint(payload:dict):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    canonical=json.dumps(n["record"],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return {"ok":True,"version":VERSION,"algorithm":"sha256","fingerprint":hashlib.sha256(canonical).hexdigest(),"canonical_bytes":len(canonical)}


def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"review_resolution":True,"append_only_decision_lineage":True,"revision_actions_explicit":True,"project_persistence_explicit":True,"cross_workspace_resolution_handoff":True}
def contract(): return {"ok":True,"version":VERSION,"dispositions":list(DISPOSITIONS),"actions":list(ACTIONS),"revision_ref_required_for":sorted(REVISION_REF_ACTIONS),"max_resolution_events":200,"project_collection":"graphStudioReviewResolutions","annotation_mutation":False}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["create-review-annotation","record-disposition","record-revision-action","verify-annotation-status-mark","save-resolution-record","open-resolution-context"],"full_render_count_must_not_increase":True}
def acceptance_report(): return {"ok":True,"version":VERSION,"review_resolution":True,"append_only_decision_lineage":True,"revision_actions_explicit":True,"full_graph_redraw_for_resolution":False,"annotation_mutation":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"scientific_preference":False}
