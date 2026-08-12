from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

VERSION = "0.41.0"
MODEL_SCHEMA = "sc-lab-model-studio-model/0.41.0"
GRAPH_SCHEMA = "sc-lab-scientific-graph/0.41.0"
RESULT_SCHEMA = "sc-lab-model-studio-result/0.41.0"
BUNDLE_SCHEMA = "sc-lab-model-studio-bundle/0.41.0"

MODEL_FAMILIES = {
    "linear-multivariate": {"label": "Linear multivariate", "execution": "model-calibration-v0302"},
    "polynomial-univariate": {"label": "Polynomial univariate", "execution": "model-calibration-v0302"},
    "exponential-univariate": {"label": "Exponential univariate", "execution": "model-calibration-v0302"},
    "logistic-univariate": {"label": "Logistic univariate", "execution": "model-calibration-v0302"},
    "registered-model": {"label": "Registered scientific model", "execution": "model-registry-v0340"},
    "declarative-expression": {"label": "Declarative expression (definition only)", "execution": "v0.42.0-planned"},
}
GRAPH_TYPES = {"line", "scatter", "line-scatter", "histogram", "horizontal-bars", "heatmap"}
ALLOWED_PARAMETER_ROLES = {"estimated", "fixed", "initial", "derived"}
ALLOWED_BINDING_ROLES = {"feature", "response", "weight", "group", "time", "identifier"}
SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")


class ModelStudioError(ValueError):
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
        raise ModelStudioError(f"{name} is required.")
    if len(text) > max_len:
        raise ModelStudioError(f"{name} exceeds {max_len} characters.")
    return text


def _symbol(value: Any, name: str) -> str:
    text = _text(value, name, 64, True)
    if not SYMBOL_RE.fullmatch(text):
        raise ModelStudioError(f"{name} must be a safe scientific symbol.")
    return text


def _finite(value: Any, name: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ModelStudioError(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise ModelStudioError(f"{name} must be finite.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "modelSchema": MODEL_SCHEMA,
        "graphSchema": GRAPH_SCHEMA,
        "resultSchema": RESULT_SCHEMA,
        "bundleSchema": BUNDLE_SCHEMA,
        "modelFamilies": [{"id": key, **value} for key, value in MODEL_FAMILIES.items()],
        "graphTypes": sorted(GRAPH_TYPES),
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryFormulaExecution": False,
            "declarativeExpressionDefinition": True,
            "registeredModelExecution": True,
            "browserLocalDrafts": True,
            "provenanceRequired": True,
            "unitsMetadata": True,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "model-studio-foundation-ready",
        "version": VERSION,
        "modelFamilies": len(MODEL_FAMILIES),
        "graphTypes": len(GRAPH_TYPES),
        "sharedVisualizationContract": True,
        "arbitraryCode": False,
        "arbitraryFormulaExecution": False,
    }


def normalize_model(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelStudioError("Model definition must be an object.")
    src = deepcopy(payload)
    family = _text(src.get("family") or src.get("modelFamily"), "family", 80, True)
    if family not in MODEL_FAMILIES:
        raise ModelStudioError("Unknown registered model family.")

    variables = []
    seen = set()
    for index, row in enumerate(src.get("variables") or []):
        if not isinstance(row, dict):
            raise ModelStudioError("variables must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"variables[{index}].symbol")
        if symbol in seen:
            raise ModelStudioError(f"Duplicate variable symbol: {symbol}.")
        seen.add(symbol)
        variables.append({
            "symbol": symbol,
            "label": _text(row.get("label") or symbol, "variable label", 120, True),
            "unit": _text(row.get("unit"), "variable unit", 80),
            "role": _text(row.get("role") or "input", "variable role", 40),
        })

    parameters = []
    p_seen = set()
    for index, row in enumerate(src.get("parameters") or []):
        if not isinstance(row, dict):
            raise ModelStudioError("parameters must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"parameters[{index}].symbol")
        if symbol in p_seen:
            raise ModelStudioError(f"Duplicate parameter symbol: {symbol}.")
        p_seen.add(symbol)
        role = _text(row.get("role") or "estimated", "parameter role", 40)
        if role not in ALLOWED_PARAMETER_ROLES:
            raise ModelStudioError(f"Unsupported parameter role: {role}.")
        lower = _finite((row.get("bounds") or {}).get("lower") if isinstance(row.get("bounds"), dict) else row.get("lower"), f"{symbol} lower bound")
        upper = _finite((row.get("bounds") or {}).get("upper") if isinstance(row.get("bounds"), dict) else row.get("upper"), f"{symbol} upper bound")
        if lower is not None and upper is not None and lower > upper:
            raise ModelStudioError(f"Lower bound exceeds upper bound for {symbol}.")
        value = _finite(row.get("value"), f"{symbol} value")
        parameters.append({
            "symbol": symbol,
            "label": _text(row.get("label") or symbol, "parameter label", 120, True),
            "unit": _text(row.get("unit"), "parameter unit", 80),
            "role": role,
            "value": value,
            "bounds": {"lower": lower, "upper": upper},
        })

    bindings = []
    for index, row in enumerate(src.get("datasetBindings") or src.get("bindings") or []):
        if not isinstance(row, dict):
            raise ModelStudioError("datasetBindings must contain objects.")
        role = _text(row.get("role"), "binding role", 40, True)
        if role not in ALLOWED_BINDING_ROLES:
            raise ModelStudioError(f"Unsupported dataset binding role: {role}.")
        bindings.append({
            "column": _text(row.get("column"), f"datasetBindings[{index}].column", 128, True),
            "symbol": _symbol(row.get("symbol"), f"datasetBindings[{index}].symbol"),
            "role": role,
            "unit": _text(row.get("unit"), "binding unit", 80),
        })

    created_at = _text(src.get("createdAt") or _now(), "createdAt", 80, True)
    normalized = {
        "schema": MODEL_SCHEMA,
        "version": VERSION,
        "recordType": "model-studio-model",
        "id": _text(src.get("id") or f"model-{_digest(src)[:16]}", "id", 120, True),
        "title": _text(src.get("title") or "Untitled scientific model", "title", 180, True),
        "status": _text(src.get("status") or "draft", "status", 32, True),
        "family": family,
        "definition": {
            "equation": _text((src.get("definition") or {}).get("equation") if isinstance(src.get("definition"), dict) else src.get("equation"), "equation", 1000),
            "registeredModelId": _text((src.get("definition") or {}).get("registeredModelId") if isinstance(src.get("definition"), dict) else src.get("registeredModelId"), "registeredModelId", 160),
            "executionAdapter": MODEL_FAMILIES[family]["execution"],
            "executable": family != "declarative-expression",
        },
        "variables": variables,
        "parameters": parameters,
        "dataset": {
            "datasetId": _text((src.get("dataset") or {}).get("datasetId") if isinstance(src.get("dataset"), dict) else src.get("datasetId"), "datasetId", 160),
            "bindings": bindings,
        },
        "assumptions": [_text(v, "assumption", 500, True) for v in (src.get("assumptions") or [])][:50],
        "limitations": [_text(v, "limitation", 500, True) for v in (src.get("limitations") or [])][:50],
        "provenance": {
            "projectId": _text((src.get("provenance") or {}).get("projectId") if isinstance(src.get("provenance"), dict) else src.get("projectId"), "projectId", 160),
            "sourceIds": [_text(v, "sourceId", 160, True) for v in ((src.get("provenance") or {}).get("sourceIds") if isinstance(src.get("provenance"), dict) else [])][:100],
            "createdAt": created_at,
            "updatedAt": _now(),
            "createdBy": _text((src.get("provenance") or {}).get("createdBy") if isinstance(src.get("provenance"), dict) else "", "createdBy", 160),
        },
    }
    hashable = deepcopy(normalized)
    hashable.pop("modelHash", None)
    normalized["modelHash"] = _digest(hashable)
    return normalized


def normalize_graph(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelStudioError("Graph specification must be an object.")
    kind = _text(payload.get("kind") or payload.get("type") or "scatter", "graph kind", 40, True)
    if kind not in GRAPH_TYPES:
        raise ModelStudioError("Unsupported graph kind.")
    series = []
    for index, row in enumerate(payload.get("series") or []):
        if not isinstance(row, dict):
            raise ModelStudioError("series must contain objects.")
        points = []
        for p_index, point in enumerate(row.get("points") or []):
            if not isinstance(point, dict):
                raise ModelStudioError("series points must be objects.")
            points.append({"x": _finite(point.get("x"), f"series[{index}].points[{p_index}].x"), "y": _finite(point.get("y"), f"series[{index}].points[{p_index}].y")})
        series.append({"id": _text(row.get("id") or f"series-{index+1}", "series id", 80, True), "label": _text(row.get("label") or f"Series {index+1}", "series label", 120, True), "mode": _text(row.get("mode") or ("scatter" if kind == "scatter" else "line"), "series mode", 30, True), "points": points})
    graph = {
        "schema": GRAPH_SCHEMA,
        "version": VERSION,
        "kind": kind,
        "title": _text(payload.get("title") or "Scientific graph", "graph title", 180, True),
        "description": _text(payload.get("description") or "Scientific visualization generated by Model Studio.", "graph description", 600, True),
        "xLabel": _text(payload.get("xLabel") or "X", "xLabel", 120),
        "yLabel": _text(payload.get("yLabel") or "Y", "yLabel", 120),
        "series": series,
        "annotations": deepcopy(payload.get("annotations") or [])[:100],
        "accessibility": {"role": "img", "tabularFallback": True},
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": False, "pan": False},
        "exports": ["svg", "png", "csv", "json"],
    }
    graph["graphHash"] = _digest(graph)
    return graph


def build_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelStudioError("Model Studio bundle request must be an object.")
    model = normalize_model(payload.get("model") or payload)
    graphs = [normalize_graph(row) for row in (payload.get("graphs") or [])]
    result = payload.get("result") or None
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "version": VERSION,
        "createdAt": _now(),
        "model": model,
        "graphs": graphs,
        "result": result,
        "handoffTargets": ["model-calibration", "design-studies", "ensemble-uncertainty", "model-registry", "workbench"],
        "boundaries": {"arbitraryCode": False, "arbitraryFormulaExecution": False},
    }
    bundle["bundleHash"] = _digest(bundle)
    return bundle
