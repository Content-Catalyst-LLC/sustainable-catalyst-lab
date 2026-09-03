import math
import pytest
from app.annotation_measurement_markup_v0810 import (
    ScientificMarkupError,
    attach_markup,
    build_workspace,
    compute_measurement,
    health,
    normalize_annotation,
    normalize_markup_layer,
)


def test_health_and_scientific_boundaries():
    h = health()
    assert h["status"] == "annotation-measurement-scientific-markup-ready"
    assert h["version"] == "0.81.0"
    assert h["engineVersion"] == "2.8.0"
    assert h["scientificAnnotation"] is True
    assert h["v0800SpatialCompatibility"] is True
    assert h["annotationIsObservation"] is False
    assert h["automaticGeodesicMeasurement"] is False


def test_annotation_is_explicitly_not_observation():
    a = normalize_annotation({"id": "a", "type": "label", "points": [[2, 3]], "text": "Observed maximum", "units": "s"})
    assert a["scientificRole"] == "annotation"
    assert a["isObservation"] is False
    assert a["isDerivedScientificDatum"] is False
    assert a["points"] == [[2.0, 3.0]]
    assert a["boundaries"]["automaticObservationCreation"] is False


def test_distance_and_polyline_measurements_use_declared_coordinate_units():
    d = compute_measurement({"type": "distance", "points": [[0, 0], [3, 4]], "units": "m", "coordinateSpace": "projected"})
    assert d["value"] == 5.0
    assert d["outputUnits"] == "m"
    assert d["method"] == "euclidean-coordinate-space"
    assert d["isObservation"] is False
    line = compute_measurement({"type": "polyline-length", "points": [[0, 0], [3, 4], [6, 8]], "units": "m", "coordinateSpace": "projected"})
    assert line["value"] == 10.0


def test_angle_measurement():
    m = compute_measurement({"type": "angle", "points": [[1, 0], [0, 0], [0, 1]], "units": "m"})
    assert math.isclose(m["value"], 90.0)
    assert m["outputUnits"] == "degrees"


def test_area_measurement_requires_2d_and_is_explicit_coordinate_space():
    m = compute_measurement({"type": "area", "points": [[0, 0], [4, 0], [4, 3], [0, 3]], "units": "m", "coordinateSpace": "projected"})
    assert m["value"] == 12.0
    assert m["outputUnits"] == "m^2"
    with pytest.raises(ScientificMarkupError, match="2D"):
        compute_measurement({"type": "area", "points": [[0, 0, 0], [1, 0, 0], [1, 1, 0]], "units": "m", "coordinateSpace": "data-3d"})


def test_geographic_distance_refuses_approximation():
    with pytest.raises(ScientificMarkupError, match="geodesy"):
        compute_measurement({"type": "distance", "points": [[-87.6, 41.8], [-74, 40.7]], "units": "degrees", "coordinateSpace": "geographic", "crs": {"id": "EPSG:4326"}})


def test_markup_layer_normalizes_annotations_and_measurements():
    layer = normalize_markup_layer({
        "id": "review",
        "annotations": [{"type": "point", "points": [[0.25, 0.5]], "coordinateSpace": "screen-normalized"}],
        "measurements": [{"type": "distance", "points": [[0, 0], [1, 0]], "units": "cm"}],
    })
    assert layer["annotationCount"] == 1
    assert layer["measurementCount"] == 1
    assert layer["boundaries"]["annotationIsObservation"] is False


def test_attach_markup_preserves_base_figure():
    base = {"schema": "sc-lab-spatial-figure/0.80.0", "renderer": "canvas-spatial", "title": "Base", "fingerprint": "base-fp", "layers": [{"id": "x"}]}
    out = attach_markup({"baseFigure": base, "markupLayers": [{"annotations": [{"type": "label", "points": [[0.5, 0.5]], "coordinateSpace": "screen-normalized", "text": "A"}]}]})["figure"]
    assert out["baseFigureFingerprint"] == "base-fp"
    assert out["baseRenderer"] == "canvas-spatial"
    assert out["baseFigure"] == base
    assert out["baseFigure"] is not base
    assert out["boundaries"]["baseFigureMutation"] is False


def test_workspace_keeps_renderer_and_overlay_registries():
    w = build_workspace({"figure": {"baseFigure": {"renderer": "svg2d", "title": "F"}, "markupLayers": [{"annotations": [{"type": "label", "points": [[0.1, 0.2]], "coordinateSpace": "screen-normalized"}]}]}})["workspace"]
    assert w["schema"] == "sc-lab-figure-workspace/0.81.0"
    assert "canvas-spatial" in w["rendererRegistry"]
    assert w["overlayRegistry"] == ["scientific-markup"]
