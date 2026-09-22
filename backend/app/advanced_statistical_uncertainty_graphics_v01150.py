from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from statistics import NormalDist, mean
from typing import Any

from .uncertainty_ensemble_distribution_v0820 import (
    UncertaintyVisualizationError,
    normalize_distribution as normalize_v0820_distribution,
    normalize_ensemble as normalize_v0820_ensemble,
    normalize_uncertainty as normalize_v0820_uncertainty,
)
from .scientific_visualization_design_system_v01140 import (
    VisualizationDesignSystemError,
    build_publication_figure as build_v01140_publication_figure,
    compose_small_multiples as compose_v01140_small_multiples,
)

VERSION = "0.115.0"
ENGINE_VERSION = "3.1.0"
SCHEMA = "sc-lab-advanced-statistical-uncertainty-graphics/0.115.0"
FIGURE_SCHEMA = "sc-lab-advanced-statistical-figure/0.115.0"
MAX_SAMPLES = 250_000
MAX_RECORDS = 100_000
MAX_SERIES = 64
MAX_COMPONENTS = 256

GRAPHIC_TYPES = {
    "histogram", "ecdf", "box", "violin", "raincloud", "ridge",
    "interval-ribbon", "fan-chart", "posterior-density", "coefficient-forest",
    "calibration-reliability", "residual-diagnostics", "qq",
    "sensitivity", "uncertainty-decomposition", "coverage",
}
INTERVAL_SEMANTICS = {"confidence", "credible", "prediction", "bootstrap", "custom"}
SENSITIVITY_METHODS = {"sobol", "morris", "tornado", "ranked-effect"}
REFERENCE_DISTRIBUTIONS = {"normal"}


class AdvancedStatisticalGraphicsError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 1200, required: bool = False) -> str:
    s = str(value or "").strip()
    if required and not s:
        raise AdvancedStatisticalGraphicsError(f"{label} is required.")
    if len(s) > maximum:
        raise AdvancedStatisticalGraphicsError(f"{label} exceeds {maximum} characters.")
    return s


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise AdvancedStatisticalGraphicsError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise AdvancedStatisticalGraphicsError(f"{label} must be finite.")
    return out


def _samples(value: Any, label: str = "samples") -> list[float]:
    if not isinstance(value, list) or not value:
        raise AdvancedStatisticalGraphicsError(f"{label} must be a non-empty array.")
    if len(value) > MAX_SAMPLES:
        raise AdvancedStatisticalGraphicsError(f"{label} exceeds {MAX_SAMPLES} values.", 413)
    return [_finite(v, f"{label}[{i}]") for i, v in enumerate(value)]


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise AdvancedStatisticalGraphicsError("quantile input is empty.")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    f = pos - lo
    return sorted_values[lo] * (1 - f) + sorted_values[hi] * f


def _base_figure(kind: str, title: str, x_label: str, y_label: str, publication: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "kind": kind,
        "title": title,
        "axes": {"x": {"label": x_label}, "y": {"label": y_label}},
        "series": [], "bars": [], "boxes": [], "violins": [], "bins": [], "annotations": [],
        "publication": copy.deepcopy(publication or {}),
    }


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "graphic_types": sorted(GRAPHIC_TYPES),
        "interval_semantics": sorted(INTERVAL_SEMANTICS),
        "sensitivity_methods": sorted(SENSITIVITY_METHODS),
        "reference_distributions": sorted(REFERENCE_DISTRIBUTIONS),
        "density_policy": "explicit-bandwidth-for-kde",
        "publication_design_system": "0.114.0",
        "uncertainty_engine": "0.82.0",
    }


def normalize_distribution(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        dist = normalize_v0820_distribution(payload)
    except UncertaintyVisualizationError as exc:
        raise AdvancedStatisticalGraphicsError(str(exc), getattr(exc, "status_code", 400)) from exc
    values = sorted(dist["samples"])
    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "distribution": dist,
        "descriptive": {
            "n": len(values),
            "mean": sum(values) / len(values),
            "median": _quantile(values, 0.5),
            "q05": _quantile(values, 0.05),
            "q25": _quantile(values, 0.25),
            "q75": _quantile(values, 0.75),
            "q95": _quantile(values, 0.95),
        },
        "boundaries": {"automatic_parametric_fit": False, "automatic_kde": False, "automatic_distribution_inference": False},
    }
    result["fingerprint"] = _hash({k: v for k, v in result.items() if k != "fingerprint"})
    return {"ok": True, **result}


def explicit_kde(payload: dict[str, Any]) -> dict[str, Any]:
    values = _samples(payload.get("samples"))
    bandwidth = _finite(payload.get("bandwidth"), "bandwidth")
    if bandwidth <= 0:
        raise AdvancedStatisticalGraphicsError("bandwidth must be greater than zero.")
    kernel = _text(payload.get("kernel") or "gaussian", "kernel", 40, True).lower()
    if kernel != "gaussian":
        raise AdvancedStatisticalGraphicsError("v0.115 supports gaussian KDE only.")
    points = int(payload.get("points") or 160)
    if not 32 <= points <= 1024:
        raise AdvancedStatisticalGraphicsError("points must be between 32 and 1024.")
    lo = min(values) - 3 * bandwidth
    hi = max(values) + 3 * bandwidth
    step = (hi - lo) / (points - 1) if points > 1 else 1.0
    norm = 1.0 / (len(values) * bandwidth * math.sqrt(2 * math.pi))
    density = []
    for i in range(points):
        x = lo + i * step
        y = norm * sum(math.exp(-0.5 * ((x - v) / bandwidth) ** 2) for v in values)
        density.append({"x": x, "y": y})
    out = {
        "ok": True, "schema": SCHEMA, "version": VERSION, "method": "gaussian-kde",
        "bandwidth": bandwidth, "point_count": points, "density": density,
        "automatic_bandwidth_selection": False, "automatic_distribution_assumption": False,
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def build_distribution_figure(payload: dict[str, Any]) -> dict[str, Any]:
    mode = _text(payload.get("mode") or "histogram", "mode", 40, True).lower()
    if mode not in {"histogram", "ecdf", "box", "violin", "raincloud", "ridge"}:
        raise AdvancedStatisticalGraphicsError(f"Unsupported distribution figure mode: {mode}")
    norm = normalize_distribution(payload)
    dist = norm["distribution"]
    title = _text(payload.get("title") or "Distribution", "title", 180, True)
    pub = copy.deepcopy(payload.get("publication") or {})
    if mode == "histogram":
        spec = _base_figure("histogram", title, payload.get("x_label") or "Value", "Count", pub)
        spec["bins"] = copy.deepcopy(dist["histogram"]["cells"])
    elif mode == "ecdf":
        spec = _base_figure("ecdf", title, payload.get("x_label") or "Value", "Cumulative probability", pub)
        spec["series"] = [{"id": "ecdf", "label": "ECDF", "semantic_role": "observed", "points": [{"x": r["value"], "y": r["p"]} for r in dist["ecdf"]["points"]]}]
    elif mode == "box":
        b = dist["boxSummary"]
        spec = _base_figure("box", title, "Group", payload.get("y_label") or "Value", pub)
        spec["boxes"] = [{"label": payload.get("label") or "Distribution", **b}]
    else:
        density_cfg = payload.get("density")
        if not isinstance(density_cfg, dict) or density_cfg.get("bandwidth") is None:
            raise AdvancedStatisticalGraphicsError(f"{mode} requires density.bandwidth; v0.115 does not choose KDE bandwidth automatically.", 422)
        kde = explicit_kde({"samples": dist["samples"], **density_cfg})
        spec = _base_figure("violin" if mode in {"violin", "raincloud", "ridge"} else "density", title, payload.get("x_label") or "Value", "Density", pub)
        spec["series"] = [{"id": "density", "label": payload.get("label") or "Density", "semantic_role": "observed", "points": kde["density"]}]
        spec["violins"] = [{"label": payload.get("label") or "Distribution", "density": kde["density"], "box": dist["boxSummary"], "mode": mode}]
    return _wrap_advanced_figure(spec, mode, {"distribution_fingerprint": dist["fingerprint"], "descriptive": norm["descriptive"]}, payload)


def build_interval_figure(payload: dict[str, Any]) -> dict[str, Any]:
    semantics = _text(payload.get("semantics"), "semantics", 40, True).lower()
    if semantics not in INTERVAL_SEMANTICS:
        raise AdvancedStatisticalGraphicsError(f"Unsupported interval semantics: {semantics}")
    level = payload.get("level")
    if semantics in {"confidence", "credible", "prediction"} and level is None:
        raise AdvancedStatisticalGraphicsError(f"{semantics} interval requires an explicit level.")
    try:
        u = normalize_v0820_uncertainty({"type": "interval", "semantics": semantics, "level": level, "records": payload.get("records"), "units": payload.get("units") or "unitless", "provenance": payload.get("provenance") or {}})
    except UncertaintyVisualizationError as exc:
        raise AdvancedStatisticalGraphicsError(str(exc), getattr(exc, "status_code", 400)) from exc
    spec = _base_figure("confidence-band", _text(payload.get("title") or "Interval estimate", "title", 180, True), payload.get("x_label") or "X", payload.get("y_label") or "Estimate", payload.get("publication") or {})
    pts = [{"x": r["x"], "y": r["center"] if r["center"] is not None else (r["lower"] + r["upper"]) / 2, "yLow": r["lower"], "yHigh": r["upper"]} for r in u["records"]]
    spec["series"] = [{"id": "interval", "label": payload.get("label") or semantics.title(), "semantic_role": "model", "points": pts}]
    return _wrap_advanced_figure(spec, "interval-ribbon", {"semantics": semantics, "level": u["level"], "uncertainty_fingerprint": u["fingerprint"]}, payload)


def build_fan_chart(payload: dict[str, Any]) -> dict[str, Any]:
    levels = payload.get("quantile_levels") or payload.get("quantileLevels")
    records = payload.get("records")
    if not isinstance(levels, list) or len(levels) < 3 or not isinstance(records, list) or not records:
        raise AdvancedStatisticalGraphicsError("fan chart requires quantile_levels (>=3) and records.")
    q = [_finite(x, f"quantile_levels[{i}]") for i, x in enumerate(levels)]
    if q != sorted(set(q)) or q[0] <= 0 or q[-1] >= 1:
        raise AdvancedStatisticalGraphicsError("quantile_levels must be unique, ascending, and inside (0,1).")
    median_i = min(range(len(q)), key=lambda i: abs(q[i] - 0.5))
    norm_records = []
    for i, row in enumerate(records[:MAX_RECORDS]):
        if not isinstance(row, dict) or not isinstance(row.get("values"), list) or len(row["values"]) != len(q):
            raise AdvancedStatisticalGraphicsError(f"records[{i}].values must match quantile_levels.")
        vals = [_finite(v, f"records[{i}].values[{j}]") for j, v in enumerate(row["values"])]
        if vals != sorted(vals):
            raise AdvancedStatisticalGraphicsError(f"records[{i}] quantile values must be non-decreasing.")
        norm_records.append({"x": row.get("x", i), "values": vals})
    median = [{"x": r["x"], "y": r["values"][median_i]} for r in norm_records]
    bands = []
    pairs = min(median_i, len(q) - median_i - 1)
    for depth in range(pairs):
        li, ui = depth, len(q) - 1 - depth
        bands.append({"lower_quantile": q[li], "upper_quantile": q[ui], "records": [{"x": r["x"], "lower": r["values"][li], "upper": r["values"][ui]} for r in norm_records]})
    spec = _base_figure("confidence-band", _text(payload.get("title") or "Forecast fan chart", "title", 180, True), payload.get("x_label") or "Time", payload.get("y_label") or "Value", payload.get("publication") or {})
    spec["series"] = [{"id": "median", "label": "Median", "semantic_role": "forecast", "points": median}]
    return _wrap_advanced_figure(spec, "fan-chart", {"quantile_levels": q, "bands": bands, "median_quantile": q[median_i], "automatic_quantile_inference": False}, payload)


def build_posterior_figure(payload: dict[str, Any]) -> dict[str, Any]:
    parameters = payload.get("parameters")
    if not isinstance(parameters, list) or not parameters:
        raise AdvancedStatisticalGraphicsError("parameters must be a non-empty array.")
    if len(parameters) > MAX_SERIES:
        raise AdvancedStatisticalGraphicsError(f"parameters exceeds {MAX_SERIES} entries.", 413)
    rows = []
    for i, p in enumerate(parameters):
        if not isinstance(p, dict):
            raise AdvancedStatisticalGraphicsError(f"parameters[{i}] must be an object.")
        name = _text(p.get("name") or f"parameter-{i+1}", "parameter name", 120, True)
        draws = sorted(_samples(p.get("samples"), f"parameters[{i}].samples"))
        level = _finite(p.get("credible_level", payload.get("credible_level", 0.95)), "credible_level")
        if not 0 < level < 1:
            raise AdvancedStatisticalGraphicsError("credible_level must be between 0 and 1.")
        alpha = (1 - level) / 2
        rows.append({"name": name, "median": _quantile(draws, 0.5), "lower": _quantile(draws, alpha), "upper": _quantile(draws, 1-alpha), "level": level, "n": len(draws)})
    spec = _base_figure("error-bar", _text(payload.get("title") or "Posterior intervals", "title", 180, True), "Parameter", payload.get("y_label") or "Estimate", payload.get("publication") or {})
    spec["series"] = [{"id": "posterior", "label": "Posterior", "semantic_role": "model", "points": [{"x": r["name"], "y": r["median"], "yLow": r["lower"], "yHigh": r["upper"]} for r in rows]}]
    return _wrap_advanced_figure(spec, "posterior-density", {"posterior_intervals": rows, "automatic_prior_inference": False, "automatic_convergence_certification": False}, payload)


def build_coefficient_forest(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("coefficients")
    if not isinstance(rows, list) or not rows:
        raise AdvancedStatisticalGraphicsError("coefficients must be a non-empty array.")
    pts = []
    for i, r in enumerate(rows[:MAX_COMPONENTS]):
        if not isinstance(r, dict):
            raise AdvancedStatisticalGraphicsError(f"coefficients[{i}] must be an object.")
        label = _text(r.get("label") or r.get("name") or f"coefficient-{i+1}", "coefficient label", 160, True)
        estimate = _finite(r.get("estimate"), f"coefficients[{i}].estimate")
        lower = _finite(r.get("lower"), f"coefficients[{i}].lower")
        upper = _finite(r.get("upper"), f"coefficients[{i}].upper")
        if lower > estimate or estimate > upper:
            raise AdvancedStatisticalGraphicsError(f"coefficients[{i}] requires lower <= estimate <= upper.")
        pts.append({"x": label, "y": estimate, "yLow": lower, "yHigh": upper})
    spec = _base_figure("error-bar", _text(payload.get("title") or "Coefficient estimates", "title", 180, True), "Coefficient", payload.get("y_label") or "Estimate", payload.get("publication") or {})
    spec["series"] = [{"id": "coefficients", "label": "Estimate", "semantic_role": "model", "points": pts}]
    spec["annotations"].append({"type": "reference-line", "axis": "y", "value": _finite(payload.get("reference", 0), "reference")})
    return _wrap_advanced_figure(spec, "coefficient-forest", {"coefficient_count": len(pts)}, payload)


def build_calibration_figure(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("bins")
    if not isinstance(rows, list) or not rows:
        raise AdvancedStatisticalGraphicsError("bins must be a non-empty array.")
    points, total_weight, weighted_error = [], 0.0, 0.0
    for i, r in enumerate(rows[:1000]):
        if not isinstance(r, dict):
            raise AdvancedStatisticalGraphicsError(f"bins[{i}] must be an object.")
        p = _finite(r.get("predicted"), f"bins[{i}].predicted")
        o = _finite(r.get("observed"), f"bins[{i}].observed")
        n = _finite(r.get("count", 1), f"bins[{i}].count")
        if not (0 <= p <= 1 and 0 <= o <= 1) or n <= 0:
            raise AdvancedStatisticalGraphicsError("calibration predicted/observed must be in [0,1] and count > 0.")
        points.append({"x": p, "y": o, "weight": n})
        total_weight += n
        weighted_error += n * abs(p - o)
    ece = weighted_error / total_weight
    spec = _base_figure("line-scatter", _text(payload.get("title") or "Calibration reliability", "title", 180, True), "Predicted probability", "Observed frequency", payload.get("publication") or {})
    spec["axes"]["x"]["domain"] = [0, 1]; spec["axes"]["y"]["domain"] = [0, 1]
    spec["series"] = [
        {"id": "calibration", "label": "Observed", "semantic_role": "model", "points": points},
        {"id": "perfect", "label": "Perfect calibration", "semantic_role": "reference", "points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]},
    ]
    return _wrap_advanced_figure(spec, "calibration-reliability", {"expected_calibration_error": ece, "bin_count": len(points), "automatic_model_quality_certification": False}, payload)


def build_residual_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    observed = _samples(payload.get("observed"), "observed")
    predicted = _samples(payload.get("predicted"), "predicted")
    if len(observed) != len(predicted):
        raise AdvancedStatisticalGraphicsError("observed and predicted must have equal length.")
    residuals = [o-p for o,p in zip(observed,predicted)]
    fitted = [{"x": p, "y": r} for p,r in zip(predicted,residuals)]
    sorted_resid = sorted(residuals)
    nd = NormalDist()
    qq = [{"x": nd.inv_cdf((i+0.5)/len(sorted_resid)), "y": v} for i,v in enumerate(sorted_resid)]
    spec = _base_figure("residual", _text(payload.get("title") or "Residual diagnostics", "title", 180, True), "Fitted value", "Residual", payload.get("publication") or {})
    spec["series"] = [{"id": "residuals", "label": "Residuals", "semantic_role": "observed", "points": fitted}]
    metadata = {"n": len(residuals), "mean_residual": sum(residuals)/len(residuals), "rmse": math.sqrt(sum(r*r for r in residuals)/len(residuals)), "qq_normal_reference": qq, "reference_distribution_declared": "normal", "automatic_diagnostic_pass_fail": False}
    return _wrap_advanced_figure(spec, "residual-diagnostics", metadata, payload)


def build_qq_figure(payload: dict[str, Any]) -> dict[str, Any]:
    values = sorted(_samples(payload.get("samples")))
    reference = _text(payload.get("reference_distribution"), "reference_distribution", 40, True).lower()
    if reference not in REFERENCE_DISTRIBUTIONS:
        raise AdvancedStatisticalGraphicsError(f"Unsupported reference distribution: {reference}")
    if reference == "normal":
        reference_mean = _finite(payload.get("reference_mean", 0), "reference_mean")
        reference_sd = _finite(payload.get("reference_sd", 1), "reference_sd")
        if reference_sd <= 0:
            raise AdvancedStatisticalGraphicsError("reference_sd must be > 0.")
        nd = NormalDist(mu=reference_mean, sigma=reference_sd)
        points = [{"x": nd.inv_cdf((i+0.5)/len(values)), "y": v} for i,v in enumerate(values)]
    spec = _base_figure("qq", _text(payload.get("title") or "Q–Q plot", "title", 180, True), f"Theoretical quantile ({reference})", "Observed quantile", payload.get("publication") or {})
    spec["series"] = [{"id": "qq", "label": "Quantiles", "semantic_role": "observed", "points": points}]
    return _wrap_advanced_figure(spec, "qq", {"reference_distribution": reference, "automatic_distribution_selection": False, "automatic_normality_test": False}, payload)


def build_sensitivity_figure(payload: dict[str, Any]) -> dict[str, Any]:
    method = _text(payload.get("method"), "method", 40, True).lower()
    if method not in SENSITIVITY_METHODS:
        raise AdvancedStatisticalGraphicsError(f"Unsupported sensitivity method: {method}")
    rows = payload.get("effects") or payload.get("indices")
    if not isinstance(rows, list) or not rows:
        raise AdvancedStatisticalGraphicsError("effects/indices must be a non-empty array.")
    normalized = []
    for i,r in enumerate(rows[:MAX_COMPONENTS]):
        if not isinstance(r,dict): raise AdvancedStatisticalGraphicsError(f"effects[{i}] must be an object.")
        name=_text(r.get("name") or r.get("parameter") or f"parameter-{i+1}","parameter",160,True)
        primary = r.get("effect", r.get("st", r.get("mu_star", r.get("value"))))
        value = _finite(primary, f"effects[{i}].value")
        secondary = r.get("s1", r.get("sigma"))
        normalized.append({"name":name,"value":value,"secondary":_finite(secondary,f"effects[{i}].secondary") if secondary is not None else None})
    ranked=sorted(normalized,key=lambda x:abs(x["value"]),reverse=True)
    spec=_base_figure("horizontal-bars",_text(payload.get("title") or f"{method.title()} sensitivity","title",180,True),"Effect","Parameter",payload.get("publication") or {})
    spec["bars"]=[{"category":r["name"],"value":r["value"],"secondary":r["secondary"]} for r in ranked]
    return _wrap_advanced_figure(spec,"sensitivity",{"method":method,"ranked_effects":ranked,"automatic_significance_inference":False,"automatic_causal_inference":False},payload)


def build_uncertainty_decomposition(payload: dict[str, Any]) -> dict[str, Any]:
    components=payload.get("components")
    if not isinstance(components,list) or not components: raise AdvancedStatisticalGraphicsError("components must be a non-empty array.")
    rows=[]; total=0.0
    for i,c in enumerate(components[:MAX_COMPONENTS]):
        if not isinstance(c,dict): raise AdvancedStatisticalGraphicsError(f"components[{i}] must be an object.")
        name=_text(c.get("name") or f"component-{i+1}","component name",160,True); variance=_finite(c.get("variance"),f"components[{i}].variance")
        if variance < 0: raise AdvancedStatisticalGraphicsError("variance components must be non-negative.")
        rows.append({"name":name,"variance":variance}); total += variance
    for r in rows: r["share"] = (r["variance"]/total) if total>0 else 0.0
    spec=_base_figure("pareto",_text(payload.get("title") or "Uncertainty decomposition","title",180,True),"Component","Variance contribution",payload.get("publication") or {})
    spec["bars"]=[{"category":r["name"],"value":r["variance"]} for r in sorted(rows,key=lambda x:x["variance"],reverse=True)]
    return _wrap_advanced_figure(spec,"uncertainty-decomposition",{"total_variance":total,"components":rows,"automatic_variance_attribution":False},payload)


def build_coverage_figure(payload: dict[str, Any]) -> dict[str, Any]:
    records=payload.get("records")
    if not isinstance(records,list) or not records: raise AdvancedStatisticalGraphicsError("records must be a non-empty array.")
    points=[]; covered=0
    for i,r in enumerate(records[:MAX_RECORDS]):
        if not isinstance(r,dict): raise AdvancedStatisticalGraphicsError(f"records[{i}] must be an object.")
        lower=_finite(r.get("lower"),f"records[{i}].lower"); upper=_finite(r.get("upper"),f"records[{i}].upper"); truth=_finite(r.get("truth"),f"records[{i}].truth")
        if lower>upper: raise AdvancedStatisticalGraphicsError(f"records[{i}] lower exceeds upper.")
        is_cov=lower<=truth<=upper; covered += int(is_cov)
        points.append({"x":r.get("x",i),"y":truth,"yLow":lower,"yHigh":upper,"covered":is_cov})
    rate=covered/len(points)
    spec=_base_figure("error-bar",_text(payload.get("title") or "Interval coverage","title",180,True),payload.get("x_label") or "Case",payload.get("y_label") or "Value",payload.get("publication") or {})
    spec["series"]=[{"id":"coverage","label":"Interval and truth","semantic_role":"observed","points":points}]
    return _wrap_advanced_figure(spec,"coverage",{"coverage_rate":rate,"covered":covered,"count":len(points),"automatic_coverage_adequacy_judgment":False},payload)


def compose_statistical_small_multiples(payload: dict[str, Any]) -> dict[str, Any]:
    panels=payload.get("panels")
    if not isinstance(panels,list) or not panels: raise AdvancedStatisticalGraphicsError("panels must be a non-empty array.")
    try:
        result=compose_v01140_small_multiples({"panels":panels,"columns":payload.get("columns",2),"share_x":payload.get("share_x",False),"share_y":payload.get("share_y",False)})
    except VisualizationDesignSystemError as exc:
        raise AdvancedStatisticalGraphicsError(str(exc),getattr(exc,"status_code",400)) from exc
    result["version"]=VERSION; result["schema"]=SCHEMA; result["statistical_consistency"]={"shared_interval_semantics_required":bool(payload.get("require_shared_interval_semantics",False)),"automatic_scale_harmonization":False,"automatic_statistical_comparison":False}
    return result


def _wrap_advanced_figure(spec: dict[str, Any], graphic_type: str, statistical_metadata: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    if graphic_type not in GRAPHIC_TYPES:
        raise AdvancedStatisticalGraphicsError(f"Unsupported graphic type: {graphic_type}")
    result = {
        "ok": True, "schema": FIGURE_SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION,
        "graphic_type": graphic_type, "spec": spec, "statistical_metadata": copy.deepcopy(statistical_metadata),
        "design_system_version": "0.114.0",
        "boundaries": {"automatic_statistical_inference": False, "automatic_scientific_validity_certification": False, "automatic_truth_determination": False},
    }
    result["fingerprint"]=_hash({k:v for k,v in result.items() if k!="fingerprint"})
    return result


def build_publication_figure(payload: dict[str, Any]) -> dict[str, Any]:
    advanced = payload.get("advanced_figure")
    if not isinstance(advanced, dict):
        builder = _text(payload.get("builder"), "builder", 60, True)
        builders = {
            "distribution": build_distribution_figure, "interval": build_interval_figure, "fan-chart": build_fan_chart,
            "posterior": build_posterior_figure, "coefficient-forest": build_coefficient_forest,
            "calibration": build_calibration_figure, "residuals": build_residual_diagnostics, "qq": build_qq_figure,
            "sensitivity": build_sensitivity_figure, "uncertainty-decomposition": build_uncertainty_decomposition,
            "coverage": build_coverage_figure,
        }
        if builder not in builders: raise AdvancedStatisticalGraphicsError(f"Unsupported builder: {builder}")
        advanced = builders[builder](payload)
    try:
        pub = build_v01140_publication_figure({
            "spec": advanced["spec"], "profile": payload.get("profile") or "journal-double",
            "alt_text": payload.get("alt_text") or payload.get("altText") or "Advanced statistical scientific figure.",
            "annotations": payload.get("annotations") or [], "uncertainty_layers": payload.get("uncertainty_layers") or [],
        })
    except VisualizationDesignSystemError as exc:
        raise AdvancedStatisticalGraphicsError(str(exc), getattr(exc,"status_code",400)) from exc
    return {"ok":True,"version":VERSION,"advanced_figure":advanced,"publication":pub,"publication_ready":bool(pub.get("audit",{}).get("publication_ready")),"scientific_validity_certified":False,"automatic_statistical_inference":False}


def manifest() -> dict[str, Any]:
    return {
        "ok": True, "status": "advanced-statistical-uncertainty-graphics-ready", "version": VERSION,
        "engine_version": ENGINE_VERSION, "graphic_type_count": len(GRAPHIC_TYPES),
        "publication_design_system": "0.114.0", "uncertainty_engine": "0.82.0",
        "distribution_graphics": True, "interval_graphics": True, "fan_charts": True,
        "posterior_graphics": True, "coefficient_forests": True, "calibration_reliability": True,
        "residual_diagnostics": True, "qq_plots": True, "sensitivity_graphics": True,
        "uncertainty_decomposition": True, "coverage_graphics": True, "statistical_small_multiples": True,
        "boundaries": {
            "automatic_kde_bandwidth": False, "automatic_distribution_selection": False,
            "automatic_interval_semantics": False, "automatic_significance_inference": False,
            "automatic_causal_inference": False, "automatic_model_quality_certification": False,
            "automatic_scientific_validity_certification": False, "automatic_truth_determination": False,
        },
    }


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "max_samples": MAX_SAMPLES, "max_records": MAX_RECORDS}
