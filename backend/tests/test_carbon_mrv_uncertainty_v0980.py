import math
import pytest

from app.carbon_mrv_uncertainty_v0980 import (
    LAB_RELEASE_VERSION, DOMAIN_VERSION, ASSESSMENT_SCHEMA,
    CarbonMRVUncertaintyV01500Error,
    health, schema, policies, uncertainty_budget, change_detection,
    required_sample_size, build_assessment, validate_assessment, build_project_packet,
)


def complete_payload():
    return {
        "project_id": "project:fixture",
        "title": "SOC MRV uncertainty and detection assessment",
        "metric": "SOC stock change",
        "unit": "Mg C/ha",
        "monitoring_plan_ref": "monitoring-plan:fixture",
        "protocol_ref": "mrv-protocol:fixture",
        "uncertainty_budget": {
            "estimate": 100,
            "unit": "Mg C/ha",
            "coverage_factor": 2,
            "components": [
                {"component_key": "sampling", "standard_uncertainty": 3, "source_ref": "evidence:sampling"},
                {"component_key": "laboratory", "standard_uncertainty": 4, "source_ref": "evidence:lab"},
            ],
        },
        "change_detection": {
            "design": "paired", "observed_change": 4, "critical_value": 1.96,
            "sd_change": 8, "n_pairs": 16,
        },
        "detection_sample_size": {
            "design": "paired", "minimum_detectable_change": 4,
            "z_alpha": 1.96, "z_power": 0.84, "expected_sd_change": 8,
        },
        "methodology_refs": ["library-methodology:soc-direct-measurement"],
        "source_refs": ["evidence:sampling", "evidence:lab"],
    }


def test_identity_health_schema_policy():
    assert LAB_RELEASE_VERSION == "0.98.0"
    assert DOMAIN_VERSION == "0.15.0"
    assert health()["status"] == "mrv-uncertainty-detection-engine-ready"
    assert schema()["assessment_schema"] == ASSESSMENT_SCHEMA
    assert policies()["guardrails"]["no_hidden_confidence_or_coverage_defaults"] is True


def test_uncertainty_budget_reference_fixture():
    r = uncertainty_budget({
        "estimate": 100, "unit": "Mg C/ha", "coverage_factor": 2,
        "components": [
            {"component_key": "a", "standard_uncertainty": 3},
            {"component_key": "b", "standard_uncertainty": 4},
        ],
    })
    assert r["combined_standard_uncertainty"] == 5
    assert r["combined_relative_percent"] == 5
    assert r["expanded_uncertainty"] == 10
    assert r["expanded_interval"] == [90, 110]


def test_relative_uncertainty_component_is_explicitly_converted():
    r = uncertainty_budget({"estimate": 200, "unit": "kg", "components": [{"component_key": "scale", "relative_percent": 2.5}]})
    assert r["components"][0]["standard_uncertainty"] == 5
    assert r["expanded_uncertainty"] is None


def test_uncertainty_component_requires_exactly_one_input_form():
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        uncertainty_budget({"estimate": 100, "unit": "kg", "components": [{"component_key": "x", "standard_uncertainty": 2, "relative_percent": 2}]})
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        uncertainty_budget({"estimate": 100, "unit": "kg", "components": [{"component_key": "x"}]})


def test_covariance_is_only_used_when_explicit():
    r = uncertainty_budget({
        "estimate": 100, "unit": "kg",
        "components": [{"component_key": "a", "standard_uncertainty": 3}, {"component_key": "b", "standard_uncertainty": 4}],
        "covariance_terms": [{"component_a": "a", "component_b": "b", "covariance": 6}],
    })
    assert math.isclose(r["combined_standard_uncertainty"], math.sqrt(37))


def test_invalid_covariance_reference_and_negative_variance_rejected():
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        uncertainty_budget({"estimate": 1, "unit": "x", "components": [{"component_key": "a", "standard_uncertainty": 1}], "covariance_terms": [{"component_a": "a", "component_b": "b", "covariance": 1}]})
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        uncertainty_budget({"estimate": 1, "unit": "x", "components": [{"component_key": "a", "standard_uncertainty": 1}, {"component_key": "b", "standard_uncertainty": 1}], "covariance_terms": [{"component_a": "a", "component_b": "b", "covariance": -2}]})


def test_paired_change_detection_fixture():
    r = change_detection({"design": "paired", "observed_change": 4, "critical_value": 1.96, "sd_change": 8, "n_pairs": 16})
    assert r["standard_error_change"] == 2
    assert math.isclose(r["detection_threshold"], 3.92)
    assert r["change_detected_at_supplied_threshold"] is True


def test_independent_change_detection_fixture_not_detected():
    r = change_detection({"design": "independent", "observed_change": 4, "critical_value": 1.96, "baseline_sd": 10, "followup_sd": 10, "n_baseline": 25, "n_followup": 25})
    assert math.isclose(r["standard_error_change"], math.sqrt(8))
    assert r["change_detected_at_supplied_threshold"] is False


def test_detection_requires_explicit_critical_value_and_variability():
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        change_detection({"design": "paired", "observed_change": 4, "sd_change": 8, "n_pairs": 16})
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        change_detection({"design": "paired", "observed_change": 4, "critical_value": 1.96, "n_pairs": 16})


def test_paired_detection_sample_size_fixture():
    r = required_sample_size({"design": "paired", "minimum_detectable_change": 4, "z_alpha": 1.96, "z_power": 0.84, "expected_sd_change": 8})
    assert r["recommended_pairs"] == 32


def test_independent_equal_detection_sample_size_fixture():
    r = required_sample_size({"design": "independent-equal", "minimum_detectable_change": 5, "z_alpha": 1.96, "z_power": 0.84, "baseline_sd": 10, "followup_sd": 10})
    assert r["recommended_per_period"] == 63


def test_sample_size_requires_user_power_side_value_even_if_zero():
    with pytest.raises(CarbonMRVUncertaintyV01500Error):
        required_sample_size({"design": "paired", "minimum_detectable_change": 4, "z_alpha": 1.96, "expected_sd_change": 8})


def test_complete_assessment_is_internal_review_ready_only():
    r = build_assessment(complete_payload())
    a, v = r["assessment"], r["validation"]
    assert a["status"] == "ready-for-internal-review"
    assert v["ready_for_internal_review"] is True
    assert v["external_methodology_compliance"] is None
    assert v["verification_status"] is None
    assert v["credit_eligibility"] is None
    assert v["deduction_factor"] is None


def test_incomplete_assessment_reports_missing_core_fields():
    p = complete_payload(); p["monitoring_plan_ref"] = None
    v = build_assessment(p)["validation"]
    assert "monitoring_plan_ref" in v["missing_core_fields"]
    assert v["ready_for_internal_review"] is False


def test_assessment_is_deterministic():
    a = build_assessment(complete_payload())
    b = build_assessment(complete_payload())
    assert a["assessment"]["assessment_fingerprint"] == b["assessment"]["assessment_fingerprint"]
    assert a["validation"]["result_fingerprint"] == b["validation"]["result_fingerprint"]


def test_validation_recomputes_from_source_fields():
    built = build_assessment(complete_payload())
    a = built["assessment"]
    a["status"] = "draft"
    v = validate_assessment({"assessment": a})
    assert v["ready_for_internal_review"] is True


def test_project_packet_is_model_run_and_links_to_monitoring_plan():
    built = build_assessment(complete_payload())
    r = build_project_packet({"assessment": built["assessment"], "actor_ref": "actor:reviewer"})
    obj = r["packet"]["objects"][0]
    assert obj["object_type"] == "model-run"
    assert obj["payload"]["record_type"] == "mrv-uncertainty-detection-assessment"
    assert any(x["to"] == "monitoring-plan:fixture" for x in r["packet"]["links"])
    assert r["packet"]["provenance"][0]["event_type"] == "modeled"


def test_guardrails_do_not_turn_detection_into_verification():
    g = policies()["guardrails"]
    assert g["detection_threshold_is_not_verification"] is True
    assert g["no_verification_determination"] is True
    assert g["uncertainty_is_not_automatically_a_deduction_factor"] is True
