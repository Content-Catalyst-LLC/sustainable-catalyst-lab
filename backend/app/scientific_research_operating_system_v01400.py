from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from . import research_change_impact_living_analysis_v01370 as living
from . import research_program_intelligence_v01380 as programs
from . import scholarly_study_original_research_package_v01390 as scholarly

VERSION = "0.140.0"
ROUTE_COUNT = 25
SCHEMA = "sc-lab-scientific-research-operating-system/0.140.0"
SNAPSHOT_SCHEMA = "sc-lab-scientific-research-os-snapshot/0.140.0"
BOUNDARY = (
    "Scientific Research Operating System coordinates declared Lab research objects and capability handoffs across the "
    "scientific lifecycle. It does not replace source systems, infer scientific truth, automatically advance research "
    "states, certify validity or reproducibility, rank evidence, resolve reviewer disagreement, or grant publication acceptance."
)

PHASES = (
    "question", "design", "data", "compute", "analysis", "evidence", "interpretation",
    "review", "reproduction", "publication", "living-research", "research-program",
)
CAPABILITIES = (
    ("research-question-hypothesis", "0.131.0"),
    ("method-selection", "0.132.0"),
    ("assumption-diagnostics", "0.133.0"),
    ("evidence-synthesis", "0.134.0"),
    ("competing-model-hypothesis", "0.135.0"),
    ("integrated-review-reproducibility", "0.136.0"),
    ("research-change-impact-living-analysis", "0.137.0"),
    ("research-program-intelligence", "0.138.0"),
    ("scholarly-study-original-research-package", "0.139.0"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _txt(value: Any, limit: int = 4096) -> str:
    return str(value or "").strip()[:limit]


def _dict(value: Any) -> dict:
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def _list(value: Any) -> list:
    return copy.deepcopy(value) if isinstance(value, list) else []


def _get(obj: dict, *names: str, default=None):
    if not isinstance(obj, dict):
        return default
    for name in names:
        if name in obj and obj[name] is not None:
            return obj[name]
    return default


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _fp(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def capability_catalog() -> list[dict]:
    return [{"capability": name, "introducedVersion": version, "sourceAuthorityPreserved": True} for name, version in CAPABILITIES]


def normalize(payload: dict) -> dict:
    raw = payload.get("researchOS") if isinstance(payload, dict) and isinstance(payload.get("researchOS"), dict) else (payload if isinstance(payload, dict) else {})
    project_id = _txt(_get(raw, "projectId", "project_id", "studyId", "study_id", "id"), 512)
    title = _txt(_get(raw, "title", "name"), 1024)
    if not project_id and not title:
        return {"ok": False, "version": VERSION, "error": "projectId, studyId, id, or title is required", "boundary": BOUNDARY}
    if not project_id:
        project_id = f"research-os-{_fp({'title': title})[:20]}"
    declared_phase = _txt(_get(raw, "phase", "currentPhase", "current_phase"), 128) or "question"
    if declared_phase not in PHASES:
        declared_phase = "question"
    record = {
        "schema": SCHEMA,
        "version": VERSION,
        "recordType": "scientific-research-operating-system",
        "collection": "scientificResearchOperatingSystems",
        "id": _txt(_get(raw, "id", "researchOSId", "research_os_id"), 512) or f"research-os:{project_id}",
        "projectId": project_id,
        "studyId": _txt(_get(raw, "studyId", "study_id"), 512) or project_id,
        "title": title or project_id,
        "phase": declared_phase,
        "phaseDeclaredByUser": True,
        "question": copy.deepcopy(_get(raw, "question", "researchQuestion", "research_question")),
        "hypotheses": _list(raw.get("hypotheses")),
        "methods": _list(raw.get("methods")),
        "datasets": _list(raw.get("datasets")),
        "executions": _list(_get(raw, "executions", "runs", default=[])),
        "analyses": _list(raw.get("analyses")),
        "models": _list(raw.get("models")),
        "figures": _list(raw.get("figures")),
        "tables": _list(raw.get("tables")),
        "evidence": _list(raw.get("evidence")),
        "claims": _list(raw.get("claims")),
        "findings": _list(raw.get("findings")),
        "limitations": _list(raw.get("limitations")),
        "reviews": _list(_get(raw, "reviews", "reviewRecords", default=[])),
        "reproductionPackages": _list(_get(raw, "reproductionPackages", "reproduction_packages", default=[])),
        "manuscripts": _list(raw.get("manuscripts")),
        "nodes": _list(raw.get("nodes")),
        "edges": _list(raw.get("edges")),
        "changeEvents": _list(_get(raw, "changeEvents", "change_events", default=[])),
        "program": _dict(raw.get("program")),
        "scholarlyPackage": _dict(_get(raw, "scholarlyPackage", "scholarly_package")),
        "workspace": _dict(_get(raw, "workspace", "workspaceState", "workspace_state")),
        "provenance": _dict(raw.get("provenance")),
        "capabilities": capability_catalog(),
        "createdAt": _txt(_get(raw, "createdAt", "created_at"), 128) or _now(),
        "createdBy": _txt(_get(raw, "createdBy", "created_by"), 256) or "user",
        "sourceAuthorityPreserved": True,
        "automaticPhaseAdvance": False,
        "automaticScientificValidity": False,
        "automaticPublicationAcceptance": False,
        "boundary": BOUNDARY,
    }
    record["fingerprint"] = _fp({k: v for k, v in record.items() if k not in {"fingerprint", "createdAt"}})
    return {"ok": True, "version": VERSION, "record": record, "boundary": BOUNDARY}


def validate(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    warnings = []
    if r["question"] in (None, "", {}): warnings.append("no research question is declared")
    if not r["methods"]: warnings.append("no methods are declared")
    if not r["datasets"] and not r["evidence"]: warnings.append("no datasets or evidence are declared")
    if not r["limitations"]: warnings.append("no limitations are declared")
    return {"ok": True, "version": VERSION, "record": r, "errors": [], "warnings": warnings, "boundary": BOUNDARY}


def lifecycle(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"): return out
    r = out["record"]
    signals = {
        "question": bool(r["question"] or r["hypotheses"]),
        "design": bool(r["methods"]),
        "data": bool(r["datasets"]),
        "compute": bool(r["executions"] or r["models"]),
        "analysis": bool(r["analyses"]),
        "evidence": bool(r["evidence"] or r["claims"] or r["findings"]),
        "interpretation": bool(r["findings"] or r["limitations"]),
        "review": bool(r["reviews"]),
        "reproduction": bool(r["reproductionPackages"]),
        "publication": bool(r["manuscripts"] or r["scholarlyPackage"]),
        "living-research": bool(r["changeEvents"]),
        "research-program": bool(r["program"]),
    }
    rows = [{"phase": p, "declaredArtifactsPresent": bool(signals[p]), "stateInferred": False} for p in PHASES]
    return {"ok": True, "version": VERSION, "projectId": r["projectId"], "declaredCurrentPhase": r["phase"], "phases": rows, "automaticPhaseAdvance": False, "boundary": BOUNDARY}


def capability_matrix(payload: dict | None = None) -> dict:
    return {"ok": True, "version": VERSION, "capabilities": capability_catalog(), "count": len(CAPABILITIES), "orchestrationDoesNotReplaceSubsystemAuthority": True, "boundary": BOUNDARY}


def study_context(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    return {"ok": True, "version": VERSION, "study": {"projectId": r["projectId"], "studyId": r["studyId"], "title": r["title"], "phase": r["phase"], "fingerprint": r["fingerprint"]}, "boundary": BOUNDARY}


def living_context(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    if not r["nodes"] and not r["changeEvents"]:
        return {"ok": True, "version": VERSION, "projectId": r["projectId"], "livingAnalysis": None, "reason": "no living-analysis inputs declared", "boundary": BOUNDARY}
    result=living.living_status({"projectId":r["projectId"],"nodes":r["nodes"],"edges":r["edges"],"changeEvents":r["changeEvents"]})
    return {"ok": bool(result.get("ok")), "version": VERSION, "projectId": r["projectId"], "livingAnalysis": result, "sourceVersion": "0.137.0", "boundary": BOUNDARY}


def program_context(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    if not r["program"]:
        return {"ok": True, "version": VERSION, "projectId": r["projectId"], "programContext": None, "boundary": BOUNDARY}
    p=copy.deepcopy(r["program"]); p.setdefault("studyId",r["studyId"])
    result=programs.study_context({**p,"program":p,"studyId":r["studyId"]})
    return {"ok": bool(result.get("ok")), "version": VERSION, "projectId": r["projectId"], "programContext": result, "sourceVersion": "0.138.0", "boundary": BOUNDARY}


def scholarly_context(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    package=copy.deepcopy(r["scholarlyPackage"])
    if not package:
        package={k:r[k] for k in ("studyId","projectId","title","methods","datasets","executions","models","analyses","figures","tables","evidence","claims","findings","limitations","reviews","reproductionPackages","manuscripts","nodes","edges","changeEvents","program")}
        package["packageId"] = f"package:{r['projectId']}"
        package["researchQuestion"] = r["question"]
    result=scholarly.readiness(package)
    return {"ok": bool(result.get("ok")), "version": VERSION, "projectId": r["projectId"], "scholarlyPackage": result, "sourceVersion": "0.139.0", "boundary": BOUNDARY}


def research_session(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    packet={"schema":"sc-lab-research-os-session/0.140.0","version":VERSION,"projectId":r["projectId"],"studyId":r["studyId"],"declaredPhase":r["phase"],"workspace":r["workspace"],"recordFingerprint":r["fingerprint"],"sourceAuthorityPreserved":True,"automaticScientificValidity":False}
    packet["fingerprint"]=_fp({k:v for k,v in packet.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"session":packet,"boundary":BOUNDARY}


def workspace_state(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    state={"projectId":r["projectId"],"activePhase":r["phase"],"workspace":r["workspace"],"availableCapabilities":[x[0] for x in CAPABILITIES],"persistenceScope":"project","scientificRecordsMutated":False}
    return {"ok":True,"version":VERSION,"workspaceState":state,"boundary":BOUNDARY}


def dependency_map(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    nodes=[{"id":name,"version":version,"type":"lab-capability"} for name,version in CAPABILITIES]
    edges=[]
    for a,b in zip(CAPABILITIES,CAPABILITIES[1:]): edges.append({"from":a[0],"to":b[0],"relationship":"can-feed-context"})
    return {"ok":True,"version":VERSION,"projectId":r["projectId"],"nodes":nodes,"edges":edges,"relationshipSemantics":"orchestration dependency only; not scientific causation","boundary":BOUNDARY}


def readiness(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    checks={
        "identity": bool(r["projectId"] and r["title"]),
        "question": bool(r["question"] or r["hypotheses"]),
        "methods": bool(r["methods"]),
        "dataOrEvidence": bool(r["datasets"] or r["evidence"]),
        "analysisOrExecution": bool(r["analyses"] or r["executions"] or r["models"]),
        "findings": bool(r["findings"]),
        "limitations": bool(r["limitations"]),
        "provenance": bool(r["provenance"] or r["nodes"] or r["edges"]),
    }
    return {"ok":True,"version":VERSION,"projectId":r["projectId"],"checks":checks,"administrativelyComplete":all(checks.values()),"scientificValidityCertified":False,"reproducibilityCertified":False,"publicationAccepted":False,"boundary":BOUNDARY}


def continuity(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    return {"ok":True,"version":VERSION,"projectId":r["projectId"],"bridges":[{"version":"0.137.0","capability":"living-analysis","active":bool(r["nodes"] or r["changeEvents"])},{"version":"0.138.0","capability":"research-program","active":bool(r["program"])},{"version":"0.139.0","capability":"scholarly-package","active":bool(r["scholarlyPackage"] or r["manuscripts"] or r["findings"])}],"sourceAuthorityPreserved":True,"boundary":BOUNDARY}


def snapshot(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    s={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"projectId":r["projectId"],"studyId":r["studyId"],"phase":r["phase"],"recordFingerprint":r["fingerprint"],"capabilityVersions":{n:v for n,v in CAPABILITIES},"capturedAt":_now(),"sourceAuthorityPreserved":True}
    s["fingerprint"]=_fp({k:v for k,v in s.items() if k not in {"fingerprint","capturedAt"}})
    return {"ok":True,"version":VERSION,"snapshot":s,"boundary":BOUNDARY}


def compare_snapshots(payload: dict) -> dict:
    left=_dict(payload.get("left") if isinstance(payload,dict) else None); right=_dict(payload.get("right") if isinstance(payload,dict) else None)
    if not left or not right: return {"ok":False,"version":VERSION,"error":"left and right snapshots are required","boundary":BOUNDARY}
    fields=("projectId","studyId","phase","recordFingerprint","fingerprint")
    changed=[f for f in fields if left.get(f)!=right.get(f)]
    return {"ok":True,"version":VERSION,"changed":bool(changed),"changedFields":changed,"scientificMeaningInferred":False,"boundary":BOUNDARY}


def handoff(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    packet={"schema":"sc-lab-research-os-handoff/0.140.0","version":VERSION,"projectId":r["projectId"],"studyId":r["studyId"],"recordFingerprint":r["fingerprint"],"phase":r["phase"],"target":_txt(_get(payload,"target","targetProduct"),128) or "project-workspace","sourceAuthorityPreserved":True,"automaticImport":False}
    packet["fingerprint"]=_fp({k:v for k,v in packet.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}


def publication_packet(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    package={k:r[k] for k in ("studyId","projectId","title","methods","datasets","executions","models","analyses","figures","tables","evidence","claims","findings","limitations","reviews","reproductionPackages","manuscripts","nodes","edges","changeEvents","program")}
    package["packageId"]=_txt(_get(r["scholarlyPackage"],"packageId","id"),512) or f"package:{r['projectId']}"; package["researchQuestion"]=r["question"]
    result=scholarly.export_plan(package)
    return {"ok":bool(result.get("ok")),"version":VERSION,"publicationPacket":result,"automaticPublicationAcceptance":False,"boundary":BOUNDARY}


def reproducibility_packet(payload: dict) -> dict:
    out=normalize(payload)
    if not out.get("ok"): return out
    r=out["record"]
    packet={"schema":"sc-lab-research-os-reproducibility/0.140.0","version":VERSION,"projectId":r["projectId"],"executionRefs":[_txt(_get(x,"ref","id"),512) for x in r["executions"] if isinstance(x,dict)],"reproductionPackages":r["reproductionPackages"],"recordFingerprint":r["fingerprint"],"reproducibleDoesNotEqualCorrect":True,"scientificValidityCertified":False}
    packet["fingerprint"]=_fp({k:v for k,v in packet.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"reproducibility":packet,"boundary":BOUNDARY}


def contract() -> dict:
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"routeCount":ROUTE_COUNT,"phases":list(PHASES),"capabilities":capability_catalog(),"boundary":BOUNDARY}


def policy() -> dict:
    return {"ok":True,"version":VERSION,"sourceAuthorityPreserved":True,"automaticPhaseAdvance":False,"automaticScientificValidity":False,"automaticReproducibilityCertification":False,"automaticEvidenceRanking":False,"automaticReviewResolution":False,"automaticPublicationAcceptance":False,"boundary":BOUNDARY}


def acceptance_report() -> dict:
    return {"ok":True,"version":VERSION,"scientificResearchOperatingSystem":True,"api_route_count":ROUTE_COUNT,"lifecycleOrchestration":True,"capabilityMatrix":True,"livingAnalysisBridge":True,"researchProgramBridge":True,"scholarlyPackageBridge":True,"researchSession":True,"workspaceState":True,"dependencyMap":True,"continuity":True,"deterministicSnapshots":True,"publicationPacket":True,"reproducibilityPacket":True,"backwardCompatibleV01390":True,"automaticPhaseAdvance":False,"automaticScientificValidity":False,"automaticPublicationAcceptance":False,"boundary":BOUNDARY}


def health() -> dict:
    return {"ok":True,"version":VERSION,"scientific_research_operating_system":True,"api_route_count":ROUTE_COUNT,"retained_versions":["0.137.0","0.138.0","0.139.0"],"boundary":BOUNDARY}


def release_gates() -> dict:
    return {"ok":True,"version":VERSION,"requiredRouteCount":ROUTE_COUNT,"requiresV01370":True,"requiresV01380":True,"requiresV01390":True,"sourceAuthorityPreserved":True,"automaticScientificValidity":False,"automaticPublicationAcceptance":False,"boundary":BOUNDARY}
