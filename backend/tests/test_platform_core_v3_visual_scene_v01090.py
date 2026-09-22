from app.platform_core_v3_visual_scene_v01090 import (
    build_core_scene_contract, build_core_visual_binding, bridge_linked_views,
    bridge_uncertainty_visual, health, manifest, map_legacy_scene, normalize_scene,
    normalize_visual, renderer_catalog, negotiate_renderer,
)

CTX={"project_ref":"project:p1","session_id":"8","session_key":"s1","title":"Study","workflow_ref":"lab:workflow:w1","project_state_ref":"core:state:1","researcher_ref":"researcher:r1"}
SCENE={
 "id":"scene-1","title":"Test scene","rendererPreference":"native-webgpu",
 "cameras":[{"id":"cam-1","type":"perspective"}],
 "nodes":[{"id":"points","type":"point-cloud","name":"Points","sourceObjectId":"lab:dataset:d1","vertexCount":3,"children":[]}]
}

def test_health_manifest_boundaries():
    h=health(); m=manifest()
    assert h["lab_release_version"]=="0.109.0" and h["minimum_core_release"]=="3.0.0"
    assert h["renderer_count"] >= 4
    assert m["boundaries"]["core_renders_visuals"] is False
    assert m["boundaries"]["bridge_auto_submits_to_core"] is False

def test_visual_normalize_and_binding():
    n=normalize_visual({"context":CTX,"visual":{"id":"v1","visual_type":"scientific-figure","title":"Figure","source_refs":["lab:dataset:d1"],"renderer":"svg2d"}})
    assert n["visual"]["visual_ref"]=="lab:visual:v1"
    b=build_core_visual_binding({"context":CTX,"visual":n["visual"]})
    assert b["target_endpoint"].endswith("/visual-bindings")
    assert b["data"]["session_id"]=="8"
    assert b["data"]["source_refs"]==["lab:dataset:d1"]
    assert b["automatic_submission"] is False

def test_advanced_scene_to_core_scene_contract():
    n=normalize_scene({"context":CTX,"scene":SCENE})
    assert n["scene"]["scene_kind"]=="advanced-scene"
    s=build_core_scene_contract({"context":CTX,"scene":SCENE})
    assert s["core_scene"]["contract"]=="sc.visual-runtime.scene.v1"
    assert s["core_scene"]["nodes"][0]["source_ref"]=="lab:dataset:d1"
    assert s["automatic_rendering"] is False

def test_legacy_scene_map_builds_visual_binding():
    x=map_legacy_scene({"context":CTX,"scene":SCENE})
    assert x["core_visual_binding"]["data"]["visual_type"]=="scientific-scene"
    assert x["core_visual_binding"]["data"]["scene_ref"].startswith("lab:scientific-scene:")
    assert x["automatic_rendering"] is False

def test_linked_views_bridge_does_not_infer_links():
    comp={"title":"Linked","views":[{"id":"a","renderer":"svg2d","datasetId":"d1"},{"id":"b","renderer":"canvas3d","datasetId":"d1"}],"links":[{"sourceViewId":"a","targetViewIds":["b"],"channel":"selection","key":"id"}]}
    x=bridge_linked_views({"context":CTX,"composition":comp,"source_refs":["lab:dataset:d1"]})
    assert x["composition"]["links"][0]["sourceViewId"]=="a"
    assert x["automatic_link_inference"] is False
    assert x["core_visual_binding"]["data"]["visual_type"]=="linked-views"

def test_uncertainty_visual_bridge_preserves_declared_uncertainty():
    layer={"id":"u1","uncertaintySeries":[{"id":"s1","type":"interval","semantics":"custom","records":[{"x":0,"center":2,"lower":1.5,"upper":2.5},{"x":1,"center":3,"lower":2.5,"upper":3.5}],"units":"m"}]}
    x=bridge_uncertainty_visual({"context":CTX,"layer":layer,"source_refs":["lab:result:r1"]})
    assert x["automatic_uncertainty_inference"] is False
    assert x["core_visual_binding"]["data"]["visual_type"]=="uncertainty-view"

def test_renderer_catalog_and_negotiation():
    c=renderer_catalog(); assert c["core_renders_visuals"] is False and len(c["registry"]["renderers"])>=4
    n=negotiate_renderer({"browserCapabilities":{"detected":{"svg":True,"canvas2d":True,"webgl2":True,"webgpu":False}},"requiredFeatures":["3d"],"preferredRenderers":["webgpu","webgl2","canvas3d"],"allowFallback":True})
    assert n["decision"]["selectedRenderer"] in {"webgl2","canvas3d"}
    assert n["core_renderer_selection"] is False
