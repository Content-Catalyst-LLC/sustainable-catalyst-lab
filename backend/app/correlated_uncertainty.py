from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np
from scipy import stats

from .probabilistic_analysis import (
    ProbabilisticAnalysisError,
    _cdf_graph,
    _curve_graph,
    _digest,
    _evaluate_matrix,
    _histogram_graph,
    _sensitivity,
    _sensitivity_graph,
    _summary,
    _transform,
    _unit_design,
    normalize_study as normalize_independent_study,
)

VERSION = "0.53.0"
STUDY_SCHEMA = "sc-lab-dependent-probabilistic-study/0.53.0"
RESULT_SCHEMA = "sc-lab-dependent-probabilistic-analysis/0.53.0"
DEPENDENCY_SCHEMA = "sc-lab-probabilistic-dependency/0.53.0"
GRAPH_SCHEMA = "sc-lab-scientific-graph/0.46.0"
DEPENDENCY_METHODS = {"independent", "gaussian-copula"}
MATRIX_TYPES = {"correlation", "covariance"}
MAX_DEPENDENCY_ROWS = 50000


class CorrelatedUncertaintyError(ProbabilisticAnalysisError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _finite_matrix(raw: Any, n: int, name: str) -> np.ndarray:
    if not isinstance(raw, list) or len(raw) != n or any(not isinstance(row, list) or len(row) != n for row in raw):
        raise CorrelatedUncertaintyError(f"{name} must be a {n}x{n} numeric matrix aligned to uncertainInputs order.")
    try:
        matrix = np.asarray(raw, dtype=float)
    except (TypeError, ValueError) as exc:
        raise CorrelatedUncertaintyError(f"{name} must contain only numeric values.") from exc
    if not np.all(np.isfinite(matrix)):
        raise CorrelatedUncertaintyError(f"{name} must contain only finite values.")
    return matrix


def _validate_symmetric(matrix: np.ndarray, name: str) -> None:
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-8):
        raise CorrelatedUncertaintyError(f"{name} must be symmetric.")


def _nearest_psd_diagnostics(correlation: np.ndarray) -> dict[str, Any]:
    eig = np.linalg.eigvalsh(correlation)
    positive = eig[eig > 1e-12]
    condition = float(np.max(positive) / np.min(positive)) if positive.size else math.inf
    return {
        "minimumEigenvalue": float(np.min(eig)),
        "maximumEigenvalue": float(np.max(eig)),
        "conditionNumber": condition,
        "positiveSemidefinite": bool(np.min(eig) >= -1e-8),
        "rank": int(np.linalg.matrix_rank(correlation, tol=1e-10)),
    }


def _normalize_dependency(raw: Any, symbols: list[str], design_method: str) -> dict[str, Any]:
    n = len(symbols)
    if raw in (None, {}, ""):
        return {
            "schema": DEPENDENCY_SCHEMA,
            "version": VERSION,
            "method": "independent",
            "symbols": symbols,
            "matrixType": "correlation",
            "matrix": np.eye(n).tolist(),
            "latentCorrelation": np.eye(n).tolist(),
            "diagnostics": _nearest_psd_diagnostics(np.eye(n)),
        }
    if not isinstance(raw, dict):
        raise CorrelatedUncertaintyError("dependency must be an object.")
    method = str(raw.get("method") or "independent").strip().lower()
    if method not in DEPENDENCY_METHODS:
        raise CorrelatedUncertaintyError("dependency.method must be independent or gaussian-copula.")
    if method == "independent":
        return {
            "schema": DEPENDENCY_SCHEMA,
            "version": VERSION,
            "method": method,
            "symbols": symbols,
            "matrixType": "correlation",
            "matrix": np.eye(n).tolist(),
            "latentCorrelation": np.eye(n).tolist(),
            "diagnostics": _nearest_psd_diagnostics(np.eye(n)),
        }
    if design_method == "saltelli-sobol":
        raise CorrelatedUncertaintyError(
            "Saltelli–Sobol sensitivity is not available for dependent inputs because its standard variance decomposition assumes independence. Use Monte Carlo, Latin hypercube, or Sobol sequence sampling."
        )
    matrix_type = str(raw.get("matrixType") or "correlation").strip().lower()
    if matrix_type not in MATRIX_TYPES:
        raise CorrelatedUncertaintyError("dependency.matrixType must be correlation or covariance.")
    declared_symbols = raw.get("symbols") or symbols
    if declared_symbols != symbols:
        raise CorrelatedUncertaintyError("dependency.symbols must exactly match uncertainInputs order.")
    matrix = _finite_matrix(raw.get("matrix"), n, "dependency.matrix")
    _validate_symmetric(matrix, "dependency.matrix")
    if matrix_type == "correlation":
        if not np.allclose(np.diag(matrix), np.ones(n), rtol=0.0, atol=1e-8):
            raise CorrelatedUncertaintyError("Correlation-matrix diagonal entries must all equal 1.")
        if np.max(np.abs(matrix)) > 1 + 1e-8:
            raise CorrelatedUncertaintyError("Correlation coefficients must lie between -1 and 1.")
        correlation = matrix.copy()
    else:
        diagonal = np.diag(matrix)
        if np.any(diagonal <= 0):
            raise CorrelatedUncertaintyError("Covariance-matrix diagonal entries must be positive.")
        scale = np.sqrt(diagonal)
        correlation = matrix / np.outer(scale, scale)
        np.fill_diagonal(correlation, 1.0)
    diagnostics = _nearest_psd_diagnostics(correlation)
    if not diagnostics["positiveSemidefinite"]:
        raise CorrelatedUncertaintyError(
            f"Dependency matrix must be positive semidefinite; minimum eigenvalue is {diagnostics['minimumEigenvalue']:.6g}."
        )
    return {
        "schema": DEPENDENCY_SCHEMA,
        "version": VERSION,
        "method": method,
        "symbols": symbols,
        "matrixType": matrix_type,
        "matrix": matrix.tolist(),
        "latentCorrelation": correlation.tolist(),
        "diagnostics": diagnostics,
        "source": str(raw.get("source") or "operator-supplied").strip()[:240],
        "notes": str(raw.get("notes") or "").strip()[:1000],
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "studySchema": STUDY_SCHEMA,
        "resultSchema": RESULT_SCHEMA,
        "dependencySchema": DEPENDENCY_SCHEMA,
        "dependencyMethods": sorted(DEPENDENCY_METHODS),
        "matrixTypes": sorted(MATRIX_TYPES),
        "marginalDistributions": ["normal", "uniform", "lognormal", "triangular"],
        "samplingDesigns": ["monte-carlo", "latin-hypercube", "sobol"],
        "dependentSaltelliSobol": False,
        "empiricalDependencyEstimation": True,
        "automaticCausalInterpretation": False,
        "automaticDependencyInference": False,
        "arbitraryCode": False,
        "limits": {"uncertainInputs": 32, "dependencyRows": MAX_DEPENDENCY_ROWS},
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "correlated-uncertainty-ready",
        "version": VERSION,
        "correlationMatrices": True,
        "covarianceMatrices": True,
        "gaussianCopula": True,
        "marginalDistributionPreservation": True,
        "empiricalPearsonSpearmanDiagnostics": True,
        "empiricalDependencyEstimation": True,
        "dependencyHeatmap": True,
        "graphStudioHandoff": True,
        "reproduciblePackageCompatible": True,
        "dependentSaltelliSobol": False,
        "automaticDependencyInference": False,
        "automaticCausalInterpretation": False,
        "arbitraryCode": False,
    }


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        base = normalize_independent_study(payload)
    except ProbabilisticAnalysisError as exc:
        raise CorrelatedUncertaintyError(str(exc), getattr(exc, "status_code", 400)) from exc
    symbols = [row["symbol"] for row in base["uncertainInputs"]]
    dependency = _normalize_dependency(payload.get("dependency"), symbols, base["design"]["method"])
    study = deepcopy(base)
    study["schema"] = STUDY_SCHEMA
    study["version"] = VERSION
    study["dependency"] = dependency
    study["governance"] = {
        "independentInputs": dependency["method"] == "independent",
        "dependentInputs": dependency["method"] != "independent",
        "dependencyMethod": dependency["method"],
        "safeDeclarativeExecution": True,
        "arbitraryCode": False,
        "automaticDependencyInference": False,
        "automaticCausalInterpretation": False,
    }
    study["createdAt"] = _now()
    study["studyHash"] = _digest({k: v for k, v in study.items() if k not in {"createdAt", "studyHash"}})
    return study


def _correlation_sqrt(correlation: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(correlation)
    values = np.clip(values, 0.0, None)
    return vectors @ np.diag(np.sqrt(values)) @ vectors.T


def _sample_matrix(study: dict[str, Any]) -> np.ndarray:
    specs = study["uncertainInputs"]
    samples = int(study["design"]["samples"])
    method = study["design"]["method"]
    seed = int(study["design"]["seed"])
    d = len(specs)
    unit = _unit_design(method, samples, d, seed)
    dependency = study["dependency"]
    if dependency["method"] == "gaussian-copula":
        z = stats.norm.ppf(np.clip(unit, 1e-12, 1 - 1e-12))
        root = _correlation_sqrt(np.asarray(dependency["latentCorrelation"], dtype=float))
        unit = stats.norm.cdf(z @ root.T)
    columns = [_transform(unit[:, i], spec) for i, spec in enumerate(specs)]
    return np.column_stack(columns)


def _matrix_records(matrix: np.ndarray, symbols: list[str]) -> list[dict[str, Any]]:
    return [
        {"row": symbols[i], "column": symbols[j], "value": float(matrix[i, j])}
        for i in range(len(symbols)) for j in range(len(symbols))
    ]


def _dependency_diagnostics(study: dict[str, Any], matrix: np.ndarray) -> dict[str, Any]:
    symbols = [row["symbol"] for row in study["uncertainInputs"]]
    if len(symbols) == 1:
        pearson = spearman = np.ones((1, 1), dtype=float)
    else:
        pearson = np.corrcoef(matrix, rowvar=False)
        ranked = np.column_stack([stats.rankdata(matrix[:, i], method="average") for i in range(matrix.shape[1])])
        spearman = np.corrcoef(ranked, rowvar=False)
    target = np.asarray(study["dependency"]["latentCorrelation"], dtype=float)
    return {
        "symbols": symbols,
        "targetLatentCorrelation": target.tolist(),
        "empiricalPearson": pearson.tolist(),
        "empiricalSpearman": spearman.tolist(),
        "maximumAbsolutePearsonDeviationFromTarget": float(np.max(np.abs(pearson - target))),
        "targetDiagnostics": study["dependency"]["diagnostics"],
        "interpretation": "Empirical dependence is a sampling diagnostic. Association does not establish causal dependence.",
    }


def _dependency_heatmap(study: dict[str, Any], diagnostics: dict[str, Any]) -> dict[str, Any]:
    symbols = diagnostics["symbols"]
    matrix = np.asarray(diagnostics["empiricalSpearman"], dtype=float)
    cells = [
        {"xIndex": j, "yIndex": i, "x": j, "y": i, "z": float(matrix[i, j]), "row": symbols[i], "column": symbols[j]}
        for i in range(len(symbols)) for j in range(len(symbols))
    ]
    return {
        "schema": GRAPH_SCHEMA,
        "version": "0.46.0",
        "kind": "heatmap",
        "title": f"{study['title']} — sampled dependency",
        "description": "Empirical Spearman dependence among sampled uncertain inputs.",
        "xLabel": "Uncertain input index",
        "yLabel": "Uncertain input index",
        "xValues": list(range(len(symbols))),
        "yValues": list(range(len(symbols))),
        "cells": cells,
        "domain": {"x": [0, max(0, len(symbols) - 1)], "y": [0, max(0, len(symbols) - 1)], "z": [-1, 1]},
        "table": {"columns": ["row", "column", "correlation"], "rows": _matrix_records(matrix, symbols)},
        "publication": {
            "caption": "Empirical rank-dependence matrix for sampled uncertain inputs.",
            "source": "Sustainable Catalyst Lab correlated uncertainty",
            "method": study["dependency"]["method"],
            "notes": "Dependence is modeled explicitly and does not imply causality.",
            "aspectRatio": "1:1", "showGrid": True, "showLegend": False,
        },
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": False},
        "exports": ["svg", "png", "csv", "json"],
    }


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload.get("study") if isinstance(payload, dict) and isinstance(payload.get("study"), dict) else payload)
    matrix = _sample_matrix(study)
    outputs = _evaluate_matrix(study, matrix)
    summary = _summary(outputs, study["analysis"]["confidence"], study["analysis"]["thresholds"])
    sensitivity = _sensitivity(study, matrix, outputs, None)
    if study["dependency"]["method"] != "independent":
        sensitivity["interpretation"] = "Sensitivity coefficients reflect association under dependent inputs; they are not an independent-input variance decomposition or a causal attribution."
        sensitivity["dependentInputs"] = True
    diagnostics = _dependency_diagnostics(study, matrix)
    output_symbol = study["model"]["definition"].get("outputSymbol") or "output"
    output_unit = next((row.get("unit") or "" for row in study["model"].get("variables", []) if row["symbol"] == output_symbol), "")
    graphs = {
        "distribution": _histogram_graph(study["title"], output_unit, outputs, summary),
        "cdf": _cdf_graph(study["title"], output_unit, outputs),
        "sensitivity": _sensitivity_graph(study["title"], sensitivity),
        "dependency": _dependency_heatmap(study, diagnostics),
    }
    # Correct inherited publication notes when dependence is explicit.
    for graph in graphs.values():
        publication = graph.get("publication") if isinstance(graph, dict) else None
        if isinstance(publication, dict):
            publication["notes"] = (
                "Uncertain inputs were propagated with an explicit Gaussian-copula dependency model; association does not imply causality."
                if study["dependency"]["method"] != "independent"
                else "Uncertain inputs were propagated independently."
            )
    curve_records = None
    if study.get("curve"):
        graphs["uncertaintyBand"], curve_records = _curve_graph(study, matrix)
        graphs["uncertaintyBand"]["publication"]["notes"] = (
            "Ribbon reflects propagated marginal uncertainty and explicit Gaussian-copula dependence."
            if study["dependency"]["method"] != "independent"
            else "Ribbon reflects propagated input uncertainty under independent-input assumptions."
        )
    result = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "study": study,
        "summary": summary,
        "sensitivity": sensitivity,
        "dependencyDiagnostics": diagnostics,
        "graphs": graphs,
        "curve": curve_records,
        "samplePreview": [
            {**{study["uncertainInputs"][j]["symbol"]: float(matrix[i, j]) for j in range(len(study["uncertainInputs"]))}, output_symbol: float(outputs[i])}
            for i in range(min(40, len(outputs)))
        ],
        "governance": deepcopy(study["governance"]),
        "createdAt": _now(),
    }
    result["analysisHash"] = _digest({k: v for k, v in result.items() if k not in {"createdAt", "analysisHash"}})
    return {"ok": True, "result": result}


def estimate_dependency(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CorrelatedUncertaintyError("Dependency estimation payload must be an object.")
    symbols = payload.get("symbols") or []
    rows = payload.get("rows") or []
    method = str(payload.get("method") or "gaussian-rank-correlation").strip().lower()
    if method not in {"pearson", "spearman", "gaussian-rank-correlation"}:
        raise CorrelatedUncertaintyError("Dependency estimation method must be pearson, spearman, or gaussian-rank-correlation.")
    if not isinstance(symbols, list) or not 2 <= len(symbols) <= 32 or len(set(symbols)) != len(symbols):
        raise CorrelatedUncertaintyError("symbols must contain 2 to 32 unique input names.")
    if not isinstance(rows, list) or len(rows) < 8 or len(rows) > MAX_DEPENDENCY_ROWS:
        raise CorrelatedUncertaintyError(f"rows must contain between 8 and {MAX_DEPENDENCY_ROWS} complete observations.")
    data = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise CorrelatedUncertaintyError(f"rows[{i}] must be an object.")
        try:
            values = [float(row[symbol]) for symbol in symbols]
        except (KeyError, TypeError, ValueError) as exc:
            raise CorrelatedUncertaintyError(f"rows[{i}] must contain finite numeric values for every requested symbol.") from exc
        if not np.all(np.isfinite(values)):
            raise CorrelatedUncertaintyError(f"rows[{i}] must contain finite numeric values.")
        data.append(values)
    x = np.asarray(data, dtype=float)
    if method == "pearson":
        corr = np.corrcoef(x, rowvar=False)
    elif method == "spearman":
        ranks = np.column_stack([stats.rankdata(x[:, i], method="average") for i in range(x.shape[1])])
        corr = np.corrcoef(ranks, rowvar=False)
    else:
        n = x.shape[0]
        uniforms = np.column_stack([(stats.rankdata(x[:, i], method="average") - 0.5) / n for i in range(x.shape[1])])
        latent = stats.norm.ppf(np.clip(uniforms, 1e-9, 1 - 1e-9))
        corr = np.corrcoef(latent, rowvar=False)
    np.fill_diagonal(corr, 1.0)
    diagnostics = _nearest_psd_diagnostics(corr)
    return {
        "ok": True,
        "dependency": {
            "schema": DEPENDENCY_SCHEMA,
            "version": VERSION,
            "method": "gaussian-copula",
            "symbols": symbols,
            "matrixType": "correlation",
            "matrix": corr.tolist(),
            "source": f"empirical-{method}",
            "notes": f"Estimated from {len(rows)} complete observations; review before use.",
        },
        "estimation": {
            "method": method,
            "rows": len(rows),
            "diagnostics": diagnostics,
            "governance": {"automaticUse": False, "requiresOperatorReview": True, "causalInterpretation": False},
        },
    }
