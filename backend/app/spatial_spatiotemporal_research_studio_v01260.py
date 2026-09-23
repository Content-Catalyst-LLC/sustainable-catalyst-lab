from __future__ import annotations

import copy
import json
import math
from collections import defaultdict
from hashlib import sha256
from typing import Any

import numpy as np

from .spatial_geospatial_raster_v0800 import normalize_crs, normalize_raster, SpatialVisualizationError

VERSION = "0.126.0"
ENGINE_VERSION = "7.0.0"
SCHEMA = "sc-lab-spatial-spatiotemporal-research-studio/0.126.0"
SNAPSHOT_SCHEMA = "sc-lab-spatial-spatiotemporal-research-snapshot/0.126.0"
MAX_ROWS = 50_000
MAX_LOCATIONS = 10_000
MAX_NEIGHBORS = 64
MAX_RASTER_CELLS = 1_048_576
MAX_TIME_BINS = 512

METHOD_FAMILIES = {
    "spatial-weights",
    "global-morans-i",
    "local-morans-i",
    "getis-ord-gi-star",
    "nearest-neighbor",
    "spatial-lag-descriptive",
    "raster-zonal-statistics",
    "raster-change",
    "spatiotemporal-cube",
    "spatiotemporal-change-profile",
    "space-time-autocorrelation",
    "trajectory-summary",
}

FIGURE_FAMILIES = {
    "choropleth",
    "proportional-symbol",
    "spatial-lag-scatter",
    "moran-scatter",
    "local-association-map",
    "hotspot-map",
    "nearest-neighbor-map",
    "raster-grid",
    "raster-difference",
    "zonal-summary",
    "space-time-cube",
    "temporal-small-multiples",
    "trajectory-map",
    "hotspot-persistence-map",
}


class SpatialResearchStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise SpatialResearchStudioError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise SpatialResearchStudioError(f"{label} must be finite.")
    return out


def _string(value: Any, label: str, limit: int = 180) -> str:
    out = str(value or "").strip()
    if not out:
        raise SpatialResearchStudioError(f"{label} is required.")
    return out[:limit]


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise SpatialResearchStudioError("rows must be a non-empty array of row objects.")
    if len(rows) > MAX_ROWS:
        raise SpatialResearchStudioError(f"rows cannot exceed {MAX_ROWS} records.", 413)
    if not all(isinstance(row, dict) for row in rows):
        raise SpatialResearchStudioError("Each row must be an object.")
    return copy.deepcopy(rows)


def _column(rows: list[dict[str, Any]], name: str) -> np.ndarray:
    values = []
    for i, row in enumerate(rows):
        if name not in row:
            raise SpatialResearchStudioError(f"Missing column {name!r} at row {i}.")
        values.append(_finite(row[name], f"{name}[{i}]"))
    return np.asarray(values, dtype=float)


def _xy_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str, str, str]:
    rows = _rows(payload)
    x_name = _string(payload.get("x") or "x", "x")
    y_name = _string(payload.get("y") or "y", "y")
    id_name = str(payload.get("id_column") or "id")
    _column(rows, x_name)
    _column(rows, y_name)
    ids = [str(row.get(id_name, i)) for i, row in enumerate(rows)]
    if len(set(ids)) != len(ids):
        raise SpatialResearchStudioError("location identifiers must be unique for spatial-weight construction.")
    if len(rows) > MAX_LOCATIONS:
        raise SpatialResearchStudioError(f"spatial methods support at most {MAX_LOCATIONS} unique locations.", 413)
    return rows, x_name, y_name, id_name


def _crs(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return normalize_crs(payload.get("crs") or {})
    except SpatialVisualizationError as exc:
        raise SpatialResearchStudioError(exc.detail, exc.status_code) from exc


def schema_info() -> dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "snapshot_schema": SNAPSHOT_SCHEMA,
        "limits": {
            "rows": MAX_ROWS,
            "locations": MAX_LOCATIONS,
            "neighbors": MAX_NEIGHBORS,
            "raster_cells": MAX_RASTER_CELLS,
            "time_bins": MAX_TIME_BINS,
        },
    }


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "method_families": sorted(METHOD_FAMILIES),
        "figure_families": sorted(FIGURE_FAMILIES),
        "retained_spatial_engine": "spatial-geospatial-raster-v0.80.0",
        "automatic_reprojection": False,
        "automatic_spatial_join": False,
        "automatic_causal_interpretation": False,
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "spatial-spatiotemporal-research-studio-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "vector_research": True,
        "raster_research": True,
        "spatial_statistics": True,
        "spatiotemporal_analysis": True,
        "trajectory_analysis": True,
        "spatial_visualization_planning": True,
        "explicit_crs_required": True,
        "explicit_weights_required_or_constructed_from_declared_rule": True,
        "automatic_reprojection": False,
        "automatic_bandwidth_selection": False,
        "automatic_spatial_join": False,
        "automatic_significance_labels": False,
        "automatic_causal_interpretation": False,
        "automatic_scientific_validity_certification": False,
        "automatic_core_submission": False,
        "determine_truth": False,
    }


def health() -> dict[str, Any]:
    return {
        **manifest(),
        "schema": SCHEMA,
        "method_family_count": len(METHOD_FAMILIES),
        "figure_family_count": len(FIGURE_FAMILIES),
    }


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SpatialResearchStudioError("study payload must be an object.")
    rows = _rows(payload)
    crs = _crs(payload)
    x_name = _string(payload.get("x") or "x", "x")
    y_name = _string(payload.get("y") or "y", "y")
    _column(rows, x_name)
    _column(rows, y_name)
    time_name = str(payload.get("time") or "").strip() or None
    value_name = str(payload.get("value") or "").strip() or None
    if time_name:
        _column(rows, time_name)
    if value_name:
        _column(rows, value_name)
    study = {
        "schema": SCHEMA,
        "version": VERSION,
        "id": str(payload.get("id") or "spatial-study")[:180],
        "title": str(payload.get("title") or "Spatial and spatiotemporal research study")[:400],
        "rows": rows,
        "row_count": len(rows),
        "x": x_name,
        "y": y_name,
        "time": time_name,
        "value": value_name,
        "crs": crs,
        "coordinate_units": crs.get("units"),
        "data_semantics": str(payload.get("data_semantics") or "researcher-provided-spatial-data")[:160],
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
        "boundaries": {
            "automatic_reprojection": False,
            "automatic_spatial_join": False,
            "automatic_topology_repair": False,
            "automatic_causal_interpretation": False,
        },
    }
    study["study_hash"] = _hash({k: v for k, v in study.items() if k != "study_hash"})
    return {"ok": True, "version": VERSION, "study": study}


def crs_audit(payload: dict[str, Any]) -> dict[str, Any]:
    crs = _crs(payload)
    warnings = []
    if crs.get("id") == "LOCAL:UNSPECIFIED":
        warnings.append("CRS is locally declared but unspecified; physical-distance interpretations require a researcher-declared coordinate reference and units.")
    if crs.get("geographic"):
        warnings.append("Geographic coordinates are angular. Planar distance calculations remain in declared coordinate units and are not silently converted to geodesic distance.")
    if str(crs.get("units") or "unknown") == "unknown":
        warnings.append("Coordinate units are unknown; distance-based outputs must not be interpreted as physical distances without additional metadata.")
    return {
        "ok": True,
        "schema": f"{SCHEMA}/crs-audit",
        "version": VERSION,
        "crs": crs,
        "warnings": warnings,
        "automatic_reprojection": False,
        "physical_distance_certified": False,
    }


def build_spatial_weights(payload: dict[str, Any]) -> dict[str, Any]:
    rows, x_name, y_name, id_name = _xy_rows(payload)
    ids = [str(row.get(id_name, i)) for i, row in enumerate(rows)]
    x = _column(rows, x_name)
    y = _column(rows, y_name)
    coords = np.column_stack([x, y])
    n = len(rows)
    method = str(payload.get("method") or "knn").lower()
    row_standardize = bool(payload.get("row_standardize", True))
    symmetric = bool(payload.get("symmetric", True))
    W = np.zeros((n, n), dtype=float)
    if method == "knn":
        k = int(payload.get("k") or min(4, max(1, n - 1)))
        if not 1 <= k <= min(MAX_NEIGHBORS, n - 1):
            raise SpatialResearchStudioError(f"k must be between 1 and {min(MAX_NEIGHBORS, n-1)}.")
        for i in range(n):
            d = np.sqrt(np.sum((coords - coords[i]) ** 2, axis=1))
            order = [int(j) for j in np.argsort(d, kind="stable") if int(j) != i][:k]
            for j in order:
                W[i, j] = 1.0
    elif method == "distance-band":
        threshold = _finite(payload.get("threshold"), "threshold")
        if threshold <= 0:
            raise SpatialResearchStudioError("distance-band threshold must be positive.")
        for i in range(n):
            d = np.sqrt(np.sum((coords - coords[i]) ** 2, axis=1))
            W[i, (d > 0) & (d <= threshold)] = 1.0
        k = None
    else:
        raise SpatialResearchStudioError("weights method must be knn or distance-band.")
    if symmetric:
        W = np.maximum(W, W.T)
    isolates = np.where(W.sum(axis=1) == 0)[0]
    if len(isolates):
        raise SpatialResearchStudioError(f"Spatial weights contain {len(isolates)} isolate(s); revise the declared neighbor rule.")
    raw_W = W.copy()
    if row_standardize:
        W = W / W.sum(axis=1, keepdims=True)
    neighbors = []
    for i in range(n):
        entries = []
        for j in np.where(raw_W[i] > 0)[0]:
            entries.append({"id": ids[int(j)], "weight": float(W[i, j]), "distance": float(np.linalg.norm(coords[i] - coords[j]))})
        neighbors.append({"id": ids[i], "neighbors": entries})
    spec = {
        "schema": f"{SCHEMA}/weights",
        "version": VERSION,
        "method": method,
        "k": k,
        "threshold": payload.get("threshold") if method == "distance-band" else None,
        "symmetric": symmetric,
        "row_standardized": row_standardize,
        "ids": ids,
        "matrix": W.tolist(),
        "neighbors": neighbors,
        "coordinate_units": _crs(payload).get("units"),
        "automatic_bandwidth_selection": False,
    }
    spec["weights_hash"] = _hash({k: v for k, v in spec.items() if k != "weights_hash"})
    return {"ok": True, "version": VERSION, "weights": spec}


def _weights_and_values(payload: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, Any]]:
    value_name = _string(payload.get("value"), "value")
    rows, _, _, id_name = _xy_rows(payload)
    values = _column(rows, value_name)
    weights = payload.get("weights")
    if isinstance(weights, dict) and isinstance(weights.get("matrix"), list):
        spec = copy.deepcopy(weights)
    else:
        spec = build_spatial_weights(payload)["weights"]
    W = np.asarray(spec.get("matrix"), dtype=float)
    if W.shape != (len(values), len(values)):
        raise SpatialResearchStudioError("weights matrix dimensions must equal the number of rows.")
    if not np.isfinite(W).all() or (W < 0).any():
        raise SpatialResearchStudioError("weights matrix must contain finite non-negative values.")
    ids = [str(row.get(id_name, i)) for i, row in enumerate(rows)]
    return values, W, ids, spec


def global_morans_i(payload: dict[str, Any]) -> dict[str, Any]:
    values, W, ids, spec = _weights_and_values(payload)
    n = len(values)
    z = values - float(values.mean())
    denom = float(np.dot(z, z))
    s0 = float(W.sum())
    if denom <= 0 or s0 <= 0:
        raise SpatialResearchStudioError("Moran's I requires non-constant values and positive total spatial weight.")
    I = float((n / s0) * (z @ W @ z) / denom)
    expected = -1.0 / (n - 1) if n > 1 else None
    return {
        "ok": True,
        "schema": f"{SCHEMA}/global-morans-i",
        "version": VERSION,
        "moran_i": I,
        "expected_under_randomization": expected,
        "n": n,
        "weights_hash": spec.get("weights_hash"),
        "ids": ids,
        "permutation_inference_performed": False,
        "significance_certified": False,
        "causal_interpretation": False,
    }


def local_morans_i(payload: dict[str, Any]) -> dict[str, Any]:
    values, W, ids, spec = _weights_and_values(payload)
    z = values - float(values.mean())
    m2 = float(np.mean(z ** 2))
    if m2 <= 0:
        raise SpatialResearchStudioError("Local Moran's I requires non-constant values.")
    lag = W @ z
    local = z * lag / m2
    rows = []
    for i, value in enumerate(local):
        zi = z[i]
        li = lag[i]
        quadrant = "HH" if zi >= 0 and li >= 0 else "LL" if zi < 0 and li < 0 else "HL" if zi >= 0 else "LH"
        rows.append({"id": ids[i], "local_moran_i": float(value), "centered_value": float(zi), "spatial_lag": float(li), "quadrant": quadrant})
    return {
        "ok": True,
        "schema": f"{SCHEMA}/local-morans-i",
        "version": VERSION,
        "locations": rows,
        "weights_hash": spec.get("weights_hash"),
        "permutation_inference_performed": False,
        "significance_labels_assigned": False,
    }


def getis_ord_gi_star(payload: dict[str, Any]) -> dict[str, Any]:
    values, W, ids, spec = _weights_and_values(payload)
    include_self = bool(payload.get("include_self", True))
    WW = W.copy()
    if include_self:
        np.fill_diagonal(WW, np.maximum(np.diag(WW), 1.0))
    n = len(values)
    mean = float(values.mean())
    sd = float(values.std(ddof=0))
    if sd <= 0 or n < 3:
        raise SpatialResearchStudioError("Getis-Ord Gi* requires at least three rows with non-constant values.")
    rows = []
    for i in range(n):
        wi = WW[i]
        sw = float(wi.sum())
        sw2 = float(np.dot(wi, wi))
        denom_term = max(0.0, (n * sw2 - sw * sw) / (n - 1))
        denom = sd * math.sqrt(denom_term)
        score = None if denom <= 0 else float((np.dot(wi, values) - mean * sw) / denom)
        rows.append({"id": ids[i], "gi_star_z": score})
    return {
        "ok": True,
        "schema": f"{SCHEMA}/getis-ord-gi-star",
        "version": VERSION,
        "locations": rows,
        "weights_hash": spec.get("weights_hash"),
        "include_self": include_self,
        "significance_labels_assigned": False,
        "multiple_testing_adjustment_performed": False,
    }


def nearest_neighbor_report(payload: dict[str, Any]) -> dict[str, Any]:
    rows, x_name, y_name, id_name = _xy_rows(payload)
    ids = [str(row.get(id_name, i)) for i, row in enumerate(rows)]
    coords = np.column_stack([_column(rows, x_name), _column(rows, y_name)])
    nearest = []
    for i in range(len(coords)):
        d = np.sqrt(np.sum((coords - coords[i]) ** 2, axis=1))
        d[i] = np.inf
        j = int(np.argmin(d))
        nearest.append({"id": ids[i], "neighbor_id": ids[j], "distance": float(d[j])})
    distances = np.asarray([r["distance"] for r in nearest], dtype=float)
    return {
        "ok": True,
        "schema": f"{SCHEMA}/nearest-neighbor",
        "version": VERSION,
        "mean_nearest_distance": float(distances.mean()),
        "median_nearest_distance": float(np.median(distances)),
        "nearest": nearest,
        "coordinate_units": _crs(payload).get("units"),
        "random_spatial_process_comparison_performed": False,
        "physical_distance_certified": False,
    }


def spatial_lag_estimate(payload: dict[str, Any]) -> dict[str, Any]:
    values, W, ids, spec = _weights_and_values(payload)
    rows = _rows(payload)
    covariates = [str(x) for x in (payload.get("covariates") or [])]
    X = [np.ones(len(rows), dtype=float), W @ values]
    names = ["intercept", "spatial_lag_y"]
    for name in covariates:
        X.append(_column(rows, name)); names.append(name)
    X = np.column_stack(X)
    if X.shape[0] <= X.shape[1]:
        raise SpatialResearchStudioError("Not enough rows for the declared spatial-lag descriptive regression.")
    beta = np.linalg.pinv(X.T @ X) @ (X.T @ values)
    fitted = X @ beta
    resid = values - fitted
    rows_out = [{"term": names[i], "estimate": float(beta[i])} for i in range(len(names))]
    return {
        "ok": True,
        "schema": f"{SCHEMA}/spatial-lag-descriptive",
        "version": VERSION,
        "coefficients": rows_out,
        "rmse": float(np.sqrt(np.mean(resid ** 2))),
        "weights_hash": spec.get("weights_hash"),
        "ids": ids,
        "model_type": "descriptive-spatial-lag-regression",
        "causal_interpretation": False,
        "simultaneous_spatial_model_certified": False,
    }


def raster_zonal_stats(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        raster = normalize_raster(payload.get("raster") or {})
    except SpatialVisualizationError as exc:
        raise SpatialResearchStudioError(exc.detail, exc.status_code) from exc
    zones = payload.get("zones")
    if not isinstance(zones, list) or len(zones) != raster["height"] or any(not isinstance(r, list) or len(r) != raster["width"] for r in zones):
        raise SpatialResearchStudioError("zones must match the raster grid dimensions exactly.")
    by_zone: dict[str, list[float]] = defaultdict(list)
    for yy in range(raster["height"]):
        for xx in range(raster["width"]):
            value = raster["values"][yy][xx]
            zone = zones[yy][xx]
            if value is None or zone is None:
                continue
            by_zone[str(zone)].append(float(value))
    summaries = []
    for zone in sorted(by_zone):
        arr = np.asarray(by_zone[zone], dtype=float)
        summaries.append({"zone": zone, "count": int(len(arr)), "mean": float(arr.mean()), "sum": float(arr.sum()), "min": float(arr.min()), "max": float(arr.max()), "std": float(arr.std(ddof=1)) if len(arr) > 1 else None})
    return {
        "ok": True,
        "schema": f"{SCHEMA}/raster-zonal-statistics",
        "version": VERSION,
        "raster_fingerprint": raster.get("fingerprint"),
        "zones": summaries,
        "automatic_zone_inference": False,
        "automatic_resampling": False,
    }


def raster_change_summary(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        before = normalize_raster(payload.get("before") or {})
        after = normalize_raster(payload.get("after") or {})
    except SpatialVisualizationError as exc:
        raise SpatialResearchStudioError(exc.detail, exc.status_code) from exc
    keys = ("width", "height", "bounds")
    if any(before[k] != after[k] for k in keys) or before["crs"]["id"] != after["crs"]["id"]:
        raise SpatialResearchStudioError("before and after rasters must already share dimensions, bounds, and CRS; automatic resampling/reprojection is disabled.")
    deltas = []
    grid = []
    for y in range(before["height"]):
        row = []
        for x in range(before["width"]):
            a = before["values"][y][x]; b = after["values"][y][x]
            if a is None or b is None:
                row.append(None)
            else:
                d = float(b - a); row.append(d); deltas.append(d)
        grid.append(row)
    arr = np.asarray(deltas, dtype=float) if deltas else np.asarray([], dtype=float)
    return {
        "ok": True,
        "schema": f"{SCHEMA}/raster-change",
        "version": VERSION,
        "change_grid": grid,
        "summary": {"valid_change_cells": int(len(arr)), "mean_change": float(arr.mean()) if len(arr) else None, "min_change": float(arr.min()) if len(arr) else None, "max_change": float(arr.max()) if len(arr) else None},
        "automatic_reprojection": False,
        "automatic_resampling": False,
        "change_causal_attribution": False,
    }


def spatial_join_plan(payload: dict[str, Any]) -> dict[str, Any]:
    left_ref = _string(payload.get("left_ref"), "left_ref")
    right_ref = _string(payload.get("right_ref"), "right_ref")
    predicate = str(payload.get("predicate") or "intersects")
    if predicate not in {"intersects", "contains", "within", "nearest", "bbox-intersects"}:
        raise SpatialResearchStudioError("Unsupported declared spatial-join predicate.")
    return {
        "ok": True,
        "schema": f"{SCHEMA}/spatial-join-plan",
        "version": VERSION,
        "left_ref": left_ref,
        "right_ref": right_ref,
        "predicate": predicate,
        "maximum_distance": payload.get("maximum_distance"),
        "automatic_execution": False,
        "automatic_reprojection": False,
        "automatic_topology_repair": False,
        "relationship_inference": False,
    }


def build_spatiotemporal_cube(payload: dict[str, Any]) -> dict[str, Any]:
    rows = _rows(payload)
    x_name = _string(payload.get("x") or "x", "x")
    y_name = _string(payload.get("y") or "y", "y")
    t_name = _string(payload.get("time") or "time", "time")
    v_name = _string(payload.get("value"), "value")
    x = _column(rows, x_name); y = _column(rows, y_name); t = _column(rows, t_name); v = _column(rows, v_name)
    x_edges = np.asarray(payload.get("x_edges") or [], dtype=float)
    y_edges = np.asarray(payload.get("y_edges") or [], dtype=float)
    t_edges = np.asarray(payload.get("time_edges") or [], dtype=float)
    for name, edges in (("x_edges", x_edges), ("y_edges", y_edges), ("time_edges", t_edges)):
        if len(edges) < 2 or len(edges) - 1 > MAX_TIME_BINS or not np.all(np.diff(edges) > 0):
            raise SpatialResearchStudioError(f"{name} must be a strictly increasing array with at least two edges and at most {MAX_TIME_BINS+1} values.")
    stat = str(payload.get("statistic") or "mean")
    if stat not in {"mean", "sum", "count"}:
        raise SpatialResearchStudioError("statistic must be mean, sum, or count.")
    xi = np.digitize(x, x_edges) - 1; yi = np.digitize(y, y_edges) - 1; ti = np.digitize(t, t_edges) - 1
    buckets: dict[tuple[int, int, int], list[float]] = defaultdict(list)
    for i in range(len(rows)):
        if 0 <= xi[i] < len(x_edges)-1 and 0 <= yi[i] < len(y_edges)-1 and 0 <= ti[i] < len(t_edges)-1:
            buckets[(int(ti[i]), int(yi[i]), int(xi[i]))].append(float(v[i]))
    cells = []
    for key in sorted(buckets):
        vals = np.asarray(buckets[key], dtype=float)
        value = float(vals.mean()) if stat == "mean" else float(vals.sum()) if stat == "sum" else int(len(vals))
        cells.append({"time_bin": key[0], "y_bin": key[1], "x_bin": key[2], "value": value, "count": int(len(vals))})
    cube = {"schema": f"{SCHEMA}/space-time-cube", "version": VERSION, "statistic": stat, "x_edges": x_edges.tolist(), "y_edges": y_edges.tolist(), "time_edges": t_edges.tolist(), "cells": cells, "source_row_count": len(rows), "included_row_count": int(sum(c["count"] for c in cells)), "automatic_binning": False}
    cube["cube_hash"] = _hash({k: v for k, v in cube.items() if k != "cube_hash"})
    return {"ok": True, "version": VERSION, "cube": cube}


def spatiotemporal_change_profile(payload: dict[str, Any]) -> dict[str, Any]:
    rows = _rows(payload)
    id_name = _string(payload.get("location_id") or "location_id", "location_id")
    time_name = _string(payload.get("time") or "time", "time")
    value_name = _string(payload.get("value"), "value")
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for i, row in enumerate(rows):
        if id_name not in row:
            raise SpatialResearchStudioError(f"Missing {id_name!r} at row {i}.")
        grouped[str(row[id_name])].append((_finite(row.get(time_name), f"{time_name}[{i}]"), _finite(row.get(value_name), f"{value_name}[{i}]")))
    profiles = []
    for loc in sorted(grouped):
        pts = sorted(grouped[loc])
        tt = np.asarray([p[0] for p in pts], dtype=float); vv = np.asarray([p[1] for p in pts], dtype=float)
        slope = None
        if len(pts) >= 2 and np.var(tt) > 0:
            slope = float(np.cov(tt, vv, ddof=0)[0, 1] / np.var(tt))
        profiles.append({"location_id": loc, "n": len(pts), "first_time": float(tt[0]), "last_time": float(tt[-1]), "first_value": float(vv[0]), "last_value": float(vv[-1]), "absolute_change": float(vv[-1]-vv[0]), "linear_slope": slope})
    return {"ok": True, "schema": f"{SCHEMA}/spatiotemporal-change-profile", "version": VERSION, "locations": profiles, "automatic_change_point_detection": False, "causal_attribution": False}


def space_time_autocorrelation(payload: dict[str, Any]) -> dict[str, Any]:
    rows = _rows(payload)
    time_name = _string(payload.get("time") or "time", "time")
    value_name = _string(payload.get("value"), "value")
    id_name = _string(payload.get("id_column") or "id", "id_column")
    groups: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for i, row in enumerate(rows):
        groups[_finite(row.get(time_name), f"{time_name}[{i}]")].append(row)
    slices = []
    for time_value in sorted(groups):
        sub = groups[time_value]
        if len(sub) < 3:
            slices.append({"time": time_value, "moran_i": None, "reason": "fewer-than-three-locations"}); continue
        sub_payload = {**payload, "rows": sub, "value": value_name, "id_column": id_name}
        try:
            result = global_morans_i(sub_payload)
            slices.append({"time": time_value, "moran_i": result["moran_i"], "n": result["n"]})
        except SpatialResearchStudioError as exc:
            slices.append({"time": time_value, "moran_i": None, "reason": exc.detail})
    return {"ok": True, "schema": f"{SCHEMA}/space-time-autocorrelation", "version": VERSION, "time_slices": slices, "temporal_model_fitted": False, "significance_certified": False}


def trajectory_report(payload: dict[str, Any]) -> dict[str, Any]:
    rows = _rows(payload)
    id_name = _string(payload.get("entity_id") or "entity_id", "entity_id")
    time_name = _string(payload.get("time") or "time", "time")
    x_name = _string(payload.get("x") or "x", "x")
    y_name = _string(payload.get("y") or "y", "y")
    grouped: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    for i, row in enumerate(rows):
        if id_name not in row:
            raise SpatialResearchStudioError(f"Missing {id_name!r} at row {i}.")
        grouped[str(row[id_name])].append((_finite(row.get(time_name), f"{time_name}[{i}]"), _finite(row.get(x_name), f"{x_name}[{i}]"), _finite(row.get(y_name), f"{y_name}[{i}]")))
    tracks = []
    for entity in sorted(grouped):
        pts = sorted(grouped[entity])
        total = 0.0
        steps = []
        for a, b in zip(pts, pts[1:]):
            dist = math.hypot(b[1]-a[1], b[2]-a[2]); dt = b[0]-a[0]
            total += dist
            steps.append({"from_time": a[0], "to_time": b[0], "distance": dist, "delta_time": dt, "speed_in_coordinate_units_per_time": None if dt == 0 else dist/dt})
        displacement = 0.0 if len(pts) < 2 else math.hypot(pts[-1][1]-pts[0][1], pts[-1][2]-pts[0][2])
        tracks.append({"entity_id": entity, "point_count": len(pts), "total_path_distance": total, "net_displacement": displacement, "steps": steps})
    return {"ok": True, "schema": f"{SCHEMA}/trajectory-report", "version": VERSION, "trajectories": tracks, "coordinate_units": _crs(payload).get("units"), "geodesic_distance_computed": False, "movement_cause_inferred": False}


def hotspot_persistence(payload: dict[str, Any]) -> dict[str, Any]:
    rows = _rows(payload)
    id_name = _string(payload.get("location_id") or "location_id", "location_id")
    time_name = _string(payload.get("time") or "time", "time")
    score_name = _string(payload.get("score") or "score", "score")
    threshold = _finite(payload.get("threshold"), "threshold")
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for i, row in enumerate(rows):
        if id_name not in row:
            raise SpatialResearchStudioError(f"Missing {id_name!r} at row {i}.")
        grouped[str(row[id_name])].append((_finite(row.get(time_name), f"{time_name}[{i}]"), _finite(row.get(score_name), f"{score_name}[{i}]")))
    out = []
    for loc in sorted(grouped):
        pts = sorted(grouped[loc]); flags = [score >= threshold for _, score in pts]
        longest = current = 0
        for flag in flags:
            current = current + 1 if flag else 0; longest = max(longest, current)
        out.append({"location_id": loc, "observations": len(pts), "threshold_exceedances": int(sum(flags)), "exceedance_fraction": float(np.mean(flags)), "longest_consecutive_run": longest})
    return {"ok": True, "schema": f"{SCHEMA}/hotspot-persistence", "version": VERSION, "threshold": threshold, "locations": out, "threshold_is_researcher_declared": True, "statistical_significance_inferred": False}


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figures = [{"figure_type": f, "renderer_family": "spatial-2d-or-3d", "publication_profile": str(payload.get("publication_profile") or "research")[:80]} for f in sorted(FIGURE_FAMILIES)]
    return {"ok": True, "schema": f"{SCHEMA}/visualization-plan", "version": VERSION, "figures": figures, "figure_count": len(figures), "automatic_claim_generation": False, "automatic_spatial_significance_labels": False}


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    study_ref = str(payload.get("study_ref") or payload.get("study_id") or "spatial-study")[:180]
    studio = {
        "schema": f"{SCHEMA}/studio",
        "version": VERSION,
        "studio_id": str(payload.get("studio_id") or f"spatial-studio:{study_ref}")[:240],
        "study_ref": study_ref,
        "methods": copy.deepcopy(payload.get("methods") or []),
        "weights_refs": copy.deepcopy(payload.get("weights_refs") or []),
        "raster_refs": copy.deepcopy(payload.get("raster_refs") or []),
        "figure_refs": copy.deepcopy(payload.get("figure_refs") or []),
        "time_semantics": copy.deepcopy(payload.get("time_semantics") or {}),
        "crs_ref": payload.get("crs_ref"),
        "automatic_analysis_execution": False,
        "automatic_causal_interpretation": False,
    }
    studio["studio_hash"] = _hash({k: v for k, v in studio.items() if k != "studio_hash"})
    return {"ok": True, "version": VERSION, "studio": studio}


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    studio = copy.deepcopy(payload.get("studio") or payload)
    snap = {"schema": SNAPSHOT_SCHEMA, "version": VERSION, "studio": studio, "source_refs": copy.deepcopy(payload.get("source_refs") or []), "runtime_ref": payload.get("runtime_ref"), "automatic_persistence": False}
    snap["snapshot_hash"] = _hash({k: v for k, v in snap.items() if k != "snapshot_hash"})
    return {"ok": True, "version": VERSION, **snap}


def build_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "schema": f"{SCHEMA}/reproduction-plan", "version": VERSION, "snapshot_ref": payload.get("snapshot_ref"), "required_inputs": copy.deepcopy(payload.get("required_inputs") or ["source data", "declared CRS", "weights rule or weights matrix", "time semantics", "analysis parameters"]), "automatic_execution": False, "automatic_data_retrieval": False}


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "schema": f"{SCHEMA}/export-plan", "version": VERSION, "formats": copy.deepcopy(payload.get("formats") or ["geojson", "csv", "svg", "png", "pdf", "research-package"]), "include_crs": True, "include_weights_metadata": True, "include_provenance": True, "include_interpretation_boundaries": True, "automatic_publication": False}


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    session_id = _string(payload.get("session_id"), "session_id")
    analysis_id = _string(payload.get("analysis_id"), "analysis_id")
    return {"ok": True, "schema": "sc.research.object-plan.v1", "version": VERSION, "session_id": session_id, "analysis_id": analysis_id, "object_type": "spatial-spatiotemporal-analysis", "source_refs": copy.deepcopy(payload.get("source_refs") or []), "visual_refs": copy.deepcopy(payload.get("visual_refs") or []), "execution_refs": copy.deepcopy(payload.get("execution_refs") or []), "automatic_core_submission": False}


def build_execution_lineage_plan(payload: dict[str, Any]) -> dict[str, Any]:
    session_id = _string(payload.get("session_id"), "session_id")
    analysis_id = _string(payload.get("analysis_id"), "analysis_id")
    return {"ok": True, "schema": "sc.research.execution-lineage-plan.v1", "version": VERSION, "session_id": session_id, "execution_ref": str(payload.get("execution_ref") or f"lab:spatial:{analysis_id}")[:240], "method_ref": str(payload.get("method_ref") or SCHEMA)[:240], "input_refs": copy.deepcopy(payload.get("input_refs") or []), "output_refs": copy.deepcopy(payload.get("output_refs") or []), "environment_ref": payload.get("environment_ref"), "automatic_execution": False, "automatic_core_submission": False}


def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": True,
        "schema": f"{SCHEMA}/interpretation-boundaries",
        "version": VERSION,
        "boundaries": [
            "Spatial association is not causal identification.",
            "Hotspot or cluster diagnostics do not automatically establish statistical significance.",
            "Coordinate reference systems and units remain researcher-declared and are not silently reprojected.",
            "Neighborhood rules and bandwidths are explicit research choices and are not silently optimized.",
            "Raster change does not by itself establish why change occurred.",
            "Spatial joins and topology repair are not automatically inferred or executed.",
            "Trajectory distances are planar coordinate-unit calculations unless a separate geodesic method is explicitly used.",
            "Spatiotemporal trends do not automatically establish interventions, mechanisms, or counterfactual effects.",
        ],
        "scientific_validity_certified": False,
        "causal_validity_certified": False,
        "significance_certified": False,
        "automatic_core_submission": False,
        "determine_truth": False,
    }
