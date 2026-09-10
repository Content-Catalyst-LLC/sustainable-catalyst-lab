import pytest

from app.advanced_scientific_scene_v0880 import (
    AdvancedScientificSceneError,
    ENGINE_VERSION,
    VERSION,
    build_render_plan,
    build_workspace,
    health,
    normalize_camera,
    normalize_light,
    normalize_material,
    normalize_node,
    normalize_scene,
    scene_descriptor,
)


def base_scene():
    return {
        "id": "scene-a",
        "rendererPreference": "native-webgpu",
        "cameras": [{"id": "camera-main", "position": [3, 2, 5], "target": [0, 0, 0]}],
        "activeCameraId": "camera-main",
        "lights": [
            {"id": "ambient", "type": "ambient", "intensity": 0.25},
            {"id": "key", "type": "directional", "direction": [0.4, 0.7, 0.8], "intensity": 0.9},
        ],
        "materials": [{"id": "mat", "type": "scientific-lambert", "color": [0.2, 0.7, 0.95, 1]}],
        "nodes": [
            {"id": "root", "type": "group", "children": ["cloud", "mesh"]},
            {"id": "cloud", "type": "point-cloud", "materialId": "mat", "geometry": {"vertexCount": 1000, "instanceCount": 1}, "sourceObjectId": "dataset:cloud"},
            {"id": "mesh", "type": "mesh", "materialId": "mat", "geometry": {"vertexCount": 8, "indexCount": 36, "instanceCount": 4}, "sourceObjectId": "mesh:cube"},
        ],
    }


def test_health_and_descriptor():
    h = health()
    assert h["ok"] is True
    assert h["version"] == VERSION == "0.88.0"
    assert h["engineVersion"] == ENGINE_VERSION == "2.14.0"
    assert h["nativeWebGPUSceneRendererReady"] is True
    assert h["threeJSAdapterReady"] is True
    assert h["threeJSRuntimeBundled"] is False
    assert h["externalCDNRequired"] is False
    d = scene_descriptor()
    assert d["boundaries"]["arbitraryShaderSource"] is False
    assert d["boundaries"]["silentRendererFallback"] is False
    assert d["boundaries"]["threeJSRequiredForScientificCorrectness"] is False


def test_camera_light_material_normalization():
    camera = normalize_camera({"projection": "orthographic", "orthographicScale": 4})
    assert camera["projection"] == "orthographic"
    assert camera["interaction"]["orbit"] is True
    light = normalize_light({"type": "point", "position": [1, 2, 3], "range": 12})
    assert light["presentationOnly"] is True
    material = normalize_material({"type": "scientific-phong", "color": [1, 0.5, 0.25, 0.8]})
    assert material["presentationOnly"] is True
    with pytest.raises(AdvancedScientificSceneError):
        normalize_material({"wgsl": "@fragment fn f(){}"})


def test_scene_graph_and_render_plan():
    s = normalize_scene(base_scene())
    assert s["rootNodeIds"] == ["root"]
    assert s["renderableNodeCount"] == 2
    built = build_render_plan({"scene": base_scene()})
    assert built["ok"] is True
    plan = built["renderPlan"]
    assert plan["drawCallCount"] == 2
    assert {p["primitive"] for p in plan["passes"]} == {"point-list", "triangle-list"}
    assert plan["fallbackPolicy"]["silent"] is False


def test_scene_graph_rejects_cycles_and_missing_materials():
    cyc = base_scene()
    cyc["nodes"][0]["children"] = ["cloud"]
    cyc["nodes"][1]["children"] = ["root"]
    with pytest.raises(AdvancedScientificSceneError, match="cycle"):
        normalize_scene(cyc)
    bad = base_scene()
    bad["nodes"][1]["materialId"] = "not-declared"
    with pytest.raises(AdvancedScientificSceneError, match="missing material"):
        normalize_scene(bad)


def test_instancing_limits_and_workspace_provenance():
    node = normalize_node({"type": "mesh", "geometry": {"vertexCount": 8, "indexCount": 36, "instanceCount": 1_000_000}})
    assert node["geometry"]["instanceCount"] == 1_000_000
    with pytest.raises(AdvancedScientificSceneError):
        normalize_node({"type": "mesh", "geometry": {"vertexCount": 8, "instanceCount": 1_000_001}})
    out = build_workspace({"scene": base_scene(), "workspaceId": "ws"})
    assert out["workspace"]["compatibility"]["v0870WebGPU"] is True
    assert len(out["workspace"]["fingerprint"]) == 64
