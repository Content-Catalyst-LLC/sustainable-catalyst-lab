from app.energy_grid_reliability import framework, plan, analyze, validate_result


def request():
    return {"study_id":"adequacy-1","question":"How sensitive is adequacy to explicit scenario assumptions?","baseline":{"demand_kw_series":[100,120,130,90],"renewable_generation_kw_series":[20,30,20,40],"storage_discharge_available_kw_series":[10,10,10,10],"firm_capacity_kw":80,"timestep_hours":1},"uncertainty":{"variables":[{"name":"demand_multiplier","distribution":"uniform","low":0.9,"high":1.1},{"name":"firm_forced_outage_rate_pct","distribution":"uniform","low":0,"high":10}],"design":{"method":"monte-carlo","samples":16,"seed":42}},"provenance":[{"source_ref":"scenario:test"}],"review":{"human_review_required":True}}


def test_framework_and_plan_are_bounded_and_reproducible():
    f=framework(); assert f["lab_version"]=="0.103.0"; assert f["version"]=="1.6.0"; assert f["workbench_required_version"]=="6.3.0"; assert f["capabilities"]["automatic_workbench_execution"] is False
    a=plan(request()); b=plan(request()); assert a["plan_id"]==b["plan_id"]; assert a["evaluation_count"]==16
    packet=a["workbench"]["handoff"]["packet"]; reqs=packet["payload"]["grid_storage_reliability"]["calculation_requests"]
    assert len(reqs)==16; assert all(r["operation"]=="adequacy-timeseries" for r in reqs); assert a["workbench"]["execution_performed"] is False


def test_analysis_summarizes_workbench_results_without_reliability_declaration():
    p=plan(request()); results=[]
    for row in p["evaluation_map"]:
        # deterministic fake Workbench result matching the certified result contract shape.
        i=row["evaluation_index"]; ens=float(i%4)*10.0; lol=1.0 if ens else 0.0
        results.append({"request_id":row["request_id"],"operation":"adequacy-timeseries","output":{"energy_not_served_kwh":str(ens),"loss_of_load_hours":str(lol),"loss_of_load_events":str(int(lol)),"served_energy_pct":str(100.0-ens/10.0)}})
    wb={"schema":"sc-energy-workbench-result-packet/1.0","workbench_version":"6.3.0","results":results}
    a=analyze({"plan":p,"workbench_result":wb}); assert a["sample_count"]==16; assert a["output"]["probability_any_energy_not_served"]==0.75; assert a["reliability_declaration"]["performed"] is False; assert validate_result(a)["valid"] is True
