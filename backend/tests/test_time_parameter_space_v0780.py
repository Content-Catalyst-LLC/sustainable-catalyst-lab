import pytest

from app.time_parameter_space_v0780 import (
    TimeParameterSpaceError,
    build_figure,
    build_workspace,
    health,
    normalize_axis,
    normalize_projection,
    normalize_state_space,
    policies,
    slice_state_space,
    state_space_from_dataset,
)


def points(n=4):
    return [
        {"x": float(i), "y": float(i * 2), "z": float(i * 3), "w": float(i), "time": i, "parameter": i / 10}
        for i in range(n)
    ]


def dataset(n=12):
    return {
        "id": "v0780-dataset",
        "title": "Observed state rows",
        "rows": [
            {"x": i, "y": i * 2, "z": i * 3, "w": i % 4, "t": i // 3, "p": (i % 4) / 10, "value": i * 0.5}
            for i in range(n)
        ],
        "provenance": {"sourceType": "test"},
    }


def binding():
    return {"x": "x", "y": "y", "z": "z", "w": "w", "time": "t", "parameter": "p", "value": "value"}


def test_health_contract():
    h = health()
    assert h["status"] == "4d-time-parameter-space-ready"
    assert h["version"] == "0.78.0"
    assert h["engineVersion"] == "2.5.0"
    assert h["renderer"] == "canvas4d"
    assert h["syntheticFrames"] is False
    assert h["temporalInterpolation"] is False


def test_policy_boundaries():
    p = policies()
    assert p["capabilities"]["timeStatePlayback"] is True
    assert p["capabilities"]["parameterSweep"] is True
    assert p["boundaries"]["parameterInterpolation"] is False
    assert p["boundaries"]["forecasting"] is False


def test_time_axis_timestamp_requires_timezone():
    with pytest.raises(TimeParameterSpaceError):
        normalize_axis({"kind": "time", "scale": "timestamp", "values": ["2026-09-03T12:00:00"]})
    axis = normalize_axis({"kind": "time", "scale": "timestamp", "values": ["2026-09-03T12:00:00Z"]})
    assert axis["values"][0].endswith("Z")


def test_projection_preserves_coordinates_and_normalizes_rotations():
    p = normalize_projection({"rotations": {"xw": 45, "yw": -30, "zw": 10}, "hyperslice": {"enabled": True, "center": 2, "tolerance": 0.1}})
    assert p["rotations"] == {"xw": 45.0, "yw": -30.0, "zw": 10.0}
    assert p["preserveOriginalCoordinates"] is True
    assert p["hyperslice"]["enabled"] is True


def test_4d_points_are_observed_only():
    state = normalize_state_space({"mode": "4d-points", "points": points(), "projection": {"rotations": {"xw": 25}}})
    assert state["pointCount"] == 4
    assert state["frameCount"] == 0
    assert state["boundaries"]["surfaceInterpolation"] is False
    assert state["boundaries"]["syntheticFrames"] is False


def test_time_sequence_builds_discrete_observed_frames():
    pts = points(6)
    for i, p in enumerate(pts):
        p["time"] = i // 2
    state = normalize_state_space({"mode": "time-sequence", "axis": {"kind": "time", "scale": "index"}, "points": pts})
    assert state["frameCount"] == 3
    assert [f["pointCount"] for f in state["frames"]] == [2, 2, 2]
    assert state["playback"]["interpolate"] is False


def test_parameter_sweep_builds_observed_states():
    pts = points(6)
    for i, p in enumerate(pts):
        p["parameter"] = [0.1, 0.1, 0.2, 0.2, 0.5, 0.5][i]
    state = normalize_state_space({"mode": "parameter-sweep", "axis": {"kind": "parameter", "scale": "numeric"}, "points": pts})
    assert state["frameCount"] == 3
    assert [f["value"] for f in state["frames"]] == [0.1, 0.2, 0.5]


def test_dataset_binding_preserves_source_fingerprint():
    result = state_space_from_dataset({"dataset": dataset(), "binding": binding(), "mode": "time-sequence", "axis": {"kind": "time", "scale": "index"}})
    state = result["stateSpace"]
    assert state["source"]["sourceRows"] == 12
    assert state["source"]["renderedRows"] == 12
    assert state["source"]["representation"] == "full"
    assert state["source"]["authoritativeDatasetFingerprint"]
    assert state["source"]["transformAfterSampling"] is False


def test_large_dataset_uses_deterministic_stride_representation():
    ds = dataset(5200)
    result = state_space_from_dataset({"dataset": ds, "binding": binding(), "mode": "4d-points", "renderPointBudget": 1000})
    state = result["stateSpace"]
    assert state["source"]["sourceRows"] == 5200
    assert state["source"]["renderedRows"] <= 1000
    assert state["source"]["representation"] == "adaptive-stride"
    assert state["source"]["strategy"] == "stride"


def test_time_slice_selects_exact_observed_frame_only():
    pts = points(6)
    for i, p in enumerate(pts):
        p["time"] = i // 2
    state = normalize_state_space({"mode": "time-sequence", "axis": {"kind": "time", "scale": "index"}, "points": pts})
    sliced = slice_state_space({"stateSpace": state, "selector": {"frameIndex": 1}})
    assert sliced["pointCount"] == 2
    assert sliced["interpolated"] is False
    assert sliced["forecast"] is False


def test_parameter_slice_rejects_unobserved_value():
    pts = points(3)
    for i, p in enumerate(pts):
        p["parameter"] = i
    state = normalize_state_space({"mode": "parameter-sweep", "axis": {"kind": "parameter", "scale": "numeric"}, "points": pts})
    with pytest.raises(TimeParameterSpaceError):
        slice_state_space({"stateSpace": state, "selector": {"value": 99}})


def test_hyperslice_is_explicit_tolerance_filter():
    state = normalize_state_space({"mode": "4d-points", "points": points(5)})
    sliced = slice_state_space({"stateSpace": state, "selector": {"w": 2, "tolerance": 0.01}})
    assert sliced["pointCount"] == 1
    assert sliced["points"][0]["w"] == 2.0


def test_figure_carries_state_provenance():
    result = build_figure({"dataset": dataset(), "binding": binding(), "mode": "parameter-sweep", "axis": {"kind": "parameter", "scale": "numeric"}})
    figure = result["figure"]
    assert figure["schema"] == "sc-lab-scientific-figure/0.78.0"
    assert figure["renderer"] == "canvas4d"
    assert figure["provenance"]["stateSpaceFingerprint"]
    assert figure["provenance"]["authoritativeDatasetFingerprint"]


def test_workspace_exposes_mode_appropriate_controls():
    result = build_workspace({"dataset": dataset(), "binding": binding(), "mode": "time-sequence", "axis": {"kind": "time", "scale": "index"}})
    controls = result["workspace"]["controls"]
    assert controls["timeScrubber"] is True
    assert controls["parameterScrubber"] is False
    assert controls["hyperslice"] is True
    assert controls["discretePlaybackOnly"] is True
