from __future__ import annotations

import copy
import itertools
import json
import math
import random
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

from .bayesian_optimization import fit_gaussian_process
from .model_registry import ModelRegistryError, ScientificModelRegistry

VERSION = "0.34.2"
STUDY_SCHEMA = "sc-lab-surrogate-rom-study/0.34.2"
MODEL_SCHEMA = "sc-lab-surrogate-rom-model/0.34.2"
PREDICTION_SCHEMA = "sc-lab-surrogate-rom-prediction/0.34.2"
EVENT_SCHEMA = "sc-lab-surrogate-rom-event/0.34.2"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")
MODES = {"surrogate", "reduced-order", "hybrid-rom"}
ALGORITHMS = {"polynomial-ridge", "radial-basis", "gaussian-process"}
KERNELS = {"rbf", "matern32", "matern52"}


class SurrogateROMError(ValueError):
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


def _finite(value: Any, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if not math.isfinite(number):
        number = default
    return max(low, min(high, number))


def _integer(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def _matrix(raw: Any, name: str, max_rows: int, max_columns: int) -> np.ndarray:
    if not isinstance(raw, list) or not raw:
        raise SurrogateROMError(f"{name} must be a non-empty array of rows.")
    if len(raw) > max_rows:
        raise SurrogateROMError(f"{name} exceeds the configured row limit.", 409)
    rows: list[list[float]] = []
    width: int | None = None
    for index, row in enumerate(raw):
        if not isinstance(row, list) or not row:
            raise SurrogateROMError(f"{name}[{index}] must be a non-empty numeric row.")
        if width is None:
            width = len(row)
            if width > max_columns:
                raise SurrogateROMError(f"{name} exceeds the configured column limit.", 409)
        if len(row) != width:
            raise SurrogateROMError(f"{name} rows must have a consistent width.")
        clean: list[float] = []
        for value in row:
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise SurrogateROMError(f"{name} contains a non-numeric value.") from exc
            if not math.isfinite(number):
                raise SurrogateROMError(f"{name} contains a non-finite value.")
            clean.append(number)
        rows.append(clean)
    return np.asarray(rows, dtype=float)


def _vector(raw: Any, name: str, expected: int, max_rows: int) -> np.ndarray:
    if not isinstance(raw, list) or not raw:
        raise SurrogateROMError(f"{name} must be a non-empty numeric array.")
    if len(raw) != expected:
        raise SurrogateROMError(f"{name} length must match the number of input rows.")
    if len(raw) > max_rows:
        raise SurrogateROMError(f"{name} exceeds the configured row limit.", 409)
    result: list[float] = []
    for value in raw:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise SurrogateROMError(f"{name} contains a non-numeric value.") from exc
        if not math.isfinite(number):
            raise SurrogateROMError(f"{name} contains a non-finite value.")
        result.append(number)
    return np.asarray(result, dtype=float)


def _normalize_features(raw: Any, width: int) -> list[str]:
    if raw is None:
        return [f"x{index + 1}" for index in range(width)]
    if not isinstance(raw, list) or len(raw) != width:
        raise SurrogateROMError("data.features must contain one unique name per input column.")
    features = [_text(item, 120) for item in raw]
    if any(not name or not ID_RE.match(name) for name in features) or len(set(features)) != len(features):
        raise SurrogateROMError("Feature names must be unique identifiers.")
    return features


def _normalize_training(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    algorithm = _text(source.get("algorithm"), 80) or "polynomial-ridge"
    if algorithm not in ALGORITHMS:
        raise SurrogateROMError("Unsupported surrogate algorithm.")
    kernel = _text(source.get("kernel"), 40) or "matern52"
    if kernel not in KERNELS:
        raise SurrogateROMError("Unsupported Gaussian-process kernel.")
    return {
        "algorithm": algorithm,
        "degree": _integer(source.get("degree"), 2, 1, 4),
        "ridge": _finite(source.get("ridge"), 1e-8, 1e-12, 1e6),
        "rbfGamma": _finite(source.get("rbfGamma"), 1.0, 1e-6, 1e6),
        "kernel": kernel,
        "lengthScale": _finite(source.get("lengthScale"), 0.35, 0.01, 10.0),
        "observationNoise": _finite(source.get("observationNoise"), 1e-6, 1e-12, 1.0),
    }


def normalize_definition(payload: dict[str, Any], max_rows: int = 50000, max_dimensions: int = 5000) -> dict[str, Any]:
    source = payload.get("study") if isinstance(payload.get("study"), dict) else payload
    study_id = _text(source.get("id"), 180)
    if not ID_RE.match(study_id):
        raise SurrogateROMError("A valid study ID is required.")
    mode = _text(source.get("mode"), 80) or "surrogate"
    if mode not in MODES:
        raise SurrogateROMError("mode must be surrogate, reduced-order, or hybrid-rom.")
    data = source.get("data") if isinstance(source.get("data"), dict) else {}
    inputs: np.ndarray | None = None
    outputs: np.ndarray | None = None
    snapshots: np.ndarray | None = None
    features: list[str] = []
    if mode in {"surrogate", "hybrid-rom"}:
        inputs = _matrix(data.get("inputs"), "data.inputs", max_rows, min(max_dimensions, 256))
        if len(inputs) < 4:
            raise SurrogateROMError("At least four training rows are required.")
        features = _normalize_features(data.get("features"), inputs.shape[1])
    if mode == "surrogate":
        assert inputs is not None
        outputs = _vector(data.get("outputs"), "data.outputs", len(inputs), max_rows)
    else:
        snapshots = _matrix(data.get("snapshots"), "data.snapshots", max_rows, max_dimensions)
        if len(snapshots) < 2:
            raise SurrogateROMError("At least two snapshots are required.")
        if mode == "hybrid-rom" and inputs is not None and len(inputs) != len(snapshots):
            raise SurrogateROMError("Hybrid ROM input and snapshot row counts must match.")
    training = _normalize_training(source.get("training"))
    validation_source = source.get("validation") if isinstance(source.get("validation"), dict) else {}
    reduced_source = source.get("reducedOrder") if isinstance(source.get("reducedOrder"), dict) else {}
    validation = {
        "holdoutFraction": _finite(validation_source.get("holdoutFraction"), 0.2, 0.0, 0.5),
        "randomSeed": _integer(validation_source.get("randomSeed"), 3420, 0, 2147483647),
        "maximumNormalizedRmse": _finite(validation_source.get("maximumNormalizedRmse"), 0.25, 0.0, 1e6),
        "minimumR2": _finite(validation_source.get("minimumR2"), -1e6, -1e6, 1.0),
    }
    reduced = {
        "method": "pod-svd",
        "energyThreshold": _finite(reduced_source.get("energyThreshold"), 0.99, 0.5, 1.0),
        "maxRank": _integer(reduced_source.get("maxRank"), 20, 1, max_dimensions),
        "center": reduced_source.get("center", True) is not False,
    }
    registration = copy.deepcopy(source.get("registration")) if isinstance(source.get("registration"), dict) else {}
    normalized = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "id": study_id,
        "title": _text(source.get("title"), 300) or study_id,
        "description": _text(source.get("description"), 4000) or None,
        "projectId": _text(source.get("projectId"), 180) or "default",
        "mode": mode,
        "data": {
            "features": features,
            "inputs": inputs.tolist() if inputs is not None else None,
            "outputs": outputs.tolist() if outputs is not None else None,
            "snapshots": snapshots.tolist() if snapshots is not None else None,
            "stateLabels": [_text(v, 180) for v in data.get("stateLabels", [])] if isinstance(data.get("stateLabels"), list) else [],
        },
        "training": training,
        "validation": validation,
        "reducedOrder": reduced,
        "registration": registration,
        "provenance": copy.deepcopy(source.get("provenance")) if isinstance(source.get("provenance"), dict) else {},
        "metadata": copy.deepcopy(source.get("metadata")) if isinstance(source.get("metadata"), dict) else {},
    }
    normalized["definitionHash"] = _hash(normalized)
    return normalized


def _split_indices(count: int, fraction: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    indices = list(range(count))
    rng = random.Random(seed)
    rng.shuffle(indices)
    holdout = max(1, int(round(count * fraction))) if fraction > 0 and count >= 5 else 0
    holdout = min(holdout, max(0, count - 2))
    validation = np.asarray(indices[:holdout], dtype=int)
    training = np.asarray(indices[holdout:], dtype=int)
    return training, validation


def _scaler(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale <= 1e-12, 1.0, scale)
    return (x - mean) / scale, mean, scale


def _powers(width: int, degree: int) -> list[list[int]]:
    result: list[list[int]] = [[0] * width]
    for order in range(1, degree + 1):
        for combo in itertools.combinations_with_replacement(range(width), order):
            exponent = [0] * width
            for index in combo:
                exponent[index] += 1
            result.append(exponent)
    if len(result) > 10000:
        raise SurrogateROMError("Polynomial feature expansion is too large.", 409)
    return result


def _design(x: np.ndarray, powers: list[list[int]]) -> np.ndarray:
    columns = []
    for power in powers:
        column = np.ones(len(x), dtype=float)
        for index, exponent in enumerate(power):
            if exponent:
                column *= np.power(x[:, index], exponent)
        columns.append(column)
    return np.column_stack(columns)


def _fit_scalar(x: np.ndarray, y: np.ndarray, config: dict[str, Any]) -> dict[str, Any]:
    scaled, mean, scale = _scaler(x)
    algorithm = config["algorithm"]
    if algorithm == "polynomial-ridge":
        powers = _powers(x.shape[1], int(config["degree"]))
        matrix = _design(scaled, powers)
        regularizer = float(config["ridge"]) * np.eye(matrix.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(matrix.T @ matrix + regularizer, matrix.T @ y)
        return {
            "algorithm": algorithm,
            "inputMean": mean.tolist(), "inputScale": scale.tolist(),
            "powers": powers, "coefficients": coefficients.tolist(),
            "degree": config["degree"], "ridge": config["ridge"],
        }
    if algorithm == "radial-basis":
        gamma = float(config["rbfGamma"])
        distances = np.sum((scaled[:, None, :] - scaled[None, :, :]) ** 2, axis=2)
        kernel = np.exp(-gamma * distances)
        weights = np.linalg.solve(kernel + float(config["ridge"]) * np.eye(len(kernel)), y)
        return {
            "algorithm": algorithm,
            "inputMean": mean.tolist(), "inputScale": scale.tolist(),
            "centers": scaled.tolist(), "weights": weights.tolist(),
            "gamma": gamma, "ridge": config["ridge"],
        }
    gp = fit_gaussian_process(scaled, y, config["kernel"], float(config["lengthScale"]), float(config["observationNoise"]))
    return {
        "algorithm": algorithm,
        "inputMean": mean.tolist(), "inputScale": scale.tolist(),
        "trainingInputs": scaled.tolist(), "trainingOutputs": y.tolist(),
        "kernel": config["kernel"], "lengthScale": config["lengthScale"],
        "observationNoise": config["observationNoise"],
        "conditionNumber": gp.condition_number,
    }


def _predict_scalar(model: dict[str, Any], x: np.ndarray) -> tuple[np.ndarray, np.ndarray | None]:
    mean = np.asarray(model["inputMean"], dtype=float)
    scale = np.asarray(model["inputScale"], dtype=float)
    scaled = (x - mean) / scale
    if model["algorithm"] == "polynomial-ridge":
        matrix = _design(scaled, model["powers"])
        return matrix @ np.asarray(model["coefficients"], dtype=float), None
    if model["algorithm"] == "radial-basis":
        centers = np.asarray(model["centers"], dtype=float)
        distances = np.sum((scaled[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        kernel = np.exp(-float(model["gamma"]) * distances)
        return kernel @ np.asarray(model["weights"], dtype=float), None
    training_x = np.asarray(model["trainingInputs"], dtype=float)
    training_y = np.asarray(model["trainingOutputs"], dtype=float)
    gp = fit_gaussian_process(training_x, training_y, model["kernel"], float(model["lengthScale"]), float(model["observationNoise"]))
    return gp.predict(scaled)


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    residual = predicted - actual
    rmse = float(np.sqrt(np.mean(residual * residual)))
    mae = float(np.mean(np.abs(residual)))
    span = float(np.max(actual) - np.min(actual)) if len(actual) else 0.0
    nrmse = rmse / max(span, float(np.std(actual)), 1e-12)
    denominator = float(np.sum((actual - np.mean(actual)) ** 2))
    r2 = 1.0 - float(np.sum(residual * residual)) / denominator if denominator > 1e-15 else (1.0 if rmse <= 1e-12 else 0.0)
    return {"rmse": rmse, "mae": mae, "normalizedRmse": nrmse, "r2": r2, "maximumAbsoluteError": float(np.max(np.abs(residual)))}


def _fit_pod(snapshots: np.ndarray, config: dict[str, Any]) -> dict[str, Any]:
    mean = np.mean(snapshots, axis=0) if config.get("center", True) else np.zeros(snapshots.shape[1], dtype=float)
    centered = snapshots - mean
    _, singular, vt = np.linalg.svd(centered, full_matrices=False)
    energy = singular * singular
    total = float(np.sum(energy))
    cumulative = np.cumsum(energy) / total if total > 1e-30 else np.ones_like(energy)
    threshold_rank = int(np.searchsorted(cumulative, float(config["energyThreshold"]), side="left") + 1)
    rank = max(1, min(int(config["maxRank"]), threshold_rank, vt.shape[0]))
    basis = vt[:rank]
    coefficients = centered @ basis.T
    reconstructed = coefficients @ basis + mean
    metrics = _metrics(snapshots.reshape(-1), reconstructed.reshape(-1))
    model = {
        "method": "pod-svd", "meanState": mean.tolist(), "basis": basis.tolist(),
        "singularValues": singular.tolist(), "retainedRank": rank,
        "availableRank": int(vt.shape[0]), "retainedEnergy": float(cumulative[rank - 1]) if len(cumulative) else 1.0,
        "componentEnergy": (energy / total).tolist() if total > 1e-30 else [0.0 for _ in singular],
        "trainingCoefficients": coefficients.tolist(), "reconstructionMetrics": metrics,
    }
    model["basisHash"] = _hash({"mean": model["meanState"], "basis": model["basis"], "rank": rank})
    return model


def train_definition(definition: dict[str, Any]) -> dict[str, Any]:
    mode = definition["mode"]
    data = definition["data"]
    validation = definition["validation"]
    result: dict[str, Any] = {
        "schema": MODEL_SCHEMA, "version": VERSION, "studyId": definition["id"],
        "mode": mode, "definitionHash": definition["definitionHash"], "trainedAt": _now(),
    }
    validation_result: dict[str, Any] = {"passed": True, "holdoutCount": 0, "metrics": {}}
    if mode == "surrogate":
        x = np.asarray(data["inputs"], dtype=float); y = np.asarray(data["outputs"], dtype=float)
        train_idx, valid_idx = _split_indices(len(x), validation["holdoutFraction"], validation["randomSeed"])
        if len(valid_idx):
            provisional = _fit_scalar(x[train_idx], y[train_idx], definition["training"])
            predicted, _ = _predict_scalar(provisional, x[valid_idx])
            metrics = _metrics(y[valid_idx], predicted)
            validation_result.update({"holdoutCount": int(len(valid_idx)), "metrics": metrics})
            validation_result["passed"] = metrics["normalizedRmse"] <= validation["maximumNormalizedRmse"] and metrics["r2"] >= validation["minimumR2"]
        model = _fit_scalar(x, y, definition["training"])
        training_prediction, _ = _predict_scalar(model, x)
        result.update({"features": data["features"], "surrogate": model, "trainingMetrics": _metrics(y, training_prediction)})
    else:
        snapshots = np.asarray(data["snapshots"], dtype=float)
        pod = _fit_pod(snapshots, definition["reducedOrder"])
        result.update({"stateLabels": data.get("stateLabels") or [], "reducedOrder": pod})
        validation_result["metrics"] = pod["reconstructionMetrics"]
        validation_result["passed"] = pod["reconstructionMetrics"]["normalizedRmse"] <= validation["maximumNormalizedRmse"]
        if mode == "hybrid-rom":
            x = np.asarray(data["inputs"], dtype=float)
            coefficients = np.asarray(pod["trainingCoefficients"], dtype=float)
            coefficient_models = [_fit_scalar(x, coefficients[:, index], definition["training"]) for index in range(coefficients.shape[1])]
            predicted_coefficients = np.column_stack([_predict_scalar(item, x)[0] for item in coefficient_models])
            basis = np.asarray(pod["basis"], dtype=float); mean_state = np.asarray(pod["meanState"], dtype=float)
            reconstructed = predicted_coefficients @ basis + mean_state
            hybrid_metrics = _metrics(snapshots.reshape(-1), reconstructed.reshape(-1))
            result.update({"features": data["features"], "coefficientSurrogates": coefficient_models, "hybridMetrics": hybrid_metrics})
            validation_result["metrics"] = hybrid_metrics
            validation_result["passed"] = hybrid_metrics["normalizedRmse"] <= validation["maximumNormalizedRmse"]
    result["validation"] = validation_result
    result["modelHash"] = _hash({k: v for k, v in result.items() if k not in {"trainedAt", "modelHash"}})
    return result


def policies(max_studies: int = 2000, max_training_rows: int = 50000, max_snapshot_dimensions: int = 5000, max_request_bytes: int = 16777216) -> dict[str, Any]:
    return {
        "ok": True, "version": VERSION, "architecture": "surrogate-models-reduced-order-analysis",
        "modes": sorted(MODES), "surrogateAlgorithms": sorted(ALGORITHMS), "reducedOrderMethods": ["pod-svd"],
        "uncertaintyPrediction": True, "holdoutValidation": True, "errorBounds": True,
        "immutableTrainingRecords": True, "modelRegistryIntegration": True,
        "arbitraryCode": False, "registeredModelsOnly": True,
        "limits": {"maxStudies": max_studies, "maxTrainingRows": max_training_rows, "maxSnapshotDimensions": max_snapshot_dimensions, "maxRequestBytes": max_request_bytes},
    }


class SurrogateReducedOrderManager:
    def __init__(self, db_path: str, registry: ScientificModelRegistry, max_studies: int = 2000, max_training_rows: int = 50000, max_snapshot_dimensions: int = 5000, history_limit: int = 50000):
        self.db_path = str(db_path)
        self.registry = registry
        self.max_studies = max(1, int(max_studies))
        self.max_training_rows = max(4, int(max_training_rows))
        self.max_snapshot_dimensions = max(2, int(max_snapshot_dimensions))
        self.history_limit = max(100, int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS studies (
              id TEXT PRIMARY KEY, title TEXT NOT NULL, project_id TEXT NOT NULL, mode TEXT NOT NULL,
              definition_hash TEXT NOT NULL, model_hash TEXT NOT NULL, status TEXT NOT NULL,
              record_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
              sequence INTEGER PRIMARY KEY AUTOINCREMENT, study_id TEXT NOT NULL, event_type TEXT NOT NULL,
              actor TEXT, reason TEXT, details_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_surrogate_project ON studies(project_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_surrogate_events ON events(study_id, sequence DESC);
            """)
            con.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('schema_version','1')")

    def _event(self, con: sqlite3.Connection, study_id: str, event_type: str, actor: str, reason: str, details: dict[str, Any]) -> None:
        con.execute("INSERT INTO events(study_id,event_type,actor,reason,details_json,created_at) VALUES(?,?,?,?,?,?)", (study_id, event_type, actor or "system", reason or "", _stable(details), _now()))
        con.execute("DELETE FROM events WHERE sequence NOT IN (SELECT sequence FROM events ORDER BY sequence DESC LIMIT ?)", (self.history_limit,))

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        definition = normalize_definition(payload, self.max_training_rows, self.max_snapshot_dimensions)
        return {"ok": True, "definition": definition, "policies": policies(self.max_studies, self.max_training_rows, self.max_snapshot_dimensions)}

    def train(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        definition = normalize_definition(payload, self.max_training_rows, self.max_snapshot_dimensions)
        model = train_definition(definition)
        now = _now()
        record = {"definition": definition, "model": model, "registration": None, "createdAt": now, "updatedAt": now}
        with self._connect() as con:
            existing = con.execute("SELECT definition_hash,model_hash FROM studies WHERE id=?", (definition["id"],)).fetchone()
            if existing:
                if existing["definition_hash"] == definition["definitionHash"] and existing["model_hash"] == model["modelHash"]:
                    return {"ok": True, "created": False, "study": self.get(definition["id"])["study"]}
                raise SurrogateROMError("Surrogate and ROM studies are immutable; choose a new study ID.", 409)
            if con.execute("SELECT COUNT(*) FROM studies").fetchone()[0] >= self.max_studies:
                raise SurrogateROMError("Surrogate study capacity reached.", 409)
            status = "validated" if model["validation"]["passed"] else "validation-failed"
            con.execute("INSERT INTO studies(id,title,project_id,mode,definition_hash,model_hash,status,record_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (definition["id"], definition["title"], definition["projectId"], definition["mode"], definition["definitionHash"], model["modelHash"], status, _stable(record), now, now))
            self._event(con, definition["id"], "surrogate-study-trained", actor, "", {"mode": definition["mode"], "modelHash": model["modelHash"], "validationPassed": model["validation"]["passed"]})
        return {"ok": True, "created": True, "study": self.get(definition["id"])["study"]}

    def list(self, project_id: str = "", status: str = "", limit: int = 100) -> dict[str, Any]:
        clauses: list[str] = []; args: list[Any] = []
        if project_id: clauses.append("project_id=?"); args.append(project_id)
        if status: clauses.append("status=?"); args.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        args.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            rows = [dict(row) for row in con.execute("SELECT id,title,project_id AS projectId,mode,status,definition_hash AS definitionHash,model_hash AS modelHash,created_at AS createdAt,updated_at AS updatedAt FROM studies" + where + " ORDER BY updated_at DESC LIMIT ?", args).fetchall()]
        return {"ok": True, "studies": rows, "count": len(rows)}

    def get(self, study_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = con.execute("SELECT status,record_json FROM studies WHERE id=?", (study_id,)).fetchone()
        if not row:
            raise SurrogateROMError("Surrogate study not found.", 404)
        record = json.loads(row["record_json"]); record["status"] = row["status"]
        return {"ok": True, "study": record}

    def predict(self, study_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        study = self.get(study_id)["study"]
        model = study["model"]; mode = model["mode"]
        if mode == "reduced-order":
            coefficients = payload.get("coefficients")
            if not isinstance(coefficients, list):
                raise SurrogateROMError("Reduced-order predictions require coefficients.")
            array = np.asarray(coefficients, dtype=float).reshape(1, -1)
            basis = np.asarray(model["reducedOrder"]["basis"], dtype=float)
            if array.shape[1] != basis.shape[0]:
                raise SurrogateROMError("Coefficient count must equal the retained ROM rank.")
            state = array @ basis + np.asarray(model["reducedOrder"]["meanState"], dtype=float)
            prediction = {"state": state[0].tolist(), "coefficients": array[0].tolist()}
        else:
            values = payload.get("inputs") if isinstance(payload.get("inputs"), dict) else payload
            features = model["features"]
            try:
                row = np.asarray([[float(values[name]) for name in features]], dtype=float)
            except (KeyError, TypeError, ValueError) as exc:
                raise SurrogateROMError("Prediction inputs must provide every numeric feature.") from exc
            if mode == "surrogate":
                mean, std = _predict_scalar(model["surrogate"], row)
                prediction = {"value": float(mean[0]), "standardDeviation": float(std[0]) if std is not None else None}
            else:
                coefficients = np.asarray([_predict_scalar(item, row)[0][0] for item in model["coefficientSurrogates"]], dtype=float)
                basis = np.asarray(model["reducedOrder"]["basis"], dtype=float)
                state = coefficients @ basis + np.asarray(model["reducedOrder"]["meanState"], dtype=float)
                prediction = {"state": state.tolist(), "coefficients": coefficients.tolist()}
        response = {"schema": PREDICTION_SCHEMA, "version": VERSION, "studyId": study_id, "modelHash": model["modelHash"], "prediction": prediction, "createdAt": _now()}
        response["predictionHash"] = _hash({k: v for k, v in response.items() if k not in {"createdAt", "predictionHash"}})
        return {"ok": True, **response}

    def register_model(self, study_id: str, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        study = self.get(study_id)["study"]
        definition = study["definition"]; model = study["model"]
        source = payload.get("model") if isinstance(payload.get("model"), dict) else payload
        model_id = _text(source.get("id") or source.get("modelId"), 180) or study_id
        model_version = _text(source.get("modelVersion"), 120)
        if not model_version:
            raise SurrogateROMError("modelVersion is required for registry publication.")
        registry_payload = {
            "id": model_id, "modelVersion": model_version,
            "title": _text(source.get("title"), 300) or definition["title"],
            "description": _text(source.get("description"), 4000) or definition.get("description"),
            "projectId": definition["projectId"], "type": "surrogate",
            "sourceRevision": _text(source.get("sourceRevision"), 180) or None,
            "artifactIds": source.get("artifactIds") if isinstance(source.get("artifactIds"), list) else [],
            "inputSchema": {"type": "object", "properties": {name: {"type": "number"} for name in model.get("features", [])}, "required": model.get("features", [])},
            "outputSchema": {"type": "object", "properties": {"value": {"type": "number"}, "state": {"type": "array", "items": {"type": "number"}}}},
            "parameters": {"studyId": study_id, "mode": model["mode"], "modelHash": model["modelHash"], "validation": model["validation"], "reducedRank": (model.get("reducedOrder") or {}).get("retainedRank")},
            "environment": source.get("environment") if isinstance(source.get("environment"), dict) else {"id": f"surrogate-rom-{VERSION.replace('.', '-')}", "dependencies": [{"name": "numpy", "version": "2.x"}, {"name": "scipy", "version": "1.x"}]},
            "provenance": {"surrogateStudyId": study_id, "definitionHash": definition["definitionHash"], "modelHash": model["modelHash"], **(definition.get("provenance") or {})},
            "metadata": {"architecture": "surrogate-model-reduced-order-analysis", "trainingRows": len(definition["data"].get("inputs") or definition["data"].get("snapshots") or []), **(source.get("metadata") if isinstance(source.get("metadata"), dict) else {})},
            "channel": _text(source.get("channel"), 40) or "draft",
        }
        try:
            registered = self.registry.register(registry_payload, actor)
        except ModelRegistryError as exc:
            raise SurrogateROMError(exc.detail, exc.status_code) from exc
        with self._connect() as con:
            row = con.execute("SELECT record_json FROM studies WHERE id=?", (study_id,)).fetchone()
            record = json.loads(row["record_json"])
            registration = {"modelId": model_id, "modelVersion": model_version, "modelHash": registered["model"]["model"].get("modelHash"), "registeredAt": _now()}
            record["registration"] = registration; record["updatedAt"] = _now()
            con.execute("UPDATE studies SET status='registered',record_json=?,updated_at=? WHERE id=?", (_stable(record), record["updatedAt"], study_id))
            self._event(con, study_id, "surrogate-model-registered", actor, "", registration)
        return {"ok": True, "registration": registered, "study": self.get(study_id)["study"]}

    def timeline(self, study_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            rows = []
            for row in con.execute("SELECT * FROM events WHERE study_id=? ORDER BY sequence DESC LIMIT ?", (study_id, max(1, min(5000, int(limit))))).fetchall():
                item = dict(row); item["details"] = json.loads(item.pop("details_json")); rows.append(item)
        return {"ok": True, "events": rows, "count": len(rows)}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            counts = {
                "studies": con.execute("SELECT COUNT(*) FROM studies").fetchone()[0],
                "validated": con.execute("SELECT COUNT(*) FROM studies WHERE status='validated'").fetchone()[0],
                "registered": con.execute("SELECT COUNT(*) FROM studies WHERE status='registered'").fetchone()[0],
                "validationFailed": con.execute("SELECT COUNT(*) FROM studies WHERE status='validation-failed'").fetchone()[0],
            }
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schemaVersion": 1, "storage": "sqlite-wal", "databasePath": self.db_path, "integrity": integrity, "counts": counts, "policies": policies(self.max_studies, self.max_training_rows, self.max_snapshot_dimensions)}
