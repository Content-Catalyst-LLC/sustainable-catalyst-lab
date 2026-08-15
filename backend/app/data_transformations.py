from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from statistics import mean, median
from typing import Any

from .datasets import profile_dataset
from .equation_builder import EquationBuilderError, compile_equation, evaluate

VERSION = "0.55.0"
PLAN_SCHEMA = "sc-lab-scientific-data-transformation-plan/0.55.0"
RESULT_SCHEMA = "sc-lab-scientific-data-transformation-result/0.55.0"
JOIN_SCHEMA = "sc-lab-scientific-data-join/0.55.0"
MAX_ROWS = 5000
MAX_OUTPUT_ROWS = 10000
MAX_COLUMNS = 200
MAX_OPERATIONS = 100
SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")


class DataTransformationError(ValueError):
    pass


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _finite_number(value: Any, label: str = "value") -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise DataTransformationError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise DataTransformationError(f"{label} must be finite.")
    return out


def _safe_name(value: Any, label: str = "column") -> str:
    text = str(value or "").strip()
    if not text or len(text) > 240:
        raise DataTransformationError(f"{label} is required and must be 240 characters or fewer.")
    return text


def _safe_symbol(value: Any, label: str = "derived variable") -> str:
    text = str(value or "").strip()
    if not SYMBOL_RE.fullmatch(text):
        raise DataTransformationError(f"{label} must use a safe scientific symbol (letters, digits, underscore; starts with a letter).")
    return text


def _rows(payload: Any, label: str = "rows") -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise DataTransformationError(f"{label} must be an array of row objects.")
    if len(payload) > MAX_ROWS:
        raise DataTransformationError(f"{label} exceeds the {MAX_ROWS}-row transformation input limit.")
    out: list[dict[str, Any]] = []
    columns: set[str] = set()
    for i, row in enumerate(payload):
        if not isinstance(row, dict):
            raise DataTransformationError(f"{label}[{i}] must be an object.")
        clean: dict[str, Any] = {}
        for key, value in row.items():
            name = _safe_name(key, "column name")
            if isinstance(value, (dict, list, tuple, set)):
                raise DataTransformationError(f"Nested values are not supported in scientific transformation rows ({name}).")
            if isinstance(value, float) and not math.isfinite(value):
                raise DataTransformationError(f"Non-finite value found in {name} at row {i}.")
            clean[name] = value
            columns.add(name)
        out.append(clean)
    if len(columns) > MAX_COLUMNS:
        raise DataTransformationError(f"Dataset exceeds the {MAX_COLUMNS}-column transformation limit.")
    return out


def _columns(rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in rows:
        for key in row:
            if key not in out:
                out.append(key)
    return out


def _numeric_values(rows: list[dict[str, Any]], column: str) -> list[float]:
    values: list[float] = []
    for i, row in enumerate(rows):
        value = row.get(column)
        if _missing(value):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise DataTransformationError(f"{column} contains a non-numeric value at row {i}.") from exc
        if not math.isfinite(number):
            raise DataTransformationError(f"{column} contains a non-finite value at row {i}.")
        values.append(number)
    return values


# value in source unit -> base unit uses base = value * factor + offset.
_UNIT_CATALOG: dict[str, tuple[str, float, float]] = {
    "m": ("length", 1.0, 0.0), "cm": ("length", 0.01, 0.0), "mm": ("length", 0.001, 0.0), "km": ("length", 1000.0, 0.0),
    "kg": ("mass", 1.0, 0.0), "g": ("mass", 0.001, 0.0), "mg": ("mass", 1e-6, 0.0),
    "s": ("time", 1.0, 0.0), "min": ("time", 60.0, 0.0), "h": ("time", 3600.0, 0.0),
    "K": ("temperature", 1.0, 0.0), "degC": ("temperature", 1.0, 273.15), "degF": ("temperature", 5.0 / 9.0, 255.3722222222222),
    "Pa": ("pressure", 1.0, 0.0), "kPa": ("pressure", 1000.0, 0.0), "MPa": ("pressure", 1e6, 0.0), "bar": ("pressure", 1e5, 0.0),
    "J": ("energy", 1.0, 0.0), "kJ": ("energy", 1000.0, 0.0), "Wh": ("energy", 3600.0, 0.0), "kWh": ("energy", 3.6e6, 0.0),
    "W": ("power", 1.0, 0.0), "kW": ("power", 1000.0, 0.0), "MW": ("power", 1e6, 0.0),
    "rad": ("angle", 1.0, 0.0), "deg": ("angle", math.pi / 180.0, 0.0),
}


def convert_unit_value(value: Any, from_unit: str, to_unit: str) -> float:
    if from_unit not in _UNIT_CATALOG or to_unit not in _UNIT_CATALOG:
        raise DataTransformationError("Unit conversion must use the governed v0.55.0 unit catalog.")
    from_dim, from_factor, from_offset = _UNIT_CATALOG[from_unit]
    to_dim, to_factor, to_offset = _UNIT_CATALOG[to_unit]
    if from_dim != to_dim:
        raise DataTransformationError(f"Incompatible unit conversion: {from_unit} → {to_unit}.")
    x = _finite_number(value, "unit-conversion value")
    base = x * from_factor + from_offset
    result = (base - to_offset) / to_factor
    if not math.isfinite(result):
        raise DataTransformationError("Unit conversion produced a non-finite value.")
    return result


_ALLOWED_TYPES = {"derive", "filter", "rename", "select", "drop", "scale", "unit-convert", "cast", "impute"}
_FILTER_OPERATORS = {"eq", "ne", "lt", "lte", "gt", "gte", "in", "not-in", "is-missing", "not-missing"}


def normalize_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DataTransformationError("Transformation plan must be an object.")
    operations = payload.get("operations") or []
    if not isinstance(operations, list) or not operations:
        raise DataTransformationError("Transformation plan requires at least one operation.")
    if len(operations) > MAX_OPERATIONS:
        raise DataTransformationError(f"Transformation plan exceeds the {MAX_OPERATIONS}-operation limit.")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(operations):
        if not isinstance(raw, dict):
            raise DataTransformationError(f"operations[{index}] must be an object.")
        kind = str(raw.get("type") or "").strip().lower()
        if kind not in _ALLOWED_TYPES:
            raise DataTransformationError(f"Unsupported transformation type: {kind or '(missing)' }.")
        op: dict[str, Any] = {"type": kind, "id": str(raw.get("id") or f"op-{index + 1}")[:120]}
        if kind == "derive":
            op.update(name=_safe_symbol(raw.get("name")), expression=str(raw.get("expression") or "").strip()[:2000], unit=str(raw.get("unit") or "")[:120], label=str(raw.get("label") or raw.get("name") or "")[:240])
            if not op["expression"]:
                raise DataTransformationError("Derived-variable expression is required.")
        elif kind == "filter":
            operator = str(raw.get("operator") or "eq").strip().lower()
            if operator not in _FILTER_OPERATORS:
                raise DataTransformationError(f"Unsupported filter operator: {operator}.")
            op.update(column=_safe_name(raw.get("column")), operator=operator, value=raw.get("value"))
        elif kind == "rename":
            op.update(source=_safe_name(raw.get("from") or raw.get("source")), target=_safe_name(raw.get("to") or raw.get("target")))
        elif kind in {"select", "drop"}:
            cols = raw.get("columns") or []
            if not isinstance(cols, list) or not cols:
                raise DataTransformationError(f"{kind} requires a non-empty columns array.")
            op["columns"] = [_safe_name(c) for c in cols]
        elif kind == "scale":
            method = str(raw.get("method") or "z-score").strip().lower()
            if method not in {"z-score", "center", "min-max"}:
                raise DataTransformationError(f"Unsupported scale method: {method}.")
            source = _safe_name(raw.get("column") or raw.get("source"))
            target = _safe_name(raw.get("target") or source)
            op.update(column=source, target=target, method=method)
        elif kind == "unit-convert":
            source = _safe_name(raw.get("column") or raw.get("source"))
            target = _safe_name(raw.get("target") or source)
            from_unit, to_unit = str(raw.get("fromUnit") or ""), str(raw.get("toUnit") or "")
            if from_unit not in _UNIT_CATALOG or to_unit not in _UNIT_CATALOG:
                raise DataTransformationError("unit-convert requires fromUnit and toUnit from the governed catalog.")
            if _UNIT_CATALOG[from_unit][0] != _UNIT_CATALOG[to_unit][0]:
                raise DataTransformationError(f"Incompatible unit conversion: {from_unit} → {to_unit}.")
            op.update(column=source, target=target, fromUnit=from_unit, toUnit=to_unit)
        elif kind == "cast":
            cast_type = str(raw.get("dataType") or raw.get("to") or "").strip().lower()
            if cast_type not in {"number", "integer", "string", "boolean"}:
                raise DataTransformationError("cast dataType must be number, integer, string, or boolean.")
            op.update(column=_safe_name(raw.get("column")), dataType=cast_type)
        elif kind == "impute":
            method = str(raw.get("method") or "constant").strip().lower()
            if method not in {"constant", "mean", "median"}:
                raise DataTransformationError("impute method must be constant, mean, or median.")
            op.update(column=_safe_name(raw.get("column")), method=method)
            if method == "constant":
                op["value"] = raw.get("value")
        normalized.append(op)
    return {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "id": str(payload.get("id") or "transformation-plan")[:180],
        "title": str(payload.get("title") or "Scientific data transformation")[:240],
        "operations": normalized,
        "provenance": deepcopy(payload.get("provenance") or {}),
        "notes": str(payload.get("notes") or "")[:4000],
        "arbitraryCode": False,
    }


def _filter_pass(value: Any, operator: str, expected: Any) -> bool:
    if operator == "is-missing": return _missing(value)
    if operator == "not-missing": return not _missing(value)
    if operator in {"in", "not-in"}:
        choices = expected if isinstance(expected, list) else [expected]
        present = value in choices
        return present if operator == "in" else not present
    if operator in {"lt", "lte", "gt", "gte"}:
        if _missing(value): return False
        left, right = _finite_number(value, "filter value"), _finite_number(expected, "filter comparison")
        return {"lt": left < right, "lte": left <= right, "gt": left > right, "gte": left >= right}[operator]
    equal = value == expected or (not _missing(value) and not _missing(expected) and str(value) == str(expected))
    return equal if operator == "eq" else not equal


def _cast(value: Any, data_type: str) -> Any:
    if _missing(value): return None
    if data_type == "number": return _finite_number(value)
    if data_type == "integer":
        number = _finite_number(value)
        if not float(number).is_integer(): raise DataTransformationError(f"Cannot cast non-integer value {value!r} to integer.")
        return int(number)
    if data_type == "string": return str(value)
    if data_type == "boolean":
        if isinstance(value, bool): return value
        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "y"}: return True
        if text in {"false", "0", "no", "n"}: return False
        raise DataTransformationError(f"Cannot cast value {value!r} to boolean.")
    raise DataTransformationError(f"Unsupported cast type: {data_type}.")


def transform_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DataTransformationError("Transformation request must be an object.")
    rows = _rows(payload.get("rows") or [])
    plan = normalize_plan(payload.get("plan") or payload)
    units = {str(k): str(v)[:120] for k, v in (payload.get("units") or {}).items()} if isinstance(payload.get("units") or {}, dict) else {}
    original_rows = deepcopy(rows)
    input_hash = _sha({"rows": original_rows, "units": units})
    lineage: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []
    warnings: list[str] = []

    for index, op in enumerate(plan["operations"]):
        before_rows, before_cols = len(rows), _columns(rows)
        before_hash = _sha({"rows": rows, "units": units})
        kind = op["type"]
        op_warnings: list[str] = []
        if kind == "derive":
            if op["name"] in before_cols:
                raise DataTransformationError(f"Derived variable {op['name']} already exists; rename or drop it explicitly first.")
            unsafe = [c for c in before_cols if not SYMBOL_RE.fullmatch(c)]
            # Safe-expression compiler only needs declared symbols that are referenced; however all AST names must be declared.
            declared = [c for c in before_cols if SYMBOL_RE.fullmatch(c)]
            try:
                compiled = compile_equation(f"{op['name']} = {op['expression']}", declared)
            except EquationBuilderError as exc:
                suffix = f" Columns requiring rename before expression use: {', '.join(unsafe[:8])}." if unsafe else ""
                raise DataTransformationError(f"Derived-variable expression is invalid: {exc}.{suffix}") from exc
            for i, row in enumerate(rows):
                try:
                    row[op["name"]] = evaluate(compiled, row)
                except EquationBuilderError as exc:
                    raise DataTransformationError(f"Derived variable {op['name']} failed at row {i}: {exc}") from exc
            units[op["name"]] = op.get("unit") or ""
            derived.append({"name": op["name"], "label": op.get("label") or op["name"], "unit": units[op["name"]], "expression": compiled.normalized, "referencedSymbols": list(compiled.symbols)})
        elif kind == "filter":
            if op["column"] not in before_cols: raise DataTransformationError(f"Filter column not found: {op['column']}.")
            rows = [row for row in rows if _filter_pass(row.get(op["column"]), op["operator"], op.get("value"))]
            if not rows: op_warnings.append("Filter removed every row; review the predicate before downstream modeling.")
        elif kind == "rename":
            if op["source"] not in before_cols: raise DataTransformationError(f"Rename source column not found: {op['source']}.")
            if op["target"] in before_cols and op["target"] != op["source"]: raise DataTransformationError(f"Rename target already exists: {op['target']}.")
            for row in rows:
                if op["source"] in row: row[op["target"]] = row.pop(op["source"])
            if op["source"] in units: units[op["target"]] = units.pop(op["source"])
        elif kind == "select":
            missing = [c for c in op["columns"] if c not in before_cols]
            if missing: raise DataTransformationError(f"Select columns not found: {', '.join(missing)}.")
            rows = [{c: row.get(c) for c in op["columns"]} for row in rows]
            units = {c: units.get(c, "") for c in op["columns"] if c in units}
        elif kind == "drop":
            unknown = [c for c in op["columns"] if c not in before_cols]
            if unknown: op_warnings.append(f"Drop ignored missing column(s): {', '.join(unknown)}.")
            for row in rows:
                for c in op["columns"]: row.pop(c, None)
            for c in op["columns"]: units.pop(c, None)
        elif kind == "scale":
            if op["column"] not in before_cols: raise DataTransformationError(f"Scale column not found: {op['column']}.")
            values = _numeric_values(rows, op["column"])
            if not values: raise DataTransformationError(f"Scale column {op['column']} has no numeric values.")
            mu, lo, hi = mean(values), min(values), max(values)
            sd = math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))
            if op["method"] == "z-score" and sd == 0: raise DataTransformationError(f"Cannot z-score a constant column: {op['column']}.")
            if op["method"] == "min-max" and hi == lo: raise DataTransformationError(f"Cannot min-max scale a constant column: {op['column']}.")
            for row in rows:
                raw = row.get(op["column"])
                if _missing(raw): row[op["target"]] = None; continue
                x = _finite_number(raw, op["column"])
                if op["method"] == "z-score": y = (x - mu) / sd
                elif op["method"] == "center": y = x - mu
                else: y = (x - lo) / (hi - lo)
                row[op["target"]] = y
            units[op["target"]] = units.get(op["column"], "") if op["method"] == "center" else "1"
        elif kind == "unit-convert":
            if op["column"] not in before_cols: raise DataTransformationError(f"Unit-conversion column not found: {op['column']}.")
            declared_unit = units.get(op["column"])
            if declared_unit and declared_unit != op["fromUnit"]:
                raise DataTransformationError(f"Declared unit for {op['column']} is {declared_unit}, not {op['fromUnit']}.")
            for row in rows:
                raw = row.get(op["column"])
                row[op["target"]] = None if _missing(raw) else convert_unit_value(raw, op["fromUnit"], op["toUnit"])
            units[op["target"]] = op["toUnit"]
        elif kind == "cast":
            if op["column"] not in before_cols: raise DataTransformationError(f"Cast column not found: {op['column']}.")
            for row in rows: row[op["column"]] = _cast(row.get(op["column"]), op["dataType"])
        elif kind == "impute":
            if op["column"] not in before_cols: raise DataTransformationError(f"Imputation column not found: {op['column']}.")
            if op["method"] == "constant": fill = op.get("value")
            else:
                values = _numeric_values(rows, op["column"])
                if not values: raise DataTransformationError(f"Cannot {op['method']}-impute {op['column']} without observed numeric values.")
                fill = mean(values) if op["method"] == "mean" else median(values)
            replaced = 0
            for row in rows:
                if _missing(row.get(op["column"])): row[op["column"]] = fill; replaced += 1
            op_warnings.append(f"Imputed {replaced} missing value(s); downstream inference should account for the imputation method.")
        if len(rows) > MAX_OUTPUT_ROWS: raise DataTransformationError(f"Transformation output exceeds {MAX_OUTPUT_ROWS} rows.")
        after_cols = _columns(rows)
        if len(after_cols) > MAX_COLUMNS: raise DataTransformationError(f"Transformation output exceeds {MAX_COLUMNS} columns.")
        after_hash = _sha({"rows": rows, "units": units})
        lineage.append({
            "index": index + 1, "id": op["id"], "type": kind, "operationHash": _sha(op),
            "inputHash": before_hash, "outputHash": after_hash,
            "rowsBefore": before_rows, "rowsAfter": len(rows), "columnsBefore": len(before_cols), "columnsAfter": len(after_cols),
            "warnings": op_warnings,
        })
        warnings.extend(op_warnings)

    output_hash = _sha({"rows": rows, "units": units})
    profile = profile_dataset({"rows": rows, "dataDictionary": [{"name": c, "unit": units.get(c, "")} for c in _columns(rows)]})["profile"]
    result = {
        "schema": RESULT_SCHEMA, "version": VERSION, "plan": plan, "planHash": _sha(plan),
        "inputHash": input_hash, "outputHash": output_hash, "rowCount": len(rows), "columnCount": len(_columns(rows)),
        "columns": _columns(rows), "units": units, "rows": rows, "derivedVariables": derived, "lineage": lineage,
        "profile": profile, "warnings": warnings, "generatedAt": _utcnow(), "arbitraryCode": False,
    }
    result["resultHash"] = _sha({k: v for k, v in result.items() if k not in {"generatedAt", "resultHash"}})
    return {"ok": True, "version": VERSION, "result": result}


def join_datasets(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict): raise DataTransformationError("Dataset join request must be an object.")
    left = _rows(payload.get("leftRows") or [], "leftRows")
    right = _rows(payload.get("rightRows") or [], "rightRows")
    left_key = _safe_name(payload.get("leftKey")); right_key = _safe_name(payload.get("rightKey") or left_key)
    how = str(payload.get("how") or "left").lower()
    if how not in {"left", "inner"}: raise DataTransformationError("Join mode must be left or inner.")
    suffix = str(payload.get("suffix") or "_right")[:40]
    if not suffix: suffix = "_right"
    left_cols, right_cols = _columns(left), _columns(right)
    if left_key not in left_cols: raise DataTransformationError(f"Left join key not found: {left_key}.")
    if right_key not in right_cols: raise DataTransformationError(f"Right join key not found: {right_key}.")
    requested = payload.get("rightColumns") or [c for c in right_cols if c != right_key]
    if not isinstance(requested, list): raise DataTransformationError("rightColumns must be an array.")
    requested = [_safe_name(c) for c in requested]
    unknown = [c for c in requested if c not in right_cols]
    if unknown: raise DataTransformationError(f"Right join columns not found: {', '.join(unknown)}.")
    index: dict[str, list[dict[str, Any]]] = {}
    for row in right:
        key = _canonical(row.get(right_key))
        index.setdefault(key, []).append(row)
    out: list[dict[str, Any]] = []
    matched_left = 0
    for lrow in left:
        matches = index.get(_canonical(lrow.get(left_key)), [])
        if matches: matched_left += 1
        if not matches and how == "left": matches = [None]
        for rrow in matches:
            joined = dict(lrow)
            for c in requested:
                target = c if c not in joined else f"{c}{suffix}"
                joined[target] = None if rrow is None else rrow.get(c)
            out.append(joined)
            if len(out) > MAX_OUTPUT_ROWS: raise DataTransformationError(f"Join output exceeds {MAX_OUTPUT_ROWS} rows; review key multiplicity.")
    result = {
        "schema": JOIN_SCHEMA, "version": VERSION, "how": how, "leftKey": left_key, "rightKey": right_key,
        "rightColumns": requested, "rowCount": len(out), "columnCount": len(_columns(out)), "matchedLeftRows": matched_left,
        "unmatchedLeftRows": len(left) - matched_left, "rows": out,
        "leftHash": _sha(left), "rightHash": _sha(right), "outputHash": _sha(out), "generatedAt": _utcnow(),
        "arbitraryCode": False,
    }
    result["joinHash"] = _sha({k: v for k, v in result.items() if k not in {"generatedAt", "joinHash"}})
    return {"ok": True, "version": VERSION, "result": result}


def policies() -> dict[str, Any]:
    return {
        "ok": True, "version": VERSION, "planSchema": PLAN_SCHEMA, "resultSchema": RESULT_SCHEMA, "joinSchema": JOIN_SCHEMA,
        "operations": sorted(_ALLOWED_TYPES), "filterOperators": sorted(_FILTER_OPERATORS),
        "scaleMethods": ["z-score", "center", "min-max"], "imputationMethods": ["constant", "mean", "median"],
        "joinModes": ["left", "inner"], "unitCatalog": {k: v[0] for k, v in sorted(_UNIT_CATALOG.items())},
        "limits": {"inputRows": MAX_ROWS, "outputRows": MAX_OUTPUT_ROWS, "columns": MAX_COLUMNS, "operations": MAX_OPERATIONS},
        "boundaries": {"arbitraryCode": False, "arbitrarySql": False, "network": False, "filesystem": False, "automaticUnitInference": False, "automaticImputation": False, "automaticFeatureEngineering": False},
    }


def health() -> dict[str, Any]:
    return {"ok": True, "status": "scientific-data-transformation-ready", "version": VERSION, "architecture": "governed-reproducible-transformation-lineage", "safeDerivedVariables": True, "unitAware": True, "joins": True, "arbitraryCode": False}
