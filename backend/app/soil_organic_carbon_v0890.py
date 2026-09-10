from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

LAB_RELEASE_VERSION = "0.89.0"
DOMAIN_VERSION = "0.6.0"
ENGINE_VERSION = "1.0.0"
LAYER_SCHEMA = "sc-carbon-nature-soc-layer/0.6.0"
PROFILE_SCHEMA = "sc-carbon-nature-soc-profile/0.6.0"
RESULT_SCHEMA = "sc-carbon-nature-soc-profile-result/0.6.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MODEL_NAME = "Sustainable Catalyst fixed-depth SOC stock foundation"
MODEL_VERSION = "0.6.0"
MAX_LAYERS = 200
MAX_PROFILE_DEPTH_CM = 500.0
MAX_AREA_HA = 10_000_000.0
SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,159}$")


class SoilOrganicCarbonV0600Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise SoilOrganicCarbonV0600Error(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise SoilOrganicCarbonV0600Error(f"{label} must be finite")
    return number


def _optional_text(value: Any, max_len: int = 1000) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > max_len:
        raise SoilOrganicCarbonV0600Error(f"text value exceeds {max_len} characters")
    return text


def _safe_id(value: Any, label: str, required: bool = False) -> str | None:
    text = _optional_text(value, 160)
    if not text:
        if required:
            raise SoilOrganicCarbonV0600Error(f"{label} is required")
        return None
    if not SAFE_ID.fullmatch(text):
        raise SoilOrganicCarbonV0600Error(f"{label} must be a stable identifier using letters, numbers, dot, underscore, colon, or hyphen")
    return text


def _string_list(value: Any, label: str, limit: int = 100) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > limit:
        raise SoilOrganicCarbonV0600Error(f"{label} must be a list with at most {limit} entries")
    out: list[str] = []
    for item in value:
        text = _optional_text(item, 300)
        if text and text not in out:
            out.append(text)
    return out


def _iso(value: Any, label: str, required: bool = False) -> str | None:
    text = _optional_text(value, 80)
    if not text:
        if required:
            raise SoilOrganicCarbonV0600Error(f"{label} is required")
        return None
    candidate = text.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SoilOrganicCarbonV0600Error(f"{label} must be an ISO-8601 date or timestamp") from exc
    return text


def _depth_cm(value: Any, unit: Any, label: str) -> float:
    number = _number(value, label)
    u = str(unit or "cm").strip().lower().replace(" ", "")
    factors = {"cm": 1.0, "mm": 0.1, "m": 100.0}
    if u not in factors:
        raise SoilOrganicCarbonV0600Error(f"{label} unit must be cm, mm, or m")
    result = number * factors[u]
    if result < 0 or result > MAX_PROFILE_DEPTH_CM:
        raise SoilOrganicCarbonV0600Error(f"{label} must normalize to 0..{MAX_PROFILE_DEPTH_CM:g} cm")
    return result


def _soc_g_per_kg(value: Any, unit: Any) -> float:
    number = _number(value, "soc_value")
    u = str(unit or "g/kg").strip().lower().replace(" ", "")
    if u in {"g/kg", "gkg", "gkg-1", "gkg^-1", "mg/g", "mgg-1", "mg/gsoil"}:
        result = number
    elif u in {"%", "percent", "percentage"}:
        result = number * 10.0
    elif u in {"fraction", "kg/kg", "kgkg-1", "kgkg^-1"}:
        result = number * 1000.0
    else:
        raise SoilOrganicCarbonV0600Error("soc_unit must be g/kg, mg/g, percent, or fraction")
    if result < 0 or result > 1000:
        raise SoilOrganicCarbonV0600Error("SOC concentration must normalize to 0..1000 g/kg")
    return result


def _bulk_density_g_cm3(value: Any, unit: Any) -> float:
    number = _number(value, "bulk_density_value")
    u = str(unit or "g/cm3").strip().lower().replace(" ", "").replace("³", "3")
    if u in {"g/cm3", "gcm-3", "gcm^-3", "mg/m3", "mgm-3", "mgm^-3", "t/m3", "tm-3", "tm^-3"}:
        result = number
    elif u in {"kg/m3", "kgm-3", "kgm^-3"}:
        result = number / 1000.0
    else:
        raise SoilOrganicCarbonV0600Error("bulk_density_unit must be g/cm3, Mg/m3, t/m3, or kg/m3")
    if result <= 0 or result > 3.5:
        raise SoilOrganicCarbonV0600Error("bulk density must normalize to >0 and <=3.5 g/cm3")
    return result


def normalize_layer(layer: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(layer, dict):
        raise SoilOrganicCarbonV0600Error(f"layers[{index}] must be an object")
    layer_id = _safe_id(layer.get("layer_id") or layer.get("id") or f"layer-{index + 1}", f"layers[{index}].layer_id", True)
    depth_unit = layer.get("depth_unit") or "cm"
    top = _depth_cm(layer.get("top_depth", 0), depth_unit, f"layers[{index}].top_depth")
    bottom = _depth_cm(layer.get("bottom_depth"), depth_unit, f"layers[{index}].bottom_depth")
    if bottom <= top:
        raise SoilOrganicCarbonV0600Error(f"layers[{index}] bottom_depth must be greater than top_depth")
    soc = _soc_g_per_kg(layer.get("soc_value"), layer.get("soc_unit") or "g/kg")
    bd = _bulk_density_g_cm3(layer.get("bulk_density_value"), layer.get("bulk_density_unit") or "g/cm3")
    cf = _number(layer.get("coarse_fragments_percent", 0), f"layers[{index}].coarse_fragments_percent")
    if cf < 0 or cf >= 100:
        raise SoilOrganicCarbonV0600Error(f"layers[{index}].coarse_fragments_percent must be >=0 and <100")
    source_refs = _string_list(layer.get("source_refs"), f"layers[{index}].source_refs")
    normalized = {
        "layer_id": layer_id,
        "top_depth_cm": top,
        "bottom_depth_cm": bottom,
        "thickness_cm": bottom - top,
        "soc_g_per_kg": soc,
        "soc_percent": soc / 10.0,
        "bulk_density_g_cm3": bd,
        "bulk_density_Mg_m3": bd,
        "coarse_fragments_percent": cf,
        "fine_earth_fraction": 1.0 - cf / 100.0,
        "sample_id": _safe_id(layer.get("sample_id"), f"layers[{index}].sample_id"),
        "observation_id": _safe_id(layer.get("observation_id"), f"layers[{index}].observation_id"),
        "methodology_key": _safe_id(layer.get("methodology_key"), f"layers[{index}].methodology_key"),
        "source_refs": source_refs,
        "notes": _optional_text(layer.get("notes"), 2000),
    }
    normalized["input_fingerprint"] = _hash({k: v for k, v in normalized.items() if k != "input_fingerprint"})
    return normalized


def calculate_layer_stock(layer: dict[str, Any], index: int = 0) -> dict[str, Any]:
    n = normalize_layer(layer, index)
    # 1 g/cm3 = 1 Mg/m3; one hectare × 1 cm = 100 m3.
    corrected_soil_mass_mg_ha = n["bulk_density_Mg_m3"] * 100.0 * n["thickness_cm"] * n["fine_earth_fraction"]
    soc_fraction = n["soc_g_per_kg"] / 1000.0
    stock = corrected_soil_mass_mg_ha * soc_fraction
    result = {
        "schema": "sc-carbon-nature-soc-layer-result/0.6.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "basis": "fixed-depth-fine-earth-corrected",
        "layer": n,
        "soil_mass_Mg_dry_soil_ha": corrected_soil_mass_mg_ha,
        "soc_stock_Mg_C_ha": stock,
        "equation": "SOC_stock_Mg_C_ha = SOC_g_per_kg × bulk_density_g_cm3 × thickness_cm × 0.1 × fine_earth_fraction",
        "assumptions": [
            "Bulk density represents the same depth interval as the SOC concentration.",
            "Coarse-fragment correction is applied as an excluded volume/mass fraction using the supplied percent.",
            "The calculation is fixed-depth and does not implement equivalent-soil-mass correction.",
        ],
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash(result)
    return result


def _profile_payload(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], float | None, str | None, list[str]]:
    if not isinstance(payload, dict):
        raise SoilOrganicCarbonV0600Error("profile request must be an object")
    layers = payload.get("layers")
    if not isinstance(layers, list) or not layers or len(layers) > MAX_LAYERS:
        raise SoilOrganicCarbonV0600Error(f"layers must contain 1..{MAX_LAYERS} records")
    results = [calculate_layer_stock(row, i) for i, row in enumerate(layers)]
    results.sort(key=lambda row: (row["layer"]["top_depth_cm"], row["layer"]["bottom_depth_cm"], row["layer"]["layer_id"]))
    previous_bottom: float | None = None
    gaps: list[dict[str, float]] = []
    for row in results:
        top = row["layer"]["top_depth_cm"]
        bottom = row["layer"]["bottom_depth_cm"]
        if previous_bottom is not None:
            if top < previous_bottom - 1e-12:
                raise SoilOrganicCarbonV0600Error("profile layers must not overlap after depth normalization")
            if top > previous_bottom + 1e-12:
                gaps.append({"top_depth_cm": previous_bottom, "bottom_depth_cm": top})
        previous_bottom = bottom
    area = None
    if payload.get("area_ha") not in (None, ""):
        area = _number(payload.get("area_ha"), "area_ha")
        if area <= 0 or area > MAX_AREA_HA:
            raise SoilOrganicCarbonV0600Error(f"area_ha must be >0 and <= {MAX_AREA_HA:g}")
    profile_id = _safe_id(payload.get("profile_id"), "profile_id")
    sources = _string_list(payload.get("source_refs"), "source_refs")
    return results, area, profile_id, sources


def calculate_profile_stock(payload: dict[str, Any]) -> dict[str, Any]:
    results, area, profile_id, sources = _profile_payload(payload)
    total = sum(row["soc_stock_Mg_C_ha"] for row in results)
    first_top = results[0]["layer"]["top_depth_cm"]
    last_bottom = max(row["layer"]["bottom_depth_cm"] for row in results)
    coverage = sum(row["layer"]["thickness_cm"] for row in results)
    gaps: list[dict[str, float]] = []
    previous = None
    for row in results:
        top = row["layer"]["top_depth_cm"]
        if previous is not None and top > previous + 1e-12:
            gaps.append({"top_depth_cm": previous, "bottom_depth_cm": top})
        previous = row["layer"]["bottom_depth_cm"]
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "model": {"name": MODEL_NAME, "version": MODEL_VERSION, "basis": "fixed-depth-fine-earth-corrected"},
        "profile_id": profile_id,
        "layer_count": len(results),
        "depth": {"top_cm": first_top, "bottom_cm": last_bottom, "covered_cm": coverage, "gaps": gaps, "contiguous": not gaps},
        "layers": results,
        "soc_stock_Mg_C_ha": total,
        "area_ha": area,
        "soc_stock_Mg_C_total": total * area if area is not None else None,
        "source_refs": sources,
        "equation_basis": {
            "canonical_soc_concentration": "g/kg",
            "canonical_bulk_density": "g/cm3 (= Mg/m3)",
            "canonical_depth": "cm",
            "canonical_stock": "Mg C/ha",
            "layer_formula": "SOC_g_per_kg × bulk_density_g_cm3 × thickness_cm × 0.1 × (1 - coarse_fragments_percent/100)",
            "aggregation": "sum of non-overlapping layer stocks",
        },
        "guardrails": _guardrails(),
    }
    result["input_fingerprint"] = _hash({
        "layers": [row["layer"]["input_fingerprint"] for row in results], "area_ha": area, "profile_id": profile_id, "source_refs": sources
    })
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilOrganicCarbonV0600Error("project-packet request must be an object")
    project_id = _safe_id(payload.get("project_id"), "project_id", True)
    parcel_id = _safe_id(payload.get("parcel_id"), "parcel_id")
    actor_ref = _safe_id(payload.get("actor_ref") or "system:sustainable-catalyst-lab", "actor_ref", True)
    run_at = _iso(payload.get("run_at") or datetime.now(timezone.utc).isoformat(), "run_at", True)
    input_object_ids = _string_list(payload.get("input_object_ids"), "input_object_ids")
    source_refs = _string_list(payload.get("source_refs"), "source_refs")
    methodology_refs = _string_list(payload.get("methodology_refs"), "methodology_refs")
    profile_payload = payload.get("profile") or {}
    if not isinstance(profile_payload, dict):
        raise SoilOrganicCarbonV0600Error("profile must be an object")
    if source_refs and not profile_payload.get("source_refs"):
        profile_payload = {**profile_payload, "source_refs": source_refs}
    profile = calculate_profile_stock(profile_payload)
    run_id = _safe_id(payload.get("model_run_id") or f"model-run:soc-{profile['result_fingerprint'][:16]}", "model_run_id", True)
    parent_ids = [x for x in [parcel_id] if x]
    model_object = {
        "object_id": run_id,
        "object_type": "model-run",
        "project_id": project_id,
        "version": 1,
        "status": "draft",
        "payload": {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "run_at": run_at,
            "input_object_ids": input_object_ids,
            "output_summary": {
                "basis": profile["model"]["basis"],
                "soc_stock_Mg_C_ha": profile["soc_stock_Mg_C_ha"],
                "area_ha": profile["area_ha"],
                "soc_stock_Mg_C_total": profile["soc_stock_Mg_C_total"],
                "profile_result_fingerprint": profile["result_fingerprint"],
            },
            "parameter_set": {
                "layers": [row["layer"] for row in profile["layers"]],
                "calculation_basis": profile["equation_basis"],
            },
            "assumption_refs": _string_list(payload.get("assumption_refs"), "assumption_refs"),
            "uncertainty_summary": "Not estimated in Carbon & Nature v0.6.0; uncertainty analysis begins in the later SOC uncertainty release.",
        },
        "source_refs": source_refs,
        "provenance_refs": [f"event:{run_id}:modeled"],
        "parent_object_ids": parent_ids,
        "evidence_refs": _string_list(payload.get("evidence_refs"), "evidence_refs"),
        "methodology_refs": methodology_refs,
        "measure_refs": _string_list(payload.get("measure_refs"), "measure_refs"),
    }
    model_object["content_fingerprint"] = _hash({k: v for k, v in model_object.items() if k != "content_fingerprint"})
    event = {
        "event_id": f"event:{run_id}:modeled",
        "event_type": "modeled",
        "object_id": run_id,
        "occurred_at": run_at,
        "actor_ref": actor_ref,
        "input_object_ids": input_object_ids,
        "source_refs": source_refs,
        "model_ref": f"{MODEL_NAME}@{MODEL_VERSION}",
        "input_fingerprint": profile["input_fingerprint"],
        "result_fingerprint": profile["result_fingerprint"],
    }
    links = [{"link_id": f"link:{oid}:{run_id}", "predicate": "input-to-model-run", "subject_id": oid, "object_id": run_id} for oid in input_object_ids]
    packet = {
        "schema": PROJECT_PACKET_SCHEMA,
        "objects": [model_object],
        "provenance": [event],
        "links": links,
    }
    return {
        "ok": True,
        "schema": "sc-carbon-nature-soc-project-handoff/0.6.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "packet": packet,
        "profile_result": profile,
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
        "fixed_depth_basis_explicit": True,
        "equivalent_soil_mass_not_implemented": True,
        "stock_change_not_inferred": True,
        "sequestration_rate_not_inferred": True,
        "co2e_not_inferred": True,
        "uncertainty_not_inferred": True,
        "methodology_not_selected_automatically": True,
        "additionality_not_determined": True,
        "permanence_not_determined": True,
        "credit_eligibility_not_determined": True,
        "verification_not_performed": True,
        "input_measurements_not_treated_as_verified": True,
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain": "Carbon & Nature Intelligence",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "engine_version": ENGINE_VERSION,
        "basis": "fixed-depth-fine-earth-corrected",
        "capabilities": {
            "soc_concentration_normalization": True,
            "bulk_density_normalization": True,
            "depth_normalization": True,
            "coarse_fragment_correction": True,
            "layer_soc_stock": True,
            "profile_soc_stock": True,
            "parcel_area_scaling": True,
            "project_packet_handoff": True,
            "deterministic_fingerprints": True,
        },
        "limits": {"max_layers": MAX_LAYERS, "max_profile_depth_cm": MAX_PROFILE_DEPTH_CM, "max_area_ha": MAX_AREA_HA},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "schemas": {
            "layer": LAYER_SCHEMA,
            "profile": PROFILE_SCHEMA,
            "result": RESULT_SCHEMA,
            "project_packet": PROJECT_PACKET_SCHEMA,
        },
        "required_layer_fields": ["bottom_depth", "soc_value", "bulk_density_value"],
        "optional_layer_fields": ["layer_id", "top_depth", "depth_unit", "soc_unit", "bulk_density_unit", "coarse_fragments_percent", "sample_id", "observation_id", "methodology_key", "source_refs", "notes"],
        "canonical_units": {"depth": "cm", "soc_concentration": "g/kg", "bulk_density": "g/cm3", "stock": "Mg C/ha", "area": "ha"},
        "accepted_units": {"depth": ["cm", "mm", "m"], "soc_concentration": ["g/kg", "mg/g", "percent", "fraction"], "bulk_density": ["g/cm3", "Mg/m3", "t/m3", "kg/m3"]},
        "guardrails": _guardrails(),
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "soil-organic-carbon-foundation-ready",
        "domain": "Carbon & Nature Intelligence",
        "domain_version": DOMAIN_VERSION,
        "release": "Soil Organic Carbon Lab Foundation",
        "lab_release_version": LAB_RELEASE_VERSION,
        "compute_core_version": ENGINE_VERSION,
        "fixed_depth_soc_stock": True,
        "profile_aggregation": True,
        "project_packet_handoff": True,
        "guardrails": _guardrails(),
    }
