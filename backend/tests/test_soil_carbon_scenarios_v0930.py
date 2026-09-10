import pytest
from app.soil_carbon_scenarios_v0930 import (
    DOMAIN_VERSION, LAB_RELEASE_VERSION, SoilCarbonScenarioV01000Error,
    build_project_packet, compare_scenarios, health, policies, project_scenario,
    schema, sensitivity_sweep,
)


def base(**extra):
    p={"scenario_id":"scenario:test","baseline_stock_Mg_C_ha":78,"horizon_years":5,"model_type":"constant-annual-change","annual_change_Mg_C_ha_yr":2}
    p.update(extra); return p


def test_identity_health_and_policy():
    assert DOMAIN_VERSION == "0.10.0" and LAB_RELEASE_VERSION == "0.93.0"
    assert health()["status"] == "soc-management-scenario-studio-ready"
    assert policies()["guardrails"]["no_default_soc_change_rate"] is True
    assert schema()["model_types"] == ["constant-annual-change","compound-relative-change","annual-change-schedule"]


def test_constant_change_reference_projection():
    r=project_scenario(base())
    assert r["final_stock_Mg_C_ha"] == pytest.approx(88)
    assert r["cumulative_stock_change_Mg_C_ha"] == pytest.approx(10)
    assert r["mean_annual_stock_change_Mg_C_ha_yr"] == pytest.approx(2)
    assert len(r["trajectory"]) == 6


def test_profile_baseline_reuses_v0600_stock_engine():
    profile={"layers":[{"layer_id":"L1","top_depth":0,"bottom_depth":30,"soc_value":2,"soc_unit":"percent","bulk_density_value":1.3,"bulk_density_unit":"g/cm3"}]}
    r=project_scenario({"scenario_id":"x","baseline_profile":profile,"horizon_years":2,"model_type":"constant-annual-change","annual_change_Mg_C_ha_yr":1})
    assert r["baseline"]["stock_Mg_C_ha"] == pytest.approx(78)
    assert r["final_stock_Mg_C_ha"] == pytest.approx(80)
    assert r["baseline"]["source_basis"] == "soc-v0600-profile-calculation"


def test_compound_relative_projection():
    r=project_scenario(base(model_type="compound-relative-change",annual_relative_change_percent=10,horizon_years=2))
    assert r["final_stock_Mg_C_ha"] == pytest.approx(94.38)


def test_schedule_projection():
    r=project_scenario(base(model_type="annual-change-schedule",horizon_years=3,annual_changes_Mg_C_ha=[1,2,3]))
    assert r["final_stock_Mg_C_ha"] == pytest.approx(84)
    assert [x["annual_change_Mg_C_ha"] for x in r["trajectory"][1:]] == [1,2,3]


def test_schedule_must_match_horizon():
    with pytest.raises(SoilCarbonScenarioV01000Error,match="exactly 3"):
        project_scenario(base(model_type="annual-change-schedule",horizon_years=3,annual_changes_Mg_C_ha=[1,2]))


def test_no_default_rate():
    p=base(); del p["annual_change_Mg_C_ha_yr"]
    with pytest.raises(SoilCarbonScenarioV01000Error,match="no default SOC change rate"):
        project_scenario(p)


def test_negative_stock_projection_is_rejected():
    with pytest.raises(SoilCarbonScenarioV01000Error,match="negative SOC stock"):
        project_scenario(base(baseline_stock_Mg_C_ha=5,horizon_years=3,annual_change_Mg_C_ha_yr=-2))


def test_parcel_scale():
    r=project_scenario(base(area_ha=10,horizon_years=2))
    assert r["parcel_scale"]["baseline_stock_Mg_C"] == pytest.approx(780)
    assert r["parcel_scale"]["cumulative_stock_change_Mg_C"] == pytest.approx(40)


def test_assumption_envelope_is_not_confidence_interval():
    r=project_scenario(base(horizon_years=2,annual_change_Mg_C_ha_yr=2,annual_change_lower_Mg_C_ha_yr=1,annual_change_upper_Mg_C_ha_yr=3))
    e=r["assumption_envelope"]
    assert e["basis"] == "user-supplied-assumption-envelope-not-confidence-interval"
    assert e["final_stock_range_Mg_C_ha"] == {"lower":80.0,"upper":84.0}


def test_bad_envelope_rejected():
    with pytest.raises(SoilCarbonScenarioV01000Error,match="lower <= central <= upper"):
        project_scenario(base(annual_change_lower_Mg_C_ha_yr=3,annual_change_upper_Mg_C_ha_yr=4))


def test_measure_refs_do_not_change_calculation():
    a=project_scenario(base())
    b=project_scenario(base(measure_refs=["cover-crop-system","reduced-tillage-system"]))
    assert a["final_stock_Mg_C_ha"] == b["final_stock_Mg_C_ha"]
    assert b["guardrails"]["measure_refs_do_not_inject_rates"] is True


def test_compare_scenarios_preserves_input_order_and_does_not_rank():
    r=compare_scenarios({"baseline_stock_Mg_C_ha":78,"scenarios":[
        {"scenario_id":"slow","horizon_years":5,"model_type":"constant-annual-change","annual_change_Mg_C_ha_yr":1},
        {"scenario_id":"fast","horizon_years":5,"model_type":"constant-annual-change","annual_change_Mg_C_ha_yr":3},
    ]})
    assert [x["scenario_id"] for x in r["comparison_table"]] == ["slow","fast"]
    assert r["automatic_ranking_performed"] is False
    assert r["comparison_table"][1]["final_stock_Mg_C_ha"] == pytest.approx(93)


def test_duplicate_scenario_id_rejected():
    with pytest.raises(SoilCarbonScenarioV01000Error,match="scenario_id values must be unique"):
        compare_scenarios({"baseline_stock_Mg_C_ha":78,"scenarios":[base(scenario_id="x"),base(scenario_id="x",annual_change_Mg_C_ha_yr=3)]})


def test_sensitivity_sweep_uses_only_supplied_values():
    r=sensitivity_sweep({"baseline_stock_Mg_C_ha":78,"horizon_years":10,"model_type":"constant-annual-change","values":[0,1,2]})
    assert r["values_source"] == "user-supplied-only"
    assert [x["final_stock_Mg_C_ha"] for x in r["rows"]] == pytest.approx([78,88,98])
    assert r["automatic_optimization_performed"] is False


def test_invalid_compound_rate_rejected():
    with pytest.raises(SoilCarbonScenarioV01000Error,match="> -100"):
        project_scenario(base(model_type="compound-relative-change",annual_relative_change_percent=-100))


def test_horizon_must_be_integer():
    with pytest.raises(SoilCarbonScenarioV01000Error,match="integer"):
        project_scenario(base(horizon_years=2.5))


def test_project_packet_is_draft_model_run():
    p=build_project_packet({"project_id":"project:test","scenario":base()})
    obj=p["packet"]["objects"][0]
    assert obj["object_type"] == "model-run"
    assert obj["status"] == "draft"
    assert obj["payload"]["model_version"] == "0.10.0"
    assert obj["payload"]["guardrails"]["credit_eligibility_not_determined"] is True


def test_fingerprints_are_deterministic():
    a=project_scenario(base()); b=project_scenario(base())
    assert a["input_fingerprint"] == b["input_fingerprint"]
    assert a["result_fingerprint"] == b["result_fingerprint"]


def test_scenario_is_not_forecast_or_verified_sequestration():
    r=project_scenario(base())
    assert r["interpretation"]["scenario_projection_is_forecast"] is False
    assert r["interpretation"]["verified_sequestration_established"] is False
    assert r["guardrails"]["whole_farm_ghg_balance_not_calculated"] is True
