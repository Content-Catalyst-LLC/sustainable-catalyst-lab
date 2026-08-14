from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution
from scipy.stats import f as f_dist, t as t_dist

VERSION = "0.46.0"
STUDY_SCHEMA = "sc-lab-response-surface-study/0.46.0"
RESULT_SCHEMA = "sc-lab-response-surface-result/0.46.0"
EXPLORATION_SCHEMA = "sc-lab-design-space-exploration/0.46.0"
OPTIMIZATION_SCHEMA = "sc-lab-design-space-optimization/0.46.0"
GRAPH_SCHEMA = "sc-lab-scientific-graph/0.46.0"
SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
MAX_FACTORS = 8
MAX_ROWS = 20000
MAX_GRID = 81
MAX_OPT_ITER = 800


class ResponseSurfaceError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, max_len: int = 240, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ResponseSurfaceError(f"{name} is required.")
    if len(text) > max_len:
        raise ResponseSurfaceError(f"{name} exceeds {max_len} characters.")
    return text


def _symbol(value: Any, name: str) -> str:
    text = _text(value, name, 64, True)
    if not SYMBOL_RE.fullmatch(text):
        raise ResponseSurfaceError(f"{name} must be a safe scientific symbol.")
    return text


def _finite(value: Any, name: str, required: bool = False) -> float | None:
    if value is None or value == "":
        if required:
            raise ResponseSurfaceError(f"{name} is required.")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ResponseSurfaceError(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise ResponseSurfaceError(f"{name} must be finite.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "studySchema": STUDY_SCHEMA,
        "resultSchema": RESULT_SCHEMA,
        "explorationSchema": EXPLORATION_SCHEMA,
        "optimizationSchema": OPTIMIZATION_SCHEMA,
        "model": "full-second-order-response-surface",
        "limits": {"factors": MAX_FACTORS, "rows": MAX_ROWS, "gridPointsPerAxis": MAX_GRID, "optimizerIterations": MAX_OPT_ITER},
        "capabilities": {
            "codedFactors": True,
            "linearTerms": True,
            "quadraticTerms": True,
            "twoFactorInteractions": True,
            "coefficientInference": True,
            "lackOfFitTestWhenReplicatesExist": True,
            "designSpaceHeatmaps": True,
            "boundedOptimization": True,
            "maximize": True,
            "minimize": True,
            "targetOptimization": True,
            "predictionUncertainty": True,
            "publicationGraphs": True,
        },
        "boundaries": {
            "arbitraryCode": False,
            "extrapolationBeyondFactorBounds": False,
            "higherThanQuadraticResponseSurfaces": False,
            "mixedIntegerOptimization": False,
            "multiResponseDesirability": False,
        },
    }


def health() -> dict[str, Any]:
    return {"ok": True, "status": "response-surfaces-ready", "version": VERSION, "secondOrderRSM": True, "boundedOptimization": True, "designSpaceExploration": True, "arbitraryCode": False}


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ResponseSurfaceError("Response-surface study must be an object.")
    factors_src = payload.get("factors") or []
    if not isinstance(factors_src, list) or not (2 <= len(factors_src) <= MAX_FACTORS):
        raise ResponseSurfaceError(f"Response-surface studies require between 2 and {MAX_FACTORS} factors.")
    factors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, row in enumerate(factors_src):
        if not isinstance(row, dict):
            raise ResponseSurfaceError("factors must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"factors[{i}].symbol")
        if symbol in seen:
            raise ResponseSurfaceError(f"Duplicate factor symbol: {symbol}.")
        seen.add(symbol)
        low = _finite(row.get("low", row.get("lower")), f"{symbol} lower bound", True)
        high = _finite(row.get("high", row.get("upper")), f"{symbol} upper bound", True)
        if high <= low:
            raise ResponseSurfaceError(f"Upper bound must exceed lower bound for {symbol}.")
        center = _finite(row.get("center"), f"{symbol} center")
        if center is None:
            center = (low + high) / 2.0
        if not (low <= center <= high):
            raise ResponseSurfaceError(f"Center for {symbol} must lie within its factor bounds.")
        factors.append({"symbol": symbol, "label": _text(row.get("label") or symbol, "factor label", 120, True), "unit": _text(row.get("unit"), "factor unit", 80), "low": low, "high": high, "center": center})
    response_src = payload.get("response") if isinstance(payload.get("response"), dict) else {"symbol": payload.get("response") or payload.get("responseColumn") or "y"}
    response_symbol = _symbol(response_src.get("symbol") or response_src.get("column") or "y", "response.symbol")
    if response_symbol in seen:
        raise ResponseSurfaceError("Response symbol must differ from factor symbols.")
    normalized = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "recordType": "response-surface-study",
        "id": _text(payload.get("id") or f"rsm-{_digest(payload)[:16]}", "id", 120, True),
        "title": _text(payload.get("title") or "Response surface study", "title", 180, True),
        "model": "full-second-order",
        "factors": factors,
        "response": {"symbol": response_symbol, "label": _text(response_src.get("label") or response_symbol, "response.label", 120, True), "unit": _text(response_src.get("unit"), "response.unit", 80)},
        "assumptions": [_text(x, "assumption", 500, True) for x in (payload.get("assumptions") or [])][:50],
        "provenance": deepcopy(payload.get("provenance") or {}),
        "createdAt": _text(payload.get("createdAt") or _now(), "createdAt", 80, True),
    }
    normalized["studyHash"] = _digest(normalized)
    return normalized


def _clean_rows(study: dict[str, Any], rows: Any) -> list[dict[str, float]]:
    if not isinstance(rows, list):
        raise ResponseSurfaceError("rows must be an array of observation objects.")
    if len(rows) > MAX_ROWS:
        raise ResponseSurfaceError(f"Response-surface fitting is limited to {MAX_ROWS} rows.")
    names = [f["symbol"] for f in study["factors"]]
    response = study["response"]["symbol"]
    clean: list[dict[str, float]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        try:
            item = {name: float(row[name]) for name in names}
            item[response] = float(row[response])
        except (KeyError, TypeError, ValueError):
            continue
        if not all(math.isfinite(v) for v in item.values()):
            continue
        for factor in study["factors"]:
            value = item[factor["symbol"]]
            if value < factor["low"] or value > factor["high"]:
                raise ResponseSurfaceError(f"Row {index + 1} has {factor['symbol']} outside the declared design-space bounds.")
        clean.append(item)
    return clean


def _coded_value(value: float, factor: dict[str, Any]) -> float:
    half = (factor["high"] - factor["low"]) / 2.0
    mid = (factor["high"] + factor["low"]) / 2.0
    return (value - mid) / half


def _terms(factors: list[dict[str, Any]]) -> list[tuple[str, tuple[int, ...]]]:
    terms: list[tuple[str, tuple[int, ...]]] = [("Intercept", ())]
    for i, f in enumerate(factors):
        terms.append((f["symbol"], (i,)))
    for i, f in enumerate(factors):
        terms.append((f"{f['symbol']}^2", (i, i)))
    for i in range(len(factors)):
        for j in range(i + 1, len(factors)):
            terms.append((f"{factors[i]['symbol']}*{factors[j]['symbol']}", (i, j)))
    return terms


def _feature_vector(coded: list[float], terms: list[tuple[str, tuple[int, ...]]]) -> np.ndarray:
    values = []
    for _, indexes in terms:
        if not indexes:
            values.append(1.0)
        elif len(indexes) == 1:
            values.append(coded[indexes[0]])
        else:
            values.append(coded[indexes[0]] * coded[indexes[1]])
    return np.asarray(values, dtype=float)


def _design_matrix(study: dict[str, Any], rows: list[dict[str, float]]) -> tuple[np.ndarray, np.ndarray, list[tuple[str, tuple[int, ...]]]]:
    factors = study["factors"]
    terms = _terms(factors)
    x = np.vstack([_feature_vector([_coded_value(row[f["symbol"]], f) for f in factors], terms) for row in rows])
    y = np.asarray([row[study["response"]["symbol"]] for row in rows], dtype=float)
    return x, y, terms


def _metrics(observed: np.ndarray, predicted: np.ndarray, p: int) -> dict[str, float | None]:
    residual = observed - predicted
    n = int(observed.size)
    sse = float(np.dot(residual, residual))
    mse = sse / max(1, n)
    mae = float(np.mean(np.abs(residual)))
    bias = float(np.mean(residual))
    mean = float(np.mean(observed))
    sst = float(np.dot(observed - mean, observed - mean))
    r2 = 1.0 - sse / sst if sst > 0 else (1.0 if sse <= 1e-15 else 0.0)
    adjusted = 1.0 - (1.0 - r2) * (n - 1) / max(1, n - p) if n > p else None
    sigma2_mle = max(sse / max(1, n), 1e-300)
    aic = float(n * math.log(sigma2_mle) + 2 * p)
    aicc = float(aic + (2 * p * (p + 1)) / (n - p - 1)) if n > p + 1 else None
    bic = float(n * math.log(sigma2_mle) + p * math.log(max(1, n)))
    return {"n": n, "parameterCount": p, "sse": sse, "rmse": math.sqrt(mse), "mae": mae, "bias": bias, "r2": r2, "adjustedR2": adjusted, "aic": aic, "aicc": aicc, "bic": bic}


def _lack_of_fit(study: dict[str, Any], rows: list[dict[str, float]], predicted: np.ndarray, p: int) -> dict[str, Any]:
    factor_names = [f["symbol"] for f in study["factors"]]
    response = study["response"]["symbol"]
    groups: dict[tuple[float, ...], list[float]] = {}
    for row in rows:
        key = tuple(row[n] for n in factor_names)
        groups.setdefault(key, []).append(row[response])
    pure_error_ss = 0.0
    pure_error_df = 0
    for values in groups.values():
        if len(values) > 1:
            arr = np.asarray(values, dtype=float)
            pure_error_ss += float(np.sum((arr - np.mean(arr)) ** 2))
            pure_error_df += len(values) - 1
    if pure_error_df <= 0:
        return {"available": False, "reason": "Replicated design points are required for a pure-error lack-of-fit test."}
    y = np.asarray([row[response] for row in rows], dtype=float)
    residual_ss = float(np.sum((y - predicted) ** 2))
    residual_df = len(rows) - p
    lof_ss = max(0.0, residual_ss - pure_error_ss)
    lof_df = residual_df - pure_error_df
    if lof_df <= 0 or pure_error_ss <= 0:
        return {"available": False, "reason": "Insufficient residual degrees of freedom for a lack-of-fit test."}
    ms_lof = lof_ss / lof_df
    ms_pe = pure_error_ss / pure_error_df
    statistic = ms_lof / ms_pe
    p_value = float(f_dist.sf(statistic, lof_df, pure_error_df))
    return {"available": True, "f": statistic, "pValue": p_value, "lackOfFitSS": lof_ss, "lackOfFitDF": lof_df, "pureErrorSS": pure_error_ss, "pureErrorDF": pure_error_df, "significantAt05": p_value < 0.05}


def _graph(kind: str, title: str, x_label: str, y_label: str, description: str, **extra: Any) -> dict[str, Any]:
    graph = {
        "schema": GRAPH_SCHEMA, "version": VERSION, "kind": kind, "title": title, "description": description,
        "xLabel": x_label, "yLabel": y_label,
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": True},
        "publication": {"subtitle": "", "caption": "", "source": "", "method": "", "notes": "", "aspectRatio": "16:9", "showGrid": True, "showLegend": True, "background": "white"},
        "exports": ["svg", "png", "csv", "json"], "accessibility": {"role": "img", "tabularFallback": True, "keyboardNavigation": True},
    }
    graph.update(extra)
    graph["graphHash"] = _digest(graph)
    return graph


def fit(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ResponseSurfaceError("Fit request must be an object.")
    study = normalize_study(payload.get("study") or payload.get("definition") or payload)
    rows = _clean_rows(study, payload.get("rows") or [])
    x, y, terms = _design_matrix(study, rows)
    p = x.shape[1]
    if len(rows) <= p:
        raise ResponseSurfaceError(f"A full second-order surface with {len(study['factors'])} factors has {p} coefficients and requires more than {p} valid rows.")
    coef, _, rank, singular = np.linalg.lstsq(x, y, rcond=None)
    predicted = x @ coef
    residuals = y - predicted
    metrics = _metrics(y, predicted, p)
    df = len(rows) - p
    sigma2 = float(np.dot(residuals, residuals) / df) if df > 0 else 0.0
    xtx_inv = np.linalg.pinv(x.T @ x)
    covariance = xtx_inv * sigma2
    se = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    coefficients = []
    for i, (name, _) in enumerate(terms):
        value = float(coef[i]); stderr = float(se[i]) if math.isfinite(float(se[i])) else None
        t_stat = value / stderr if stderr and stderr > 0 else None
        p_value = float(2 * t_dist.sf(abs(t_stat), df)) if t_stat is not None and df > 0 else None
        coefficients.append({"term": name, "estimate": value, "standardError": stderr, "t": t_stat, "pValue": p_value, "confidence95": {"lower": value - 1.96 * stderr, "upper": value + 1.96 * stderr} if stderr is not None else None})
    condition = float(np.linalg.cond(x)) if x.size else float("inf")
    warnings: list[str] = []
    if rank < p:
        warnings.append("The response-surface design matrix is rank-deficient; coefficients are not uniquely estimable.")
    elif not math.isfinite(condition) or condition > 1e8:
        warnings.append("The response-surface design matrix is ill-conditioned; coefficient estimates may be unstable.")
    lof = _lack_of_fit(study, rows, predicted, p)
    if lof.get("available") and lof.get("significantAt05"):
        warnings.append("The replicated-point lack-of-fit test is significant at α=0.05; the quadratic response surface may be inadequate over this design space.")
    row_records = []
    for i, row in enumerate(rows):
        rec = {**row, "predicted": float(predicted[i]), "residual": float(residuals[i])}
        row_records.append(rec)
    obs_graph = _graph("line-scatter", f"{study['title']} — observed vs predicted", "Observed", "Predicted", "Observed responses compared with full second-order response-surface predictions.", series=[
        {"id": "parity", "label": "Parity", "mode": "line", "points": [{"x": float(min(y.min(), predicted.min())), "y": float(min(y.min(), predicted.min()))}, {"x": float(max(y.max(), predicted.max())), "y": float(max(y.max(), predicted.max()))}]},
        {"id": "observations", "label": "Design observations", "mode": "scatter", "points": [{"x": float(y[i]), "y": float(predicted[i]), "label": f"Run {i+1}"} for i in range(len(rows))]},
    ])
    residual_graph = _graph("scatter", f"{study['title']} — residuals", "Predicted response", "Observed − predicted", "Residuals from the fitted quadratic response surface.", series=[{"id": "residuals", "label": "Residuals", "mode": "scatter", "points": [{"x": float(predicted[i]), "y": float(residuals[i]), "label": f"Run {i+1}"} for i in range(len(rows))]}], annotations=[{"type": "horizontal-line", "y": 0.0, "label": "Zero residual"}])
    coeff_graph = _graph("horizontal-bars", f"{study['title']} — coded coefficients", "Coefficient estimate", "Term", "Coded-factor response-surface coefficient estimates; intercept omitted from the influence view.", bars=[{"label": row["term"], "value": row["estimate"]} for row in coefficients if row["term"] != "Intercept"])
    result = {
        "schema": RESULT_SCHEMA, "version": VERSION, "recordType": "response-surface-result", "study": study,
        "rowCount": len(rows), "terms": [name for name, _ in terms], "coefficients": coefficients,
        "metrics": metrics, "lackOfFit": lof, "designMatrix": {"rank": int(rank), "columns": p, "conditionNumber": condition, "singularValues": [float(v) for v in singular]},
        "rows": row_records, "warnings": warnings,
        "graphs": {"observedPredicted": obs_graph, "residuals": residual_graph, "coefficients": coeff_graph},
        "fit": {"coefficientVector": [float(v) for v in coef], "covariance": covariance.tolist(), "termNames": [name for name, _ in terms]},
        "createdAt": _now(),
    }
    result["resultHash"] = _digest(result)
    return {"ok": True, "result": result}


def _fit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    supplied = payload.get("result")
    if isinstance(supplied, dict) and supplied.get("schema") == RESULT_SCHEMA:
        return supplied
    return fit(payload)["result"]


def _predict(result: dict[str, Any], point: dict[str, float]) -> tuple[float, float | None]:
    study = result["study"]
    terms = _terms(study["factors"])
    coded = [_coded_value(float(point[f["symbol"]]), f) for f in study["factors"]]
    fv = _feature_vector(coded, terms)
    coef = np.asarray(result["fit"]["coefficientVector"], dtype=float)
    pred = float(fv @ coef)
    cov = np.asarray(result["fit"].get("covariance") or [], dtype=float)
    se = None
    if cov.shape == (len(coef), len(coef)):
        variance = float(fv @ cov @ fv)
        se = math.sqrt(max(0.0, variance))
    return pred, se


def explore(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ResponseSurfaceError("Exploration request must be an object.")
    result = _fit_payload(payload)
    study = result["study"]
    factors = study["factors"]
    x_symbol = _text(payload.get("xFactor") or factors[0]["symbol"], "xFactor", 64, True)
    y_symbol = _text(payload.get("yFactor") or factors[1]["symbol"], "yFactor", 64, True)
    factor_map = {f["symbol"]: f for f in factors}
    if x_symbol == y_symbol or x_symbol not in factor_map or y_symbol not in factor_map:
        raise ResponseSurfaceError("xFactor and yFactor must identify two different study factors.")
    try:
        grid = int(payload.get("gridSize", 31))
    except (TypeError, ValueError) as exc:
        raise ResponseSurfaceError("gridSize must be an integer.") from exc
    if grid < 9 or grid > MAX_GRID:
        raise ResponseSurfaceError(f"gridSize must be between 9 and {MAX_GRID}.")
    fixed_src = payload.get("fixedFactors") if isinstance(payload.get("fixedFactors"), dict) else {}
    fixed: dict[str, float] = {}
    for factor in factors:
        if factor["symbol"] in {x_symbol, y_symbol}:
            continue
        value = _finite(fixed_src.get(factor["symbol"], factor["center"]), f"fixedFactors.{factor['symbol']}", True)
        if not (factor["low"] <= value <= factor["high"]):
            raise ResponseSurfaceError(f"Fixed value for {factor['symbol']} lies outside the design space.")
        fixed[factor["symbol"]] = value
    xs = np.linspace(factor_map[x_symbol]["low"], factor_map[x_symbol]["high"], grid)
    ys = np.linspace(factor_map[y_symbol]["low"], factor_map[y_symbol]["high"], grid)
    cells: list[dict[str, Any]] = []
    z_values = []
    uncertainty = []
    for yi, yv in enumerate(ys):
        for xi, xv in enumerate(xs):
            point = {**fixed, x_symbol: float(xv), y_symbol: float(yv)}
            pred, se = _predict(result, point)
            cells.append({"xIndex": xi, "yIndex": yi, "x": float(xv), "y": float(yv), "z": pred, "standardError": se})
            z_values.append(pred)
            if se is not None:
                uncertainty.append(se)
    constraint = payload.get("responseConstraint") if isinstance(payload.get("responseConstraint"), dict) else {}
    cmin = _finite(constraint.get("minimum"), "responseConstraint.minimum")
    cmax = _finite(constraint.get("maximum"), "responseConstraint.maximum")
    feasible = [c for c in cells if (cmin is None or c["z"] >= cmin) and (cmax is None or c["z"] <= cmax)]
    heatmap = _graph("heatmap", f"{study['title']} — design-space response surface", factor_map[x_symbol]["label"], factor_map[y_symbol]["label"], f"Predicted {study['response']['label']} across the declared design space with other factors held at configured values.", xValues=[float(v) for v in xs], yValues=[float(v) for v in ys], cells=cells, domain={"x": [float(xs[0]), float(xs[-1])], "y": [float(ys[0]), float(ys[-1])], "z": [float(min(z_values)), float(max(z_values))]}, zLabel=study["response"]["label"])
    exploration = {
        "schema": EXPLORATION_SCHEMA, "version": VERSION, "recordType": "design-space-exploration", "resultHash": result.get("resultHash"),
        "xFactor": x_symbol, "yFactor": y_symbol, "fixedFactors": fixed, "gridSize": grid,
        "responseRange": {"minimum": float(min(z_values)), "maximum": float(max(z_values))},
        "predictionStandardErrorRange": {"minimum": float(min(uncertainty)), "maximum": float(max(uncertainty))} if uncertainty else None,
        "responseConstraint": {"minimum": cmin, "maximum": cmax}, "feasibleCells": len(feasible), "totalCells": len(cells), "feasibleFraction": len(feasible) / len(cells),
        "graph": heatmap, "createdAt": _now(),
    }
    exploration["explorationHash"] = _digest(exploration)
    return {"ok": True, "exploration": exploration}


def optimize(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ResponseSurfaceError("Optimization request must be an object.")
    result = _fit_payload(payload)
    study = result["study"]
    goal = _text(payload.get("goal") or "maximize", "goal", 24, True).lower()
    if goal not in {"maximize", "minimize", "target"}:
        raise ResponseSurfaceError("goal must be maximize, minimize, or target.")
    target = _finite(payload.get("target"), "target")
    if goal == "target" and target is None:
        raise ResponseSurfaceError("target optimization requires a numeric target response.")
    factors = study["factors"]
    bounds = [(f["low"], f["high"]) for f in factors]
    def point_from_vector(vector: np.ndarray) -> dict[str, float]:
        return {f["symbol"]: float(vector[i]) for i, f in enumerate(factors)}
    def objective(vector: np.ndarray) -> float:
        pred, _ = _predict(result, point_from_vector(vector))
        if goal == "maximize":
            return -pred
        if goal == "minimize":
            return pred
        return abs(pred - float(target))
    seed = int(payload.get("seed", 42))
    maxiter = int(payload.get("maxIterations", 250))
    if maxiter < 10 or maxiter > MAX_OPT_ITER:
        raise ResponseSurfaceError(f"maxIterations must be between 10 and {MAX_OPT_ITER}.")
    solved = differential_evolution(objective, bounds=bounds, seed=seed, maxiter=maxiter, polish=True, updating="immediate", workers=1, tol=1e-9)
    optimum = point_from_vector(np.asarray(solved.x, dtype=float))
    predicted, se = _predict(result, optimum)
    at_boundary = []
    for factor in factors:
        value = optimum[factor["symbol"]]
        span = factor["high"] - factor["low"]
        if abs(value - factor["low"]) <= span * 1e-5 or abs(value - factor["high"]) <= span * 1e-5:
            at_boundary.append(factor["symbol"])
    warnings = []
    if at_boundary:
        warnings.append("The optimum lies on one or more declared factor bounds; consider whether a wider experimentally valid design region is warranted before extrapolating.")
    optimization = {
        "schema": OPTIMIZATION_SCHEMA, "version": VERSION, "recordType": "design-space-optimization", "resultHash": result.get("resultHash"),
        "goal": goal, "target": target, "optimumFactors": optimum, "predictedResponse": predicted,
        "predictionStandardError": se, "confidence95Approx": {"lower": predicted - 1.96 * se, "upper": predicted + 1.96 * se} if se is not None else None,
        "solver": {"name": "scipy-differential-evolution", "success": bool(solved.success), "message": str(solved.message), "iterations": int(solved.nit), "functionEvaluations": int(solved.nfev), "seed": seed},
        "atBoundary": at_boundary, "warnings": warnings, "createdAt": _now(),
    }
    optimization["optimizationHash"] = _digest(optimization)
    return {"ok": True, "optimization": optimization}
