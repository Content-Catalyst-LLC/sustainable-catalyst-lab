import pytest

from app.soil_carbon_uncertainty_v0920 import (
    DOMAIN_VERSION, LAB_RELEASE_VERSION, SoilCarbonUncertaintyV0900Error,
    build_project_packet, change_uncertainty, health, policies,
    propagate_layer_uncertainty, stratified_estimate, summarize_replicates,
)


def obs(i, stock, lat=None, lon=None):
    row={"observation_id":f"obs-{i}","stock_Mg_C_ha":stock}
    if lat is not None: row.update(latitude=lat, longitude=lon)
    return row


def test_identity_and_health():
    assert DOMAIN_VERSION == "0.9.0"
    assert LAB_RELEASE_VERSION == "0.92.0"
    assert health()["status"] == "soc-spatial-variability-uncertainty-ready"
    assert policies()["capabilities"]["paired_change_uncertainty"] is True
    assert health()["geostatistical_interpolation"] is False


def test_replicate_summary_reference_fixture():
    r=summarize_replicates({"observations":[obs(1,76),obs(2,78),obs(3,80),obs(4,82)]})
    assert r["statistics"]["mean_Mg_C_ha"] == pytest.approx(79.0)
    assert r["statistics"]["sample_sd_Mg_C_ha"] == pytest.approx(2.581988897)
    assert r["statistics"]["standard_error_Mg_C_ha"] == pytest.approx(1.290994449)
    assert r["statistics"]["confidence_interval_Mg_C_ha"]["lower"] < 79 < r["statistics"]["confidence_interval_Mg_C_ha"]["upper"]


def test_replicate_profile_calculation_reuses_v0600():
    profile={"layers":[{"layer_id":"L1","top_depth":0,"bottom_depth":30,"soc_value":2,"soc_unit":"percent","bulk_density_value":1.3,"bulk_density_unit":"g/cm3"}]}
    r=summarize_replicates({"observations":[{"observation_id":"a","profile":profile},{"observation_id":"b","profile":profile}]})
    assert r["statistics"]["mean_Mg_C_ha"] == pytest.approx(78.0)
    assert r["observations"][0]["source_basis"] == "soc-v0600-profile-calculation"


def test_duplicate_observation_rejected():
    with pytest.raises(SoilCarbonUncertaintyV0900Error,match="unique"):
        summarize_replicates({"observations":[{"observation_id":"x","stock_Mg_C_ha":1},{"observation_id":"x","stock_Mg_C_ha":2}]})


def test_coordinate_diagnostics_do_not_claim_representativeness():
    r=summarize_replicates({"observations":[obs(1,78,38.6,-90.5),obs(2,80,38.61,-90.49),obs(3,79,38.62,-90.51)]})
    s=r["spatial_coverage"]
    assert s["available"] is True and s["coordinate_count"] == 3
    assert s["nearest_neighbor_km"]["median"] > 0
    assert s["representativeness_determined"] is False


def test_partial_coordinates_rejected():
    with pytest.raises(SoilCarbonUncertaintyV0900Error,match="both latitude and longitude"):
        summarize_replicates({"observations":[obs(1,78),{"observation_id":"b","stock_Mg_C_ha":79,"latitude":38.6}]})


def test_stratified_area_weighted_mean():
    r=stratified_estimate({"strata":[
      {"stratum_id":"upland","area_ha":75,"observations":[obs(1,80),obs(2,84)]},
      {"stratum_id":"lowland","area_ha":25,"observations":[obs(3,60),obs(4,64)]},
    ]})
    assert r["weighted_mean_stock_Mg_C_ha"] == pytest.approx(77.0)
    assert r["total_stock_Mg_C"] == pytest.approx(7700.0)
    assert r["standard_error_Mg_C_ha"] > 0


def test_duplicate_stratum_rejected():
    with pytest.raises(SoilCarbonUncertaintyV0900Error,match="stratum_id values must be unique"):
        stratified_estimate({"strata":[{"stratum_id":"x","area_ha":1,"observations":[obs(1,1),obs(2,2)]},{"stratum_id":"x","area_ha":2,"observations":[obs(3,3),obs(4,4)]}]})


def test_paired_change_uncertainty_reference():
    pairs=[]
    for i,(b,f) in enumerate([(78,86),(77,84),(80,89),(79,87)],1):
        pairs.append({"pair_id":f"p{i}","baseline":obs(i,b),"followup":obs(i+10,f)})
    r=change_uncertainty({"mode":"paired","pairs":pairs,"elapsed_years":2})
    assert r["mean_stock_change_Mg_C_ha"] == pytest.approx(8.0)
    assert r["annualized_mean_stock_change_Mg_C_ha_yr"] == pytest.approx(4.0)
    assert r["interpretation"]["causal_attribution_established"] is False


def test_independent_change_uncertainty():
    r=change_uncertainty({"mode":"independent","baseline_observations":[obs(1,76),obs(2,78),obs(3,80)],"followup_observations":[obs(4,84),obs(5,86),obs(6,88)]})
    assert r["mean_stock_change_Mg_C_ha"] == pytest.approx(8.0)
    assert r["degrees_of_freedom"] == pytest.approx(4.0)
    assert r["standard_error_Mg_C_ha"] > 0


def test_unsupported_confidence_rejected():
    with pytest.raises(SoilCarbonUncertaintyV0900Error,match="0.90, 0.95, or 0.99"):
        summarize_replicates({"confidence_level":0.8,"observations":[obs(1,1),obs(2,2)]})


def test_paired_mode_requires_two_pairs():
    with pytest.raises(SoilCarbonUncertaintyV0900Error,match="pairs must contain"):
        change_uncertainty({"mode":"paired","pairs":[{"baseline":obs(1,1),"followup":obs(2,2)}]})


def test_interval_excluding_zero_is_not_causal_claim():
    pairs=[{"pair_id":f"p{i}","baseline":obs(i,70),"followup":obs(i+10,90+i/10)} for i in range(1,7)]
    r=change_uncertainty({"mode":"paired","pairs":pairs})
    assert r["confidence_interval_excludes_zero"] is True
    assert r["interpretation"]["directional_separation_at_stated_confidence"] is True
    assert r["interpretation"]["verified_sequestration_established"] is False


def test_layer_first_order_uncertainty_zero_inputs():
    layer={"layer_id":"L1","top_depth":0,"bottom_depth":30,"soc_value":2,"soc_unit":"percent","bulk_density_value":1.3,"bulk_density_unit":"g/cm3","coarse_fragments_percent":0}
    r=propagate_layer_uncertainty({"layer":layer})
    assert r["stock_Mg_C_ha"] == pytest.approx(78.0)
    assert r["combined_standard_uncertainty_Mg_C_ha"] == 0


def test_layer_first_order_uncertainty_nonzero():
    layer={"layer_id":"L1","top_depth":0,"bottom_depth":30,"soc_value":2,"soc_unit":"percent","bulk_density_value":1.3,"bulk_density_unit":"g/cm3","coarse_fragments_percent":5}
    r=propagate_layer_uncertainty({"layer":layer,"soc_standard_uncertainty":0.1,"bulk_density_standard_uncertainty":0.05,"thickness_standard_uncertainty":0.2,"coarse_fragments_standard_uncertainty_percent":1})
    assert r["combined_standard_uncertainty_Mg_C_ha"] > 0
    assert r["guardrails"]["correlations_not_inferred"] is True


def test_negative_uncertainty_rejected():
    layer={"top_depth":0,"bottom_depth":30,"soc_value":2,"soc_unit":"percent","bulk_density_value":1.3,"bulk_density_unit":"g/cm3"}
    with pytest.raises(SoilCarbonUncertaintyV0900Error,match=">=0"):
        propagate_layer_uncertainty({"layer":layer,"soc_standard_uncertainty":-1})


def test_project_packet_is_model_run_and_not_verification():
    pairs=[{"pair_id":"p1","baseline":obs(1,78),"followup":obs(2,86)},{"pair_id":"p2","baseline":obs(3,77),"followup":obs(4,84)}]
    p=build_project_packet({"project_id":"project:test","analysis":{"mode":"paired","pairs":pairs}})
    obj=p["packet"]["objects"][0]
    assert obj["object_type"] == "model-run"
    assert obj["payload"]["model_version"] == "0.9.0"
    assert obj["payload"]["guardrails"]["verification_not_performed"] is True


def test_fingerprints_deterministic():
    payload={"observations":[obs(1,78),obs(2,80),obs(3,82)]}
    a=summarize_replicates(payload); b=summarize_replicates(payload)
    assert a["input_fingerprint"] == b["input_fingerprint"]
    assert a["result_fingerprint"] == b["result_fingerprint"]
