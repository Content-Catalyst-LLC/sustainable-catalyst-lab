from __future__ import annotations
import copy, hashlib, json
from . import research_reproduction_replication_studio_v01290 as rr
from . import graph_studio_revision_impact_v0135160 as impact135160
from . import graph_studio_verification_artifacts_v0135150 as verification135150

VERSION = "0.135.17.0"
ROUTE_COUNT = 18
REPRO_ACTIONS = ("rerun-analysis", "revise-method", "revise-data", "revise-figure", "manual-revision", "follow-up")
EXECUTION_STATES = ("planned", "submitted", "running", "completed", "failed", "cancelled")
BOUNDARY = (
    "The review-to-reproduction bridge records declared review intent, reproduction plans, externally supplied execution outcomes, "
    "and comparisons under user-declared tolerances. A completed rerun or numerical match does not establish scientific truth, "
    "causal validity, evidentiary weight, claim confirmation, or preferred interpretation."
)

def _text(v, limit=12000): return str(v or "").strip()[:limit]
def _fp(v): return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
def _raw(payload):
    if not isinstance(payload, dict): return {}
    for k in ("bridge", "request", "record"):
        if isinstance(payload.get(k), dict): return payload[k]
    return payload

def normalize_request(payload):
    raw=_raw(payload)
    if not isinstance(raw,dict): return {"ok":False,"version":VERSION,"error":"bridge request must be an object"}
    action=_text(raw.get("revisionAction",raw.get("revision_action")),64) or "rerun-analysis"
    if action not in REPRO_ACTIONS: return {"ok":False,"version":VERSION,"error":"revisionAction is not reproduction-bridge eligible"}
    rec={
      "schema":"sc-lab-review-to-reproduction-bridge/0.135.17.0","version":VERSION,
      "record_type":"review-to-reproduction-bridge","collection":"graphStudioReviewReproductionBridges",
      "id":_text(raw.get("id"),256) or "review-reproduction-bridge",
      "thread_id":_text(raw.get("threadId",raw.get("thread_id")),512),
      "resolution_record_id":_text(raw.get("resolutionRecordId",raw.get("resolution_record_id")),512),
      "audit_record_id":_text(raw.get("auditRecordId",raw.get("audit_record_id")),512),
      "annotation_id":_text(raw.get("annotationId",raw.get("annotation_id")),512),
      "revision_action":action,
      "revision_ref":_text(raw.get("revisionRef",raw.get("revision_ref")),2048) or None,
      "revision_impact_ref":_text(raw.get("revisionImpactRef",raw.get("revision_impact_ref")),2048) or None,
      "study_ref":_text(raw.get("studyRef",raw.get("study_ref")),2048) or "study:review-reproduction",
      "source_publication_ref":_text(raw.get("sourcePublicationRef",raw.get("source_publication_ref")),2048) or None,
      "original_execution_ref":_text(raw.get("originalExecutionRef",raw.get("original_execution_ref")),2048) or None,
      "environment_lock_ref":_text(raw.get("environmentLockRef",raw.get("environment_lock_ref")),2048) or None,
      "method_plan_ref":_text(raw.get("methodPlanRef",raw.get("method_plan_ref")),2048) or None,
      "input_artifacts":copy.deepcopy((raw.get("inputArtifacts",raw.get("input_artifacts")) or [])[:500]),
      "expected_output_refs":copy.deepcopy((raw.get("expectedOutputRefs",raw.get("expected_output_refs")) or [])[:500]),
      "claim_refs":copy.deepcopy((raw.get("claimRefs",raw.get("claim_refs")) or [])[:500]),
      "seed_policy":_text(raw.get("seedPolicy",raw.get("seed_policy")),128) or "declared-only",
      "absolute_tolerance":raw.get("absoluteTolerance",raw.get("absolute_tolerance",0.0)),
      "relative_tolerance":raw.get("relativeTolerance",raw.get("relative_tolerance",0.0)),
      "created_at":_text(raw.get("createdAt",raw.get("created_at")),128) or None,
      "author":_text(raw.get("author"),256) or "user",
      "boundary":BOUNDARY,
    }
    rec["fingerprint"]=_fp(rec)
    return {"ok":True,"version":VERSION,"record":rec}

def validate_request(payload):
    n=normalize_request(payload)
    if not n.get("ok"): return n
    r=n["record"]; errors=[]; warnings=[]
    for k in ("thread_id","resolution_record_id","audit_record_id","annotation_id"):
        if not r.get(k): errors.append(f"{k} is required")
    if r["revision_action"]=="rerun-analysis" and not (r.get("original_execution_ref") or r.get("method_plan_ref")):
        warnings.append("rerun-analysis has no originalExecutionRef or methodPlanRef; execution lineage will be incomplete until supplied")
    if not r["input_artifacts"]: warnings.append("no input artifacts declared")
    if not r["expected_output_refs"]: warnings.append("no expected output references declared")
    return {"ok":not errors,"version":VERSION,"errors":errors,"warnings":warnings,"record":r,"bridge_eligible":not errors}

def reproduction_study(payload):
    n=normalize_request(payload)
    if not n.get("ok"): return n
    r=n["record"]
    return rr.normalize_study({"mode":"reproduction","study_ref":r["study_ref"],"title":"Review-triggered reproduction",
      "source_publication_ref":r["source_publication_ref"],"original_execution_ref":r["original_execution_ref"],
      "claim_refs":r["claim_refs"],"artifact_refs":[_text(a.get("artifactRef",a.get("artifact_ref")),2048) for a in r["input_artifacts"] if isinstance(a,dict)],
      "provenance":{"bridge_ref":r["id"],"annotation_ref":r["annotation_id"],"revision_ref":r["revision_ref"],"revision_impact_ref":r["revision_impact_ref"]}})

def artifact_inventory(payload):
    n=normalize_request(payload)
    if not n.get("ok"): return n
    rows=[]
    for i,a in enumerate(n["record"]["input_artifacts"]):
        if not isinstance(a,dict): continue
        rows.append({"ref":a.get("artifactRef",a.get("artifact_ref")) or f"input:{i+1}","type":a.get("artifactType",a.get("artifact_type")) or "unspecified",
          "sha256":a.get("sha256"),"uri":a.get("uri"),"required":a.get("required",True),"available":a.get("available",False)})
    out=rr.artifact_inventory({"artifacts":rows}); out["bridge_ref"]=n["record"]["id"]; return out

def execution_plan(payload):
    n=normalize_request(payload)
    if not n.get("ok"): return n
    r=n["record"]
    plan=rr.execution_reproduction_plan({"study_ref":r["study_ref"],"environment_lock_ref":r["environment_lock_ref"],"method_plan_ref":r["method_plan_ref"],
      "input_refs":[_text(a.get("artifactRef",a.get("artifact_ref")),2048) for a in r["input_artifacts"] if isinstance(a,dict)],
      "expected_output_refs":r["expected_output_refs"],"seed_policy":r["seed_policy"]})
    plan["bridge_ref"]=r["id"]; plan["annotation_ref"]=r["annotation_id"]; plan["automatic_execution"]=False; return plan

def impact_scope(payload):
    if not isinstance(payload,dict): return {"ok":False,"version":VERSION,"error":"payload must be an object"}
    existing=payload.get("revisionImpactAnalysis") or payload.get("revision_impact_analysis")
    if isinstance(existing,dict):
        down=existing.get("downstream") or {}; up=existing.get("upstream") or {}
        return {"ok":True,"version":VERSION,"source":"supplied-v0.135.16.0-analysis","revision_impact_ref":existing.get("id"),
          "seed_id":existing.get("seedId",existing.get("seed_id")),"potentially_affected_node_ids":copy.deepcopy(existing.get("potentiallyAffectedNodeIds",existing.get("potentially_affected_node_ids")) or down.get("affected_node_ids") or []),
          "dependency_node_ids":copy.deepcopy(existing.get("dependencyNodeIds",existing.get("dependency_node_ids")) or up.get("affected_node_ids") or []),
          "potential_impact_only":True,"boundary":BOUNDARY}
    if isinstance(payload.get("graph"),dict) and (payload.get("seedId") or payload.get("seed_id")):
        p=dict(payload); p.setdefault("revisionAction",payload.get("revisionAction") or "rerun-analysis")
        a=impact135160.revision_analysis(p)
        if not a.get("ok"): return a
        rec=a["record"]
        return {"ok":True,"version":VERSION,"source":"computed-v0.135.16.0-analysis","revision_impact_ref":rec["id"],"seed_id":rec["seed_id"],
          "potentially_affected_node_ids":rec["downstream"]["affected_node_ids"],"dependency_node_ids":rec["upstream"]["affected_node_ids"],"potential_impact_only":True,"boundary":BOUNDARY}
    return {"ok":True,"version":VERSION,"source":"not-supplied","revision_impact_ref":None,"seed_id":None,"potentially_affected_node_ids":[],"dependency_node_ids":[],"potential_impact_only":True,"boundary":BOUNDARY}

def normalize_execution(payload):
    if not isinstance(payload,dict): return {"ok":False,"version":VERSION,"error":"payload must be an object"}
    raw=payload.get("execution") if isinstance(payload.get("execution"),dict) else payload
    state=_text(raw.get("state",raw.get("status")),64) or "completed"
    if state not in EXECUTION_STATES: return {"ok":False,"version":VERSION,"error":"unsupported execution state"}
    ref=_text(raw.get("executionRef",raw.get("execution_ref")),2048)
    if not ref: return {"ok":False,"version":VERSION,"error":"executionRef is required"}
    rec={"schema":"sc-lab-review-reproduction-execution/0.135.17.0","version":VERSION,"record_type":"review-reproduction-execution",
      "id":_text(raw.get("id"),256) or ref,"execution_ref":ref,"bridge_ref":_text(raw.get("bridgeRef",raw.get("bridge_ref")),2048) or None,
      "source_execution_ref":_text(raw.get("sourceExecutionRef",raw.get("source_execution_ref")),2048) or None,"state":state,
      "runtime":_text(raw.get("runtime"),256) or None,"runtime_version":_text(raw.get("runtimeVersion",raw.get("runtime_version")),256) or None,
      "environment_ref":_text(raw.get("environmentRef",raw.get("environment_ref")),2048) or None,"started_at":_text(raw.get("startedAt",raw.get("started_at")),128) or None,
      "finished_at":_text(raw.get("finishedAt",raw.get("finished_at")),128) or None,"output_artifacts":copy.deepcopy((raw.get("outputArtifacts",raw.get("output_artifacts")) or [])[:500]),
      "observed":copy.deepcopy((raw.get("observed") or [])[:1000]),"log_ref":_text(raw.get("logRef",raw.get("log_ref")),4096) or None,
      "operator_note":_text(raw.get("operatorNote",raw.get("operator_note")),12000) or None,"externally_supplied_result":True,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp(rec); return {"ok":True,"version":VERSION,"record":rec}

def compare_execution(payload):
    ex=normalize_execution(payload)
    if not ex.get("ok"): return ex
    expected=payload.get("expected") or []; observed=payload.get("observed") or ex["record"].get("observed") or []
    if not expected or not observed:
        return {"ok":True,"version":VERSION,"execution_ref":ex["record"]["execution_ref"],"comparison_status":"not-compared","reason":"expected and observed numeric arrays are both required","scientific_claim_confirmed":False,"boundary":BOUNDARY}
    try:
        c=rr.result_comparison({"expected":expected,"observed":observed,"absolute_tolerance":payload.get("absoluteTolerance",payload.get("absolute_tolerance",0.0)),"relative_tolerance":payload.get("relativeTolerance",payload.get("relative_tolerance",0.0))})
    except Exception as e:
        return {"ok":False,"version":VERSION,"error":str(e)}
    status="within-declared-tolerance" if c.get("all_within_tolerance") else "outside-declared-tolerance"
    return {"ok":True,"version":VERSION,"execution_ref":ex["record"]["execution_ref"],"comparison_status":status,"comparison":c,
      "verification_outcome_suggestion":"passed" if c.get("all_within_tolerance") else "failed","suggestion_requires_human_confirmation":True,
      "scientific_claim_confirmed":False,"automatic_resolution":False,"boundary":BOUNDARY}

def deviation_register(payload):
    try: out=rr.deviation_register({"deviations":payload.get("deviations") or []})
    except Exception as e: return {"ok":False,"version":VERSION,"error":str(e)}
    out["bridge_ref"]=_text(payload.get("bridgeRef",payload.get("bridge_ref")),2048) or None; out["automatic_impact_inference"]=False; return out

def verification_bundle(payload):
    req=normalize_request(payload); ex=normalize_execution(payload)
    if not req.get("ok"): return req
    if not ex.get("ok"): return ex
    r=req["record"]; e=ex["record"]
    bundle_id=_text(payload.get("bundleId",payload.get("bundle_id")),256) or f"verification-bundle-{e['id']}"
    event_id=_text(payload.get("verificationEventId",payload.get("verification_event_id")),512)
    if not event_id: return {"ok":False,"version":VERSION,"error":"verificationEventId is required to bind the evidence bundle to the audit event"}
    outcome=_text(payload.get("verificationOutcome",payload.get("verification_outcome")),64)
    if outcome not in ("passed","failed","inconclusive"): return {"ok":False,"version":VERSION,"error":"verificationOutcome must be passed, failed, or inconclusive and must be human-confirmed"}
    arts=[]
    for i,a in enumerate(e["output_artifacts"]):
        if not isinstance(a,dict): continue
        arts.append({"artifactType":a.get("artifactType",a.get("artifact_type")) or "reproduction-result","artifactRef":a.get("artifactRef",a.get("artifact_ref")) or f"{e['execution_ref']}:output:{i+1}",
          "title":a.get("title"),"versionRef":a.get("versionRef",a.get("version_ref")),"sha256":a.get("sha256"),"sourceObjectRef":a.get("sourceObjectRef",a.get("source_object_ref")),
          "executionRef":e["execution_ref"],"uri":a.get("uri"),"mediaType":a.get("mediaType",a.get("media_type")),"capturedAt":a.get("capturedAt",a.get("captured_at")),"note":a.get("note")})
    if not arts:
        arts=[{"artifactType":"execution","artifactRef":e["execution_ref"],"title":"Review-triggered reproduction execution","executionRef":e["execution_ref"],"note":"Execution record supplied to the v0.135.17.0 review-to-reproduction bridge."}]
    raw={"id":bundle_id,"threadId":r["thread_id"],"resolutionRecordId":r["resolution_record_id"],"auditRecordId":r["audit_record_id"],"annotationId":r["annotation_id"],
      "verificationEventId":event_id,"verificationOutcome":outcome,"verificationMethod":"rerun","verificationScope":_text(payload.get("verificationScope",payload.get("verification_scope")),2048) or "Review-triggered reproduction execution and declared result comparison",
      "artifacts":arts,"author":r["author"],"createdAt":payload.get("createdAt",payload.get("created_at"))}
    out=verification135150.normalize_bundle({"bundle":raw})
    if out.get("ok"): out["bridge_ref"]=r["id"]; out["execution_ref"]=e["execution_ref"]; out["human_confirmed_outcome_required"]=True
    return out

def audit_verification_draft(payload):
    b=verification_bundle(payload)
    if not b.get("ok"): return b
    rec=b["record"]
    return {"ok":True,"version":VERSION,"event":{"eventType":"verification-recorded","annotationId":rec["annotation_id"],"outcome":rec["verification_outcome"],
      "verificationMethod":"rerun","verificationRef":rec["id"],"note":"Recorded from v0.135.17.0 review-to-reproduction bridge after explicit human confirmation."},
      "append_only_target":"graphStudioReviewAudits","automatic_append":False,"automatic_resolution":False,"boundary":BOUNDARY}

def bridge_packet(payload):
    v=validate_request(payload)
    if not v.get("ok"): return v
    study=reproduction_study(payload); inventory=artifact_inventory(payload); plan=execution_plan(payload); scope=impact_scope(payload)
    packet={"schema":"sc-lab-review-to-reproduction-packet/0.135.17.0","version":VERSION,"target":"research-reproduction-replication-studio-v0.129.0",
      "bridge":v["record"],"study":study.get("study"),"artifact_inventory":inventory,"execution_plan":plan.get("plan"),"impact_scope":scope,
      "automatic_execution":False,"automatic_verification_outcome":False,"automatic_resolution":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"packet":packet}

def fingerprint(payload):
    n=normalize_request(payload)
    if not n.get("ok"): return n
    return {"ok":True,"version":VERSION,"algorithm":"sha256","fingerprint":_fp(n["record"])}

def status(payload):
    req=validate_request(payload); ex=normalize_execution(payload) if isinstance(payload,dict) and (payload.get("execution") or payload.get("executionRef") or payload.get("execution_ref")) else None
    return {"ok":req.get("ok",False),"version":VERSION,"bridge_ready":req.get("ok",False),"execution_supplied":bool(ex and ex.get("ok")),
      "execution_state":ex.get("record",{}).get("state") if ex and ex.get("ok") else None,"automatic_execution":False,"automatic_scientific_acceptance":False,"boundary":BOUNDARY}

def health(): return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"review_to_reproduction_bridge":True,"v01290_reproduction_engine_reused":True,"revision_impact_scope":True,"execution_verification":True,"verification_bundle_handoff":True,"audit_event_draft":True,"backward_compatible_v0135160":True}
def contract(): return {"ok":True,"version":VERSION,"eligible_revision_actions":list(REPRO_ACTIONS),"execution_states":list(EXECUTION_STATES),"project_collection":"graphStudioReviewReproductionBridges","reproduction_engine":"0.129.0","verification_bundle_contract":"0.135.15.0","review_audit_contract":"0.135.14.0","automatic_execution":False,"automatic_verification_outcome":False,"automatic_resolution":False,"truth_ranking":False}
def browser_contract(): return {"ok":True,"version":VERSION,"required_actions":["bridge-current-review","create-reproduction-plan","record-execution-result","compare-results","create-verification-bundle","open-reproduction-context"],"full_render_count_must_not_increase":True}
def acceptance_report(): return {"ok":True,"version":VERSION,"review_to_reproduction_bridge":True,"execution_verification":True,"reuses_v01290":True,"revision_impact_linkage":True,"verification_artifact_handoff":True,"audit_verification_draft":True,"project_persistence_explicit":True,"full_graph_redraw_for_bridge":False,"automatic_execution":False,"automatic_retry":False,"automatic_verification_outcome":False,"automatic_resolution":False,"automatic_claim_confirmation":False,"automatic_scientific_validity":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"scientific_preference":False}
