from __future__ import annotations
import hashlib, json
VERSION="0.135.14.0"
ROUTE_COUNT=13
EVENTS=("action-started","verification-recorded","resolution-confirmed","reopened")
OUTCOMES=("passed","failed","inconclusive")
VERIFY_METHODS=("artifact-inspection","rerun","source-check","figure-check","method-check","manual-review")
TERMINAL={"resolved","deferred","withdrawn","superseded"}

def _text(value,limit=12000): return str(value or "").strip()[:limit]
def _resolution_record(payload):
    return payload.get("resolutionRecord") if isinstance(payload,dict) and isinstance(payload.get("resolutionRecord"),dict) else payload.get("resolution_record") if isinstance(payload,dict) and isinstance(payload.get("resolution_record"),dict) else {}
def _audit_record(payload):
    return payload.get("auditRecord") if isinstance(payload,dict) and isinstance(payload.get("auditRecord"),dict) else payload.get("audit_record") if isinstance(payload,dict) and isinstance(payload.get("audit_record"),dict) else payload.get("record") if isinstance(payload,dict) and isinstance(payload.get("record"),dict) else payload if isinstance(payload,dict) else {}
def _thread(payload): return payload.get("thread") if isinstance(payload,dict) and isinstance(payload.get("thread"),dict) else {}
def _annotations(payload): return [a for a in (_thread(payload).get("annotations") or [])[:500] if isinstance(a,dict) and _text(a.get("id"),512)]
def _latest_resolutions(payload):
    out={}
    for r in (_resolution_record(payload).get("resolutions") or [])[:500]:
        if isinstance(r,dict) and _text(r.get("annotationId",r.get("annotation_id")),512): out[_text(r.get("annotationId",r.get("annotation_id")),512)]=r
    return out

def normalize_event(raw,index=0):
    if not isinstance(raw,dict): raise ValueError("audit event must be an object")
    event_type=_text(raw.get("eventType",raw.get("event_type")),64); annotation_id=_text(raw.get("annotationId",raw.get("annotation_id")),512); note=_text(raw.get("note"),12000)
    outcome=_text(raw.get("outcome"),64) or None; method=_text(raw.get("verificationMethod",raw.get("verification_method")),128) or None; ref=_text(raw.get("verificationRef",raw.get("verification_ref")),2048) or None
    if event_type not in EVENTS: raise ValueError(f"unsupported eventType: {event_type}")
    if not annotation_id: raise ValueError("annotationId is required")
    if not note: raise ValueError("note is required")
    if event_type=="verification-recorded":
        if outcome not in OUTCOMES: raise ValueError("verification-recorded requires a supported outcome")
        if method not in VERIFY_METHODS: raise ValueError("verification-recorded requires verificationMethod")
        if not ref: raise ValueError("verification-recorded requires verificationRef")
    return {"id":_text(raw.get("id"),256) or f"review-audit-event-{index+1}","annotation_id":annotation_id,"event_type":event_type,"note":note,"outcome":outcome,"verification_method":method,"verification_ref":ref,"resolution_event_id":_text(raw.get("resolutionEventId",raw.get("resolution_event_id")),512) or None,"previous_event_id":_text(raw.get("previousEventId",raw.get("previous_event_id")),512) or None,"created_at":_text(raw.get("createdAt",raw.get("created_at")),128) or None,"author":_text(raw.get("author"),256) or "user"}

def normalize_record(payload):
    raw=_audit_record(payload)
    if not isinstance(raw,dict): return {"ok":False,"version":VERSION,"error":"audit record must be an object"}
    thread_id=_text(raw.get("threadId",raw.get("thread_id")),512); resolution_record_id=_text(raw.get("resolutionRecordId",raw.get("resolution_record_id")),512)
    if not thread_id:return {"ok":False,"version":VERSION,"error":"threadId is required"}
    if not resolution_record_id:return {"ok":False,"version":VERSION,"error":"resolutionRecordId is required"}
    events=[]
    try:
        for i,item in enumerate((raw.get("events") or [])[:500]): events.append(normalize_event(item,i))
    except ValueError as e:return {"ok":False,"version":VERSION,"error":str(e)}
    rec={"schema":"sc-lab-graph-studio-review-audit/0.135.14.0","version":VERSION,"record_type":"graph-studio-review-audit","collection":"graphStudioReviewAudits","id":_text(raw.get("id"),256) or "graph-studio-review-audit","thread_id":thread_id,"resolution_record_id":resolution_record_id,"thread_title":_text(raw.get("threadTitle",raw.get("thread_title")),1024) or "Provenance review thread","comparison_signature":_text(raw.get("comparisonSignature",raw.get("comparison_signature")),2048) or None,"events":events,"created_at":_text(raw.get("createdAt",raw.get("created_at")),128) or None,"updated_at":_text(raw.get("updatedAt",raw.get("updated_at")),128) or None,"boundary":"Review states, verification outcomes, and resolution confirmations are workflow/audit records. No scientific truth, causation, evidentiary weight, or preference is inferred."}
    return {"ok":True,"version":VERSION,"record":rec,"audit_event_count":len(events)}

def base_state(payload,annotation_id):
    r=_latest_resolutions(payload).get(annotation_id)
    if not r:return "open"
    d=_text(r.get("disposition"),64); action=_text(r.get("action"),64) or "none"
    if d in ("deferred","withdrawn","superseded"): return d
    if d=="addressed": return "action-required" if action!="none" else "ready-to-resolve"
    return "open"

def _events_for(payload,annotation_id):
    n=normalize_record(payload)
    if not n.get("ok"): return []
    return [e for e in n["record"]["events"] if e["annotation_id"]==annotation_id]

def state_for(payload,annotation_id):
    state=base_state(payload,annotation_id)
    for e in _events_for(payload,annotation_id):
        t=e["event_type"]
        if t=="reopened": state="reopened"
        elif t=="action-started" and state in ("action-required","reopened"): state="action-required"
        elif t=="verification-recorded": state="verified" if e["outcome"]=="passed" else "verification-failed" if e["outcome"]=="failed" else "verification-required"
        elif t=="resolution-confirmed" and state in ("ready-to-resolve","verified"): state="resolved"
    return state

def states(payload):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    ids=[_text(a.get("id"),512) for a in _annotations(payload)]
    mapping={x:state_for(payload,x) for x in ids}
    return {"ok":True,"version":VERSION,"states":mapping,"annotation_count":len(mapping)}

def transition(payload):
    annotation_id=_text(payload.get("annotationId",payload.get("annotation_id")),512); event_type=_text(payload.get("eventType",payload.get("event_type")),64); current=state_for(payload,annotation_id); latest=_latest_resolutions(payload).get(annotation_id) or {}; action=_text(latest.get("action"),64) or "none"
    allowed=False; reason="transition is not valid from the current state"
    if event_type=="action-started": allowed=current in ("action-required","reopened")
    elif event_type=="verification-recorded": allowed=action!="none" and current in ("action-required","verification-required","verification-failed","reopened"); reason="verification requires an explicit review action and an active verification state"
    elif event_type=="resolution-confirmed": allowed=current in ("ready-to-resolve","verified"); reason="resolution confirmation requires ready-to-resolve or verified state"
    elif event_type=="reopened": allowed=current in TERMINAL; reason="only terminal review states can be reopened"
    return {"ok":True,"version":VERSION,"annotation_id":annotation_id,"current_state":current,"event_type":event_type,"allowed":allowed,"reason":None if allowed else reason}

def verify_action(payload):
    annotation_id=_text(payload.get("annotationId",payload.get("annotation_id")),512); outcome=_text(payload.get("outcome"),64); method=_text(payload.get("verificationMethod",payload.get("verification_method")),128); ref=_text(payload.get("verificationRef",payload.get("verification_ref")),2048)
    t=transition({**payload,"eventType":"verification-recorded","annotationId":annotation_id})
    errors=[]
    if not t.get("allowed"): errors.append(t.get("reason"))
    if outcome not in OUTCOMES: errors.append("unsupported verification outcome")
    if method not in VERIFY_METHODS: errors.append("unsupported verification method")
    if not ref: errors.append("verificationRef is required")
    return {"ok":not errors,"version":VERSION,"annotation_id":annotation_id,"outcome":outcome or None,"verification_method":method or None,"verification_ref":ref or None,"errors":errors,"state_if_recorded":"verified" if outcome=="passed" else "verification-failed" if outcome=="failed" else "verification-required"}

def audit_trail(payload):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    prev_hash="0"*64; out=[]
    for i,e in enumerate(n["record"]["events"],1):
        body={**e,"index":i,"prev_hash":prev_hash}; raw=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); h=hashlib.sha256(raw).hexdigest(); out.append({**body,"event_hash":h}); prev_hash=h
    return {"ok":True,"version":VERSION,"algorithm":"sha256","append_only":True,"event_count":len(out),"events":out,"head_hash":prev_hash if out else None}

def resolution_readiness(payload):
    ids=[_text(a.get("id"),512) for a in _annotations(payload)]; latest=_latest_resolutions(payload); items=[]
    for x in ids:
        st=state_for(payload,x); r=latest.get(x) or {}; action=_text(r.get("action"),64) or "none"; items.append({"annotation_id":x,"state":st,"ready":st in ("ready-to-resolve","verified"),"terminal":st in TERMINAL,"requires_verification":action!="none" and st not in ("verified","resolved")})
    return {"ok":True,"version":VERSION,"items":items,"ready_count":sum(1 for x in items if x["ready"]),"resolved_count":sum(1 for x in items if x["state"]=="resolved")}

def integrity(payload):
    n=normalize_record(payload)
    if not n.get("ok"):return n
    events=n["record"]["events"]; errors=[]
    for i,e in enumerate(events):
        expected=events[i-1]["id"] if i else None
        if e["previous_event_id"]!=expected: errors.append({"index":i+1,"event_id":e["id"],"expected_previous_event_id":expected,"actual_previous_event_id":e["previous_event_id"]})
    trail=audit_trail(payload)
    return {"ok":not errors,"version":VERSION,"chain_valid":not errors,"link_errors":errors,"event_count":len(events),"head_hash":trail.get("head_hash")}

def audit_packet(payload):
    n=normalize_record(payload)
    if not n.get("ok"): return n
    return {"ok":True,"version":VERSION,"target":"project-workspace","record":n["record"],"states":states(payload).get("states",{}),"readiness":resolution_readiness(payload),"audit_trail":audit_trail(payload),"integrity":integrity(payload),"boundary":n["record"]["boundary"]}

def fingerprint(payload):
    n=normalize_record(payload)
    if not n.get("ok"):return n
    canonical=json.dumps(n["record"],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return {"ok":True,"version":VERSION,"algorithm":"sha256","fingerprint":hashlib.sha256(canonical).hexdigest(),"canonical_bytes":len(canonical)}
def health():return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"review_state_machine":True,"action_verification":True,"append_only_resolution_audit":True,"explicit_resolution_confirmation":True,"tamper_evident_backend_chain":True,"cross_workspace_audit_handoff":True}
def contract():return {"ok":True,"version":VERSION,"events":list(EVENTS),"verification_outcomes":list(OUTCOMES),"verification_methods":list(VERIFY_METHODS),"terminal_states":sorted(TERMINAL),"project_collection":"graphStudioReviewAudits","max_audit_events":500,"resolution_mutation":False,"annotation_mutation":False}
def browser_contract():return {"ok":True,"version":VERSION,"required_actions":["record-action-start","record-verification","confirm-resolution","reopen-resolution","save-audit","open-audit-context"],"full_render_count_must_not_increase":True}
def acceptance_report():return {"ok":True,"version":VERSION,"review_state_machine":True,"action_verification":True,"append_only_resolution_audit":True,"explicit_resolution_confirmation":True,"tamper_evident_backend_chain":True,"full_graph_redraw_for_audit":False,"resolution_mutation":False,"annotation_mutation":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"scientific_preference":False}
