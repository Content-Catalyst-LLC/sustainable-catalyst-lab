import pytest

from app.soil_carbon_change_v0910 import (
    DOMAIN_VERSION,
    LAB_RELEASE_VERSION,
    SoilCarbonChangeV0800Error,
    build_change_series,
    build_project_packet,
    compare_profiles,
    health,
    policies,
    schema,
)


def layer(soc_percent=2.0, bd=1.3, top=0, bottom=30, layer_id="L1", coarse=0):
    return {
        "layer_id": layer_id,
        "top_depth": top,
        "bottom_depth": bottom,
        "depth_unit": "cm",
        "soc_value": soc_percent,
        "soc_unit": "percent",
        "bulk_density_value": bd,
        "bulk_density_unit": "g/cm3",
        "coarse_fragments_percent": coarse,
    }


def comparison(**patch):
    payload = {
        "comparison_id": "comparison:test",
        "spatial_unit_id": "parcel:test",
        "baseline_at": "2025-01-01",
        "followup_at": "2026-01-01",
        "baseline_profile": {"profile_id": "profile:baseline", "layers": [layer(2.0)]},
        "followup_profile": {"profile_id": "profile:followup", "layers": [layer(2.2)]},
    }
    payload.update(patch)
    return payload


def test_identity_health_and_boundaries():
    assert DOMAIN_VERSION == "0.8.0"
    assert LAB_RELEASE_VERSION == "0.91.0"
    assert health()["status"] == "soc-stock-change-model-ready"
    assert policies()["capabilities"]["matched_profile_stock_change"] is True
    assert policies()["capabilities"]["attributed_sequestration_claim"] is False
    assert schema()["matching_policy"]["interval_policy"] == "exact-normalized-intervals"


def test_reference_change_fixture():
    result = compare_profiles(comparison())
    assert result["baseline"]["soc_stock_Mg_C_ha"] == pytest.approx(78.0)
    assert result["followup"]["soc_stock_Mg_C_ha"] == pytest.approx(85.8)
    assert result["stock_change_Mg_C_ha"] == pytest.approx(7.8)
    assert result["direction"] == "increase"
    assert result["elapsed_days"] == pytest.approx(365.0)
    assert result["annualized_stock_change_Mg_C_ha_yr"] == pytest.approx(7.805181, rel=1e-6)


def test_area_scaling():
    result = compare_profiles(comparison(area_ha=10))
    assert result["stock_change_Mg_C_total"] == pytest.approx(78.0)
    assert result["annualized_stock_change_Mg_C_total_yr"] == pytest.approx(
        result["annualized_stock_change_Mg_C_ha_yr"] * 10
    )


def test_decrease_is_reported_without_negative_sequestration_claim():
    result = compare_profiles(comparison(
        baseline_profile={"layers": [layer(2.2)]},
        followup_profile={"layers": [layer(2.0)]},
    ))
    assert result["stock_change_Mg_C_ha"] == pytest.approx(-7.8)
    assert result["direction"] == "decrease"
    assert result["gross_stock_increase_Mg_C_ha"] == 0
    assert result["gross_stock_loss_Mg_C_ha"] == pytest.approx(7.8)


def test_positive_change_is_not_attributed_sequestration():
    result = compare_profiles(comparison(intervention_ref="intervention:cover-crop"))
    i = result["interpretation"]
    assert i["positive_change_is_candidate_gross_soc_accumulation"] is True
    assert i["intervention_attribution_established"] is False
    assert i["verified_sequestration_established"] is False
    assert result["guardrails"]["credit_eligibility_not_determined"] is True


def test_depth_interval_mismatch_rejected():
    with pytest.raises(SoilCarbonChangeV0800Error, match="identical normalized fixed-depth intervals"):
        compare_profiles(comparison(followup_profile={"layers": [layer(2.2, top=0, bottom=25)]}))


def test_layer_count_mismatch_rejected():
    with pytest.raises(SoilCarbonChangeV0800Error, match="layer-count-mismatch"):
        compare_profiles(comparison(followup_profile={"layers": [layer(2.2, top=0, bottom=15, layer_id="a"), layer(1.8, top=15, bottom=30, layer_id="b")]}))


def test_time_direction_required():
    with pytest.raises(SoilCarbonChangeV0800Error, match="later than"):
        compare_profiles(comparison(followup_at="2024-01-01"))


def test_spatial_unit_required():
    with pytest.raises(SoilCarbonChangeV0800Error, match="spatial_unit_id is required"):
        compare_profiles(comparison(spatial_unit_id=None))


def test_area_conflict_rejected():
    with pytest.raises(SoilCarbonChangeV0800Error, match="area_ha values must agree"):
        compare_profiles(comparison(
            baseline_profile={"area_ha": 5, "layers": [layer(2.0)]},
            followup_profile={"area_ha": 6, "layers": [layer(2.2)]},
        ))


def test_relative_change_baseline_zero_is_none():
    result = compare_profiles(comparison(
        baseline_profile={"layers": [layer(0.0)]},
        followup_profile={"layers": [layer(0.2)]},
    ))
    assert result["relative_stock_change_percent"] is None


def test_deterministic_fingerprints():
    a = compare_profiles(comparison())
    b = compare_profiles(comparison())
    assert a["input_fingerprint"] == b["input_fingerprint"]
    assert a["result_fingerprint"] == b["result_fingerprint"]


def test_multi_layer_matched_change():
    base = {"layers": [layer(2.0, top=0, bottom=15, layer_id="a"), layer(1.0, bd=1.4, top=15, bottom=30, layer_id="b")]}
    follow = {"layers": [layer(2.1, top=0, bottom=15, layer_id="a2"), layer(1.1, bd=1.4, top=15, bottom=30, layer_id="b2")]}
    r = compare_profiles(comparison(baseline_profile=base, followup_profile=follow))
    assert len(r["depth_match"]["intervals"]) == 2
    assert r["stock_change_Mg_C_ha"] > 0


def test_change_series_orders_points_and_calculates_pairwise():
    payload = {
        "series_id": "series:test",
        "spatial_unit_id": "parcel:test",
        "observations": [
            {"observed_at": "2027-01-01", "profile": {"layers": [layer(2.4)]}},
            {"observed_at": "2025-01-01", "profile": {"layers": [layer(2.0)]}},
            {"observed_at": "2026-01-01", "profile": {"layers": [layer(2.2)]}},
        ],
    }
    r = build_change_series(payload)
    assert r["point_count"] == 3
    assert [p["observed_at"] for p in r["points"]] == ["2025-01-01", "2026-01-01", "2027-01-01"]
    assert len(r["pairwise_changes"]) == 2
    assert r["overall"]["stock_change_Mg_C_ha"] == pytest.approx(15.6)


def test_series_duplicate_timestamp_rejected():
    with pytest.raises(SoilCarbonChangeV0800Error, match="timestamps must be unique"):
        build_change_series({
            "spatial_unit_id": "parcel:test",
            "observations": [
                {"observed_at": "2025-01-01", "profile": {"layers": [layer(2.0)]}},
                {"observed_at": "2025-01-01", "profile": {"layers": [layer(2.1)]}},
            ],
        })


def test_series_depth_mismatch_rejected():
    with pytest.raises(SoilCarbonChangeV0800Error, match="identical normalized fixed-depth intervals"):
        build_change_series({
            "spatial_unit_id": "parcel:test",
            "observations": [
                {"observed_at": "2025-01-01", "profile": {"layers": [layer(2.0)]}},
                {"observed_at": "2026-01-01", "profile": {"layers": [layer(2.1, bottom=20)]}},
            ],
        })


def test_project_packet_aligns_with_carbon_project_contract():
    p = build_project_packet({
        "project_id": "project:test",
        "actor_ref": "system:lab",
        "run_at": "2026-09-10T12:00:00+00:00",
        "input_object_ids": ["model-run:baseline", "model-run:followup"],
        "comparison": comparison(),
    })
    packet = p["packet"]
    assert packet["schema"] == "sc-carbon-project-packet/1.0"
    obj = packet["objects"][0]
    assert obj["object_type"] == "model-run"
    assert obj["payload"]["model_version"] == "0.8.0"
    assert obj["payload"]["output_summary"]["stock_change_Mg_C_ha"] == pytest.approx(7.8)
    assert packet["provenance"][0]["event_type"] == "modeled"
    assert len(packet["links"]) == 2


def test_project_packet_requires_project_id():
    with pytest.raises(SoilCarbonChangeV0800Error, match="project_id is required"):
        build_project_packet({"comparison": comparison()})
