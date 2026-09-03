import pytest
from app.spatial_geospatial_raster_v0800 import (
    SpatialVisualizationError,
    bbox_select,
    build_spatial_figure,
    build_workspace,
    health,
    normalize_crs,
    normalize_raster,
    normalize_vector_layer,
    normalize_viewport,
)


def declared_crs():
    return {"id": "EPSG:4326", "name": "WGS 84 declared", "axisOrder": "xy", "units": "degrees", "geographic": True}


def vector_payload():
    return {
        "id": "observations",
        "crs": declared_crs(),
        "features": [
            {"type": "Feature", "id": "station-a", "properties": {"class": "station"}, "geometry": {"type": "Point", "coordinates": [-80, 20]}},
            {"type": "Feature", "id": "transect", "properties": {}, "geometry": {"type": "LineString", "coordinates": [[-70, 0], [0, 10], [70, 5]]}},
            {"type": "Feature", "id": "zone", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-30, -20], [30, -20], [30, 15], [-30, 15], [-30, -20]]]}}],
    }


def raster_payload():
    return {
        "id": "grid",
        "crs": declared_crs(),
        "bounds": [-90, -45, 90, 45],
        "nodata": -9999,
        "values": [[1, 2, -9999], [3, 4, 5]],
    }


def test_health_and_boundaries():
    h = health()
    assert h["status"] == "spatial-geospatial-raster-ready"
    assert h["version"] == "0.80.0"
    assert h["engineVersion"] == "2.7.0"
    assert h["renderer"] == "canvas-spatial"
    assert h["v0790LinkedViewsCompatibility"] is True
    assert h["automaticReprojection"] is False
    assert h["rasterInterpolation"] is False
    assert h["networkBasemaps"] is False


def test_crs_is_declared_not_inferred_or_reprojected():
    c = normalize_crs(declared_crs())
    assert c["id"] == "EPSG:4326"
    assert c["geographic"] is True
    assert c["boundaries"]["automaticCRSInference"] is False
    assert c["boundaries"]["automaticReprojection"] is False


def test_vector_preserves_explicit_geometry_and_source_indexes():
    layer = normalize_vector_layer(vector_payload())
    assert layer["featureCount"] == 3
    assert layer["coordinateCount"] == 9
    assert layer["features"][0]["geometry"]["coordinates"] == [-80.0, 20.0]
    assert layer["features"][2]["sourceIndex"] == 2
    assert layer["bounds"] == [-80.0, -20.0, 70.0, 20.0]
    assert layer["boundaries"]["topologyRepair"] is False


def test_raster_preserves_cells_and_nodata_without_imputation():
    r = normalize_raster(raster_payload())
    assert r["width"] == 3 and r["height"] == 2 and r["cellCount"] == 6
    assert r["values"][0][2] is None
    assert r["statistics"] == {"min": 1.0, "max": 5.0, "validCellCount": 5, "nodataCellCount": 1}
    assert r["cellSize"] == [60.0, 45.0]
    assert r["boundaries"]["rasterInterpolation"] is False
    assert r["boundaries"]["nodataImputation"] is False


def test_flat_raster_requires_explicit_dimensions():
    r = normalize_raster({"crs": declared_crs(), "bounds": [0, 0, 2, 2], "width": 2, "height": 2, "values": [1, 2, 3, 4]})
    assert r["values"] == [[1.0, 2.0], [3.0, 4.0]]
    with pytest.raises(SpatialVisualizationError):
        normalize_raster({"bounds": [0, 0, 2, 2], "width": 3, "height": 2, "values": [1, 2, 3, 4]})


def test_figure_rejects_mixed_crs_instead_of_reprojecting():
    vector = vector_payload()
    raster = raster_payload()
    raster["crs"] = {"id": "EPSG:3857", "units": "m"}
    with pytest.raises(SpatialVisualizationError, match="same declared CRS"):
        build_spatial_figure({"crs": declared_crs(), "layers": [{"kind": "vector", **vector}, {"kind": "raster", **raster}]})


def test_spatial_figure_mixes_vector_and_raster_without_mutating_scientific_values():
    out = build_spatial_figure({"title": "Map", "crs": declared_crs(), "viewport": {"bounds": [-90, -45, 90, 45]}, "layers": [{"kind": "raster", **raster_payload()}, {"kind": "vector", **vector_payload()}]})["figure"]
    assert out["renderer"] == "canvas-spatial"
    assert [x["kind"] for x in out["layers"]] == ["raster", "vector"]
    assert out["layers"][0]["values"][1][2] == 5.0
    assert out["boundaries"]["automaticSpatialJoin"] is False
    assert out["boundaries"]["rasterResampling"] is False


def test_bbox_selection_is_explicit_feature_bounds_intersection():
    r = bbox_select({"layer": vector_payload(), "bounds": [-35, -25, 35, 16]})
    assert r["selectionMode"] == "explicit-bounding-box-intersection"
    assert set(r["featureIds"]) == {"transect", "zone"}
    assert r["sourceIndexes"] == [1, 2]


def test_viewport_requires_explicit_valid_bounds():
    v = normalize_viewport({"bounds": [0, 0, 10, 5], "crs": declared_crs(), "width": 1200, "height": 600})
    assert v["bounds"] == [0.0, 0.0, 10.0, 5.0]
    with pytest.raises(SpatialVisualizationError):
        normalize_viewport({"bounds": [0, 0, 0, 5]})


def test_workspace_preserves_optional_v0790_linked_composition_reference():
    comp = {"schema": "sc-lab-linked-figure-composition/0.79.0", "views": [{"id": "spatial"}]}
    w = build_workspace({"figure": {"crs": declared_crs(), "viewport": {"bounds": [-90, -45, 90, 45]}, "layers": [{"kind": "vector", **vector_payload()}]}, "linkedComposition": comp})["workspace"]
    assert w["schema"] == "sc-lab-figure-workspace/0.80.0"
    assert "canvas-spatial" in w["rendererRegistry"]
    assert w["linkedComposition"] == comp
