from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

from .soil_organic_carbon_v0890 import calculate_profile_stock

LAB_RELEASE_VERSION = "0.90.0"
DOMAIN_VERSION = "0.7.0"
ENGINE_VERSION = "1.0.0"
SAMPLE_SCHEMA = "sc-carbon-nature-soc-field-sample/0.7.0"
BATCH_SCHEMA = "sc-carbon-nature-soc-field-sample-batch/0.7.0"
DESIGN_SCHEMA = "sc-carbon-nature-soc-sampling-design/0.7.0"
HANDOFF_SCHEMA = "sc-carbon-nature-soc-profile-input-handoff/0.7.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_SAMPLES = 10000
MAX_CUSTODY_EVENTS = 100
MAX_STRATA = 500
MAX_DEPTH_CM = 500.0
SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,159}$")

SAMPLING_METHODS = {
    "simple-random", "systematic-grid", "stratified-random", "transect",
    "paired", "composite", "purposive", "other",
}
SAMPLE_TYPES = {"intact-core", "bulk-disturbed", "auger", "composite", "other"}
MASS_BASES = {"whole-dry-soil", "fine-earth-only"}
CUSTODY_EVENT_TYPES = {"collected", "transferred", "received", "subsampled", "analyzed", "stored", "disposed"}


class SoilCarbonSamplingV0700Error(ValueError):
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
        raise SoilCarbonSamplingV0700Error(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise SoilCarbonSamplingV0700Error(f"{label} must be finite")
    return out


def _optional_text(value: Any, max_len: int = 1000) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > max_len:
        raise SoilCarbonSamplingV0700Error(f"text value exceeds {max_len} characters")
    return text


def _safe_id(value: Any, label: str, required: bool = False) -> str | None:
    text = _optional_text(value, 160)
    if not text:
        if required:
            raise SoilCarbonSamplingV0700Error(f"{label} is required")
        return None
    if not SAFE_ID.fullmatch(text):
        raise SoilCarbonSamplingV0700Error(f"{label} must use letters, numbers, dot, underscore, colon, or hyphen")
    return text


def _planned_sample_id(design_id: str, stratum_id: str, sequence: int) -> str:
    candidate = f"sample:{design_id}:{stratum_id}:{sequence:04d}"
    if len(candidate) <= 160 and SAFE_ID.fullmatch(candidate):
        return candidate
    digest = _hash({"design_id": design_id, "stratum_id": stratum_id, "sequence": sequence})[:32]
    return f"sample:planned:{digest}:{sequence:04d}"


def _iso(value: Any, label: str, required: bool = False) -> str | None:
    text = _optional_text(value, 80)
    if not text:
        if required:
            raise SoilCarbonSamplingV0700Error(f"{label} is required")
        return None
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SoilCarbonSamplingV0700Error(f"{label} must be an ISO-8601 date or timestamp") from exc
    return text


def _string_list(value: Any, label: str, limit: int = 100) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > limit:
        raise SoilCarbonSamplingV0700Error(f"{label} must be a list with at most {limit} entries")
    out: list[str] = []
    for item in value:
        text = _optional_text(item, 300)
        if text and text not in out:
            out.append(text)
    return out


def _depth_cm(value: Any, unit: Any, label: str) -> float:
    n = _number(value, label)
    u = str(unit or "cm").strip().lower().replace(" ", "")
    factor = {"cm": 1.0, "mm": 0.1, "m": 100.0}.get(u)
    if factor is None:
        raise SoilCarbonSamplingV0700Error(f"{label} unit must be cm, mm, or m")
    out = n * factor
    if out < 0 or out > MAX_DEPTH_CM:
        raise SoilCarbonSamplingV0700Error(f"{label} must normalize to 0..{MAX_DEPTH_CM:g} cm")
    return out


def _soc_gkg(value: Any, unit: Any) -> float:
    n = _number(value, "soc_value")
    u = str(unit or "g/kg").strip().lower().replace(" ", "")
    if u in {"g/kg", "gkg", "gkg-1", "gkg^-1", "mg/g", "mgg-1"}:
        out = n
    elif u in {"%", "percent", "percentage"}:
        out = n * 10.0
    elif u in {"fraction", "kg/kg", "kgkg-1", "kgkg^-1"}:
        out = n * 1000.0
    else:
        raise SoilCarbonSamplingV0700Error("soc_unit must be g/kg, mg/g, percent, or fraction")
    if out < 0 or out > 1000:
        raise SoilCarbonSamplingV0700Error("SOC concentration must normalize to 0..1000 g/kg")
    return out


def _bulk_density(value: Any, unit: Any) -> float:
    n = _number(value, "bulk_density_value")
    u = str(unit or "g/cm3").strip().lower().replace(" ", "").replace("³", "3")
    if u in {"g/cm3", "gcm-3", "gcm^-3", "mg/m3", "mgm-3", "mgm^-3", "t/m3", "tm-3", "tm^-3"}:
        out = n
    elif u in {"kg/m3", "kgm-3", "kgm^-3"}:
        out = n / 1000.0
    else:
        raise SoilCarbonSamplingV0700Error("bulk_density_unit must be g/cm3, Mg/m3, t/m3, or kg/m3")
    if out <= 0 or out > 3.5:
        raise SoilCarbonSamplingV0700Error("bulk density must normalize to >0 and <=3.5 g/cm3")
    return out


def calculate_bulk_density(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonSamplingV0700Error("bulk-density request must be an object")
    dry_mass_g = _number(payload.get("dry_mass_g"), "dry_mass_g")
    core_volume_cm3 = _number(payload.get("core_volume_cm3"), "core_volume_cm3")
    if dry_mass_g <= 0 or core_volume_cm3 <= 0:
        raise SoilCarbonSamplingV0700Error("dry_mass_g and core_volume_cm3 must be >0")
    basis = str(payload.get("mass_basis") or "whole-dry-soil").strip().lower()
    if basis not in MASS_BASES:
        raise SoilCarbonSamplingV0700Error("mass_basis must be whole-dry-soil or fine-earth-only")
    bd = dry_mass_g / core_volume_cm3
    if bd > 3.5:
        raise SoilCarbonSamplingV0700Error("calculated bulk density exceeds 3.5 g/cm3; inspect mass/volume units")
    result = {
        "ok": True,
        "schema": "sc-carbon-nature-soc-bulk-density-result/0.7.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "dry_mass_g": dry_mass_g,
        "core_volume_cm3": core_volume_cm3,
        "mass_basis": basis,
        "bulk_density_g_cm3": bd,
        "equation": "bulk_density_g_cm3 = oven_dry_mass_g / core_volume_cm3",
        "guardrails": {
            "oven_dry_basis_must_be_confirmed_by_user": True,
            "coarse_fragment_correction_not_applied_to_bulk_density_result": True,
            "field_measurement_not_treated_as_verified": True,
        },
    }
    result["result_fingerprint"] = _hash(result)
    return result


def _coordinates(payload: dict[str, Any]) -> dict[str, Any] | None:
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    if lat in (None, "") and lon in (None, ""):
        return None
    if lat in (None, "") or lon in (None, ""):
        raise SoilCarbonSamplingV0700Error("latitude and longitude must be supplied together")
    lat_n, lon_n = _number(lat, "latitude"), _number(lon, "longitude")
    if not (-90 <= lat_n <= 90) or not (-180 <= lon_n <= 180):
        raise SoilCarbonSamplingV0700Error("latitude/longitude are outside WGS84 coordinate bounds")
    return {"latitude": lat_n, "longitude": lon_n, "crs": "EPSG:4326"}


def _custody_events(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > MAX_CUSTODY_EVENTS:
        raise SoilCarbonSamplingV0700Error(f"custody_events must contain at most {MAX_CUSTODY_EVENTS} entries")
    out = []
    seen_event_ids: set[str] = set()
    for i, event in enumerate(value):
        if not isinstance(event, dict):
            raise SoilCarbonSamplingV0700Error(f"custody_events[{i}] must be an object")
        kind = str(event.get("event_type") or "").strip().lower()
        if kind not in CUSTODY_EVENT_TYPES:
            raise SoilCarbonSamplingV0700Error(f"custody_events[{i}].event_type is not supported")
        event_id = _safe_id(event.get("event_id") or f"custody-{i+1}", f"custody_events[{i}].event_id", True)
        if event_id in seen_event_ids:
            raise SoilCarbonSamplingV0700Error("custody event_id values must be unique within a sample")
        seen_event_ids.add(event_id)
        row = {
            "event_id": event_id,
            "event_type": kind,
            "occurred_at": _iso(event.get("occurred_at"), f"custody_events[{i}].occurred_at", True),
            "actor_ref": _safe_id(event.get("actor_ref"), f"custody_events[{i}].actor_ref"),
            "location": _optional_text(event.get("location"), 300),
            "notes": _optional_text(event.get("notes"), 1000),
        }
        out.append(row)
    return out


def normalize_sample(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonSamplingV0700Error(f"samples[{index}] must be an object")
    sample_id = _safe_id(payload.get("sample_id"), f"samples[{index}].sample_id", True)
    depth_unit = payload.get("depth_unit") or "cm"
    top = _depth_cm(payload.get("top_depth", 0), depth_unit, f"samples[{index}].top_depth")
    bottom = _depth_cm(payload.get("bottom_depth"), depth_unit, f"samples[{index}].bottom_depth")
    if bottom <= top:
        raise SoilCarbonSamplingV0700Error(f"samples[{index}] bottom_depth must be greater than top_depth")
    sample_type = str(payload.get("sample_type") or "bulk-disturbed").strip().lower()
    if sample_type not in SAMPLE_TYPES:
        raise SoilCarbonSamplingV0700Error(f"samples[{index}].sample_type is not supported")
    method = str(payload.get("sampling_method") or "other").strip().lower()
    if method not in SAMPLING_METHODS:
        raise SoilCarbonSamplingV0700Error(f"samples[{index}].sampling_method is not supported")
    cf = _number(payload.get("coarse_fragments_percent", 0), f"samples[{index}].coarse_fragments_percent")
    if cf < 0 or cf >= 100:
        raise SoilCarbonSamplingV0700Error(f"samples[{index}].coarse_fragments_percent must be >=0 and <100")

    direct_bd = None
    if payload.get("bulk_density_value") not in (None, ""):
        direct_bd = _bulk_density(payload.get("bulk_density_value"), payload.get("bulk_density_unit") or "g/cm3")
    has_mass = payload.get("dry_mass_g") not in (None, "")
    has_volume = payload.get("core_volume_cm3") not in (None, "")
    if has_mass != has_volume:
        raise SoilCarbonSamplingV0700Error(f"samples[{index}] dry_mass_g and core_volume_cm3 must be supplied together")
    calculated_bd = None
    mass_basis = None
    if has_mass:
        bd_result = calculate_bulk_density(payload)
        calculated_bd = bd_result["bulk_density_g_cm3"]
        mass_basis = bd_result["mass_basis"]
        if direct_bd is not None and abs(direct_bd - calculated_bd) > 1e-6:
            raise SoilCarbonSamplingV0700Error(f"samples[{index}] supplied and core-calculated bulk density disagree")
    bulk_density = direct_bd if direct_bd is not None else calculated_bd

    soc = None
    if payload.get("soc_value") not in (None, ""):
        soc = _soc_gkg(payload.get("soc_value"), payload.get("soc_unit") or "g/kg")

    replicate_value = _number(payload.get("replicate", 1), f"samples[{index}].replicate")
    replicate = int(replicate_value)
    if replicate_value != replicate or replicate < 1 or replicate > 10000:
        raise SoilCarbonSamplingV0700Error(f"samples[{index}].replicate must be an integer from 1..10000")

    row: dict[str, Any] = {
        "schema": SAMPLE_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "sample_id": sample_id,
        "field_event_id": _safe_id(payload.get("field_event_id"), f"samples[{index}].field_event_id"),
        "project_id": _safe_id(payload.get("project_id"), f"samples[{index}].project_id"),
        "parcel_id": _safe_id(payload.get("parcel_id"), f"samples[{index}].parcel_id"),
        "stratum_id": _safe_id(payload.get("stratum_id"), f"samples[{index}].stratum_id"),
        "plot_id": _safe_id(payload.get("plot_id"), f"samples[{index}].plot_id"),
        "profile_id": _safe_id(payload.get("profile_id"), f"samples[{index}].profile_id"),
        "replicate": replicate,
        "sample_type": sample_type,
        "sampling_method": method,
        "collected_at": _iso(payload.get("collected_at"), f"samples[{index}].collected_at"),
        "collector_ref": _safe_id(payload.get("collector_ref"), f"samples[{index}].collector_ref"),
        "coordinates": _coordinates(payload),
        "top_depth_cm": top,
        "bottom_depth_cm": bottom,
        "thickness_cm": bottom - top,
        "coarse_fragments_percent": cf,
        "core_volume_cm3": _number(payload.get("core_volume_cm3"), "core_volume_cm3") if has_volume else None,
        "dry_mass_g": _number(payload.get("dry_mass_g"), "dry_mass_g") if has_mass else None,
        "mass_basis": mass_basis,
        "bulk_density_g_cm3": bulk_density,
        "bulk_density_origin": "core-calculated" if calculated_bd is not None else ("supplied" if direct_bd is not None else None),
        "soc_g_per_kg": soc,
        "soc_percent": soc / 10.0 if soc is not None else None,
        "lab_sample_id": _safe_id(payload.get("lab_sample_id"), f"samples[{index}].lab_sample_id"),
        "lab_method_ref": _safe_id(payload.get("lab_method_ref"), f"samples[{index}].lab_method_ref"),
        "source_refs": _string_list(payload.get("source_refs"), f"samples[{index}].source_refs"),
        "custody_events": _custody_events(payload.get("custody_events")),
        "notes": _optional_text(payload.get("notes"), 2000),
    }
    warnings: list[str] = []
    if row["collected_at"] is None: warnings.append("collection timestamp not supplied")
    if row["collector_ref"] is None: warnings.append("collector reference not supplied")
    if row["coordinates"] is None: warnings.append("WGS84 coordinates not supplied")
    if row["soc_g_per_kg"] is not None and row["lab_method_ref"] is None: warnings.append("SOC result has no lab_method_ref")
    if row["soc_g_per_kg"] is not None and not row["custody_events"]: warnings.append("SOC result has no chain-of-custody events")
    row["readiness"] = {
        "field_identity_complete": bool(row["sample_id"] and row["parcel_id"] and row["profile_id"]),
        "soc_profile_input_ready": row["soc_g_per_kg"] is not None and row["bulk_density_g_cm3"] is not None,
        "provenance_complete": bool(row["collected_at"] and row["collector_ref"] and row["source_refs"]),
        "warnings": warnings,
    }
    row["sample_fingerprint"] = _hash({k: v for k, v in row.items() if k != "sample_fingerprint"})
    return row


def normalize_batch(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonSamplingV0700Error("sample-batch request must be an object")
    samples = payload.get("samples")
    if not isinstance(samples, list) or not samples or len(samples) > MAX_SAMPLES:
        raise SoilCarbonSamplingV0700Error(f"samples must contain 1..{MAX_SAMPLES} records")
    rows = [normalize_sample(row, i) for i, row in enumerate(samples)]
    ids = [row["sample_id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise SoilCarbonSamplingV0700Error("sample_id values must be unique within a batch")
    strata: dict[str, int] = {}
    methods: dict[str, int] = {}
    ready = 0
    for row in rows:
        strata[row["stratum_id"] or "unstratified"] = strata.get(row["stratum_id"] or "unstratified", 0) + 1
        methods[row["sampling_method"]] = methods.get(row["sampling_method"], 0) + 1
        ready += int(row["readiness"]["soc_profile_input_ready"])
    result = {
        "ok": True,
        "schema": BATCH_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "batch_id": _safe_id(payload.get("batch_id") or "batch:soc-field-samples", "batch_id", True),
        "sample_count": len(rows),
        "profile_ready_count": ready,
        "strata_counts": strata,
        "method_counts": methods,
        "samples": rows,
        "guardrails": _guardrails(),
    }
    result["batch_fingerprint"] = _hash({k: v for k, v in result.items() if k != "batch_fingerprint"})
    return result


def build_sampling_design(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SoilCarbonSamplingV0700Error("sampling-design request must be an object")
    design_id = _safe_id(payload.get("design_id"), "design_id", True)
    method = str(payload.get("sampling_method") or "stratified-random").strip().lower()
    if method not in SAMPLING_METHODS:
        raise SoilCarbonSamplingV0700Error("sampling_method is not supported")
    strata = payload.get("strata")
    if not isinstance(strata, list) or not strata or len(strata) > MAX_STRATA:
        raise SoilCarbonSamplingV0700Error(f"strata must contain 1..{MAX_STRATA} entries")
    planned = []
    normalized_strata = []
    seen_strata: set[str] = set()
    total = 0
    for i, stratum in enumerate(strata):
        if not isinstance(stratum, dict):
            raise SoilCarbonSamplingV0700Error(f"strata[{i}] must be an object")
        sid = _safe_id(stratum.get("stratum_id"), f"strata[{i}].stratum_id", True)
        if sid in seen_strata:
            raise SoilCarbonSamplingV0700Error("stratum_id values must be unique within a sampling design")
        seen_strata.add(sid)
        target_f = _number(stratum.get("target_samples"), f"strata[{i}].target_samples")
        target = int(target_f)
        if target != target_f or target < 1:
            raise SoilCarbonSamplingV0700Error(f"strata[{i}].target_samples must be a positive integer")
        total += target
        if total > MAX_SAMPLES:
            raise SoilCarbonSamplingV0700Error(f"total planned samples must not exceed {MAX_SAMPLES}")
        normalized_strata.append({"stratum_id": sid, "target_samples": target, "notes": _optional_text(stratum.get("notes"), 1000)})
        for j in range(1, target + 1):
            planned.append({
                "sample_id": _planned_sample_id(design_id, sid, j),
                "stratum_id": sid,
                "sequence": j,
                "status": "planned",
                "coordinates": None,
            })
    out = {
        "ok": True,
        "schema": DESIGN_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "design_id": design_id,
        "project_id": _safe_id(payload.get("project_id"), "project_id"),
        "parcel_id": _safe_id(payload.get("parcel_id"), "parcel_id"),
        "sampling_method": method,
        "strata": normalized_strata,
        "target_sample_count": total,
        "planned_samples": planned,
        "design_notes": _optional_text(payload.get("design_notes"), 3000),
        "design_boundaries": {
            "sample_ids_generated": True,
            "spatial_randomization_performed": False,
            "coordinates_generated": False,
            "power_analysis_performed": False,
            "sample_size_adequacy_determined": False,
        },
        "guardrails": _guardrails(),
    }
    out["design_fingerprint"] = _hash({k: v for k, v in out.items() if k != "design_fingerprint"})
    return out


def build_profile_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    batch = normalize_batch(payload)
    ready = [row for row in batch["samples"] if row["readiness"]["soc_profile_input_ready"]]
    if not ready:
        raise SoilCarbonSamplingV0700Error("no samples contain both SOC concentration and bulk density")
    requested_profile_id = _safe_id(payload.get("profile_id"), "profile_id")
    row_profile_ids = {row["profile_id"] for row in ready if row["profile_id"]}
    if len(row_profile_ids) > 1:
        raise SoilCarbonSamplingV0700Error("profile handoff cannot mix multiple profile_id values")
    if requested_profile_id and row_profile_ids and requested_profile_id not in row_profile_ids:
        raise SoilCarbonSamplingV0700Error("profile_id conflicts with profile_id on profile-ready samples")
    profile_id = requested_profile_id or (next(iter(row_profile_ids)) if row_profile_ids else "profile:soc-field-handoff")
    intervals: set[tuple[float, float]] = set()
    layers = []
    for row in sorted(ready, key=lambda r: (r["top_depth_cm"], r["bottom_depth_cm"], r["sample_id"])):
        interval = (row["top_depth_cm"], row["bottom_depth_cm"])
        if interval in intervals:
            raise SoilCarbonSamplingV0700Error("multiple profile-ready samples share a depth interval; replicate aggregation must be explicit and is not inferred in v0.7.0")
        intervals.add(interval)
        layers.append({
            "layer_id": row["sample_id"],
            "top_depth": row["top_depth_cm"],
            "bottom_depth": row["bottom_depth_cm"],
            "depth_unit": "cm",
            "soc_value": row["soc_g_per_kg"],
            "soc_unit": "g/kg",
            "bulk_density_value": row["bulk_density_g_cm3"],
            "bulk_density_unit": "g/cm3",
            "coarse_fragments_percent": row["coarse_fragments_percent"],
            "sample_id": row["sample_id"],
            "observation_id": f"observation:{row['sample_id']}:soc",
            "source_refs": row["source_refs"],
            "notes": "Prepared from governed field-sample record; no replicate averaging or stock-change inference performed.",
        })
    profile = {
        "profile_id": profile_id,
        "area_ha": payload.get("area_ha"),
        "layers": layers,
        "source_refs": sorted({ref for row in ready for ref in row["source_refs"]}),
    }
    # Validate compatibility by invoking the v0.6.0 fixed-depth calculator, but keep the handoff result explicit.
    validated = calculate_profile_stock(profile)
    out = {
        "ok": True,
        "schema": HANDOFF_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "target": "Carbon & Nature v0.6.0 fixed-depth SOC stock engine",
        "profile_input": profile,
        "compatibility_validation": {
            "ok": True,
            "target_schema": "sc-carbon-nature-soc-profile/0.6.0",
            "layer_count": len(layers),
            "validated_result_fingerprint": validated["result_fingerprint"],
            "calculated_stock_Mg_C_ha": validated["soc_stock_Mg_C_ha"],
        },
        "excluded_sample_ids": [row["sample_id"] for row in batch["samples"] if not row["readiness"]["soc_profile_input_ready"]],
        "guardrails": _guardrails(),
    }
    out["handoff_fingerprint"] = _hash({k: v for k, v in out.items() if k != "handoff_fingerprint"})
    return out


def build_field_packet(payload: dict[str, Any]) -> dict[str, Any]:
    batch = normalize_batch(payload)
    objects: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    requested_project_id = _safe_id(payload.get("project_id"), "project_id")
    sample_project_ids = {x["project_id"] for x in batch["samples"] if x["project_id"]}
    if len(sample_project_ids) > 1:
        raise SoilCarbonSamplingV0700Error("field packet cannot mix multiple project_id values")
    if requested_project_id and sample_project_ids and requested_project_id not in sample_project_ids:
        raise SoilCarbonSamplingV0700Error("project_id conflicts with project_id on field samples")
    project_id = requested_project_id or (next(iter(sample_project_ids)) if sample_project_ids else None)
    project_id = _safe_id(project_id, "project_id", True)
    for row in batch["samples"]:
        sample_obj_id = row["sample_id"] if row["sample_id"].startswith("sample:") else f"sample:{row['sample_id']}"
        sample_obj = {
            "object_id": sample_obj_id,
            "object_type": "sample",
            "project_id": project_id,
            "version": 1,
            "status": "draft",
            "payload": row,
            "source_refs": row["source_refs"],
            "provenance_refs": [f"event:{sample_obj_id}:collected"] if row["collected_at"] else [],
            "parent_object_ids": [row["parcel_id"]] if row["parcel_id"] else [],
            "evidence_refs": [], "methodology_refs": [], "measure_refs": [],
        }
        sample_obj["content_fingerprint"] = _hash({k:v for k,v in sample_obj.items() if k!="content_fingerprint"})
        objects.append(sample_obj)
        if row["collected_at"]:
            provenance.append({
                "event_id": f"event:{sample_obj_id}:collected", "event_type": "collected", "object_id": sample_obj_id,
                "occurred_at": row["collected_at"], "actor_ref": row["collector_ref"] or "actor:unrecorded",
                "source_refs": row["source_refs"], "sample_fingerprint": row["sample_fingerprint"],
            })
        if row["soc_g_per_kg"] is not None:
            oid=f"observation:{row['sample_id']}:soc"
            obs={"object_id":oid,"object_type":"observation","project_id":project_id,"version":1,"status":"draft","payload":{"observation_type":"soil-organic-carbon-concentration","value":row["soc_g_per_kg"],"unit":"g/kg","sample_id":sample_obj_id,"lab_sample_id":row["lab_sample_id"],"lab_method_ref":row["lab_method_ref"]},"source_refs":row["source_refs"],"provenance_refs":[],"parent_object_ids":[sample_obj_id],"evidence_refs":[],"methodology_refs":[row["lab_method_ref"]] if row["lab_method_ref"] else [],"measure_refs":[]}
            obs["content_fingerprint"]=_hash({k:v for k,v in obs.items() if k!="content_fingerprint"}); objects.append(obs)
            links.append({"link_id":f"link:{sample_obj_id}:{oid}","predicate":"sample-to-observation","subject_id":sample_obj_id,"object_id":oid})
        if row["bulk_density_g_cm3"] is not None:
            oid=f"observation:{row['sample_id']}:bulk-density"
            obs={"object_id":oid,"object_type":"observation","project_id":project_id,"version":1,"status":"draft","payload":{"observation_type":"soil-bulk-density","value":row["bulk_density_g_cm3"],"unit":"g/cm3","origin":row["bulk_density_origin"],"mass_basis":row["mass_basis"],"sample_id":sample_obj_id},"source_refs":row["source_refs"],"provenance_refs":[],"parent_object_ids":[sample_obj_id],"evidence_refs":[],"methodology_refs":[],"measure_refs":[]}
            obs["content_fingerprint"]=_hash({k:v for k,v in obs.items() if k!="content_fingerprint"}); objects.append(obs)
            links.append({"link_id":f"link:{sample_obj_id}:{oid}","predicate":"sample-to-observation","subject_id":sample_obj_id,"object_id":oid})
    packet={"schema":PROJECT_PACKET_SCHEMA,"objects":objects,"provenance":provenance,"links":links}
    return {
        "ok": True,
        "schema": "sc-carbon-nature-soc-field-project-handoff/0.7.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "packet": packet,
        "sample_count": batch["sample_count"],
        "object_count": len(objects),
        "packet_fingerprint": _hash(packet),
        "guardrails": _guardrails(),
    }


def _guardrails() -> dict[str, bool]:
    return {
        "field_measurements_not_treated_as_verified": True,
        "sampling_design_not_treated_as_statistically_adequate": True,
        "spatial_randomization_not_inferred": True,
        "coordinates_not_generated": True,
        "replicate_aggregation_not_inferred": True,
        "stock_change_not_inferred": True,
        "sequestration_rate_not_inferred": True,
        "uncertainty_not_inferred": True,
        "co2e_not_inferred": True,
        "methodology_eligibility_not_determined": True,
        "additionality_not_determined": True,
        "permanence_not_determined": True,
        "credit_eligibility_not_determined": True,
        "chain_of_custody_not_digitally_signed": True,
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain": "Carbon & Nature Intelligence",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "release": "SOC Sampling & Field Measurement Studio",
        "sampling_methods": sorted(SAMPLING_METHODS),
        "sample_types": sorted(SAMPLE_TYPES),
        "mass_bases": sorted(MASS_BASES),
        "custody_event_types": sorted(CUSTODY_EVENT_TYPES),
        "limits": {"max_samples": MAX_SAMPLES, "max_strata": MAX_STRATA, "max_depth_cm": MAX_DEPTH_CM, "max_custody_events_per_sample": MAX_CUSTODY_EVENTS},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "schemas": {"sample": SAMPLE_SCHEMA, "batch": BATCH_SCHEMA, "design": DESIGN_SCHEMA, "profile_handoff": HANDOFF_SCHEMA, "project_packet": PROJECT_PACKET_SCHEMA},
        "canonical_units": {"depth":"cm","soc_concentration":"g/kg","bulk_density":"g/cm3","core_volume":"cm3","dry_mass":"g","coordinates":"EPSG:4326"},
        "required_sample_fields": ["sample_id", "bottom_depth"],
        "profile_ready_fields": ["sample_id", "top_depth", "bottom_depth", "soc_value", "bulk_density_value-or-core-mass-volume"],
        "guardrails": _guardrails(),
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "soc-sampling-field-measurement-ready",
        "domain": "Carbon & Nature Intelligence",
        "domain_version": DOMAIN_VERSION,
        "release": "SOC Sampling & Field Measurement Studio",
        "lab_release_version": LAB_RELEASE_VERSION,
        "compute_core_version": ENGINE_VERSION,
        "sample_normalization": True,
        "sampling_plan_registry": True,
        "bulk_density_core_calculation": True,
        "chain_of_custody_metadata": True,
        "soc_v0600_profile_handoff": True,
        "carbon_project_packet_handoff": True,
        "guardrails": _guardrails(),
    }
