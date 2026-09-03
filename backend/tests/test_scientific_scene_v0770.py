import pytest

from app.scientific_scene_v0770 import (
    ScientificSceneError,
    build_figure,
    build_workspace,
    health,
    normalize_camera,
    normalize_scene,
    policies,
    scene_from_dataset,
)


def rows(n=12):
    return [
        {"x": i / max(1, n - 1), "y": (i % 5) / 4, "z": (i % 7) / 6, "label": f"p-{i}", "dx": .1, "dy": .2, "dz": .3}
        for i in range(n)
    ]


def test_health_and_policy_identity():
    h = health()
    assert h["ok"] is True
    assert h["status"] == "scientific-3d-scene-ready"
    assert h["version"] == "0.77.0"
    assert h["engineVersion"] == "2.4.0"
    assert h["renderer"] == "canvas3d"
    assert h["webgl"] is False
    assert h["automaticTriangulation"] is False
    p = policies()
    assert p["explicitMeshTopologyRequired"] is True
    assert p["depthBuffer"] is False


def test_camera_normalizes_perspective_and_orthographic():
    p = normalize_camera({"projection": "perspective", "position": [4, 3, 5], "target": [0, 0, 0]})
    assert p["projection"] == "perspective"
    assert p["fingerprint"]
    o = normalize_camera({"projection": "orthographic", "position": [4, 3, 5], "target": [0, 0, 0], "orthographicScale": 3})
    assert o["projection"] == "orthographic"
    assert o["orthographicScale"] == 3


def test_camera_rejects_degenerate_view():
    with pytest.raises(ScientificSceneError, match="must differ"):
        normalize_camera({"position": [0, 0, 0], "target": [0, 0, 0]})


def test_point_cloud_scene_from_dataset_preserves_coordinates():
    source = rows(10)
    result = scene_from_dataset({
        "dataset": {"id": "points", "title": "Points", "rows": source, "units": {"x": "m", "y": "m", "z": "m"}},
        "mapping": {"x": "x", "y": "y", "z": "z", "label": "label"},
        "geometry": "point-cloud",
        "title": "3D points",
    })
    assert result["spec"]["renderer"] == "canvas3d"
    assert result["spec"]["kind"] == "point-cloud-3d"
    obj = result["scene"]["objects"][0]
    assert obj["type"] == "point-cloud"
    assert obj["vertices"][3] == [source[3]["x"], source[3]["y"], source[3]["z"]]
    assert result["scene"]["axes"]["units"] == {"x": "m", "y": "m", "z": "m"}


def test_polyline_preserves_row_order():
    source = rows(9)
    result = scene_from_dataset({"dataset": {"id": "path", "rows": source}, "mapping": {"x": "x", "y": "y", "z": "z"}, "geometry": "polyline"})
    assert result["scene"]["objects"][0]["vertices"][0] == [source[0]["x"], source[0]["y"], source[0]["z"]]
    assert result["scene"]["objects"][0]["vertices"][-1] == [source[-1]["x"], source[-1]["y"], source[-1]["z"]]


def test_vector_scene_requires_and_preserves_components():
    result = scene_from_dataset({"dataset": {"id": "vec", "rows": rows(6)}, "mapping": {"x": "x", "y": "y", "z": "z", "dx": "dx", "dy": "dy", "dz": "dz"}, "geometry": "vectors"})
    obj = result["scene"]["objects"][0]
    assert obj["type"] == "vectors"
    assert obj["vectors"][0] == [.1, .2, .3]


def test_transformation_pipeline_runs_before_scene_binding():
    result = scene_from_dataset({
        "dataset": {"id": "filter", "rows": rows(20)},
        "pipeline": {"operations": [{"type": "filter", "column": "x", "operator": "gte", "value": .5}]},
        "mapping": {"x": "x", "y": "y", "z": "z"},
        "geometry": "point-cloud",
    })
    assert result["scene"]["provenance"]["renderedRowCount"] == 10
    assert result["scene"]["provenance"]["transformationLineage"][0]["type"] == "filter"


def test_large_scene_uses_v0760_deterministic_stride():
    source = rows(6000)
    result = scene_from_dataset({
        "dataset": {"id": "large", "rows": source},
        "mapping": {"x": "x", "y": "y", "z": "z"},
        "geometry": "point-cloud",
        "renderPlan": {"pointBudget": 1000},
    })
    assert result["adaptiveRendering"] is not None
    assert result["adaptiveRendering"]["renderPlan"]["strategy"] == "stride"
    assert result["scene"]["provenance"]["sourceRowCount"] == 6000
    assert result["scene"]["provenance"]["renderedRowCount"] <= 1000


def test_large_scene_rejects_transform_after_sampling():
    with pytest.raises(ScientificSceneError, match="never transform after adaptive reduction"):
        scene_from_dataset({
            "dataset": {"id": "large-transform", "rows": rows(5200)},
            "pipeline": {"operations": [{"type": "filter", "column": "x", "operator": "gte", "value": .2}]},
            "mapping": {"x": "x", "y": "y", "z": "z"},
        })


def test_explicit_mesh_topology_and_bounds():
    scene = normalize_scene({
        "id": "mesh-scene",
        "objects": [{"id": "mesh", "type": "mesh", "vertices": [[0, 0, 0], [1, 0, 0], [0, 1, 1], [1, 1, .5]], "triangles": [[0, 1, 2], [1, 3, 2]]}],
    })
    assert scene["objects"][0]["triangles"] == [[0, 1, 2], [1, 3, 2]]
    assert scene["bounds"]["min"] == [0.0, 0.0, 0.0]
    assert scene["bounds"]["max"] == [1.0, 1.0, 1.0]


def test_mesh_rejects_missing_topology():
    with pytest.raises(ScientificSceneError, match="automatic triangulation is disabled"):
        normalize_scene({"objects": [{"id": "m", "type": "mesh", "vertices": [[0, 0, 0], [1, 0, 0], [0, 1, 0]]}]})


def test_clipping_is_explicit_and_validated():
    scene = normalize_scene({
        "objects": [{"id": "p", "type": "point-cloud", "vertices": [[0, 0, 0], [2, 2, 2]]}],
        "clipping": {"enabled": True, "bounds": {"x": [0, 1], "z": [-1, 1]}},
    })
    assert scene["clipping"] == {"enabled": True, "bounds": {"x": [0.0, 1.0], "z": [-1.0, 1.0]}}


def test_figure_and_workspace_carry_scene():
    payload = {"dataset": {"id": "f", "rows": rows(8)}, "mapping": {"x": "x", "y": "y", "z": "z"}, "geometry": "point-cloud", "figure": {"title": "Figure"}}
    fig = build_figure(payload)["figure"]
    assert fig["recordType"] == "scientific-figure-v0770"
    assert fig["scene"]["renderer"] == "canvas3d"
    ws = build_workspace({**payload, "workspaceId": "ws-3d"})["workspace"]
    assert ws["recordType"] == "figure-workspace-v0770"
    assert ws["scene"]["schema"] == "sc-lab-scientific-scene/0.77.0"


def test_explicit_scene_figure_does_not_require_dataset():
    built = build_figure({"scene": {"id": "explicit", "title": "Explicit scene", "objects": [{"id": "line", "type": "polyline", "vertices": [[0, 0, 0], [1, 1, 1]]}]}})
    assert built["figure"]["graph"]["rendering"]["dataMode"] == "explicit-scene"
    assert built["figure"]["graph"]["renderer"] == "canvas3d"
