from app.scientific_visualization_design_system_v01140 import *

BASE={"kind":"line","title":"Observed and modeled response","axes":{"x":{"label":"Time","unit":"day"},"y":{"label":"Response","unit":"mg/L"}},"series":[{"id":"obs","label":"Observed","semantic_role":"observed","points":[{"x":0,"y":1},{"x":1,"y":2}]},{"id":"mod","label":"Model","semantic_role":"model","points":[{"x":0,"y":1.1},{"x":1,"y":1.9}]}],"publication":{"caption":"Observed and modeled response.","source":"Lab fixture","method":"Illustrative fixture."}}

def test_catalog_and_tokens():
    assert len(catalog()["profiles"])==6
    assert design_tokens()["typography"]["title_px"]==18

def test_normalize_and_profile():
    f=normalize_figure({"spec":BASE,"profile":"journal-double"})["figure"]
    assert f["profile"]=="journal-double" and f["rendering"]["vector_first"] is True
    assert [x["role"] for x in f["semantic_series"]]==["observed","model"]

def test_annotations_and_uncertainty():
    a=build_annotation_plan({"annotations":[{"type":"finding","text":"Peak response","x":1,"y":2,"evidence_ref":"e:1"}]})
    assert a["annotations"][0]["leader_line"] is True
    u=style_uncertainty({"layers":[{"kind":"confidence","level":.95,"label":"95% CI"}]})
    assert u["layers"][0]["style"]["fill_opacity"]>0 and u["automatic_uncertainty_inference"] is False

def test_small_multiples_responsive():
    c=compose_small_multiples({"panels":[{"id":"a"},{"id":"b"},{"id":"c"}],"columns":3})
    assert c["layout"]["rows"]==1 and c["responsive"]["mobile_columns"]==1

def test_accessibility_is_declared_not_inferred():
    a=accessibility_metadata({"alt_text":"Line chart comparing observations and model."})
    assert a["accessibility"]["color_only_encoding"] is False and a["automatic_alt_text_inference"] is False

def test_renderer_and_export_plan():
    f=normalize_figure({"spec":BASE})["figure"]
    r=renderer_plan({"figure":f,"publication":True}); assert r["preferred_renderer"]=="svg2d" and r["vector_first"] is True
    e=build_export_plan({"figure":f,"formats":["svg","pdf","png"]}); assert e["vector_formats"]==["svg","pdf"] and e["automatic_file_write"] is False

def test_publication_figure_and_audit():
    result=build_publication_figure({"spec":BASE,"profile":"journal-double","alt_text":"Two line series comparing observed and modeled response.","annotations":[{"type":"method-note","text":"Model is shown for comparison."}]})
    assert result["audit"]["publication_ready"] is True
    assert result["figure"]["accessibility"]["alt_text"]
    assert result["export_plan"]["include_provenance_id"] is True

def test_missing_axis_labels_block_publication():
    bad={**BASE,"axes":{"x":{"label":""},"y":{"label":""}}}
    # v0.74 normalizer supplies X/Y defaults; explicitly constructed figure demonstrates audit rule.
    f=normalize_figure({"spec":BASE})["figure"]
    f["spec"]["axes"]["x"]["label"]=""; f["spec"]["axes"]["y"]["label"]=""
    assert audit_figure({"figure":f})["publication_ready"] is False

def test_manifest_boundaries():
    m=manifest(); assert m["publication_grade_rendering"] is True
    assert m["boundaries"]["automatic_scientific_validity_certification"] is False
