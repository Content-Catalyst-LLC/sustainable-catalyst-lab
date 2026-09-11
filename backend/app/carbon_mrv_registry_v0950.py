from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

LAB_RELEASE_VERSION = "0.95.0"
DOMAIN_VERSION = "0.12.0"
ENGINE_VERSION = "1.0.0"
REGISTRY_VERSION = "1.0.0"
METHOD_SCHEMA = "sc-carbon-nature-mrv-method/0.12.0"
REGISTRY_SCHEMA = "sc-carbon-nature-mrv-method-registry/0.12.0"
READINESS_SCHEMA = "sc-carbon-nature-mrv-method-readiness/0.12.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_METHODS_COMPARE = 20
MAX_REFS = 100

class CarbonMRVRegistryV01200Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _text(value: Any, label: str, required: bool = False, max_len: int = 240) -> str | None:
    if value is None:
        if required:
            raise CarbonMRVRegistryV01200Error(f"{label} is required")
        return None
    out = str(value).strip()
    if not out:
        if required:
            raise CarbonMRVRegistryV01200Error(f"{label} is required")
        return None
    if len(out) > max_len:
        raise CarbonMRVRegistryV01200Error(f"{label} exceeds {max_len} characters")
    return out


def _refs(value: Any, label: str) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVRegistryV01200Error(f"{label} must be an array")
    if len(value) > MAX_REFS:
        raise CarbonMRVRegistryV01200Error(f"{label} may contain at most {MAX_REFS} values")
    out: list[str] = []
    for i, item in enumerate(value):
        ref = _text(item, f"{label}[{i}]", True)
        assert ref is not None
        if ref not in out:
            out.append(ref)
    return out


def _profile(
    key: str,
    title: str,
    method_type: str,
    summary: str,
    applies_to: list[str],
    carbon_pools: list[str],
    gases: list[str],
    measurement_basis: list[str],
    required_inputs: list[str],
    required_evidence: list[str],
    outputs: list[str],
    uncertainty_expectations: list[str],
    quality_controls: list[str],
    library_methodology_key: str,
) -> dict[str, Any]:
    rec = {
        "schema": METHOD_SCHEMA,
        "method_key": key,
        "title": title,
        "method_type": method_type,
        "summary": summary,
        "status": "foundation-profile",
        "applies_to": applies_to,
        "carbon_pools": carbon_pools,
        "gases": gases,
        "measurement_basis": measurement_basis,
        "required_inputs": required_inputs,
        "required_evidence": required_evidence,
        "outputs": outputs,
        "uncertainty_expectations": uncertainty_expectations,
        "quality_controls": quality_controls,
        "library_methodology_key": library_methodology_key,
        "source_refs": [f"library-methodology:{library_methodology_key}"],
        "interpretation": "Foundation MRV method profile for research planning. It is not an external protocol, certification, verification decision, or crediting methodology approval.",
    }
    rec["profile_fingerprint"] = _hash(rec)
    return rec


_METHODS = [
    _profile(
        "soc-direct-measurement", "SOC Direct Measurement", "direct-measurement",
        "Direct soil sampling and laboratory measurement used to estimate soil organic carbon stocks at explicit depths.",
        ["cropland", "grassland", "agroforestry", "managed-soils"], ["soil-organic-carbon"], ["CO2"],
        ["field-sampling", "laboratory-analysis", "bulk-density"],
        ["sampling-design", "sampling-depths", "soc-concentration", "bulk-density", "coarse-fragments"],
        ["field-records", "laboratory-results", "chain-of-custody", "method-references"],
        ["soc-stock", "soc-stock-change-when-temporally-matched"],
        ["sampling-variation", "laboratory-analytical-uncertainty", "bulk-density-uncertainty", "spatial-variability"],
        ["sample-identity", "depth-consistency", "replicate-controls", "laboratory-method-record", "data-quality-review"],
        "soc-direct-measurement",
    ),
    _profile(
        "soc-sampling-design", "SOC Sampling Design", "sampling-design",
        "Sampling-design framework for documenting strata, sample locations, depth intervals, replicates, and field collection plans.",
        ["cropland", "grassland", "agroforestry", "managed-soils"], ["soil-organic-carbon"], [],
        ["sampling-frame", "stratification", "field-design"],
        ["spatial-unit", "target-depths", "strata", "replicate-plan"],
        ["sampling-plan", "site-map-or-location-record", "field-protocol"],
        ["sampling-design-record", "field-sample-identifiers"],
        ["representativeness-requires-separate-assessment", "sample-size-adequacy-requires-separate-assessment"],
        ["unique-sample-identities", "explicit-strata", "explicit-depths", "location-provenance"],
        "soc-sampling-design",
    ),
    _profile(
        "modeled-carbon-stock-change", "Modeled Carbon Stock Change", "model-based",
        "Model-based estimation of carbon-stock change using explicit model identity, parameters, inputs, calibration context, and versioned assumptions.",
        ["cropland", "grassland", "forest", "agroforestry", "wetland"], ["soil-organic-carbon", "biomass-carbon"], ["CO2"],
        ["process-model", "empirical-model", "scenario-model"],
        ["baseline-state", "model-version", "parameter-set", "driver-data", "simulation-period"],
        ["model-documentation", "input-provenance", "parameter-provenance", "validation-evidence"],
        ["modeled-stock", "modeled-stock-change", "scenario-trajectory"],
        ["parameter-uncertainty", "input-uncertainty", "model-structural-uncertainty", "scenario-uncertainty"],
        ["version-pinning", "input-fingerprints", "assumption-register", "validation-record"],
        "modeled-carbon-stock-change",
    ),
    _profile(
        "hybrid-measurement-modeling", "Hybrid Measurement + Modeling", "hybrid",
        "Combines measured observations with a versioned model while preserving which outputs are observed, modeled, calibrated, or inferred.",
        ["cropland", "grassland", "forest", "agroforestry", "wetland"], ["soil-organic-carbon", "biomass-carbon"], ["CO2"],
        ["field-measurement", "laboratory-analysis", "model-calibration", "model-simulation"],
        ["observations", "model-version", "calibration-design", "parameter-set", "prediction-domain"],
        ["measurement-records", "model-documentation", "calibration-evidence", "validation-evidence"],
        ["calibrated-stock", "modeled-change", "diagnostic-record"],
        ["measurement-uncertainty", "calibration-uncertainty", "prediction-uncertainty", "model-structural-uncertainty"],
        ["observation-model-separation", "calibration-holdout-record", "version-pinning", "diagnostic-review"],
        "hybrid-measurement-modeling",
    ),
    _profile(
        "biomass-inventory-measurement", "Biomass Inventory Measurement", "direct-measurement",
        "Field inventory framework for estimating above- and below-ground biomass carbon from explicit measurements and sourced conversion relationships.",
        ["forest", "agroforestry", "woody-biomass"], ["above-ground-biomass", "below-ground-biomass"], ["CO2"],
        ["field-inventory", "allometry", "biomass-carbon-conversion"],
        ["plot-design", "tree-or-vegetation-measurements", "allometric-model", "carbon-fraction-or-conversion"],
        ["inventory-records", "allometry-source", "conversion-source", "plot-provenance"],
        ["biomass-carbon-stock", "biomass-carbon-stock-change-when-temporally-matched"],
        ["sampling-variation", "measurement-error", "allometric-uncertainty", "conversion-uncertainty"],
        ["plot-identities", "measurement-protocol", "species-or-group-mapping", "equation-version-record"],
        "biomass-inventory-measurement",
    ),
    _profile(
        "wetland-multigas-monitoring", "Wetland Multi-Gas Monitoring", "multi-gas-monitoring",
        "Monitoring framework for wetland or peatland interventions where carbon-stock change and non-CO2 greenhouse-gas fluxes must remain explicit and separately sourced.",
        ["wetland", "peatland"], ["soil-organic-carbon", "biomass-carbon"], ["CO2", "CH4", "N2O"],
        ["stock-measurement", "flux-measurement", "water-level-or-hydrology-context"],
        ["site-boundary", "monitoring-period", "gas-specific-observations", "hydrological-context"],
        ["measurement-records", "gas-method-references", "hydrology-records", "gwp-source-when-converting-to-co2e"],
        ["gas-specific-fluxes", "carbon-stock-record", "co2e-balance-only-with-explicit-factors"],
        ["temporal-variability", "spatial-variability", "gas-measurement-uncertainty", "conversion-factor-uncertainty"],
        ["gas-specific-provenance", "monitoring-frequency-record", "instrument-method-record", "explicit-gwp-source"],
        "wetland-multigas-monitoring",
    ),
    _profile(
        "whole-system-ghg-accounting", "Whole-System GHG Accounting", "accounting",
        "System-boundary accounting framework that aggregates explicitly sourced emissions and removals while preserving gas, activity, factor, period, and boundary provenance.",
        ["farm", "land-management-project", "agricultural-system"], ["soil-organic-carbon", "biomass-carbon"], ["CO2", "CH4", "N2O"],
        ["direct-co2e", "gas-mass-with-explicit-gwp", "activity-factor", "carbon-stock-change"],
        ["system-boundary", "accounting-period", "activity-data", "emission-or-removal-factors"],
        ["activity-records", "factor-sources", "gwp-source-when-applicable", "stock-change-evidence-when-included"],
        ["gross-emissions", "gross-removals", "net-ghg-balance"],
        ["activity-data-uncertainty", "factor-uncertainty", "gwp-choice", "stock-change-uncertainty"],
        ["no-hidden-factors", "category-and-gas-separation", "boundary-record", "source-ledger"],
        "whole-system-ghg-accounting",
    ),
]
METHODS = {m["method_key"]: m for m in _METHODS}


def _guardrails() -> dict[str, bool]:
    return {
        "registry_is_not_external_protocol": True,
        "no_automatic_method_selection": True,
        "no_methodology_eligibility_determination": True,
        "no_verification_determination": True,
        "no_credit_eligibility_determination": True,
        "no_current_program_rule_assertion": True,
        "no_automatic_parameter_defaults": True,
        "no_automatic_recommendation": True,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "carbon-mrv-method-registry-ready",
        "service": "Sustainable Catalyst Lab Carbon MRV Method Registry",
        "lab_release_version": LAB_RELEASE_VERSION,
        "domain_version": DOMAIN_VERSION,
        "engine_version": ENGINE_VERSION,
        "registry_version": REGISTRY_VERSION,
        "method_count": len(METHODS),
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "method_schema": METHOD_SCHEMA,
        "registry_schema": REGISTRY_SCHEMA,
        "readiness_schema": READINESS_SCHEMA,
        "method_types": sorted({m["method_type"] for m in METHODS.values()}),
        "carbon_pools": sorted({x for m in METHODS.values() for x in m["carbon_pools"]}),
        "gases": sorted({x for m in METHODS.values() for x in m["gases"]}),
        "status_values": ["foundation-profile"],
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "capabilities": {
            "governed_method_registry": True,
            "method_detail": True,
            "method_filtering": True,
            "method_comparison": True,
            "documentation_readiness": True,
            "library_methodology_crosswalk": True,
            "carbon_project_monitoring_record_handoff": True,
            "deterministic_fingerprints": True,
        },
        "limits": {"max_methods_compare": MAX_METHODS_COMPARE, "max_refs_per_field": MAX_REFS},
        "guardrails": _guardrails(),
    }


def list_methods(method_type: str | None = None, carbon_pool: str | None = None, gas: str | None = None) -> dict[str, Any]:
    mt = str(method_type or "").strip().lower()
    cp = str(carbon_pool or "").strip().lower()
    gg = str(gas or "").strip().upper()
    records = []
    for method in METHODS.values():
        if mt and method["method_type"] != mt:
            continue
        if cp and cp not in {x.lower() for x in method["carbon_pools"]}:
            continue
        if gg and gg not in method["gases"]:
            continue
        records.append(dict(method))
    return {
        "ok": True,
        "schema": REGISTRY_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "filters": {"method_type": mt or None, "carbon_pool": cp or None, "gas": gg or None},
        "count": len(records),
        "methods": records,
        "registry_fingerprint": _hash([m["profile_fingerprint"] for m in records]),
    }


def get_method(method_key: str) -> dict[str, Any]:
    key = _text(method_key, "method_key", True)
    assert key is not None
    if key not in METHODS:
        raise CarbonMRVRegistryV01200Error(f"unknown MRV method: {key}", 404)
    return {"ok": True, "method": dict(METHODS[key])}


def compare_methods(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVRegistryV01200Error("comparison request must be an object")
    keys = _refs(payload.get("method_keys"), "method_keys")
    if not (2 <= len(keys) <= MAX_METHODS_COMPARE):
        raise CarbonMRVRegistryV01200Error(f"method_keys must contain 2..{MAX_METHODS_COMPARE} unique values")
    unknown = [k for k in keys if k not in METHODS]
    if unknown:
        raise CarbonMRVRegistryV01200Error("unknown MRV methods: " + ", ".join(unknown), 404)
    methods = [dict(METHODS[k]) for k in keys]
    dimensions = ["method_type", "applies_to", "carbon_pools", "gases", "measurement_basis", "required_inputs", "required_evidence", "outputs", "uncertainty_expectations", "quality_controls"]
    comparison = {d: {m["method_key"]: m[d] for m in methods} for d in dimensions}
    result = {
        "ok": True,
        "schema": "sc-carbon-nature-mrv-method-comparison/0.12.0",
        "method_keys": keys,
        "methods": methods,
        "comparison": comparison,
        "ranking_performed": False,
        "recommendation_generated": False,
        "interpretation": "Comparison preserves input order and descriptive differences. It does not rank methods or determine methodology eligibility.",
    }
    result["result_fingerprint"] = _hash(result)
    return result


def assess_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVRegistryV01200Error("readiness request must be an object")
    key = _text(payload.get("method_key"), "method_key", True)
    assert key is not None
    if key not in METHODS:
        raise CarbonMRVRegistryV01200Error(f"unknown MRV method: {key}", 404)
    method = METHODS[key]
    available_inputs = _refs(payload.get("available_inputs"), "available_inputs")
    available_evidence = _refs(payload.get("available_evidence"), "available_evidence")
    methodology_refs = _refs(payload.get("methodology_refs"), "methodology_refs")
    source_refs = _refs(payload.get("source_refs"), "source_refs")
    have_inputs = {x.lower() for x in available_inputs}
    have_evidence = {x.lower() for x in available_evidence}
    missing_inputs = [x for x in method["required_inputs"] if x.lower() not in have_inputs]
    missing_evidence = [x for x in method["required_evidence"] if x.lower() not in have_evidence]
    documentation_ready = not missing_inputs and not missing_evidence
    result = {
        "ok": True,
        "schema": READINESS_SCHEMA,
        "method_key": key,
        "documentation_readiness": "ready" if documentation_ready else "incomplete",
        "documentation_ready": documentation_ready,
        "available_inputs": available_inputs,
        "available_evidence": available_evidence,
        "missing_inputs": missing_inputs,
        "missing_evidence": missing_evidence,
        "methodology_refs": methodology_refs,
        "source_refs": source_refs,
        "external_methodology_eligibility": None,
        "verification_status": None,
        "credit_eligibility": None,
        "interpretation": "Readiness only checks whether this Sustainable Catalyst foundation profile has the named documentation fields. It does not establish compliance with an external protocol, verifier requirements, or crediting program rules.",
        "guardrails": _guardrails(),
    }
    result["input_fingerprint"] = _hash(payload)
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVRegistryV01200Error("project packet request must be an object")
    project_id = _text(payload.get("project_id"), "project_id", True)
    actor = _text(payload.get("actor_ref") or "actor:lab-user", "actor_ref", True)
    assert project_id and actor
    readiness_payload = payload.get("readiness")
    if not isinstance(readiness_payload, dict):
        raise CarbonMRVRegistryV01200Error("readiness must be an object")
    readiness = assess_readiness(readiness_payload)
    key = readiness["method_key"]
    object_id = _text(payload.get("object_id") or f"monitoring-record:mrv-{_hash([project_id, key, readiness['result_fingerprint']])[:16]}", "object_id", True)
    refs = []
    for ref in readiness.get("source_refs", []) + readiness.get("methodology_refs", []) + METHODS[key]["source_refs"]:
        if ref not in refs:
            refs.append(ref)
    provenance_id = f"provenance:mrv-method-registry-{readiness['result_fingerprint'][:16]}"
    obj = {
        "object_id": object_id,
        "object_type": "monitoring-record",
        "project_id": project_id,
        "version": "1.0.0",
        "status": "draft",
        "payload": {
            "record_type": "mrv-method-readiness",
            "registry_version": REGISTRY_VERSION,
            "lab_release_version": LAB_RELEASE_VERSION,
            "domain_version": DOMAIN_VERSION,
            "method_key": key,
            "library_methodology_key": METHODS[key]["library_methodology_key"],
            "documentation_readiness": readiness["documentation_readiness"],
            "missing_inputs": readiness["missing_inputs"],
            "missing_evidence": readiness["missing_evidence"],
            "result_fingerprint": readiness["result_fingerprint"],
            "guardrails": readiness["guardrails"],
        },
        "source_refs": refs,
        "evidence_refs": readiness.get("source_refs", []),
        "methodology_refs": readiness.get("methodology_refs", []),
        "provenance_refs": [provenance_id],
    }
    event = {
        "provenance_id": provenance_id,
        "event_type": "created",
        "object_id": object_id,
        "actor_ref": actor,
        "details": {
            "registry_version": REGISTRY_VERSION,
            "method_key": key,
            "documentation_ready": readiness["documentation_ready"],
            "external_methodology_eligibility_determined": False,
        },
    }
    packet = {"schema": PROJECT_PACKET_SCHEMA, "objects": [obj], "provenance": [event], "links": []}
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "packet": packet,
        "readiness": readiness,
        "packet_fingerprint": _hash(packet),
    }
