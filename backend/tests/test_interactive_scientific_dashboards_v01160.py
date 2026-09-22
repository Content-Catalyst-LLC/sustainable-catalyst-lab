import pytest
from app.interactive_scientific_dashboards_v01160 import *

PANEL_A={"id":"a","title":"Observed","renderer":"svg2d","figure_kind":"scatter","figure_ref":"lab:figure:a","source_refs":["lab:dataset:d1"],"spec":{"kind":"scatter","title":"Observed","axes":{"x":{"label":"X","unit":"unitless"},"y":{"label":"Y","unit":"unitless"}},"series":[{"id":"s1","points":[{"x":1,"y":2}]}],"publication":{"caption":"A","source":"fixture"},"accessibility":{"alt_text":"Observed scatter plot."}}}
PANEL_B={"id":"b","title":"Model","renderer":"svg2d","figure_kind":"line","figure_ref":"lab:figure:b","source_refs":["lab:model:m1"],"spec":{"kind":"line","title":"Model","axes":{"x":{"label":"X","unit":"unitless"},"y":{"label":"Y","unit":"unitless"}},"series":[{"id":"s2","points":[{"x":1,"y":2}]}],"publication":{"caption":"B","source":"fixture"},"accessibility":{"alt_text":"Model line plot."}}}

def dashboard():
    return {"id":"dash-1","title":"Scientific dashboard","panels":[PANEL_A,PANEL_B],"controls":[{"id":"c1","type":"category-filter","key":"group","target_panel_ids":["a","b"]}],"links":[{"id":"l1","source_panel_id":"a","target_panel_ids":["b"],"channel":"selection","key":"sample","direction":"bidirectional"}],"layout":{"type":"grid","columns":2}}

def test_catalog_and_manifest():
    assert len(catalog()["interaction_channels"])==7
    assert manifest()["features"]["linked_brushing"] is True
    assert manifest()["boundaries"]["automatic_cross_dataset_join"] is False

def test_normalize_dashboard():
    d=normalize_dashboard(dashboard())["dashboard"]
    assert len(d["panels"])==2 and d["layout"]["responsive"]["mobile_columns"]==1
    assert d["controls"][0]["target_panel_ids"]==["a","b"]

def test_unknown_link_panel_rejected():
    bad=dashboard(); bad["links"]=[{"source_panel_id":"a","target_panel_ids":["missing"],"channel":"selection"}]
    with pytest.raises(InteractiveDashboardError): normalize_dashboard(bad)

def test_small_multiples():
    sm=compose_small_multiples({"panels":[PANEL_A,PANEL_B],"columns":2,"shared_x":True})
    assert sm["composition"]["responsive"]["mobile_columns"]==1
    assert sm["automatic_scale_harmonization"] is False

def test_linked_interaction_propagation():
    result=propagate_interaction({"dashboard":dashboard(),"event":{"source_panel_id":"a","channel":"selection","value":[1,2]}})
    assert result["propagation_count"]==1 and result["updates"][0]["panel_id"]=="b"
    reverse=propagate_interaction({"dashboard":dashboard(),"event":{"source_panel_id":"b","channel":"selection","value":[3]}})
    assert reverse["updates"][0]["panel_id"]=="a"

def test_filter_state_is_declarative():
    state=build_filter_state({"filters":[{"key":"country","operator":"in","value":["US","CA"]}]})["state"]
    assert state["filter_count"]==1 and state["automatic_query_execution"] is False

def test_scale_sync_requires_declared_domains():
    with pytest.raises(InteractiveDashboardError): synchronize_scales({"groups":[{"id":"g","axis":"x","panel_ids":["a","b"]}]})
    s=synchronize_scales({"groups":[{"id":"g","axis":"x","panel_ids":["a","b"],"declared_domains":[[0,10],[-2,8]]}]})
    assert s["groups"][0]["synchronized_domain"]==[-2.0,10.0]
    assert s["automatic_domain_inference"] is False

def test_snapshot_and_restore():
    snap=snapshot_state({"dashboard":dashboard(),"filters":[{"key":"group","value":"A"}],"selections":{"a":[1]}})
    plan=restore_plan({"dashboard":dashboard(),"state":snap["state"]})
    assert plan["compatible"] is True and plan["automatic_restore"] is False
    changed=dashboard(); changed["title"]="Changed"
    assert restore_plan({"dashboard":changed,"state":snap["state"]})["compatible"] is False

def test_provenance_and_accessibility():
    p=provenance_trace({"dashboard":dashboard()})
    assert "lab:dataset:d1" in p["source_refs"] and p["automatic_source_inference"] is False
    a=accessibility_audit({"dashboard":dashboard()})
    assert a["dashboard_accessible"] is True and a["automatic_alt_text_inference"] is False

def test_export_publication_core_plan():
    e=export_plan({"dashboard":dashboard(),"mode":"publication-sheet","formats":["svg","pdf","json"]})
    assert e["automatic_file_write"] is False and len(e["panel_exports"])==2
    p=build_publication_dashboard({"dashboard":dashboard(),"formats":["svg","pdf","json"]})
    assert p["publication_ready"] is True and p["scientific_validity_certified"] is False
    c=core_visual_plan({"dashboard":dashboard(),"session_id":"s1"})
    assert c["binding_count"]==2 and c["automatic_core_submission"] is False
