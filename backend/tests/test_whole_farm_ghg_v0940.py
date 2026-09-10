import pytest
from app.whole_farm_ghg_v0940 import DOMAIN_VERSION,LAB_RELEASE_VERSION,CO2_PER_C,WholeFarmGHGV01100Error,normalize_entry,calculate_balance,build_project_packet,health,policies,schema

def direct(entry_id="direct:1",value=1000,direction="emission",**extra):
    p={"entry_id":entry_id,"category":"energy","direction":direction,"co2e_kg":value,"source_refs":["evidence:user-record"]};p.update(extra);return p

def test_identity_and_health():
    assert LAB_RELEASE_VERSION=="0.94.0" and DOMAIN_VERSION=="0.11.0";assert health()["status"]=="whole-farm-ghg-balance-ready";assert policies()["guardrails"]["no_default_non_co2_gwp_factors"] is True;assert schema()["entry_calculation_bases"]==["direct-co2e","gas-mass","activity-factor"]
def test_direct_co2e_emission():
    r=normalize_entry(direct());assert r["signed_co2e_kg"]==pytest.approx(1000);assert r["calculation_basis"]=="direct-co2e"
def test_direct_removal_sign(): assert normalize_entry(direct(value=200,direction="removal"))["signed_co2e_kg"]==pytest.approx(-200)
def test_co2_mass_identity_gwp():
    r=normalize_entry({"entry_id":"co2","category":"fuel","direction":"emission","gas":"CO2","mass_kg":25});assert r["gwp_factor"]==1 and r["signed_co2e_kg"]==25
def test_non_co2_requires_explicit_gwp():
    with pytest.raises(WholeFarmGHGV01100Error,match="no GWP factor supplied"): normalize_entry({"entry_id":"ch4","category":"livestock","gas":"CH4","mass_kg":2})
def test_entry_specific_gwp_requires_source():
    with pytest.raises(WholeFarmGHGV01100Error,match="gwp_source_ref is required"): normalize_entry({"entry_id":"ch4","category":"livestock","gas":"CH4","mass_kg":2,"gwp100":10})
def test_entry_specific_gwp_calculation(): assert normalize_entry({"entry_id":"ch4","category":"livestock","gas":"CH4","mass_kg":2,"gwp100":10,"gwp_source_ref":"source:test-gwp"})["signed_co2e_kg"]==pytest.approx(20)
def test_gwp_set_requires_source_for_non_co2():
    with pytest.raises(WholeFarmGHGV01100Error,match="source_ref is required"): calculate_balance({"entries":[{"entry_id":"ch4","category":"livestock","gas":"CH4","mass_kg":2}],"gwp_set":{"factors":{"CH4":10}}})
def test_activity_factor_requires_source():
    with pytest.raises(WholeFarmGHGV01100Error,match="factor_source_ref is required"): normalize_entry({"entry_id":"diesel","category":"fuel","activity_value":100,"activity_unit":"L","emission_factor_kg_co2e_per_unit":2.5})
def test_activity_factor_calculation(): assert normalize_entry({"entry_id":"diesel","category":"fuel","activity_value":100,"activity_unit":"L","emission_factor_kg_co2e_per_unit":2.5,"factor_source_ref":"factor:test"})["signed_co2e_kg"]==pytest.approx(250)
def test_exactly_one_basis_required():
    with pytest.raises(WholeFarmGHGV01100Error,match="exactly one"): normalize_entry({"entry_id":"bad","category":"x","co2e_kg":1,"gas":"CO2","mass_kg":1})
def test_balance_reference_fixture():
    p={"balance_id":"fixture:whole-farm","area_ha":1,"gwp_set":{"name":"fixture","source_ref":"source:user-gwp","factors":{"CH4":10,"N2O":100}},"entries":[{"entry_id":"co2","category":"fuel","gas":"CO2","mass_kg":1000,"direction":"emission"},{"entry_id":"ch4","category":"livestock","gas":"CH4","mass_kg":10,"direction":"emission"},{"entry_id":"n2o","category":"soil-nitrogen","gas":"N2O","mass_kg":1,"direction":"emission"}],"soc_stock_change":{"stock_change_Mg_C_ha":0.1,"basis":"measured-change","include_in_net":True,"source_refs":["model-run:soc-change"]}}
    r=calculate_balance(p);assert r["gross_emissions_kg_CO2e"]==pytest.approx(1200);assert r["gross_removals_kg_CO2e"]==pytest.approx(0.1*1000*CO2_PER_C);assert r["net_balance_kg_CO2e"]==pytest.approx(833.3333333333334);assert r["net_direction"]=="net-emissions"
def test_soc_is_excluded_from_net_unless_explicit():
    r=calculate_balance({"area_ha":1,"entries":[direct()],"soc_stock_change":{"stock_change_Mg_C_ha":1,"basis":"measured-change","include_in_net":False}});assert r["net_balance_kg_CO2e"]==pytest.approx(1000);assert r["soc_stock_change"]["signed_co2e_kg"]==pytest.approx(-1000*CO2_PER_C)
def test_soc_negative_stock_change_is_emission():
    r=calculate_balance({"area_ha":2,"entries":[direct(value=0)],"soc_stock_change":{"stock_change_Mg_C_ha":-1,"basis":"measured-change","include_in_net":True}});assert r["gross_emissions_kg_CO2e"]==pytest.approx(2*1000*CO2_PER_C)
def test_area_required_for_soc_conversion():
    with pytest.raises(WholeFarmGHGV01100Error,match="area_ha is required"): calculate_balance({"entries":[direct()],"soc_stock_change":{"stock_change_Mg_C_ha":1,"basis":"measured-change","include_in_net":True}})
def test_category_and_gas_aggregation():
    r=calculate_balance({"gwp_set":{"source_ref":"source:gwp","factors":{"CH4":5}},"entries":[{"entry_id":"a","category":"livestock","gas":"CH4","mass_kg":2},{"entry_id":"b","category":"livestock","co2e_kg":5,"direction":"removal","source_refs":["e"]}]});assert r["by_category"]["livestock"]["net_kg_CO2e"]==pytest.approx(5);assert r["by_gas"]["CH4"]["gas_mass_kg"]==pytest.approx(2)
def test_annualization_requires_period():
    with pytest.raises(WholeFarmGHGV01100Error,match="period is required"): calculate_balance({"entries":[direct()],"annualize":True})
def test_period_validation_and_annualization():
    r=calculate_balance({"entries":[direct(value=365.2425)],"period":{"start_date":"2026-01-01","end_date":"2027-01-01"},"annualize":True});assert r["period"]["elapsed_days"]==365;assert r["annualized"]["net_kg_CO2e_per_year"]>365
def test_duplicate_ids_rejected():
    with pytest.raises(WholeFarmGHGV01100Error,match="entry_id values must be unique"): calculate_balance({"entries":[direct("x"),direct("x",2)]})
def test_direct_entries_without_sources_are_flagged_not_silently_rejected(): assert calculate_balance({"entries":[{"entry_id":"x","category":"other","co2e_kg":1}]})["evidence_diagnostics"]["direct_co2e_entries_without_source_refs"]==["x"]
def test_project_packet_is_draft_model_run():
    r=build_project_packet({"project_id":"project:test","balance":{"entries":[direct()]}});obj=r["packet"]["objects"][0];assert obj["object_type"]=="model-run" and obj["status"]=="draft";assert obj["payload"]["model_version"]=="0.11.0";assert obj["payload"]["guardrails"]["credit_eligibility_not_determined"] is True
def test_fingerprints_are_deterministic():
    p={"entries":[direct()]};a=calculate_balance(p);b=calculate_balance(p);assert a["input_fingerprint"]==b["input_fingerprint"] and a["result_fingerprint"]==b["result_fingerprint"]
def test_balance_is_not_verification_or_crediting():
    r=calculate_balance({"entries":[direct()]});assert r["interpretation"]["whole_farm_balance_is_verification"] is False;assert r["guardrails"]["additionality_not_determined"] is True;assert r["guardrails"]["credit_eligibility_not_determined"] is True
