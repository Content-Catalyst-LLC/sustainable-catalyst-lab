import math
import pytest

from app.soil_organic_carbon_v0890 import (
    DOMAIN_VERSION, LAB_RELEASE_VERSION, SoilOrganicCarbonV0600Error,
    calculate_layer_stock, calculate_profile_stock, build_project_packet, health, policies, schema,
)


def layer(**overrides):
    row={"layer_id":"layer-1","top_depth":0,"bottom_depth":30,"depth_unit":"cm","soc_value":2,"soc_unit":"percent","bulk_density_value":1.3,"bulk_density_unit":"g/cm3","coarse_fragments_percent":0}
    row.update(overrides); return row


def test_identity_and_boundaries():
    assert DOMAIN_VERSION=="0.6.0" and LAB_RELEASE_VERSION=="0.89.0"
    assert health()["status"]=="soil-organic-carbon-foundation-ready"
    assert policies()["guardrails"]["sequestration_rate_not_inferred"] is True
    assert schema()["canonical_units"]["stock"]=="Mg C/ha"


def test_reference_layer_formula():
    result=calculate_layer_stock(layer())
    assert result["soc_stock_Mg_C_ha"] == pytest.approx(78.0)
    assert result["soil_mass_Mg_dry_soil_ha"] == pytest.approx(3900.0)


def test_coarse_fragment_correction():
    result=calculate_layer_stock(layer(coarse_fragments_percent=20))
    assert result["soc_stock_Mg_C_ha"] == pytest.approx(62.4)


def test_unit_normalization_equivalence():
    a=calculate_layer_stock(layer())
    b=calculate_layer_stock(layer(soc_value=20,soc_unit="g/kg",bulk_density_value=1300,bulk_density_unit="kg/m3",bottom_depth=.3,depth_unit="m"))
    assert b["soc_stock_Mg_C_ha"] == pytest.approx(a["soc_stock_Mg_C_ha"])


def test_profile_aggregation_and_area_scaling():
    result=calculate_profile_stock({"profile_id":"profile-1","area_ha":2.5,"layers":[layer(layer_id="a",bottom_depth=15),layer(layer_id="b",top_depth=15,bottom_depth=30,soc_value=1.5)]})
    assert result["layer_count"]==2
    assert result["depth"]["contiguous"] is True
    assert result["soc_stock_Mg_C_total"] == pytest.approx(result["soc_stock_Mg_C_ha"]*2.5)


def test_profile_reports_gaps_without_filling_them():
    result=calculate_profile_stock({"layers":[layer(layer_id="a",bottom_depth=10),layer(layer_id="b",top_depth=20,bottom_depth=30)]})
    assert result["depth"]["contiguous"] is False
    assert result["depth"]["gaps"]==[{"top_depth_cm":10.0,"bottom_depth_cm":20.0}]


def test_overlapping_layers_are_rejected():
    with pytest.raises(SoilOrganicCarbonV0600Error, match="must not overlap"):
        calculate_profile_stock({"layers":[layer(layer_id="a",bottom_depth=20),layer(layer_id="b",top_depth=10,bottom_depth=30)]})

@pytest.mark.parametrize("patch",[
    {"bottom_depth":0}, {"soc_value":-1}, {"soc_value":101,"soc_unit":"percent"},
    {"bulk_density_value":0}, {"bulk_density_value":4}, {"coarse_fragments_percent":100},
])
def test_invalid_physical_inputs_are_rejected(patch):
    with pytest.raises(SoilOrganicCarbonV0600Error): calculate_layer_stock(layer(**patch))


def test_no_implicit_co2e_or_sequestration_claims():
    result=calculate_profile_stock({"layers":[layer()]})
    text=str(result).lower()
    assert "co2e" not in result
    assert result["guardrails"]["co2e_not_inferred"] is True
    assert result["guardrails"]["stock_change_not_inferred"] is True


def test_deterministic_fingerprints():
    a=calculate_profile_stock({"profile_id":"stable","layers":[layer()]})
    b=calculate_profile_stock({"profile_id":"stable","layers":[layer()]})
    assert a["input_fingerprint"]==b["input_fingerprint"]
    assert a["result_fingerprint"]==b["result_fingerprint"]


def test_project_packet_aligns_with_library_contract():
    result=build_project_packet({"project_id":"project:demo","parcel_id":"parcel:demo","actor_ref":"system:lab","run_at":"2026-09-10T08:00:00+00:00","input_object_ids":["observation:soc","observation:bd"],"profile":{"layers":[layer()]}})
    packet=result["packet"]
    assert packet["schema"]=="sc-carbon-project-packet/1.0"
    obj=packet["objects"][0]
    assert obj["object_type"]=="model-run"
    assert obj["payload"]["model_version"]=="0.6.0"
    assert obj["payload"]["output_summary"]["soc_stock_Mg_C_ha"]==pytest.approx(78.0)
    assert packet["provenance"][0]["event_type"]=="modeled"
    assert len(packet["links"])==2


def test_project_packet_does_not_invent_input_objects():
    result=build_project_packet({"project_id":"project:demo","profile":{"layers":[layer()]}})
    assert len(result["packet"]["objects"])==1
    assert result["packet"]["links"]==[]
