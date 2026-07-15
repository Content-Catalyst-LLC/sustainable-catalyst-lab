from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from math import sqrt
from statistics import mean, median
from typing import Any

VERSION = "0.28.1"
MAX_ROWS = 5000
MAX_COLUMNS = 200

class DatasetProfileError(ValueError):
    pass

def _missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())

def _kind(values: list[Any]) -> str:
    present = [value for value in values if not _missing(value)]
    if not present:
        return "unknown"
    if all(isinstance(value, bool) or str(value).lower() in {"true", "false"} for value in present):
        return "boolean"
    try:
        numeric = [float(value) for value in present]
        if all(float(value).is_integer() for value in numeric):
            return "integer"
        return "number"
    except (TypeError, ValueError):
        pass
    if all(isinstance(value, (dict, list)) for value in present):
        return "object"
    return "string"

def _numeric(values: list[Any]) -> dict[str, float] | None:
    converted: list[float] = []
    for value in values:
        if _missing(value):
            continue
        try:
            converted.append(float(value))
        except (TypeError, ValueError):
            return None
    if not converted:
        return None
    avg = mean(converted)
    return {
        "min": min(converted),
        "max": max(converted),
        "mean": avg,
        "median": median(converted),
        "standardDeviation": sqrt(sum((value - avg) ** 2 for value in converted) / len(converted)),
    }

def profile_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise DatasetProfileError("rows must be an array of objects")
    if len(rows) > MAX_ROWS:
        raise DatasetProfileError(f"dataset profile exceeds the {MAX_ROWS}-row request limit")
    if any(not isinstance(row, dict) for row in rows):
        raise DatasetProfileError("each dataset row must be an object")
    columns: list[str] = []
    for row in rows:
        for key in row:
            name = str(key)[:240]
            if name not in columns:
                columns.append(name)
    requested_dictionary = payload.get("dataDictionary") or []
    dictionary_by_name = {str(item.get("name")): item for item in requested_dictionary if isinstance(item, dict) and item.get("name")}
    if not columns:
        columns = list(dictionary_by_name)
    if len(columns) > MAX_COLUMNS:
        raise DatasetProfileError(f"dataset profile exceeds the {MAX_COLUMNS}-variable request limit")
    variables = []
    missing_total = 0
    issues = []
    for name in columns:
        values = [row.get(name) for row in rows]
        present = [value for value in values if not _missing(value)]
        missing_count = len(values) - len(present)
        missing_total += missing_count
        meta = dictionary_by_name.get(name, {})
        data_type = str(meta.get("dataType") or _kind(values))
        variable: dict[str, Any] = {
            "name": name,
            "label": str(meta.get("label") or name)[:240],
            "dataType": data_type,
            "unit": str(meta.get("unit") or "")[:120],
            "role": str(meta.get("role") or "attribute")[:40],
            "count": len(present),
            "missingCount": missing_count,
            "missingRate": missing_count / len(values) if values else 0.0,
            "uniqueCount": len({repr(value) for value in present}),
        }
        stats = _numeric(values) if data_type in {"number", "integer"} else None
        if stats:
            variable["numeric"] = stats
        elif data_type == "string" and present:
            lengths = [len(str(value)) for value in present]
            variable["string"] = {"minLength": min(lengths), "maxLength": max(lengths), "topValues": Counter(str(value) for value in present).most_common(10)}
        if str(meta.get("missingPolicy") or "allowed") == "not-allowed" and missing_count:
            issues.append({"severity": "error", "code": "missing_not_allowed", "variable": name, "message": f"{name} contains missing values."})
        variables.append(variable)
    if not columns:
        issues.append({"severity": "error", "code": "columns_missing", "message": "No variables were detected."})
    status = "invalid" if any(item["severity"] == "error" for item in issues) else ("warning" if issues else "valid")
    validation = {"status": status, "issues": issues, "validatedAt": datetime.now(timezone.utc).isoformat()}
    profile = {
        "schema": "sc-lab-dataset-profile/0.28.1",
        "version": VERSION,
        "rowCount": len(rows),
        "columnCount": len(columns),
        "missingCellCount": missing_total,
        "missingRate": missing_total / (len(rows) * len(columns)) if rows and columns else 0.0,
        "variables": variables,
        "validation": validation,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "limits": {"maxRows": MAX_ROWS, "maxColumns": MAX_COLUMNS},
    }
    return {"ok": True, "version": VERSION, "profile": profile, "validation": validation}

def health() -> dict[str, Any]:
    return {"ok": True, "status": "ready", "version": VERSION, "architecture": "governed-dataset-profiler", "maxRows": MAX_ROWS, "maxColumns": MAX_COLUMNS, "arbitraryCode": False}
