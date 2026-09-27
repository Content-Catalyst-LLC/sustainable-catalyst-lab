
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from . import graph_studio_revision_impact_v0135160 as impact
from . import graph_studio_integrated_scientific_review_reproducibility_v01360 as integrated

VERSION = "0.137.0"
ROUTE_COUNT = 20
BOUNDARY = (
    "Living analysis follows declared dependencies and records potentially affected research objects. "
    "It does not automatically invalidate science, establish causation, determine truth, rank evidence, "
    "or decide whether rerun or re-review is scientifically sufficient."
)
CHANGE_TYPES = ("dataset","method","code","model","evidence","assumption","execution","figure","finding","claim","source","other")

def _now(): return datetime.now(timezone.utc).isoformat()
def _fp(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def _txt(x,n=2048): return str(x or "").strip()[:n]

def normalize_change_event(payload):
    raw = payload.get("changeEvent", payload) if isinstance(payload, dict) else {}
    oid = _txt(raw.get("objectId") or raw.get("object_id"), 512)
    typ = _txt(raw.get("objectType") or raw.get("object_type") or "other", 128).lower()
    if not oid: return {"ok":False,"version":VERSION,"error":"objectId is required","boundary":BOUNDARY}
    if typ not in CHANGE_TYPES: typ="other"
    rec={
        "schema":"sc-lab-research-change-event/0.137.0","version":VERSION,
        "recordType":"research-change-event","collection":"graphStudioResearchChangeEvents",
        "id":_txt(raw.get("id"),512) or f"change-{oid}",
        "projectId":_txt(raw.get("projectId") or raw.get("project_id"),512) or "unbound-project",
        "objectId":oid,"objectType":typ,
        "beforeRef":_txt(raw.get("beforeRef") or raw.get("before_ref")) or None,
        "afterRef":_txt(raw.get("afterRef") or raw.get("after_ref")) or None,
        "changeSummary":_txt(raw.get("changeSummary") or raw.get("change_summary"),8000) or None,
        "changedAt":_txt(raw.get("changedAt") or raw.get("changed_at"),128) or _now(),
        "changedBy":_txt(raw.get("changedBy") or raw.get("changed_by"),256) or "user",
        "boundary":BOUNDARY,
    }
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"record":rec,"boundary":BOUNDARY}

def validate_change_event(payload):
    n=normalize_change_event(payload)
    if not n.get("ok"): return n
    warnings=[]
    if n["record"].get("beforeRef") and n["record"].get("beforeRef")==n["record"].get("afterRef"):
        warnings.append("beforeRef and afterRef are identical")
    return {**n,"warnings":warnings}

def _obligation(obj,event):
    typ=str(obj.get("type") or "").lower(); src=event["objectType"]
    actions=["re-review"]
    if any(x in typ for x in ("execution","model","simulation","analysis","figure","finding")) or src in ("dataset","method","code","model","assumption","execution"):
        actions.append("assess-rerun")
    return {
        "objectId":obj["id"],"objectType":obj.get("type"),"objectRef":obj.get("object_ref"),
        "hopCount":obj.get("hop_count"),"impactClass":obj.get("impact_class"),
        "status":"assessment-required","suggestedActions":sorted(set(actions)),
        "reason":"reachable through declared downstream dependency path",
        "scientificValidity":None,
    }

def analyze_change(payload):
    ev=normalize_change_event(payload)
    if not ev.get("ok"): return ev
    raw=dict(payload or {}); raw["seedId"]=ev["record"]["objectId"]
    trav=impact.downstream(raw)
    if not trav.get("ok"):
        return {"ok":False,"version":VERSION,"error":trav.get("error"),"changeEvent":ev["record"],"boundary":BOUNDARY}
    obligations=[_obligation(x,ev["record"]) for x in trav["affected"]]
    rec={
        "schema":"sc-lab-living-analysis-impact/0.137.0","version":VERSION,
        "recordType":"living-analysis-impact","collection":"graphStudioLivingAnalysisImpacts",
        "id":f"living-impact-{ev['record']['id']}","projectId":ev["record"]["projectId"],
        "changeEvent":ev["record"],"potentiallyAffected":trav["affected"],"affectedPaths":trav["paths"],
        "obligations":obligations,"declaredDependenciesOnly":True,"potentialImpactOnly":True,
        "automaticScientificInvalidation":False,"createdAt":_now(),"boundary":BOUNDARY,
    }
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"record":rec,"boundary":BOUNDARY}

def living_status(payload):
    payload=payload if isinstance(payload,dict) else {}
    events=payload.get("changeEvents") or payload.get("change_events") or []
    analyses=[]
    for event in events:
        q=dict(payload); q["changeEvent"]=event
        r=analyze_change(q)
        if r.get("ok"): analyses.append(r["record"])
    affected={o["objectId"]:o for a in analyses for o in a["obligations"]}
    items=sorted(affected.values(),key=lambda x:x["objectId"])
    return {
        "ok":True,"version":VERSION,"projectId":_txt(payload.get("projectId") or payload.get("project_id"),512) or "unbound-project",
        "changeEventCount":len(events),"analysisCount":len(analyses),"assessmentRequiredCount":len(items),
        "affectedObjects":items,"state":"attention-required" if items else "current-within-declared-change-log",
        "scientificValidity":None,"truthJudgment":None,"boundary":BOUNDARY,
    }

def obligation_register(payload):
    s=living_status(payload)
    return {"ok":True,"version":VERSION,"items":s["affectedObjects"],"count":s["assessmentRequiredCount"],"boundary":BOUNDARY}

def review_candidates(payload):
    o=obligation_register(payload); o["items"]=[x for x in o["items"] if "re-review" in x["suggestedActions"]]; o["count"]=len(o["items"]); return o

def rerun_candidates(payload):
    o=obligation_register(payload); o["items"]=[x for x in o["items"] if "assess-rerun" in x["suggestedActions"]]; o["count"]=len(o["items"]); return o

def acknowledge(payload):
    payload=payload if isinstance(payload,dict) else {}
    oid=_txt(payload.get("objectId"),512); action=_txt(payload.get("action"),128)
    if not oid or not action: return {"ok":False,"version":VERSION,"error":"objectId and action are required","boundary":BOUNDARY}
    rec={"schema":"sc-lab-living-analysis-acknowledgement/0.137.0","version":VERSION,"objectId":oid,"action":action,"note":_txt(payload.get("note"),8000) or None,"acknowledgedAt":_now(),"acknowledgedBy":_txt(payload.get("acknowledgedBy"),256) or "user","scientificJudgment":"human","boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"record":rec,"boundary":BOUNDARY}

def snapshot(payload):
    s=living_status(payload)
    snap={"schema":"sc-lab-living-analysis-snapshot/0.137.0","version":VERSION,"projectId":s["projectId"],"state":s["state"],"changeEventCount":s["changeEventCount"],"affectedObjects":s["affectedObjects"],"createdAt":_now(),"boundary":BOUNDARY}
    snap["fingerprint"]=_fp({k:v for k,v in snap.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}

def compare_snapshots(payload):
    payload=payload if isinstance(payload,dict) else {}; L=payload.get("left") or {}; R=payload.get("right") or {}
    li={x.get("objectId") for x in L.get("affectedObjects",[]) if isinstance(x,dict)}; ri={x.get("objectId") for x in R.get("affectedObjects",[]) if isinstance(x,dict)}
    return {"ok":True,"version":VERSION,"addedPotentiallyAffected":sorted(ri-li),"removedPotentiallyAffected":sorted(li-ri),"unchangedPotentiallyAffected":sorted(li&ri),"boundary":BOUNDARY}

def project_workspace_packet(payload):
    s=living_status(payload)
    packet={"schema":"sc-lab-project-workspace-living-analysis/0.137.0","version":VERSION,"projectId":s["projectId"],"livingAnalysis":s,"boundary":BOUNDARY}
    packet["packetFingerprint"]=_fp({k:v for k,v in packet.items() if k!="packetFingerprint"})
    return {"ok":True,"version":VERSION,"packet":packet,"boundary":BOUNDARY}

def integrated_status(payload):
    return {"ok":True,"version":VERSION,"integratedWorkspace":integrated.status(payload),"livingAnalysis":living_status(payload),"boundary":BOUNDARY}

def contract(): return {"ok":True,"version":VERSION,"route_count":ROUTE_COUNT,"changeTypes":list(CHANGE_TYPES),"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"declaredDependenciesOnly":True,"potentialImpactOnly":True,"humanResolutionRequired":True,"automaticScientificInvalidation":False,"automaticTruthJudgment":False,"automaticCausalInference":False,"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"research_change_impact":True,"living_analysis":True,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"researchChangeEvents":True,"downstreamChangeImpact":True,"livingAnalysisStatus":True,"reReviewObligations":True,"rerunAssessmentCandidates":True,"snapshots":True,"projectWorkspaceHandoff":True,"backwardCompatibleV01360":True,"automaticScientificInvalidation":False,"automaticTruthJudgment":False,"automaticCausalInference":False,"route_count":ROUTE_COUNT,"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"requiredRouteCount":ROUTE_COUNT,"researchChangeImpact":True,"livingAnalysis":True,"declaredDependenciesOnly":True,"automaticScientificInvalidation":False,"boundary":BOUNDARY}
