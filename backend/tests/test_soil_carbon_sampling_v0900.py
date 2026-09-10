import pytest
from app.soil_carbon_sampling_v0900 import (
    DOMAIN_VERSION, LAB_RELEASE_VERSION, SoilCarbonSamplingV0700Error,
    calculate_bulk_density, normalize_sample, normalize_batch, build_sampling_design,
    build_profile_handoff, build_field_packet, health, policies, schema,
)


def sample(**patch):
    row={
        "sample_id":"S1","project_id":"project:demo","parcel_id":"parcel:demo","profile_id":"profile:demo",
        "sampling_method":"stratified-random","sample_type":"intact-core","collected_at":"2026-09-10T12:00:00+00:00",
        "collector_ref":"actor:field-tech","latitude":41.88,"longitude":-87.63,
        "top_depth":0,"bottom_depth":30,"depth_unit":"cm","soc_value":2,"soc_unit":"percent",
        "dry_mass_g":130,"core_volume_cm3":100,"mass_basis":"whole-dry-soil","coarse_fragments_percent":0,
        "lab_sample_id":"lab:S1","lab_method_ref":"method:dry-combustion","source_refs":["source:field-sheet"],
        "custody_events":[{"event_type":"collected","event_id":"custody:S1:1","occurred_at":"2026-09-10T12:00:00+00:00","actor_ref":"actor:field-tech"}],
    }
    row.update(patch); return row


def test_identity_and_health():
    assert DOMAIN_VERSION=="0.7.0" and LAB_RELEASE_VERSION=="0.90.0"
    assert health()["status"]=="soc-sampling-field-measurement-ready"
    assert policies()["guardrails"]["spatial_randomization_not_inferred"] is True
    assert schema()["canonical_units"]["coordinates"]=="EPSG:4326"


def test_bulk_density_reference_fixture():
    r=calculate_bulk_density({"dry_mass_g":130,"core_volume_cm3":100,"mass_basis":"whole-dry-soil"})
    assert r["bulk_density_g_cm3"]==pytest.approx(1.3)


def test_bulk_density_rejects_impossible_value():
    with pytest.raises(SoilCarbonSamplingV0700Error):
        calculate_bulk_density({"dry_mass_g":400,"core_volume_cm3":100})


def test_sample_normalization_and_profile_readiness():
    r=normalize_sample(sample())
    assert r["soc_g_per_kg"]==pytest.approx(20)
    assert r["bulk_density_g_cm3"]==pytest.approx(1.3)
    assert r["coordinates"]["crs"]=="EPSG:4326"
    assert r["readiness"]["soc_profile_input_ready"] is True


def test_sample_without_lab_result_is_valid_but_not_profile_ready():
    r=normalize_sample(sample(soc_value=None, lab_method_ref=None, lab_sample_id=None))
    assert r["readiness"]["soc_profile_input_ready"] is False


def test_coordinate_pair_required():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="supplied together"):
        normalize_sample(sample(longitude=None))


def test_supplied_and_calculated_bulk_density_must_agree():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="disagree"):
        normalize_sample(sample(bulk_density_value=1.4, bulk_density_unit="g/cm3"))


def test_batch_requires_unique_sample_ids():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="unique"):
        normalize_batch({"samples":[sample(),sample()]})


def test_sampling_design_generates_ids_not_coordinates():
    d=build_sampling_design({"design_id":"design:demo","project_id":"project:demo","parcel_id":"parcel:demo","sampling_method":"stratified-random","strata":[{"stratum_id":"upland","target_samples":2},{"stratum_id":"lowland","target_samples":1}]})
    assert d["target_sample_count"]==3
    assert len(d["planned_samples"])==3
    assert all(x["coordinates"] is None for x in d["planned_samples"])
    assert d["design_boundaries"]["spatial_randomization_performed"] is False


def test_sampling_design_rejects_fractional_target():
    with pytest.raises(SoilCarbonSamplingV0700Error):
        build_sampling_design({"design_id":"design:demo","strata":[{"stratum_id":"a","target_samples":1.5}]})


def test_profile_handoff_uses_v0600_contract_and_reference_stock():
    h=build_profile_handoff({"batch_id":"batch:demo","profile_id":"profile:demo","samples":[sample()]})
    assert h["compatibility_validation"]["ok"] is True
    assert h["compatibility_validation"]["calculated_stock_Mg_C_ha"]==pytest.approx(78.0)
    assert h["profile_input"]["layers"][0]["soc_unit"]=="g/kg"


def test_profile_handoff_refuses_implicit_replicate_aggregation():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="replicate aggregation"):
        build_profile_handoff({"samples":[sample(),sample(sample_id="S2",replicate=2)]})


def test_field_packet_creates_sample_and_observations():
    p=build_field_packet({"project_id":"project:demo","samples":[sample()]})
    types=[x["object_type"] for x in p["packet"]["objects"]]
    assert types.count("sample")==1 and types.count("observation")==2
    assert len(p["packet"]["links"])==2
    assert p["packet"]["provenance"][0]["event_type"]=="collected"


def test_missing_project_id_rejected_for_project_packet():
    row=sample(project_id=None)
    with pytest.raises(SoilCarbonSamplingV0700Error, match="project_id is required"):
        build_field_packet({"samples":[row]})


def test_replicate_must_be_integer():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="integer"):
        normalize_sample(sample(replicate=1.5))


def test_custody_event_ids_must_be_unique():
    events=[
        {"event_type":"collected","event_id":"custody:dup","occurred_at":"2026-09-10T12:00:00+00:00"},
        {"event_type":"received","event_id":"custody:dup","occurred_at":"2026-09-10T13:00:00+00:00"},
    ]
    with pytest.raises(SoilCarbonSamplingV0700Error, match="custody event_id"):
        normalize_sample(sample(custody_events=events))


def test_sampling_design_rejects_duplicate_strata():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="stratum_id values must be unique"):
        build_sampling_design({"design_id":"design:demo","strata":[{"stratum_id":"upland","target_samples":1},{"stratum_id":"upland","target_samples":1}]})


def test_sampling_design_generated_ids_round_trip_when_input_ids_are_long():
    design_id="d" + "x"*120
    stratum_id="s" + "y"*120
    d=build_sampling_design({"design_id":design_id,"strata":[{"stratum_id":stratum_id,"target_samples":1}]})
    generated=d["planned_samples"][0]["sample_id"]
    assert len(generated) <= 160
    r=normalize_sample(sample(sample_id=generated))
    assert r["sample_id"] == generated


def test_profile_handoff_rejects_mixed_profile_ids():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="multiple profile_id"):
        build_profile_handoff({"samples":[sample(),sample(sample_id="S2",profile_id="profile:other",top_depth=30,bottom_depth=60)]})


def test_profile_handoff_rejects_explicit_profile_conflict():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="conflicts"):
        build_profile_handoff({"profile_id":"profile:other","samples":[sample()]})


def test_field_packet_rejects_mixed_project_ids():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="multiple project_id"):
        build_field_packet({"samples":[sample(),sample(sample_id="S2",project_id="project:other",top_depth=30,bottom_depth=60)]})


def test_field_packet_rejects_explicit_project_conflict():
    with pytest.raises(SoilCarbonSamplingV0700Error, match="conflicts"):
        build_field_packet({"project_id":"project:other","samples":[sample()]})

@pytest.mark.parametrize("patch",[
    {"bottom_depth":0},{"coarse_fragments_percent":100},{"latitude":91},{"sampling_method":"magic"},{"sample_type":"mystery"},{"replicate":0},
])
def test_invalid_sample_inputs_rejected(patch):
    with pytest.raises(SoilCarbonSamplingV0700Error): normalize_sample(sample(**patch))


def test_fingerprints_are_deterministic():
    a=normalize_sample(sample()); b=normalize_sample(sample())
    assert a["sample_fingerprint"]==b["sample_fingerprint"]
