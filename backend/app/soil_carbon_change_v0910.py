from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

from .soil_organic_carbon_v0890 import calculate_profile_stock

LAB_RELEASE_VERSION = "0.91.0"
DOMAIN_VERSION = "0.8.0"
ENGINE_VERSION = "1.0.0"
MODEL_VERSION = "0.8.0"
MODEL_NAME = "Sustainable Catalyst matched fixed-depth SOC stock-change model"
CHANGE_SCHEMA = "sc-carbon-nature-soc-stock-change/0.8.0"
SERIES_SCHEMA = "sc-carbon-nature-soc-stock-change-series/0.8.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_SERIES_POINTS = 100
MAX_AREA_HA = 10_000_000.0
SECONDS_PER_DAY = 86400.0
DAYS_PER_YEAR = 365.2425
SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,159}$")


class SoilCarbonChangeV0800Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _number(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise SoilCarbonChangeV0800Error(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise SoilCarbonChangeV0800Error(f"{label} must be finite")
    return out


def _optional_text(value: Any, max_len: int = 1000) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > max_len:
        raise SoilCarbonChangeV0800Error(f"text value exceeds {max_len} characters")
    return text


def _safe_id(value: Any, label: str, required: bool = False) -> str | None:
    text = _optional_text(value, 160)
    if not text:
        if required:
            raise SoilCarbonChangeV0800Error(f"{label} is required")
        return None
    if not SAFE_ID.fullmatch(text):
        raise SoilCarbonChangeV0800Error(
            f"{label} must use letters, numbers, dot, underscore, colon, or hyphen"
        )
    return text


def _string_list(value: Any, label: str, limit: int = 100) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > limit:
        raise SoilCarbonChangeV0800Error(f"{label} must be a list with at most {limit} entries")
    out: list[str] = []
    for item in value:
        text = _optional_text(item, 300)
        if text and text not in out:
            out.append(text)
    return out


def _time(value: Any, label: str) -> tuple[str, datetime]:
    text = _optional_text(value, 80)
    if not text:
        raise SoilCarbonChangeV0800Error(f"{label} is required")
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SoilCarbonChangeV0800Error(f"{label} must be an ISO-8601 date or timestamp") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return text, dt.astimezone(timezone.utc)


def _optional_area(payload: dict[str, Any], baseline: dict[str, Any], followup: dict[str, Any]) -> float | None:
    requested = payload.get("area_ha")
    baseline_area = baseline.get("area_ha")
    followup_area = followup.get("area_ha")
    supplied = [x for x in (requested, baseline_area, followup_area) if x not in (None, "")]
    if not supplied:
        return None
    values = [_number(x, "area_ha") for x in supplied]
    if any(x <= 0 or x > MAX_AREA_HA for x in values):
        raise SoilCarbonChangeV0800Error(f"area_ha must be >0 and <= {MAX_AREA_HA:g}")
    reference = values[0]
    if any(abs(x - reference) > 1e-9 for x in values[1:]):
        raise SoilCarbonChangeV0800Error("baseline, follow-up, and comparison area_ha values must agree")
    return reference


def _depth_signature(profile_result: dict[str, Any]) -> list[dict[str, float]]:
    return [
        {
            "top_depth_cm": float(row["layer"]["top_depth_cm"]),
            "bottom_depth_cm": float(row["layer"]["bottom_depth_cm"]),
        }
        for row in profile_result["layers"]
    ]


def _profiles_match(baseline: dict[str, Any], followup: dict[str, Any]) -> tuple[bool, list[str]]:
    a, b = _depth_signature(baseline), _depth_signature(followup)
    issues: list[str] = []
    if len(a) != len(b):
        issues.append("layer-count-mismatch")
    else:
        for i, (left, right) in enumerate(zip(a, b)):
            if (
                abs(left["top_depth_cm"] - right["top_depth_cm"]) > 1e-9
                or abs(left["bottom_depth_cm"] - right["bottom_depth_cm"]) > 1e-9
            ):
                issues.append(f"depth-interval-mismatch:{i+1}")
    if baseline["depth"]["contiguous"] != followup["depth"]["contiguous"]:
        issues.append("depth-contiguity-mismatch")
    if baseline["depth"]["gaps"] != followup["depth"]["gaps"]:
        issues.append("depth-gap-mismatch")
    return not issues, issues


def _profile_payload(payload: Any, label: str, area_ha: float | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonChangeV0800Error(f"{label} must be an object")
    row = dict(payload)
    if area_ha is not None and row.get("area_ha") in (None, ""):
        row["area_ha"] = area_ha
    try:
        return calculate_profile_stock(row)
    except Exception as exc:
        # Preserve the v0.6 calculator's detailed message without leaking implementation type.
        detail = getattr(exc, "detail", str(exc))
        raise SoilCarbonChangeV0800Error(f"{label} is invalid: {detail}") from exc


def compare_profiles(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonChangeV0800Error("stock-change request must be an object")
    comparison_id = _safe_id(payload.get("comparison_id") or "comparison:soc-change", "comparison_id", True)
    spatial_unit_id = _safe_id(payload.get("spatial_unit_id"), "spatial_unit_id", True)
    baseline_at_raw, baseline_at = _time(payload.get("baseline_at"), "baseline_at")
    followup_at_raw, followup_at = _time(payload.get("followup_at"), "followup_at")
    elapsed_seconds = (followup_at - baseline_at).total_seconds()
    if elapsed_seconds <= 0:
        raise SoilCarbonChangeV0800Error("followup_at must be later than baseline_at")

    requested_area = None
    if payload.get("area_ha") not in (None, ""):
        requested_area = _number(payload.get("area_ha"), "area_ha")
        if requested_area <= 0 or requested_area > MAX_AREA_HA:
            raise SoilCarbonChangeV0800Error(f"area_ha must be >0 and <= {MAX_AREA_HA:g}")

    baseline = _profile_payload(payload.get("baseline_profile"), "baseline_profile", requested_area)
    followup = _profile_payload(payload.get("followup_profile"), "followup_profile", requested_area)
    area = _optional_area(payload, baseline, followup)

    matched, issues = _profiles_match(baseline, followup)
    if not matched:
        raise SoilCarbonChangeV0800Error(
            "baseline and follow-up profiles must use identical normalized fixed-depth intervals; "
            + ", ".join(issues)
        )

    baseline_stock = float(baseline["soc_stock_Mg_C_ha"])
    followup_stock = float(followup["soc_stock_Mg_C_ha"])
    change = followup_stock - baseline_stock
    elapsed_days = elapsed_seconds / SECONDS_PER_DAY
    elapsed_years = elapsed_days / DAYS_PER_YEAR
    annualized = change / elapsed_years
    relative = (change / baseline_stock * 100.0) if baseline_stock != 0 else None
    epsilon = 1e-12
    direction = "increase" if change > epsilon else "decrease" if change < -epsilon else "no-arithmetic-change"

    source_refs = sorted(set(
        _string_list(payload.get("source_refs"), "source_refs")
        + list(baseline.get("source_refs") or [])
        + list(followup.get("source_refs") or [])
    ))
    baseline_ref = _safe_id(payload.get("baseline_ref"), "baseline_ref")
    intervention_ref = _safe_id(payload.get("intervention_ref"), "intervention_ref")

    result: dict[str, Any] = {
        "ok": True,
        "schema": CHANGE_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "model": {
            "name": MODEL_NAME,
            "version": MODEL_VERSION,
            "basis": "matched-fixed-depth-fine-earth-corrected",
            "annualization_basis_days_per_year": DAYS_PER_YEAR,
        },
        "comparison_id": comparison_id,
        "spatial_unit_id": spatial_unit_id,
        "baseline_at": baseline_at_raw,
        "followup_at": followup_at_raw,
        "elapsed_days": elapsed_days,
        "elapsed_years": elapsed_years,
        "depth_match": {
            "policy": "exact-normalized-intervals",
            "matched": True,
            "intervals": _depth_signature(baseline),
            "baseline_contiguous": baseline["depth"]["contiguous"],
            "followup_contiguous": followup["depth"]["contiguous"],
        },
        "baseline": {
            "profile_id": baseline.get("profile_id"),
            "soc_stock_Mg_C_ha": baseline_stock,
            "profile_result_fingerprint": baseline["result_fingerprint"],
        },
        "followup": {
            "profile_id": followup.get("profile_id"),
            "soc_stock_Mg_C_ha": followup_stock,
            "profile_result_fingerprint": followup["result_fingerprint"],
        },
        "stock_change_Mg_C_ha": change,
        "annualized_stock_change_Mg_C_ha_yr": annualized,
        "relative_stock_change_percent": relative,
        "direction": direction,
        "gross_stock_increase_Mg_C_ha": max(change, 0.0),
        "gross_stock_loss_Mg_C_ha": max(-change, 0.0),
        "area_ha": area,
        "stock_change_Mg_C_total": change * area if area is not None else None,
        "annualized_stock_change_Mg_C_total_yr": annualized * area if area is not None else None,
        "baseline_ref": baseline_ref,
        "intervention_ref": intervention_ref,
        "source_refs": source_refs,
        "interpretation": {
            "positive_change_is_candidate_gross_soc_accumulation": change > epsilon,
            "intervention_attribution_established": False,
            "additionality_established": False,
            "net_ghg_benefit_established": False,
            "verified_sequestration_established": False,
            "statement": (
                "A positive result is a matched fixed-depth SOC stock increase over the supplied interval. "
                "It is not, by itself, proof of intervention-attributable or creditable sequestration."
            ),
        },
        "profile_results": {"baseline": baseline, "followup": followup},
        "equations": {
            "stock_change": "delta_SOC = SOC_followup - SOC_baseline",
            "annualized_stock_change": "delta_SOC_per_year = delta_SOC / elapsed_years",
            "relative_change_percent": "100 * delta_SOC / SOC_baseline when baseline != 0",
        },
        "guardrails": _guardrails(),
    }
    result["input_fingerprint"] = _hash({
        "comparison_id": comparison_id,
        "spatial_unit_id": spatial_unit_id,
        "baseline_at": baseline_at_raw,
        "followup_at": followup_at_raw,
        "baseline_profile_fingerprint": baseline["input_fingerprint"],
        "followup_profile_fingerprint": followup["input_fingerprint"],
        "area_ha": area,
        "baseline_ref": baseline_ref,
        "intervention_ref": intervention_ref,
        "source_refs": source_refs,
    })
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_change_series(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonChangeV0800Error("series request must be an object")
    series_id = _safe_id(payload.get("series_id") or "series:soc-change", "series_id", True)
    spatial_unit_id = _safe_id(payload.get("spatial_unit_id"), "spatial_unit_id", True)
    observations = payload.get("observations")
    if not isinstance(observations, list) or not (2 <= len(observations) <= MAX_SERIES_POINTS):
        raise SoilCarbonChangeV0800Error(f"observations must contain 2..{MAX_SERIES_POINTS} records")
    area = payload.get("area_ha")
    rows: list[dict[str, Any]] = []
    seen_times: set[str] = set()
    reference_signature: list[dict[str, float]] | None = None
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict):
            raise SoilCarbonChangeV0800Error(f"observations[{i}] must be an object")
        raw, dt = _time(obs.get("observed_at"), f"observations[{i}].observed_at")
        stamp = dt.isoformat()
        if stamp in seen_times:
            raise SoilCarbonChangeV0800Error("observation timestamps must be unique")
        seen_times.add(stamp)
        profile = _profile_payload(obs.get("profile"), f"observations[{i}].profile", _number(area, "area_ha") if area not in (None, "") else None)
        signature = _depth_signature(profile)
        if reference_signature is None:
            reference_signature = signature
        elif signature != reference_signature:
            raise SoilCarbonChangeV0800Error("all series profiles must use identical normalized fixed-depth intervals")
        rows.append({
            "observation_id": _safe_id(obs.get("observation_id") or f"observation:{series_id}:{i+1}", f"observations[{i}].observation_id", True),
            "observed_at": raw,
            "_dt": dt,
            "profile": profile,
        })
    rows.sort(key=lambda x: x["_dt"])
    points = []
    for row in rows:
        points.append({
            "observation_id": row["observation_id"],
            "observed_at": row["observed_at"],
            "soc_stock_Mg_C_ha": row["profile"]["soc_stock_Mg_C_ha"],
            "profile_result_fingerprint": row["profile"]["result_fingerprint"],
        })
    changes = []
    for left, right in zip(rows, rows[1:]):
        seconds = (right["_dt"] - left["_dt"]).total_seconds()
        if seconds <= 0:
            raise SoilCarbonChangeV0800Error("series timestamps must increase after normalization")
        delta = right["profile"]["soc_stock_Mg_C_ha"] - left["profile"]["soc_stock_Mg_C_ha"]
        years = seconds / SECONDS_PER_DAY / DAYS_PER_YEAR
        changes.append({
            "from_observation_id": left["observation_id"],
            "to_observation_id": right["observation_id"],
            "elapsed_years": years,
            "stock_change_Mg_C_ha": delta,
            "annualized_stock_change_Mg_C_ha_yr": delta / years,
        })
    first, last = rows[0], rows[-1]
    elapsed_years = (last["_dt"] - first["_dt"]).total_seconds() / SECONDS_PER_DAY / DAYS_PER_YEAR
    overall_delta = last["profile"]["soc_stock_Mg_C_ha"] - first["profile"]["soc_stock_Mg_C_ha"]
    result = {
        "ok": True,
        "schema": SERIES_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "series_id": series_id,
        "spatial_unit_id": spatial_unit_id,
        "point_count": len(points),
        "points": points,
        "pairwise_changes": changes,
        "overall": {
            "elapsed_years": elapsed_years,
            "stock_change_Mg_C_ha": overall_delta,
            "annualized_stock_change_Mg_C_ha_yr": overall_delta / elapsed_years,
        },
        "depth_match": {"policy": "exact-normalized-intervals", "intervals": reference_signature},
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonChangeV0800Error("project-packet request must be an object")
    project_id = _safe_id(payload.get("project_id"), "project_id", True)
    actor_ref = _safe_id(payload.get("actor_ref") or "system:sustainable-catalyst-lab", "actor_ref", True)
    input_object_ids = _string_list(payload.get("input_object_ids"), "input_object_ids")
    evidence_refs = _string_list(payload.get("evidence_refs"), "evidence_refs")
    methodology_refs = _string_list(payload.get("methodology_refs"), "methodology_refs")
    measure_refs = _string_list(payload.get("measure_refs"), "measure_refs")
    result = compare_profiles(payload.get("comparison") or payload)
    run_at_raw, _ = _time(payload.get("run_at") or datetime.now(timezone.utc).isoformat(), "run_at")
    run_id = _safe_id(payload.get("model_run_id") or f"model-run:soc-change-{result['result_fingerprint'][:16]}", "model_run_id", True)
    parent_ids = [result["spatial_unit_id"]]
    model_object = {
        "object_id": run_id,
        "object_type": "model-run",
        "project_id": project_id,
        "version": 1,
        "status": "draft",
        "payload": {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "run_at": run_at_raw,
            "input_object_ids": input_object_ids,
            "output_summary": {
                "comparison_id": result["comparison_id"],
                "spatial_unit_id": result["spatial_unit_id"],
                "baseline_stock_Mg_C_ha": result["baseline"]["soc_stock_Mg_C_ha"],
                "followup_stock_Mg_C_ha": result["followup"]["soc_stock_Mg_C_ha"],
                "stock_change_Mg_C_ha": result["stock_change_Mg_C_ha"],
                "annualized_stock_change_Mg_C_ha_yr": result["annualized_stock_change_Mg_C_ha_yr"],
                "direction": result["direction"],
                "change_result_fingerprint": result["result_fingerprint"],
            },
            "parameter_set": {
                "basis": result["model"]["basis"],
                "depth_match": result["depth_match"],
                "elapsed_days": result["elapsed_days"],
                "annualization_basis_days_per_year": DAYS_PER_YEAR,
                "baseline_ref": result["baseline_ref"],
                "intervention_ref": result["intervention_ref"],
            },
            "assumption_refs": _string_list(payload.get("assumption_refs"), "assumption_refs"),
            "uncertainty_summary": "Not estimated in Carbon & Nature v0.8.0; uncertainty analysis is reserved for v0.9.0.",
        },
        "source_refs": result["source_refs"],
        "provenance_refs": [f"event:{run_id}:modeled"],
        "parent_object_ids": parent_ids,
        "evidence_refs": evidence_refs,
        "methodology_refs": methodology_refs,
        "measure_refs": measure_refs,
    }
    model_object["content_fingerprint"] = _hash({k: v for k, v in model_object.items() if k != "content_fingerprint"})
    event = {
        "event_id": f"event:{run_id}:modeled",
        "event_type": "modeled",
        "object_id": run_id,
        "occurred_at": run_at_raw,
        "actor_ref": actor_ref,
        "input_object_ids": input_object_ids,
        "source_refs": result["source_refs"],
        "model_ref": f"{MODEL_NAME}@{MODEL_VERSION}",
        "input_fingerprint": result["input_fingerprint"],
        "result_fingerprint": result["result_fingerprint"],
    }
    links = [
        {"link_id": f"link:{oid}:{run_id}", "predicate": "input-to-model-run", "subject_id": oid, "object_id": run_id}
        for oid in input_object_ids
    ]
    packet = {"schema": PROJECT_PACKET_SCHEMA, "objects": [model_object], "provenance": [event], "links": links}
    return {
        "ok": True,
        "schema": "sc-carbon-nature-soc-stock-change-project-handoff/0.8.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "packet": packet,
        "change_result": result,
        "handoff": {
            "target_contract": PROJECT_PACKET_SCHEMA,
            "compatible_with": "Carbon & Nature v0.4+ Carbon Project Object Model & Provenance",
            "persistence": "not-performed-by-this-endpoint",
            "validation_scope": "structural handoff construction only",
        },
        "guardrails": _guardrails(),
        "packet_fingerprint": _hash(packet),
    }


def _guardrails() -> dict[str, bool]:
    return {
        "exact_depth_interval_matching_required": True,
        "fixed_depth_basis_explicit": True,
        "equivalent_soil_mass_not_implemented": True,
        "positive_stock_change_not_treated_as_attributed_sequestration": True,
        "counterfactual_not_established": True,
        "intervention_attribution_not_inferred": True,
        "additionality_not_determined": True,
        "leakage_not_determined": True,
        "permanence_not_determined": True,
        "uncertainty_not_inferred": True,
        "co2e_not_inferred": True,
        "whole_farm_ghg_balance_not_calculated": True,
        "methodology_eligibility_not_determined": True,
        "verification_not_performed": True,
        "credit_eligibility_not_determined": True,
        "input_measurements_not_treated_as_verified": True,
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain": "Carbon & Nature Intelligence",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "release": "SOC Change & Sequestration Model",
        "basis": "matched-fixed-depth-fine-earth-corrected",
        "capabilities": {
            "matched_profile_stock_change": True,
            "annualized_stock_change": True,
            "relative_stock_change": True,
            "parcel_area_scaling": True,
            "multi_date_change_series": True,
            "project_packet_handoff": True,
            "deterministic_fingerprints": True,
            "attributed_sequestration_claim": False,
        },
        "limits": {"max_series_points": MAX_SERIES_POINTS, "max_area_ha": MAX_AREA_HA},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "schemas": {
            "stock_change": CHANGE_SCHEMA,
            "change_series": SERIES_SCHEMA,
            "project_packet": PROJECT_PACKET_SCHEMA,
            "input_profile": "sc-carbon-nature-soc-profile/0.6.0",
        },
        "required_comparison_fields": [
            "spatial_unit_id", "baseline_at", "followup_at", "baseline_profile", "followup_profile"
        ],
        "matching_policy": {
            "depth_basis": "fixed-depth",
            "interval_policy": "exact-normalized-intervals",
            "layer_count_must_match": True,
            "depth_gaps_must_match": True,
        },
        "canonical_units": {
            "stock": "Mg C/ha", "stock_change": "Mg C/ha", "annualized_stock_change": "Mg C/ha/yr", "area": "ha"
        },
        "guardrails": _guardrails(),
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "soc-stock-change-model-ready",
        "domain": "Carbon & Nature Intelligence",
        "domain_version": DOMAIN_VERSION,
        "release": "SOC Change & Sequestration Model",
        "lab_release_version": LAB_RELEASE_VERSION,
        "compute_core_version": ENGINE_VERSION,
        "matched_fixed_depth_comparison": True,
        "annualized_stock_change": True,
        "change_series": True,
        "carbon_project_packet_handoff": True,
        "attributed_sequestration_claim": False,
        "guardrails": _guardrails(),
    }
