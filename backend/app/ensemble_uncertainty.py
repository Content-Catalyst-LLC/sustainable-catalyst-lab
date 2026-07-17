from __future__ import annotations

import copy
import json
import math
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from scipy.stats import qmc

VERSION = "0.34.1"
STUDY_SCHEMA = "sc-lab-ensemble-study/0.34.1"
EVALUATION_SCHEMA = "sc-lab-ensemble-evaluation/0.34.1"
RESULT_SCHEMA = "sc-lab-ensemble-analysis/0.34.1"
EVENT_SCHEMA = "sc-lab-ensemble-event/0.34.1"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")
DESIGNS = {"monte-carlo", "latin-hypercube", "sobol", "saltelli-sobol"}
DISTRIBUTIONS = {"uniform", "normal", "lognormal", "triangular", "discrete"}
STATES = {"draft", "queued", "running", "completed", "failed", "cancelled"}


class EnsembleError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 500) -> str:
    return str(value or "").strip()[:limit]


def _number(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise EnsembleError(f"{name} must be numeric.") from exc
    if not math.isfinite(result):
        raise EnsembleError(f"{name} must be finite.")
    return result


def _set_path(target: dict[str, Any], path: str, value: Any) -> None:
    parts = [part for part in path.split(".") if part]
    if not parts:
        raise EnsembleError("Variable paths cannot be empty.")
    cursor = target
    for part in parts[:-1]:
        existing = cursor.get(part)
        if existing is None:
            cursor[part] = {}
            existing = cursor[part]
        if not isinstance(existing, dict):
            raise EnsembleError(f"Cannot assign variable path {path}; {part} is not an object.")
        cursor = existing
    cursor[parts[-1]] = value


def _get_path(value: Any, path: str) -> Any:
    cursor = value
    for part in [item for item in path.split(".") if item]:
        if isinstance(cursor, dict) and part in cursor:
            cursor = cursor[part]
        elif isinstance(cursor, list) and part.isdigit() and int(part) < len(cursor):
            cursor = cursor[int(part)]
        else:
            raise KeyError(path)
    return cursor


def _extract_numeric(result: Any, path: str) -> float:
    candidates = [result]
    if isinstance(result, dict):
        for key in ("result", "output", "outputs", "values", "summary"):
            if key in result:
                candidates.append(result[key])
        nested = result.get("result")
        if isinstance(nested, dict):
            for key in ("result", "output", "outputs", "values", "summary"):
                if key in nested:
                    candidates.append(nested[key])
    errors: list[str] = []
    for candidate in candidates:
        try:
            raw = _get_path(candidate, path) if path else candidate
            return _number(raw, f"Output path {path or '<root>'}")
        except (KeyError, EnsembleError) as exc:
            errors.append(str(exc))
    raise EnsembleError(f"Output path {path!r} did not resolve to a numeric value.")


def _normalize_variable(raw: dict[str, Any]) -> dict[str, Any]:
    name = _text(raw.get("name"), 180)
    path = _text(raw.get("path") or name, 300)
    distribution = _text(raw.get("distribution"), 60).lower() or "uniform"
    if not ID_RE.match(name):
        raise EnsembleError("Each uncertain variable requires a valid name.")
    if distribution not in DISTRIBUTIONS:
        raise EnsembleError(f"Unsupported distribution for {name}.")
    record: dict[str, Any] = {"name": name, "path": path, "distribution": distribution}
    if distribution == "uniform":
        low = _number(raw.get("low"), f"{name}.low")
        high = _number(raw.get("high"), f"{name}.high")
        if high <= low:
            raise EnsembleError(f"{name}.high must exceed low.")
        record.update(low=low, high=high)
    elif distribution == "normal":
        mean = _number(raw.get("mean", 0), f"{name}.mean")
        std = _number(raw.get("stdDev"), f"{name}.stdDev")
        if std <= 0:
            raise EnsembleError(f"{name}.stdDev must be positive.")
        record.update(mean=mean, stdDev=std)
    elif distribution == "lognormal":
        mean_log = _number(raw.get("meanLog", 0), f"{name}.meanLog")
        std_log = _number(raw.get("stdLog"), f"{name}.stdLog")
        if std_log <= 0:
            raise EnsembleError(f"{name}.stdLog must be positive.")
        record.update(meanLog=mean_log, stdLog=std_log)
    elif distribution == "triangular":
        low = _number(raw.get("low"), f"{name}.low")
        mode = _number(raw.get("mode"), f"{name}.mode")
        high = _number(raw.get("high"), f"{name}.high")
        if not low <= mode <= high or high <= low:
            raise EnsembleError(f"{name} triangular bounds must satisfy low <= mode <= high.")
        record.update(low=low, mode=mode, high=high)
    else:
        values = raw.get("values") if isinstance(raw.get("values"), list) else []
        if not values or len(values) > 100:
            raise EnsembleError(f"{name}.values must contain 1 to 100 discrete values.")
        probabilities = raw.get("probabilities") if isinstance(raw.get("probabilities"), list) else []
        if probabilities:
            if len(probabilities) != len(values):
                raise EnsembleError(f"{name}.probabilities must match values.")
            probs = [_number(item, f"{name}.probabilities") for item in probabilities]
            if any(item < 0 for item in probs) or sum(probs) <= 0:
                raise EnsembleError(f"{name}.probabilities must be non-negative and sum above zero.")
            total = sum(probs)
            probabilities = [item / total for item in probs]
        else:
            probabilities = [1.0 / len(values)] * len(values)
        record.update(values=copy.deepcopy(values), probabilities=probabilities)
    return record


def _transform(unit: np.ndarray, variable: dict[str, Any]) -> np.ndarray:
    u = np.clip(np.asarray(unit, dtype=float), 1e-12, 1 - 1e-12)
    kind = variable["distribution"]
    if kind == "uniform":
        return variable["low"] + u * (variable["high"] - variable["low"])
    if kind == "normal":
        return stats.norm.ppf(u, loc=variable["mean"], scale=variable["stdDev"])
    if kind == "lognormal":
        return stats.lognorm.ppf(u, s=variable["stdLog"], scale=math.exp(variable["meanLog"]))
    if kind == "triangular":
        c = (variable["mode"] - variable["low"]) / (variable["high"] - variable["low"])
        return stats.triang.ppf(u, c=c, loc=variable["low"], scale=variable["high"] - variable["low"])
    cumulative = np.cumsum(np.asarray(variable["probabilities"], dtype=float))
    indices = np.searchsorted(cumulative, u, side="right")
    indices = np.minimum(indices, len(variable["values"]) - 1)
    return np.asarray([variable["values"][int(index)] for index in indices], dtype=object)


def _unit_design(method: str, samples: int, dimensions: int, seed: int) -> np.ndarray:
    if method == "monte-carlo":
        return np.random.default_rng(seed).random((samples, dimensions))
    if method == "latin-hypercube":
        return qmc.LatinHypercube(d=dimensions, seed=seed).random(samples)
    exponent = max(1, math.ceil(math.log2(samples)))
    matrix = qmc.Sobol(d=dimensions, scramble=True, seed=seed).random_base2(exponent)
    return matrix[:samples]


def generate_design(definition: dict[str, Any]) -> list[dict[str, Any]]:
    variables = definition["variables"]
    method = definition["design"]["method"]
    samples = definition["design"]["samples"]
    seed = definition["design"]["seed"]
    dimensions = len(variables)
    records: list[dict[str, Any]] = []
    if method != "saltelli-sobol":
        unit = _unit_design(method, samples, dimensions, seed)
        transformed = [_transform(unit[:, index], variable) for index, variable in enumerate(variables)]
        for row in range(samples):
            values = {variables[col]["name"]: transformed[col][row].item() if hasattr(transformed[col][row], "item") else transformed[col][row] for col in range(dimensions)}
            records.append({"designIndex": row, "role": "sample", "baseIndex": row, "parameterName": None, "values": values})
        return records
    unit = _unit_design("sobol", samples, dimensions * 2, seed)
    a = unit[:, :dimensions]
    b = unit[:, dimensions:]
    transformed_a = [_transform(a[:, index], variable) for index, variable in enumerate(variables)]
    transformed_b = [_transform(b[:, index], variable) for index, variable in enumerate(variables)]
    index = 0
    for row in range(samples):
        values_a = {variables[col]["name"]: transformed_a[col][row].item() if hasattr(transformed_a[col][row], "item") else transformed_a[col][row] for col in range(dimensions)}
        values_b = {variables[col]["name"]: transformed_b[col][row].item() if hasattr(transformed_b[col][row], "item") else transformed_b[col][row] for col in range(dimensions)}
        records.append({"designIndex": index, "role": "A", "baseIndex": row, "parameterName": None, "values": values_a}); index += 1
        records.append({"designIndex": index, "role": "B", "baseIndex": row, "parameterName": None, "values": values_b}); index += 1
        for col, variable in enumerate(variables):
            mixed = dict(values_a)
            mixed[variable["name"]] = values_b[variable["name"]]
            records.append({"designIndex": index, "role": "AB", "baseIndex": row, "parameterName": variable["name"], "values": mixed}); index += 1
    return records


def normalize_definition(payload: dict[str, Any], registry: Any) -> dict[str, Any]:
    source = payload.get("study") if isinstance(payload.get("study"), dict) else payload
    study_id = _text(source.get("id"), 180) or f"ensemble-{secrets.token_hex(8)}"
    if not ID_RE.match(study_id):
        raise EnsembleError("Study ID contains unsupported characters.")
    variables_raw = source.get("variables") if isinstance(source.get("variables"), list) else []
    if not 1 <= len(variables_raw) <= 50:
        raise EnsembleError("Ensemble studies require 1 to 50 uncertain variables.")
    variables = [_normalize_variable(item) for item in variables_raw if isinstance(item, dict)]
    if len(variables) != len(variables_raw) or len({item["name"] for item in variables}) != len(variables):
        raise EnsembleError("Uncertain variable names must be unique.")
    design_raw = source.get("design") if isinstance(source.get("design"), dict) else {}
    method = _text(design_raw.get("method"), 60).lower() or "latin-hypercube"
    if method not in DESIGNS:
        raise EnsembleError("Unsupported ensemble design method.")
    try:
        samples = int(design_raw.get("samples", 128))
        seed = int(design_raw.get("seed", 2026))
    except (TypeError, ValueError) as exc:
        raise EnsembleError("Design samples and seed must be integers.") from exc
    if samples < 4 or samples > 10000:
        raise EnsembleError("Design samples must be between 4 and 10,000.")
    members_raw = source.get("members") if isinstance(source.get("members"), list) else []
    if not members_raw:
        model_ref = source.get("model") if isinstance(source.get("model"), dict) else {}
        if model_ref:
            members_raw = [model_ref]
    if not 1 <= len(members_raw) <= 32:
        raise EnsembleError("Ensembles require 1 to 32 registered model members.")
    members: list[dict[str, Any]] = []
    total_weight = 0.0
    for index, raw in enumerate(members_raw):
        if not isinstance(raw, dict):
            raise EnsembleError("Each ensemble member must be an object.")
        model_id = _text(raw.get("modelId") or raw.get("id"), 180)
        version = _text(raw.get("modelVersion") or raw.get("version") or raw.get("alias") or "production", 120)
        if not model_id:
            raise EnsembleError("Each ensemble member requires modelId.")
        try:
            resolved = registry.get(model_id, version)["model"]
        except Exception as exc:
            status = getattr(exc, "status_code", 422)
            raise EnsembleError(f"Unable to resolve ensemble member {model_id}@{version}: {exc}", status) from exc
        if resolved.get("type") != "registered-method" or not resolved.get("methodId"):
            raise EnsembleError("v0.34.1 ensemble execution supports registered-method model versions only.")
        weight = _number(raw.get("weight", 1), f"members[{index}].weight")
        if weight <= 0:
            raise EnsembleError("Ensemble member weights must be positive.")
        total_weight += weight
        members.append({
            "memberIndex": index,
            "modelId": resolved["modelId"],
            "modelVersion": resolved["modelVersion"],
            "modelHash": resolved["modelHash"],
            "environmentLockHash": resolved.get("environment", {}).get("lockHash"),
            "methodId": resolved["methodId"],
            "weight": weight,
            "defaultInputs": copy.deepcopy(resolved.get("defaultInputs") or {}),
            "parameters": copy.deepcopy(resolved.get("parameters") or {}),
        })
    for member in members:
        member["normalizedWeight"] = member["weight"] / total_weight
    output_raw = source.get("output") if isinstance(source.get("output"), dict) else {}
    output_path = _text(output_raw.get("path"), 400)
    if not output_path:
        raise EnsembleError("output.path is required.")
    evaluation_count = samples * len(members) * (len(variables) + 2 if method == "saltelli-sobol" else 1)
    try:
        maximum_evaluations = min(200000, int(source.get("maximumEvaluations", 50000) or 50000))
    except (TypeError, ValueError) as exc:
        raise EnsembleError("maximumEvaluations must be an integer.") from exc
    if maximum_evaluations < 1:
        raise EnsembleError("maximumEvaluations must be positive.")
    if evaluation_count > maximum_evaluations:
        raise EnsembleError(f"Study requires {evaluation_count} evaluations, above the configured limit of {maximum_evaluations}.", 409)
    record = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "id": study_id,
        "title": _text(source.get("title"), 300) or study_id,
        "description": _text(source.get("description"), 4000) or None,
        "projectId": _text(source.get("projectId"), 180) or "default",
        "members": members,
        "variables": variables,
        "design": {"method": method, "samples": samples, "seed": seed, "evaluationCount": evaluation_count},
        "baseInputs": copy.deepcopy(source.get("baseInputs")) if isinstance(source.get("baseInputs"), dict) else {},
        "parameters": copy.deepcopy(source.get("parameters")) if isinstance(source.get("parameters"), dict) else {},
        "output": {"path": output_path, "label": _text(output_raw.get("label"), 300) or output_path, "unit": _text(output_raw.get("unit"), 80) or None},
        "analysis": {
            "confidence": max(0.5, min(0.999, _number((source.get("analysis") or {}).get("confidence", 0.95) if isinstance(source.get("analysis"), dict) else 0.95, "analysis.confidence"))),
            "thresholds": [_number(item, "analysis.thresholds") for item in ((source.get("analysis") or {}).get("thresholds", []) if isinstance(source.get("analysis"), dict) and isinstance((source.get("analysis") or {}).get("thresholds"), list) else [])][:20],
            "globalSensitivity": True,
            "uncertaintyIntervals": True,
        },
        "execution": {
            "priority": max(0, min(100, int((source.get("execution") or {}).get("priority", 50) if isinstance(source.get("execution"), dict) else 50))),
            "maxAttempts": max(1, min(20, int((source.get("execution") or {}).get("maxAttempts", 3) if isinstance(source.get("execution"), dict) else 3))),
            "timeoutSeconds": max(1, min(86400, int((source.get("execution") or {}).get("timeoutSeconds", 900) if isinstance(source.get("execution"), dict) else 900))),
        },
        "governance": {"registeredModelsOnly": True, "arbitraryCode": False, "independentInputs": True},
        "createdAt": _now(),
    }
    record["definitionHash"] = _hash({k: v for k, v in record.items() if k not in {"createdAt", "definitionHash"}})
    return record


def _summary(values: np.ndarray, confidence: float, thresholds: list[float]) -> dict[str, Any]:
    values = np.asarray(values, dtype=float)
    alpha = (1 - confidence) / 2
    result = {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "standardDeviation": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
        "variance": float(np.var(values, ddof=1)) if values.size > 1 else 0.0,
        "minimum": float(np.min(values)),
        "maximum": float(np.max(values)),
        "median": float(np.median(values)),
        "quantiles": {
            "p01": float(np.quantile(values, 0.01)), "p05": float(np.quantile(values, 0.05)),
            "p25": float(np.quantile(values, 0.25)), "p75": float(np.quantile(values, 0.75)),
            "p95": float(np.quantile(values, 0.95)), "p99": float(np.quantile(values, 0.99)),
        },
        "confidenceInterval": [float(np.quantile(values, alpha)), float(np.quantile(values, 1 - alpha))],
        "thresholdProbabilities": [{"threshold": threshold, "probabilityAbove": float(np.mean(values > threshold)), "probabilityBelowOrEqual": float(np.mean(values <= threshold))} for threshold in thresholds],
    }
    return result


def analyze_results(definition: dict[str, Any], evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [item for item in evaluations if item.get("status") == "completed" and item.get("outputValue") is not None]
    if not completed:
        raise EnsembleError("No completed numeric evaluations are available for analysis.", 409)
    members = definition["members"]
    variables = definition["variables"]
    confidence = definition["analysis"]["confidence"]
    thresholds = definition["analysis"]["thresholds"]
    per_member: list[dict[str, Any]] = []
    for member in members:
        values = [float(item["outputValue"]) for item in completed if item["memberIndex"] == member["memberIndex"]]
        per_member.append({"modelId": member["modelId"], "modelVersion": member["modelVersion"], "weight": member["normalizedWeight"], "uncertainty": _summary(np.asarray(values), confidence, thresholds) if values else None})
    groups: dict[tuple[str, int, str | None], dict[int, float]] = {}
    sample_values: dict[tuple[str, int, str | None], dict[str, Any]] = {}
    for item in completed:
        key = (item["role"], int(item["baseIndex"]), item.get("parameterName"))
        groups.setdefault(key, {})[int(item["memberIndex"])] = float(item["outputValue"])
        sample_values[key] = item["sampleValues"]
    pooled_records: list[dict[str, Any]] = []
    for key, outputs in groups.items():
        if len(outputs) != len(members):
            continue
        pooled = sum(outputs[member["memberIndex"]] * member["normalizedWeight"] for member in members)
        pooled_records.append({"role": key[0], "baseIndex": key[1], "parameterName": key[2], "sampleValues": sample_values[key], "output": float(pooled)})
    if not pooled_records:
        raise EnsembleError("No complete cross-member sample groups are available for ensemble analysis.", 409)
    pooled_outputs = np.asarray([item["output"] for item in pooled_records], dtype=float)
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "studyId": definition["id"],
        "definitionHash": definition["definitionHash"],
        "completedEvaluations": len(completed),
        "completeEnsembleSamples": len(pooled_records),
        "memberCount": len(members),
        "uncertainty": _summary(pooled_outputs, confidence, thresholds),
        "members": per_member,
        "sensitivity": {"method": "correlation-and-standardized-regression", "variables": []},
        "createdAt": _now(),
    }
    method = definition["design"]["method"]
    if method == "saltelli-sobol":
        by_role = {(item["role"], item["baseIndex"], item.get("parameterName")): item["output"] for item in pooled_records}
        a = np.asarray([by_role[("A", index, None)] for index in range(definition["design"]["samples"]) if ("A", index, None) in by_role], dtype=float)
        b = np.asarray([by_role[("B", index, None)] for index in range(definition["design"]["samples"]) if ("B", index, None) in by_role], dtype=float)
        if len(a) == len(b) == definition["design"]["samples"]:
            variance = float(np.var(np.concatenate([a, b]), ddof=1))
            indices = []
            if variance > 0:
                for variable in variables:
                    ab = np.asarray([by_role[("AB", index, variable["name"])] for index in range(definition["design"]["samples"]) if ("AB", index, variable["name"]) in by_role], dtype=float)
                    if len(ab) == len(a):
                        first = float(np.mean(b * (ab - a)) / variance)
                        total = float(0.5 * np.mean((a - ab) ** 2) / variance)
                        indices.append({"name": variable["name"], "firstOrder": first, "totalOrder": total})
            result["sensitivity"] = {"method": "saltelli-sobol", "outputVariance": variance, "variables": indices}
    else:
        matrix_rows = [item for item in pooled_records if item["role"] == "sample"]
        numeric_variables = [item for item in variables if item["distribution"] != "discrete"]
        if len(matrix_rows) >= 3 and numeric_variables:
            x = np.asarray([[float(row["sampleValues"][variable["name"]]) for variable in numeric_variables] for row in matrix_rows], dtype=float)
            y = np.asarray([row["output"] for row in matrix_rows], dtype=float)
            x_standard = (x - np.mean(x, axis=0)) / np.where(np.std(x, axis=0, ddof=1) > 0, np.std(x, axis=0, ddof=1), 1)
            y_std_value = float(np.std(y, ddof=1))
            y_standard = (y - np.mean(y)) / (y_std_value if y_std_value > 0 else 1)
            coefficients = np.linalg.lstsq(np.column_stack([np.ones(len(x_standard)), x_standard]), y_standard, rcond=None)[0][1:]
            records = []
            for index, variable in enumerate(numeric_variables):
                pearson = stats.pearsonr(x[:, index], y).statistic if np.std(x[:, index]) > 0 and np.std(y) > 0 else 0.0
                spearman = stats.spearmanr(x[:, index], y).statistic if np.std(x[:, index]) > 0 and np.std(y) > 0 else 0.0
                records.append({"name": variable["name"], "pearson": float(pearson), "spearman": float(spearman), "standardizedRegression": float(coefficients[index])})
            result["sensitivity"]["variables"] = records
    result["analysisHash"] = _hash({k: v for k, v in result.items() if k not in {"createdAt", "analysisHash"}})
    return result


def policies(max_studies: int = 2000, max_evaluations: int = 200000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "ensemble-simulation-global-sensitivity-uncertainty",
        "designs": sorted(DESIGNS),
        "distributions": sorted(DISTRIBUTIONS),
        "registeredModelsOnly": True,
        "immutableModelVersions": True,
        "weightedModelEnsembles": True,
        "globalSensitivity": ["pearson", "spearman", "standardized-regression", "saltelli-sobol"],
        "uncertainty": ["moments", "quantiles", "confidence-intervals", "threshold-probabilities"],
        "arbitraryCode": False,
        "limits": {"studies": max_studies, "evaluations": max_evaluations, "variables": 50, "members": 32},
    }


class EnsembleStudyManager:
    def __init__(self, db_path: str, registry: Any, dispatcher: Any, max_studies: int = 2000, max_evaluations: int = 200000, history_limit: int = 50000):
        self.db_path = str(db_path)
        self.registry = registry
        self.dispatcher = dispatcher
        self.max_studies = max(1, int(max_studies))
        self.max_evaluations = max(100, int(max_evaluations))
        self.history_limit = max(100, int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS studies(
              id TEXT PRIMARY KEY,title TEXT NOT NULL,project_id TEXT NOT NULL,status TEXT NOT NULL,
              definition_hash TEXT NOT NULL,definition_json TEXT NOT NULL,analysis_json TEXT,error_text TEXT,
              created_at TEXT NOT NULL,started_at TEXT,completed_at TEXT,updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evaluations(
              id TEXT PRIMARY KEY,study_id TEXT NOT NULL,design_index INTEGER NOT NULL,role TEXT NOT NULL,
              base_index INTEGER NOT NULL,parameter_name TEXT,member_index INTEGER NOT NULL,model_id TEXT NOT NULL,
              model_version TEXT NOT NULL,member_weight REAL NOT NULL,sample_json TEXT NOT NULL,inputs_json TEXT NOT NULL,
              parameters_json TEXT NOT NULL,queue_id TEXT,status TEXT NOT NULL,result_json TEXT,output_value REAL,error_text TEXT,
              created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
              UNIQUE(study_id,design_index,member_index),FOREIGN KEY(study_id) REFERENCES studies(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_ensemble_eval_study_status ON evaluations(study_id,status);
            CREATE INDEX IF NOT EXISTS idx_ensemble_eval_queue ON evaluations(queue_id);
            CREATE TABLE IF NOT EXISTS events(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,study_id TEXT NOT NULL,event_type TEXT NOT NULL,
              actor TEXT NOT NULL,details_json TEXT NOT NULL,created_at TEXT NOT NULL
            );
            """)

    def _event(self, con: sqlite3.Connection, study_id: str, event_type: str, actor: str, details: dict[str, Any]) -> None:
        con.execute("INSERT INTO events(study_id,event_type,actor,details_json,created_at) VALUES(?,?,?,?,?)", (study_id, event_type, actor or "system", _stable(details), _now()))
        con.execute("DELETE FROM events WHERE sequence NOT IN (SELECT sequence FROM events ORDER BY sequence DESC LIMIT ?)", (self.history_limit,))

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        definition = normalize_definition(payload, self.registry)
        return {"ok": True, "study": definition, "policies": policies(self.max_studies, self.max_evaluations)}

    def create(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        definition = normalize_definition(payload, self.registry)
        now = _now()
        with self._connect() as con:
            count = con.execute("SELECT COUNT(*) FROM studies").fetchone()[0]
            if count >= self.max_studies:
                raise EnsembleError("Ensemble study capacity reached.", 409)
            existing = con.execute("SELECT definition_hash FROM studies WHERE id=?", (definition["id"],)).fetchone()
            if existing:
                if existing["definition_hash"] == definition["definitionHash"]:
                    return {"ok": True, "created": False, **self.get(definition["id"], reconcile=False)}
                raise EnsembleError("Study IDs are immutable; choose a new ID for a changed definition.", 409)
            con.execute("INSERT INTO studies(id,title,project_id,status,definition_hash,definition_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)", (definition["id"], definition["title"], definition["projectId"], "draft", definition["definitionHash"], _stable(definition), now, now))
            self._event(con, definition["id"], "study-created", actor, {"definitionHash": definition["definitionHash"], "evaluationCount": definition["design"]["evaluationCount"]})
        return {"ok": True, "created": True, **self.get(definition["id"], reconcile=False)}

    def start(self, study_id: str, actor: str = "operator") -> dict[str, Any]:
        study_id = _text(study_id, 180)
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM studies WHERE id=?", (study_id,)).fetchone()
            if not row:
                con.execute("ROLLBACK"); raise EnsembleError("Ensemble study was not found.", 404)
            if row["status"] not in {"draft", "failed"}:
                con.execute("ROLLBACK"); raise EnsembleError("Only draft or failed studies can be started.", 409)
            existing_evaluations = con.execute("SELECT COUNT(*) FROM evaluations WHERE study_id=?", (study_id,)).fetchone()[0]
            if existing_evaluations:
                con.execute("ROLLBACK"); raise EnsembleError("A started study cannot be restarted in place; create a new immutable study ID.", 409)
            definition = json.loads(row["definition_json"])
            design = generate_design(definition)
            count = con.execute("SELECT COUNT(*) FROM evaluations WHERE status NOT IN ('completed','failed','cancelled')").fetchone()[0]
            if count + definition["design"]["evaluationCount"] > self.max_evaluations:
                con.execute("ROLLBACK"); raise EnsembleError("Ensemble evaluation capacity reached.", 409)
            now = _now()
            queued_ids: list[str] = []
            try:
                for sample in design:
                    for member in definition["members"]:
                        inputs = copy.deepcopy(member["defaultInputs"])
                        inputs.update(copy.deepcopy(definition["baseInputs"]))
                        for variable in definition["variables"]:
                            _set_path(inputs, variable["path"], sample["values"][variable["name"]])
                        parameters = copy.deepcopy(member["parameters"])
                        parameters.update(copy.deepcopy(definition["parameters"]))
                        workload = {
                            "title": f"{definition['title']} / {member['modelId']} / sample {sample['designIndex']}",
                            "method": member["methodId"],
                            "projectId": definition["projectId"],
                            "priority": definition["execution"]["priority"],
                            "timeoutSeconds": definition["execution"]["timeoutSeconds"],
                            "request": {
                                "method": member["methodId"], "inputs": inputs, "parameters": parameters,
                                "projectId": definition["projectId"], "randomSeed": definition["design"]["seed"] + sample["designIndex"],
                                "governance": {"ensembleStudyId": study_id, "modelId": member["modelId"], "modelVersion": member["modelVersion"], "definitionHash": definition["definitionHash"]},
                            },
                            "maxAttempts": definition["execution"]["maxAttempts"],
                        }
                        queue_item = self.dispatcher.enqueue(workload)["queueItem"]
                        queued_ids.append(queue_item["id"])
                        evaluation_id = f"ensemble-eval-{secrets.token_hex(10)}"
                        con.execute("""INSERT INTO evaluations(id,study_id,design_index,role,base_index,parameter_name,member_index,model_id,model_version,member_weight,sample_json,inputs_json,parameters_json,queue_id,status,created_at,updated_at)
                                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (evaluation_id, study_id, sample["designIndex"], sample["role"], sample["baseIndex"], sample.get("parameterName"), member["memberIndex"], member["modelId"], member["modelVersion"], member["normalizedWeight"], _stable(sample["values"]), _stable(inputs), _stable(parameters), queue_item["id"], "queued", now, now))
                con.execute("UPDATE studies SET status='queued',started_at=?,error_text=NULL,updated_at=? WHERE id=?", (now, now, study_id))
                self._event(con, study_id, "study-started", actor, {"queuedEvaluations": len(queued_ids), "design": definition["design"]})
                con.execute("COMMIT")
            except Exception as exc:
                con.execute("ROLLBACK")
                for queue_id in queued_ids:
                    try:
                        self.dispatcher.cancel_queue_item(queue_id, {"operatorId": actor, "reason": "Ensemble study start rolled back."})
                    except Exception:
                        pass
                raise EnsembleError(f"Unable to queue ensemble evaluations: {exc}", getattr(exc, "status_code", 409)) from exc
        return self.get(study_id)

    def _evaluation_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": EVALUATION_SCHEMA, "version": VERSION, "id": row["id"], "studyId": row["study_id"],
            "designIndex": row["design_index"], "role": row["role"], "baseIndex": row["base_index"], "parameterName": row["parameter_name"],
            "memberIndex": row["member_index"], "modelId": row["model_id"], "modelVersion": row["model_version"], "memberWeight": row["member_weight"],
            "sampleValues": json.loads(row["sample_json"]), "inputs": json.loads(row["inputs_json"]), "parameters": json.loads(row["parameters_json"]),
            "queueId": row["queue_id"], "status": row["status"], "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "outputValue": row["output_value"], "error": row["error_text"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        }

    def reconcile(self, study_id: str) -> dict[str, Any]:
        study_id = _text(study_id, 180)
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            study = con.execute("SELECT * FROM studies WHERE id=?", (study_id,)).fetchone()
            if not study:
                con.execute("ROLLBACK"); raise EnsembleError("Ensemble study was not found.", 404)
            definition = json.loads(study["definition_json"])
            rows = con.execute("SELECT * FROM evaluations WHERE study_id=? AND status IN ('queued','running')", (study_id,)).fetchall()
            changed = 0
            for row in rows:
                try:
                    queue_item = self.dispatcher.queue_item(row["queue_id"])["queueItem"]
                except Exception as exc:
                    con.execute("UPDATE evaluations SET status='failed',error_text=?,updated_at=? WHERE id=?", (_text(str(exc), 2000), _now(), row["id"])); changed += 1
                    continue
                queue_status = queue_item["status"]
                if queue_status in {"leased", "running"} and row["status"] != "running":
                    con.execute("UPDATE evaluations SET status='running',updated_at=? WHERE id=?", (_now(), row["id"])); changed += 1
                elif queue_status == "completed":
                    try:
                        output_value = _extract_numeric(queue_item.get("result"), definition["output"]["path"])
                        con.execute("UPDATE evaluations SET status='completed',result_json=?,output_value=?,error_text=NULL,updated_at=? WHERE id=?", (_stable(queue_item.get("result")), output_value, _now(), row["id"]))
                    except EnsembleError as exc:
                        con.execute("UPDATE evaluations SET status='failed',result_json=?,error_text=?,updated_at=? WHERE id=?", (_stable(queue_item.get("result")), exc.detail, _now(), row["id"]))
                    changed += 1
                elif queue_status in {"failed", "dead-lettered", "cancelled"}:
                    con.execute("UPDATE evaluations SET status=?,result_json=?,error_text=?,updated_at=? WHERE id=?", ("cancelled" if queue_status == "cancelled" else "failed", _stable(queue_item.get("result")), _text(queue_item.get("error") or f"Dispatcher status: {queue_status}", 2000), _now(), row["id"])); changed += 1
            all_rows = con.execute("SELECT * FROM evaluations WHERE study_id=? ORDER BY design_index,member_index", (study_id,)).fetchall()
            statuses = [row["status"] for row in all_rows]
            now = _now()
            if statuses and all(status == "completed" for status in statuses):
                evaluations = [self._evaluation_dict(row) for row in all_rows]
                analysis = analyze_results(definition, evaluations)
                con.execute("UPDATE studies SET status='completed',analysis_json=?,error_text=NULL,completed_at=?,updated_at=? WHERE id=?", (_stable(analysis), now, now, study_id))
                self._event(con, study_id, "study-completed", "system", {"analysisHash": analysis["analysisHash"], "evaluations": len(evaluations)})
            elif any(status == "failed" for status in statuses) and not any(status in {"queued", "running"} for status in statuses):
                failed = sum(status == "failed" for status in statuses)
                con.execute("UPDATE studies SET status='failed',error_text=?,completed_at=?,updated_at=? WHERE id=?", (f"{failed} ensemble evaluations failed.", now, now, study_id))
                self._event(con, study_id, "study-failed", "system", {"failedEvaluations": failed})
            elif any(status in {"queued", "running"} for status in statuses):
                con.execute("UPDATE studies SET status='running',updated_at=? WHERE id=?", (now, study_id))
            con.execute("COMMIT")
        result = self.get(study_id, reconcile=False)
        result["reconciliation"] = {"changedEvaluations": changed}
        return result

    def record_result(self, study_id: str, evaluation_id: str, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        value = _number(payload.get("outputValue"), "outputValue")
        with self._connect() as con:
            row = con.execute("SELECT * FROM evaluations WHERE id=? AND study_id=?", (_text(evaluation_id, 220), _text(study_id, 180))).fetchone()
            if not row:
                raise EnsembleError("Ensemble evaluation was not found.", 404)
            if row["status"] == "completed":
                if row["output_value"] == value:
                    return {"ok": True, "evaluation": self._evaluation_dict(row), "idempotent": True}
                raise EnsembleError("Completed evaluation results are immutable.", 409)
            if row["queue_id"]:
                try:
                    self.dispatcher.cancel_queue_item(
                        row["queue_id"],
                        {
                            "operatorId": actor,
                            "reason": "Governed external result superseded the queued evaluation.",
                        },
                    )
                except Exception:
                    # The result record remains authoritative even if the queue item
                    # was already terminal or was removed by an external operator.
                    pass
            now = _now()
            con.execute("UPDATE evaluations SET status='completed',result_json=?,output_value=?,error_text=NULL,updated_at=? WHERE id=?", (_stable(payload.get("result") if isinstance(payload.get("result"), dict) else {"manual": True, "outputValue": value}), value, now, row["id"]))
            self._event(con, study_id, "evaluation-recorded", actor, {"evaluationId": row["id"], "outputValue": value, "manual": True, "supersededQueueId": row["queue_id"]})
        return self.reconcile(study_id)

    def cancel(self, study_id: str, actor: str = "operator", reason: str = "operator cancellation") -> dict[str, Any]:
        with self._connect() as con:
            study = con.execute("SELECT * FROM studies WHERE id=?", (_text(study_id, 180),)).fetchone()
            if not study:
                raise EnsembleError("Ensemble study was not found.", 404)
            rows = con.execute("SELECT id,queue_id FROM evaluations WHERE study_id=? AND status IN ('queued','running')", (study_id,)).fetchall()
            for row in rows:
                if row["queue_id"]:
                    try:
                        self.dispatcher.cancel_queue_item(row["queue_id"], {"operatorId": actor, "reason": reason})
                    except Exception:
                        pass
            now = _now()
            con.execute("UPDATE evaluations SET status='cancelled',error_text=?,updated_at=? WHERE study_id=? AND status IN ('queued','running')", (reason, now, study_id))
            con.execute("UPDATE studies SET status='cancelled',error_text=?,completed_at=?,updated_at=? WHERE id=?", (reason, now, now, study_id))
            self._event(con, study_id, "study-cancelled", actor, {"reason": reason, "cancelledEvaluations": len(rows)})
        return self.get(study_id, reconcile=False)

    def get(self, study_id: str, reconcile: bool = True, evaluation_limit: int = 5000) -> dict[str, Any]:
        if reconcile:
            with self._connect() as con:
                state = con.execute("SELECT status FROM studies WHERE id=?", (_text(study_id, 180),)).fetchone()
            if state and state["status"] in {"queued", "running"}:
                return self.reconcile(study_id)
        with self._connect() as con:
            study = con.execute("SELECT * FROM studies WHERE id=?", (_text(study_id, 180),)).fetchone()
            if not study:
                raise EnsembleError("Ensemble study was not found.", 404)
            evaluations = [self._evaluation_dict(row) for row in con.execute("SELECT * FROM evaluations WHERE study_id=? ORDER BY design_index,member_index LIMIT ?", (study["id"], max(1, min(200000, int(evaluation_limit))))).fetchall()]
        counts = {state: 0 for state in ("queued", "running", "completed", "failed", "cancelled")}
        for evaluation in evaluations:
            counts[evaluation["status"]] = counts.get(evaluation["status"], 0) + 1
        return {"ok": True, "study": {"schema": STUDY_SCHEMA, "version": VERSION, "id": study["id"], "title": study["title"], "projectId": study["project_id"], "status": study["status"], "definitionHash": study["definition_hash"], "definition": json.loads(study["definition_json"]), "analysis": json.loads(study["analysis_json"]) if study["analysis_json"] else None, "error": study["error_text"], "counts": counts, "evaluations": evaluations, "createdAt": study["created_at"], "startedAt": study["started_at"], "completedAt": study["completed_at"], "updatedAt": study["updated_at"]}}

    def list(self, project_id: str = "", status: str = "", limit: int = 100) -> dict[str, Any]:
        clauses: list[str] = []; args: list[Any] = []
        if project_id:
            clauses.append("project_id=?"); args.append(_text(project_id, 180))
        if status:
            if status not in STATES:
                raise EnsembleError("Unsupported ensemble study status.")
            clauses.append("status=?"); args.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        args.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT id,title,project_id,status,definition_hash,error_text,created_at,started_at,completed_at,updated_at FROM studies{where} ORDER BY created_at DESC LIMIT ?", args).fetchall()
        return {"ok": True, "studies": [{"id": row["id"], "title": row["title"], "projectId": row["project_id"], "status": row["status"], "definitionHash": row["definition_hash"], "error": row["error_text"], "createdAt": row["created_at"], "startedAt": row["started_at"], "completedAt": row["completed_at"], "updatedAt": row["updated_at"]} for row in rows], "count": len(rows)}

    def timeline(self, study_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            if not con.execute("SELECT 1 FROM studies WHERE id=?", (_text(study_id, 180),)).fetchone():
                raise EnsembleError("Ensemble study was not found.", 404)
            rows = con.execute("SELECT * FROM events WHERE study_id=? ORDER BY sequence DESC LIMIT ?", (study_id, max(1, min(5000, int(limit))))).fetchall()
        events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "studyId": row["study_id"], "eventType": row["event_type"], "actor": row["actor"], "details": json.loads(row["details_json"]), "createdAt": row["created_at"]} for row in rows]
        return {"ok": True, "events": events, "count": len(events)}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            counts = {row["status"]: row["count"] for row in con.execute("SELECT status,COUNT(*) count FROM studies GROUP BY status").fetchall()}
            evaluations = con.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
            completed = con.execute("SELECT COUNT(*) FROM evaluations WHERE status='completed'").fetchone()[0]
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schemaVersion": 1, "architecture": "ensemble-simulation-global-sensitivity-uncertainty", "storage": "sqlite-wal", "databasePath": self.db_path, "integrity": integrity, "counts": {"studies": sum(counts.values()), "evaluations": evaluations, "completedEvaluations": completed, **counts}, "policies": policies(self.max_studies, self.max_evaluations)}
