from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from typing import Any

VERSION = "0.67.0"
DESIGN_SCHEMA = "sc-lab-causal-design/0.67.0"
ESTIMATE_SCHEMA = "sc-lab-causal-estimate/0.67.0"
DIAGNOSTIC_SCHEMA = "sc-lab-causal-diagnostic/0.67.0"
PACKET_SCHEMA = "sc-lab-causal-inference-packet/0.67.0"

METHODS = {"matching", "weighting", "difference-in-differences", "interrupted-time-series", "regression-discontinuity"}
REVIEW_DECISIONS = {"accept-assumptions", "accept-with-qualification", "block", "reopen"}
ASSUMPTION_STATUSES = {"asserted", "qualified", "challenged", "unassessed"}
DIAGNOSTIC_STATES = {"pass", "caution", "fail", "inconclusive"}
EFFECT_METRICS = {"difference", "standardized-difference", "log-odds-ratio", "log-risk-ratio", "ratio", "slope-change", "level-change", "custom"}

METHOD_REQUIREMENTS = {
    "matching": {
        "assumptions": {"conditional-exchangeability", "overlap", "consistency"},
        "diagnostics": {"balance", "overlap", "sensitivity"},
    },
    "weighting": {
        "assumptions": {"conditional-exchangeability", "overlap", "consistency"},
        "diagnostics": {"balance", "overlap", "sensitivity"},
    },
    "difference-in-differences": {
        "assumptions": {"parallel-trends", "no-anticipation", "stable-composition"},
        "diagnostics": {"parallel-trends", "placebo", "sensitivity"},
    },
    "interrupted-time-series": {
        "assumptions": {"stable-pretrend", "no-concurrent-intervention", "stable-measurement"},
        "diagnostics": {"pretrend", "placebo", "sensitivity"},
    },
    "regression-discontinuity": {
        "assumptions": {"continuity-at-cutoff", "no-precise-manipulation", "local-comparability"},
        "diagnostics": {"bandwidth", "continuity", "manipulation", "sensitivity"},
    },
}

FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64", "individualdata", "participantdata",
    "treatmentvector", "outcomevector", "covariatematrix", "unitrecords", "microdata"
}


class CausalInferenceError(ValueError):
    pass


def _canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(v: Any) -> str:
    return hashlib.sha256(_canonical(v).encode("utf-8")).hexdigest()


def _text(v: Any, limit: int) -> str:
    return str(v or "").strip()[:limit]


def _id(v: Any, default: str = "") -> str:
    s = _text(v, 180)
    safe = "".join(ch for ch in s if ch.isalnum() or ch in "-_.:")
    return safe or default


def _ids(v: Any, limit: int = 100) -> list[str]:
    if not isinstance(v, list):
        return []
    out: list[str] = []
    for raw in v[:limit]:
        x = _id(raw)
        if x and x not in out:
            out.append(x)
    return out


def _finite(v: Any, name: str, allow_none: bool = False) -> float | None:
    if v in (None, "") and allow_none:
        return None
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise CausalInferenceError(f"{name} must be numeric.") from exc
    if not math.isfinite(x):
        raise CausalInferenceError(f"{name} must be finite.")
    return x


def _scan_forbidden(value: Any, path: str = "$") -> None:
    norm_forbidden = {k.replace("_", "").replace("-", "") for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            norm = str(key).replace("_", "").replace("-", "").lower()
            if norm in norm_forbidden:
                raise CausalInferenceError(f"Causal inference accepts governed aggregate metadata only; prohibited field at {path}.{key}.")
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{i}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True, "version": VERSION, "methods": sorted(METHODS),
        "explicitIdentificationAssumptionsRequired": True,
        "methodSpecificDiagnosticsRequired": True,
        "sensitivityAnalysisRequired": True,
        "humanCausalReviewRequired": True,
        "aggregateEstimatesOnly": True,
        "automaticCausalProofAuthorized": False,
        "automaticAssumptionSatisfactionAuthorized": False,
        "automaticPublicationAuthorized": False,
        "rawScientificDataAccepted": False,
        "participantLevelDataAccepted": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True, "status": "causal-inference-ready", "version": VERSION, "platformVersion": "1.0.0",
        "methods": sorted(METHODS), "reviewDecisions": sorted(REVIEW_DECISIONS),
        "humanCausalReviewRequired": True, "automaticCausalProof": False,
        "rawScientificDataAccepted": False, "participantLevelDataAccepted": False, "arbitraryCode": False,
    }


def _normalize_assumptions(v: Any) -> list[dict[str, Any]]:
    if not isinstance(v, list):
        return []
    out=[]
    for i, raw in enumerate(v[:50]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        kind=_id(raw.get("kind"), f"assumption-{i+1}")
        status=_text(raw.get("status"),40).lower() or "unassessed"
        if status not in ASSUMPTION_STATUSES: status="unassessed"
        row={"kind":kind,"status":status,"statement":_text(raw.get("statement"),3000),"note":_text(raw.get("note"),2000)}
        row["assumptionHash"]=_hash(row); out.append(row)
    return out


def _reviews(v: Any) -> list[dict[str, Any]]:
    if not isinstance(v, list): return []
    out=[]
    for i, raw in enumerate(v[:100]):
        if not isinstance(raw, dict): continue
        _scan_forbidden(raw)
        decision=_text(raw.get("decision"),80).lower()
        if decision not in REVIEW_DECISIONS: continue
        row={"id":_id(raw.get("id"),f"causal-review-{i+1}"),"decision":decision,"rationale":_text(raw.get("rationale"),3000),"reviewerRole":_text(raw.get("reviewerRole") or "researcher",80),"reviewedAt":_text(raw.get("reviewedAt"),64)}
        row["reviewHash"]=_hash(row); out.append(row)
    return out


def normalize_design(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw=payload if isinstance(payload,dict) else {}; _scan_forbidden(raw)
    method=_text(raw.get("method"),80).lower()
    if method not in METHODS: raise CausalInferenceError("Causal design method is not registered for v0.67.")
    design={
        "schema":DESIGN_SCHEMA,"version":VERSION,"id":_id(raw.get("id"),"causal-design-1"),
        "title":_text(raw.get("title") or "Causal design",600),"method":method,
        "studyId":_id(raw.get("studyId")),"linkedClaimIds":_ids(raw.get("linkedClaimIds"),100),
        "estimand":_text(raw.get("estimand"),3000),"treatmentDefinition":_text(raw.get("treatmentDefinition"),3000),
        "comparisonDefinition":_text(raw.get("comparisonDefinition"),3000),"outcomeDefinition":_text(raw.get("outcomeDefinition"),3000),
        "timeBoundary":_text(raw.get("timeBoundary"),2000),"assignmentMechanism":_text(raw.get("assignmentMechanism"),3000),
        "identificationAssumptions":_normalize_assumptions(raw.get("identificationAssumptions")),
        "methodNotes":_text(raw.get("methodNotes"),4000),"limitations":_text(raw.get("limitations"),4000),
        "reviewHistory":_reviews(raw.get("reviewHistory")),
    }
    design["designHash"]=_hash(design); return design


def normalize_estimate(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw=payload if isinstance(payload,dict) else {}; _scan_forbidden(raw)
    metric=_text(raw.get("effectMetric"),80).lower() or "custom"
    if metric not in EFFECT_METRICS: metric="custom"
    est=_finite(raw.get("estimate"),"estimate")
    se=_finite(raw.get("standardError"),"standardError",True)
    lo=_finite(raw.get("ciLower"),"ciLower",True); hi=_finite(raw.get("ciUpper"),"ciUpper",True)
    if se is not None and se <= 0: raise CausalInferenceError("standardError must be greater than zero.")
    if lo is not None and hi is not None and lo > hi: raise CausalInferenceError("ciLower cannot exceed ciUpper.")
    if se is None and (lo is None or hi is None): raise CausalInferenceError("Causal estimates require standardError or both confidence interval bounds.")
    row={"schema":ESTIMATE_SCHEMA,"version":VERSION,"id":_id(raw.get("id"),"causal-estimate-1"),"designId":_id(raw.get("designId")),"effectMetric":metric,"estimate":est,"standardError":se,"ciLower":lo,"ciUpper":hi,"confidenceLevel":_finite(raw.get("confidenceLevel") if raw.get("confidenceLevel") not in (None,"") else 0.95,"confidenceLevel"),"sampleSizeTreated":int(max(0,_finite(raw.get("sampleSizeTreated") or 0,"sampleSizeTreated"))),"sampleSizeComparison":int(max(0,_finite(raw.get("sampleSizeComparison") or 0,"sampleSizeComparison"))),"note":_text(raw.get("note"),3000)}
    if not row["designId"]: raise CausalInferenceError("Causal estimates require designId.")
    row["estimateHash"]=_hash(row); return row


def normalize_diagnostic(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw=payload if isinstance(payload,dict) else {}; _scan_forbidden(raw)
    kind=_id(raw.get("kind"))
    if not kind: raise CausalInferenceError("Causal diagnostic requires a kind.")
    state=_text(raw.get("state"),40).lower()
    if state not in DIAGNOSTIC_STATES: raise CausalInferenceError("Causal diagnostic state must be pass, caution, fail, or inconclusive.")
    row={"schema":DIAGNOSTIC_SCHEMA,"version":VERSION,"id":_id(raw.get("id"),"causal-diagnostic-1"),"designId":_id(raw.get("designId")),"kind":kind,"state":state,"value":_finite(raw.get("value"),"value",True),"threshold":_finite(raw.get("threshold"),"threshold",True),"evidenceRef":_id(raw.get("evidenceRef")),"note":_text(raw.get("note"),3000)}
    if not row["designId"]: raise CausalInferenceError("Causal diagnostics require designId.")
    row["diagnosticHash"]=_hash(row); return row


def record_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict) or not isinstance(payload.get("design"),dict) or not isinstance(payload.get("review"),dict):
        raise CausalInferenceError("Causal review requires design and review objects.")
    design=normalize_design(payload["design"]); review=payload["review"]; _scan_forbidden(review)
    decision=_text(review.get("decision"),80).lower()
    if decision not in REVIEW_DECISIONS: raise CausalInferenceError("Causal review decision is not recognized.")
    rationale=_text(review.get("rationale"),3000)
    if decision != "reopen" and len(rationale)<4: raise CausalInferenceError("Causal review decisions require a rationale.")
    if decision == "accept-with-qualification" and len(design.get("limitations") or "") < 8:
        raise CausalInferenceError("Qualified causal review requires explicit limitations.")
    row={"id":_id(review.get("id"),f"{design['id']}-review-{len(design['reviewHistory'])+1}"),"decision":decision,"rationale":rationale,"reviewerRole":_text(review.get("reviewerRole") or "researcher",80),"reviewedAt":_text(review.get("reviewedAt"),64)}
    row["reviewHash"]=_hash(row)
    base=deepcopy(design); base.pop("designHash",None); base["reviewHistory"]=[*design["reviewHistory"],row]
    return {"ok":True,"version":VERSION,"review":row,"design":normalize_design(base)}


def _latest_review(design: dict[str,Any]) -> str | None:
    rows=design.get("reviewHistory") or []
    return rows[-1]["decision"] if rows else None


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise CausalInferenceError("Causal evaluation requires design, estimates, and diagnostics.")
    allowed={"design","estimates","diagnostics"}; _scan_forbidden({k:v for k,v in payload.items() if k not in allowed})
    design=normalize_design(payload.get("design") if isinstance(payload.get("design"),dict) else {})
    estimates=[normalize_estimate(x) for x in (payload.get("estimates") or [])[:100] if isinstance(x,dict)] if isinstance(payload.get("estimates"),list) else []
    diagnostics=[normalize_diagnostic(x) for x in (payload.get("diagnostics") or [])[:200] if isinstance(x,dict)] if isinstance(payload.get("diagnostics"),list) else []
    estimates=[x for x in estimates if x["designId"]==design["id"]]
    diagnostics=[x for x in diagnostics if x["designId"]==design["id"]]
    req=METHOD_REQUIREMENTS[design["method"]]
    assumption_by={x["kind"]:x for x in design["identificationAssumptions"]}
    missing_assumptions=sorted(req["assumptions"]-set(assumption_by))
    challenged_assumptions=sorted(k for k,v in assumption_by.items() if k in req["assumptions"] and v["status"]=="challenged")
    unassessed_assumptions=sorted(k for k in req["assumptions"] if assumption_by.get(k,{}).get("status") in {None,"unassessed"})
    diag_by={}
    for d in diagnostics: diag_by.setdefault(d["kind"],[]).append(d)
    missing_diagnostics=sorted(k for k in req["diagnostics"] if k not in diag_by)
    failing=sorted({d["kind"] for d in diagnostics if d["kind"] in req["diagnostics"] and d["state"]=="fail"})
    cautions=sorted({d["kind"] for d in diagnostics if d["kind"] in req["diagnostics"] and d["state"] in {"caution","inconclusive"}})
    decision=_latest_review(design)
    if decision=="block": gate="blocked"
    elif missing_assumptions or unassessed_assumptions: gate="needs-identification-assumptions"
    elif challenged_assumptions: gate="assumption-challenge"
    elif not estimates: gate="needs-estimate"
    elif missing_diagnostics: gate="needs-diagnostics"
    elif failing: gate="diagnostic-failure"
    elif cautions and decision!="accept-with-qualification": gate="sensitivity-or-qualification-needed"
    elif decision in {None,"reopen"}: gate="needs-review"
    elif decision=="accept-with-qualification": gate="causal-estimate-bounded-with-qualification"
    elif decision=="accept-assumptions": gate="causal-estimate-bounded"
    else: gate="needs-review"
    result={"ok":True,"version":VERSION,"design":design,"gate":gate,"requiredAssumptionKinds":sorted(req["assumptions"]),"missingAssumptionKinds":missing_assumptions,"challengedAssumptionKinds":challenged_assumptions,"unassessedAssumptionKinds":unassessed_assumptions,"requiredDiagnosticKinds":sorted(req["diagnostics"]),"missingDiagnosticKinds":missing_diagnostics,"failingDiagnosticKinds":failing,"cautionDiagnosticKinds":cautions,"estimateRows":[{"id":e["id"],"effectMetric":e["effectMetric"],"estimate":e["estimate"],"standardError":e["standardError"],"ciLower":e["ciLower"],"ciUpper":e["ciUpper"],"estimateHash":e["estimateHash"]} for e in estimates],"diagnosticRows":[{"id":d["id"],"kind":d["kind"],"state":d["state"],"diagnosticHash":d["diagnosticHash"]} for d in diagnostics],"humanReviewDecision":decision,"humanCausalReviewRequired":True,"automaticCausalProof":False,"automaticAssumptionSatisfaction":False,"causalLanguageBoundary":"A bounded causal estimate is conditional on the stated design, assumptions, diagnostics, sensitivity analysis, and human review; it is not automatic proof of causation.","boundaries":policies()}
    result["evaluationHash"]=_hash(result); return result


def build_packet(payload: dict[str,Any]) -> dict[str,Any]:
    r=evaluate(payload)
    packet={"ok":True,"version":VERSION,"schema":PACKET_SCHEMA,"designId":r["design"]["id"],"designHash":r["design"]["designHash"],"method":r["design"]["method"],"gate":r["gate"],"evaluationHash":r["evaluationHash"],"linkedClaimIds":r["design"]["linkedClaimIds"],"studyId":r["design"]["studyId"],"estimand":r["design"]["estimand"],"assumptionHashes":[x["assumptionHash"] for x in r["design"]["identificationAssumptions"]],"estimateHashes":[x["estimateHash"] for x in r["estimateRows"]],"diagnosticHashes":[x["diagnosticHash"] for x in r["diagnosticRows"]],"humanReviewDecision":r["humanReviewDecision"],"automaticCausalProof":False,"rawScientificDataIncluded":False,"participantLevelDataIncluded":False,"causalLanguageBoundary":r["causalLanguageBoundary"]}
    packet["packetHash"]=_hash(packet); return packet


def verify_packet(payload: dict[str,Any]) -> dict[str,Any]:
    packet=payload.get("packet") if isinstance(payload,dict) and isinstance(payload.get("packet"),dict) else payload
    if not isinstance(packet,dict): raise CausalInferenceError("Causal packet is required.")
    supplied=_text(packet.get("packetHash"),64).lower(); base=deepcopy(packet); base.pop("packetHash",None); expected=_hash(base)
    return {"ok":bool(supplied and supplied==expected),"version":VERSION,"expectedPacketHash":expected,"suppliedPacketHash":supplied}
