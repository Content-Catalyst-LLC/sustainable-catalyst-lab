from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from statistics import NormalDist, mean, median
from typing import Any

from .data_transformations import (
    DataTransformationError,
    convert_unit_value,
    transform_dataset as transform_dataset_v0550,
)
from .visualization_engine_v0740 import (
    VisualizationGrammarError,
    normalize_spec as normalize_visualization_v0740,
)

VERSION = "0.75.0"
ENGINE_VERSION = "2.2.0"
DATASET_SCHEMA = "sc-lab-scientific-dataset/0.75.0"
PIPELINE_SCHEMA = "sc-lab-data-transformation-pipeline/0.75.0"
PIPELINE_RESULT_SCHEMA = "sc-lab-data-transformation-result/0.75.0"
BINDING_SCHEMA = "sc-lab-visualization-data-binding/0.75.0"
SPEC_SCHEMA = "sc-lab-scientific-visualization/0.75.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.75.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.75.0"
PLOT_GRAMMAR = "sc-lab-advanced-2d-plot-grammar/0.74.0"
MAX_ROWS = 5000
MAX_COLUMNS = 200
MAX_OPERATIONS = 100
MAX_SERIES = 64
MAX_POINTS = 100000
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
SAFE_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
DATA_TYPES = {"number", "integer", "string", "boolean", "datetime", "category"}
LEGACY_TRANSFORMS = {"derive", "filter", "rename", "select", "drop", "scale", "unit-convert", "cast", "impute"}
EXTENDED_TRANSFORMS = {"sort", "aggregate", "bin", "drop-missing"}
TRANSFORMS = LEGACY_TRANSFORMS | EXTENDED_TRANSFORMS
AGGREGATES = {"count", "sum", "mean", "median", "min", "max", "std"}
SORT_DIRECTIONS = {"asc", "desc"}
BINDING_ROLES = {"x", "y", "z", "w", "yLow", "yHigh", "xLow", "xHigh", "group", "label", "size", "weight", "value", "level"}


class ScientificDataBindingError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, max_len: int = 500, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ScientificDataBindingError(f"{name} is required.")
    if len(text) > max_len:
        raise ScientificDataBindingError(f"{name} exceeds {max_len} characters.")
    return text


def _missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ScientificDataBindingError(f"{name} must be numeric.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ScientificDataBindingError(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise ScientificDataBindingError(f"{name} must be finite.")
    return number


def _safe_key(value: Any, name: str = "column") -> str:
    key = _text(value, name, 64, True)
    if not SAFE_KEY_RE.fullmatch(key):
        raise ScientificDataBindingError(f"{name} must start with a letter and use only letters, digits, and underscore.")
    return key


def _clean_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ScientificDataBindingError("dataset.rows must be an array of row objects.")
    if len(value) > MAX_ROWS:
        raise ScientificDataBindingError(f"dataset.rows exceeds the {MAX_ROWS}-row v0.75 binding limit.")
    rows: list[dict[str, Any]] = []
    columns: list[str] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise ScientificDataBindingError(f"dataset.rows[{index}] must be an object.")
        row: dict[str, Any] = {}
        for raw_key, cell in raw.items():
            key = _text(raw_key, "column name", 240, True)
            if isinstance(cell, (dict, list, tuple, set)):
                raise ScientificDataBindingError(f"Nested values are not supported in binding rows ({key}).")
            if isinstance(cell, float) and not math.isfinite(cell):
                raise ScientificDataBindingError(f"Non-finite value in {key} at row {index + 1}.")
            row[key] = cell
            if key not in columns:
                columns.append(key)
        rows.append(row)
    if len(columns) > MAX_COLUMNS:
        raise ScientificDataBindingError(f"Dataset exceeds the {MAX_COLUMNS}-column limit.")
    return rows


def _column_order(rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in rows:
        for key in row:
            if key not in out:
                out.append(key)
    return out


def _infer_type(values: list[Any]) -> str:
    observed = [value for value in values if not _missing(value)]
    if not observed:
        return "string"
    if all(isinstance(v, bool) for v in observed):
        return "boolean"
    numeric = 0
    integer = 0
    for value in observed:
        if isinstance(value, bool):
            continue
        try:
            number = float(value)
            if math.isfinite(number):
                numeric += 1
                if number.is_integer():
                    integer += 1
        except (TypeError, ValueError):
            pass
    if numeric == len(observed):
        return "integer" if integer == len(observed) else "number"
    unique = {str(v) for v in observed}
    if len(unique) <= min(50, max(10, int(len(observed) * 0.2))):
        return "category"
    return "string"


def _column_metadata(rows: list[dict[str, Any]], supplied: Any, units: dict[str, str]) -> list[dict[str, Any]]:
    supplied_map: dict[str, dict[str, Any]] = {}
    if supplied not in (None, ""):
        if not isinstance(supplied, list):
            raise ScientificDataBindingError("dataset.columns must be an array when supplied.")
        for index, item in enumerate(supplied):
            if not isinstance(item, dict):
                raise ScientificDataBindingError(f"dataset.columns[{index}] must be an object.")
            key = _text(item.get("key") or item.get("name"), f"dataset.columns[{index}].key", 240, True)
            supplied_map[key] = item
    out: list[dict[str, Any]] = []
    for key in _column_order(rows):
        item = supplied_map.get(key, {})
        values = [row.get(key) for row in rows]
        dtype = _text(item.get("dataType") or item.get("type") or _infer_type(values), f"column {key} dataType", 30, True)
        if dtype not in DATA_TYPES:
            raise ScientificDataBindingError(f"Unsupported data type for {key}: {dtype}.")
        unit = _text(item.get("unit") if "unit" in item else units.get(key), f"column {key} unit", 120)
        units[key] = unit
        observed = [v for v in values if not _missing(v)]
        numeric_count = 0
        for value in observed:
            try:
                if not isinstance(value, bool) and math.isfinite(float(value)):
                    numeric_count += 1
            except (TypeError, ValueError):
                pass
        out.append({
            "key": key,
            "label": _text(item.get("label") or key, f"column {key} label", 240, True),
            "dataType": dtype,
            "unit": unit,
            "description": _text(item.get("description"), f"column {key} description", 800),
            "missingCount": sum(1 for value in values if _missing(value)),
            "observedCount": len(observed),
            "numericCount": numeric_count,
        })
    unknown = [key for key in supplied_map if key not in {c["key"] for c in out}]
    if unknown:
        raise ScientificDataBindingError(f"dataset.columns references column(s) absent from rows: {', '.join(unknown[:10])}.")
    return out


def normalize_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificDataBindingError("Dataset definition must be an object.")
    rows = _clean_rows(payload.get("rows") or [])
    if not rows:
        raise ScientificDataBindingError("Dataset requires at least one row.")
    units = {str(k): _text(v, f"unit {k}", 120) for k, v in (payload.get("units") or {}).items()} if isinstance(payload.get("units"), dict) else {}
    columns = _column_metadata(rows, payload.get("columns") or payload.get("dataDictionary"), units)
    raw_id = _text(payload.get("id") or payload.get("datasetId") or f"dataset-{_digest(rows)[:16]}", "dataset id", 160, True)
    if not ID_RE.fullmatch(raw_id):
        raise ScientificDataBindingError("Dataset id contains unsupported characters.")
    prov = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    dataset = {
        "schema": DATASET_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-dataset-v0750",
        "id": raw_id,
        "title": _text(payload.get("title") or raw_id, "dataset title", 240, True),
        "description": _text(payload.get("description"), "dataset description", 1500),
        "rowCount": len(rows),
        "columnCount": len(columns),
        "columns": columns,
        "units": {column["key"]: column["unit"] for column in columns if column["unit"]},
        "rows": rows,
        "provenance": {
            "projectId": _text(prov.get("projectId"), "projectId", 160),
            "sourceId": _text(prov.get("sourceId") or payload.get("sourceId"), "sourceId", 240),
            "sourceType": _text(prov.get("sourceType") or "inline", "sourceType", 80, True),
            "sourceUri": _text(prov.get("sourceUri") or prov.get("url"), "sourceUri", 1000),
            "license": _text(prov.get("license"), "license", 240),
            "citation": _text(prov.get("citation"), "citation", 1200),
            "retrievedAt": _text(prov.get("retrievedAt"), "retrievedAt", 80),
            "notes": _text(prov.get("notes"), "provenance notes", 1500),
        },
        "arbitraryCode": False,
    }
    dataset["fingerprint"] = _digest({
        "id": dataset["id"], "columns": dataset["columns"], "rows": dataset["rows"], "provenance": dataset["provenance"]
    })
    return dataset


def _normalize_operation(raw: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ScientificDataBindingError(f"pipeline.operations[{index}] must be an object.")
    kind = _text(raw.get("type"), f"pipeline.operations[{index}].type", 40, True).lower()
    if kind not in TRANSFORMS:
        raise ScientificDataBindingError(f"Unsupported v0.75 transformation type: {kind}.")
    out = deepcopy(raw)
    out["type"] = kind
    out["id"] = _text(raw.get("id") or f"op-{index + 1}", "operation id", 120, True)
    if kind == "sort":
        by = raw.get("by") or raw.get("keys")
        if isinstance(by, str):
            by = [{"column": by, "direction": raw.get("direction") or "asc"}]
        if not isinstance(by, list) or not by:
            raise ScientificDataBindingError("sort requires a non-empty by array.")
        norm = []
        for j, item in enumerate(by):
            if isinstance(item, str):
                item = {"column": item, "direction": "asc"}
            if not isinstance(item, dict):
                raise ScientificDataBindingError(f"sort.by[{j}] must be an object or column name.")
            column = _text(item.get("column"), f"sort.by[{j}].column", 240, True)
            direction = _text(item.get("direction") or "asc", f"sort.by[{j}].direction", 10, True).lower()
            if direction not in SORT_DIRECTIONS:
                raise ScientificDataBindingError("sort direction must be asc or desc.")
            norm.append({"column": column, "direction": direction})
        out = {"type": kind, "id": out["id"], "by": norm}
    elif kind == "aggregate":
        group_by = raw.get("groupBy") or []
        if isinstance(group_by, str):
            group_by = [group_by]
        if not isinstance(group_by, list):
            raise ScientificDataBindingError("aggregate.groupBy must be an array.")
        metrics = raw.get("metrics") or []
        if not isinstance(metrics, list) or not metrics:
            raise ScientificDataBindingError("aggregate requires at least one metric.")
        norm_metrics = []
        for j, metric in enumerate(metrics):
            if not isinstance(metric, dict):
                raise ScientificDataBindingError(f"aggregate.metrics[{j}] must be an object.")
            op = _text(metric.get("op") or metric.get("method"), f"aggregate.metrics[{j}].op", 20, True).lower()
            if op not in AGGREGATES:
                raise ScientificDataBindingError(f"Unsupported aggregate operation: {op}.")
            column = _text(metric.get("column"), f"aggregate.metrics[{j}].column", 240, op != "count")
            target = _safe_key(metric.get("as") or metric.get("target") or (f"{op}_{column}" if column else "count"), "aggregate output")
            norm_metrics.append({"op": op, "column": column, "as": target})
        out = {"type": kind, "id": out["id"], "groupBy": [_text(c, "groupBy column", 240, True) for c in group_by], "metrics": norm_metrics}
    elif kind == "bin":
        column = _text(raw.get("column"), "bin.column", 240, True)
        target = _safe_key(raw.get("target") or f"{column}_bin", "bin.target")
        count = int(raw.get("count") or raw.get("bins") or 10)
        if count < 2 or count > 200:
            raise ScientificDataBindingError("bin.count must be between 2 and 200.")
        out = {"type": kind, "id": out["id"], "column": column, "target": target, "count": count}
    elif kind == "drop-missing":
        columns = raw.get("columns") or []
        if isinstance(columns, str):
            columns = [columns]
        if not isinstance(columns, list) or not columns:
            raise ScientificDataBindingError("drop-missing requires a non-empty columns array.")
        mode = _text(raw.get("mode") or "any", "drop-missing.mode", 10, True).lower()
        if mode not in {"any", "all"}:
            raise ScientificDataBindingError("drop-missing.mode must be any or all.")
        out = {"type": kind, "id": out["id"], "columns": [_text(c, "drop-missing column", 240, True) for c in columns], "mode": mode}
    return out


def normalize_pipeline(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    operations = source.get("operations") or []
    if not isinstance(operations, list):
        raise ScientificDataBindingError("pipeline.operations must be an array.")
    if len(operations) > MAX_OPERATIONS:
        raise ScientificDataBindingError(f"pipeline.operations exceeds the {MAX_OPERATIONS}-operation limit.")
    out = {
        "schema": PIPELINE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-data-transformation-pipeline-v0750",
        "id": _text(source.get("id") or f"pipeline-{_digest(operations)[:16]}", "pipeline id", 160, True),
        "title": _text(source.get("title") or "Visualization data preparation", "pipeline title", 240, True),
        "operations": [_normalize_operation(op, index) for index, op in enumerate(operations)],
        "boundaries": {"arbitraryCode": False, "arbitrarySql": False, "network": False, "filesystem": False, "automaticImputation": False, "automaticUnitInference": False},
    }
    if not ID_RE.fullmatch(out["id"]):
        raise ScientificDataBindingError("Pipeline id contains unsupported characters.")
    out["fingerprint"] = _digest({"operations": out["operations"], "boundaries": out["boundaries"]})
    return out


def _stage_hash(rows: list[dict[str, Any]], units: dict[str, str]) -> str:
    return _digest({"rows": rows, "units": units})


def _eval_expression(node: Any, row: dict[str, Any]) -> float:
    if isinstance(node, bool):
        raise ScientificDataBindingError("Derived expression constants cannot be boolean.")
    if isinstance(node, (int, float)):
        return _finite(node, "derived constant")
    if isinstance(node, str):
        if node not in row:
            raise ScientificDataBindingError(f"Derived expression field not found: {node}.")
        return _finite(row.get(node), node)
    if not isinstance(node, dict):
        raise ScientificDataBindingError("Structured derive expressions must be objects using field/value or op/args.")
    if "field" in node:
        key = _text(node.get("field"), "derive field", 240, True)
        if key not in row:
            raise ScientificDataBindingError(f"Derived expression field not found: {key}.")
        return _finite(row.get(key), key)
    if "value" in node:
        return _finite(node.get("value"), "derived constant")
    op = _text(node.get("op"), "derive operation", 30, True).lower()
    args = node.get("args") or []
    if not isinstance(args, list):
        raise ScientificDataBindingError("derive expression args must be an array.")
    values = [_eval_expression(arg, row) for arg in args]
    if op == "add": return sum(values)
    if op == "subtract" and len(values) == 2: return values[0] - values[1]
    if op == "multiply":
        out = 1.0
        for value in values: out *= value
        return out
    if op == "divide" and len(values) == 2:
        if values[1] == 0: raise ScientificDataBindingError("Derived expression division by zero.")
        return values[0] / values[1]
    if op == "pow" and len(values) == 2: return math.pow(values[0], values[1])
    if op == "sqrt" and len(values) == 1: return math.sqrt(values[0])
    if op == "abs" and len(values) == 1: return abs(values[0])
    if op == "log" and len(values) == 1: return math.log(values[0])
    if op == "log10" and len(values) == 1: return math.log10(values[0])
    if op == "exp" and len(values) == 1: return math.exp(values[0])
    raise ScientificDataBindingError(f"Unsupported structured derive operation or arity: {op}.")


def _apply_sort(rows: list[dict[str, Any]], op: dict[str, Any]) -> list[dict[str, Any]]:
    columns = _column_order(rows)
    for item in op["by"]:
        if item["column"] not in columns:
            raise ScientificDataBindingError(f"Sort column not found: {item['column']}.")
    out = deepcopy(rows)
    def key_value(value: Any):
        if _missing(value):
            return (1, "")
        try:
            return (0, float(value))
        except (TypeError, ValueError):
            return (0, str(value))
    for item in reversed(op["by"]):
        out.sort(key=lambda row, c=item["column"]: key_value(row.get(c)), reverse=item["direction"] == "desc")
    return out


def _aggregate_metric(values: list[Any], op: str) -> float | int:
    if op == "count":
        return sum(1 for value in values if not _missing(value))
    nums = [_finite(value, "aggregate value") for value in values if not _missing(value)]
    if not nums:
        raise ScientificDataBindingError(f"Aggregate {op} has no observed numeric values.")
    if op == "sum": return sum(nums)
    if op == "mean": return mean(nums)
    if op == "median": return median(nums)
    if op == "min": return min(nums)
    if op == "max": return max(nums)
    if op == "std":
        mu = mean(nums)
        return math.sqrt(sum((value - mu) ** 2 for value in nums) / len(nums))
    raise ScientificDataBindingError(f"Unsupported aggregate operation: {op}.")


def _apply_aggregate(rows: list[dict[str, Any]], units: dict[str, str], op: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    columns = _column_order(rows)
    missing = [c for c in op["groupBy"] if c not in columns]
    missing += [m["column"] for m in op["metrics"] if m["column"] and m["column"] not in columns]
    if missing:
        raise ScientificDataBindingError(f"Aggregate column(s) not found: {', '.join(sorted(set(missing)))}.")
    groups: dict[str, tuple[list[Any], list[dict[str, Any]]]] = {}
    if op["groupBy"]:
        for row in rows:
            key_values = [row.get(c) for c in op["groupBy"]]
            key = _canonical(key_values)
            groups.setdefault(key, (key_values, []))[1].append(row)
    else:
        groups["[]"] = ([], rows)
    output: list[dict[str, Any]] = []
    output_units = {c: units.get(c, "") for c in op["groupBy"] if units.get(c)}
    for _, (key_values, members) in groups.items():
        row = {column: value for column, value in zip(op["groupBy"], key_values)}
        for metric in op["metrics"]:
            values = [member.get(metric["column"]) for member in members] if metric["column"] else [1 for _ in members]
            row[metric["as"]] = _aggregate_metric(values, metric["op"])
            if metric["op"] in {"sum", "mean", "median", "min", "max", "std"} and metric["column"] in units:
                output_units[metric["as"]] = units[metric["column"]]
            elif metric["op"] == "count":
                output_units[metric["as"]] = "count"
        output.append(row)
    return output, output_units


def _apply_bin(rows: list[dict[str, Any]], units: dict[str, str], op: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, Any]]:
    columns = _column_order(rows)
    if op["column"] not in columns:
        raise ScientificDataBindingError(f"Bin column not found: {op['column']}.")
    values = [_finite(row.get(op["column"]), op["column"]) for row in rows if not _missing(row.get(op["column"]))]
    if not values:
        raise ScientificDataBindingError(f"Bin column {op['column']} has no observed numeric values.")
    lo, hi = min(values), max(values)
    width = (hi - lo) / op["count"] if hi != lo else 1.0
    out = deepcopy(rows)
    for row in out:
        raw = row.get(op["column"])
        if _missing(raw):
            row[op["target"]] = None
            continue
        value = _finite(raw, op["column"])
        index = 0 if hi == lo else min(op["count"] - 1, max(0, int((value - lo) / width)))
        left = lo + index * width
        right = left + width
        row[op["target"]] = left + width / 2
        row[f"{op['target']}_index"] = index
        row[f"{op['target']}_label"] = f"[{left:.6g}, {right:.6g}{']' if index == op['count'] - 1 else ')'}"
    output_units = dict(units)
    if units.get(op["column"]):
        output_units[op["target"]] = units[op["column"]]
    return out, output_units, {"min": lo, "max": hi, "width": width, "count": op["count"]}


def execute_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificDataBindingError("Pipeline execution request must be an object.")
    dataset = normalize_dataset(payload.get("dataset") or payload.get("data") or {})
    pipeline = normalize_pipeline(payload.get("pipeline") or {"operations": []})
    rows = deepcopy(dataset["rows"])
    units = dict(dataset["units"])
    lineage: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, op in enumerate(pipeline["operations"]):
        before_rows = len(rows)
        before_columns = len(_column_order(rows))
        input_hash = _stage_hash(rows, units)
        details: dict[str, Any] = {}
        stage_warnings: list[str] = []
        try:
            if op["type"] == "derive" and isinstance(op.get("expression"), dict):
                name = _safe_key(op.get("name"), "derive output")
                if name in _column_order(rows):
                    raise ScientificDataBindingError(f"Derived variable {name} already exists.")
                for row_index, row in enumerate(rows):
                    try:
                        row[name] = _eval_expression(op["expression"], row)
                    except ScientificDataBindingError as exc:
                        raise ScientificDataBindingError(f"Structured derived variable {name} failed at row {row_index + 1}: {exc}") from exc
                units[name] = _text(op.get("unit"), "derive unit", 120)
                details["structuredExpression"] = True
            elif op["type"] in LEGACY_TRANSFORMS:
                result = transform_dataset_v0550({"rows": rows, "units": units, "plan": {"operations": [op]}})["result"]
                rows = deepcopy(result["rows"])
                units = dict(result.get("units") or {})
                stage_warnings.extend(result.get("warnings") or [])
                details["v0550ResultHash"] = result.get("resultHash")
            elif op["type"] == "sort":
                rows = _apply_sort(rows, op)
            elif op["type"] == "aggregate":
                rows, units = _apply_aggregate(rows, units, op)
            elif op["type"] == "bin":
                rows, units, details["bin"] = _apply_bin(rows, units, op)
            elif op["type"] == "drop-missing":
                columns = _column_order(rows)
                missing = [c for c in op["columns"] if c not in columns]
                if missing:
                    raise ScientificDataBindingError(f"drop-missing column(s) not found: {', '.join(missing)}.")
                kept = []
                for row in rows:
                    flags = [_missing(row.get(c)) for c in op["columns"]]
                    drop = any(flags) if op["mode"] == "any" else all(flags)
                    if not drop:
                        kept.append(row)
                removed = len(rows) - len(kept)
                rows = kept
                details["removedRows"] = removed
                if removed:
                    stage_warnings.append(f"drop-missing removed {removed} row(s).")
        except DataTransformationError as exc:
            raise ScientificDataBindingError(str(exc)) from exc
        if len(rows) > MAX_ROWS:
            raise ScientificDataBindingError(f"Pipeline output exceeds the {MAX_ROWS}-row binding limit.")
        output_hash = _stage_hash(rows, units)
        lineage.append({
            "index": index + 1,
            "id": op["id"],
            "type": op["type"],
            "operationHash": _digest(op),
            "inputHash": input_hash,
            "outputHash": output_hash,
            "rowsBefore": before_rows,
            "rowsAfter": len(rows),
            "columnsBefore": before_columns,
            "columnsAfter": len(_column_order(rows)),
            "warnings": stage_warnings,
            "details": details,
        })
        warnings.extend(stage_warnings)
    transformed = normalize_dataset({
        "id": f"{dataset['id']}-transformed",
        "title": f"{dataset['title']} — transformed",
        "description": dataset["description"],
        "rows": rows,
        "units": units,
        "provenance": {
            **dataset["provenance"],
            "sourceId": dataset["id"],
            "sourceType": "derived-transformation",
            "notes": f"Derived by {pipeline['id']} from dataset fingerprint {dataset['fingerprint']}.",
        },
    })
    result = {
        "schema": PIPELINE_RESULT_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-data-transformation-result-v0750",
        "datasetId": dataset["id"],
        "datasetFingerprint": dataset["fingerprint"],
        "pipeline": pipeline,
        "pipelineFingerprint": pipeline["fingerprint"],
        "inputFingerprint": _stage_hash(dataset["rows"], dataset["units"]),
        "outputFingerprint": _stage_hash(rows, units),
        "rowCount": len(rows),
        "columnCount": len(_column_order(rows)),
        "rows": rows,
        "units": units,
        "lineage": lineage,
        "warnings": warnings,
        "transformedDataset": transformed,
        "generatedAt": _now(),
        "arbitraryCode": False,
    }
    result["fingerprint"] = _digest({k: v for k, v in result.items() if k not in {"generatedAt", "fingerprint"}})
    return result


def normalize_binding(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificDataBindingError("Visualization binding must be an object.")
    kind = _text(payload.get("kind") or payload.get("visualizationKind"), "binding kind", 40, True)
    mappings_src = payload.get("mappings") or {}
    if not isinstance(mappings_src, dict):
        raise ScientificDataBindingError("binding.mappings must be an object.")
    mappings: dict[str, str] = {}
    for role, column in mappings_src.items():
        if role not in BINDING_ROLES:
            raise ScientificDataBindingError(f"Unsupported visual encoding role: {role}.")
        if column not in (None, ""):
            mappings[role] = _text(column, f"binding mapping {role}", 240, True)
    series_src = payload.get("series") or []
    if not isinstance(series_src, list):
        raise ScientificDataBindingError("binding.series must be an array.")
    series = []
    for index, item in enumerate(series_src[:MAX_SERIES]):
        if not isinstance(item, dict):
            raise ScientificDataBindingError(f"binding.series[{index}] must be an object.")
        y = _text(item.get("y") or item.get("column"), f"binding.series[{index}].y", 240, True)
        series.append({
            "y": y,
            "label": _text(item.get("label") or y, f"binding.series[{index}].label", 160, True),
            "mode": _text(item.get("mode"), f"binding.series[{index}].mode", 30),
            "yLow": _text(item.get("yLow"), f"binding.series[{index}].yLow", 240),
            "yHigh": _text(item.get("yHigh"), f"binding.series[{index}].yHigh", 240),
        })
    options = payload.get("options") if isinstance(payload.get("options"), dict) else {}
    binding = {
        "schema": BINDING_SCHEMA,
        "version": VERSION,
        "recordType": "visualization-data-binding-v0750",
        "id": _text(payload.get("id") or f"binding-{_digest({'kind': kind, 'mappings': mappings, 'series': series})[:16]}", "binding id", 160, True),
        "kind": kind,
        "mappings": mappings,
        "series": series,
        "options": {
            "histogramBins": max(2, min(200, int(options.get("histogramBins") or 12))),
            "hexbinSize": max(1e-12, float(options.get("hexbinSize") or 1.0)),
            "densityPoints": max(16, min(512, int(options.get("densityPoints") or 80))),
            "dropMissingMappedRows": bool(options.get("dropMissingMappedRows", True)),
        },
    }
    if not ID_RE.fullmatch(binding["id"]):
        raise ScientificDataBindingError("Binding id contains unsupported characters.")
    binding["fingerprint"] = _digest({k: v for k, v in binding.items() if k != "fingerprint"})
    return binding


def _mapped_rows(rows: list[dict[str, Any]], binding: dict[str, Any]) -> list[dict[str, Any]]:
    columns = set(_column_order(rows))
    required_columns = set(binding["mappings"].values())
    for item in binding["series"]:
        required_columns.add(item["y"])
        if item.get("yLow"): required_columns.add(item["yLow"])
        if item.get("yHigh"): required_columns.add(item["yHigh"])
    missing = sorted(c for c in required_columns if c and c not in columns)
    if missing:
        raise ScientificDataBindingError(f"Binding references column(s) absent from transformed data: {', '.join(missing)}.")
    if not binding["options"]["dropMissingMappedRows"]:
        return deepcopy(rows)
    required = [c for c in required_columns if c]
    return [deepcopy(row) for row in rows if all(not _missing(row.get(c)) for c in required)]


def _group_series(rows: list[dict[str, Any]], x_key: str, y_key: str, group_key: str | None, label: str, mode: str = "", y_low: str = "", y_high: str = "") -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    if group_key:
        for row in rows:
            groups.setdefault(str(row.get(group_key)), []).append(row)
    else:
        groups[label] = rows
    out = []
    for group, members in groups.items():
        points = []
        for index, row in enumerate(members):
            point = {"x": row.get(x_key, index), "y": _finite(row.get(y_key), y_key)}
            if y_low: point["yLow"] = _finite(row.get(y_low), y_low)
            if y_high: point["yHigh"] = _finite(row.get(y_high), y_high)
            points.append(point)
        try:
            points.sort(key=lambda item: float(item["x"]))
        except (TypeError, ValueError):
            pass
        out.append({"id": re.sub(r"[^A-Za-z0-9._:-]+", "-", group)[:80] or "series", "label": group if group_key else label, "mode": mode or "auto", "points": points})
    return out


def _quantile(values: list[float], q: float) -> float:
    values = sorted(values)
    if not values:
        return math.nan
    pos = (len(values) - 1) * q
    lo = math.floor(pos); hi = math.ceil(pos)
    if lo == hi: return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def _kde(values: list[float], points: int) -> list[dict[str, float]]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [{"x": lo, "y": 1.0}]
    mu = mean(values)
    sd = math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))
    bandwidth = 1.06 * max(sd, (hi - lo) / max(4, len(values))) * (len(values) ** -0.2)
    bandwidth = max(bandwidth, (hi - lo) / 200, 1e-12)
    norm = len(values) * bandwidth * math.sqrt(2 * math.pi)
    out = []
    for index in range(points):
        x = lo + (hi - lo) * index / max(1, points - 1)
        y = sum(math.exp(-0.5 * ((x - value) / bandwidth) ** 2) for value in values) / norm
        out.append({"x": x, "y": y})
    return out


def _axis_template(figure: dict[str, Any], role: str, column: str, units: dict[str, str]) -> dict[str, Any]:
    axes = figure.get("axes") if isinstance(figure.get("axes"), dict) else {}
    src = axes.get(role) if isinstance(axes.get(role), dict) else {}
    return {
        "scale": src.get("scale") or "linear",
        "label": src.get("label") or figure.get(f"{role}Label") or column,
        "unit": src.get("unit") if "unit" in src else units.get(column, ""),
        "tickFormat": src.get("tickFormat") or "auto",
        "inverted": bool(src.get("inverted", False)),
        "domain": src.get("domain"),
        "categories": src.get("categories") or [],
        "linthresh": src.get("linthresh", 1.0),
    }


def _build_2d_spec(rows: list[dict[str, Any]], units: dict[str, str], binding: dict[str, Any], figure: dict[str, Any]) -> dict[str, Any]:
    kind = binding["kind"]
    m = binding["mappings"]
    x_key = m.get("x") or m.get("label") or ""
    y_key = m.get("y") or m.get("value") or ""
    z_key = m.get("z") or m.get("value") or ""
    group_key = m.get("group")
    label_key = m.get("label")
    title = _text(figure.get("title") or "Scientific figure", "figure title", 180, True)
    spec: dict[str, Any] = {
        "kind": kind,
        "title": title,
        "subtitle": _text(figure.get("subtitle"), "figure subtitle", 240),
        "axes": {
            "x": _axis_template(figure, "x", x_key or "x", units),
            "y": _axis_template(figure, "y", y_key or "y", units),
        },
        "publication": deepcopy(figure.get("publication") or {}),
        "interaction": deepcopy(figure.get("interaction") or {}),
        "series": [], "bars": [], "boxes": [], "violins": [], "cells": [], "contours": [], "bins": [],
    }
    interval_low = m.get("yLow", ""); interval_high = m.get("yHigh", "")
    simple_series = {"line", "scatter", "line-scatter", "step", "area", "stacked-area", "residual", "error-bar", "confidence-band"}
    if kind in simple_series:
        if not x_key or not (y_key or binding["series"]):
            raise ScientificDataBindingError(f"{kind} binding requires x and y mappings (or explicit series).")
        defs = binding["series"] or [{"y": y_key, "label": y_key, "mode": "", "yLow": interval_low, "yHigh": interval_high}]
        for item in defs:
            spec["series"].extend(_group_series(rows, x_key, item["y"], group_key, item["label"], item.get("mode") or ("scatter" if kind in {"scatter", "residual", "error-bar"} else "line"), item.get("yLow") or interval_low, item.get("yHigh") or interval_high))
    elif kind in {"histogram", "density", "ecdf", "qq"}:
        value_key = m.get("value") or y_key or x_key
        if not value_key:
            raise ScientificDataBindingError(f"{kind} binding requires a value mapping.")
        grouped: dict[str, list[float]] = {}
        for row in rows:
            group = str(row.get(group_key)) if group_key else value_key
            grouped.setdefault(group, []).append(_finite(row.get(value_key), value_key))
        if kind == "histogram":
            all_values = [v for values in grouped.values() for v in values]
            lo, hi = min(all_values), max(all_values); count = binding["options"]["histogramBins"]
            width = (hi - lo) / count if hi != lo else 1.0
            counts = [0] * count
            for value in all_values:
                index = 0 if hi == lo else min(count - 1, max(0, int((value - lo) / width)))
                counts[index] += 1
            spec["bars"] = [{"x": lo + (i + .5) * width, "y": n} for i, n in enumerate(counts)]
            spec["axes"]["x"] = _axis_template(figure, "x", value_key, units)
            spec["axes"]["y"]["label"] = spec["axes"]["y"].get("label") or "Count"
        elif kind == "density":
            spec["series"] = [{"id": f"density-{i+1}", "label": group, "mode": "line", "points": _kde(values, binding["options"]["densityPoints"])} for i, (group, values) in enumerate(grouped.items())]
            spec["axes"]["x"] = _axis_template(figure, "x", value_key, units)
            spec["axes"]["y"]["label"] = "Density"
        elif kind == "ecdf":
            spec["series"] = []
            for i, (group, values) in enumerate(grouped.items()):
                ordered = sorted(values); n = len(ordered)
                spec["series"].append({"id": f"ecdf-{i+1}", "label": group, "mode": "line", "points": [{"x": value, "y": (j + 1) / n} for j, value in enumerate(ordered)]})
            spec["axes"]["x"] = _axis_template(figure, "x", value_key, units)
            spec["axes"]["y"].update({"label": "Empirical cumulative probability", "unit": "1"})
        else:
            spec["series"] = []
            normal = NormalDist()
            for i, (group, values) in enumerate(grouped.items()):
                ordered = sorted(values); n = len(ordered)
                points = [{"x": normal.inv_cdf((j + .5) / n), "y": value} for j, value in enumerate(ordered)]
                spec["series"].append({"id": f"qq-{i+1}", "label": group, "mode": "scatter", "points": points})
            spec["axes"]["x"].update({"label": "Theoretical normal quantile", "unit": "1"})
            spec["axes"]["y"] = _axis_template(figure, "y", value_key, units)
    elif kind in {"bar", "grouped-bar", "stacked-bar", "waterfall", "pareto", "horizontal-bars"}:
        if not x_key or not (y_key or binding["series"]):
            raise ScientificDataBindingError(f"{kind} binding requires category x and y/value mappings.")
        defs = binding["series"] or [{"y": y_key, "label": y_key, "mode": ""}]
        categories = []
        for row in rows:
            category = str(row.get(x_key))
            if category not in categories: categories.append(category)
        spec["axes"]["x"].update({"scale": "categorical", "categories": categories})
        if kind == "horizontal-bars" and len(defs) == 1:
            spec["bars"] = [{"label": str(row.get(x_key)), "value": _finite(row.get(defs[0]["y"]), defs[0]["y"])} for row in rows]
        else:
            spec["series"] = []
            for si, item in enumerate(defs):
                points = [{"x": i, "y": _finite(row.get(item["y"]), item["y"]), "label": str(row.get(x_key))} for i, row in enumerate(rows)]
                spec["series"].append({"id": item["y"], "label": item["label"], "stack": "stack-1" if kind == "stacked-bar" else "", "points": points})
            spec["bars"] = [
                {"x": i + ((si - (len(defs)-1)/2) * .22 if kind == "grouped-bar" else 0), "y": point["y"], "label": point["label"], "index": i, "series": si}
                for si, series in enumerate(spec["series"]) for i, point in enumerate(series["points"])
            ]
    elif kind in {"box", "violin"}:
        if not y_key:
            raise ScientificDataBindingError(f"{kind} binding requires y/value mapping.")
        groups: dict[str, list[float]] = {}
        for row in rows:
            group = str(row.get(x_key)) if x_key else "All"
            groups.setdefault(group, []).append(_finite(row.get(y_key), y_key))
        names = list(groups)
        spec["axes"]["x"].update({"scale": "categorical", "categories": names, "label": spec["axes"]["x"].get("label") or (x_key or "Group")})
        if kind == "box":
            spec["boxes"] = [{"x": i, "label": name, "min": min(values), "q1": _quantile(values, .25), "median": _quantile(values, .5), "q3": _quantile(values, .75), "max": max(values)} for i, (name, values) in enumerate(groups.items())]
        else:
            spec["violins"] = []
            for i, (name, values) in enumerate(groups.items()):
                kde = _kde(values, binding["options"]["densityPoints"])
                spec["violins"].append({"x": i, "label": name, "points": [{"value": p["x"], "density": p["y"]} for p in kde]})
    elif kind == "heatmap":
        if not x_key or not y_key or not z_key:
            raise ScientificDataBindingError("heatmap binding requires x, y, and z/value mappings.")
        xs = [] ; ys = []
        for row in rows:
            x = row.get(x_key); y = row.get(y_key)
            if x not in xs: xs.append(x)
            if y not in ys: ys.append(y)
        spec["xValues"] = xs; spec["yValues"] = ys
        spec["cells"] = [{"xIndex": xs.index(row.get(x_key)), "yIndex": ys.index(row.get(y_key)), "x": row.get(x_key), "y": row.get(y_key), "z": _finite(row.get(z_key), z_key)} for row in rows]
    elif kind == "hexbin":
        if not x_key or not y_key:
            raise ScientificDataBindingError("hexbin binding requires x and y mappings.")
        size = binding["options"]["hexbinSize"]; bins: dict[str, dict[str, Any]] = {}
        for row in rows:
            x = _finite(row.get(x_key), x_key); y = _finite(row.get(y_key), y_key)
            ix = round(x / size); iy = round(y / (size * .866025403784))
            key = f"{ix}:{iy}"; cell = bins.setdefault(key, {"x": ix * size, "y": iy * size * .866025403784, "count": 0})
            cell["count"] += 1
        spec["bins"] = list(bins.values())
    elif kind == "contour":
        if not x_key or not y_key or not (m.get("level") or z_key):
            raise ScientificDataBindingError("contour binding requires x, y, and level/z mappings.")
        level_key = m.get("level") or z_key
        levels: dict[str, list[dict[str, Any]]] = {}
        values: dict[str, Any] = {}
        for row in rows:
            level = row.get(level_key); token = _canonical(level); values[token] = level
            levels.setdefault(token, []).append({"x": _finite(row.get(x_key), x_key), "y": _finite(row.get(y_key), y_key)})
        spec["contours"] = [{"level": values[token], "label": f"Level {values[token]}", "points": points} for token, points in levels.items()]
    else:
        raise ScientificDataBindingError(f"v0.75 binding has no data adapter for visualization kind {kind}.")
    try:
        normalized = normalize_visualization_v0740(spec)
    except VisualizationGrammarError as exc:
        raise ScientificDataBindingError(str(exc)) from exc
    normalized.update({"schema": SPEC_SCHEMA, "version": VERSION, "visualizationEngine": ENGINE_VERSION})
    normalized["dataBindingVersion"] = VERSION
    normalized["rendering"]["dataMode"] = "project-data-bound"
    return normalized


def _normalize_to_unit(value: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    return ((value - lo) / (hi - lo)) * 2.0 - 1.0


def _build_surface4d_spec(rows: list[dict[str, Any]], units: dict[str, str], binding: dict[str, Any], figure: dict[str, Any]) -> dict[str, Any]:
    m = binding["mappings"]
    required = [m.get(role) for role in ("x", "y", "z", "w")]
    if any(not value for value in required):
        raise ScientificDataBindingError("surface-4d project-data binding requires x, y, z, and w mappings.")
    xk, yk, zk, wk = required
    values = {key: [_finite(row.get(key), key) for row in rows] for key in required}
    domains = {key: [min(vals), max(vals)] for key, vals in values.items()}
    points = []
    label_key = m.get("label")
    for row in rows[:MAX_POINTS]:
        points.append({
            "x": _normalize_to_unit(_finite(row.get(xk), xk), *domains[xk]),
            "y": _normalize_to_unit(_finite(row.get(yk), yk), *domains[yk]),
            "z": _normalize_to_unit(_finite(row.get(zk), zk), *domains[zk]),
            "w": _normalize_to_unit(_finite(row.get(wk), wk), *domains[wk]),
            "label": str(row.get(label_key))[:160] if label_key and row.get(label_key) is not None else "",
        })
    dimensions = [
        {"key": key, "label": (figure.get("axes") or {}).get(role, {}).get("label") if isinstance((figure.get("axes") or {}).get(role), dict) else key, "role": role, "unit": units.get(key, "")}
        for role, key in zip(("x", "y", "z", "w"), required)
    ]
    for item in dimensions:
        if not item["label"]: item["label"] = item["key"]
    spec = {
        "schema": SPEC_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-visualization-spec",
        "grammar": PLOT_GRAMMAR,
        "kind": "surface-4d",
        "renderer": "canvas4d",
        "rendererVersion": "0.75.0",
        "visualizationEngine": ENGINE_VERSION,
        "title": _text(figure.get("title") or "Project-data 4D scientific projection", "figure title", 180, True),
        "subtitle": _text(figure.get("subtitle"), "figure subtitle", 240),
        "profile": "project-data",
        "dimensions": dimensions,
        "visualEncoding": {role: key for role, key in zip(("x", "y", "z", "w"), required)},
        "surface": {
            "profile": "project-data", "slice": 0.0, "range": [-1.0, 1.0],
            "rotation": {"xw": .34, "yw": -.22, "zw": .12},
            "layers": {"surface": False, "vector": False, "uncertainty": False, "contours": False, "projection4d": True},
            "animation": {"enabled": False},
        },
        "dataBinding": {"mode": "project-data", "points": points, "sourceDomains": domains, "pointCount": len(points)},
        "publication": deepcopy(figure.get("publication") or {}),
        "interaction": {"tooltip": True, "hyperslice": True, "rotation4d": True, "animation": True, "layerToggle": False},
        "exports": ["png", "json"],
        "rendering": {"renderer": "canvas4d", "adapter": "scientific-data-binding-v0750", "dataMode": "project-data-bound", "interactive": True},
        "dataBoundary": "Project dataset values are normalized to [-1,1] per mapped dimension for 4D projection. Points are observations/records supplied by the bound dataset; Lab does not interpolate, estimate, forecast, or infer a response surface in v0.75.",
        "warnings": [] if all(domains[k][0] != domains[k][1] for k in required) else ["One or more mapped dimensions are constant; those coordinates project to zero."],
    }
    return spec


def bind_visualization(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificDataBindingError("Visualization binding request must be an object.")
    dataset = normalize_dataset(payload.get("dataset") or {})
    pipeline_result = execute_pipeline({"dataset": dataset, "pipeline": payload.get("pipeline") or {"operations": []}})
    binding = normalize_binding(payload.get("binding") or {})
    rows = _mapped_rows(pipeline_result["rows"], binding)
    if not rows:
        raise ScientificDataBindingError("No rows remain after transformation and mapped-value missingness checks.")
    figure = payload.get("figure") if isinstance(payload.get("figure"), dict) else {}
    spec = _build_surface4d_spec(rows, pipeline_result["units"], binding, figure) if binding["kind"] == "surface-4d" else _build_2d_spec(rows, pipeline_result["units"], binding, figure)
    provenance = {
        "datasetId": dataset["id"],
        "datasetFingerprint": dataset["fingerprint"],
        "pipelineId": pipeline_result["pipeline"]["id"],
        "pipelineFingerprint": pipeline_result["pipelineFingerprint"],
        "pipelineResultFingerprint": pipeline_result["fingerprint"],
        "bindingId": binding["id"],
        "bindingFingerprint": binding["fingerprint"],
        "sourceRowCount": dataset["rowCount"],
        "transformedRowCount": pipeline_result["rowCount"],
        "boundRowCount": len(rows),
        "visualizationEngine": ENGINE_VERSION,
        "renderer": spec["renderer"],
    }
    spec["dataBinding"] = {**(spec.get("dataBinding") or {}), "binding": binding, "provenance": provenance, "transformationLineage": pipeline_result["lineage"]}
    spec["fingerprint"] = _digest({k: v for k, v in spec.items() if k != "fingerprint"})
    return {"ok": True, "version": VERSION, "dataset": dataset, "pipelineResult": pipeline_result, "binding": binding, "spec": spec, "provenance": provenance}


def build_figure(payload: dict[str, Any]) -> dict[str, Any]:
    bound = bind_visualization(payload)
    figure_src = payload.get("figure") if isinstance(payload.get("figure"), dict) else {}
    raw_id = _text(figure_src.get("id") or f"figure-{bound['spec']['fingerprint'][:16]}", "figure id", 160, True)
    if not ID_RE.fullmatch(raw_id):
        raise ScientificDataBindingError("Figure id contains unsupported characters.")
    figure = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-figure-v0750",
        "id": raw_id,
        "title": _text(figure_src.get("title") or bound["spec"]["title"], "figure title", 180, True),
        "status": _text(figure_src.get("status") or "draft", "figure status", 40, True),
        "sourceContext": _text(figure_src.get("sourceContext") or "graph-studio", "sourceContext", 120, True),
        "tags": [_text(tag, "tag", 80, True) for tag in (figure_src.get("tags") or [])][:30],
        "graph": bound["spec"],
        "dataset": {"id": bound["dataset"]["id"], "fingerprint": bound["dataset"]["fingerprint"], "title": bound["dataset"]["title"]},
        "pipeline": {"id": bound["pipelineResult"]["pipeline"]["id"], "fingerprint": bound["pipelineResult"]["pipelineFingerprint"], "resultFingerprint": bound["pipelineResult"]["fingerprint"]},
        "binding": {"id": bound["binding"]["id"], "fingerprint": bound["binding"]["fingerprint"], "mappings": bound["binding"]["mappings"]},
        "provenance": {**bound["provenance"], "createdAt": _now(), "updatedAt": _now()},
    }
    figure["fingerprint"] = _digest({k: v for k, v in figure.items() if k != "fingerprint"})
    return {"ok": True, "version": VERSION, "figure": figure, "bindingResult": bound}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificDataBindingError("Workspace request must be an object.")
    figures_src = payload.get("figures") or []
    if not isinstance(figures_src, list):
        raise ScientificDataBindingError("workspace.figures must be an array.")
    figures = []
    for item in figures_src[:200]:
        if isinstance(item, dict) and item.get("recordType") == "scientific-figure-v0750":
            figures.append(deepcopy(item))
        elif isinstance(item, dict):
            figures.append(build_figure(item)["figure"])
        else:
            raise ScientificDataBindingError("Workspace figure entries must be objects.")
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "recordType": "figure-workspace-v0750",
        "projectId": _text(payload.get("projectId"), "projectId", 160),
        "title": _text(payload.get("title") or "Scientific figure workspace", "workspace title", 240, True),
        "figureCount": len(figures),
        "figures": figures,
        "generatedAt": _now(),
    }
    workspace["fingerprint"] = _digest({k: v for k, v in workspace.items() if k not in {"generatedAt", "fingerprint"}})
    return {"ok": True, "version": VERSION, "workspace": workspace}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "schemas": {"dataset": DATASET_SCHEMA, "pipeline": PIPELINE_SCHEMA, "pipelineResult": PIPELINE_RESULT_SCHEMA, "binding": BINDING_SCHEMA, "spec": SPEC_SCHEMA, "figure": FIGURE_SCHEMA, "workspace": WORKSPACE_SCHEMA},
        "transforms": sorted(TRANSFORMS),
        "legacyTransformationEngine": "0.55.0",
        "extendedTransforms": sorted(EXTENDED_TRANSFORMS),
        "aggregateMethods": sorted(AGGREGATES),
        "bindingRoles": sorted(BINDING_ROLES),
        "limits": {"rows": MAX_ROWS, "columns": MAX_COLUMNS, "operations": MAX_OPERATIONS, "series": MAX_SERIES, "points": MAX_POINTS},
        "capabilities": {"realProjectData2d": True, "realProjectData4dPointProjection": True, "transformationLineage": True, "unitMetadata": True, "unitConversionViaV0550": True, "datasetFingerprinting": True, "pipelineFingerprinting": True, "bindingFingerprinting": True, "figureFingerprinting": True},
        "boundaries": {"arbitraryCode": False, "arbitrarySql": False, "network": False, "filesystem": False, "automaticUnitInference": False, "automaticImputation": False, "automaticFeatureEngineering": False, "surfaceInterpolation": False, "surfaceForecasting": False, "polarRadar": False, "dualAxis": False},
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-data-binding-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "datasetBinding": True,
        "transformationPipeline": True,
        "transformationLineage": True,
        "unitAware": True,
        "realProjectData2d": True,
        "realProjectData4dPointProjection": True,
        "surfaceInterpolation": False,
        "legacyV0550TransformCompatibility": True,
        "advanced2dCompatibility": True,
        "canvas4dCompatibility": True,
        "arbitraryCode": False,
    }
