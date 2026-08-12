from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from statistics import mean, pstdev
from typing import Any

import numpy as np
from scipy.stats import norm

from .model_calibration import (
    ModelCalibrationError,
    _clean_dataset,
    _diagnostics,
    _metrics,
    _parameter_names,
    _predict,
    calibrate,
    normalize_study,
)
from .model_studio import normalize_graph

VERSION = "0.43.0"
DIAGNOSTICS_SCHEMA = "sc-lab-model-diagnostics/0.43.0"
CV_SCHEMA = "sc-lab-cross-validation/0.43.0"
COMPARISON_SCHEMA = "sc-lab-scientific-model-comparison/0.43.0"
MAX_FOLDS = 20
MAX_REPEATS = 10
MAX_CANDIDATES = 12


class ModelDiagnosticsError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schemas": {
            "diagnostics": DIAGNOSTICS_SCHEMA,
            "crossValidation": CV_SCHEMA,
            "comparison": COMPARISON_SCHEMA,
        },
        "validation": {
            "methods": ["k-fold", "repeated-k-fold"],
            "folds": {"minimum": 2, "maximum": MAX_FOLDS, "default": 5},
            "repeats": {"minimum": 1, "maximum": MAX_REPEATS, "default": 1},
            "seeded": True,
        },
        "metrics": ["rmse", "mae", "bias", "rSquared", "maxAbsoluteError", "aic", "aicc", "bic"],
        "diagnostics": ["observed-vs-predicted", "residual-vs-fitted", "standardized-residuals", "qq-normal", "residual-summary"],
        "comparisonPolicy": "lowest mean cross-validation RMSE; AICc then BIC as tie breakers",
        "boundaries": {
            "registeredCalibrationFormsOnly": True,
            "arbitraryCode": False,
            "safeDeclarativeEquationDefinition": True,
            "declarativeParameterFitting": False,
            "deterministicSplits": True,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "model-diagnostics-ready",
        "version": VERSION,
        "crossValidation": True,
        "repeatedCrossValidation": True,
        "residualDiagnostics": True,
        "informationCriteria": ["AIC", "AICc", "BIC"],
        "scientificModelComparison": True,
        "sharedVisualizationContract": True,
        "arbitraryCode": False,
    }


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows") or payload.get("dataset") or []
    if not isinstance(rows, list) or not rows:
        raise ModelDiagnosticsError("A non-empty dataset row array is required.")
    return [row for row in rows if isinstance(row, dict)]


def _study_payload(study: dict[str, Any], **updates: Any) -> dict[str, Any]:
    out = dict(study)
    out.update(updates)
    # Let the calibration service derive a fresh stable hash for the fit configuration.
    out.pop("studyHash", None)
    out.pop("updatedAt", None)
    return out




def _evaluation_dataset(study: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, int]:
    features = study.get("features") or []
    response = study.get("response")
    X: list[list[float]] = []
    y: list[float] = []
    dropped = 0
    for row in rows:
        values = [_finite(row.get(name)) for name in features]
        target = _finite(row.get(response))
        if target is None or any(value is None for value in values):
            dropped += 1
            continue
        X.append([float(value) for value in values])
        y.append(float(target))
    if not X:
        raise ModelDiagnosticsError("No complete numeric rows are available for diagnostics.")
    return np.asarray(X, dtype=float), np.asarray(y, dtype=float), dropped

def _params_vector(study: dict[str, Any], result: dict[str, Any]) -> np.ndarray:
    names = _parameter_names(study)
    params = result.get("parameters") if isinstance(result.get("parameters"), dict) else {}
    missing = [name for name in names if _finite(params.get(name)) is None]
    if missing:
        raise ModelDiagnosticsError("Calibration result is missing numeric parameters: " + ", ".join(missing))
    return np.asarray([float(params[name]) for name in names], dtype=float)


def _information_criteria(metrics: dict[str, Any], n: int, k: int) -> dict[str, float | None]:
    sse = max(float(metrics.get("sse") or 0.0), 1e-300)
    n = max(int(n), 1)
    k = max(int(k), 1)
    aic = float(n * math.log(sse / n) + 2 * k)
    bic = float(n * math.log(sse / n) + k * math.log(n))
    aicc = None
    denom = n - k - 1
    if denom > 0:
        aicc = float(aic + (2 * k * (k + 1)) / denom)
    return {"aic": aic, "aicc": aicc, "bic": bic}


def _graph_observed_predicted(title: str, observed: np.ndarray, predicted: np.ndarray) -> dict[str, Any]:
    lo = float(min(np.min(observed), np.min(predicted)))
    hi = float(max(np.max(observed), np.max(predicted)))
    return normalize_graph({
        "kind": "line-scatter",
        "title": f"{title} — observed vs predicted",
        "description": "Observed response values compared with fitted predictions. The parity line represents exact agreement.",
        "xLabel": "Observed",
        "yLabel": "Predicted",
        "series": [
            {"id": "parity", "label": "Parity", "mode": "line", "points": [{"x": lo, "y": lo}, {"x": hi, "y": hi}]},
            {"id": "fitted", "label": "Observations", "mode": "scatter", "points": [{"x": float(o), "y": float(p)} for o, p in zip(observed, predicted)]},
        ],
    })


def _graph_residual_fitted(title: str, predicted: np.ndarray, residuals: np.ndarray) -> dict[str, Any]:
    xlo, xhi = float(np.min(predicted)), float(np.max(predicted))
    return normalize_graph({
        "kind": "line-scatter",
        "title": f"{title} — residuals vs fitted",
        "description": "Residual structure across fitted values. Systematic patterns can indicate misspecification or heteroscedasticity.",
        "xLabel": "Fitted value",
        "yLabel": "Residual",
        "series": [
            {"id": "zero", "label": "Zero residual", "mode": "line", "points": [{"x": xlo, "y": 0.0}, {"x": xhi, "y": 0.0}]},
            {"id": "residuals", "label": "Residuals", "mode": "scatter", "points": [{"x": float(p), "y": float(r)} for p, r in zip(predicted, residuals)]},
        ],
    })


def _graph_qq(title: str, residuals: np.ndarray) -> dict[str, Any]:
    ordered = np.sort(np.asarray(residuals, dtype=float))
    n = len(ordered)
    probs = (np.arange(1, n + 1) - 0.5) / n
    theoretical = norm.ppf(probs)
    mu = float(np.mean(ordered))
    sigma = float(np.std(ordered, ddof=1)) if n > 1 else 1.0
    expected = mu + sigma * theoretical
    lo = float(min(np.min(expected), np.min(ordered)))
    hi = float(max(np.max(expected), np.max(ordered)))
    return normalize_graph({
        "kind": "line-scatter",
        "title": f"{title} — normal Q–Q diagnostic",
        "description": "Ordered residuals against normal-theory quantiles. Departures from the reference line indicate non-normal residual structure.",
        "xLabel": "Normal-theory residual quantile",
        "yLabel": "Observed residual quantile",
        "series": [
            {"id": "qq-reference", "label": "Normal reference", "mode": "line", "points": [{"x": lo, "y": lo}, {"x": hi, "y": hi}]},
            {"id": "qq-residuals", "label": "Residual quantiles", "mode": "scatter", "points": [{"x": float(x), "y": float(y)} for x, y in zip(expected, ordered)]},
        ],
    })


def diagnose(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelDiagnosticsError("Diagnostics request must be an object.")
    rows = _rows(payload)
    try:
        study = normalize_study(payload)
    except ModelCalibrationError as exc:
        raise ModelDiagnosticsError(str(exc)) from exc

    result = payload.get("result") if isinstance(payload.get("result"), dict) else None
    if result is None:
        try:
            fitted = calibrate({"study": _study_payload(study, holdoutFraction=0.0), "rows": rows})
        except ModelCalibrationError as exc:
            raise ModelDiagnosticsError(str(exc)) from exc
        study = fitted["study"]
        result = fitted["result"]

    try:
        X, y, dropped = _evaluation_dataset(study, rows)
        p = _params_vector(study, result)
        predicted = np.asarray(_predict(study, p, X), dtype=float)
    except ModelCalibrationError as exc:
        raise ModelDiagnosticsError(str(exc)) from exc

    residuals = y - predicted
    metrics = _metrics(y, predicted)
    residual_summary = _diagnostics(y, predicted)
    residual_std = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0
    standardized = residuals / residual_std if residual_std > 0 else np.zeros_like(residuals)
    k = len(p)
    criteria = _information_criteria(metrics, len(y), k)
    flags = [
        {"index": int(i), "observed": float(y[i]), "predicted": float(predicted[i]), "residual": float(residuals[i]), "standardizedResidual": float(standardized[i])}
        for i in range(len(y)) if abs(float(standardized[i])) >= 2.5
    ][:100]
    title = study.get("title") or "Scientific model"
    graphs = {
        "observedPredicted": _graph_observed_predicted(title, y, predicted),
        "residualVsFitted": _graph_residual_fitted(title, predicted, residuals),
        "qqNormal": _graph_qq(title, residuals),
    }
    record = {
        "schema": DIAGNOSTICS_SCHEMA,
        "version": VERSION,
        "recordType": "model-diagnostics",
        "id": f"model-diagnostics-{_digest([study.get('id'), result.get('id'), rows])[:16]}",
        "title": f"Diagnostics: {title}",
        "studyId": study.get("id"),
        "resultId": result.get("id"),
        "modelType": study.get("modelType"),
        "metrics": metrics,
        "informationCriteria": criteria,
        "residualSummary": residual_summary,
        "standardizedResiduals": [float(x) for x in standardized[:2000]],
        "flaggedObservations": flags,
        "rowCounts": {"supplied": len(rows), "usable": len(y), "dropped": dropped},
        "parameterCount": k,
        "graphs": graphs,
        "createdAt": _now(),
    }
    record["diagnosticsHash"] = _digest(record)
    return {"ok": True, "study": study, "result": result, "diagnostics": record}


def _summary(values: list[float | None]) -> dict[str, float | None]:
    clean = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if not clean:
        return {"mean": None, "std": None, "min": None, "max": None}
    return {
        "mean": float(mean(clean)),
        "std": float(pstdev(clean)) if len(clean) > 1 else 0.0,
        "min": float(min(clean)),
        "max": float(max(clean)),
    }


def cross_validate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelDiagnosticsError("Cross-validation request must be an object.")
    rows = _rows(payload)
    try:
        study = normalize_study(payload)
        X, _, _, kept, dropped = _clean_dataset(study, rows)
    except ModelCalibrationError as exc:
        raise ModelDiagnosticsError(str(exc)) from exc

    usable = len(X)
    folds = int(payload.get("folds") or payload.get("k") or 5)
    repeats = int(payload.get("repeats") or 1)
    if folds < 2 or folds > MAX_FOLDS:
        raise ModelDiagnosticsError(f"folds must be between 2 and {MAX_FOLDS}.")
    if repeats < 1 or repeats > MAX_REPEATS:
        raise ModelDiagnosticsError(f"repeats must be between 1 and {MAX_REPEATS}.")
    min_train = max(4, len(study.get("features") or []) + 2)
    if usable < folds or usable - math.ceil(usable / folds) < min_train:
        raise ModelDiagnosticsError("Dataset is too small for the requested fold count and model complexity.")
    seed = int(payload.get("seed") if payload.get("seed") is not None else study.get("seed") or 42)

    fold_records: list[dict[str, Any]] = []
    for repeat in range(repeats):
        rng = np.random.default_rng(seed + repeat * 1009)
        indices = np.arange(usable)
        rng.shuffle(indices)
        split = np.array_split(indices, folds)
        for fold_index, test_idx in enumerate(split):
            train_idx = np.concatenate([part for j, part in enumerate(split) if j != fold_index])
            train_rows = [kept[int(i)] for i in train_idx]
            test_rows = [kept[int(i)] for i in test_idx]
            try:
                fit = calibrate({
                    "study": _study_payload(study, holdoutFraction=0.0, seed=seed + repeat * 1009 + fold_index),
                    "rows": train_rows,
                })
                fold_diag = diagnose({"study": fit["study"], "result": fit["result"], "rows": test_rows})["diagnostics"]
            except (ModelCalibrationError, ModelDiagnosticsError) as exc:
                raise ModelDiagnosticsError(f"Cross-validation failed at repeat {repeat + 1}, fold {fold_index + 1}: {exc}") from exc
            m = fold_diag["metrics"]
            fold_records.append({
                "repeat": repeat + 1,
                "fold": fold_index + 1,
                "trainingCount": len(train_rows),
                "validationCount": len(test_rows),
                "rmse": m.get("rmse"),
                "mae": m.get("mae"),
                "bias": m.get("bias"),
                "rSquared": m.get("rSquared"),
                "maxAbsoluteError": m.get("maxAbsoluteError"),
                "resultId": fit["result"].get("id"),
            })

    # Refit on all usable rows for final diagnostics and information criteria.
    full = calibrate({"study": _study_payload(study, holdoutFraction=0.0, seed=seed), "rows": kept})
    full_diag = diagnose({"study": full["study"], "result": full["result"], "rows": kept})["diagnostics"]
    aggregate = {
        metric: _summary([row.get(metric) for row in fold_records])
        for metric in ("rmse", "mae", "bias", "rSquared", "maxAbsoluteError")
    }
    cv_graph = normalize_graph({
        "kind": "line-scatter",
        "title": f"{study.get('title') or 'Scientific model'} — cross-validation RMSE",
        "description": "Validation RMSE for each deterministic fold in evaluation order.",
        "xLabel": "Fold evaluation",
        "yLabel": "RMSE",
        "series": [{
            "id": "cv-rmse",
            "label": "Validation RMSE",
            "mode": "line-scatter",
            "points": [{"x": i + 1, "y": row["rmse"]} for i, row in enumerate(fold_records)],
        }],
    })
    record = {
        "schema": CV_SCHEMA,
        "version": VERSION,
        "recordType": "cross-validation",
        "id": f"cross-validation-{_digest([study.get('id'), folds, repeats, seed, fold_records])[:16]}",
        "title": f"Cross-validation: {study.get('title') or 'Scientific model'}",
        "studyId": study.get("id"),
        "modelType": study.get("modelType"),
        "method": "repeated-k-fold" if repeats > 1 else "k-fold",
        "folds": folds,
        "repeats": repeats,
        "seed": seed,
        "foldResults": fold_records,
        "aggregate": aggregate,
        "fullDatasetFit": {
            "resultId": full["result"].get("id"),
            "metrics": full_diag.get("metrics"),
            "informationCriteria": full_diag.get("informationCriteria"),
            "parameters": full["result"].get("parameters"),
            "confidenceIntervals": full["result"].get("confidenceIntervals"),
        },
        "rowCounts": {"supplied": len(rows), "usable": usable, "dropped": dropped},
        "graphs": {
            "foldRMSE": cv_graph,
            "observedPredicted": full_diag["graphs"]["observedPredicted"],
            "residualVsFitted": full_diag["graphs"]["residualVsFitted"],
            "qqNormal": full_diag["graphs"]["qqNormal"],
        },
        "createdAt": _now(),
    }
    record["crossValidationHash"] = _digest(record)
    return {"ok": True, "study": study, "result": full["result"], "crossValidation": record, "diagnostics": full_diag}


def compare(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelDiagnosticsError("Model comparison request must be an object.")
    candidates = payload.get("candidates") or []
    if not isinstance(candidates, list) or len(candidates) < 2:
        raise ModelDiagnosticsError("At least two model candidates are required.")
    if len(candidates) > MAX_CANDIDATES:
        raise ModelDiagnosticsError(f"No more than {MAX_CANDIDATES} model candidates can be compared at once.")
    common_rows = payload.get("rows")
    folds = int(payload.get("folds") or 5)
    repeats = int(payload.get("repeats") or 1)
    seed = int(payload.get("seed") or 42)

    evaluated = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ModelDiagnosticsError(f"candidates[{index}] must be an object.")
        study_payload = candidate.get("study") if isinstance(candidate.get("study"), dict) else candidate
        rows = candidate.get("rows") if isinstance(candidate.get("rows"), list) else common_rows
        if not isinstance(rows, list) or not rows:
            raise ModelDiagnosticsError(f"Candidate {index + 1} has no dataset rows.")
        cv = cross_validate({"study": study_payload, "rows": rows, "folds": folds, "repeats": repeats, "seed": seed})
        agg = cv["crossValidation"]["aggregate"]
        criteria = cv["crossValidation"]["fullDatasetFit"]["informationCriteria"]
        result = cv["result"]
        candidate_id = str(candidate.get("id") or study_payload.get("id") or f"candidate-{index + 1}")
        title = str(candidate.get("title") or study_payload.get("title") or result.get("title") or candidate_id)
        evaluated.append({
            "candidateId": candidate_id,
            "title": title,
            "modelType": result.get("modelType"),
            "cvRMSE": agg["rmse"]["mean"],
            "cvRMSEStd": agg["rmse"]["std"],
            "cvMAE": agg["mae"]["mean"],
            "cvRSquared": agg["rSquared"]["mean"],
            "aic": criteria.get("aic"),
            "aicc": criteria.get("aicc"),
            "bic": criteria.get("bic"),
            "parameterCount": len(result.get("parameters") or {}),
            "resultId": result.get("id"),
            "crossValidationId": cv["crossValidation"].get("id"),
        })

    evaluated.sort(key=lambda row: (
        float("inf") if row["cvRMSE"] is None else row["cvRMSE"],
        float("inf") if row["aicc"] is None else row["aicc"],
        float("inf") if row["bic"] is None else row["bic"],
    ))
    finite_aicc = [row["aicc"] for row in evaluated if row["aicc"] is not None and math.isfinite(float(row["aicc"]))]
    min_aicc = min(finite_aicc) if finite_aicc else None
    weights = []
    if min_aicc is not None:
        raw = [math.exp(-0.5 * (float(row["aicc"]) - min_aicc)) if row["aicc"] is not None else 0.0 for row in evaluated]
        denom = sum(raw) or 1.0
        weights = [v / denom for v in raw]
    else:
        weights = [None] * len(evaluated)
    for rank, (row, weight) in enumerate(zip(evaluated, weights), start=1):
        row["rank"] = rank
        row["deltaAICc"] = float(row["aicc"] - min_aicc) if min_aicc is not None and row["aicc"] is not None else None
        row["akaikeWeight"] = float(weight) if weight is not None else None

    graph = normalize_graph({
        "kind": "horizontal-bars",
        "title": str(payload.get("title") or "Scientific model comparison") + " — cross-validation RMSE",
        "description": "Lower cross-validation RMSE indicates stronger out-of-sample predictive performance under the configured folds.",
        "xLabel": "Cross-validation RMSE",
        "yLabel": "Candidate",
        "bars": [{"label": row["title"], "value": row["cvRMSE"]} for row in evaluated if row["cvRMSE"] is not None],
        "series": [],
    })
    record = {
        "schema": COMPARISON_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-model-comparison",
        "id": f"scientific-model-comparison-{_digest([evaluated, folds, repeats, seed])[:16]}",
        "title": str(payload.get("title") or "Scientific model comparison"),
        "method": "repeated-k-fold" if repeats > 1 else "k-fold",
        "folds": folds,
        "repeats": repeats,
        "seed": seed,
        "ranking": evaluated,
        "recommendedCandidateId": evaluated[0]["candidateId"],
        "selectionPolicy": "lowest mean cross-validation RMSE; AICc then BIC as tie breakers",
        "graph": graph,
        "createdAt": _now(),
    }
    record["comparisonHash"] = _digest(record)
    return {"ok": True, "comparison": record}
