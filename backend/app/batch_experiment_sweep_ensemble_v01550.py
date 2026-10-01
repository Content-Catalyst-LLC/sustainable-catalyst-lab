from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import sqlite3
import statistics
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.155.0"
CAMPAIGN_SCHEMA = "sc-lab-batch-experiment-campaign/0.155.0"
TRIAL_SCHEMA = "sc-lab-batch-experiment-trial/0.155.0"
MANIFEST_SCHEMA = "sc-lab-batch-experiment-manifest/0.155.0"
HANDOFF_SCHEMA = "sc-lab-workspace-execution-handoff/0.155.0"
SUPPORTED_MODES = {
    "parameter-sweep",
    "hyperparameter-search",
    "monte-carlo",
    "factorial",
    "repeated-trials",
    "ensemble",
}
BOUNDARY = (
    "Batch campaigns generate bounded, reproducible trial specifications and explicit execution handoffs. "
    "They do not execute arbitrary code, automatically dispatch Workspace jobs, establish causality, "
    "statistical significance, calibration, model validity, or scientific validity. Human review remains required."
)


class BatchCampaignError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip()
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise BatchCampaignError(f"Invalid {label}.")
    return text


def _text(value: Any, label: str, maximum: int = 4000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise BatchCampaignError(f"{label} is required.")
    if len(text) > maximum:
        raise BatchCampaignError(f"{label} exceeds {maximum} characters.")
    return text


def _json(value: Any, label: str, maximum_bytes: int = 1_500_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise BatchCampaignError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise BatchCampaignError(f"{label} exceeds the payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


def _number(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise BatchCampaignError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise BatchCampaignError(f"{label} must be finite.")
    return out


def _linspace(lo: float, hi: float, levels: int) -> list[float]:
    if levels <= 1:
        return [lo]
    step = (hi - lo) / (levels - 1)
    return [lo + step * i for i in range(levels)]


def _quantile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        raise BatchCampaignError("Cannot compute a quantile without values.")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def _normalize_parameter(raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise BatchCampaignError(f"Parameter {index + 1} must be an object.")
    name = _text(raw.get("name") or raw.get("path"), f"parameter {index + 1} name", 180, True)
    path = _text(raw.get("path") or name, f"parameter {index + 1} path", 300, True)
    if isinstance(raw.get("values"), list):
        values = [_json(v, f"parameter {name} value", 100_000) for v in raw["values"][:200]]
        if not values:
            raise BatchCampaignError(f"Parameter {name} values cannot be empty.")
        return {"name": name, "path": path, "kind": "values", "values": values}
    lo = _number(raw.get("min"), f"parameter {name} min")
    hi = _number(raw.get("max"), f"parameter {name} max")
    if hi < lo:
        raise BatchCampaignError(f"Parameter {name} max must be >= min.")
    levels = max(2, min(100, int(raw.get("levels") or 5)))
    distribution = str(raw.get("distribution") or "uniform").strip().lower()
    if distribution not in {"uniform", "log-uniform", "normal"}:
        raise BatchCampaignError(f"Unsupported distribution for {name}: {distribution}.")
    out = {"name": name, "path": path, "kind": "range", "min": lo, "max": hi, "levels": levels, "distribution": distribution}
    if raw.get("mean") is not None:
        out["mean"] = _number(raw.get("mean"), f"parameter {name} mean")
    if raw.get("stddev") is not None:
        out["stddev"] = abs(_number(raw.get("stddev"), f"parameter {name} stddev"))
    return out


def normalize_campaign(payload: dict[str, Any], max_trials_limit: int = 10000) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BatchCampaignError("Campaign payload must be an object.")
    mode = str(payload.get("mode") or "parameter-sweep").strip().lower().replace("_", "-")
    if mode not in SUPPORTED_MODES:
        raise BatchCampaignError(f"Unsupported campaign mode: {mode}.")
    title = _text(payload.get("title"), "title", 500, True)
    objective = _text(payload.get("objective"), "objective", 12000, False)
    method = _text(payload.get("method") or payload.get("executionMethod"), "execution method", 300, True)
    workflow_ref = _text(payload.get("workflowRef"), "workflowRef", 300, False)
    model_ref = _text(payload.get("modelRef"), "modelRef", 300, False)
    parameters_raw = payload.get("parameters") or []
    if not isinstance(parameters_raw, list):
        raise BatchCampaignError("parameters must be an array.")
    parameters = [_normalize_parameter(v, i) for i, v in enumerate(parameters_raw[:20])]
    if mode not in {"repeated-trials", "ensemble"} and not parameters:
        raise BatchCampaignError(f"{mode} requires at least one parameter.")
    repeats = max(1, min(1000, int(payload.get("repeats") or 1)))
    samples = max(1, min(max_trials_limit, int(payload.get("samples") or payload.get("trialCount") or 100)))
    base_seed = int(payload.get("baseSeed") if payload.get("baseSeed") is not None else 155000) & 0x7FFFFFFF
    search = str(payload.get("search") or ("random" if mode in {"monte-carlo", "hyperparameter-search"} else "grid")).strip().lower()
    if search not in {"grid", "random"}:
        raise BatchCampaignError("search must be grid or random.")
    members = payload.get("members") or []
    if mode == "ensemble":
        if not isinstance(members, list) or not members:
            raise BatchCampaignError("ensemble mode requires members.")
        clean_members = []
        for i, member in enumerate(members[:200]):
            if not isinstance(member, dict):
                raise BatchCampaignError(f"Ensemble member {i + 1} must be an object.")
            clean_members.append({
                "ref": _text(member.get("ref") or member.get("modelRef"), f"ensemble member {i + 1} ref", 300, True),
                "weight": _number(member.get("weight") if member.get("weight") is not None else 1.0, f"ensemble member {i + 1} weight"),
                "parameters": _json(member.get("parameters") or {}, f"ensemble member {i + 1} parameters", 250_000),
            })
        members = clean_members
    else:
        members = []
    fixed_inputs = _json(payload.get("inputs") or {}, "inputs", 500_000)
    fixed_parameters = _json(payload.get("fixedParameters") or {}, "fixedParameters", 500_000)
    requested_outputs = [str(v)[:160] for v in (payload.get("requestedOutputs") or ["summary", "values"]) if str(v).strip()][:100]
    metrics = [str(v)[:300] for v in (payload.get("metrics") or []) if str(v).strip()][:100]
    tags = [str(v)[:120] for v in (payload.get("tags") or []) if str(v).strip()][:50]
    return {
        "schema": CAMPAIGN_SCHEMA,
        "version": VERSION,
        "title": title,
        "objective": objective,
        "mode": mode,
        "method": method,
        "workflowRef": workflow_ref,
        "modelRef": model_ref,
        "parameters": parameters,
        "members": members,
        "inputs": fixed_inputs,
        "fixedParameters": fixed_parameters,
        "requestedOutputs": requested_outputs,
        "metrics": metrics,
        "tags": tags,
        "repeats": repeats,
        "samples": samples,
        "baseSeed": base_seed,
        "search": search,
        "automaticExecution": False,
        "arbitraryCodeExecution": False,
        "humanReviewRequired": True,
    }


def _sample_parameter(spec: dict[str, Any], rng: random.Random) -> Any:
    if spec["kind"] == "values":
        return spec["values"][rng.randrange(len(spec["values"]))]
    lo, hi = float(spec["min"]), float(spec["max"])
    distribution = spec.get("distribution", "uniform")
    if distribution == "log-uniform":
        if lo <= 0 or hi <= 0:
            raise BatchCampaignError(f"Log-uniform parameter {spec['name']} requires positive bounds.")
        return math.exp(rng.uniform(math.log(lo), math.log(hi)))
    if distribution == "normal":
        mean = float(spec.get("mean", (lo + hi) / 2))
        stddev = float(spec.get("stddev", max((hi - lo) / 6, 1e-12)))
        return min(hi, max(lo, rng.gauss(mean, stddev)))
    return rng.uniform(lo, hi)


def _grid_values(spec: dict[str, Any]) -> list[Any]:
    if spec["kind"] == "values":
        return list(spec["values"])
    return _linspace(float(spec["min"]), float(spec["max"]), int(spec.get("levels", 5)))


def generate_trials(definition: dict[str, Any], max_trials_limit: int = 10000) -> list[dict[str, Any]]:
    mode = definition["mode"]
    base_seed = int(definition["baseSeed"])
    repeats = int(definition["repeats"])
    trial_specs: list[dict[str, Any]] = []

    def append_trial(parameter_values: dict[str, Any], repeat_index: int = 0, member: dict[str, Any] | None = None) -> None:
        if len(trial_specs) >= max_trials_limit:
            raise BatchCampaignError(f"Campaign exceeds the configured trial limit ({max_trials_limit}).")
        ordinal = len(trial_specs) + 1
        seed = (base_seed + ordinal * 104729 + repeat_index * 1009) & 0x7FFFFFFF
        spec = {
            "schema": TRIAL_SCHEMA,
            "ordinal": ordinal,
            "seed": seed,
            "repeat": repeat_index + 1,
            "parameterValues": parameter_values,
            "member": member or None,
            "method": definition["method"],
            "workflowRef": definition.get("workflowRef") or "",
            "modelRef": (member or {}).get("ref") or definition.get("modelRef") or "",
            "inputs": definition.get("inputs") or {},
            "fixedParameters": definition.get("fixedParameters") or {},
            "requestedOutputs": definition.get("requestedOutputs") or [],
        }
        spec["specHash"] = _sha(spec)
        trial_specs.append(spec)

    if mode == "repeated-trials":
        for rep in range(repeats):
            append_trial({}, rep)
    elif mode == "ensemble":
        for member in definition["members"]:
            for rep in range(repeats):
                append_trial({}, rep, member)
    elif mode in {"factorial", "parameter-sweep"} and definition.get("search") == "grid":
        value_sets = [_grid_values(p) for p in definition["parameters"]]
        for combo in itertools.product(*value_sets):
            values = {p["path"]: v for p, v in zip(definition["parameters"], combo)}
            for rep in range(repeats):
                append_trial(values, rep)
    else:
        samples = int(definition["samples"])
        for sample_index in range(samples):
            rng = random.Random(base_seed + sample_index * 7919)
            values = {p["path"]: _sample_parameter(p, rng) for p in definition["parameters"]}
            for rep in range(repeats):
                append_trial(values, rep)
    if not trial_specs:
        raise BatchCampaignError("Campaign produced no trials.")
    return trial_specs


class BatchExperimentCampaignManager:
    def __init__(self, db_path: str, persistent_disk_mounted: bool = False, max_campaigns: int = 1000, max_trials: int = 10000, history_limit: int = 100000) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_campaigns = max(1, int(max_campaigns))
        self.max_trials = max(1, int(max_trials))
        self.history_limit = max(100, int(history_limit))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        class _ClosingConnection(sqlite3.Connection):
            def __exit__(self, exc_type, exc, tb):
                try:
                    return super().__exit__(exc_type, exc, tb)
                finally:
                    self.close()
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False, factory=_ClosingConnection)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS bec_campaigns(
                  id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, mode TEXT NOT NULL,
                  status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL,
                  definition_json TEXT NOT NULL, definition_hash TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS bec_campaign_project_idx ON bec_campaigns(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS bec_trials(
                  id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL, ordinal INTEGER NOT NULL, status TEXT NOT NULL,
                  attempt INTEGER NOT NULL DEFAULT 1, seed INTEGER NOT NULL, spec_json TEXT NOT NULL, spec_hash TEXT NOT NULL,
                  execution_ref TEXT NOT NULL DEFAULT '', result_ref TEXT NOT NULL DEFAULT '', metrics_json TEXT NOT NULL DEFAULT '{}',
                  error_text TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  UNIQUE(campaign_id, ordinal), FOREIGN KEY(campaign_id) REFERENCES bec_campaigns(id)
                );
                CREATE INDEX IF NOT EXISTS bec_trial_campaign_idx ON bec_trials(campaign_id, ordinal);
                CREATE INDEX IF NOT EXISTS bec_trial_status_idx ON bec_trials(campaign_id, status, ordinal);
                CREATE TABLE IF NOT EXISTS bec_events(
                  seq INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id TEXT NOT NULL, trial_id TEXT NOT NULL DEFAULT '',
                  event_type TEXT NOT NULL, occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
                  payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
                );
                """
            )

    def _event(self, db: sqlite3.Connection, campaign_id: str, trial_id: str, event_type: str, actor: str, payload: Any) -> None:
        row = db.execute("SELECT event_hash FROM bec_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = str(row["event_hash"]) if row else ""
        occurred = _now()
        envelope = {"campaignId": campaign_id, "trialId": trial_id, "eventType": event_type, "occurredAt": occurred, "actor": actor, "payload": payload, "previousHash": previous}
        event_hash = _sha(envelope)
        db.execute(
            "INSERT INTO bec_events(campaign_id,trial_id,event_type,occurred_at,actor,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (campaign_id, trial_id, event_type, occurred, actor, json.dumps(payload, sort_keys=True), previous, event_hash),
        )
        db.execute("DELETE FROM bec_events WHERE seq NOT IN (SELECT seq FROM bec_events ORDER BY seq DESC LIMIT ?)", (self.history_limit,))

    def policies(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "supportedModes": sorted(SUPPORTED_MODES),
            "maxCampaigns": self.max_campaigns,
            "maxTrialsPerCampaign": self.max_trials,
            "executionAuthority": "Workspace/runtime fabric",
            "automaticDispatch": False,
            "arbitraryCodeExecution": False,
            "explicitStateRecording": True,
            "failedTrialRetry": "explicit-user-action",
            "humanScientificReviewRequired": True,
            "boundary": BOUNDARY,
        }

    def health(self) -> dict[str, Any]:
        with self._connect() as db:
            campaigns = int(db.execute("SELECT COUNT(*) AS n FROM bec_campaigns").fetchone()["n"])
            trials = int(db.execute("SELECT COUNT(*) AS n FROM bec_trials").fetchone()["n"])
        return {
            "ok": True, "status": "ready", "version": VERSION,
            "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local-volume",
            "campaignSchema": CAMPAIGN_SCHEMA, "trialSchema": TRIAL_SCHEMA, "manifestSchema": MANIFEST_SCHEMA,
            "campaignModes": sorted(SUPPORTED_MODES), "automaticDispatch": False, "arbitraryCodeExecution": False,
            "deterministicTrialSpecifications": True, "manifestDigestVerification": True,
            "partialFailureRecovery": True, "aggregation": True,
            "counts": {"campaigns": campaigns, "trials": trials}, "boundary": BOUNDARY,
        }

    def create(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "projectId")
        actor = _text(actor, "actor", 300, True)
        definition = normalize_campaign(payload, self.max_trials)
        trials = generate_trials(definition, self.max_trials)
        with self._lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) AS n FROM bec_campaigns WHERE project_id=? AND archived=0", (project_id,)).fetchone()["n"])
            if count >= self.max_campaigns:
                raise BatchCampaignError("Project campaign limit reached.", 409)
            campaign_id = f"bec:{uuid.uuid4().hex}"
            now = _now(); definition_hash = _sha(definition)
            db.execute(
                "INSERT INTO bec_campaigns(id,project_id,title,mode,status,created_at,updated_at,actor,definition_json,definition_hash,archived) VALUES(?,?,?,?,?,?,?,?,?,?,0)",
                (campaign_id, project_id, definition["title"], definition["mode"], "planned", now, now, actor, json.dumps(definition, sort_keys=True), definition_hash),
            )
            for spec in trials:
                trial_id = f"trial:{uuid.uuid4().hex}"
                db.execute(
                    "INSERT INTO bec_trials(id,campaign_id,ordinal,status,attempt,seed,spec_json,spec_hash,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (trial_id, campaign_id, spec["ordinal"], "planned", 1, spec["seed"], json.dumps(spec, sort_keys=True), spec["specHash"], now, now),
                )
            self._event(db, campaign_id, "", "campaign-created", actor, {"definitionHash": definition_hash, "trialCount": len(trials), "mode": definition["mode"]})
            db.commit()
        return self.get(campaign_id, include_trials=True)

    @staticmethod
    def _campaign(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": CAMPAIGN_SCHEMA, "id": row["id"], "projectId": row["project_id"], "title": row["title"],
            "mode": row["mode"], "status": row["status"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
            "actor": row["actor"], "definition": json.loads(row["definition_json"]), "definitionHash": row["definition_hash"],
            "archived": bool(row["archived"]),
        }

    @staticmethod
    def _trial(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": TRIAL_SCHEMA, "id": row["id"], "campaignId": row["campaign_id"], "ordinal": int(row["ordinal"]),
            "status": row["status"], "attempt": int(row["attempt"]), "seed": int(row["seed"]),
            "spec": json.loads(row["spec_json"]), "specHash": row["spec_hash"], "executionRef": row["execution_ref"],
            "resultRef": row["result_ref"], "metrics": json.loads(row["metrics_json"] or "{}"), "error": row["error_text"],
            "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        }

    def _refresh_status(self, db: sqlite3.Connection, campaign_id: str) -> str:
        rows = db.execute("SELECT status,COUNT(*) AS n FROM bec_trials WHERE campaign_id=? GROUP BY status", (campaign_id,)).fetchall()
        counts = {str(r["status"]): int(r["n"]) for r in rows}
        total = sum(counts.values())
        if total and counts.get("succeeded", 0) == total:
            status = "completed"
        elif total and counts.get("cancelled", 0) == total:
            status = "cancelled"
        elif counts.get("failed", 0) and counts.get("succeeded", 0):
            status = "partial-failure"
        elif counts.get("failed", 0) and sum(counts.get(s, 0) for s in ("planned", "queued", "running")) == 0:
            status = "failed"
        elif counts.get("running", 0) or counts.get("queued", 0):
            status = "running"
        else:
            status = "planned"
        db.execute("UPDATE bec_campaigns SET status=?,updated_at=? WHERE id=?", (status, _now(), campaign_id))
        return status

    def get(self, campaign_id: str, include_trials: bool = False, trial_limit: int = 500) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM bec_campaigns WHERE id=?", (campaign_id,)).fetchone()
            if not row:
                raise BatchCampaignError("Campaign not found.", 404)
            counts = {str(r["status"]): int(r["n"]) for r in db.execute("SELECT status,COUNT(*) AS n FROM bec_trials WHERE campaign_id=? GROUP BY status", (campaign_id,)).fetchall()}
            body = {"ok": True, "campaign": self._campaign(row), "trialCounts": counts, "totalTrials": sum(counts.values())}
            if include_trials:
                body["trials"] = [self._trial(r) for r in db.execute("SELECT * FROM bec_trials WHERE campaign_id=? ORDER BY ordinal LIMIT ?", (campaign_id, max(1, min(5000, int(trial_limit))))).fetchall()]
            return body

    def list(self, project_id: str, limit: int = 100, include_archived: bool = False) -> dict[str, Any]:
        project_id = _clean_id(project_id, "projectId")
        sql = "SELECT * FROM bec_campaigns WHERE project_id=?"
        args: list[Any] = [project_id]
        if not include_archived:
            sql += " AND archived=0"
        sql += " ORDER BY updated_at DESC LIMIT ?"; args.append(max(1, min(500, int(limit))))
        with self._connect() as db:
            rows = db.execute(sql, args).fetchall()
        return {"ok": True, "count": len(rows), "campaigns": [self._campaign(r) for r in rows]}

    def execution_batch(self, campaign_id: str, limit: int = 100, status: str = "planned") -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId")
        status = str(status or "planned").strip().lower()
        if status not in {"planned", "failed"}:
            raise BatchCampaignError("Execution batches may be requested only for planned or failed trials.")
        with self._connect() as db:
            campaign = db.execute("SELECT * FROM bec_campaigns WHERE id=?", (campaign_id,)).fetchone()
            if not campaign:
                raise BatchCampaignError("Campaign not found.", 404)
            rows = db.execute("SELECT * FROM bec_trials WHERE campaign_id=? AND status=? ORDER BY ordinal LIMIT ?", (campaign_id, status, max(1, min(1000, int(limit))))).fetchall()
        handoffs = []
        for row in rows:
            trial = self._trial(row); spec = trial["spec"]
            handoff = {
                "schema": HANDOFF_SCHEMA,
                "campaignId": campaign_id,
                "trialId": trial["id"],
                "attempt": trial["attempt"],
                "method": spec["method"],
                "workflowRef": spec.get("workflowRef") or "",
                "modelRef": spec.get("modelRef") or "",
                "inputs": spec.get("inputs") or {},
                "parameters": {**(spec.get("fixedParameters") or {}), **(spec.get("parameterValues") or {})},
                "requestedOutputs": spec.get("requestedOutputs") or [],
                "randomSeed": trial["seed"],
                "trialSpecHash": trial["specHash"],
                "dispatchRequested": False,
                "executionAuthority": "Workspace/runtime fabric",
            }
            handoff["handoffHash"] = _sha(handoff)
            handoffs.append(handoff)
        return {"ok": True, "campaignId": campaign_id, "count": len(handoffs), "automaticDispatch": False, "handoffs": handoffs}

    def record_trial_state(self, campaign_id: str, trial_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId"); trial_id = _clean_id(trial_id, "trialId")
        actor = _text(actor, "actor", 300, True)
        state = str(payload.get("status") or "").strip().lower()
        allowed = {"planned", "queued", "running", "succeeded", "failed", "cancelled"}
        if state not in allowed:
            raise BatchCampaignError(f"Unsupported trial status: {state}.")
        metrics = _json(payload.get("metrics") or {}, "metrics", 500_000)
        if not isinstance(metrics, dict):
            raise BatchCampaignError("metrics must be an object.")
        for key, value in list(metrics.items()):
            if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isfinite(float(value)):
                raise BatchCampaignError(f"Metric {key} must be finite.")
        execution_ref = _text(payload.get("executionRef"), "executionRef", 500, False)
        result_ref = _text(payload.get("resultRef"), "resultRef", 500, False)
        error_text = _text(payload.get("error"), "error", 4000, False)
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM bec_trials WHERE id=? AND campaign_id=?", (trial_id, campaign_id)).fetchone()
            if not row:
                raise BatchCampaignError("Trial not found.", 404)
            db.execute(
                "UPDATE bec_trials SET status=?,execution_ref=?,result_ref=?,metrics_json=?,error_text=?,updated_at=? WHERE id=?",
                (state, execution_ref, result_ref, json.dumps(metrics, sort_keys=True), error_text, _now(), trial_id),
            )
            self._event(db, campaign_id, trial_id, "trial-state-recorded", actor, {"status": state, "executionRef": execution_ref, "resultRef": result_ref, "metrics": metrics, "error": error_text})
            self._refresh_status(db, campaign_id); db.commit()
        return self.get(campaign_id, include_trials=False) | {"trial": self.trial(trial_id)}

    def trial(self, trial_id: str) -> dict[str, Any]:
        trial_id = _clean_id(trial_id, "trialId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM bec_trials WHERE id=?", (trial_id,)).fetchone()
            if not row:
                raise BatchCampaignError("Trial not found.", 404)
        return self._trial(row)

    def retry_failed(self, campaign_id: str, actor: str, limit: int = 100) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId"); actor = _text(actor, "actor", 300, True)
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT * FROM bec_trials WHERE campaign_id=? AND status='failed' ORDER BY ordinal LIMIT ?", (campaign_id, max(1, min(1000, int(limit))))).fetchall()
            for row in rows:
                db.execute("UPDATE bec_trials SET status='planned',attempt=attempt+1,execution_ref='',result_ref='',metrics_json='{}',error_text='',updated_at=? WHERE id=?", (_now(), row["id"]))
                self._event(db, campaign_id, row["id"], "trial-retry-planned", actor, {"previousAttempt": int(row["attempt"]), "nextAttempt": int(row["attempt"]) + 1})
            self._refresh_status(db, campaign_id); db.commit()
        return {"ok": True, "campaignId": campaign_id, "retryCount": len(rows), "automaticDispatch": False, "campaign": self.get(campaign_id)["campaign"]}

    def aggregate(self, campaign_id: str) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId")
        with self._connect() as db:
            rows = db.execute("SELECT metrics_json FROM bec_trials WHERE campaign_id=? AND status='succeeded' ORDER BY ordinal", (campaign_id,)).fetchall()
        buckets: dict[str, list[float]] = {}
        for row in rows:
            metrics = json.loads(row["metrics_json"] or "{}")
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
                    buckets.setdefault(str(key), []).append(float(value))
        summary: dict[str, Any] = {}
        for key, values in buckets.items():
            values.sort(); n = len(values)
            summary[key] = {
                "count": n, "mean": statistics.fmean(values), "stdev": statistics.stdev(values) if n > 1 else 0.0,
                "min": values[0], "q05": _quantile(values, 0.05), "median": _quantile(values, 0.5),
                "q95": _quantile(values, 0.95), "max": values[-1],
            }
        return {"ok": True, "campaignId": campaign_id, "succeededTrials": len(rows), "metrics": summary, "descriptiveOnly": True, "scientificValidityEstablished": False}

    def manifest(self, campaign_id: str) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId")
        with self._connect() as db:
            campaign = db.execute("SELECT * FROM bec_campaigns WHERE id=?", (campaign_id,)).fetchone()
            if not campaign:
                raise BatchCampaignError("Campaign not found.", 404)
            rows = db.execute("SELECT id,ordinal,attempt,seed,spec_hash,status,execution_ref,result_ref FROM bec_trials WHERE campaign_id=? ORDER BY ordinal", (campaign_id,)).fetchall()
        body = {
            "schema": MANIFEST_SCHEMA, "version": VERSION, "campaignId": campaign_id, "projectId": campaign["project_id"],
            "definitionHash": campaign["definition_hash"],
            "trials": [{"id": r["id"], "ordinal": int(r["ordinal"]), "attempt": int(r["attempt"]), "seed": int(r["seed"]), "specHash": r["spec_hash"], "status": r["status"], "executionRef": r["execution_ref"], "resultRef": r["result_ref"]} for r in rows],
            "automaticDispatch": False, "arbitraryCodeExecution": False, "humanScientificReviewRequired": True,
        }
        body["manifestDigest"] = _sha(body)
        return {"ok": True, "manifest": body}

    def verify_manifest(self, payload: dict[str, Any]) -> dict[str, Any]:
        manifest = _json(payload.get("manifest") or payload, "manifest", 2_000_000)
        if not isinstance(manifest, dict):
            raise BatchCampaignError("manifest must be an object.")
        supplied = str(manifest.get("manifestDigest") or "")
        unsigned = dict(manifest); unsigned.pop("manifestDigest", None)
        computed = _sha(unsigned)
        return {"ok": supplied == computed and bool(supplied), "suppliedDigest": supplied, "computedDigest": computed, "schema": manifest.get("schema")}

    def archive(self, campaign_id: str, actor: str) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId"); actor = _text(actor, "actor", 300, True)
        with self._lock, self._connect() as db:
            row = db.execute("SELECT id FROM bec_campaigns WHERE id=?", (campaign_id,)).fetchone()
            if not row:
                raise BatchCampaignError("Campaign not found.", 404)
            db.execute("UPDATE bec_campaigns SET archived=1,updated_at=? WHERE id=?", (_now(), campaign_id))
            self._event(db, campaign_id, "", "campaign-archived", actor, {})
            db.commit()
        return self.get(campaign_id)

    def timeline(self, campaign_id: str, limit: int = 500) -> dict[str, Any]:
        campaign_id = _clean_id(campaign_id, "campaignId")
        with self._connect() as db:
            rows = db.execute("SELECT * FROM bec_events WHERE campaign_id=? ORDER BY seq DESC LIMIT ?", (campaign_id, max(1, min(5000, int(limit))))).fetchall()
        events = [{"seq": int(r["seq"]), "campaignId": r["campaign_id"], "trialId": r["trial_id"], "eventType": r["event_type"], "occurredAt": r["occurred_at"], "actor": r["actor"], "payload": json.loads(r["payload_json"] or "{}"), "previousHash": r["previous_hash"], "eventHash": r["event_hash"]} for r in rows]
        return {"ok": True, "campaignId": campaign_id, "count": len(events), "events": events}
