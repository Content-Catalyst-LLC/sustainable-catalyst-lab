from __future__ import annotations

from hashlib import sha256
import json
import math
from typing import Any

LAB_RELEASE_VERSION = "0.98.0"
DOMAIN_VERSION = "0.15.0"
ENGINE_VERSION = "1.0.0"
ASSESSMENT_VERSION = "1.0.0"
BUDGET_SCHEMA = "sc-carbon-nature-mrv-uncertainty-budget/0.15.0"
DETECTION_SCHEMA = "sc-carbon-nature-mrv-change-detection/0.15.0"
SAMPLE_SIZE_SCHEMA = "sc-carbon-nature-mrv-detection-sample-size/0.15.0"
ASSESSMENT_SCHEMA = "sc-carbon-nature-mrv-uncertainty-assessment/0.15.0"
VALIDATION_SCHEMA = "sc-carbon-nature-mrv-uncertainty-assessment-validation/0.15.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_COMPONENTS = 100
MAX_REFS = 100


class CarbonMRVUncertaintyV01500Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _text(value: Any, label: str, required: bool = False, max_len: int = 1200) -> str | None:
    if value is None:
        if required:
            raise CarbonMRVUncertaintyV01500Error(f"{label} is required")
        return None
    out = str(value).strip()
    if not out:
        if required:
            raise CarbonMRVUncertaintyV01500Error(f"{label} is required")
        return None
    if len(out) > max_len:
        raise CarbonMRVUncertaintyV01500Error(f"{label} exceeds {max_len} characters")
    return out


def _number(value: Any, label: str, required: bool = False, gt: float | None = None, ge: float | None = None) -> float | None:
    if value in (None, ""):
        if required:
            raise CarbonMRVUncertaintyV01500Error(f"{label} is required")
        return None
    if isinstance(value, bool):
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be finite")
    if gt is not None and not out > gt:
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be greater than {gt}")
    if ge is not None and out < ge:
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be at least {ge}")
    return out


def _integer(value: Any, label: str, required: bool = False, minimum: int | None = None) -> int | None:
    n = _number(value, label, required)
    if n is None:
        return None
    if not n.is_integer():
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be an integer")
    out = int(n)
    if minimum is not None and out < minimum:
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be at least {minimum}")
    return out


def _refs(value: Any, label: str) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVUncertaintyV01500Error(f"{label} must be an array")
    if len(value) > MAX_REFS:
        raise CarbonMRVUncertaintyV01500Error(f"{label} may contain at most {MAX_REFS} values")
    out: list[str] = []
    for i, item in enumerate(value):
        ref = _text(item, f"{label}[{i}]", True, 240)
        assert ref is not None
        if ref not in out:
            out.append(ref)
    return out


def _guardrails() -> dict[str, bool]:
    return {
        "no_hidden_confidence_or_coverage_defaults": True,
        "uncertainty_budget_requires_explicit_components": True,
        "correlation_requires_explicit_covariance": True,
        "detection_threshold_is_not_verification": True,
        "sample_size_is_planning_estimate_not_power_guarantee": True,
        "uncertainty_is_not_automatically_a_deduction_factor": True,
        "no_methodology_eligibility_determination": True,
        "no_verification_determination": True,
        "no_credit_eligibility_determination": True,
        "no_causal_attribution_inference": True,
    }


def _components(value: Any, estimate: float) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CarbonMRVUncertaintyV01500Error("components must be a non-empty array")
    if len(value) > MAX_COMPONENTS:
        raise CarbonMRVUncertaintyV01500Error(f"components may contain at most {MAX_COMPONENTS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CarbonMRVUncertaintyV01500Error(f"components[{i}] must be an object")
        key = _text(item.get("component_key"), f"components[{i}].component_key", True, 120)
        assert key is not None
        if key in seen:
            raise CarbonMRVUncertaintyV01500Error(f"duplicate component_key: {key}")
        seen.add(key)
        absolute = _number(item.get("standard_uncertainty"), f"components[{i}].standard_uncertainty", False, ge=0)
        relative = _number(item.get("relative_percent"), f"components[{i}].relative_percent", False, ge=0)
        if absolute is not None and relative is not None:
            raise CarbonMRVUncertaintyV01500Error(f"components[{i}] must provide standard_uncertainty or relative_percent, not both")
        if absolute is None and relative is None:
            raise CarbonMRVUncertaintyV01500Error(f"components[{i}] requires standard_uncertainty or relative_percent")
        std = absolute if absolute is not None else abs(estimate) * float(relative) / 100.0
        out.append({
            "component_key": key,
            "description": _text(item.get("description"), f"components[{i}].description", False, 500),
            "standard_uncertainty": std,
            "relative_percent_input": relative,
            "source_ref": _text(item.get("source_ref"), f"components[{i}].source_ref", False, 240),
        })
    return out


def uncertainty_budget(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVUncertaintyV01500Error("uncertainty-budget request must be an object")
    estimate = _number(payload.get("estimate"), "estimate", True)
    unit = _text(payload.get("unit"), "unit", True, 80)
    assert estimate is not None and unit is not None
    components = _components(payload.get("components"), estimate)
    covariance_terms = payload.get("covariance_terms") or []
    if not isinstance(covariance_terms, list):
        raise CarbonMRVUncertaintyV01500Error("covariance_terms must be an array")
    known = {x["component_key"] for x in components}
    cov_sum = 0.0
    normalized_cov = []
    for i, item in enumerate(covariance_terms):
        if not isinstance(item, dict):
            raise CarbonMRVUncertaintyV01500Error(f"covariance_terms[{i}] must be an object")
        a = _text(item.get("component_a"), f"covariance_terms[{i}].component_a", True, 120)
        b = _text(item.get("component_b"), f"covariance_terms[{i}].component_b", True, 120)
        cov = _number(item.get("covariance"), f"covariance_terms[{i}].covariance", True)
        assert a and b and cov is not None
        if a not in known or b not in known or a == b:
            raise CarbonMRVUncertaintyV01500Error(f"covariance_terms[{i}] must reference two distinct known components")
        cov_sum += cov
        normalized_cov.append({"component_a": a, "component_b": b, "covariance": cov})
    variance = sum(float(x["standard_uncertainty"]) ** 2 for x in components) + 2.0 * cov_sum
    if variance < -1e-12:
        raise CarbonMRVUncertaintyV01500Error("covariance terms produce a negative combined variance")
    variance = max(0.0, variance)
    combined = math.sqrt(variance)
    k = _number(payload.get("coverage_factor"), "coverage_factor", False, gt=0)
    expanded = combined * k if k is not None else None
    result = {
        "ok": True,
        "schema": BUDGET_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "estimate": estimate,
        "unit": unit,
        "components": components,
        "covariance_terms": normalized_cov,
        "combined_standard_uncertainty": combined,
        "combined_relative_percent": (combined / abs(estimate) * 100.0) if estimate != 0 else None,
        "coverage_factor": k,
        "expanded_uncertainty": expanded,
        "expanded_interval": ([estimate - expanded, estimate + expanded] if expanded is not None else None),
        "interpretation": "Combined standard uncertainty is calculated from explicit standard-uncertainty components and any explicit covariance terms. Expanded uncertainty is only reported when a coverage factor is supplied.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def change_detection(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVUncertaintyV01500Error("change-detection request must be an object")
    design = _text(payload.get("design"), "design", True, 40)
    change = _number(payload.get("observed_change"), "observed_change", True)
    critical = _number(payload.get("critical_value"), "critical_value", True, gt=0)
    assert design and change is not None and critical is not None
    if design == "paired":
        sd = _number(payload.get("sd_change"), "sd_change", True, gt=0)
        n = _integer(payload.get("n_pairs"), "n_pairs", True, 2)
        assert sd is not None and n is not None
        se = sd / math.sqrt(n)
        detail = {"sd_change": sd, "n_pairs": n}
    elif design == "independent":
        bsd = _number(payload.get("baseline_sd"), "baseline_sd", True, gt=0)
        fsd = _number(payload.get("followup_sd"), "followup_sd", True, gt=0)
        nb = _integer(payload.get("n_baseline"), "n_baseline", True, 2)
        nf = _integer(payload.get("n_followup"), "n_followup", True, 2)
        assert bsd is not None and fsd is not None and nb is not None and nf is not None
        se = math.sqrt((bsd * bsd / nb) + (fsd * fsd / nf))
        detail = {"baseline_sd": bsd, "followup_sd": fsd, "n_baseline": nb, "n_followup": nf}
    else:
        raise CarbonMRVUncertaintyV01500Error("design must be paired or independent")
    threshold = critical * se
    detected = abs(change) >= threshold
    result = {
        "ok": True,
        "schema": DETECTION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "design": design,
        "observed_change": change,
        "critical_value": critical,
        "standard_error_change": se,
        "detection_threshold": threshold,
        "change_detected_at_supplied_threshold": detected,
        "signal_to_threshold_ratio": (abs(change) / threshold if threshold > 0 else None),
        **detail,
        "interpretation": "Detection compares the absolute observed change with a threshold derived from the supplied critical value and sampling variability. It is a statistical signal check, not verification, additionality, or credit issuance.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def required_sample_size(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVUncertaintyV01500Error("detection sample-size request must be an object")
    design = _text(payload.get("design"), "design", True, 40)
    mdd = _number(payload.get("minimum_detectable_change"), "minimum_detectable_change", True, gt=0)
    z_alpha = _number(payload.get("z_alpha"), "z_alpha", True, gt=0)
    z_power = _number(payload.get("z_power"), "z_power", True, ge=0)
    assert design and mdd is not None and z_alpha is not None and z_power is not None
    zsum = z_alpha + z_power
    if design == "paired":
        sd = _number(payload.get("expected_sd_change"), "expected_sd_change", True, gt=0)
        assert sd is not None
        n = int(math.ceil(((zsum * sd) / mdd) ** 2))
        result_n = {"recommended_pairs": max(2, n), "expected_sd_change": sd}
    elif design == "independent-equal":
        bsd = _number(payload.get("baseline_sd"), "baseline_sd", True, gt=0)
        fsd = _number(payload.get("followup_sd"), "followup_sd", True, gt=0)
        assert bsd is not None and fsd is not None
        n = int(math.ceil((zsum * zsum * (bsd * bsd + fsd * fsd)) / (mdd * mdd)))
        result_n = {"recommended_per_period": max(2, n), "baseline_sd": bsd, "followup_sd": fsd}
    else:
        raise CarbonMRVUncertaintyV01500Error("design must be paired or independent-equal")
    result = {
        "ok": True,
        "schema": SAMPLE_SIZE_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "design": design,
        "minimum_detectable_change": mdd,
        "z_alpha": z_alpha,
        "z_power": z_power,
        **result_n,
        "interpretation": "Normal-approximation planning estimate using explicitly supplied alpha-side and power-side critical values. It does not guarantee achieved power or methodology compliance.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def _validation_from_assessment(assessment: dict[str, Any]) -> dict[str, Any]:
    missing = []
    for field in ("project_id", "title", "metric", "unit", "monitoring_plan_ref"):
        if not assessment.get(field):
            missing.append(field)
    if assessment.get("uncertainty_budget") is None:
        missing.append("uncertainty_budget")
    if assessment.get("change_detection") is None:
        missing.append("change_detection")
    if not assessment.get("source_refs"):
        missing.append("source_refs")
    ready = not missing
    result = {
        "ok": True,
        "schema": VALIDATION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "assessment_id": assessment["assessment_id"],
        "assessment_readiness": "ready-for-internal-review" if ready else "draft-incomplete",
        "ready_for_internal_review": ready,
        "missing_core_fields": missing,
        "external_methodology_compliance": None,
        "verification_status": None,
        "credit_eligibility": None,
        "deduction_factor": None,
        "interpretation": "Internal-review readiness means the uncertainty budget, detection calculation, provenance references, and core identifiers are documented. It is not external methodology compliance, verification, or credit eligibility.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_assessment(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVUncertaintyV01500Error("uncertainty-assessment request must be an object")
    project_id = _text(payload.get("project_id"), "project_id", False, 240)
    title = _text(payload.get("title"), "title", False, 240)
    metric = _text(payload.get("metric"), "metric", False, 240)
    unit = _text(payload.get("unit"), "unit", False, 80)
    monitoring_plan_ref = _text(payload.get("monitoring_plan_ref"), "monitoring_plan_ref", False, 240)
    protocol_ref = _text(payload.get("protocol_ref"), "protocol_ref", False, 240)
    budget_payload = payload.get("uncertainty_budget")
    detection_payload = payload.get("change_detection")
    planning_payload = payload.get("detection_sample_size")
    budget = uncertainty_budget(budget_payload) if isinstance(budget_payload, dict) and budget_payload else None
    detection = change_detection(detection_payload) if isinstance(detection_payload, dict) and detection_payload else None
    planning = required_sample_size(planning_payload) if isinstance(planning_payload, dict) and planning_payload else None
    assessment_id = _text(payload.get("assessment_id") or f"mrv-uncertainty:{_hash([project_id,title,metric,monitoring_plan_ref])[:16]}", "assessment_id", True, 240)
    assert assessment_id is not None
    assessment = {
        "schema": ASSESSMENT_SCHEMA,
        "assessment_id": assessment_id,
        "assessment_version": ASSESSMENT_VERSION,
        "status": "draft",
        "project_id": project_id,
        "title": title,
        "metric": metric,
        "unit": unit,
        "monitoring_plan_ref": monitoring_plan_ref,
        "protocol_ref": protocol_ref,
        "uncertainty_budget": budget,
        "change_detection": detection,
        "detection_sample_size": planning,
        "methodology_refs": _refs(payload.get("methodology_refs"), "methodology_refs"),
        "source_refs": _refs(payload.get("source_refs"), "source_refs"),
        "interpretation": "Governed MRV uncertainty and detectability assessment assembled from explicit uncertainty components, sampling variability, critical values, and provenance references.",
        "guardrails": _guardrails(),
    }
    assessment["assessment_fingerprint"] = _hash({k: v for k, v in assessment.items() if k != "assessment_fingerprint"})
    validation = _validation_from_assessment(assessment)
    assessment["status"] = "ready-for-internal-review" if validation["ready_for_internal_review"] else "draft"
    assessment["assessment_fingerprint"] = _hash({k: v for k, v in assessment.items() if k != "assessment_fingerprint"})
    validation = _validation_from_assessment(assessment)
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "assessment": assessment, "validation": validation}


def validate_assessment(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVUncertaintyV01500Error("validation request must be an object")
    if isinstance(payload.get("assessment"), dict):
        a = payload["assessment"]
        if a.get("schema") != ASSESSMENT_SCHEMA:
            raise CarbonMRVUncertaintyV01500Error(f"assessment.schema must be {ASSESSMENT_SCHEMA}")
        source = {
            "assessment_id": a.get("assessment_id"), "project_id": a.get("project_id"), "title": a.get("title"), "metric": a.get("metric"), "unit": a.get("unit"),
            "monitoring_plan_ref": a.get("monitoring_plan_ref"), "protocol_ref": a.get("protocol_ref"),
            "uncertainty_budget": ({"estimate": a["uncertainty_budget"]["estimate"], "unit": a["uncertainty_budget"]["unit"], "components": [{"component_key": x["component_key"], "standard_uncertainty": x["standard_uncertainty"], "description": x.get("description"), "source_ref": x.get("source_ref")} for x in a["uncertainty_budget"]["components"]], "covariance_terms": a["uncertainty_budget"].get("covariance_terms", []), "coverage_factor": a["uncertainty_budget"].get("coverage_factor")} if isinstance(a.get("uncertainty_budget"), dict) else None),
            "change_detection": ({k: v for k, v in a["change_detection"].items() if k in {"design","observed_change","critical_value","sd_change","n_pairs","baseline_sd","followup_sd","n_baseline","n_followup"}} if isinstance(a.get("change_detection"), dict) else None),
            "methodology_refs": a.get("methodology_refs"), "source_refs": a.get("source_refs"),
        }
        return build_assessment(source)["validation"]
    return build_assessment(payload)["validation"]


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVUncertaintyV01500Error("project packet request must be an object")
    source = payload.get("assessment") if isinstance(payload.get("assessment"), dict) else payload
    if isinstance(source, dict) and source.get("schema") == ASSESSMENT_SCHEMA:
        validation = _validation_from_assessment(source)
        assessment = source
    else:
        built = build_assessment(source)
        assessment, validation = built["assessment"], built["validation"]
    if not assessment.get("project_id"):
        raise CarbonMRVUncertaintyV01500Error("project_id is required for a project packet")
    actor = _text(payload.get("actor_ref") or "actor:lab-user", "actor_ref", True, 240)
    object_id = _text(payload.get("object_id") or f"model-run:mrv-uncertainty-{assessment['assessment_fingerprint'][:16]}", "object_id", True, 240)
    assert actor and object_id
    provenance_id = f"provenance:mrv-uncertainty-{assessment['assessment_fingerprint'][:16]}"
    obj = {
        "object_id": object_id, "object_type": "model-run", "project_id": assessment["project_id"], "version": "1.0.0", "status": "draft",
        "payload": {"record_type": "mrv-uncertainty-detection-assessment", "lab_release_version": LAB_RELEASE_VERSION, "domain_version": DOMAIN_VERSION, "assessment_id": assessment["assessment_id"], "monitoring_plan_ref": assessment.get("monitoring_plan_ref"), "ready_for_internal_review": validation["ready_for_internal_review"], "assessment_fingerprint": assessment["assessment_fingerprint"], "validation_fingerprint": validation["result_fingerprint"], "guardrails": assessment["guardrails"]},
        "source_refs": assessment["source_refs"], "evidence_refs": assessment["source_refs"], "methodology_refs": assessment["methodology_refs"], "provenance_refs": [provenance_id],
    }
    event = {"provenance_id": provenance_id, "event_type": "modeled", "object_id": object_id, "actor_ref": actor, "details": {"record_type": "mrv-uncertainty-detection-assessment", "assessment_id": assessment["assessment_id"], "ready_for_internal_review": validation["ready_for_internal_review"]}}
    links = []
    if assessment.get("monitoring_plan_ref"):
        links.append({"relationship": "derived-from", "from": object_id, "to": assessment["monitoring_plan_ref"]})
    if assessment.get("protocol_ref"):
        links.append({"relationship": "derived-from", "from": object_id, "to": assessment["protocol_ref"]})
    packet = {"schema": PROJECT_PACKET_SCHEMA, "objects": [obj], "provenance": [event], "links": links}
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "packet": packet, "assessment": assessment, "validation": validation, "packet_fingerprint": _hash(packet)}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "capabilities": {
            "explicit_uncertainty_budget": True,
            "relative_and_absolute_uncertainty_components": True,
            "explicit_covariance_terms": True,
            "expanded_uncertainty_with_user_coverage_factor": True,
            "paired_change_detection": True,
            "independent_change_detection": True,
            "detection_sample_size_planning": True,
            "monitoring_plan_linkage": True,
            "carbon_project_model_run_handoff": True,
            "deterministic_fingerprints": True,
        },
        "limits": {"max_uncertainty_components": MAX_COMPONENTS, "max_refs_per_field": MAX_REFS},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "budget_schema": BUDGET_SCHEMA,
        "detection_schema": DETECTION_SCHEMA,
        "sample_size_schema": SAMPLE_SIZE_SCHEMA,
        "assessment_schema": ASSESSMENT_SCHEMA,
        "validation_schema": VALIDATION_SCHEMA,
        "detection_designs": ["paired", "independent"],
        "sample_size_designs": ["paired", "independent-equal"],
        "assessment_status_values": ["draft", "ready-for-internal-review"],
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "mrv-uncertainty-detection-engine-ready",
        "service": "Sustainable Catalyst Lab MRV Uncertainty & Detection Engine",
        "lab_release_version": LAB_RELEASE_VERSION,
        "domain_version": DOMAIN_VERSION,
        "engine_version": ENGINE_VERSION,
        "assessment_version": ASSESSMENT_VERSION,
        "guardrails": _guardrails(),
    }
