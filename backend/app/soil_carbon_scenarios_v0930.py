from __future__ import annotations

from hashlib import sha256
import json
import math
from typing import Any

from .soil_organic_carbon_v0890 import calculate_profile_stock

LAB_RELEASE_VERSION = "0.93.0"
DOMAIN_VERSION = "0.10.0"
ENGINE_VERSION = "1.0.0"
MODEL_VERSION = "0.10.0"
SCENARIO_SCHEMA = "sc-carbon-nature-soc-management-scenario/0.10.0"
COMPARISON_SCHEMA = "sc-carbon-nature-soc-management-scenario-comparison/0.10.0"
SENSITIVITY_SCHEMA = "sc-carbon-nature-soc-management-sensitivity/0.10.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_HORIZON_YEARS = 100
MAX_SCENARIOS = 50
MAX_SWEEP_VALUES = 101
MAX_REFS = 100


class SoilCarbonScenarioV01000Error(ValueError):
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
        raise SoilCarbonScenarioV01000Error(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise SoilCarbonScenarioV01000Error(f"{label} must be finite")
    return out


def _positive(value: Any, label: str, allow_zero: bool = False) -> float:
    out = _number(value, label)
    if (out < 0 if allow_zero else out <= 0):
        op = ">=0" if allow_zero else ">0"
        raise SoilCarbonScenarioV01000Error(f"{label} must be {op}")
    return out


def _integer(value: Any, label: str, low: int, high: int) -> int:
    out = _number(value, label)
    if not out.is_integer():
        raise SoilCarbonScenarioV01000Error(f"{label} must be an integer")
    i = int(out)
    if not low <= i <= high:
        raise SoilCarbonScenarioV01000Error(f"{label} must be between {low} and {high}")
    return i


def _text(value: Any, label: str, required: bool = False, max_len: int = 240) -> str | None:
    if value is None:
        if required:
            raise SoilCarbonScenarioV01000Error(f"{label} is required")
        return None
    text = str(value).strip()
    if not text:
        if required:
            raise SoilCarbonScenarioV01000Error(f"{label} is required")
        return None
    if len(text) > max_len:
        raise SoilCarbonScenarioV01000Error(f"{label} exceeds {max_len} characters")
    return text


def _refs(value: Any, label: str) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise SoilCarbonScenarioV01000Error(f"{label} must be an array")
    if len(value) > MAX_REFS:
        raise SoilCarbonScenarioV01000Error(f"{label} may contain at most {MAX_REFS} values")
    out: list[str] = []
    for i, item in enumerate(value):
        text = _text(item, f"{label}[{i}]", True, 240)
        assert text is not None
        if text not in out:
            out.append(text)
    return out


def _baseline(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("baseline_stock_Mg_C_ha") not in (None, ""):
        stock = _number(payload.get("baseline_stock_Mg_C_ha"), "baseline_stock_Mg_C_ha")
        if stock < 0:
            raise SoilCarbonScenarioV01000Error("baseline_stock_Mg_C_ha must be >=0")
        return {"stock_Mg_C_ha": stock, "source_basis": "user-supplied-stock", "profile_result_fingerprint": None}
    profile = payload.get("baseline_profile")
    if isinstance(profile, dict):
        try:
            result = calculate_profile_stock(profile)
        except Exception as exc:
            raise SoilCarbonScenarioV01000Error(f"baseline_profile invalid: {getattr(exc, 'detail', str(exc))}") from exc
        return {
            "stock_Mg_C_ha": float(result["soc_stock_Mg_C_ha"]),
            "source_basis": "soc-v0600-profile-calculation",
            "profile_result_fingerprint": result.get("result_fingerprint"),
        }
    raise SoilCarbonScenarioV01000Error("baseline_stock_Mg_C_ha or baseline_profile is required")


def _normalize_model(scenario: dict[str, Any], horizon: int) -> dict[str, Any]:
    model = str(scenario.get("model_type") or "").strip().lower()
    if model not in {"constant-annual-change", "compound-relative-change", "annual-change-schedule"}:
        raise SoilCarbonScenarioV01000Error(
            "model_type must be constant-annual-change, compound-relative-change, or annual-change-schedule"
        )
    if model == "constant-annual-change":
        if scenario.get("annual_change_Mg_C_ha_yr") in (None, ""):
            raise SoilCarbonScenarioV01000Error("annual_change_Mg_C_ha_yr is required; Sustainable Catalyst supplies no default SOC change rate")
        rate = _number(scenario.get("annual_change_Mg_C_ha_yr"), "annual_change_Mg_C_ha_yr")
        normalized: dict[str, Any] = {"model_type": model, "annual_change_Mg_C_ha_yr": rate}
        low = scenario.get("annual_change_lower_Mg_C_ha_yr")
        high = scenario.get("annual_change_upper_Mg_C_ha_yr")
        if low not in (None, "") or high not in (None, ""):
            if low in (None, "") or high in (None, ""):
                raise SoilCarbonScenarioV01000Error("constant annual-change envelope requires both lower and upper rates")
            lo = _number(low, "annual_change_lower_Mg_C_ha_yr")
            hi = _number(high, "annual_change_upper_Mg_C_ha_yr")
            if not lo <= rate <= hi:
                raise SoilCarbonScenarioV01000Error("annual-change envelope must satisfy lower <= central <= upper")
            normalized["assumption_envelope"] = {"lower": lo, "upper": hi, "unit": "Mg C/ha/yr"}
        return normalized
    if model == "compound-relative-change":
        if scenario.get("annual_relative_change_percent") in (None, ""):
            raise SoilCarbonScenarioV01000Error("annual_relative_change_percent is required; Sustainable Catalyst supplies no default relative SOC change rate")
        rate = _number(scenario.get("annual_relative_change_percent"), "annual_relative_change_percent")
        if rate <= -100:
            raise SoilCarbonScenarioV01000Error("annual_relative_change_percent must be > -100")
        normalized = {"model_type": model, "annual_relative_change_percent": rate}
        low = scenario.get("annual_relative_change_lower_percent")
        high = scenario.get("annual_relative_change_upper_percent")
        if low not in (None, "") or high not in (None, ""):
            if low in (None, "") or high in (None, ""):
                raise SoilCarbonScenarioV01000Error("relative-change envelope requires both lower and upper rates")
            lo = _number(low, "annual_relative_change_lower_percent")
            hi = _number(high, "annual_relative_change_upper_percent")
            if lo <= -100 or not lo <= rate <= hi:
                raise SoilCarbonScenarioV01000Error("relative-change envelope must satisfy -100 < lower <= central <= upper")
            normalized["assumption_envelope"] = {"lower": lo, "upper": hi, "unit": "%/yr"}
        return normalized
    values = scenario.get("annual_changes_Mg_C_ha")
    if not isinstance(values, list) or len(values) != horizon:
        raise SoilCarbonScenarioV01000Error(f"annual_changes_Mg_C_ha must contain exactly {horizon} values")
    rates = [_number(v, f"annual_changes_Mg_C_ha[{i}]") for i, v in enumerate(values)]
    return {"model_type": model, "annual_changes_Mg_C_ha": rates}


def _step(stock: float, model: dict[str, Any], year_index: int, envelope_key: str | None = None) -> tuple[float, float]:
    kind = model["model_type"]
    if kind == "constant-annual-change":
        rate = model["annual_change_Mg_C_ha_yr"]
        if envelope_key:
            rate = model["assumption_envelope"][envelope_key]
        return stock + rate, rate
    if kind == "compound-relative-change":
        pct = model["annual_relative_change_percent"]
        if envelope_key:
            pct = model["assumption_envelope"][envelope_key]
        change = stock * pct / 100.0
        return stock + change, change
    change = model["annual_changes_Mg_C_ha"][year_index]
    return stock + change, change


def _trajectory(start: float, model: dict[str, Any], horizon: int, base_year: int | None = None, envelope_key: str | None = None) -> list[dict[str, Any]]:
    stock = start
    rows = [{"year_index": 0, "calendar_year": base_year, "stock_Mg_C_ha": stock, "annual_change_Mg_C_ha": None, "cumulative_change_Mg_C_ha": 0.0}]
    for i in range(horizon):
        stock, change = _step(stock, model, i, envelope_key)
        if stock < -1e-10:
            raise SoilCarbonScenarioV01000Error(
                f"scenario projects negative SOC stock in year {i + 1}; revise the supplied rate, schedule, or horizon"
            )
        stock = max(0.0, stock)
        rows.append({
            "year_index": i + 1,
            "calendar_year": base_year + i + 1 if base_year is not None else None,
            "stock_Mg_C_ha": stock,
            "annual_change_Mg_C_ha": change,
            "cumulative_change_Mg_C_ha": stock - start,
        })
    return rows


def project_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonScenarioV01000Error("scenario request must be an object")
    scenario = payload.get("scenario") if isinstance(payload.get("scenario"), dict) else payload
    baseline_source = dict(payload)
    baseline_source.update({k: v for k, v in scenario.items() if k in {"baseline_stock_Mg_C_ha", "baseline_profile"}})
    baseline = _baseline(baseline_source)
    scenario_id = _text(scenario.get("scenario_id") or "scenario:soc-management", "scenario_id", True)
    label = _text(scenario.get("label") or scenario_id, "label", True)
    horizon = _integer(scenario.get("horizon_years"), "horizon_years", 1, MAX_HORIZON_YEARS)
    base_year = None
    if scenario.get("base_year") not in (None, ""):
        base_year = _integer(scenario.get("base_year"), "base_year", 1800, 2500)
    area_ha = None
    if scenario.get("area_ha") not in (None, ""):
        area_ha = _positive(scenario.get("area_ha"), "area_ha")
    model = _normalize_model(scenario, horizon)
    trajectory = _trajectory(baseline["stock_Mg_C_ha"], model, horizon, base_year)
    final_stock = trajectory[-1]["stock_Mg_C_ha"]
    cumulative = final_stock - baseline["stock_Mg_C_ha"]
    envelope = None
    if "assumption_envelope" in model:
        low_traj = _trajectory(baseline["stock_Mg_C_ha"], model, horizon, base_year, "lower")
        high_traj = _trajectory(baseline["stock_Mg_C_ha"], model, horizon, base_year, "upper")
        low_final = low_traj[-1]["stock_Mg_C_ha"]
        high_final = high_traj[-1]["stock_Mg_C_ha"]
        envelope = {
            "basis": "user-supplied-assumption-envelope-not-confidence-interval",
            "lower_trajectory": low_traj,
            "upper_trajectory": high_traj,
            "final_stock_range_Mg_C_ha": {"lower": min(low_final, high_final), "upper": max(low_final, high_final)},
        }
    result: dict[str, Any] = {
        "ok": True,
        "schema": SCENARIO_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "scenario_id": scenario_id,
        "label": label,
        "baseline": baseline,
        "horizon_years": horizon,
        "base_year": base_year,
        "area_ha": area_ha,
        "model": model,
        "trajectory": trajectory,
        "final_stock_Mg_C_ha": final_stock,
        "cumulative_stock_change_Mg_C_ha": cumulative,
        "mean_annual_stock_change_Mg_C_ha_yr": cumulative / horizon,
        "relative_change_percent": (cumulative / baseline["stock_Mg_C_ha"] * 100.0) if baseline["stock_Mg_C_ha"] > 0 else None,
        "measure_refs": _refs(scenario.get("measure_refs"), "measure_refs"),
        "assumption_refs": _refs(scenario.get("assumption_refs"), "assumption_refs"),
        "evidence_refs": _refs(scenario.get("evidence_refs"), "evidence_refs"),
        "notes": _text(scenario.get("notes"), "notes", False, 4000),
        "assumption_envelope": envelope,
        "interpretation": {
            "scenario_projection_is_forecast": False,
            "causal_attribution_established": False,
            "verified_sequestration_established": False,
            "statement": "This is a deterministic scenario projection from user-supplied assumptions. A projected SOC increase is not a forecast, causal attribution, verified sequestration, additionality finding, or carbon-credit claim.",
        },
        "guardrails": _guardrails(),
    }
    if area_ha is not None:
        result["parcel_scale"] = {
            "baseline_stock_Mg_C": baseline["stock_Mg_C_ha"] * area_ha,
            "final_stock_Mg_C": final_stock * area_ha,
            "cumulative_stock_change_Mg_C": cumulative * area_ha,
        }
    normalized_for_fingerprint = {k: v for k, v in result.items() if k not in {"input_fingerprint", "result_fingerprint"}}
    result["input_fingerprint"] = _hash({"baseline": baseline, "scenario": scenario})
    result["result_fingerprint"] = _hash(normalized_for_fingerprint)
    return result


def compare_scenarios(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonScenarioV01000Error("scenario comparison request must be an object")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not (2 <= len(scenarios) <= MAX_SCENARIOS):
        raise SoilCarbonScenarioV01000Error(f"scenarios must contain 2..{MAX_SCENARIOS} records")
    shared: dict[str, Any] = {}
    for key in ("baseline_stock_Mg_C_ha", "baseline_profile", "area_ha", "base_year"):
        if key in payload:
            shared[key] = payload[key]
    results = []
    seen: set[str] = set()
    for i, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise SoilCarbonScenarioV01000Error(f"scenarios[{i}] must be an object")
        merged = {**shared, **scenario}
        result = project_scenario(merged)
        if result["scenario_id"] in seen:
            raise SoilCarbonScenarioV01000Error("scenario_id values must be unique")
        seen.add(result["scenario_id"])
        results.append(result)
    table = [{
        "scenario_id": x["scenario_id"],
        "label": x["label"],
        "model_type": x["model"]["model_type"],
        "horizon_years": x["horizon_years"],
        "final_stock_Mg_C_ha": x["final_stock_Mg_C_ha"],
        "cumulative_stock_change_Mg_C_ha": x["cumulative_stock_change_Mg_C_ha"],
        "mean_annual_stock_change_Mg_C_ha_yr": x["mean_annual_stock_change_Mg_C_ha_yr"],
        "relative_change_percent": x["relative_change_percent"],
    } for x in results]
    result = {
        "ok": True,
        "schema": COMPARISON_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "comparison_id": _text(payload.get("comparison_id") or "comparison:soc-management", "comparison_id", True),
        "scenario_count": len(results),
        "scenarios": results,
        "comparison_table": table,
        "automatic_ranking_performed": False,
        "automatic_recommendation_generated": False,
        "guardrails": _guardrails(),
    }
    result["input_fingerprint"] = _hash(payload)
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def sensitivity_sweep(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonScenarioV01000Error("sensitivity request must be an object")
    model_type = str(payload.get("model_type") or "constant-annual-change").strip().lower()
    if model_type not in {"constant-annual-change", "compound-relative-change"}:
        raise SoilCarbonScenarioV01000Error("sensitivity model_type must be constant-annual-change or compound-relative-change")
    values = payload.get("values")
    if not isinstance(values, list) or not (1 <= len(values) <= MAX_SWEEP_VALUES):
        raise SoilCarbonScenarioV01000Error(f"values must contain 1..{MAX_SWEEP_VALUES} user-supplied values")
    numeric = [_number(v, f"values[{i}]") for i, v in enumerate(values)]
    if model_type == "compound-relative-change" and any(v <= -100 for v in numeric):
        raise SoilCarbonScenarioV01000Error("compound relative sensitivity values must be > -100")
    horizon = _integer(payload.get("horizon_years"), "horizon_years", 1, MAX_HORIZON_YEARS)
    baseline = _baseline(payload)
    rows=[]
    for i, value in enumerate(numeric):
        scenario={
            "scenario_id": f"sensitivity:{i+1}",
            "horizon_years": horizon,
            "baseline_stock_Mg_C_ha": baseline["stock_Mg_C_ha"],
            "model_type": model_type,
        }
        if model_type == "constant-annual-change": scenario["annual_change_Mg_C_ha_yr"] = value
        else: scenario["annual_relative_change_percent"] = value
        projected=project_scenario(scenario)
        rows.append({
            "input_value": value,
            "input_unit": "Mg C/ha/yr" if model_type == "constant-annual-change" else "%/yr",
            "final_stock_Mg_C_ha": projected["final_stock_Mg_C_ha"],
            "cumulative_stock_change_Mg_C_ha": projected["cumulative_stock_change_Mg_C_ha"],
        })
    result={
        "ok":True,"schema":SENSITIVITY_SCHEMA,"domain_version":DOMAIN_VERSION,"lab_release_version":LAB_RELEASE_VERSION,
        "sensitivity_id":_text(payload.get("sensitivity_id") or "sensitivity:soc-management","sensitivity_id",True),
        "baseline":baseline,"horizon_years":horizon,"model_type":model_type,"values_source":"user-supplied-only","rows":rows,
        "automatic_optimization_performed":False,"automatic_recommendation_generated":False,"guardrails":_guardrails(),
    }
    result["input_fingerprint"]=_hash(payload); result["result_fingerprint"]=_hash({k:v for k,v in result.items() if k!='result_fingerprint'})
    return result


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonScenarioV01000Error("project packet request must be an object")
    project_id = _text(payload.get("project_id"), "project_id", True)
    actor = _text(payload.get("actor_ref") or "system:sustainable-catalyst-lab", "actor_ref", True)
    scenario_payload = payload.get("scenario")
    if not isinstance(scenario_payload, dict):
        raise SoilCarbonScenarioV01000Error("scenario object is required")
    scenario = project_scenario(scenario_payload)
    object_id = _text(payload.get("object_id") or f"model-run:soc-scenario-{scenario['result_fingerprint'][:16]}", "object_id", True)
    obj = {
        "object_id": object_id,
        "object_type": "model-run",
        "project_id": project_id,
        "version": "1.0.0",
        "status": "draft",
        "payload": {
            "model_key": "soc-management-scenario-v1000",
            "model_version": MODEL_VERSION,
            "lab_release_version": LAB_RELEASE_VERSION,
            "domain_version": DOMAIN_VERSION,
            "scenario_id": scenario["scenario_id"],
            "model_type": scenario["model"]["model_type"],
            "horizon_years": scenario["horizon_years"],
            "output_summary": {
                "baseline_stock_Mg_C_ha": scenario["baseline"]["stock_Mg_C_ha"],
                "final_stock_Mg_C_ha": scenario["final_stock_Mg_C_ha"],
                "cumulative_stock_change_Mg_C_ha": scenario["cumulative_stock_change_Mg_C_ha"],
                "mean_annual_stock_change_Mg_C_ha_yr": scenario["mean_annual_stock_change_Mg_C_ha_yr"],
            },
            "result_fingerprint": scenario["result_fingerprint"],
            "interpretation": scenario["interpretation"],
            "guardrails": scenario["guardrails"],
        },
        "source_refs": scenario["evidence_refs"],
        "evidence_refs": scenario["evidence_refs"],
        "measure_refs": scenario["measure_refs"],
        "provenance_refs": ["provenance:soc-management-scenario-model-run"],
    }
    event = {
        "provenance_id": "provenance:soc-management-scenario-model-run",
        "event_type": "modeled",
        "object_id": object_id,
        "actor_ref": actor,
        "details": {
            "model_version": MODEL_VERSION,
            "result_fingerprint": scenario["result_fingerprint"],
            "assumption_refs": scenario["assumption_refs"],
            "scenario_projection_is_forecast": False,
        },
    }
    packet = {"schema": PROJECT_PACKET_SCHEMA, "objects": [obj], "provenance": [event], "links": []}
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "packet": packet, "scenario": scenario, "packet_fingerprint": _hash(packet)}


def _guardrails() -> dict[str, bool]:
    return {
        "no_default_soc_change_rate": True,
        "measure_refs_do_not_inject_rates": True,
        "scenario_projection_is_not_forecast": True,
        "projected_increase_is_not_verified_sequestration": True,
        "soil_capacity_or_saturation_not_inferred": True,
        "spatial_representativeness_not_inferred": True,
        "uncertainty_not_inferred_from_scenario_spread": True,
        "co2e_not_inferred": True,
        "whole_farm_ghg_balance_not_calculated": True,
        "causal_attribution_not_established": True,
        "additionality_not_determined": True,
        "leakage_not_determined": True,
        "permanence_not_determined": True,
        "verification_not_performed": True,
        "credit_eligibility_not_determined": True,
        "automatic_recommendation_generated": False,
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "capabilities": {
            "constant_annual_change_scenarios": True,
            "compound_relative_change_scenarios": True,
            "annual_change_schedules": True,
            "multi_scenario_comparison": True,
            "user_supplied_assumption_envelopes": True,
            "user_supplied_sensitivity_sweeps": True,
            "parcel_scale_projection": True,
            "carbon_project_packet_handoff": True,
            "deterministic_fingerprints": True,
        },
        "limits": {"max_horizon_years": MAX_HORIZON_YEARS, "max_scenarios": MAX_SCENARIOS, "max_sweep_values": MAX_SWEEP_VALUES},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "schemas": {"scenario": SCENARIO_SCHEMA, "comparison": COMPARISON_SCHEMA, "sensitivity": SENSITIVITY_SCHEMA},
        "model_types": ["constant-annual-change", "compound-relative-change", "annual-change-schedule"],
        "units": {"stock": "Mg C/ha", "annual_change": "Mg C/ha/yr", "relative_change": "%/yr", "area": "ha"},
        "rate_policy": "All SOC change assumptions are user supplied. No measure registry entry injects a default rate.",
        "guardrails": _guardrails(),
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "soc-management-scenario-studio-ready",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "compute_core_version": ENGINE_VERSION,
        "scenario_projection": True,
        "scenario_comparison": True,
        "sensitivity_sweep": True,
        "automatic_recommendation": False,
        "whole_farm_ghg_balance": False,
        "guardrails": _guardrails(),
    }
