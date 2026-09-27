from __future__ import annotations
import copy, hashlib, json, re
from datetime import datetime, timezone
from . import graph_studio_cross_review_synthesis_v0135190 as crossreview

VERSION = "0.135.20.0"
ROUTE_COUNT = 21
BOUNDARY = (
    "Review closure and publication readiness are administrative/reproducibility workflow assessments. "
    "A ready state does not establish scientific truth, validity, causal correctness, evidentiary weight, "
    "reviewer consensus, or publication acceptance. Dissent and limitations remain preserved as disclosures."
)
FAIL_STATES = {"failed","fail","invalid","mismatch","rejected","error","unverified","not-verified","not_verified"}
CLOSED_STATES = {"resolved","closed","complete","completed","archived"}


def _now(): return datetime.now(timezone.utc).isoformat()
def _text(v, limit=4096): return "" if v is None else str(v).strip()[:limit]
def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default
def _list(v, limit=5000): return copy.deepcopy(v[:limit]) if isinstance(v,list) else []
def _slug(v, fallback="closure"):
    s=re.sub(r"[^a-zA-Z0-9._:-]+","-",_text(v,256)).strip("-")
    return s or fallback
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _fp(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _state(o): return _text(_get(o,"status","state","verification_outcome","verificationOutcome","execution_state","executionState"),128).lower()

def default_policy():
    return {
        "requireAdministrativeClosure": True,
        "requirePanelCompletionWhenPanelExists": True,
        "requireVerificationIntegrity": True,
        "requireAuditTrail": True,
        "requireReproductionSuccessWhenRecorded": True,
        "preserveDissentAsDisclosure": True,
        "allowDissentWithoutConsensus": True,
        "requireScientificConsensus": False,
        "automaticScientificValidity": False,
        "automaticPublicationAcceptance": False,
    }

def _policy(raw):
    p=default_policy(); incoming=_get(raw,"readinessPolicy","readiness_policy",default={})
    if isinstance(incoming,dict):
        for k in p:
            if k in incoming and isinstance(incoming[k],bool): p[k]=incoming[k]
    # Hard scientific boundaries may not be enabled by a package.
    p["requireScientificConsensus"]=False
    p["automaticScientificValidity"]=False
    p["automaticPublicationAcceptance"]=False
    return p

def _synthesis_from(raw):
    s=_get(raw,"synthesis","crossReviewSynthesis","cross_review_synthesis",default=None)
    if isinstance(s,dict):
        n=crossreview.normalize_synthesis({"synthesis":s})
        return n.get("record") if n.get("ok") else None
    # Allow closure build directly from project review collections.
    keys=("reviewThreads","resolutionRecords","reviewerPanels","verificationBundles","reproductionBridges","impactAnalyses","auditRecords")
    if any(k in raw for k in keys):
        n=crossreview.normalize_synthesis(raw)
        return n.get("record") if n.get("ok") else None
    return None

def normalize_closure(payload):
    if not isinstance(payload,dict): return {"ok":False,"version":VERSION,"error":"payload must be an object"}
    raw=payload.get("closure") if isinstance(payload.get("closure"),dict) else payload
    synthesis=_synthesis_from(raw)
    project_id=_text(_get(raw,"projectId","project_id"),512) or _text(_get(synthesis or {},"project_id","projectId"),512) or "unbound-project"
    cid=_text(_get(raw,"id","closureId","closure_id"),512) or f"review-closure-{_slug(project_id)}"
    rec={
        "schema":"sc-lab-review-closure-package/0.135.20.0",
        "version":VERSION,
        "record_type":"review-closure-package",
        "collection":"graphStudioReviewClosurePackages",
        "id":cid,
        "project_id":project_id,
        "project_version_ref":_text(_get(raw,"projectVersionRef","project_version_ref"),2048) or None,
        "synthesis":copy.deepcopy(synthesis),
        "readiness_policy":_policy(raw),
        "closure_notes":_text(_get(raw,"closureNotes","closure_notes"),12000) or None,
        "publication_target":copy.deepcopy(_get(raw,"publicationTarget","publication_target",default={})) if isinstance(_get(raw,"publicationTarget","publication_target",default={}),dict) else {},
        "created_at":_text(_get(raw,"createdAt","created_at"),128) or _now(),
        "created_by":_text(_get(raw,"createdBy","created_by","author"),256) or "user",
        "boundary":BOUNDARY,
    }
    rec["package_fingerprint"]=_fp({k:v for k,v in rec.items() if k not in {"package_fingerprint","freeze"}})
    return {"ok":True,"version":VERSION,"record":rec}

def validate_closure(payload):
    n=normalize_closure(payload)
    if not n.get("record"): return n
    r=n["record"]; errors=[]; warnings=[]
    if not r["project_id"]: errors.append("projectId is required")
    if not isinstance(r.get("synthesis"),dict): errors.append("cross-review synthesis is required")
    else:
        v=crossreview.validate_synthesis({"synthesis":r["synthesis"]})
        if not v.get("ok"): errors.extend(["synthesis: "+x for x in v.get("errors",[])])
        if _text(_get(r["synthesis"],"project_id","projectId"),512) not in {"",r["project_id"]}: warnings.append("closure project differs from synthesis project")
    return {"ok":not errors,"version":VERSION,"record":r,"errors":errors,"warnings":warnings,"boundary":BOUNDARY}

def _matrix(s):
    if not isinstance(s,dict): return []
    return crossreview.resolution_matrix({"synthesis":s}).get("rows",[])

def _verification_records(s): return _list(_get(s,"verification_bundles","verificationBundles",default=[]))
def _reproduction_records(s): return _list(_get(s,"reproduction_bridges","reproductionBridges",default=[]))
def _audit_records(s): return _list(_get(s,"audit_records","auditRecords",default=[]))
def _panel_records(s): return _list(_get(s,"reviewer_panels","reviewerPanels",default=[]))
def _impact_records(s): return _list(_get(s,"impact_analyses","impactAnalyses",default=[]))

def _integrity_status(obj):
    st=_state(obj)
    if st in FAIL_STATES: return "failed"
    integrity=_get(obj,"integrity",default=None)
    if isinstance(integrity,dict) and integrity.get("ok") is False: return "failed"
    if _get(obj,"integrity_ok","integrityOk") is False: return "failed"
    return "recorded"

def readiness_report(payload):
    n=normalize_closure(payload)
    if not n.get("record"): return n
    r=n["record"]; s=r.get("synthesis") or {}; p=r["readiness_policy"]; matrix=_matrix(s)
    blockers=[]; disclosures=[]; checks=[]
    def check(cid,label,passed,required=True,detail=None):
        checks.append({"id":cid,"label":label,"passed":bool(passed),"required":bool(required),"detail":detail})
        if required and not passed: blockers.append({"code":cid,"label":label,"detail":detail})
    open_rows=[x for x in matrix if x.get("administratively_open") is True or x.get("administrativelyOpen") is True]
    check("administrative-closure","All review threads are administratively closed",len(open_rows)==0,p["requireAdministrativeClosure"],{"openThreadIds":[_get(x,"thread_id","threadId") for x in open_rows]})
    incomplete_panels=[x for x in matrix if (_get(x,"reviewer_panel_count","reviewerPanelCount",default=0) or 0)>0 and _get(x,"panel_administratively_complete","panelAdministrativelyComplete") is not True]
    check("panel-completion","Reviewer panels with assigned reviewers are administratively complete",len(incomplete_panels)==0,p["requirePanelCompletionWhenPanelExists"],{"threadIds":[_get(x,"thread_id","threadId") for x in incomplete_panels]})
    ver=_verification_records(s); bad_ver=[_get(x,"id",default="unknown") for x in ver if _integrity_status(x)=="failed"]
    check("verification-integrity","Recorded verification bundles contain no declared failure/integrity failure",len(bad_ver)==0,p["requireVerificationIntegrity"],{"failedVerificationIds":bad_ver})
    reps=_reproduction_records(s); bad_rep=[_get(x,"id",default="unknown") for x in reps if _state(x) in FAIL_STATES]
    check("reproduction-results","Recorded reproduction workflows contain no declared failed terminal outcome",len(bad_rep)==0,p["requireReproductionSuccessWhenRecorded"],{"failedReproductionIds":bad_rep})
    audits=_audit_records(s)
    check("audit-trail","Review audit records are present when review threads exist",bool(audits) or len(matrix)==0,p["requireAuditTrail"],{"auditRecordCount":len(audits)})
    dissent=[]
    for panel in _panel_records(s):
        for d in _list(_get(panel,"dissents",default=[]),1000):
            dissent.append({"panelId":_get(panel,"id"),"threadId":_get(panel,"thread_id","threadId"),"dissentId":_get(d,"id"),"reviewerId":_get(d,"reviewer_id","reviewerId"),"statement":_text(_get(d,"statement"),4000),"alternativeInterpretation":_get(d,"alternative_interpretation","alternativeInterpretation")})
    if dissent and p["preserveDissentAsDisclosure"]:
        disclosures.append({"code":"reviewer-dissent","label":"Reviewer dissent is preserved in the closure package","count":len(dissent),"records":dissent})
    if reps:
        disclosures.append({"code":"reproduction-records","label":"Reproduction/replication records are included and must be interpreted with their declared tolerances and limitations","count":len(reps)})
    impacts=_impact_records(s)
    if impacts:
        disclosures.append({"code":"revision-impact","label":"Revision-impact analyses identify declared dependencies, not scientific invalidity or causation","count":len(impacts)})
    state="not-ready" if blockers else ("ready-with-disclosures" if disclosures else "ready")
    return {"ok":True,"version":VERSION,"closure_id":r["id"],"project_id":r["project_id"],"state":state,"administratively_ready":not blockers,"checks":checks,"blockers":blockers,"disclosures":disclosures,"scientific_validity":None,"publication_acceptance":None,"consensus_required":False,"boundary":BOUNDARY}

def blocker_register(payload):
    r=readiness_report(payload); return {"ok":r.get("ok",False),"version":VERSION,"blockers":r.get("blockers",[]),"count":len(r.get("blockers",[])),"boundary":BOUNDARY}
def disclosure_register(payload):
    r=readiness_report(payload); return {"ok":r.get("ok",False),"version":VERSION,"disclosures":r.get("disclosures",[]),"count":len(r.get("disclosures",[])),"boundary":BOUNDARY}

def closure_manifest(payload):
    n=normalize_closure(payload)
    if not n.get("record"): return n
    r=n["record"]; s=r.get("synthesis") or {}; matrix=_matrix(s)
    components={
        "crossReviewSynthesis":1 if s else 0,
        "reviewThreads":len(_list(_get(s,"review_threads","reviewThreads",default=[]))),
        "resolutionRecords":len(_list(_get(s,"resolution_records","resolutionRecords",default=[]))),
        "reviewerPanels":len(_panel_records(s)),
        "verificationBundles":len(_verification_records(s)),
        "reproductionBridges":len(_reproduction_records(s)),
        "impactAnalyses":len(_impact_records(s)),
        "auditRecords":len(_audit_records(s)),
        "matrixRows":len(matrix),
    }
    hashes={"synthesis":_fp(s),"resolutionMatrix":_fp(matrix),"readinessPolicy":_fp(r["readiness_policy"])}
    manifest={"schema":"sc-lab-review-closure-manifest/0.135.20.0","version":VERSION,"closureId":r["id"],"projectId":r["project_id"],"createdAt":_now(),"components":components,"componentFingerprints":hashes,"boundary":BOUNDARY}
    manifest["manifestFingerprint"]=_fp({k:v for k,v in manifest.items() if k!="manifestFingerprint"})
    return {"ok":True,"version":VERSION,"manifest":manifest}

def build_closure(payload):
    n=normalize_closure(payload)
    if not n.get("record"): return n
    rec=n["record"]
    valid=validate_closure({"closure":rec})
    ready=readiness_report({"closure":rec})
    manifest=closure_manifest({"closure":rec}).get("manifest")
    s=rec.get("synthesis") or {}
    package=copy.deepcopy(rec)
    package.update({
        "resolution_matrix":_matrix(s),
        "open_items":crossreview.open_items({"synthesis":s}).get("items",[]),
        "disagreement_register":crossreview.disagreement_register({"synthesis":s}).get("items",[]),
        "verification_matrix":crossreview.verification_matrix({"synthesis":s}).get("items",[]),
        "reproduction_matrix":crossreview.reproduction_matrix({"synthesis":s}).get("items",[]),
        "revision_impact_matrix":crossreview.revision_impact_matrix({"synthesis":s}).get("items",[]),
        "resolution_history":crossreview.resolution_history({"synthesis":s}).get("items",[]),
        "subject_index":crossreview.subject_index({"synthesis":s}).get("items",[]),
        "readiness":ready,
        "manifest":manifest,
        "frozen":False,
    })
    package["package_fingerprint"]=_fp({k:v for k,v in package.items() if k not in {"package_fingerprint","freeze"}})
    return {"ok":valid.get("ok",False),"version":VERSION,"package":package,"validation":valid,"readiness":ready,"boundary":BOUNDARY}

def freeze_package(payload):
    built=build_closure(payload)
    if not built.get("package"): return built
    package=copy.deepcopy(built["package"]); readiness=built["readiness"]
    allow_not_ready=bool(_get(payload,"allowNotReadyFreeze","allow_not_ready_freeze",default=False)) if isinstance(payload,dict) else False
    if readiness.get("state")=="not-ready" and not allow_not_ready:
        return {"ok":False,"version":VERSION,"error":"closure package is not publication-ready; set allowNotReadyFreeze=true only to create a non-ready archival freeze","readiness":readiness,"boundary":BOUNDARY}
    core={k:v for k,v in package.items() if k not in {"freeze","package_fingerprint","frozen"}}
    freeze={"schema":"sc-lab-review-closure-freeze/0.135.20.0","version":VERSION,"frozenAt":_now(),"closureFingerprint":_fp(core),"readinessState":readiness.get("state"),"archivalOnly":readiness.get("state")=="not-ready"}
    freeze["freezeFingerprint"]=_fp(freeze)
    package["frozen"]=True; package["freeze"]=freeze; package["package_fingerprint"]=_fp({k:v for k,v in package.items() if k!="package_fingerprint"})
    return {"ok":True,"version":VERSION,"package":package,"freeze":freeze,"readiness":readiness,"boundary":BOUNDARY}

def verify_freeze(payload):
    pkg=_get(payload,"package",default=payload) if isinstance(payload,dict) else None
    if not isinstance(pkg,dict): return {"ok":False,"version":VERSION,"error":"package must be an object"}
    fr=pkg.get("freeze") if isinstance(pkg.get("freeze"),dict) else None
    if not fr: return {"ok":False,"version":VERSION,"verified":False,"error":"freeze record missing"}
    core={k:v for k,v in pkg.items() if k not in {"freeze","package_fingerprint","frozen"}}
    closure_ok=_fp(core)==fr.get("closureFingerprint")
    fcopy={k:v for k,v in fr.items() if k!="freezeFingerprint"}; freeze_ok=_fp(fcopy)==fr.get("freezeFingerprint")
    pcopy={k:v for k,v in pkg.items() if k!="package_fingerprint"}; package_ok=_fp(pcopy)==pkg.get("package_fingerprint")
    return {"ok":closure_ok and freeze_ok and package_ok,"version":VERSION,"verified":closure_ok and freeze_ok and package_ok,"closureFingerprintValid":closure_ok,"freezeFingerprintValid":freeze_ok,"packageFingerprintValid":package_ok,"boundary":BOUNDARY}

def compare_packages(payload):
    a=_get(payload,"before","a",default={}) if isinstance(payload,dict) else {}; b=_get(payload,"after","b",default={}) if isinstance(payload,dict) else {}
    def summary(x):
        if not isinstance(x,dict): return {}
        rr=x.get("readiness") if isinstance(x.get("readiness"),dict) else {}
        return {"id":x.get("id"),"fingerprint":x.get("package_fingerprint"),"readiness":rr.get("state"),"blockerCount":len(rr.get("blockers",[])),"disclosureCount":len(rr.get("disclosures",[])),"frozen":bool(x.get("frozen"))}
    sa,sb=summary(a),summary(b)
    return {"ok":True,"version":VERSION,"before":sa,"after":sb,"changed":sa!=sb,"fingerprintChanged":sa.get("fingerprint")!=sb.get("fingerprint"),"boundary":BOUNDARY}

def closure_summary(payload):
    b=build_closure(payload)
    if not b.get("package"): return b
    p=b["package"]; r=b["readiness"]
    return {"ok":b.get("ok",False),"version":VERSION,"closureId":p["id"],"projectId":p["project_id"],"readinessState":r["state"],"blockerCount":len(r["blockers"]),"disclosureCount":len(r["disclosures"]),"reviewThreadCount":len(p.get("resolution_matrix",[])),"frozen":bool(p.get("frozen")),"boundary":BOUNDARY}

def publication_handoff(payload):
    b=build_closure(payload)
    if not b.get("package"): return b
    p=b["package"]; r=b["readiness"]
    packet={"schema":"sc-lab-publication-readiness-handoff/0.135.20.0","version":VERSION,"target":"publication-studio","closureId":p["id"],"projectId":p["project_id"],"projectVersionRef":p.get("project_version_ref"),"readiness":copy.deepcopy(r),"closureManifest":copy.deepcopy(p.get("manifest")),"closurePackageFingerprint":p.get("package_fingerprint"),"publicationTarget":copy.deepcopy(p.get("publication_target",{})),"scientificValidity":None,"publicationAcceptance":None,"createdAt":_now(),"boundary":BOUNDARY}
    packet["fingerprint"]=_fp({k:v for k,v in packet.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"packet":packet,"boundary":BOUNDARY}

def project_workspace_packet(payload):
    b=build_closure(payload)
    if not b.get("package"): return b
    p=b["package"]
    return {"ok":True,"version":VERSION,"packet":{"schema":"sc-lab-project-workspace-review-closure/0.135.20.0","version":VERSION,"closure":p,"readiness":b["readiness"],"openedAt":_now(),"boundary":BOUNDARY}}

def audit_event_draft(payload):
    b=build_closure(payload)
    if not b.get("package"): return b
    p=b["package"]
    event={"schema":"sc-lab-review-audit-event-draft/0.135.20.0","version":VERSION,"eventType":"review-closure-package-prepared","projectId":p["project_id"],"closureId":p["id"],"readinessState":b["readiness"]["state"],"packageFingerprint":p["package_fingerprint"],"createdAt":_now(),"appendOnly":True,"boundary":BOUNDARY}
    event["fingerprint"]=_fp({k:v for k,v in event.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"event":event}

def reopen_plan(payload):
    pkg=_get(payload,"package",default=payload) if isinstance(payload,dict) else {}
    cid=_text(_get(pkg,"id","closureId","closure_id"),512) or "unknown-closure"
    reason=_text(_get(payload,"reason"),8000) if isinstance(payload,dict) else ""
    plan={"schema":"sc-lab-review-closure-reopen-plan/0.135.20.0","version":VERSION,"closureId":cid,"reason":reason or "Reopen reason required before execution","requiresHumanConfirmation":True,"automaticReopen":False,"createdAt":_now(),"boundary":BOUNDARY}
    plan["fingerprint"]=_fp({k:v for k,v in plan.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"plan":plan}

def status(payload):
    s=closure_summary(payload); s.update({"publicationReadiness":True,"closureFreeze":True,"automaticScientificValidity":False,"automaticPublicationAcceptance":False}); return s

def health():
    return {"ok":True,"version":VERSION,"api_route_count":ROUTE_COUNT,"review_closure_packages":True,"publication_readiness":True,"closure_freeze":True,"dissent_preserved":True,"cross_review_synthesis_dependency":"0.135.19.0","backward_compatible_v0135190":True}
def contract():
    return {"ok":True,"version":VERSION,"schema":"sc-lab-review-closure-package/0.135.20.0","collection":"graphStudioReviewClosurePackages","readinessStates":["not-ready","ready-with-disclosures","ready"],"boundary":BOUNDARY}
def browser_contract():
    return {"ok":True,"version":VERSION,"global":"SCLabGraphStudioReviewClosureV0135200","contextKey":"scLabGraphStudioReviewClosureV0135200","fullGraphRedraw":False,"incrementalUI":True,"projectWorkspaceHandoff":True,"publicationStudioHandoff":True}
def acceptance_report():
    return {"ok":True,"version":VERSION,"review_closure_packages":True,"publication_readiness":True,"closure_manifest":True,"fingerprinted_freeze":True,"blocker_register":True,"disclosure_register":True,"dissent_preserved":True,"publication_studio_handoff":True,"cross_review_synthesis_reused":True,"automatic_resolution":False,"majority_voting":False,"consensus_scoring":False,"reviewer_ranking":False,"automatic_scientific_validity":False,"automatic_publication_acceptance":False,"truth_ranking":False,"causal_inference":False,"evidence_weight_inference":False,"full_graph_redraw":False,"boundary":BOUNDARY}
