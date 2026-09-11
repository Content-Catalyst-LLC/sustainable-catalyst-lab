import pytest

from app.carbon_mrv_protocol_v0960 import (
    LAB_RELEASE_VERSION,
    DOMAIN_VERSION,
    PROTOCOL_SCHEMA,
    SECTION_DEFINITIONS,
    CarbonMRVProtocolV01300Error,
    health,
    schema,
    policies,
    protocol_template,
    build_protocol,
    validate_protocol,
    build_project_packet,
)
from app.carbon_mrv_registry_v0950 import METHODS


def complete_payload():
    method = METHODS["soc-direct-measurement"]
    return {
        "protocol_id": "mrv-protocol:test",
        "project_id": "project:test",
        "title": "SOC monitoring protocol",
        "objective": "Measure repeated fixed-depth SOC stocks for the named parcel using an explicit field and laboratory workflow.",
        "method_key": "soc-direct-measurement",
        "spatial_boundary_ref": "parcel:test",
        "monitoring_period": {"start_date": "2026-01-01", "end_date": "2030-12-31"},
        "monitoring_frequency": "Baseline in 2026 and repeat campaign in 2030; deviations recorded explicitly.",
        "responsible_roles": [
            {"role": "field lead", "actor_ref": "actor:field-team", "responsibility": "Field sampling and custody"},
            {"role": "laboratory reviewer", "actor_ref": "actor:lab-review", "responsibility": "Analytical review"},
        ],
        "available_inputs": method["required_inputs"],
        "available_evidence": method["required_evidence"],
        "methodology_refs": ["library-methodology:soc-direct-measurement"],
        "source_refs": ["evidence:field-plan", "evidence:lab-sop"],
        "sections": {
            "objective_and_scope": "Parcel boundary, 0-30 cm mineral soil, SOC pool; non-SOC pools excluded from this protocol.",
            "measurement_and_sampling_plan": "Use the project sampling design, explicit sample IDs, fixed depth, bulk density, SOC concentration, and coarse-fragment observations.",
            "calculation_plan": "Use the governed fixed-depth fine-earth-corrected SOC stock model with explicit units and versioned inputs.",
            "uncertainty_plan": "Quantify replicate sampling variability and record analytical and bulk-density uncertainty; unresolved components remain explicit.",
            "quality_control_plan": "Check sample identity, depth consistency, custody, replicate completeness, laboratory method record, and data-quality review.",
            "data_management_plan": "Use stable sample IDs, source refs, versioned records, and provenance links from field observations to model runs.",
            "monitoring_schedule": "Baseline campaign in 2026 and repeat campaign in 2030; record actual collection dates for every sample.",
            "reporting_plan": "Produce a monitoring record with stock estimates, uncertainty, evidence links, and limitations for internal review.",
            "change_control_plan": "Version protocol changes, preserve superseded versions, record reasons, and require reviewer signoff for material revisions.",
        },
    }


def test_identity_health_and_schema():
    assert LAB_RELEASE_VERSION == "0.96.0"
    assert DOMAIN_VERSION == "0.13.0"
    assert health()["status"] == "mrv-protocol-builder-ready"
    assert health()["method_registry_count"] == 7
    assert health()["section_count"] == len(SECTION_DEFINITIONS) == 9
    assert schema()["protocol_schema"] == PROTOCOL_SCHEMA
    assert policies()["guardrails"]["no_methodology_eligibility_determination"] is True


def test_template_is_method_derived_without_claiming_external_compliance():
    t = protocol_template("soc-direct-measurement")
    assert t["method_key"] == "soc-direct-measurement"
    assert "sampling-design" in t["required_inputs"]
    assert len(t["sections"]) == 9
    assert t["guardrails"]["protocol_is_not_external_methodology"] is True
    assert len(t["template_fingerprint"]) == 64


def test_template_unknown_method():
    with pytest.raises(CarbonMRVProtocolV01300Error) as exc:
        protocol_template("bad")
    assert exc.value.status_code == 404


def test_draft_protocol_surfaces_gaps_instead_of_filling_them():
    r = build_protocol({"method_key": "soc-direct-measurement"})
    p, v = r["protocol"], r["validation"]
    assert p["status"] == "draft"
    assert v["ready_for_internal_review"] is False
    assert "project_id" in v["missing_core_fields"]
    assert "objective_and_scope" in v["missing_sections"]
    assert "sampling-design" in v["missing_method_inputs"]
    assert v["external_methodology_compliance"] is None


def test_complete_protocol_is_ready_for_internal_review_only():
    r = build_protocol(complete_payload())
    p, v = r["protocol"], r["validation"]
    assert p["status"] == "ready-for-internal-review"
    assert v["ready_for_internal_review"] is True
    assert not v["missing_core_fields"]
    assert not v["missing_sections"]
    assert not v["missing_method_inputs"]
    assert not v["missing_method_evidence"]
    assert v["verification_status"] is None
    assert v["credit_eligibility"] is None


def test_protocol_is_deterministic():
    p = complete_payload()
    a = build_protocol(p)
    b = build_protocol(p)
    assert a["protocol"]["protocol_fingerprint"] == b["protocol"]["protocol_fingerprint"]
    assert a["validation"]["result_fingerprint"] == b["validation"]["result_fingerprint"]


def test_invalid_monitoring_period_is_rejected():
    p = complete_payload()
    p["monitoring_period"] = {"start_date": "2030-01-01", "end_date": "2026-01-01"}
    with pytest.raises(CarbonMRVProtocolV01300Error):
        build_protocol(p)


def test_unknown_section_is_rejected():
    p = complete_payload()
    p["sections"]["invented"] = "x"
    with pytest.raises(CarbonMRVProtocolV01300Error):
        build_protocol(p)


def test_validate_protocol_recomputes_readiness_from_source_fields():
    r = build_protocol(complete_payload())
    p = r["protocol"]
    p["method_documentation_readiness"]["documentation_ready"] = False
    v = validate_protocol({"protocol": p})
    assert v["ready_for_internal_review"] is True


def test_missing_source_and_methodology_refs_block_internal_review():
    p = complete_payload()
    p["source_refs"] = []
    p["methodology_refs"] = []
    v = build_protocol(p)["validation"]
    assert set(v["missing_references"]) == {"source_refs", "methodology_refs"}
    assert v["ready_for_internal_review"] is False


def test_project_packet_uses_monitoring_record_and_preserves_guardrails():
    r = build_project_packet({"protocol": build_protocol(complete_payload())["protocol"], "actor_ref": "actor:reviewer"})
    obj = r["packet"]["objects"][0]
    assert obj["object_type"] == "monitoring-record"
    assert obj["payload"]["record_type"] == "mrv-protocol"
    assert obj["payload"]["ready_for_internal_review"] is True
    assert obj["payload"]["guardrails"]["no_verification_determination"] is True
    assert r["packet"]["provenance"][0]["event_type"] == "created"


def test_project_packet_requires_project_id():
    p = complete_payload()
    p["project_id"] = None
    with pytest.raises(CarbonMRVProtocolV01300Error):
        build_project_packet(p)


def test_no_hidden_method_defaults_or_selection():
    assert policies()["guardrails"]["no_automatic_method_selection"] is True
    assert policies()["guardrails"]["no_hidden_measurement_or_sampling_defaults"] is True
    with pytest.raises(CarbonMRVProtocolV01300Error):
        build_protocol({})
