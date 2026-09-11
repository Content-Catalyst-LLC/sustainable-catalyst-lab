from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import math
from typing import Any

from .carbon_mrv_registry_v0950 import METHODS, assess_readiness

LAB_RELEASE_VERSION = "0.97.0"
DOMAIN_VERSION = "0.14.0"
ENGINE_VERSION = "1.0.0"
PLAN_VERSION = "1.0.0"
PLAN_SCHEMA = "sc-carbon-nature-monitoring-plan/0.14.0"
VALIDATION_SCHEMA = "sc-carbon-nature-monitoring-plan-validation/0.14.0"
SAMPLE_SIZE_SCHEMA = "sc-carbon-nature-sample-size-plan/0.14.0"
ALLOCATION_SCHEMA = "sc-carbon-nature-stratified-allocation/0.14.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_REFS = 100
MAX_CAMPAIGNS = 50
MAX_STRATA = 100
MAX_DEPTHS = 30

STRATEGIES = {
    "simple-random": "Simple random sampling from an explicit sampling frame.",
    "systematic": "Systematic sampling using a user-defined interval/origin documented outside this calculator.",
    "stratified-random": "Random sampling within explicitly defined strata.",
    "repeated-location": "Repeated sampling at explicitly identified locations or sampling units.",
    "judgmental": "Purposive/judgmental sampling; statistical representativeness is not inferred.",
}


class CarbonMRVMonitoringV01400Error(ValueError):
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
            raise CarbonMRVMonitoringV01400Error(f"{label} is required")
        return None
    out = str(value).strip()
    if not out:
        if required:
            raise CarbonMRVMonitoringV01400Error(f"{label} is required")
        return None
    if len(out) > max_len:
        raise CarbonMRVMonitoringV01400Error(f"{label} exceeds {max_len} characters")
    return out


def _number(value: Any, label: str, required: bool = False, gt: float | None = None) -> float | None:
    if value in (None, ""):
        if required:
            raise CarbonMRVMonitoringV01400Error(f"{label} is required")
        return None
    if isinstance(value, bool):
        raise CarbonMRVMonitoringV01400Error(f"{label} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise CarbonMRVMonitoringV01400Error(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise CarbonMRVMonitoringV01400Error(f"{label} must be finite")
    if gt is not None and not out > gt:
        raise CarbonMRVMonitoringV01400Error(f"{label} must be greater than {gt}")
    return out


def _integer(value: Any, label: str, required: bool = False, minimum: int | None = None) -> int | None:
    n = _number(value, label, required)
    if n is None:
        return None
    if not n.is_integer():
        raise CarbonMRVMonitoringV01400Error(f"{label} must be an integer")
    out = int(n)
    if minimum is not None and out < minimum:
        raise CarbonMRVMonitoringV01400Error(f"{label} must be at least {minimum}")
    return out


def _refs(value: Any, label: str) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVMonitoringV01400Error(f"{label} must be an array")
    if len(value) > MAX_REFS:
        raise CarbonMRVMonitoringV01400Error(f"{label} may contain at most {MAX_REFS} values")
    out: list[str] = []
    for i, item in enumerate(value):
        ref = _text(item, f"{label}[{i}]", True, 240)
        assert ref is not None
        if ref not in out:
            out.append(ref)
    return out


def _date(value: Any, label: str) -> str | None:
    raw = _text(value, label, False, 32)
    if raw is None:
        return None
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError as exc:
        raise CarbonMRVMonitoringV01400Error(f"{label} must be an ISO date (YYYY-MM-DD)") from exc


def _guardrails() -> dict[str, bool]:
    return {
        "sampling_plan_is_not_proof_of_representativeness": True,
        "sample_size_is_planning_estimate_not_power_guarantee": True,
        "no_hidden_precision_or_variability_defaults": True,
        "no_automatic_coordinate_generation": True,
        "no_automatic_outlier_removal": True,
        "no_methodology_eligibility_determination": True,
        "no_verification_determination": True,
        "no_credit_eligibility_determination": True,
        "no_current_program_rule_assertion": True,
        "no_causal_attribution_inference": True,
    }


def sample_size_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVMonitoringV01400Error("sample-size request must be an object")
    expected_sd = _number(payload.get("expected_sd"), "expected_sd", True, 0)
    z_value = _number(payload.get("z_value"), "z_value", True, 0)
    assert expected_sd is not None and z_value is not None
    half_width = _number(payload.get("target_half_width"), "target_half_width", False, 0)
    rel_pct = _number(payload.get("relative_precision_percent"), "relative_precision_percent", False, 0)
    expected_mean = _number(payload.get("expected_mean"), "expected_mean", False)
    if half_width is not None and rel_pct is not None:
        raise CarbonMRVMonitoringV01400Error("provide target_half_width or relative_precision_percent, not both")
    if half_width is None and rel_pct is None:
        raise CarbonMRVMonitoringV01400Error("target_half_width or relative_precision_percent is required")
    if rel_pct is not None:
        if expected_mean is None or expected_mean == 0:
            raise CarbonMRVMonitoringV01400Error("expected_mean must be non-zero when relative_precision_percent is used")
        half_width = abs(expected_mean) * rel_pct / 100.0
    assert half_width is not None and half_width > 0
    n_unadjusted = int(math.ceil((z_value * expected_sd / half_width) ** 2))
    n_unadjusted = max(1, n_unadjusted)
    population_size = _integer(payload.get("population_size"), "population_size", False, 1)
    finite_population_applied = population_size is not None
    if population_size is not None:
        n_final = int(math.ceil(n_unadjusted / (1.0 + ((n_unadjusted - 1.0) / population_size))))
        n_final = min(population_size, max(1, n_final))
    else:
        n_final = n_unadjusted
    result = {
        "ok": True,
        "schema": SAMPLE_SIZE_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "calculation": "ceil((z_value * expected_sd / target_half_width)^2), with optional finite-population correction",
        "expected_sd": expected_sd,
        "z_value": z_value,
        "target_half_width": half_width,
        "relative_precision_percent": rel_pct,
        "expected_mean": expected_mean,
        "population_size": population_size,
        "unadjusted_sample_size": n_unadjusted,
        "recommended_planning_sample_size": n_final,
        "finite_population_correction_applied": finite_population_applied,
        "interpretation": "Planning estimate based only on the supplied variability and precision assumptions. It does not establish representativeness, statistical power for a specific hypothesis test, or methodology compliance.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def _strata(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CarbonMRVMonitoringV01400Error("strata must be a non-empty array")
    if len(value) > MAX_STRATA:
        raise CarbonMRVMonitoringV01400Error(f"strata may contain at most {MAX_STRATA} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CarbonMRVMonitoringV01400Error(f"strata[{i}] must be an object")
        key = _text(item.get("stratum_key"), f"strata[{i}].stratum_key", True, 120)
        assert key is not None
        if key in seen:
            raise CarbonMRVMonitoringV01400Error(f"duplicate stratum_key: {key}")
        seen.add(key)
        size = _number(item.get("size"), f"strata[{i}].size", True, 0)
        sd = _number(item.get("expected_sd"), f"strata[{i}].expected_sd", False, 0)
        out.append({"stratum_key": key, "size": size, "expected_sd": sd})
    return out


def allocate_strata(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVMonitoringV01400Error("allocation request must be an object")
    strata = _strata(payload.get("strata"))
    total_n = _integer(payload.get("total_sample_size"), "total_sample_size", True, 1)
    method = _text(payload.get("allocation_method"), "allocation_method", True, 40)
    assert total_n is not None and method is not None
    if total_n < len(strata):
        raise CarbonMRVMonitoringV01400Error("total_sample_size must be at least the number of strata so each stratum receives at least one sample")
    if method not in {"equal", "proportional", "neyman"}:
        raise CarbonMRVMonitoringV01400Error("allocation_method must be equal, proportional, or neyman")
    if method == "neyman" and any(s["expected_sd"] is None for s in strata):
        raise CarbonMRVMonitoringV01400Error("neyman allocation requires expected_sd for every stratum")

    if method == "equal":
        weights = [1.0 for _ in strata]
    elif method == "proportional":
        weights = [float(s["size"]) for s in strata]
    else:
        weights = [float(s["size"]) * float(s["expected_sd"]) for s in strata]
    if sum(weights) <= 0:
        raise CarbonMRVMonitoringV01400Error("allocation weights must sum to more than zero")

    raw = [total_n * w / sum(weights) for w in weights]
    floors = [int(math.floor(v)) for v in raw]
    allocations = list(floors)
    leftovers = total_n - sum(allocations)
    order = sorted(range(len(strata)), key=lambda i: (-(raw[i] - floors[i]), strata[i]["stratum_key"]))
    for i in order[:leftovers]:
        allocations[i] += 1
    # Because total_n >= number of strata, preserve at least one planned sample in each stratum.
    zeros = [i for i, n in enumerate(allocations) if n == 0]
    for zi in zeros:
        donors = sorted((i for i, n in enumerate(allocations) if n > 1), key=lambda i: (-allocations[i], strata[i]["stratum_key"]))
        if not donors:
            raise CarbonMRVMonitoringV01400Error("unable to allocate at least one sample to every stratum")
        allocations[donors[0]] -= 1
        allocations[zi] = 1

    rows = []
    for s, n, w in zip(strata, allocations, weights):
        rows.append({**s, "allocation_weight": w, "allocated_sample_size": n})
    result = {
        "ok": True,
        "schema": ALLOCATION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "allocation_method": method,
        "total_sample_size": total_n,
        "strata": rows,
        "interpretation": "Integer planning allocation across user-defined strata. Allocation does not establish frame quality, spatial coverage, independence, or representativeness.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def _campaigns(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVMonitoringV01400Error("campaigns must be an array")
    if len(value) > MAX_CAMPAIGNS:
        raise CarbonMRVMonitoringV01400Error(f"campaigns may contain at most {MAX_CAMPAIGNS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CarbonMRVMonitoringV01400Error(f"campaigns[{i}] must be an object")
        cid = _text(item.get("campaign_id"), f"campaigns[{i}].campaign_id", True, 160)
        purpose = _text(item.get("purpose"), f"campaigns[{i}].purpose", True, 240)
        start = _date(item.get("planned_start_date"), f"campaigns[{i}].planned_start_date")
        end = _date(item.get("planned_end_date"), f"campaigns[{i}].planned_end_date")
        if start and end and end < start:
            raise CarbonMRVMonitoringV01400Error(f"campaigns[{i}].planned_end_date must be on or after planned_start_date")
        assert cid is not None and purpose is not None
        if cid in seen:
            raise CarbonMRVMonitoringV01400Error(f"duplicate campaign_id: {cid}")
        seen.add(cid)
        out.append({"campaign_id": cid, "purpose": purpose, "planned_start_date": start, "planned_end_date": end, "repeat_of": _text(item.get("repeat_of"), f"campaigns[{i}].repeat_of", False, 160)})
    return out


def _depth_intervals(value: Any) -> list[dict[str, float]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVMonitoringV01400Error("depth_intervals_cm must be an array")
    if len(value) > MAX_DEPTHS:
        raise CarbonMRVMonitoringV01400Error(f"depth_intervals_cm may contain at most {MAX_DEPTHS} values")
    out = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CarbonMRVMonitoringV01400Error(f"depth_intervals_cm[{i}] must be an object")
        top = _number(item.get("top_cm"), f"depth_intervals_cm[{i}].top_cm", True)
        bottom = _number(item.get("bottom_cm"), f"depth_intervals_cm[{i}].bottom_cm", True)
        assert top is not None and bottom is not None
        if top < 0 or bottom <= top:
            raise CarbonMRVMonitoringV01400Error(f"depth_intervals_cm[{i}] must satisfy 0 <= top_cm < bottom_cm")
        out.append({"top_cm": top, "bottom_cm": bottom})
    ordered = sorted(out, key=lambda r: (r["top_cm"], r["bottom_cm"]))
    for a, b in zip(ordered, ordered[1:]):
        if b["top_cm"] < a["bottom_cm"]:
            raise CarbonMRVMonitoringV01400Error("depth_intervals_cm must not overlap")
    return ordered


def plan_template(method_key: str) -> dict[str, Any]:
    key = _text(method_key, "method_key", True, 120)
    assert key is not None
    if key not in METHODS:
        raise CarbonMRVMonitoringV01400Error(f"unknown MRV method: {key}", 404)
    method = METHODS[key]
    result = {
        "ok": True,
        "schema": "sc-carbon-nature-monitoring-plan-template/0.14.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "method_key": key,
        "method_title": method["title"],
        "library_methodology_key": method["library_methodology_key"],
        "required_inputs": list(method["required_inputs"]),
        "required_evidence": list(method["required_evidence"]),
        "strategy_options": [{"key": k, "description": v} for k, v in STRATEGIES.items()],
        "interpretation": "Template surfaces planning fields and method requirements; it does not choose a sampling strategy or assert that the resulting design satisfies an external methodology.",
        "guardrails": _guardrails(),
    }
    result["template_fingerprint"] = _hash({k: v for k, v in result.items() if k != "template_fingerprint"})
    return result


def _validation_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    missing_core = []
    for field in ("project_id", "protocol_id", "title", "objective", "spatial_boundary_ref", "sampling_frame_ref", "sample_unit"):
        if not plan.get(field):
            missing_core.append(field)
    design = plan["sampling_design"]
    if not design.get("strategy"):
        missing_core.append("sampling_design.strategy")
    if not plan.get("campaigns"):
        missing_core.append("campaigns")
    if not plan.get("methodology_refs"):
        missing_core.append("methodology_refs")
    if not plan.get("source_refs"):
        missing_core.append("source_refs")

    if plan["method_key"] in {"soc-direct-measurement", "soc-sampling-design"} and not design.get("depth_intervals_cm"):
        missing_core.append("sampling_design.depth_intervals_cm")
    if design.get("strategy") == "stratified-random" and not design.get("strata"):
        missing_core.append("sampling_design.strata")

    readiness = plan["method_documentation_readiness"]
    ready = not missing_core and readiness["documentation_ready"]
    result = {
        "ok": True,
        "schema": VALIDATION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "monitoring_plan_id": plan["monitoring_plan_id"],
        "method_key": plan["method_key"],
        "plan_readiness": "ready-for-internal-review" if ready else "draft-incomplete",
        "ready_for_internal_review": ready,
        "missing_core_fields": missing_core,
        "missing_method_inputs": list(readiness["missing_inputs"]),
        "missing_method_evidence": list(readiness["missing_evidence"]),
        "sampling_representativeness": None,
        "external_methodology_compliance": None,
        "verification_status": None,
        "credit_eligibility": None,
        "interpretation": "Internal-review readiness means required Sustainable Catalyst planning fields and named method documentation are populated. It is not proof of sampling representativeness, external methodology compliance, verification, or credit eligibility.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVMonitoringV01400Error("monitoring-plan request must be an object")
    method_key = _text(payload.get("method_key"), "method_key", True, 120)
    assert method_key is not None
    if method_key not in METHODS:
        raise CarbonMRVMonitoringV01400Error(f"unknown MRV method: {method_key}", 404)
    sampling = payload.get("sampling_design") or {}
    if not isinstance(sampling, dict):
        raise CarbonMRVMonitoringV01400Error("sampling_design must be an object")
    strategy = _text(sampling.get("strategy"), "sampling_design.strategy", False, 80)
    if strategy is not None and strategy not in STRATEGIES:
        raise CarbonMRVMonitoringV01400Error("sampling_design.strategy is not supported")

    sample_size = None
    if isinstance(sampling.get("sample_size_assumptions"), dict) and sampling.get("sample_size_assumptions"):
        sample_size = sample_size_plan(sampling["sample_size_assumptions"])
    allocation = None
    if isinstance(sampling.get("stratified_allocation"), dict) and sampling.get("stratified_allocation"):
        allocation = allocate_strata(sampling["stratified_allocation"])

    available_inputs = _refs(payload.get("available_inputs"), "available_inputs")
    available_evidence = _refs(payload.get("available_evidence"), "available_evidence")
    method_readiness = assess_readiness({
        "method_key": method_key,
        "available_inputs": available_inputs,
        "available_evidence": available_evidence,
        "methodology_refs": _refs(payload.get("methodology_refs"), "methodology_refs"),
        "source_refs": _refs(payload.get("source_refs"), "source_refs"),
    })
    project_id = _text(payload.get("project_id"), "project_id", False, 240)
    protocol_id = _text(payload.get("protocol_id"), "protocol_id", False, 240)
    title = _text(payload.get("title"), "title", False, 240)
    objective = _text(payload.get("objective"), "objective", False, 3000)
    boundary = _text(payload.get("spatial_boundary_ref"), "spatial_boundary_ref", False, 240)
    seed = [project_id, protocol_id, method_key, title, boundary, strategy]
    plan_id = _text(payload.get("monitoring_plan_id") or f"monitoring-plan:{_hash(seed)[:16]}", "monitoring_plan_id", True, 240)
    assert plan_id is not None

    plan = {
        "schema": PLAN_SCHEMA,
        "monitoring_plan_id": plan_id,
        "plan_version": PLAN_VERSION,
        "status": "draft",
        "project_id": project_id,
        "protocol_id": protocol_id,
        "title": title,
        "objective": objective,
        "method_key": method_key,
        "method_title": METHODS[method_key]["title"],
        "library_methodology_key": METHODS[method_key]["library_methodology_key"],
        "spatial_boundary_ref": boundary,
        "campaigns": _campaigns(payload.get("campaigns")),
        "sampling_frame_ref": _text(payload.get("sampling_frame_ref"), "sampling_frame_ref", False, 240),
        "sample_unit": _text(payload.get("sample_unit"), "sample_unit", False, 240),
        "sampling_design": {
            "strategy": strategy,
            "strategy_description": STRATEGIES.get(strategy) if strategy else None,
            "target_population": _text(sampling.get("target_population"), "sampling_design.target_population", False, 1200),
            "depth_intervals_cm": _depth_intervals(sampling.get("depth_intervals_cm")),
            "field_qc_steps": _refs(sampling.get("field_qc_steps"), "sampling_design.field_qc_steps"),
            "laboratory_qc_steps": _refs(sampling.get("laboratory_qc_steps"), "sampling_design.laboratory_qc_steps"),
            "sample_size_plan": sample_size,
            "stratified_allocation": allocation,
            "strata": _strata(sampling.get("strata")) if sampling.get("strata") else [],
        },
        "available_inputs": method_readiness["available_inputs"],
        "available_evidence": method_readiness["available_evidence"],
        "methodology_refs": method_readiness["methodology_refs"],
        "source_refs": method_readiness["source_refs"],
        "method_documentation_readiness": method_readiness,
        "interpretation": "Governed monitoring and sampling plan assembled from explicit project, method, campaign, frame, sampling, and evidence inputs. No sampling locations or scientific assumptions are invented.",
        "guardrails": _guardrails(),
    }
    plan["plan_fingerprint"] = _hash({k: v for k, v in plan.items() if k != "plan_fingerprint"})
    validation = _validation_from_plan(plan)
    plan["status"] = "ready-for-internal-review" if validation["ready_for_internal_review"] else "draft"
    plan["plan_fingerprint"] = _hash({k: v for k, v in plan.items() if k != "plan_fingerprint"})
    validation = _validation_from_plan(plan)
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "plan": plan, "validation": validation}


def validate_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVMonitoringV01400Error("validation request must be an object")
    if isinstance(payload.get("plan"), dict):
        p = payload["plan"]
        if p.get("schema") != PLAN_SCHEMA:
            raise CarbonMRVMonitoringV01400Error(f"plan.schema must be {PLAN_SCHEMA}")
        sampling = p.get("sampling_design") or {}
        source = {
            "monitoring_plan_id": p.get("monitoring_plan_id"), "project_id": p.get("project_id"), "protocol_id": p.get("protocol_id"),
            "title": p.get("title"), "objective": p.get("objective"), "method_key": p.get("method_key"), "spatial_boundary_ref": p.get("spatial_boundary_ref"),
            "campaigns": p.get("campaigns"), "sampling_frame_ref": p.get("sampling_frame_ref"), "sample_unit": p.get("sample_unit"),
            "sampling_design": {"strategy": sampling.get("strategy"), "target_population": sampling.get("target_population"), "depth_intervals_cm": sampling.get("depth_intervals_cm"), "field_qc_steps": sampling.get("field_qc_steps"), "laboratory_qc_steps": sampling.get("laboratory_qc_steps"), "strata": sampling.get("strata")},
            "available_inputs": p.get("available_inputs"), "available_evidence": p.get("available_evidence"), "methodology_refs": p.get("methodology_refs"), "source_refs": p.get("source_refs"),
        }
        return build_plan(source)["validation"]
    return build_plan(payload)["validation"]


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVMonitoringV01400Error("project packet request must be an object")
    source = payload.get("plan") if isinstance(payload.get("plan"), dict) else payload
    built = build_plan(source)
    plan, validation = built["plan"], built["validation"]
    if not plan.get("project_id"):
        raise CarbonMRVMonitoringV01400Error("project_id is required for a project packet")
    actor = _text(payload.get("actor_ref") or "actor:lab-user", "actor_ref", True, 240)
    assert actor is not None
    object_id = _text(payload.get("object_id") or f"monitoring-record:plan-{plan['plan_fingerprint'][:16]}", "object_id", True, 240)
    assert object_id is not None
    provenance_id = f"provenance:monitoring-plan-{plan['plan_fingerprint'][:16]}"
    obj = {
        "object_id": object_id, "object_type": "monitoring-record", "project_id": plan["project_id"], "version": "1.0.0", "status": "draft",
        "payload": {"record_type": "monitoring-plan", "plan_version": PLAN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "domain_version": DOMAIN_VERSION, "monitoring_plan_id": plan["monitoring_plan_id"], "protocol_id": plan.get("protocol_id"), "method_key": plan["method_key"], "plan_status": plan["status"], "ready_for_internal_review": validation["ready_for_internal_review"], "plan_fingerprint": plan["plan_fingerprint"], "validation_fingerprint": validation["result_fingerprint"], "guardrails": plan["guardrails"]},
        "source_refs": plan["source_refs"], "evidence_refs": plan["source_refs"], "methodology_refs": plan["methodology_refs"], "provenance_refs": [provenance_id],
    }
    event = {"provenance_id": provenance_id, "event_type": "created", "object_id": object_id, "actor_ref": actor, "details": {"record_type": "monitoring-plan", "monitoring_plan_id": plan["monitoring_plan_id"], "method_key": plan["method_key"], "ready_for_internal_review": validation["ready_for_internal_review"]}}
    packet = {"schema": PROJECT_PACKET_SCHEMA, "objects": [obj], "provenance": [event], "links": ([{"relationship": "monitoring-for", "from": object_id, "to": plan["protocol_id"]}] if plan.get("protocol_id") else [])}
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "packet": packet, "plan": plan, "validation": validation, "packet_fingerprint": _hash(packet)}


def policies() -> dict[str, Any]:
    return {
        "ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION,
        "capabilities": {"monitoring_plan_builder": True, "campaign_schedule_design": True, "sampling_strategy_documentation": True, "precision_based_sample_size_planning": True, "finite_population_correction": True, "stratified_equal_allocation": True, "stratified_proportional_allocation": True, "stratified_neyman_allocation": True, "soc_depth_interval_governance": True, "method_documentation_gap_analysis": True, "carbon_project_monitoring_record_handoff": True, "deterministic_fingerprints": True},
        "limits": {"max_refs_per_field": MAX_REFS, "max_campaigns": MAX_CAMPAIGNS, "max_strata": MAX_STRATA, "max_depth_intervals": MAX_DEPTHS},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "plan_schema": PLAN_SCHEMA, "validation_schema": VALIDATION_SCHEMA, "sample_size_schema": SAMPLE_SIZE_SCHEMA, "allocation_schema": ALLOCATION_SCHEMA, "method_keys": list(METHODS), "strategy_keys": list(STRATEGIES), "allocation_methods": ["equal", "proportional", "neyman"], "plan_status_values": ["draft", "ready-for-internal-review"]}


def health() -> dict[str, Any]:
    return {"ok": True, "status": "monitoring-plan-sampling-designer-ready", "service": "Sustainable Catalyst Lab Monitoring Plan & Sampling Designer", "lab_release_version": LAB_RELEASE_VERSION, "domain_version": DOMAIN_VERSION, "engine_version": ENGINE_VERSION, "plan_version": PLAN_VERSION, "method_registry_count": len(METHODS), "strategy_count": len(STRATEGIES), "guardrails": _guardrails()}
