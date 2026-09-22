from app.scientific_figure_intelligence_automatic_layout_v01190 import *
import pytest

BASE={
 "id":"fig-1","figure_ref":"lab:figure:fig-1","title":"Observed response","caption":"Declared caption.","alt_text":"Line chart of observed response.",
 "publication_profile":"web-responsive","width_px":1200,"height_px":760,
 "axes":{"x":{"title":"Time","unit":"year","labels":[str(x) for x in range(2000,2020)],"domain":[2000,2019],"scale":"linear"},"y":{"title":"Response","unit":"%","labels":["0","20","40","60","80","100"],"domain":[0,100],"scale":"linear"}},
 "legend":{"entries":[{"label":"Observed"},{"label":"Model"},{"label":"Forecast"}]},
 "panels":[{"id":"a"},{"id":"b"},{"id":"c"},{"id":"d"}],"shared_x":True,
 "annotations":[{"id":"a1","x":0.5,"y":0.4,"width_px":120,"height_px":32},{"id":"a2","x":0.51,"y":0.41,"width_px":120,"height_px":32}],
}

def test_health_manifest_catalog():
 assert health()["ok"] and health()["version"]=="0.119.0"
 assert manifest()["boundaries"]["automatic_scientific_encoding_changes"] is False
 assert "small-multiples" in catalog()["layout_modes"]

def test_context_and_analysis():
 f=normalize_figure_context(BASE); assert f["scientific_encoding_locked"] is True and len(f["context_hash"])==64
 a=analyze_figure(BASE); assert a["automatic_data_inspection"] is False

def test_axes_preserve_science():
 p=plan_axes(BASE); assert p["axes"]["x"]["domain_preserved"] is True and p["automatic_domain_changes"] is False
 assert p["axes"]["x"]["label_strategy"] in LABEL_STRATEGIES

def test_legend_and_panels():
 l=plan_legend(BASE); assert l["automatic_series_reordering"] is False
 p=plan_panels(BASE); assert p["panels"]["count"]==4 and p["automatic_panel_reordering"] is False

def test_annotation_collision_plan_preserves_annotations():
 p=plan_annotations(BASE); assert len(p["annotations"])==2 and p["automatic_annotation_deletion"] is False
 assert collision_audit(BASE)["annotation_count"]==2

def test_responsive_and_print():
 r=plan_responsive(BASE); assert r["preserve_panel_order"] is True and r["breakpoints"][-1]["columns"]==1
 pr=plan_print(BASE); assert pr["vector_first"] is True and pr["automatic_content_removal"] is False

def test_layout_and_explanation_are_deterministic():
 a=plan_layout(BASE)["layout"]; b=plan_layout(BASE)["layout"]
 assert a["layout_hash"]==b["layout_hash"] and a["scientific_encoding_locked"] is True
 assert explain_layout(BASE)["automatic_scientific_interpretation"] is False

def test_quality_and_accessibility():
 q=quality_audit(BASE); assert q["scientific_validity_certified"] is False
 assert accessibility_audit(BASE)["accessible"] is True

def test_combined_intelligence_snapshot_export():
 i=build_figure_intelligence(BASE)["figure_intelligence"]; assert len(i["intelligence_hash"])==64
 s=build_snapshot(BASE); assert s["automatic_persistence"] is False and len(s["snapshot"]["snapshot_hash"])==64
 e=build_export_plan({**BASE,"formats":["svg","pdf","json"]}); assert e["automatic_file_write"] is False

def test_core_plan_is_reference_first():
 c=build_core_visual_plan({**BASE,"session_id":"session-1"}); assert c["automatic_core_submission"] is False and c["core_changes_scientific_encoding"] is False

def test_missing_core_session_rejected():
 with pytest.raises(FigureLayoutIntelligenceError): build_core_visual_plan(BASE)
