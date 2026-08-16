from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from typing import Any

VERSION = "0.68.0"
MODEL_SCHEMA = "sc-lab-hierarchical-model/0.68.0"
UNIT_SCHEMA = "sc-lab-hierarchical-unit-estimate/0.68.0"
FIT_SCHEMA = "sc-lab-hierarchical-fit/0.68.0"
PACKET_SCHEMA = "sc-lab-hierarchical-modeling-packet/0.68.0"

MODEL_TYPES = {"hierarchical-normal", "random-intercept", "random-slope", "cross-study-pooling", "cross-study-meta-regression"}
REVIEW_DECISIONS = {"accept-within-scope", "accept-with-qualification", "block", "reopen"}
EFFECT_METRICS = {"difference", "standardized-difference", "log-odds-ratio", "log-risk-ratio", "fisher-z", "slope", "level", "custom"}
LEVEL_TYPES = {"group", "site", "study", "region", "cohort", "institution", "custom"}

FORBIDDEN_KEYS = {
    "rows", "rawrows", "rawdata", "datasetpayload", "datasetspayload", "inputs", "records",
    "credentials", "credential", "secrets", "secret", "password", "token", "apikey", "api_key",
    "authorization", "cookie", "privatekey", "private_key", "callback", "callbackurl", "webhook",
    "python", "javascript", "shell", "sql", "code", "fulltext", "full_text", "pdfbytes", "pdf_bytes",
    "attachmentbytes", "attachment_bytes", "binary", "base64", "individualdata", "participantdata",
    "outcomevector", "predictormatrix", "covariatematrix", "unitrecords", "microdata", "participantrecords"
}


class HierarchicalModelingError(ValueError):
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
        raise HierarchicalModelingError(f"{name} must be numeric.") from exc
    if not math.isfinite(x):
        raise HierarchicalModelingError(f"{name} must be finite.")
    return x


def _scan_forbidden(value: Any, path: str = "$") -> None:
    norm_forbidden = {k.replace("_", "").replace("-", "") for k in FORBIDDEN_KEYS}
    if isinstance(value, dict):
        for key, child in value.items():
            norm = str(key).replace("_", "").replace("-", "").lower()
            if norm in norm_forbidden:
                raise HierarchicalModelingError(
                    f"Hierarchical modeling accepts governed aggregate metadata only; prohibited field at {path}.{key}."
                )
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{i}]")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "modelTypes": sorted(MODEL_TYPES),
        "aggregateUnitEstimatesOnly": True,
        "partialPoolingExplicit": True,
        "heterogeneityReported": True,
        "shrinkageDiagnosticsReported": True,
        "humanModelReviewRequired": True,
        "populationBoundaryRequired": True,
        "generalizationBoundaryRequired": True,
        "automaticGeneralizabilityAuthorized": False,
        "automaticEcologicalInferenceAuthorized": False,
        "automaticCausalProofAuthorized": False,
        "automaticModelSelectionAuthorized": False,
        "participantLevelDataAccepted": False,
        "rawScientificDataAccepted": False,
        "networkFetchDuringEvaluationAuthorized": False,
        "arbitraryCodeExecutionAuthorized": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "hierarchical-modeling-ready",
        "version": VERSION,
        "platformVersion": "1.0.0",
        "modelTypes": sorted(MODEL_TYPES),
        "reviewDecisions": sorted(REVIEW_DECISIONS),
        "aggregateUnitEstimatesOnly": True,
        "humanModelReviewRequired": True,
        "automaticGeneralizability": False,
        "participantLevelDataAccepted": False,
        "arbitraryCode": False,
    }


def _reviews(v: Any) -> list[dict[str, Any]]:
    if not isinstance(v, list):
        return []
    out = []
    for i, raw in enumerate(v[:100]):
        if not isinstance(raw, dict):
            continue
        _scan_forbidden(raw)
        decision = _text(raw.get("decision"), 80).lower()
        if decision not in REVIEW_DECISIONS:
            continue
        row = {
            "id": _id(raw.get("id"), f"hierarchical-review-{i+1}"),
            "decision": decision,
            "rationale": _text(raw.get("rationale"), 3000),
            "reviewerRole": _text(raw.get("reviewerRole") or "researcher", 80),
            "reviewedAt": _text(raw.get("reviewedAt"), 64),
        }
        row["reviewHash"] = _hash(row)
        out.append(row)
    return out


def normalize_model(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    model_type = _text(raw.get("modelType"), 80).lower()
    if model_type not in MODEL_TYPES:
        raise HierarchicalModelingError("Hierarchical model type is not registered for v0.68.")
    level_type = _text(raw.get("levelType"), 80).lower() or "group"
    if level_type not in LEVEL_TYPES:
        level_type = "custom"
    metric = _text(raw.get("effectMetric"), 80).lower() or "custom"
    if metric not in EFFECT_METRICS:
        metric = "custom"
    model = {
        "schema": MODEL_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "hierarchical-model-1"),
        "title": _text(raw.get("title") or "Hierarchical model", 600),
        "modelType": model_type,
        "levelType": level_type,
        "effectMetric": metric,
        "studyId": _id(raw.get("studyId")),
        "linkedClaimIds": _ids(raw.get("linkedClaimIds"), 100),
        "linkedSynthesisIds": _ids(raw.get("linkedSynthesisIds"), 100),
        "outcomeDefinition": _text(raw.get("outcomeDefinition"), 3000),
        "moderatorName": _id(raw.get("moderatorName")),
        "populationBoundary": _text(raw.get("populationBoundary"), 3000),
        "generalizationBoundary": _text(raw.get("generalizationBoundary"), 4000),
        "modelingAssumptions": _text(raw.get("modelingAssumptions"), 5000),
        "limitations": _text(raw.get("limitations"), 5000),
        "reviewHistory": _reviews(raw.get("reviewHistory")),
    }
    if model_type in {"random-slope", "cross-study-meta-regression"} and not model["moderatorName"]:
        raise HierarchicalModelingError("Random-slope and cross-study meta-regression models require moderatorName.")
    model["modelHash"] = _hash(model)
    return model


def normalize_unit(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    _scan_forbidden(raw)
    estimate = _finite(raw.get("estimate"), "estimate")
    se = _finite(raw.get("standardError"), "standardError", True)
    lo = _finite(raw.get("ciLower"), "ciLower", True)
    hi = _finite(raw.get("ciUpper"), "ciUpper", True)
    if se is None:
        if lo is None or hi is None:
            raise HierarchicalModelingError("Unit estimates require standardError or both confidence interval bounds.")
        if lo > hi:
            raise HierarchicalModelingError("ciLower cannot exceed ciUpper.")
        se = (hi - lo) / (2.0 * 1.96)
    if se <= 0:
        raise HierarchicalModelingError("standardError must be greater than zero.")
    moderator = _finite(raw.get("moderatorValue"), "moderatorValue", True)
    row = {
        "schema": UNIT_SCHEMA,
        "version": VERSION,
        "id": _id(raw.get("id"), "hierarchical-unit-1"),
        "modelId": _id(raw.get("modelId")),
        "unitId": _id(raw.get("unitId"), _id(raw.get("id"), "unit-1")),
        "clusterId": _id(raw.get("clusterId")),
        "sourceRef": _id(raw.get("sourceRef")),
        "estimate": estimate,
        "standardError": se,
        "ciLower": lo,
        "ciUpper": hi,
        "moderatorValue": moderator,
        "sampleSize": int(max(0, _finite(raw.get("sampleSize") or 0, "sampleSize"))),
        "note": _text(raw.get("note"), 3000),
    }
    if not row["modelId"]:
        raise HierarchicalModelingError("Unit estimates require modelId.")
    row["unitHash"] = _hash(row)
    return row


def record_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("model"), dict) or not isinstance(payload.get("review"), dict):
        raise HierarchicalModelingError("Hierarchical review requires model and review objects.")
    model = normalize_model(payload["model"])
    review = payload["review"]
    _scan_forbidden(review)
    decision = _text(review.get("decision"), 80).lower()
    if decision not in REVIEW_DECISIONS:
        raise HierarchicalModelingError("Hierarchical review decision is not recognized.")
    rationale = _text(review.get("rationale"), 3000)
    if decision != "reopen" and len(rationale) < 4:
        raise HierarchicalModelingError("Hierarchical review decisions require a rationale.")
    if decision == "accept-with-qualification" and len(model.get("limitations") or "") < 8:
        raise HierarchicalModelingError("Qualified multilevel review requires explicit limitations.")
    row = {
        "id": _id(review.get("id"), f"{model['id']}-review-{len(model['reviewHistory'])+1}"),
        "decision": decision,
        "rationale": rationale,
        "reviewerRole": _text(review.get("reviewerRole") or "researcher", 80),
        "reviewedAt": _text(review.get("reviewedAt"), 64),
    }
    row["reviewHash"] = _hash(row)
    base = deepcopy(model)
    base.pop("modelHash", None)
    base["reviewHistory"] = [*model["reviewHistory"], row]
    return {"ok": True, "version": VERSION, "review": row, "model": normalize_model(base)}


def _latest_review(model: dict[str, Any]) -> str | None:
    rows = model.get("reviewHistory") or []
    return rows[-1]["decision"] if rows else None


def _random_effects(values: list[dict[str, Any]]) -> dict[str, Any]:
    if len(values) < 2:
        raise HierarchicalModelingError("Random-effects pooling requires at least two aggregate unit estimates.")
    ys = [float(r["estimate"]) for r in values]
    vs = [float(r["standardError"]) ** 2 for r in values]
    wf = [1.0 / v for v in vs]
    sw = sum(wf)
    mu_fixed = sum(w * y for w, y in zip(wf, ys)) / sw
    q = sum(w * (y - mu_fixed) ** 2 for w, y in zip(wf, ys))
    df = len(values) - 1
    c = sw - sum(w * w for w in wf) / sw
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    wr = [1.0 / (v + tau2) for v in vs]
    swr = sum(wr)
    mu = sum(w * y for w, y in zip(wr, ys)) / swr
    se_mu = math.sqrt(1.0 / swr)
    i2 = max(0.0, ((q - df) / q) * 100.0) if q > 0 else 0.0
    shrinkage = []
    for row, y, v in zip(values, ys, vs):
        obs_weight = tau2 / (tau2 + v) if tau2 > 0 else 0.0
        pooled_weight = 1.0 - obs_weight
        shrunken = obs_weight * y + pooled_weight * mu
        post_var = (tau2 * v / (tau2 + v)) if tau2 > 0 else 0.0
        shrinkage.append({
            "id": row["id"], "unitId": row["unitId"], "clusterId": row.get("clusterId") or "",
            "observedEstimate": y, "shrunkenEstimate": shrunken,
            "observedWeight": obs_weight, "pooledWeight": pooled_weight,
            "posteriorSEApprox": math.sqrt(max(0.0, post_var)), "unitHash": row["unitHash"],
        })
    return {
        "pooledEstimate": mu, "pooledSE": se_mu, "ciLower": mu - 1.96 * se_mu, "ciUpper": mu + 1.96 * se_mu,
        "fixedEffectEstimate": mu_fixed, "q": q, "df": df, "i2Percent": i2, "tauSquared": tau2,
        "unitCount": len(values), "shrinkageRows": shrinkage,
    }


def _fit_wls(values: list[dict[str, Any]], use_random: bool = True) -> dict[str, Any]:
    if len(values) < 4:
        raise HierarchicalModelingError("Random-slope/meta-regression modeling requires at least four unit estimates.")
    if any(r.get("moderatorValue") is None for r in values):
        raise HierarchicalModelingError("All unit estimates require moderatorValue for random-slope/meta-regression models.")
    xs = [float(r["moderatorValue"]) for r in values]
    if max(xs) - min(xs) <= 1e-12:
        raise HierarchicalModelingError("Moderator values must vary for random-slope/meta-regression models.")
    ys = [float(r["estimate"]) for r in values]
    vs = [float(r["standardError"]) ** 2 for r in values]

    def regress(weights: list[float]) -> tuple[float, float, float, float, float]:
        sw = sum(weights); sx = sum(w*x for w,x in zip(weights,xs)); sy = sum(w*y for w,y in zip(weights,ys))
        sxx = sum(w*x*x for w,x in zip(weights,xs)); sxy = sum(w*x*y for w,x,y in zip(weights,xs,ys))
        det = sw*sxx - sx*sx
        if det <= 1e-18:
            raise HierarchicalModelingError("Moderator design is singular or too weak for random-slope/meta-regression fitting.")
        slope = (sw*sxy - sx*sy) / det
        intercept = (sy - slope*sx) / sw
        return intercept, slope, sw, sx, sxx

    wf = [1.0/v for v in vs]
    b0f, b1f, sw, sx, sxx = regress(wf)
    q = sum(w*(y-(b0f+b1f*x))**2 for w,x,y in zip(wf,xs,ys))
    df = len(values)-2
    sw2 = sum(w*w for w in wf); sw2x = sum((w*w)*x for w,x in zip(wf,xs)); sw2xx = sum((w*w)*x*x for w,x in zip(wf,xs))
    det = sw*sxx-sx*sx
    inv00, inv01, inv11 = sxx/det, -sx/det, sw/det
    trace = inv00*sw2 + 2.0*inv01*sw2x + inv11*sw2xx
    c = sw - trace
    tau2 = max(0.0, (q-df)/c) if use_random and c > 0 else 0.0
    wr = [1.0/(v+tau2) for v in vs]
    b0, b1, swr, sxr, sxxr = regress(wr)
    detr = swr*sxxr-sxr*sxr
    se0 = math.sqrt(sxxr/detr); se1 = math.sqrt(swr/detr)
    i2 = max(0.0, ((q-df)/q)*100.0) if q > 0 else 0.0
    residuals=[]
    for row,x,y in zip(values,xs,ys):
        pred=b0+b1*x
        residuals.append({"id":row["id"],"unitId":row["unitId"],"moderatorValue":x,"observedEstimate":y,"predictedEstimate":pred,"residual":y-pred,"unitHash":row["unitHash"]})
    return {
        "intercept": b0, "interceptSE": se0, "interceptCiLower": b0-1.96*se0, "interceptCiUpper": b0+1.96*se0,
        "slope": b1, "slopeSE": se1, "slopeCiLower": b1-1.96*se1, "slopeCiUpper": b1+1.96*se1,
        "moderatorMin": min(xs), "moderatorMax": max(xs), "qResidual": q, "dfResidual": df, "i2Percent": i2,
        "tauSquared": tau2, "unitCount": len(values), "residualRows": residuals,
    }


def _fit_random_intercept(values: list[dict[str, Any]]) -> dict[str, Any]:
    clusters: dict[str, list[dict[str, Any]]] = {}
    for row in values:
        cid = row.get("clusterId") or ""
        if not cid:
            raise HierarchicalModelingError("Random-intercept models require clusterId on every unit estimate.")
        clusters.setdefault(cid, []).append(row)
    if len(clusters) < 2:
        raise HierarchicalModelingError("Random-intercept models require at least two clusters.")
    cluster_rows=[]
    for cid, rows in sorted(clusters.items()):
        ws=[1.0/(r["standardError"]**2) for r in rows]
        sw=sum(ws); mu=sum(w*r["estimate"] for w,r in zip(ws,rows))/sw; se=math.sqrt(1.0/sw)
        base={"schema":UNIT_SCHEMA,"version":VERSION,"id":f"cluster:{cid}","modelId":rows[0]["modelId"],"unitId":cid,"clusterId":cid,"sourceRef":"","estimate":mu,"standardError":se,"ciLower":None,"ciUpper":None,"moderatorValue":None,"sampleSize":sum(r.get("sampleSize",0) for r in rows),"note":"Aggregate cluster estimate"}
        base["unitHash"]=_hash(base); cluster_rows.append(base)
    fit=_random_effects(cluster_rows)
    fit["clusterCount"]=len(cluster_rows); fit["originalUnitCount"]=len(values); fit["clusterEstimates"]=[{"clusterId":r["clusterId"],"estimate":r["estimate"],"standardError":r["standardError"],"unitHash":r["unitHash"]} for r in cluster_rows]
    return fit


def fit_model(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HierarchicalModelingError("Hierarchical fit requires model and unitEstimates.")
    allowed={"model","unitEstimates"}
    _scan_forbidden({k:v for k,v in payload.items() if k not in allowed})
    model=normalize_model(payload.get("model") if isinstance(payload.get("model"),dict) else {})
    units=[normalize_unit(x) for x in (payload.get("unitEstimates") or [])[:300] if isinstance(x,dict)] if isinstance(payload.get("unitEstimates"),list) else []
    units=[x for x in units if x["modelId"]==model["id"]]
    if len(units)<2:
        raise HierarchicalModelingError("Hierarchical modeling requires at least two aggregate unit estimates.")
    cross_study=model["modelType"] in {"cross-study-pooling","cross-study-meta-regression"}
    missing_sources=[u["id"] for u in units if cross_study and not u.get("sourceRef")]
    if missing_sources:
        raise HierarchicalModelingError("Cross-study models require sourceRef on every unit estimate.")
    if model["modelType"]=="random-intercept":
        fit=_fit_random_intercept(units)
        fit_kind="random-intercept"
    elif model["modelType"] in {"random-slope","cross-study-meta-regression"}:
        fit=_fit_wls(units,True); fit_kind="random-slope-meta-regression"
    else:
        fit=_random_effects(units); fit_kind="hierarchical-normal-partial-pooling"
    result={"ok":True,"version":VERSION,"schema":FIT_SCHEMA,"modelId":model["id"],"modelType":model["modelType"],"fitKind":fit_kind,"effectMetric":model["effectMetric"],"unitHashes":[u["unitHash"] for u in units],**fit}
    result["fitHash"]=_hash(result)
    return result


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HierarchicalModelingError("Hierarchical evaluation requires model and unitEstimates.")
    model=normalize_model(payload.get("model") if isinstance(payload.get("model"),dict) else {})
    try:
        fit=fit_model({"model":model,"unitEstimates":payload.get("unitEstimates") or []})
        fit_error=""
    except HierarchicalModelingError as exc:
        fit=None; fit_error=str(exc)
    units=[normalize_unit(x) for x in (payload.get("unitEstimates") or [])[:300] if isinstance(x,dict)] if isinstance(payload.get("unitEstimates"),list) else []
    units=[x for x in units if x["modelId"]==model["id"]]
    decision=_latest_review(model)
    high_heterogeneity=bool(fit and float(fit.get("i2Percent") or 0.0)>=75.0)
    severe_heterogeneity=bool(fit and float(fit.get("i2Percent") or 0.0)>=90.0)
    boundary_missing=len(model.get("populationBoundary") or "")<8 or len(model.get("generalizationBoundary") or "")<8
    if decision=="block": gate="blocked"
    elif len(units)<2: gate="needs-units"
    elif fit is None:
        low=fit_error.lower()
        if "sourceref" in low: gate="needs-study-provenance"
        elif "cluster" in low: gate="weak-group-structure"
        elif "moderator" in low or "singular" in low: gate="needs-moderator-variation"
        else: gate="model-fit-blocked"
    elif boundary_missing: gate="needs-generalization-boundary"
    elif high_heterogeneity and decision!="accept-with-qualification": gate="heterogeneity-caution"
    elif decision in {None,"reopen"}: gate="needs-review"
    elif decision=="accept-with-qualification": gate="multilevel-estimate-bounded-with-qualification"
    elif decision=="accept-within-scope": gate="multilevel-estimate-bounded"
    else: gate="needs-review"
    result={
        "ok":True,"version":VERSION,"model":model,"gate":gate,"fit":fit,"fitError":fit_error,
        "unitCount":len(units),"unitRows":[{"id":u["id"],"unitId":u["unitId"],"clusterId":u["clusterId"],"sourceRef":u["sourceRef"],"estimate":u["estimate"],"standardError":u["standardError"],"moderatorValue":u["moderatorValue"],"unitHash":u["unitHash"]} for u in units],
        "highHeterogeneity":high_heterogeneity,"severeHeterogeneity":severe_heterogeneity,
        "humanReviewDecision":decision,"humanModelReviewRequired":True,"automaticGeneralizability":False,
        "generalizationBoundary":"Partial pooling summarizes modeled variation among the recorded units/studies. It does not establish universal population transportability, ecological inference, or causal proof beyond the stated scope.",
        "boundaries":policies(),
    }
    result["evaluationHash"]=_hash(result)
    return result


def build_packet(payload: dict[str, Any]) -> dict[str, Any]:
    r=evaluate(payload)
    packet={
        "ok":True,"version":VERSION,"schema":PACKET_SCHEMA,"modelId":r["model"]["id"],"modelHash":r["model"]["modelHash"],
        "modelType":r["model"]["modelType"],"effectMetric":r["model"]["effectMetric"],"gate":r["gate"],
        "evaluationHash":r["evaluationHash"],"fitHash":r["fit"].get("fitHash") if r.get("fit") else "",
        "unitHashes":[u["unitHash"] for u in r["unitRows"]],"linkedClaimIds":r["model"]["linkedClaimIds"],
        "linkedSynthesisIds":r["model"]["linkedSynthesisIds"],"studyId":r["model"]["studyId"],
        "populationBoundary":r["model"]["populationBoundary"],"generalizationBoundary":r["model"]["generalizationBoundary"],
        "humanReviewDecision":r["humanReviewDecision"],"automaticGeneralizability":False,"automaticCausalProof":False,
        "rawScientificDataIncluded":False,"participantLevelDataIncluded":False,"generalizationLanguageBoundary":r["generalizationBoundary"],
    }
    packet["packetHash"]=_hash(packet)
    return packet


def verify_packet(payload: dict[str, Any]) -> dict[str, Any]:
    packet=payload.get("packet") if isinstance(payload,dict) and isinstance(payload.get("packet"),dict) else payload
    if not isinstance(packet,dict):
        raise HierarchicalModelingError("Hierarchical modeling packet is required.")
    supplied=_text(packet.get("packetHash"),64).lower(); base=deepcopy(packet); base.pop("packetHash",None); expected=_hash(base)
    return {"ok":bool(supplied and supplied==expected),"version":VERSION,"expectedPacketHash":expected,"suppliedPacketHash":supplied}
