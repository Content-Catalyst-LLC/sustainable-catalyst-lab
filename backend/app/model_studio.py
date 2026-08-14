from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

from .equation_builder import EquationBuilderError, catalog as equation_catalog, evaluate_rows as evaluate_equation_rows, validate_definition as validate_equation_definition

VERSION = "0.45.0"
MODEL_SCHEMA = "sc-lab-model-studio-model/0.45.0"
GRAPH_SCHEMA = "sc-lab-scientific-graph/0.45.0"
RESULT_SCHEMA = "sc-lab-model-studio-result/0.45.0"
BUNDLE_SCHEMA = "sc-lab-model-studio-bundle/0.45.0"

MODEL_FAMILIES = {
    "linear-multivariate": {"label": "Linear multivariate", "execution": "model-calibration-v0302"},
    "polynomial-univariate": {"label": "Polynomial univariate", "execution": "model-calibration-v0302"},
    "exponential-univariate": {"label": "Exponential univariate", "execution": "model-calibration-v0302"},
    "logistic-univariate": {"label": "Logistic univariate", "execution": "model-calibration-v0302"},
    "registered-model": {"label": "Registered scientific model", "execution": "model-registry-v0340"},
    "declarative-expression": {"label": "Declarative scientific expression", "execution": "equation-builder-v0420"},
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
        "visualizationEngine": {
            "version": "0.44.0",
            "contractVersion": "0.45.0",
            "interactions": ["tooltip", "crosshair", "zoom", "pan", "series-toggle", "keyboard-navigation"],
            "uncertainty": ["error-bars", "confidence-ribbons"],
            "publicationExports": ["svg", "png", "csv", "json"],
            "aspectRatios": ["16:9", "3:2", "4:3", "1:1"],
        },
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryFormulaExecution": False,
            "safeDeclarativeExpressionExecution": True,
            "declarativeExpressionDefinition": True,
            "registeredModelExecution": True,
            "browserLocalDrafts": True,
            "provenanceRequired": True,
            "unitsMetadata": True,
            "dynamicSystems": True,
            "safeDeclarativeDerivativeExpressions": True,
            "boundedDynamicParameterEstimation": True,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "interactive-visualization-ready",
        "version": VERSION,
        "modelFamilies": len(MODEL_FAMILIES),
        "graphTypes": len(GRAPH_TYPES),
        "sharedVisualizationContract": True,
        "interactiveVisualization": True,
        "publicationGraphics": True,
        "uncertaintyRendering": True,
        "dynamicSystems": True,
        "odeParameterEstimation": True,
        "arbitraryCode": False,
        "arbitraryFormulaExecution": False,
        "safeDeclarativeExpressionExecution": True,
        "equationBuilder": equation_catalog(),
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

    constants = []
    c_seen = set()
    for index, row in enumerate(src.get("constants") or []):
        if not isinstance(row, dict):
            raise ModelStudioError("constants must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"constants[{index}].symbol")
        if symbol in c_seen or symbol in p_seen or symbol in seen:
            raise ModelStudioError(f"Duplicate scientific symbol: {symbol}.")
        c_seen.add(symbol)
        value = _finite(row.get("value"), f"{symbol} constant value")
        if value is None:
            raise ModelStudioError(f"Constant {symbol} requires a numeric value.")
        constants.append({
            "symbol": symbol,
            "label": _text(row.get("label") or symbol, "constant label", 120, True),
            "unit": _text(row.get("unit"), "constant unit", 80),
            "value": value,
        })

    initial_conditions = []
    for index, row in enumerate(src.get("initialConditions") or []):
        if not isinstance(row, dict):
            raise ModelStudioError("initialConditions must contain objects.")
        symbol = _symbol(row.get("symbol"), f"initialConditions[{index}].symbol")
        value = _finite(row.get("value"), f"initial condition {symbol}")
        if value is None:
            raise ModelStudioError(f"Initial condition {symbol} requires a numeric value.")
        initial_conditions.append({"symbol": symbol, "value": value, "unit": _text(row.get("unit"), "initial condition unit", 80)})

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
            "equation": _text((src.get("definition") or {}).get("equation") if isinstance(src.get("definition"), dict) else src.get("equation"), "equation", 2000),
            "registeredModelId": _text((src.get("definition") or {}).get("registeredModelId") if isinstance(src.get("definition"), dict) else src.get("registeredModelId"), "registeredModelId", 160),
            "executionAdapter": MODEL_FAMILIES[family]["execution"],
            "executable": True,
        },
        "variables": variables,
        "parameters": parameters,
        "constants": constants,
        "initialConditions": initial_conditions,
        "dataset": {
            "datasetId": _text((src.get("dataset") or {}).get("datasetId") if isinstance(src.get("dataset"), dict) else src.get("datasetId"), "datasetId", 160),
            "bindings": bindings,
        },
        "assumptions": [_text(v, "assumption", 500, True) for v in (src.get("assumptions") or [])][:50],
        "limitations": [_text(v, "limitation", 500, True) for v in (src.get("limitations") or [])][:50],
        "provenance": {
            "projectId": _text((src.get("provenance") or {}).get("projectId") if isinstance(src.get("provenance"), dict) else src.get("projectId"), "projectId", 160),
            "sourceIds": [_text(v, "sourceId", 160, True) for v in (((src.get("provenance") or {}).get("sourceIds") if isinstance(src.get("provenance"), dict) else []) or [])][:100],
            "createdAt": created_at,
            "updatedAt": _now(),
            "createdBy": _text((src.get("provenance") or {}).get("createdBy") if isinstance(src.get("provenance"), dict) else "", "createdBy", 160),
        },
    }
    if family == "declarative-expression":
        if not normalized["definition"]["equation"]:
            raise ModelStudioError("Declarative scientific models require an equation.")
        declared = variables + parameters + constants
        response_symbols = [row["symbol"] for row in variables if row.get("role") == "response"]
        output_symbol = response_symbols[0] if response_symbols else None
        try:
            equation_validation = validate_equation_definition({
                "equation": normalized["definition"]["equation"],
                "variables": variables,
                "parameters": parameters,
                "constants": constants,
                "outputSymbol": output_symbol,
            })
        except EquationBuilderError as exc:
            raise ModelStudioError(str(exc)) from exc
        normalized["definition"]["equation"] = equation_validation["equation"]
        normalized["definition"]["outputSymbol"] = equation_validation["outputSymbol"]
        normalized["definition"]["referencedSymbols"] = equation_validation["referencedSymbols"]
        normalized["definition"]["functions"] = equation_validation["functions"]
        normalized["definition"]["safeExecution"] = True
    else:
        normalized["definition"]["safeExecution"] = False

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
            normalized_point = {
                "x": _finite(point.get("x"), f"series[{index}].points[{p_index}].x"),
                "y": _finite(point.get("y"), f"series[{index}].points[{p_index}].y"),
            }
            for key in ("xLow", "xHigh", "yLow", "yHigh"):
                value = _finite(point.get(key), f"series[{index}].points[{p_index}].{key}")
                if value is not None:
                    normalized_point[key] = value
            label = _text(point.get("label"), f"series[{index}].points[{p_index}].label", 160)
            if label:
                normalized_point["label"] = label
            points.append(normalized_point)
        series.append({
            "id": _text(row.get("id") or f"series-{index+1}", "series id", 80, True),
            "label": _text(row.get("label") or f"Series {index+1}", "series label", 120, True),
            "mode": _text(row.get("mode") or ("scatter" if kind == "scatter" else "line"), "series mode", 30, True),
            "points": points,
        })
    publication_payload = payload.get("publication") if isinstance(payload.get("publication"), dict) else {}
    aspect = _text(publication_payload.get("aspectRatio") or "16:9", "publication aspectRatio", 16, True)
    if aspect not in {"16:9", "4:3", "3:2", "1:1"}:
        raise ModelStudioError("Unsupported publication aspect ratio.")
    interaction_payload = payload.get("interaction") if isinstance(payload.get("interaction"), dict) else {}
    graph = {
        "schema": GRAPH_SCHEMA,
        "version": VERSION,
        "kind": kind,
        "title": _text(payload.get("title") or "Scientific graph", "graph title", 180, True),
        "description": _text(payload.get("description") or "Scientific visualization generated by Model Studio.", "graph description", 600, True),
        "xLabel": _text(payload.get("xLabel") or "X", "xLabel", 120),
        "yLabel": _text(payload.get("yLabel") or "Y", "yLabel", 120),
        "series": series,
        "bars": [
            {"label": _text(row.get("label") or f"Bar {index+1}", f"bars[{index}].label", 120, True), "value": _finite(row.get("value"), f"bars[{index}].value")}
            for index, row in enumerate(payload.get("bars") or []) if isinstance(row, dict)
        ][:200],
        "annotations": deepcopy(payload.get("annotations") or [])[:100],
        "accessibility": {"role": "img", "tabularFallback": True, "keyboardNavigation": True},
        "interaction": {
            "tooltip": bool(interaction_payload.get("tooltip", True)),
            "focusablePoints": bool(interaction_payload.get("focusablePoints", True)),
            "zoom": bool(interaction_payload.get("zoom", True)),
            "pan": bool(interaction_payload.get("pan", True)),
            "crosshair": bool(interaction_payload.get("crosshair", True)),
            "seriesToggle": bool(interaction_payload.get("seriesToggle", True)),
        },
        "publication": {
            "subtitle": _text(publication_payload.get("subtitle"), "publication subtitle", 240),
            "caption": _text(publication_payload.get("caption"), "publication caption", 800),
            "source": _text(publication_payload.get("source"), "publication source", 300),
            "method": _text(publication_payload.get("method"), "publication method", 500),
            "notes": _text(publication_payload.get("notes"), "publication notes", 500),
            "aspectRatio": aspect,
            "showGrid": bool(publication_payload.get("showGrid", True)),
            "showLegend": bool(publication_payload.get("showLegend", True)),
            "background": "white",
        },
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
        "handoffTargets": ["dynamic-systems", "model-diagnostics", "model-calibration", "design-studies", "ensemble-uncertainty", "model-registry", "workbench"],
        "boundaries": {"arbitraryCode": False, "arbitraryFormulaExecution": False, "safeDeclarativeExpressionExecution": True},
    }
    bundle["bundleHash"] = _digest(bundle)
    return bundle


def validate_equation(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return validate_equation_definition(payload)
    except EquationBuilderError as exc:
        raise ModelStudioError(str(exc)) from exc


def preview_equation_model(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelStudioError("Equation preview request must be an object.")
    model = normalize_model(payload.get("model") or payload)
    if model["family"] != "declarative-expression":
        raise ModelStudioError("Equation preview requires the declarative-expression model family.")
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise ModelStudioError("rows must be an array.")
    parameter_values = {}
    for row in model["parameters"]:
        if row.get("value") is not None:
            parameter_values[row["symbol"]] = row["value"]
    for row in model.get("constants") or []:
        parameter_values[row["symbol"]] = row["value"]
    try:
        evaluated = evaluate_equation_rows({
            "definition": {
                "equation": model["definition"]["equation"],
                "variables": model["variables"],
                "parameters": model["parameters"],
                "constants": model.get("constants") or [],
                "outputSymbol": model["definition"].get("outputSymbol"),
            },
            "values": parameter_values,
            "rows": rows,
        })
    except EquationBuilderError as exc:
        raise ModelStudioError(str(exc)) from exc
    feature_bindings = [b for b in model["dataset"]["bindings"] if b["role"] in {"feature", "time"}]
    if not feature_bindings:
        raise ModelStudioError("Equation preview requires at least one feature or time binding.")
    x_binding = feature_bindings[0]
    output_symbol = model["definition"]["outputSymbol"]
    response_binding = next((b for b in model["dataset"]["bindings"] if b["role"] == "response" and b["symbol"] == output_symbol), None)
    points = []
    for row in evaluated["rows"]:
        if x_binding["column"] not in row:
            raise ModelStudioError(f"Preview row is missing x column: {x_binding['column']}.")
        points.append({"x": row[x_binding["column"]], "y": row[output_symbol]})
    x_label = x_binding["column"] + (f" ({x_binding['unit']})" if x_binding.get("unit") else "")
    y_unit = response_binding.get("unit") if response_binding else next((v.get("unit") for v in model["variables"] if v["symbol"] == output_symbol), "")
    y_label = output_symbol + (f" ({y_unit})" if y_unit else "")
    graph = normalize_graph({
        "kind": "line-scatter",
        "title": f"{model['title']} — equation preview",
        "description": "Safe declarative equation evaluated over the supplied preview rows.",
        "xLabel": x_label,
        "yLabel": y_label,
        "series": [{"id": "equation-preview", "label": "Model output", "mode": "line-scatter", "points": points}],
    })
    return {
        "ok": True,
        "version": VERSION,
        "model": model,
        "evaluation": evaluated,
        "graph": graph,
        "boundaries": {"arbitraryCode": False, "safeDeclarativeExpressionExecution": True},
    }
