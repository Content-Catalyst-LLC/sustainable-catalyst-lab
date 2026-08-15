from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np
from scipy.optimize import least_squares, minimize
from scipy.special import expit, gammaln
from scipy.stats import norm

from .model_studio import normalize_graph

VERSION = "0.51.0"
STUDY_SCHEMA = "sc-lab-statistical-model-study/0.51.0"
RESULT_SCHEMA = "sc-lab-statistical-model-result/0.51.0"
CV_SCHEMA = "sc-lab-statistical-model-validation/0.51.0"
COMPARISON_SCHEMA = "sc-lab-statistical-model-comparison/0.51.0"
MAX_ROWS = 5000
MAX_FEATURES = 40
MAX_KNOTS = 12
MAX_FOLDS = 20
MAX_REPEATS = 10
MAX_CANDIDATES = 12

FAMILIES = {"gaussian", "binomial-logit", "poisson-log"}
ESTIMATORS = {"ols", "weighted-least-squares", "huber", "ridge", "lasso", "elastic-net", "glm"}
MODEL_TYPES = {"linear", "cubic-spline"}


class AdvancedStatisticalModelingError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, limit: int = 180, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise AdvancedStatisticalModelingError(f"{label} is required.")
    if len(text) > limit:
        raise AdvancedStatisticalModelingError(f"{label} exceeds {limit} characters.")
    return text


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AdvancedStatisticalModelingError(f"{label} must be numeric.") from exc
    if not math.isfinite(number):
        raise AdvancedStatisticalModelingError(f"{label} must be finite.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schemas": {"study": STUDY_SCHEMA, "result": RESULT_SCHEMA, "validation": CV_SCHEMA, "comparison": COMPARISON_SCHEMA},
        "families": sorted(FAMILIES),
        "estimators": sorted(ESTIMATORS),
        "modelTypes": sorted(MODEL_TYPES),
        "regularization": {"ridge": True, "lasso": True, "elasticNet": True, "interceptPenalized": False},
        "splines": {"kind": "cubic-truncated-power", "maximumInteriorKnots": MAX_KNOTS},
        "validation": {"methods": ["k-fold", "repeated-k-fold"], "maximumFolds": MAX_FOLDS, "maximumRepeats": MAX_REPEATS},
        "inference": {
            "ols": True,
            "weightedLeastSquares": True,
            "unpenalizedGlm": True,
            "regularizedModels": False,
            "huber": False,
        },
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryFormulaExecution": False,
            "namedDatasetColumnsOnly": True,
            "automaticCausalClaims": False,
            "automaticFeatureSelection": False,
            "automaticPublication": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "advanced-statistical-modeling-ready",
        "version": VERSION,
        "gaussianRegression": True,
        "robustRegression": True,
        "regularizedRegression": ["ridge", "lasso", "elastic-net"],
        "generalizedLinearModels": ["binomial-logit", "poisson-log"],
        "cubicSplines": True,
        "crossValidation": True,
        "scientificModelComparison": True,
        "sharedVisualizationContract": True,
        "reproduciblePackageCompatible": True,
        "arbitraryCode": False,
    }


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedStatisticalModelingError("Statistical model study must be an object.")
    family = _text(payload.get("family") or "gaussian", "family", 40, True)
    estimator = _text(payload.get("estimator") or ("glm" if family != "gaussian" else "ols"), "estimator", 60, True)
    model_type = _text(payload.get("modelType") or "linear", "modelType", 40, True)
    if family not in FAMILIES:
        raise AdvancedStatisticalModelingError("Unsupported statistical family.")
    if estimator not in ESTIMATORS:
        raise AdvancedStatisticalModelingError("Unsupported statistical estimator.")
    if model_type not in MODEL_TYPES:
        raise AdvancedStatisticalModelingError("Unsupported statistical model type.")
    if family == "gaussian" and estimator == "glm":
        raise AdvancedStatisticalModelingError("Gaussian models use OLS, WLS, Huber, ridge, lasso, or elastic-net estimation in v0.51.0.")
    if family != "gaussian" and estimator not in {"glm", "ridge"}:
        raise AdvancedStatisticalModelingError("Binomial and Poisson GLMs support unpenalized GLM or ridge estimation in v0.51.0.")
    if family != "gaussian" and model_type != "linear":
        raise AdvancedStatisticalModelingError("Cubic splines are limited to Gaussian regression in v0.51.0.")
    features = payload.get("features") or []
    if isinstance(features, str):
        features = [row.strip() for row in features.split(",") if row.strip()]
    if not isinstance(features, list) or not features:
        raise AdvancedStatisticalModelingError("At least one feature column is required.")
    features = [_text(row, "feature", 120, True) for row in features]
    if len(features) > MAX_FEATURES or len(set(features)) != len(features):
        raise AdvancedStatisticalModelingError(f"Features must be unique and limited to {MAX_FEATURES} columns.")
    response = _text(payload.get("response"), "response", 120, True)
    if response in features:
        raise AdvancedStatisticalModelingError("Response column cannot also be a feature column.")
    alpha = _finite(payload.get("alpha", 1.0), "alpha")
    if alpha < 0:
        raise AdvancedStatisticalModelingError("alpha must be non-negative.")
    l1_ratio = _finite(payload.get("l1Ratio", 0.5), "l1Ratio")
    if not 0 <= l1_ratio <= 1:
        raise AdvancedStatisticalModelingError("l1Ratio must be between 0 and 1.")
    knots_payload = payload.get("knots", 3)
    if isinstance(knots_payload, list):
        knots = [_finite(v, "knot") for v in knots_payload]
        if len(knots) > MAX_KNOTS:
            raise AdvancedStatisticalModelingError(f"At most {MAX_KNOTS} interior spline knots are supported.")
        if sorted(set(knots)) != sorted(knots):
            raise AdvancedStatisticalModelingError("Spline knots must be unique.")
    else:
        knots = int(_finite(knots_payload, "knots"))
        if knots < 0 or knots > MAX_KNOTS:
            raise AdvancedStatisticalModelingError(f"knots must be between 0 and {MAX_KNOTS}.")
    study = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "recordType": "advanced-statistical-model-study",
        "id": _text(payload.get("id") or f"stats-{_digest({'features': features, 'response': response, 'family': family, 'estimator': estimator, 'modelType': model_type})[:12]}", "study id", 180, True),
        "title": _text(payload.get("title") or "Statistical model", "title", 240, True),
        "family": family,
        "estimator": estimator,
        "modelType": model_type,
        "features": features,
        "response": response,
        "weightColumn": _text(payload.get("weightColumn"), "weightColumn", 120),
        "standardize": bool(payload.get("standardize", estimator in {"ridge", "lasso", "elastic-net"})),
        "alpha": alpha,
        "l1Ratio": l1_ratio,
        "splineFeature": _text(payload.get("splineFeature") or features[0], "splineFeature", 120, True),
        "knots": knots,
        "confidenceLevel": min(max(_finite(payload.get("confidenceLevel", 0.95), "confidenceLevel"), 0.5), 0.999),
        "classificationThreshold": min(max(_finite(payload.get("classificationThreshold", 0.5), "classificationThreshold"), 0.01), 0.99),
        "maxIterations": min(max(int(_finite(payload.get("maxIterations", 2000), "maxIterations")), 50), 10000),
        "tolerance": min(max(_finite(payload.get("tolerance", 1e-8), "tolerance"), 1e-12), 1e-2),
        "provenance": deepcopy(payload.get("provenance") or {}) if isinstance(payload.get("provenance"), dict) else {},
        "boundaries": {"arbitraryCode": False, "automaticCausalClaims": False, "namedDatasetColumnsOnly": True},
    }
    if study["splineFeature"] not in features:
        raise AdvancedStatisticalModelingError("splineFeature must be one of the declared feature columns.")
    study["studyHash"] = _digest({k: v for k, v in study.items() if k not in {"studyHash"}})
    return study


def _clean_rows(study: dict[str, Any], rows: Any) -> tuple[list[dict[str, Any]], int]:
    if not isinstance(rows, list) or not rows:
        raise AdvancedStatisticalModelingError("A non-empty dataset row array is required.")
    if len(rows) > MAX_ROWS:
        raise AdvancedStatisticalModelingError(f"Statistical fitting is limited to {MAX_ROWS} rows per request.")
    required = list(study["features"]) + [study["response"]]
    if study.get("weightColumn"):
        required.append(study["weightColumn"])
    clean: list[dict[str, Any]] = []
    dropped = 0
    for row in rows:
        if not isinstance(row, dict):
            dropped += 1
            continue
        out = dict(row)
        ok = True
        for key in required:
            try:
                out[key] = _finite(row.get(key), key)
            except AdvancedStatisticalModelingError:
                ok = False
                break
        if not ok:
            dropped += 1
            continue
        if study.get("weightColumn") and out[study["weightColumn"]] <= 0:
            dropped += 1
            continue
        clean.append(out)
    if len(clean) < max(4, len(study["features"]) + 2):
        raise AdvancedStatisticalModelingError("Too few complete numeric rows remain for this model.")
    y = np.asarray([row[study["response"]] for row in clean], dtype=float)
    if study["family"] == "binomial-logit" and not np.all(np.isin(y, [0.0, 1.0])):
        raise AdvancedStatisticalModelingError("Binomial-logit response values must be 0 or 1.")
    if study["family"] == "binomial-logit" and len(np.unique(y)) < 2:
        raise AdvancedStatisticalModelingError("Binomial-logit fitting requires both response classes.")
    if study["family"] == "poisson-log" and (np.any(y < 0) or np.any(np.abs(y - np.round(y)) > 1e-9)):
        raise AdvancedStatisticalModelingError("Poisson-log response values must be non-negative counts.")
    return clean, dropped


def _clean_prediction_rows(study: dict[str, Any], rows: Any) -> tuple[list[dict[str, Any]], int]:
    if not isinstance(rows, list) or not rows:
        raise AdvancedStatisticalModelingError("A non-empty prediction row array is required.")
    if len(rows) > MAX_ROWS:
        raise AdvancedStatisticalModelingError(f"Prediction is limited to {MAX_ROWS} rows per request.")
    clean: list[dict[str, Any]] = []
    dropped = 0
    for row in rows:
        if not isinstance(row, dict):
            dropped += 1
            continue
        out = dict(row)
        ok = True
        for key in study["features"]:
            try:
                out[key] = _finite(row.get(key), key)
            except AdvancedStatisticalModelingError:
                ok = False
                break
        if ok:
            clean.append(out)
        else:
            dropped += 1
    if not clean:
        raise AdvancedStatisticalModelingError("No complete numeric prediction rows remain.")
    return clean, dropped


def _resolve_knots(values: np.ndarray, knots: int | list[float]) -> list[float]:
    if isinstance(knots, list):
        lo, hi = float(np.min(values)), float(np.max(values))
        resolved = [float(v) for v in knots if lo < float(v) < hi]
    else:
        if knots <= 0:
            return []
        probs = np.linspace(0, 1, int(knots) + 2)[1:-1]
        resolved = [float(v) for v in np.quantile(values, probs)]
    return sorted(set(resolved))[:MAX_KNOTS]


def _basis(study: dict[str, Any], rows: list[dict[str, Any]], state: dict[str, Any] | None = None) -> tuple[np.ndarray, list[str], dict[str, Any]]:
    raw = np.asarray([[float(row[f]) for f in study["features"]] for row in rows], dtype=float)
    labels = list(study["features"])
    cols: list[np.ndarray] = []
    basis_state = deepcopy(state or {})
    if study["modelType"] == "cubic-spline":
        spline_index = study["features"].index(study["splineFeature"])
        x = raw[:, spline_index]
        knots = basis_state.get("knots") if state else _resolve_knots(x, study["knots"])
        basis_state["knots"] = knots
        cols.extend([x, x ** 2, x ** 3])
        labels = [study["splineFeature"], f"{study['splineFeature']}²", f"{study['splineFeature']}³"]
        for knot in knots:
            cols.append(np.maximum(x - knot, 0.0) ** 3)
            labels.append(f"({study['splineFeature']}-{knot:.6g})₊³")
        for i, feature in enumerate(study["features"]):
            if i != spline_index:
                cols.append(raw[:, i])
                labels.append(feature)
        matrix = np.column_stack(cols) if cols else np.empty((len(rows), 0))
    else:
        matrix = raw
    if study.get("standardize"):
        if state:
            means = np.asarray(basis_state.get("means"), dtype=float)
            scales = np.asarray(basis_state.get("scales"), dtype=float)
        else:
            means = np.mean(matrix, axis=0)
            scales = np.std(matrix, axis=0)
            scales = np.where(scales > 1e-12, scales, 1.0)
            basis_state["means"] = means.tolist()
            basis_state["scales"] = scales.tolist()
        matrix = (matrix - means) / scales
        labels = [f"z({label})" for label in labels]
    X = np.column_stack([np.ones(len(rows)), matrix])
    labels = ["Intercept"] + labels
    basis_state["labels"] = labels
    basis_state["modelType"] = study["modelType"]
    basis_state["standardized"] = bool(study.get("standardize"))
    return X, labels, basis_state


def _soft_threshold(value: float, penalty: float) -> float:
    if value > penalty:
        return value - penalty
    if value < -penalty:
        return value + penalty
    return 0.0


def _fit_elastic_net(X: np.ndarray, y: np.ndarray, alpha: float, l1_ratio: float, max_iter: int, tol: float) -> tuple[np.ndarray, dict[str, Any]]:
    n, p = X.shape
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    converged = False
    iterations = 0
    for iteration in range(1, max_iter + 1):
        old = beta.copy()
        for j in range(p):
            residual = y - X @ beta + X[:, j] * beta[j]
            rho = float(np.dot(X[:, j], residual) / n)
            denom = float(np.dot(X[:, j], X[:, j]) / n)
            if j == 0:
                beta[j] = rho / max(denom, 1e-15)
            else:
                beta[j] = _soft_threshold(rho, alpha * l1_ratio) / max(denom + alpha * (1.0 - l1_ratio), 1e-15)
        iterations = iteration
        if float(np.max(np.abs(beta - old))) <= tol:
            converged = True
            break
    return beta, {"converged": converged, "iterations": iterations}


def _gaussian_fit(study: dict[str, Any], X: np.ndarray, y: np.ndarray, weights: np.ndarray | None) -> tuple[np.ndarray, dict[str, Any]]:
    estimator = study["estimator"]
    if estimator == "ols":
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        return beta, {"converged": True, "iterations": 1}
    if estimator == "weighted-least-squares":
        if weights is None:
            raise AdvancedStatisticalModelingError("Weighted least squares requires a positive weightColumn.")
        root = np.sqrt(weights)
        beta = np.linalg.lstsq(X * root[:, None], y * root, rcond=None)[0]
        return beta, {"converged": True, "iterations": 1}
    if estimator == "huber":
        initial = np.linalg.lstsq(X, y, rcond=None)[0]
        result = least_squares(lambda b: X @ b - y, initial, loss="huber", f_scale=1.0, max_nfev=study["maxIterations"], xtol=study["tolerance"], ftol=study["tolerance"], gtol=study["tolerance"])
        return np.asarray(result.x, dtype=float), {"converged": bool(result.success), "iterations": int(result.nfev), "message": str(result.message)}
    if estimator == "ridge":
        penalty = np.eye(X.shape[1]) * study["alpha"]
        penalty[0, 0] = 0.0
        beta = np.linalg.pinv(X.T @ X + penalty) @ X.T @ y
        return beta, {"converged": True, "iterations": 1}
    if estimator in {"lasso", "elastic-net"}:
        ratio = 1.0 if estimator == "lasso" else study["l1Ratio"]
        return _fit_elastic_net(X, y, study["alpha"], ratio, study["maxIterations"], study["tolerance"])
    raise AdvancedStatisticalModelingError("Gaussian regression requires OLS, weighted least squares, Huber, ridge, lasso, or elastic-net estimation.")


def _glm_fit(study: dict[str, Any], X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    alpha = study["alpha"] if study["estimator"] == "ridge" else 0.0
    def penalty(beta: np.ndarray) -> tuple[float, np.ndarray]:
        grad = np.zeros_like(beta)
        grad[1:] = alpha * beta[1:]
        return 0.5 * alpha * float(np.dot(beta[1:], beta[1:])), grad
    if study["family"] == "binomial-logit":
        def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
            eta = X @ beta
            p = expit(eta)
            eps = 1e-12
            pen, pen_grad = penalty(beta)
            nll = -float(np.sum(y * np.log(np.clip(p, eps, 1-eps)) + (1-y) * np.log(np.clip(1-p, eps, 1-eps)))) + pen
            grad = X.T @ (p - y) + pen_grad
            return nll, grad
    else:
        def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
            eta = np.clip(X @ beta, -30, 30)
            mu = np.exp(eta)
            pen, pen_grad = penalty(beta)
            nll = float(np.sum(mu - y * eta + gammaln(y + 1))) + pen
            grad = X.T @ (mu - y) + pen_grad
            return nll, grad
    initial = np.zeros(X.shape[1], dtype=float)
    if study["family"] == "poisson-log":
        initial[0] = math.log(max(float(np.mean(y)), 1e-6))
    result = minimize(lambda b: objective(b)[0], initial, jac=lambda b: objective(b)[1], method="L-BFGS-B", options={"maxiter": study["maxIterations"], "ftol": study["tolerance"]})
    if not result.success and not np.all(np.isfinite(result.x)):
        raise AdvancedStatisticalModelingError(f"GLM optimizer failed: {result.message}")
    return np.asarray(result.x, dtype=float), {"converged": bool(result.success), "iterations": int(result.nit), "message": str(result.message)}


def _predict_from_state(study: dict[str, Any], rows: list[dict[str, Any]], state: dict[str, Any], beta: np.ndarray) -> np.ndarray:
    X, _, _ = _basis(study, rows, state)
    eta = X @ beta
    if study["family"] == "binomial-logit":
        return expit(eta)
    if study["family"] == "poisson-log":
        return np.exp(np.clip(eta, -30, 30))
    return eta


def _information(study: dict[str, Any], X: np.ndarray, y: np.ndarray, pred: np.ndarray, beta: np.ndarray, weights: np.ndarray | None) -> tuple[dict[str, Any], np.ndarray | None]:
    n, k = len(y), len(beta)
    if study["family"] == "gaussian":
        residual = y - pred
        sse = float(np.sum(residual ** 2))
        sigma2 = sse / max(n - k, 1)
        loglike = -0.5 * n * (math.log(2 * math.pi * max(sigma2, 1e-300)) + 1)
        metrics = {
            "rmse": float(np.sqrt(np.mean(residual ** 2))),
            "mae": float(np.mean(np.abs(residual))),
            "rSquared": float(1 - sse / max(float(np.sum((y - np.mean(y)) ** 2)), 1e-300)),
            "sse": sse,
            "aic": float(2 * k - 2 * loglike),
            "bic": float(k * math.log(n) - 2 * loglike),
        }
        denom = n - k - 1
        metrics["aicc"] = float(metrics["aic"] + (2*k*(k+1))/denom) if denom > 0 else None
        cov = None
        if study["estimator"] in {"ols", "weighted-least-squares"}:
            if weights is None:
                cov = sigma2 * np.linalg.pinv(X.T @ X)
            else:
                cov = sigma2 * np.linalg.pinv(X.T @ (weights[:, None] * X))
        return metrics, cov
    if study["family"] == "binomial-logit":
        p = np.clip(pred, 1e-12, 1-1e-12)
        nll = -float(np.sum(y*np.log(p) + (1-y)*np.log(1-p)))
        null_p = np.clip(float(np.mean(y)), 1e-12, 1-1e-12)
        null_nll = -float(np.sum(y*math.log(null_p) + (1-y)*math.log(1-null_p)))
        metrics = {
            "logLoss": nll/n,
            "accuracy": float(np.mean((p >= study["classificationThreshold"]).astype(float) == y)),
            "pseudoRSquaredMcFadden": float(1 - nll/max(null_nll, 1e-300)),
            "aic": float(2*k + 2*nll),
            "bic": float(k*math.log(n) + 2*nll),
        }
        cov = None
        if study["estimator"] == "glm":
            w = p*(1-p)
            cov = np.linalg.pinv(X.T @ (w[:, None]*X))
        return metrics, cov
    mu = np.clip(pred, 1e-12, None)
    term = np.where(y > 0, y*np.log(np.clip(y/mu, 1e-300, None)) - (y-mu), mu)
    deviance = 2*float(np.sum(term))
    nll = float(np.sum(mu - y*np.log(mu) + gammaln(y+1)))
    metrics = {
        "rmse": float(np.sqrt(np.mean((y-mu)**2))),
        "mae": float(np.mean(np.abs(y-mu))),
        "poissonDeviance": deviance,
        "poissonDevianceMean": deviance/n,
        "aic": float(2*k + 2*nll),
        "bic": float(k*math.log(n) + 2*nll),
    }
    cov = np.linalg.pinv(X.T @ (mu[:, None]*X)) if study["estimator"] == "glm" else None
    return metrics, cov


def _coefficient_table(study: dict[str, Any], labels: list[str], beta: np.ndarray, cov: np.ndarray | None) -> list[dict[str, Any]]:
    z = float(norm.ppf(0.5 + study["confidenceLevel"] / 2))
    rows = []
    for i, (label, value) in enumerate(zip(labels, beta)):
        row: dict[str, Any] = {"term": label, "estimate": float(value), "penalized": bool(i > 0 and study["estimator"] in {"ridge", "lasso", "elastic-net"})}
        if cov is not None and i < cov.shape[0] and cov[i, i] >= 0:
            se = float(math.sqrt(cov[i, i]))
            row.update({"standardError": se, "zOrT": float(value/se) if se > 0 else None, "pValue": float(2*norm.sf(abs(value/se))) if se > 0 else None, "confidenceLow": float(value-z*se), "confidenceHigh": float(value+z*se)})
        else:
            row.update({"standardError": None, "zOrT": None, "pValue": None, "confidenceLow": None, "confidenceHigh": None})
        rows.append(row)
    return rows


def _graphs(study: dict[str, Any], y: np.ndarray, pred: np.ndarray, residual: np.ndarray, coeffs: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    lo = float(min(np.min(y), np.min(pred))); hi = float(max(np.max(y), np.max(pred)))
    observed = normalize_graph({
        "kind": "line-scatter", "title": f"{study['title']} — observed vs predicted", "xLabel": "Observed", "yLabel": "Predicted",
        "description": "Observed response values compared with fitted model predictions.",
        "series": [{"id":"parity","label":"Parity","mode":"line","points":[{"x":lo,"y":lo},{"x":hi,"y":hi}]},{"id":"fit","label":"Fitted observations","mode":"scatter","points":[{"x":float(a),"y":float(b)} for a,b in zip(y,pred)]}],
    })
    residual_graph = normalize_graph({
        "kind":"line-scatter","title":f"{study['title']} — residuals vs fitted","xLabel":"Fitted value","yLabel":"Residual",
        "description":"Residual structure across fitted values.",
        "series":[{"id":"zero","label":"Zero","mode":"line","points":[{"x":float(np.min(pred)),"y":0},{"x":float(np.max(pred)),"y":0}]},{"id":"residual","label":"Residuals","mode":"scatter","points":[{"x":float(a),"y":float(b)} for a,b in zip(pred,residual)]}],
    })
    coefficient_graph = normalize_graph({
        "kind":"horizontal-bars","title":f"{study['title']} — coefficient estimates","xLabel":"Coefficient","yLabel":"Term","description":"Estimated model coefficients. Penalized-model coefficients are shrinkage estimates and do not receive classical p-values in this release.",
        "bars":[{"label":row["term"],"value":row["estimate"]} for row in coeffs[:100]],
    })
    out = {"observedPredicted": observed, "residualVsFitted": residual_graph, "coefficients": coefficient_graph}
    if study["modelType"] == "cubic-spline":
        xkey = study["splineFeature"]
        ordered = sorted(zip([float(r[xkey]) for r in rows], pred), key=lambda pair: pair[0])
        out["splineCurve"] = normalize_graph({"kind":"line-scatter","title":f"{study['title']} — spline fit","xLabel":xkey,"yLabel":study["response"],"description":"Cubic truncated-power spline fitted over the observed predictor range.","series":[{"id":"spline","label":"Spline fit","mode":"line","points":[{"x":x,"y":float(v)} for x,v in ordered]}]})
    return out


def fit(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedStatisticalModelingError("Statistical fit request must be an object.")
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
    rows, dropped = _clean_rows(study, payload.get("rows") or (payload.get("study") or {}).get("rows"))
    X, labels, state = _basis(study, rows)
    y = np.asarray([float(row[study["response"]]) for row in rows], dtype=float)
    weights = np.asarray([float(row[study["weightColumn"]]) for row in rows], dtype=float) if study.get("weightColumn") else None
    beta, convergence = _gaussian_fit(study, X, y, weights) if study["family"] == "gaussian" else _glm_fit(study, X, y)
    pred = _predict_from_state(study, rows, state, beta)
    residual = y - pred
    metrics, cov = _information(study, X, y, pred, beta, weights)
    coeffs = _coefficient_table(study, labels, beta, cov)
    rank = int(np.linalg.matrix_rank(X)); condition = float(np.linalg.cond(X)) if X.size else 0.0
    inference_available = cov is not None
    result = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "recordType": "advanced-statistical-model-result",
        "study": study,
        "n": len(rows),
        "droppedRows": dropped,
        "design": {"rank": rank, "columns": X.shape[1], "conditionNumber": condition, "state": state},
        "coefficients": coeffs,
        "coefficientVector": [float(v) for v in beta],
        "metrics": metrics,
        "convergence": convergence,
        "predictions": [{"index": i, "observed": float(y[i]), "predicted": float(pred[i]), "residual": float(residual[i])} for i in range(len(y))],
        "graphs": _graphs(study, y, pred, residual, coeffs, rows),
        "inference": {"available": inference_available, "confidenceLevel": study["confidenceLevel"], "note": "Classical coefficient uncertainty is reported only for OLS/WLS and unpenalized GLMs; robust and regularized estimates intentionally omit classical p-values."},
        "governance": {"associationNotCausation": True, "arbitraryCode": False, "automaticFeatureSelection": False, "regularizedPValuesSuppressed": True},
        "createdAt": _now(),
    }
    result["resultHash"] = _digest({k:v for k,v in result.items() if k not in {"createdAt","resultHash"}})
    return {"ok": True, "result": result}


def predict(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("result"), dict):
        raise AdvancedStatisticalModelingError("Prediction requires a v0.51.0 fitted result.")
    result = payload["result"]
    if result.get("schema") != RESULT_SCHEMA:
        raise AdvancedStatisticalModelingError("Unsupported statistical result contract.")
    study = normalize_study(result.get("study") or {})
    rows, dropped = _clean_prediction_rows(study, payload.get("rows"))
    beta = np.asarray(result.get("coefficientVector") or [], dtype=float)
    state = ((result.get("design") or {}).get("state") or {})
    if beta.size == 0:
        raise AdvancedStatisticalModelingError("Fitted result is missing coefficients.")
    pred = _predict_from_state(study, rows, state, beta)
    return {"ok": True, "version": VERSION, "predictions": [float(v) for v in pred], "rows": len(rows), "droppedRows": dropped}


def _primary_metric(study: dict[str, Any]) -> tuple[str, bool]:
    if study["family"] == "gaussian": return "rmse", True
    if study["family"] == "binomial-logit": return "logLoss", True
    return "poissonDevianceMean", True


def cross_validate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedStatisticalModelingError("Cross-validation request must be an object.")
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
    rows, dropped = _clean_rows(study, payload.get("rows") or (payload.get("study") or {}).get("rows"))
    folds = min(max(int(payload.get("folds", 5)), 2), min(MAX_FOLDS, len(rows)))
    repeats = min(max(int(payload.get("repeats", 1)), 1), MAX_REPEATS)
    seed = int(payload.get("seed", 42))
    key, lower_better = _primary_metric(study)
    values: list[float] = []
    fold_rows: list[dict[str, Any]] = []
    all_indices = np.arange(len(rows))
    for repeat in range(repeats):
        rng = np.random.default_rng(seed + repeat)
        shuffled = rng.permutation(all_indices)
        parts = np.array_split(shuffled, folds)
        for fold_index, test_idx in enumerate(parts):
            train_idx = np.setdiff1d(all_indices, test_idx, assume_unique=True)
            train_rows = [rows[int(i)] for i in train_idx]
            test_rows = [rows[int(i)] for i in test_idx]
            fitted = fit({"study": study, "rows": train_rows})["result"]
            pred = np.asarray(predict({"result": fitted, "rows": test_rows})["predictions"], dtype=float)
            y = np.asarray([float(row[study["response"]]) for row in test_rows], dtype=float)
            if study["family"] == "gaussian":
                value = float(np.sqrt(np.mean((y-pred)**2)))
            elif study["family"] == "binomial-logit":
                p = np.clip(pred,1e-12,1-1e-12); value = -float(np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
            else:
                mu=np.clip(pred,1e-12,None); term=np.where(y>0,y*np.log(np.clip(y/mu,1e-300,None))-(y-mu),mu); value=2*float(np.mean(term))
            values.append(value)
            fold_rows.append({"repeat": repeat+1, "fold": fold_index+1, key: value, "testRows": len(test_rows)})
    record = {
        "schema": CV_SCHEMA, "version": VERSION, "recordType": "advanced-statistical-model-validation", "study": study,
        "folds": folds, "repeats": repeats, "seed": seed, "primaryMetric": key, "lowerIsBetter": lower_better,
        "mean": float(np.mean(values)), "standardDeviation": float(np.std(values, ddof=1)) if len(values)>1 else 0.0,
        "minimum": float(np.min(values)), "maximum": float(np.max(values)), "foldResults": fold_rows, "droppedRows": dropped, "createdAt": _now(),
    }
    record["validationHash"] = _digest({k:v for k,v in record.items() if k not in {"createdAt","validationHash"}})
    return {"ok": True, "validation": record}


def compare(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedStatisticalModelingError("Model comparison request must be an object.")
    candidates = payload.get("candidates") or []
    rows = payload.get("rows")
    if not isinstance(candidates, list) or len(candidates) < 2 or len(candidates) > MAX_CANDIDATES:
        raise AdvancedStatisticalModelingError(f"Model comparison requires 2 to {MAX_CANDIDATES} candidates.")
    normalized = [normalize_study(row) for row in candidates if isinstance(row, dict)]
    if len(normalized) != len(candidates):
        raise AdvancedStatisticalModelingError("Every comparison candidate must be an object.")
    families = {row["family"] for row in normalized}
    responses = {row["response"] for row in normalized}
    if len(families) != 1 or len(responses) != 1:
        raise AdvancedStatisticalModelingError("Comparison candidates must share the same response distribution family and response column.")
    results = []
    for study in normalized:
        cv = cross_validate({"study": study, "rows": rows, "folds": payload.get("folds",5), "repeats": payload.get("repeats",1), "seed": payload.get("seed",42)})["validation"]
        fitted = fit({"study": study, "rows": rows})["result"]
        results.append({"studyId": study["id"], "title": study["title"], "family": study["family"], "estimator": study["estimator"], "modelType": study["modelType"], "validationMean": cv["mean"], "validationSD": cv["standardDeviation"], "primaryMetric": cv["primaryMetric"], "aic": fitted["metrics"].get("aic"), "bic": fitted["metrics"].get("bic"), "resultHash": fitted["resultHash"]})
    ranked = sorted(results, key=lambda row: (row["validationMean"], row.get("aic") if row.get("aic") is not None else float("inf"), row.get("bic") if row.get("bic") is not None else float("inf")))
    for i,row in enumerate(ranked): row["rank"] = i+1
    graph = normalize_graph({"kind":"horizontal-bars","title":"Advanced statistical model comparison","xLabel":ranked[0]["primaryMetric"],"yLabel":"Candidate","description":"Repeated validation score by candidate; lower is better.","bars":[{"label":row["title"],"value":row["validationMean"]} for row in ranked]})
    record = {"schema":COMPARISON_SCHEMA,"version":VERSION,"recordType":"advanced-statistical-model-comparison","primaryMetric":ranked[0]["primaryMetric"],"lowerIsBetter":True,"ranking":ranked,"winner":ranked[0],"graph":graph,"createdAt":_now()}
    record["comparisonHash"] = _digest({k:v for k,v in record.items() if k not in {"createdAt","comparisonHash"}})
    return {"ok":True,"comparison":record}
