from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

import numpy as np
from scipy import stats
from scipy.stats import qmc

from .equation_builder import EquationBuilderError, compile_equation, evaluate
from .model_studio import ModelStudioError, normalize_model

VERSION = "0.48.0"
STUDY_SCHEMA = "sc-lab-probabilistic-study/0.48.0"
RESULT_SCHEMA = "sc-lab-probabilistic-analysis/0.48.0"
GRAPH_SCHEMA = "sc-lab-scientific-graph/0.46.0"
DESIGNS = {"monte-carlo", "latin-hypercube", "sobol", "saltelli-sobol"}
DISTRIBUTIONS = {"uniform", "normal", "lognormal", "triangular"}
SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
MAX_BASE_SAMPLES = 65536
MAX_EVALUATIONS = 250000
MAX_CURVE_POINTS = 160


class ProbabilisticAnalysisError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, limit: int = 240, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ProbabilisticAnalysisError(f"{name} is required.")
    if len(text) > limit:
        raise ProbabilisticAnalysisError(f"{name} exceeds {limit} characters.")
    return text


def _finite(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ProbabilisticAnalysisError(f"{name} must be numeric.") from exc
    if not math.isfinite(result):
        raise ProbabilisticAnalysisError(f"{name} must be finite.")
    return result


def _symbol(value: Any, name: str) -> str:
    text = _text(value, name, 64, True)
    if not SYMBOL_RE.fullmatch(text):
        raise ProbabilisticAnalysisError(f"{name} must be a safe scientific symbol.")
    return text


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "studySchema": STUDY_SCHEMA,
        "resultSchema": RESULT_SCHEMA,
        "graphSchema": GRAPH_SCHEMA,
        "designs": sorted(DESIGNS),
        "distributions": sorted(DISTRIBUTIONS),
        "sensitivity": ["pearson", "spearman", "standardized-regression", "saltelli-sobol"],
        "probabilisticSummaries": ["moments", "quantiles", "central-interval", "threshold-probabilities", "skewness", "kurtosis"],
        "probabilisticVisualizations": ["histogram", "empirical-cdf", "sensitivity-bars", "uncertainty-ribbon"],
        "independentInputs": True,
        "safeDeclarativeModels": True,
        "registeredModelEnsembles": "ensemble-uncertainty-v0341",
        "arbitraryCode": False,
        "limits": {"baseSamples": MAX_BASE_SAMPLES, "evaluations": MAX_EVALUATIONS, "uncertainInputs": 32, "curvePoints": MAX_CURVE_POINTS},
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "integrated-probabilistic-analysis-ready",
        "version": VERSION,
        "safeDeclarativeModels": True,
        "monteCarlo": True,
        "latinHypercube": True,
        "sobolSampling": True,
        "saltelliSobolSensitivity": True,
        "probabilisticVisualization": True,
        "graphStudioHandoff": True,
        "legacyEnsembleCompatibility": "0.34.1",
        "arbitraryCode": False,
    }


def _normalize_distribution(raw: dict[str, Any], allowed_symbols: set[str]) -> dict[str, Any]:
    symbol = _symbol(raw.get("symbol") or raw.get("name"), "uncertain input symbol")
    if symbol not in allowed_symbols:
        raise ProbabilisticAnalysisError(f"Uncertain input {symbol} is not an eligible model input or parameter.")
    distribution = _text(raw.get("distribution") or "uniform", f"{symbol}.distribution", 32, True).lower()
    if distribution not in DISTRIBUTIONS:
        raise ProbabilisticAnalysisError(f"Unsupported uncertainty distribution for {symbol}.")
    record: dict[str, Any] = {
        "symbol": symbol,
        "label": _text(raw.get("label") or symbol, f"{symbol}.label", 120, True),
        "unit": _text(raw.get("unit"), f"{symbol}.unit", 80),
        "distribution": distribution,
    }
    if distribution == "uniform":
        low = _finite(raw.get("low"), f"{symbol}.low")
        high = _finite(raw.get("high"), f"{symbol}.high")
        if high <= low:
            raise ProbabilisticAnalysisError(f"{symbol}.high must exceed low.")
        record.update(low=low, high=high)
    elif distribution == "normal":
        mean = _finite(raw.get("mean", 0), f"{symbol}.mean")
        std = _finite(raw.get("stdDev"), f"{symbol}.stdDev")
        if std <= 0:
            raise ProbabilisticAnalysisError(f"{symbol}.stdDev must be positive.")
        record.update(mean=mean, stdDev=std)
    elif distribution == "lognormal":
        mean_log = _finite(raw.get("meanLog", 0), f"{symbol}.meanLog")
        std_log = _finite(raw.get("stdLog"), f"{symbol}.stdLog")
        if std_log <= 0:
            raise ProbabilisticAnalysisError(f"{symbol}.stdLog must be positive.")
        record.update(meanLog=mean_log, stdLog=std_log)
    else:
        low = _finite(raw.get("low"), f"{symbol}.low")
        mode = _finite(raw.get("mode"), f"{symbol}.mode")
        high = _finite(raw.get("high"), f"{symbol}.high")
        if high <= low or not low <= mode <= high:
            raise ProbabilisticAnalysisError(f"{symbol} triangular bounds must satisfy low <= mode <= high with high > low.")
        record.update(low=low, mode=mode, high=high)
    return record


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProbabilisticAnalysisError("Probabilistic study must be an object.")
    try:
        model = normalize_model(payload.get("model") or {})
    except ModelStudioError as exc:
        raise ProbabilisticAnalysisError(str(exc)) from exc
    if model.get("family") != "declarative-expression" or model.get("definition", {}).get("safeExecution") is not True:
        raise ProbabilisticAnalysisError("Integrated probabilistic analysis currently requires a safe declarative-expression Model Studio model.")

    response_symbols = {row["symbol"] for row in model.get("variables", []) if row.get("role") == "response"}
    allowed_symbols = {row["symbol"] for row in model.get("variables", []) if row.get("role") != "response"}
    allowed_symbols.update(row["symbol"] for row in model.get("parameters", []))
    uncertain_raw = payload.get("uncertainInputs") or payload.get("uncertainVariables") or []
    if not isinstance(uncertain_raw, list) or not uncertain_raw:
        raise ProbabilisticAnalysisError("At least one uncertain input is required.")
    if len(uncertain_raw) > 32:
        raise ProbabilisticAnalysisError("Probabilistic studies are limited to 32 uncertain inputs.")
    uncertain = [_normalize_distribution(row, allowed_symbols) for row in uncertain_raw if isinstance(row, dict)]
    if len(uncertain) != len(uncertain_raw):
        raise ProbabilisticAnalysisError("uncertainInputs must contain objects.")
    names = [row["symbol"] for row in uncertain]
    if len(names) != len(set(names)):
        raise ProbabilisticAnalysisError("Uncertain input symbols must be unique.")
    if response_symbols.intersection(names):
        raise ProbabilisticAnalysisError("Response symbols cannot be sampled as uncertain inputs.")

    design_raw = payload.get("design") if isinstance(payload.get("design"), dict) else {}
    method = _text(design_raw.get("method") or "latin-hypercube", "design.method", 40, True).lower()
    if method not in DESIGNS:
        raise ProbabilisticAnalysisError("Unsupported probabilistic sampling design.")
    samples = int(design_raw.get("samples", 2048))
    if samples < 16 or samples > MAX_BASE_SAMPLES:
        raise ProbabilisticAnalysisError(f"design.samples must be between 16 and {MAX_BASE_SAMPLES}.")
    seed = int(design_raw.get("seed", 42))
    actual_evaluations = samples * (len(uncertain) + 2) if method == "saltelli-sobol" else samples
    if actual_evaluations > MAX_EVALUATIONS:
        raise ProbabilisticAnalysisError(f"Requested design requires {actual_evaluations} evaluations; maximum is {MAX_EVALUATIONS}.")

    analysis_raw = payload.get("analysis") if isinstance(payload.get("analysis"), dict) else {}
    confidence = _finite(analysis_raw.get("confidence", 0.95), "analysis.confidence")
    if not 0.5 <= confidence <= 0.999:
        raise ProbabilisticAnalysisError("analysis.confidence must be between 0.5 and 0.999.")
    thresholds = [_finite(v, "analysis.thresholds") for v in (analysis_raw.get("thresholds") or [])][:20]

    values: dict[str, float] = {}
    for row in model.get("parameters", []):
        if row.get("value") is not None:
            values[row["symbol"]] = float(row["value"])
    for row in model.get("constants", []):
        values[row["symbol"]] = float(row["value"])
    supplied_values = payload.get("values") or payload.get("fixedValues") or {}
    if not isinstance(supplied_values, dict):
        raise ProbabilisticAnalysisError("values must be an object.")
    for key, value in supplied_values.items():
        values[_symbol(key, "fixed value symbol")] = _finite(value, f"values.{key}")
    for symbol in names:
        values.pop(symbol, None)

    curve = None
    curve_raw = payload.get("curve")
    if curve_raw:
        if not isinstance(curve_raw, dict):
            raise ProbabilisticAnalysisError("curve must be an object.")
        x_symbol = _symbol(curve_raw.get("xSymbol"), "curve.xSymbol")
        if x_symbol not in allowed_symbols or x_symbol in names:
            raise ProbabilisticAnalysisError("curve.xSymbol must be a deterministic model input that is not itself sampled.")
        start = _finite(curve_raw.get("start"), "curve.start")
        stop = _finite(curve_raw.get("stop"), "curve.stop")
        points = int(curve_raw.get("points", 41))
        if points < 3 or points > MAX_CURVE_POINTS or stop <= start:
            raise ProbabilisticAnalysisError(f"curve requires stop > start and 3 to {MAX_CURVE_POINTS} points.")
        if samples * points > MAX_EVALUATIONS:
            raise ProbabilisticAnalysisError("Curve uncertainty would exceed the maximum probabilistic evaluation budget.")
        curve = {"xSymbol": x_symbol, "start": start, "stop": stop, "points": points}

    study = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "id": _text(payload.get("id") or f"prob-{_digest(payload)[:16]}", "study id", 140, True),
        "title": _text(payload.get("title") or f"{model['title']} — uncertainty", "study title", 220, True),
        "model": model,
        "uncertainInputs": uncertain,
        "values": values,
        "design": {"method": method, "samples": samples, "seed": seed, "evaluationCount": actual_evaluations},
        "analysis": {"confidence": confidence, "thresholds": thresholds},
        "curve": curve,
        "governance": {"independentInputs": True, "safeDeclarativeExecution": True, "arbitraryCode": False},
        "createdAt": _now(),
    }
    study["studyHash"] = _digest({k: v for k, v in study.items() if k not in {"createdAt", "studyHash"}})
    return study


def _transform(unit: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    u = np.clip(np.asarray(unit, dtype=float), 1e-12, 1 - 1e-12)
    kind = spec["distribution"]
    if kind == "uniform":
        return spec["low"] + u * (spec["high"] - spec["low"])
    if kind == "normal":
        return stats.norm.ppf(u, loc=spec["mean"], scale=spec["stdDev"])
    if kind == "lognormal":
        return stats.lognorm.ppf(u, s=spec["stdLog"], scale=math.exp(spec["meanLog"]))
    c = (spec["mode"] - spec["low"]) / (spec["high"] - spec["low"])
    return stats.triang.ppf(u, c=c, loc=spec["low"], scale=spec["high"] - spec["low"])


def _unit_design(method: str, samples: int, dimensions: int, seed: int) -> np.ndarray:
    if method == "monte-carlo":
        return np.random.default_rng(seed).random((samples, dimensions))
    if method == "latin-hypercube":
        return qmc.LatinHypercube(d=dimensions, seed=seed).random(samples)
    exponent = max(1, math.ceil(math.log2(samples)))
    return qmc.Sobol(d=dimensions, scramble=True, seed=seed).random_base2(exponent)[:samples]


def _sample_matrix(method: str, samples: int, specs: list[dict[str, Any]], seed: int) -> tuple[np.ndarray, dict[str, Any] | None]:
    d = len(specs)
    if method != "saltelli-sobol":
        unit = _unit_design(method, samples, d, seed)
        columns = [_transform(unit[:, i], spec) for i, spec in enumerate(specs)]
        return np.column_stack(columns), None
    unit = _unit_design("sobol", samples, d * 2, seed)
    a_u, b_u = unit[:, :d], unit[:, d:]
    a = np.column_stack([_transform(a_u[:, i], spec) for i, spec in enumerate(specs)])
    b = np.column_stack([_transform(b_u[:, i], spec) for i, spec in enumerate(specs)])
    ab = []
    for i in range(d):
        mixed = a.copy()
        mixed[:, i] = b[:, i]
        ab.append(mixed)
    return np.vstack([a, b, *ab]), {"a": (0, samples), "b": (samples, samples * 2), "ab": [(samples * (2 + i), samples * (3 + i)) for i in range(d)]}


def _summary(values: np.ndarray, confidence: float, thresholds: list[float]) -> dict[str, Any]:
    y = np.asarray(values, dtype=float)
    alpha = (1.0 - confidence) / 2.0
    return {
        "count": int(y.size),
        "mean": float(np.mean(y)),
        "standardDeviation": float(np.std(y, ddof=1)) if y.size > 1 else 0.0,
        "variance": float(np.var(y, ddof=1)) if y.size > 1 else 0.0,
        "minimum": float(np.min(y)),
        "maximum": float(np.max(y)),
        "median": float(np.median(y)),
        "skewness": float(stats.skew(y, bias=False)) if y.size > 2 and np.std(y) > 0 else 0.0,
        "excessKurtosis": float(stats.kurtosis(y, fisher=True, bias=False)) if y.size > 3 and np.std(y) > 0 else 0.0,
        "quantiles": {name: float(np.quantile(y, q)) for name, q in (("p01", .01), ("p05", .05), ("p25", .25), ("p50", .50), ("p75", .75), ("p95", .95), ("p99", .99))},
        "centralInterval": {"confidence": confidence, "lower": float(np.quantile(y, alpha)), "upper": float(np.quantile(y, 1 - alpha))},
        "thresholdProbabilities": [
            {"threshold": t, "probabilityAbove": float(np.mean(y > t)), "probabilityBelowOrEqual": float(np.mean(y <= t))}
            for t in thresholds
        ],
    }


def _evaluate_matrix(study: dict[str, Any], matrix: np.ndarray) -> np.ndarray:
    model = study["model"]
    declared = [row["symbol"] for row in model.get("variables", []) + model.get("parameters", []) + model.get("constants", [])]
    try:
        compiled = compile_equation(model["definition"]["equation"], declared, model["definition"].get("outputSymbol"))
    except EquationBuilderError as exc:
        raise ProbabilisticAnalysisError(str(exc)) from exc
    fixed = dict(study["values"])
    specs = study["uncertainInputs"]
    missing = [s for s in compiled.symbols if s not in fixed and s not in {row["symbol"] for row in specs}]
    if missing:
        raise ProbabilisticAnalysisError("Missing deterministic values for model symbols: " + ", ".join(sorted(missing)) + ".")
    output = np.empty(matrix.shape[0], dtype=float)
    for i, row in enumerate(matrix):
        env = dict(fixed)
        env.update({specs[j]["symbol"]: float(row[j]) for j in range(len(specs))})
        try:
            output[i] = evaluate(compiled, env)
        except EquationBuilderError as exc:
            raise ProbabilisticAnalysisError(f"Model evaluation failed at probabilistic sample {i}: {exc}") from exc
    return output


def _sensitivity(study: dict[str, Any], matrix: np.ndarray, outputs: np.ndarray, layout: dict[str, Any] | None) -> dict[str, Any]:
    specs = study["uncertainInputs"]
    if layout is not None:
        a0, a1 = layout["a"]
        b0, b1 = layout["b"]
        a = outputs[a0:a1]
        b = outputs[b0:b1]
        variance = float(np.var(np.concatenate([a, b]), ddof=1))
        rows = []
        for i, spec in enumerate(specs):
            ab0, ab1 = layout["ab"][i]
            ab = outputs[ab0:ab1]
            first = float(np.mean(b * (ab - a)) / variance) if variance > 0 else 0.0
            total = float(0.5 * np.mean((a - ab) ** 2) / variance) if variance > 0 else 0.0
            rows.append({"symbol": spec["symbol"], "label": spec["label"], "firstOrder": first, "totalOrder": total, "importance": total})
        rows.sort(key=lambda row: abs(row["importance"]), reverse=True)
        return {"method": "saltelli-sobol", "outputVariance": variance, "variables": rows}

    y = outputs
    x = matrix
    x_std = np.std(x, axis=0, ddof=1)
    y_std = float(np.std(y, ddof=1))
    xz = (x - np.mean(x, axis=0)) / np.where(x_std > 0, x_std, 1.0)
    yz = (y - np.mean(y)) / (y_std if y_std > 0 else 1.0)
    coefficients = np.linalg.lstsq(np.column_stack([np.ones(len(xz)), xz]), yz, rcond=None)[0][1:]
    rows = []
    for i, spec in enumerate(specs):
        pearson = float(stats.pearsonr(x[:, i], y).statistic) if x_std[i] > 0 and y_std > 0 else 0.0
        spearman = float(stats.spearmanr(x[:, i], y).statistic) if x_std[i] > 0 and y_std > 0 else 0.0
        src = float(coefficients[i])
        rows.append({"symbol": spec["symbol"], "label": spec["label"], "pearson": pearson, "spearman": spearman, "standardizedRegression": src, "importance": abs(src)})
    rows.sort(key=lambda row: row["importance"], reverse=True)
    return {"method": "correlation-and-standardized-regression", "variables": rows}


def _histogram_graph(title: str, unit: str, y: np.ndarray, summary: dict[str, Any]) -> dict[str, Any]:
    bins = min(48, max(10, int(round(math.sqrt(len(y))))))
    counts, edges = np.histogram(y, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    return {
        "schema": GRAPH_SCHEMA, "version": "0.46.0", "kind": "histogram",
        "title": f"{title} — output distribution", "description": "Probabilistic output distribution from governed uncertainty propagation.",
        "xLabel": f"Output{f' ({unit})' if unit else ''}", "yLabel": "Count",
        "bars": [{"x": float(x), "y": int(c)} for x, c in zip(centers, counts)],
        "annotations": [
            {"type": "vertical-line", "x": summary["median"], "label": "Median"},
            {"type": "vertical-line", "x": summary["centralInterval"]["lower"], "label": "Lower interval"},
            {"type": "vertical-line", "x": summary["centralInterval"]["upper"], "label": "Upper interval"},
        ],
        "publication": {"caption": "Probabilistic output distribution.", "source": "Sustainable Catalyst Lab probabilistic analysis", "method": "Governed sampling and safe declarative model evaluation", "notes": "Input uncertainties are treated as independent.", "aspectRatio": "16:9", "showGrid": True, "showLegend": False},
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": True},
        "exports": ["svg", "png", "csv", "json"],
    }


def _cdf_graph(title: str, unit: str, y: np.ndarray) -> dict[str, Any]:
    ordered = np.sort(y)
    stride = max(1, len(ordered) // 1000)
    indices = list(range(0, len(ordered), stride))
    if indices[-1] != len(ordered) - 1:
        indices.append(len(ordered) - 1)
    points = [{"x": float(ordered[i]), "y": float((i + 1) / len(ordered))} for i in indices]
    return {
        "schema": GRAPH_SCHEMA, "version": "0.46.0", "kind": "line",
        "title": f"{title} — empirical cumulative probability", "description": "Empirical CDF of the probabilistic model output.",
        "xLabel": f"Output{f' ({unit})' if unit else ''}", "yLabel": "Cumulative probability",
        "series": [{"id": "ecdf", "label": "Empirical CDF", "mode": "line", "points": points}],
        "publication": {"caption": "Empirical cumulative distribution of model output.", "source": "Sustainable Catalyst Lab probabilistic analysis", "method": "Empirical CDF", "notes": "", "aspectRatio": "16:9", "showGrid": True, "showLegend": True},
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": True},
        "exports": ["svg", "png", "csv", "json"],
    }


def _sensitivity_graph(title: str, sensitivity: dict[str, Any]) -> dict[str, Any]:
    sobol = sensitivity.get("method") == "saltelli-sobol"
    bars = []
    for row in sensitivity.get("variables", []):
        value = row.get("totalOrder") if sobol else row.get("standardizedRegression")
        bars.append({"label": row.get("label") or row.get("symbol"), "value": float(value or 0)})
    return {
        "schema": GRAPH_SCHEMA, "version": "0.46.0", "kind": "horizontal-bars",
        "title": f"{title} — sensitivity", "description": "Ranked model-output sensitivity to uncertain inputs.",
        "xLabel": "Sobol total-order index" if sobol else "Standardized regression coefficient", "yLabel": "Uncertain input", "bars": bars,
        "publication": {"caption": "Global sensitivity ranking.", "source": "Sustainable Catalyst Lab probabilistic analysis", "method": "Saltelli–Sobol total-order sensitivity" if sobol else "Standardized regression with Pearson and Spearman diagnostics", "notes": "Independent-input sensitivity analysis.", "aspectRatio": "16:9", "showGrid": True, "showLegend": False},
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": True},
        "exports": ["svg", "png", "csv", "json"],
    }


def _curve_graph(study: dict[str, Any], matrix: np.ndarray) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    curve = study.get("curve")
    if not curve:
        raise ProbabilisticAnalysisError("No uncertainty curve was requested.")
    model = study["model"]
    declared = [row["symbol"] for row in model.get("variables", []) + model.get("parameters", []) + model.get("constants", [])]
    compiled = compile_equation(model["definition"]["equation"], declared, model["definition"].get("outputSymbol"))
    specs = study["uncertainInputs"]
    fixed = dict(study["values"])
    x_values = np.linspace(curve["start"], curve["stop"], curve["points"])
    confidence = study["analysis"]["confidence"]
    alpha = (1 - confidence) / 2
    records = []
    for x in x_values:
        y = np.empty(matrix.shape[0], dtype=float)
        for i, sample in enumerate(matrix):
            env = dict(fixed)
            env[curve["xSymbol"]] = float(x)
            env.update({specs[j]["symbol"]: float(sample[j]) for j in range(len(specs))})
            try:
                y[i] = evaluate(compiled, env)
            except EquationBuilderError as exc:
                raise ProbabilisticAnalysisError(f"Curve uncertainty evaluation failed at x={x}: {exc}") from exc
        records.append({"x": float(x), "median": float(np.median(y)), "mean": float(np.mean(y)), "lower": float(np.quantile(y, alpha)), "upper": float(np.quantile(y, 1 - alpha))})
    x_unit = next((row.get("unit") or "" for row in model.get("variables", []) if row["symbol"] == curve["xSymbol"]), "")
    output_symbol = model["definition"].get("outputSymbol") or "output"
    y_unit = next((row.get("unit") or "" for row in model.get("variables", []) if row["symbol"] == output_symbol), "")
    graph = {
        "schema": GRAPH_SCHEMA, "version": "0.46.0", "kind": "line",
        "title": f"{study['title']} — uncertainty band", "description": "Median prediction with central probabilistic uncertainty ribbon.",
        "xLabel": f"{curve['xSymbol']}{f' ({x_unit})' if x_unit else ''}", "yLabel": f"{output_symbol}{f' ({y_unit})' if y_unit else ''}",
        "series": [{"id": "probabilistic-median", "label": f"Median with {confidence*100:.1f}% interval", "mode": "line", "points": [{"x": row["x"], "y": row["median"], "yLow": row["lower"], "yHigh": row["upper"]} for row in records]}],
        "publication": {"caption": "Probabilistic model prediction with central uncertainty interval.", "source": "Sustainable Catalyst Lab probabilistic analysis", "method": f"{study['design']['method']} uncertainty propagation", "notes": "Ribbon reflects propagated input uncertainty under independent-input assumptions.", "aspectRatio": "16:9", "showGrid": True, "showLegend": True},
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": True},
        "exports": ["svg", "png", "csv", "json"],
    }
    return graph, records


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload.get("study") if isinstance(payload, dict) and isinstance(payload.get("study"), dict) else payload)
    specs = study["uncertainInputs"]
    matrix, layout = _sample_matrix(study["design"]["method"], study["design"]["samples"], specs, study["design"]["seed"])
    outputs = _evaluate_matrix(study, matrix)
    if layout is not None:
        a0, a1 = layout["a"]
        b0, b1 = layout["b"]
        summary_outputs = np.concatenate([outputs[a0:a1], outputs[b0:b1]])
        summary_matrix = np.vstack([matrix[a0:a1], matrix[b0:b1]])
    else:
        summary_outputs = outputs
        summary_matrix = matrix
    summary = _summary(summary_outputs, study["analysis"]["confidence"], study["analysis"]["thresholds"])
    sensitivity = _sensitivity(study, matrix, outputs, layout)
    output_symbol = study["model"]["definition"].get("outputSymbol") or "output"
    output_unit = next((row.get("unit") or "" for row in study["model"].get("variables", []) if row["symbol"] == output_symbol), "")
    graphs = {
        "distribution": _histogram_graph(study["title"], output_unit, summary_outputs, summary),
        "cdf": _cdf_graph(study["title"], output_unit, summary_outputs),
        "sensitivity": _sensitivity_graph(study["title"], sensitivity),
    }
    curve_records = None
    if study.get("curve"):
        # Use the base A matrix for Saltelli designs so the ribbon is not weighted by AB construction samples.
        curve_matrix = summary_matrix[: study["design"]["samples"]] if layout is not None else summary_matrix
        graphs["uncertaintyBand"], curve_records = _curve_graph(study, curve_matrix)
    result = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "study": study,
        "summary": summary,
        "sensitivity": sensitivity,
        "graphs": graphs,
        "curve": curve_records,
        "samplePreview": [
            {**{specs[j]["symbol"]: float(summary_matrix[i, j]) for j in range(len(specs))}, output_symbol: float(summary_outputs[i])}
            for i in range(min(40, len(summary_outputs)))
        ],
        "governance": {"independentInputs": True, "arbitraryCode": False, "safeDeclarativeExecution": True},
        "createdAt": _now(),
    }
    result["analysisHash"] = _digest({k: v for k, v in result.items() if k not in {"createdAt", "analysisHash"}})
    return {"ok": True, "result": result}
