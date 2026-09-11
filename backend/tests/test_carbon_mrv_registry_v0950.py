from app.carbon_mrv_registry_v0950 import (
    LAB_RELEASE_VERSION, DOMAIN_VERSION, METHODS, CarbonMRVRegistryV01200Error,
    health, schema, policies, list_methods, get_method, compare_methods, assess_readiness, build_project_packet,
)
import pytest

def test_identity_and_registry_count():
    assert LAB_RELEASE_VERSION == "0.95.0"
    assert DOMAIN_VERSION == "0.12.0"
    assert health()["status"] == "carbon-mrv-method-registry-ready"
    assert health()["method_count"] == 7
    assert len(METHODS) == 7
    assert policies()["guardrails"]["no_automatic_method_selection"] is True

def test_method_keys_stable():
    assert list(METHODS) == [
        "soc-direct-measurement","soc-sampling-design","modeled-carbon-stock-change",
        "hybrid-measurement-modeling","biomass-inventory-measurement","wetland-multigas-monitoring",
        "whole-system-ghg-accounting",
    ]

def test_list_filtering():
    assert list_methods(method_type="hybrid")["count"] == 1
    assert list_methods(carbon_pool="soil-organic-carbon")["count"] >= 5
    assert list_methods(gas="CH4")["count"] == 2

def test_detail_and_unknown():
    m=get_method("soc-direct-measurement")["method"]
    assert m["library_methodology_key"] == "soc-direct-measurement"
    assert len(m["profile_fingerprint"]) == 64
    with pytest.raises(CarbonMRVRegistryV01200Error) as exc:
        get_method("not-a-method")
    assert exc.value.status_code == 404

def test_comparison_is_nonranking():
    r=compare_methods({"method_keys":["soc-direct-measurement","modeled-carbon-stock-change"]})
    assert r["ranking_performed"] is False
    assert r["recommendation_generated"] is False
    assert r["method_keys"][0] == "soc-direct-measurement"

def test_comparison_rejects_single_or_unknown():
    with pytest.raises(CarbonMRVRegistryV01200Error): compare_methods({"method_keys":["soc-direct-measurement"]})
    with pytest.raises(CarbonMRVRegistryV01200Error): compare_methods({"method_keys":["soc-direct-measurement","bad"]})

def test_readiness_incomplete_without_requirements():
    r=assess_readiness({"method_key":"soc-direct-measurement","available_inputs":[],"available_evidence":[]})
    assert r["documentation_ready"] is False
    assert "sampling-design" in r["missing_inputs"]
    assert r["external_methodology_eligibility"] is None
    assert r["credit_eligibility"] is None

def test_readiness_ready_when_all_named_requirements_present():
    m=METHODS["soc-direct-measurement"]
    r=assess_readiness({"method_key":"soc-direct-measurement","available_inputs":m["required_inputs"],"available_evidence":m["required_evidence"],"source_refs":["evidence:test"]})
    assert r["documentation_ready"] is True
    assert r["documentation_readiness"] == "ready"
    assert not r["missing_inputs"] and not r["missing_evidence"]

def test_readiness_is_deterministic():
    p={"method_key":"soc-sampling-design","available_inputs":["spatial-unit"],"available_evidence":[]}
    assert assess_readiness(p)["result_fingerprint"] == assess_readiness(p)["result_fingerprint"]

def test_project_packet_monitoring_record_and_guardrails():
    m=METHODS["soc-sampling-design"]
    r=build_project_packet({"project_id":"project:test","readiness":{"method_key":"soc-sampling-design","available_inputs":m["required_inputs"],"available_evidence":m["required_evidence"],"source_refs":["evidence:field-plan"],"methodology_refs":["methodology:internal"]}})
    obj=r["packet"]["objects"][0]
    assert obj["object_type"] == "monitoring-record"
    assert obj["status"] == "draft"
    assert obj["payload"]["domain_version"] == "0.12.0"
    assert obj["payload"]["documentation_readiness"] == "ready"
    assert obj["payload"]["guardrails"]["no_verification_determination"] is True
    assert r["packet"]["provenance"][0]["event_type"] == "created"

def test_schema_dimensions():
    s=schema()
    assert "direct-measurement" in s["method_types"]
    assert "soil-organic-carbon" in s["carbon_pools"]
    assert "CH4" in s["gases"]

def test_nonco2_wetland_profile_requires_explicit_gwp_source_when_co2e_is_generated():
    m=METHODS["wetland-multigas-monitoring"]
    assert "gwp-source-when-converting-to-co2e" in m["required_evidence"]
    assert set(["CO2","CH4","N2O"]).issubset(m["gases"])

def test_registry_profiles_are_foundation_profiles_not_external_protocols():
    for m in METHODS.values():
        assert m["status"] == "foundation-profile"
        assert "not an external protocol" in m["interpretation"]
