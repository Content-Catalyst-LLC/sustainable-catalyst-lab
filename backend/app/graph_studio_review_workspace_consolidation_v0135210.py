from __future__ import annotations
import copy, hashlib, json, time
from datetime import datetime, timezone

VERSION = "0.135.21.0"
ROUTE_COUNT = 18
BOUNDARY = (
    "Runtime certification verifies deterministic workspace assembly, ownership, hydration, restore, "
    "and retained review contracts. It does not establish scientific truth, validity, causal correctness, "
    "evidentiary weight, reviewer consensus, publication acceptance, or correctness of conclusions."
)

COLLECTIONS = (
    ("reviewThreads", ("reviewThreads", "review_threads")),
    ("resolutionRecords", ("resolutionRecords", "resolution_records")),
    ("auditRecords", ("auditRecords", "audit_records")),
    ("verificationBundles", ("verificationBundles", "verification_bundles")),
    ("impactAnalyses", ("impactAnalyses", "impact_analyses")),
    ("reproductionBridges", ("reproductionBridges", "reproduction_bridges")),
    ("reviewerPanels", ("reviewerPanels", "reviewer_panels")),
    ("crossReviewSyntheses", ("crossReviewSyntheses", "cross_review_syntheses")),
    ("reviewClosurePackages", ("reviewClosurePackages", "review_closure_packages")),
)
RESTORE_ORDER = [x[0] for x in COLLECTIONS]
EXPECTED_OWNERS = {
    "bootstrap": {"module": "graph-studio-bootstrap-finalization-v0135831", "version": "0.135.8.3.1"},
    "renderer": {"module": "graph-studio-renderer-replacement-v013582", "version": "0.135.8.2"},
    "provenance": {"module": "graph-studio-native-provenance-v013585", "version": "0.135.8.5.3"},
    "incrementalInteraction": {"module": "graph-studio-incremental-interaction-v0135852", "version": "0.135.8.5.2"},
    "reviewOrchestration": {"module": "graph-studio-review-workspace-consolidation-v0135210", "version": VERSION},
    "hydration": {"module": "graph-studio-review-workspace-consolidation-v0135210", "version": VERSION},
    "closure": {"module": "graph-studio-review-closure-v0135200", "version": "0.135.20.0"},
}
DISALLOWED_ACTIVE_MODULES = {
    "graph-studio-v0790", "graph-studio-v0800", "graph-studio-v0810", "graph-studio-v0820",
    "graph-studio-v0830", "graph-studio-v0840", "graph-studio-v0850", "graph-studio-v0870",
    "graph-studio-v0880", "graph-studio-provenance-interaction-recovery-v0135841",
}
EXPECTED_EVENTS = (
    "sc-lab:project:changed",
    "sc-lab:graph-studio-review-closure-v0135200",
    "sc-lab:graph-studio-cross-review-synthesis-v0135190",
)


def _now(): return datetime.now(timezone.utc).isoformat()
def _canon(v): return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _text(v, limit=4096): return "" if v is None else str(v).strip()[:limit]
def _get(o, *names, default=None):
    if not isinstance(o, dict): return default
    for name in names:
        if name in o and o[name] is not None: return o[name]
    return default

def _records(payload, names):
    source = payload.get("projectState") if isinstance(payload, dict) and isinstance(payload.get("projectState"), dict) else payload
    if not isinstance(source, dict): return []
    for name in names:
        value = source.get(name)
        if isinstance(value, list): return copy.deepcopy(value)
    return []

def _record_sort_key(rec):
    if not isinstance(rec, dict): return ("", "", _canon(rec))
    rid = _text(_get(rec, "id", "recordId", "record_id"), 1024)
    ts = _text(_get(rec, "updatedAt", "updated_at", "createdAt", "created_at", "timestamp"), 256)
    return (rid, ts, _canon(rec))

def _normalize_collection(records):
    out=[]; seen={}; duplicates=[]
    for raw in sorted(records, key=_record_sort_key):
        rec=copy.deepcopy(raw)
        rid=_text(_get(rec, "id", "recordId", "record_id"), 1024)
        if rid:
            if rid in seen: duplicates.append(rid)
            seen[rid]=seen.get(rid,0)+1
        out.append(rec)
    return out, sorted(set(duplicates))

def default_policy():
    return {
        "singleReviewWorkspaceController": True,
        "deterministicHydration": True,
        "deterministicRestoreOrder": True,
        "incrementalRendererOnly": True,
        "legacyGraphStudioExecutorsDisallowed": True,
        "duplicateCanonicalOwnersDisallowed": True,
        "duplicateConsolidationListenersDisallowed": True,
        "preserveHistoricalReviewRecords": True,
        "automaticScientificValidity": False,
        "automaticPublicationAcceptance": False,
        "truthRanking": False,
        "causalInference": False,
        "evidenceWeightInference": False,
    }

def normalize_workspace(payload):
    if not isinstance(payload, dict):
        return {"ok": False, "version": VERSION, "error": "payload must be an object", "boundary": BOUNDARY}
    project_id=_text(_get(payload, "projectId", "project_id"), 512) or "unbound-project"
    normalized={}; duplicates={}; counts={}
    for canonical,names in COLLECTIONS:
        rows,dups=_normalize_collection(_records(payload,names))
        normalized[canonical]=rows; counts[canonical]=len(rows)
        if dups: duplicates[canonical]=dups
    state={
        "schema":"sc-lab-graph-studio-review-workspace-state/0.135.21.0",
        "version":VERSION,
        "projectId":project_id,
        "collections":normalized,
        "counts":counts,
        "duplicateIds":duplicates,
        "restoreOrder":RESTORE_ORDER,
        "rendererMode":"incremental",
        "fullGraphRedraw":False,
        "scientificValidity":None,
        "publicationAcceptance":None,
        "boundary":BOUNDARY,
    }
    state["stateDigest"]=_fp({"projectId":project_id,"collections":normalized,"restoreOrder":RESTORE_ORDER})
    return {"ok":True,"version":VERSION,"state":state,"boundary":BOUNDARY}

def validate_workspace(payload):
    n=normalize_workspace(payload)
    if not n.get("ok"): return n
    state=n["state"]; errors=[]; warnings=[]
    if state["duplicateIds"]:
        errors.append("duplicate record ids detected in one or more consolidated review collections")
    if state["rendererMode"]!="incremental" or state["fullGraphRedraw"] is not False:
        errors.append("canonical workspace must preserve incremental renderer ownership")
    if sum(state["counts"].values())==0:
        warnings.append("workspace contains no review records; empty-state certification only")
    return {"ok":not errors,"version":VERSION,"state":state,"errors":errors,"warnings":warnings,"boundary":BOUNDARY}

def state_digest(payload):
    n=normalize_workspace(payload)
    return {"ok":n.get("ok",False),"version":VERSION,"projectId":n.get("state",{}).get("projectId"),"stateDigest":n.get("state",{}).get("stateDigest"),"counts":n.get("state",{}).get("counts",{}),"boundary":BOUNDARY}

def runtime_inventory():
    return {"ok":True,"version":VERSION,"owners":copy.deepcopy(EXPECTED_OWNERS),"disallowedActiveModules":sorted(DISALLOWED_ACTIVE_MODULES),"restoreOrder":list(RESTORE_ORDER),"expectedEvents":list(EXPECTED_EVENTS),"boundary":BOUNDARY}

def ownership_audit(payload):
    inventory=_get(payload,"runtimeInventory","runtime_inventory",default=[]) if isinstance(payload,dict) else []
    if not isinstance(inventory,list): inventory=[]
    active=[]
    for item in inventory:
        if isinstance(item,str): active.append({"module":item})
        elif isinstance(item,dict): active.append(copy.deepcopy(item))
    modules=[_text(x.get("module"),256) for x in active]
    missing=[]; mismatched=[]; duplicate_domains=[]
    for domain,expected in EXPECTED_OWNERS.items():
        matches=[x for x in active if _text(x.get("domain"),128)==domain or _text(x.get("module"),256)==expected["module"]]
        if active and not matches: missing.append(domain)
        if len(matches)>1: duplicate_domains.append(domain)
        for match in matches:
            version=_text(match.get("version"),128)
            if version and version!=expected["version"]: mismatched.append({"domain":domain,"expected":expected["version"],"actual":version})
    legacy=sorted(set(modules)&DISALLOWED_ACTIVE_MODULES)
    certified=not (missing or mismatched or duplicate_domains or legacy)
    return {"ok":certified,"version":VERSION,"certified":certified,"missingOwners":missing,"mismatchedOwners":mismatched,"duplicateOwnerDomains":duplicate_domains,"disallowedActiveModules":legacy,"expectedOwners":copy.deepcopy(EXPECTED_OWNERS),"boundary":BOUNDARY}

def listener_audit(payload):
    listeners=_get(payload,"listeners","listenerInventory","listener_inventory",default=[]) if isinstance(payload,dict) else []
    if not isinstance(listeners,list): listeners=[]
    relevant={}
    for item in listeners:
        if not isinstance(item,dict): continue
        event=_text(_get(item,"event","eventName","event_name"),256)
        owner=_text(_get(item,"owner","module"),256)
        if event: relevant.setdefault(event,[]).append(owner or "unknown")
    duplicates={e:owners for e,owners in relevant.items() if len([x for x in owners if x=="graph-studio-review-workspace-consolidation-v0135210"])>1}
    return {"ok":not duplicates,"version":VERSION,"duplicateConsolidationListeners":duplicates,"events":relevant,"expectedEvents":list(EXPECTED_EVENTS),"boundary":BOUNDARY}

def restore_plan(payload):
    n=normalize_workspace(payload)
    if not n.get("ok"): return n
    state=n["state"]; steps=[]
    for i,name in enumerate(RESTORE_ORDER,1):
        steps.append({"order":i,"collection":name,"recordCount":state["counts"][name],"mode":"hydrate-no-redraw" if name!="reviewThreads" else "hydrate"})
    plan={"schema":"sc-lab-graph-studio-review-restore-plan/0.135.21.0","version":VERSION,"projectId":state["projectId"],"stateDigest":state["stateDigest"],"steps":steps,"rendererAction":"preserve-scene-graph","fullGraphRedraw":False,"requiresHumanScientificJudgment":True,"createdAt":_now(),"boundary":BOUNDARY}
    plan["planDigest"]=_fp({k:v for k,v in plan.items() if k not in {"createdAt","planDigest"}})
    return {"ok":True,"version":VERSION,"plan":plan,"boundary":BOUNDARY}

def performance_profile(payload):
    start=time.perf_counter(); n=normalize_workspace(payload); elapsed_ms=(time.perf_counter()-start)*1000
    state=n.get("state",{}); total=sum(state.get("counts",{}).values())
    return {"ok":n.get("ok",False),"version":VERSION,"records":total,"normalizationMs":round(elapsed_ms,3),"stateDigest":state.get("stateDigest"),"profile":"deterministic-linear-collection-normalization","rendererWork":"none","fullGraphRedraw":False,"boundary":BOUNDARY}

def compatibility_report(payload):
    supplied=_get(payload,"versions","moduleVersions","module_versions",default={}) if isinstance(payload,dict) else {}
    if not isinstance(supplied,dict): supplied={}
    checks=[]
    for domain,expected in EXPECTED_OWNERS.items():
        actual=_text(supplied.get(domain),128)
        checks.append({"domain":domain,"expected":expected["version"],"actual":actual or None,"compatible":not actual or actual==expected["version"]})
    return {"ok":all(x["compatible"] for x in checks),"version":VERSION,"checks":checks,"boundary":BOUNDARY}

def certify(payload):
    valid=validate_workspace(payload)
    owners=ownership_audit(payload)
    listeners=listener_audit(payload)
    plan=restore_plan(payload)
    perf=performance_profile(payload)
    errors=[]
    if not valid.get("ok"): errors.extend(valid.get("errors",[]))
    if not owners.get("ok"): errors.append("runtime ownership audit failed")
    if not listeners.get("ok"): errors.append("consolidation listener audit failed")
    if not plan.get("ok"): errors.append("restore plan generation failed")
    report={
        "schema":"sc-lab-graph-studio-runtime-certification/0.135.21.0",
        "version":VERSION,
        "projectId":valid.get("state",{}).get("projectId"),
        "stateDigest":valid.get("state",{}).get("stateDigest"),
        "certified":not errors,
        "errors":errors,
        "warnings":valid.get("warnings",[]),
        "ownership":owners,
        "listeners":listeners,
        "restorePlan":plan.get("plan"),
        "performance":perf,
        "rendererMode":"incremental",
        "fullGraphRedraw":False,
        "scientificValidity":None,
        "publicationAcceptance":None,
        "createdAt":_now(),
        "boundary":BOUNDARY,
    }
    report["certificationDigest"]=_fp({k:v for k,v in report.items() if k not in {"createdAt","certificationDigest"}})
    return {"ok":report["certified"],"version":VERSION,"certification":report,"boundary":BOUNDARY}

def project_workspace_packet(payload):
    cert=certify(payload)
    return {"ok":cert.get("ok",False),"version":VERSION,"packet":{"schema":"sc-lab-project-workspace-review-runtime-certification/0.135.21.0","target":"project-workspace","certification":cert.get("certification"),"readOnly":True,"createdAt":_now(),"boundary":BOUNDARY},"boundary":BOUNDARY}

def status(payload):
    n=normalize_workspace(payload); return {"ok":n.get("ok",False),"version":VERSION,"projectId":n.get("state",{}).get("projectId"),"counts":n.get("state",{}).get("counts",{}),"stateDigest":n.get("state",{}).get("stateDigest"),"rendererMode":"incremental","fullGraphRedraw":False,"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"review_workspace_consolidation":True,"deterministic_hydration":True,"runtime_certification":True,"chromium_certification_harness":True,"incremental_renderer_only":True,"full_graph_redraw":False,"backward_compatible_v0135200":True,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"single_review_workspace_controller":True,"deterministic_hydration":True,"deterministic_restore":True,"ownership_audit":True,"listener_audit":True,"runtime_certification":True,"project_workspace_packet":True,"chromium_certification_harness":True,"historical_review_records_preserved":True,"automatic_scientific_validity":False,"automatic_publication_acceptance":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"full_graph_redraw":False,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":"sc-lab-graph-studio-review-workspace-consolidation/0.135.21.0","collection":"graphStudioReviewWorkspaceCertifications","restoreOrder":list(RESTORE_ORDER),"owners":copy.deepcopy(EXPECTED_OWNERS),"boundary":BOUNDARY}

def browser_contract():
    return {"ok":True,"version":VERSION,"requiredHarness":"tests/chromium-v0135210.html","requiredAssertions":["single-consolidated-toolbar","deterministic-state-digest","no-full-redraw","retained-review-api","project-switch-rehydrate"],"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":["javascript-static","javascript-runtime","php-integration","backend-regression","manifest-integrity","packaged-backend-import","packaged-repository-gate","chromium-headless"],"requiredRouteCount":ROUTE_COUNT,"boundary":BOUNDARY}
