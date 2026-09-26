from __future__ import annotations
import copy, hashlib, json, re
from datetime import datetime, timezone

VERSION = "0.135.19.0"
ROUTE_COUNT = 21
MAX_RECORDS = 5000
BOUNDARY = (
    "Cross-review synthesis summarizes declared review workflow records across a project. "
    "Counts, completion states, verification records, reproduction outcomes, dissent, and resolution history "
    "do not establish scientific truth, evidentiary weight, causal validity, consensus, or an automatic scientific resolution."
)
CLOSED_STATES = {"resolved", "closed", "complete", "completed", "archived"}


def _now(): return datetime.now(timezone.utc).isoformat()
def _text(value, limit=4096): return "" if value is None else str(value).strip()[:limit]
def _slug(value, fallback="record"):
    s=re.sub(r"[^a-zA-Z0-9._:-]+","-",_text(value,256)).strip("-")
    return s or fallback
def _fp(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
def _list(value): return copy.deepcopy(value[:MAX_RECORDS]) if isinstance(value,list) else []
def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default

def _thread_id(o): return _text(_get(o,"thread_id","threadId","id"),512)
def _resolution_thread_id(o): return _text(_get(o,"thread_id","threadId"),512)
def _panel_thread_id(o): return _text(_get(o,"thread_id","threadId"),512)
def _bridge_thread_id(o): return _text(_get(o,"thread_id","threadId"),512)
def _bundle_thread_id(o): return _text(_get(o,"thread_id","threadId"),512)
def _audit_thread_id(o): return _text(_get(o,"thread_id","threadId"),512)
def _impact_thread_id(o): return _text(_get(o,"thread_id","threadId"),512)
def _created(o): return _text(_get(o,"updated_at","updatedAt","created_at","createdAt"),128)
def _state(o): return _text(_get(o,"status","state","review_state","reviewState","resolution_status","resolutionStatus"),128).lower()
def _subject_refs(o):
    vals=_get(o,"subject_refs","subjectRefs",default=[])
    if not isinstance(vals,list): vals=[]
    out=[]
    for x in vals[:1000]:
        s=_text(x,2048)
        if s and s not in out: out.append(s)
    for k in ("objectA","objectB","seed_id","seedId"):
        v=_get(o,k)
        if isinstance(v,dict): v=_get(v,"id","objectId","ref")
        s=_text(v,2048)
        if s and s not in out: out.append(s)
    return out

def normalize_synthesis(payload):
    if not isinstance(payload,dict): return {"ok":False,"version":VERSION,"error":"payload must be an object"}
    raw=payload.get("synthesis") if isinstance(payload.get("synthesis"),dict) else payload
    project_id=_text(_get(raw,"projectId","project_id"),512) or "unbound-project"
    sid=_text(_get(raw,"id","synthesisId","synthesis_id"),512) or f"cross-review-{_slug(project_id)}"
    rec={
        "schema":"sc-lab-cross-review-synthesis/0.135.19.0","version":VERSION,"record_type":"cross-review-synthesis",
        "collection":"graphStudioCrossReviewSyntheses","id":sid,"project_id":project_id,
        "project_version_ref":_text(_get(raw,"projectVersionRef","project_version_ref"),2048) or None,
        "review_threads":_list(_get(raw,"reviewThreads","review_threads",default=[])),
        "resolution_records":_list(_get(raw,"resolutionRecords","resolution_records",default=[])),
        "reviewer_panels":_list(_get(raw,"reviewerPanels","reviewer_panels",default=[])),
        "verification_bundles":_list(_get(raw,"verificationBundles","verification_bundles",default=[])),
        "reproduction_bridges":_list(_get(raw,"reproductionBridges","reproduction_bridges",default=[])),
        "impact_analyses":_list(_get(raw,"impactAnalyses","impact_analyses",default=[])),
        "audit_records":_list(_get(raw,"auditRecords","audit_records",default=[])),
        "created_at":_text(_get(raw,"createdAt","created_at"),128) or _now(),
        "author":_text(_get(raw,"author"),256) or "user","boundary":BOUNDARY,
    }
    rec["fingerprint"]=_fp(rec)
    return {"ok":True,"version":VERSION,"record":rec}

def validate_synthesis(payload):
    n=normalize_synthesis(payload)
    if not n.get("record"): return n
    r=n["record"]; errors=[]
    if not r["project_id"]: errors.append("projectId is required")
    ids=[]
    for t in r["review_threads"]:
        tid=_thread_id(t)
        if not tid: errors.append("review thread without id")
        elif tid in ids: errors.append(f"duplicate review thread id: {tid}")
        else: ids.append(tid)
    return {"ok":not errors,"version":VERSION,"record":r,"errors":errors,"boundary":BOUNDARY}

def _latest(items):
    if not items: return None
    return sorted(items,key=lambda x:(_created(x),_text(_get(x,"id"),512)))[-1]

def _panel_stats(panels):
    reviewers=assessments=signoffs=dissents=0; admin_complete=True if panels else False
    for p in panels:
        rs=_get(p,"reviewers",default=[]) or []; aa=_get(p,"assessments",default=[]) or []; ss=_get(p,"signoffs",default=[]) or []; dd=_get(p,"dissents",default=[]) or []
        reviewers+=len(rs); assessments+=len(aa); signoffs+=len(ss); dissents+=len(dd)
        ids=[_text(_get(x,"reviewer_id","reviewerId","id"),256) for x in rs]
        for rid in ids:
            has_a=any(_text(_get(x,"reviewer_id","reviewerId"),256)==rid for x in aa)
            has_s=any(_text(_get(x,"reviewer_id","reviewerId"),256)==rid for x in ss)
            if not (has_a and has_s): admin_complete=False
        if len(ids)<2: admin_complete=False
    return reviewers,assessments,signoffs,dissents,admin_complete

def _resolution_actions(records):
    actions=[]
    for rr in records:
        vals=_get(rr,"resolutions",default=[])
        if isinstance(vals,list): actions.extend([x for x in vals if isinstance(x,dict)])
    open_actions=[]
    for a in actions:
        st=_state(a)
        if st not in CLOSED_STATES: open_actions.append(a)
    return actions,open_actions

def resolution_matrix(payload):
    n=normalize_synthesis(payload)
    if not n.get("record"): return n
    s=n["record"]; tids=[]
    for t in s["review_threads"]:
        tid=_thread_id(t)
        if tid and tid not in tids: tids.append(tid)
    for collection,fn in ((s["resolution_records"],_resolution_thread_id),(s["reviewer_panels"],_panel_thread_id),(s["verification_bundles"],_bundle_thread_id),(s["reproduction_bridges"],_bridge_thread_id),(s["audit_records"],_audit_thread_id),(s["impact_analyses"],_impact_thread_id)):
        for x in collection:
            tid=fn(x)
            if tid and tid not in tids: tids.append(tid)
    rows=[]
    for tid in sorted(tids):
        threads=[x for x in s["review_threads"] if _thread_id(x)==tid]; t=_latest(threads) or {"id":tid}
        resolutions=[x for x in s["resolution_records"] if _resolution_thread_id(x)==tid]
        panels=[x for x in s["reviewer_panels"] if _panel_thread_id(x)==tid]
        bundles=[x for x in s["verification_bundles"] if _bundle_thread_id(x)==tid]
        bridges=[x for x in s["reproduction_bridges"] if _bridge_thread_id(x)==tid]
        impacts=[x for x in s["impact_analyses"] if _impact_thread_id(x)==tid]
        audits=[x for x in s["audit_records"] if _audit_thread_id(x)==tid]
        actions,open_actions=_resolution_actions(resolutions)
        reviewers,assessments,signoffs,dissents,admin_complete=_panel_stats(panels)
        state=_state(t) or _state(_latest(resolutions) or {}) or "unspecified"
        recorded_closed=state in CLOSED_STATES
        refs=[]
        for obj in threads+resolutions+panels:
            for ref in _subject_refs(obj):
                if ref not in refs: refs.append(ref)
        verification_states=[_text(_get(b,"verification_outcome","verificationOutcome","status","state"),64) for b in bundles]
        reproduction_states=[_text(_get(b,"status","state","execution_state","executionState","verification_outcome","verificationOutcome"),64) for b in bridges]
        latest_dates=[_created(x) for x in threads+resolutions+panels+bundles+bridges+impacts+audits if _created(x)]
        row={"thread_id":tid,"title":_text(_get(t,"title"),1024) or tid,"recorded_state":state,"recorded_closed":recorded_closed,
             "subject_refs":refs,"resolution_record_count":len(resolutions),"resolution_action_count":len(actions),"open_action_count":len(open_actions),
             "reviewer_panel_count":len(panels),"reviewer_count":reviewers,"assessment_count":assessments,"signoff_count":signoffs,"dissent_count":dissents,
             "panel_administratively_complete":admin_complete,"verification_bundle_count":len(bundles),"verification_states":[x for x in verification_states if x],
             "reproduction_bridge_count":len(bridges),"reproduction_states":[x for x in reproduction_states if x],"impact_analysis_count":len(impacts),
             "audit_record_count":len(audits),"latest_activity_at":max(latest_dates) if latest_dates else None,
             "administratively_open":(not recorded_closed) or bool(open_actions),"scientifically_resolved":None,"automatic_resolution":False}
        row["fingerprint"]=_fp(row); rows.append(row)
    return {"ok":True,"version":VERSION,"project_id":s["project_id"],"rows":rows,"row_count":len(rows),"consensus_score":None,"winner":None,"truth_ranking":False,"boundary":BOUNDARY}

def synthesize(payload):
    n=validate_synthesis(payload)
    if not n.get("ok"): return n
    s=n["record"]; m=resolution_matrix({"synthesis":s}); dg=disagreement_register({"synthesis":s}); oi=open_items({"synthesis":s})
    out={"schema":"sc-lab-cross-review-synthesis-result/0.135.19.0","version":VERSION,"synthesis_id":s["id"],"project_id":s["project_id"],
         "matrix":m["rows"],"open_items":oi["items"],"disagreements":dg["items"],"summary":{"review_thread_count":len(m["rows"]),"administratively_open_count":len(oi["items"]),"dissent_record_count":len(dg["items"])},
         "automatic_scientific_resolution":False,"consensus_inferred":False,"boundary":BOUNDARY}
    out["fingerprint"]=_fp(out); return {"ok":True,"version":VERSION,"result":out}

def open_items(payload):
    m=resolution_matrix(payload)
    if not m.get("ok"): return m
    items=[r for r in m["rows"] if r["administratively_open"]]
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"priority_ranking":False,"scientific_severity_scoring":False,"boundary":BOUNDARY}

def disagreement_register(payload):
    n=normalize_synthesis(payload)
    if not n.get("record"): return n
    items=[]
    for p in n["record"]["reviewer_panels"]:
        tid=_panel_thread_id(p); pid=_text(_get(p,"id"),512)
        for d in (_get(p,"dissents",default=[]) or []):
            if not isinstance(d,dict): continue
            items.append({"thread_id":tid or None,"panel_id":pid or None,"dissent_id":_text(_get(d,"id"),512) or None,"reviewer_id":_text(_get(d,"reviewer_id","reviewerId"),256) or None,
                          "dissent_kind":_text(_get(d,"dissent_kind","dissentKind"),128) or "other","statement":_text(_get(d,"statement"),16000),
                          "alternative_interpretation":_text(_get(d,"alternative_interpretation","alternativeInterpretation"),16000) or None,
                          "evidence_refs":_get(d,"evidence_refs","evidenceRefs",default=[]) or [],"created_at":_created(d) or None})
    items=sorted(items,key=lambda x:(x["thread_id"] or "",x["created_at"] or "",x["dissent_id"] or ""))
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"minority_views_preserved":True,"consensus_inferred":False,"boundary":BOUNDARY}

def verification_matrix(payload):
    n=normalize_synthesis(payload); s=n.get("record")
    if not s:return n
    items=[]
    for b in s["verification_bundles"]:
        items.append({"thread_id":_bundle_thread_id(b) or None,"bundle_id":_text(_get(b,"id"),512) or None,"verification_event_id":_text(_get(b,"verification_event_id","verificationEventId"),512) or None,
                      "recorded_outcome":_text(_get(b,"verification_outcome","verificationOutcome","status","state"),128) or None,"artifact_count":len(_get(b,"artifacts",default=[]) or []),"created_at":_created(b) or None})
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"outcome_is_workflow_record_not_truth":True,"boundary":BOUNDARY}

def reproduction_matrix(payload):
    n=normalize_synthesis(payload); s=n.get("record")
    if not s:return n
    items=[]
    for b in s["reproduction_bridges"]:
        items.append({"thread_id":_bridge_thread_id(b) or None,"bridge_id":_text(_get(b,"id"),512) or None,"revision_action":_text(_get(b,"revision_action","revisionAction"),128) or None,
                      "revision_impact_ref":_text(_get(b,"revision_impact_ref","revisionImpactRef"),512) or None,"recorded_state":_state(b) or None,"created_at":_created(b) or None})
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"reproduction_does_not_confirm_claims":True,"boundary":BOUNDARY}

def revision_impact_matrix(payload):
    n=normalize_synthesis(payload); s=n.get("record")
    if not s:return n
    items=[]
    for a in s["impact_analyses"]:
        affected=_get(a,"potentially_affected_node_ids","potentiallyAffectedNodeIds",default=[]) or []
        deps=_get(a,"dependency_node_ids","dependencyNodeIds",default=[]) or []
        items.append({"thread_id":_impact_thread_id(a) or None,"analysis_id":_text(_get(a,"id"),512) or None,"revision_action":_text(_get(a,"revision_action","revisionAction"),128) or None,
                      "seed_id":_text(_get(a,"seed_id","seedId"),512) or None,"potentially_affected_count":len(affected),"dependency_count":len(deps),"created_at":_created(a) or None})
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"impact_is_declared_dependency_not_invalidation":True,"boundary":BOUNDARY}

def resolution_history(payload):
    n=normalize_synthesis(payload); s=n.get("record")
    if not s:return n
    items=[]
    for rr in s["resolution_records"]:
        tid=_resolution_thread_id(rr); rid=_text(_get(rr,"id"),512)
        for x in (_get(rr,"resolutions",default=[]) or []):
            if isinstance(x,dict): items.append({"thread_id":tid or None,"resolution_record_id":rid or None,"event_type":"resolution-record","recorded_state":_state(x) or None,"record_ref":_text(_get(x,"id"),512) or None,"at":_created(x) or _created(rr) or None})
    for ar in s["audit_records"]:
        tid=_audit_thread_id(ar); aid=_text(_get(ar,"id"),512)
        for e in (_get(ar,"events",default=[]) or []):
            if isinstance(e,dict): items.append({"thread_id":tid or None,"audit_record_id":aid or None,"event_type":_text(_get(e,"event_type","eventType"),128) or "audit-event","recorded_state":_state(e) or None,"record_ref":_text(_get(e,"id","recordRef","record_ref"),512) or None,"at":_created(e) or _created(ar) or None})
    items=sorted(items,key=lambda x:(x["at"] or "",x["thread_id"] or "",x["event_type"]))
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"append_history_preserved":True,"boundary":BOUNDARY}

def subject_index(payload):
    m=resolution_matrix(payload)
    if not m.get("ok"): return m
    idx={}
    for r in m["rows"]:
        for ref in r["subject_refs"]: idx.setdefault(ref,[]).append(r["thread_id"])
    items=[{"subject_ref":k,"thread_ids":sorted(set(v)),"review_count":len(set(v))} for k,v in sorted(idx.items())]
    return {"ok":True,"version":VERSION,"items":items,"count":len(items),"subject_importance_ranking":False,"boundary":BOUNDARY}

def filter_matrix(payload):
    m=resolution_matrix(payload)
    if not m.get("ok"): return m
    rows=m["rows"]
    if payload.get("openOnly",payload.get("open_only",False)): rows=[r for r in rows if r["administratively_open"]]
    if payload.get("dissentOnly",payload.get("dissent_only",False)): rows=[r for r in rows if r["dissent_count"]>0]
    q=_text(payload.get("query"),256).lower()
    if q: rows=[r for r in rows if q in json.dumps(r,ensure_ascii=False).lower()]
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"ranking_applied":False,"boundary":BOUNDARY}

def snapshot(payload):
    syn=synthesize(payload)
    if not syn.get("ok"): return syn
    r=syn["result"]
    snap={"schema":"sc-lab-cross-review-snapshot/0.135.19.0","version":VERSION,"id":_text(payload.get("snapshotId",payload.get("snapshot_id")),512) or f"cross-review-snapshot-{_slug(r['project_id'])}",
          "project_id":r["project_id"],"captured_at":_text(payload.get("capturedAt",payload.get("captured_at")),128) or _now(),"matrix":r["matrix"],"open_items":r["open_items"],"disagreements":r["disagreements"],"boundary":BOUNDARY}
    snap["fingerprint"]=_fp(snap);return {"ok":True,"version":VERSION,"snapshot":snap}

def compare_snapshots(payload):
    a=payload.get("before") or {}; b=payload.get("after") or {}
    ar={x.get("thread_id"):x for x in (a.get("matrix") or []) if isinstance(x,dict) and x.get("thread_id")}; br={x.get("thread_id"):x for x in (b.get("matrix") or []) if isinstance(x,dict) and x.get("thread_id")}
    ids=sorted(set(ar)|set(br)); changed=[i for i in ids if _fp(ar.get(i))!=_fp(br.get(i))]
    return {"ok":True,"version":VERSION,"added_thread_ids":[i for i in ids if i not in ar],"removed_thread_ids":[i for i in ids if i not in br],"changed_thread_ids":changed,
            "before_open_count":len(a.get("open_items") or []),"after_open_count":len(b.get("open_items") or []),"scientific_improvement_inferred":False,"boundary":BOUNDARY}

def project_workspace_packet(payload):
    syn=synthesize(payload)
    if not syn.get("ok"):return syn
    r=syn["result"]; packet={"schema":"sc-lab-cross-review-workspace-packet/0.135.19.0","version":VERSION,"result":r,"resolution_history":resolution_history(payload)["items"],
                             "verification_matrix":verification_matrix(payload)["items"],"reproduction_matrix":reproduction_matrix(payload)["items"],"revision_impact_matrix":revision_impact_matrix(payload)["items"],
                             "truth_ranking":False,"consensus_score":None,"automatic_resolution":False,"boundary":BOUNDARY};packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"packet":packet}

def audit_event_draft(payload):
    n=normalize_synthesis(payload)
    if not n.get("record"):return n
    s=n["record"]
    return {"ok":True,"version":VERSION,"event":{"eventType":"cross-review-synthesis-snapshot","synthesisId":s["id"],"projectId":s["project_id"],"recordRef":_text(payload.get("recordRef",payload.get("record_ref")),512) or None,"note":_text(payload.get("note"),8000) or None},
            "append_only_target":"graphStudioReviewAudits","automatic_append":False,"automatic_resolution":False,"boundary":BOUNDARY}

def status(payload):
    syn=synthesize(payload)
    if not syn.get("ok"):return syn
    r=syn["result"]
    return {"ok":True,"version":VERSION,"project_id":r["project_id"],"review_thread_count":r["summary"]["review_thread_count"],"administratively_open_count":r["summary"]["administratively_open_count"],
            "dissent_record_count":r["summary"]["dissent_record_count"],"scientific_consensus_inferred":False,"automatic_resolution":False,"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"cross_review_synthesis":True,"resolution_matrix":True,"dissent_preserved":True,"project_workspace_handoff":True,"backward_compatible_v0135180":True}
def contract():
    return {"ok":True,"version":VERSION,"project_collection":"graphStudioCrossReviewSyntheses","source_collections":["graphStudioReviewThreads","graphStudioReviewResolutions","graphStudioReviewAudits","graphStudioVerificationArtifactBundles","graphStudioRevisionImpactAnalyses","graphStudioReviewReproductionBridges","graphStudioMultiReviewerPanels"],
            "majority_voting":False,"consensus_scoring":False,"reviewer_ranking":False,"automatic_resolution":False,"truth_ranking":False,"scientific_severity_scoring":False}
def browser_contract():
    return {"ok":True,"version":VERSION,"required_actions":["synthesize-project","filter-open-items","show-disagreement-register","snapshot-synthesis","open-project-context"],"full_graph_redraw_for_synthesis":False,"matrix_must_not_rank_reviewers":True}
def acceptance_report():
    return {"ok":True,"version":VERSION,"cross_review_synthesis":True,"project_resolution_matrix":True,"open_item_register":True,"dissent_register":True,"verification_matrix":True,"reproduction_matrix":True,"revision_impact_matrix":True,"resolution_history":True,"snapshot_comparison":True,"project_workspace_handoff":True,
            "full_graph_redraw_for_synthesis":False,"majority_voting":False,"consensus_scoring":False,"reviewer_ranking":False,"automatic_resolution":False,"automatic_scientific_validity":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"scientific_preference":False}
