import pytest

from app.carbon_mrv_monitoring_v0970 import (
    LAB_RELEASE_VERSION, DOMAIN_VERSION, PLAN_SCHEMA, STRATEGIES,
    CarbonMRVMonitoringV01400Error, health, schema, policies, plan_template,
    sample_size_plan, allocate_strata, build_plan, validate_plan, build_project_packet,
)
from app.carbon_mrv_registry_v0950 import METHODS


def complete_payload():
    m = METHODS["soc-direct-measurement"]
    return {
        "monitoring_plan_id": "monitoring-plan:test",
        "project_id": "project:test",
        "protocol_id": "mrv-protocol:test",
        "title": "SOC monitoring and sampling plan",
        "objective": "Design repeated fixed-depth SOC sampling for the named parcel.",
        "method_key": "soc-direct-measurement",
        "spatial_boundary_ref": "parcel:test",
        "campaigns": [
            {"campaign_id": "campaign:baseline", "purpose": "baseline", "planned_start_date": "2026-04-01", "planned_end_date": "2026-04-15"},
            {"campaign_id": "campaign:repeat", "purpose": "follow-up", "planned_start_date": "2030-04-01", "planned_end_date": "2030-04-15", "repeat_of": "campaign:baseline"},
        ],
        "sampling_frame_ref": "sampling-frame:parcel-test",
        "sample_unit": "field core / composite sampling location",
        "sampling_design": {
            "strategy": "stratified-random",
            "target_population": "Mineral soil within the named parcel and explicit management strata.",
            "depth_intervals_cm": [{"top_cm": 0, "bottom_cm": 15}, {"top_cm": 15, "bottom_cm": 30}],
            "field_qc_steps": ["stable sample IDs", "depth verification", "chain-of-custody"],
            "laboratory_qc_steps": ["method record", "duplicate review"],
            "strata": [{"stratum_key": "A", "size": 60, "expected_sd": 10}, {"stratum_key": "B", "size": 40, "expected_sd": 20}],
            "sample_size_assumptions": {"expected_sd": 12, "z_value": 1.96, "target_half_width": 4},
            "stratified_allocation": {"allocation_method": "proportional", "total_sample_size": 36, "strata": [{"stratum_key": "A", "size": 60}, {"stratum_key": "B", "size": 40}]},
        },
        "available_inputs": m["required_inputs"], "available_evidence": m["required_evidence"],
        "methodology_refs": ["library-methodology:soc-direct-measurement"], "source_refs": ["evidence:sampling-frame", "evidence:field-sop"],
    }


def test_identity_health_schema_and_policy():
    assert LAB_RELEASE_VERSION == "0.97.0"
    assert DOMAIN_VERSION == "0.14.0"
    assert health()["status"] == "monitoring-plan-sampling-designer-ready"
    assert health()["strategy_count"] == len(STRATEGIES) == 5
    assert schema()["plan_schema"] == PLAN_SCHEMA
    assert policies()["guardrails"]["no_hidden_precision_or_variability_defaults"] is True


def test_template_surfaces_strategy_and_method_requirements_without_selection():
    t = plan_template("soc-direct-measurement")
    assert t["method_title"] == "SOC Direct Measurement"
    assert len(t["strategy_options"]) == 5
    assert t["guardrails"]["sampling_plan_is_not_proof_of_representativeness"] is True


def test_sample_size_fixture_absolute_precision():
    r = sample_size_plan({"expected_sd": 12, "z_value": 1.96, "target_half_width": 4})
    assert r["unadjusted_sample_size"] == 35
    assert r["recommended_planning_sample_size"] == 35
    assert r["finite_population_correction_applied"] is False


def test_sample_size_relative_precision_and_fpc():
    r = sample_size_plan({"expected_sd": 10, "z_value": 1.96, "relative_precision_percent": 5, "expected_mean": 100, "population_size": 100})
    assert r["target_half_width"] == 5
    assert r["unadjusted_sample_size"] == 16
    assert r["recommended_planning_sample_size"] == 14


def test_sample_size_rejects_hidden_precision():
    with pytest.raises(CarbonMRVMonitoringV01400Error):
        sample_size_plan({"expected_sd": 10, "z_value": 1.96})


def test_proportional_allocation_is_integer_and_exact():
    r = allocate_strata({"allocation_method": "proportional", "total_sample_size": 36, "strata": [{"stratum_key": "A", "size": 60}, {"stratum_key": "B", "size": 40}]})
    assert [x["allocated_sample_size"] for x in r["strata"]] == [22, 14]
    assert sum(x["allocated_sample_size"] for x in r["strata"]) == 36


def test_neyman_allocation_requires_sd_and_uses_supplied_sd():
    with pytest.raises(CarbonMRVMonitoringV01400Error):
        allocate_strata({"allocation_method": "neyman", "total_sample_size": 20, "strata": [{"stratum_key": "A", "size": 50}, {"stratum_key": "B", "size": 50}]})
    r = allocate_strata({"allocation_method": "neyman", "total_sample_size": 20, "strata": [{"stratum_key": "A", "size": 50, "expected_sd": 1}, {"stratum_key": "B", "size": 50, "expected_sd": 3}]})
    assert [x["allocated_sample_size"] for x in r["strata"]] == [5, 15]


def test_complete_soc_plan_ready_for_internal_review_only():
    r = build_plan(complete_payload())
    p, v = r["plan"], r["validation"]
    assert p["status"] == "ready-for-internal-review"
    assert v["ready_for_internal_review"] is True
    assert p["sampling_design"]["sample_size_plan"]["recommended_planning_sample_size"] == 35
    assert v["sampling_representativeness"] is None
    assert v["external_methodology_compliance"] is None
    assert v["verification_status"] is None
    assert v["credit_eligibility"] is None


def test_soc_plan_requires_depths_for_internal_review():
    p = complete_payload(); p["sampling_design"]["depth_intervals_cm"] = []
    v = build_plan(p)["validation"]
    assert "sampling_design.depth_intervals_cm" in v["missing_core_fields"]
    assert v["ready_for_internal_review"] is False


def test_stratified_strategy_requires_strata():
    p = complete_payload(); p["sampling_design"]["strata"] = []
    v = build_plan(p)["validation"]
    assert "sampling_design.strata" in v["missing_core_fields"]


def test_overlapping_depths_rejected():
    p = complete_payload(); p["sampling_design"]["depth_intervals_cm"] = [{"top_cm": 0, "bottom_cm": 20}, {"top_cm": 15, "bottom_cm": 30}]
    with pytest.raises(CarbonMRVMonitoringV01400Error):
        build_plan(p)


def test_duplicate_campaign_ids_rejected():
    p = complete_payload(); p["campaigns"].append(dict(p["campaigns"][0]))
    with pytest.raises(CarbonMRVMonitoringV01400Error):
        build_plan(p)


def test_plan_is_deterministic():
    a = build_plan(complete_payload()); b = build_plan(complete_payload())
    assert a["plan"]["plan_fingerprint"] == b["plan"]["plan_fingerprint"]
    assert a["validation"]["result_fingerprint"] == b["validation"]["result_fingerprint"]


def test_validation_recomputes_from_source_fields():
    r = build_plan(complete_payload()); p = r["plan"]
    p["method_documentation_readiness"]["documentation_ready"] = False
    v = validate_plan({"plan": p})
    assert v["ready_for_internal_review"] is True


def test_project_packet_is_monitoring_record_and_links_to_protocol():
    r = build_project_packet({"plan": build_plan(complete_payload())["plan"], "actor_ref": "actor:reviewer"})
    obj = r["packet"]["objects"][0]
    assert obj["object_type"] == "monitoring-record"
    assert obj["payload"]["record_type"] == "monitoring-plan"
    assert obj["payload"]["ready_for_internal_review"] is True
    assert r["packet"]["links"][0]["relationship"] == "monitoring-for"


def test_no_coordinate_generation_or_representativeness_claim():
    g = policies()["guardrails"]
    assert g["no_automatic_coordinate_generation"] is True
    assert g["sampling_plan_is_not_proof_of_representativeness"] is True
