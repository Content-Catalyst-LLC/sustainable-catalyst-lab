from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import copy
import json
import math
from pathlib import Path
import random
import re
import secrets
import sqlite3
import threading
from typing import Any

from .workflow_orchestration import WorkflowError
from .bayesian_optimization import (
    BayesianOptimizationError,
    estimate_cost,
    normalize_resource_model,
    normalize_strategy as normalize_bayesian_strategy,
    propose as propose_bayesian,
)

VERSION = "0.33.1"
CAMPAIGN_SCHEMA = "sc-lab-experiment-campaign/0.33.1"
TRIAL_SCHEMA = "sc-lab-experiment-trial/0.33.1"
EVENT_SCHEMA = "sc-lab-experiment-campaign-event/0.33.1"
SURROGATE_SCHEMA = "sc-lab-experiment-surrogate/0.33.1"
DB_SCHEMA_VERSION = 2
CAMPAIGN_STATES = {"draft", "running", "paused", "completed", "failed", "cancelled"}
TRIAL_STATES = {"proposed", "queued", "running", "completed", "failed", "cancelled"}
TERMINAL_TRIAL_STATES = {"completed", "failed", "cancelled"}
PARAMETER_TYPES = {"continuous", "integer", "categorical"}
STRATEGIES = {"random", "grid", "adaptive-explore-exploit", "bayesian-optimization", "active-learning", "resource-aware-bayesian"}
GOALS = {"minimize", "maximize"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")


class ExperimentCampaignError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 2000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _int(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def _float(value: Any, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if not math.isfinite(number):
        number = default
    return max(low, min(high, number))


def _deep_set(target: dict[str, Any], path: str, value: Any) -> None:
    parts = [part for part in path.split(".") if part]
    if not parts:
        raise ExperimentCampaignError("A parameter input path is required.")
    current = target
    for part in parts[:-1]:
        child = current.get(part)
        if child is None:
            child = {}
            current[part] = child
        if not isinstance(child, dict):
            raise ExperimentCampaignError(f"Parameter input path crosses a non-object value: {path}")
        current = child
    current[parts[-1]] = copy.deepcopy(value)


def _deep_get_optional(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    for part in [item for item in path.split(".") if item]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, copy.deepcopy(current)


def _normalize_parameter(name: str, raw: Any) -> dict[str, Any]:
    if not ID_RE.match(name):
        raise ExperimentCampaignError(f"Invalid parameter name: {name}")
    if not isinstance(raw, dict):
        raise ExperimentCampaignError(f"Parameter {name} must be an object.")
    kind = _text(raw.get("type"), 40)
    if kind not in PARAMETER_TYPES:
        raise ExperimentCampaignError(f"Parameter {name} has unsupported type: {kind}")
    parameter: dict[str, Any] = {"type": kind}
    if kind == "categorical":
        values = raw.get("values")
        if not isinstance(values, list) or not values or len(values) > 1000:
            raise ExperimentCampaignError(f"Categorical parameter {name} requires 1–1000 values.")
        if any(isinstance(item, (dict, list)) for item in values):
            raise ExperimentCampaignError(f"Categorical parameter {name} values must be scalar.")
        parameter["values"] = copy.deepcopy(values)
        return parameter
    minimum = _float(raw.get("min"), 0.0, -1e15, 1e15)
    maximum = _float(raw.get("max"), 1.0, -1e15, 1e15)
    if maximum <= minimum:
        raise ExperimentCampaignError(f"Parameter {name} requires max greater than min.")
    parameter.update({"min": minimum, "max": maximum})
    if kind == "integer":
        parameter["min"] = int(math.ceil(minimum))
        parameter["max"] = int(math.floor(maximum))
        if parameter["max"] < parameter["min"]:
            raise ExperimentCampaignError(f"Integer parameter {name} has no valid values.")
        parameter["step"] = _int(raw.get("step"), 1, 1, max(1, parameter["max"] - parameter["min"] + 1))
    else:
        parameter["precision"] = _int(raw.get("precision"), 8, 0, 15)
    return parameter


def normalize_campaign(payload: dict[str, Any], max_trials_limit: int = 10000) -> dict[str, Any]:
    source = payload.get("campaign") if isinstance(payload.get("campaign"), dict) else payload
    campaign_id = _text(source.get("id"), 180) or f"campaign-{secrets.token_hex(8)}"
    if not ID_RE.match(campaign_id):
        raise ExperimentCampaignError("Campaign ID must contain only letters, numbers, dots, underscores, and hyphens.")
    workflow_id = _text(source.get("workflowId"), 180)
    if not workflow_id or not ID_RE.match(workflow_id):
        raise ExperimentCampaignError("A valid workflowId is required.")
    raw_space = source.get("parameterSpace")
    if not isinstance(raw_space, dict) or not raw_space:
        raise ExperimentCampaignError("parameterSpace must contain at least one parameter.")
    if len(raw_space) > 100:
        raise ExperimentCampaignError("A campaign may define at most 100 parameters.")
    parameter_space = {str(name): _normalize_parameter(str(name), raw) for name, raw in raw_space.items()}

    objective_raw = source.get("objective") if isinstance(source.get("objective"), dict) else {}
    objective_path = _text(objective_raw.get("path"), 500)
    if not objective_path or not (objective_path.startswith("nodes.") or objective_path.startswith("run.")):
        raise ExperimentCampaignError("objective.path must begin with nodes. or run.")
    goal = _text(objective_raw.get("goal"), 20) or "minimize"
    if goal not in GOALS:
        raise ExperimentCampaignError("objective.goal must be minimize or maximize.")
    objective: dict[str, Any] = {"path": objective_path, "goal": goal}
    if objective_raw.get("target") is not None:
        objective["target"] = _float(objective_raw.get("target"), 0.0, -1e300, 1e300)

    strategy_raw = source.get("strategy") if isinstance(source.get("strategy"), dict) else {}
    strategy_type = _text(strategy_raw.get("type"), 80) or "bayesian-optimization"
    if strategy_type not in STRATEGIES:
        raise ExperimentCampaignError(f"Unsupported campaign strategy: {strategy_type}")
    if strategy_type in {"bayesian-optimization", "active-learning", "resource-aware-bayesian"}:
        try:
            strategy = normalize_bayesian_strategy({**strategy_raw, "type": strategy_type}, len(parameter_space))
        except BayesianOptimizationError as exc:
            raise ExperimentCampaignError(str(exc)) from exc
    else:
        strategy = {
            "type": strategy_type,
            "initialRandomTrials": _int(strategy_raw.get("initialRandomTrials"), max(3, min(8, len(parameter_space) * 2)), 1, 1000),
            "explorationRate": _float(strategy_raw.get("explorationRate"), 0.30, 0.0, 1.0),
            "neighborhoodScale": _float(strategy_raw.get("neighborhoodScale"), 0.20, 0.001, 1.0),
            "gridLevels": _int(strategy_raw.get("gridLevels"), 5, 2, 100),
            "randomSeed": _int(strategy_raw.get("randomSeed"), 3300, 0, 2147483647),
        }
    resource_model = normalize_resource_model(source.get("resourceModel"), parameter_space)
    if strategy_type == "resource-aware-bayesian":
        resource_model["enabled"] = True

    budget_raw = source.get("budget") if isinstance(source.get("budget"), dict) else {}
    max_trials = _int(budget_raw.get("maxTrials"), 25, 1, max_trials_limit)
    budget = {
        "maxTrials": max_trials,
        "maxFailures": _int(budget_raw.get("maxFailures"), max(3, min(10, max_trials // 3 or 1)), 1, max_trials),
        "maxConcurrentTrials": _int(budget_raw.get("maxConcurrentTrials"), 1, 1, min(100, max_trials)),
    }

    stopping_raw = source.get("stopping") if isinstance(source.get("stopping"), dict) else {}
    stopping: dict[str, Any] = {
        "patience": _int(stopping_raw.get("patience"), max(5, len(parameter_space) * 2), 1, max_trials),
        "minImprovement": _float(stopping_raw.get("minImprovement"), 0.0, 0.0, 1e300),
    }
    if stopping_raw.get("target") is not None:
        stopping["target"] = _float(stopping_raw.get("target"), 0.0, -1e300, 1e300)
    elif "target" in objective:
        stopping["target"] = objective["target"]

    run_raw = source.get("run") if isinstance(source.get("run"), dict) else {}
    input_path = _text(run_raw.get("parameterInputPath"), 500) or "campaign.parameters"
    if not re.match(r"^[A-Za-z0-9_.-]+$", input_path):
        raise ExperimentCampaignError("run.parameterInputPath contains unsupported characters.")
    run = {
        "baseInputs": copy.deepcopy(run_raw.get("baseInputs")) if isinstance(run_raw.get("baseInputs"), dict) else {},
        "baseContext": copy.deepcopy(run_raw.get("baseContext")) if isinstance(run_raw.get("baseContext"), dict) else {},
        "parameterInputPath": input_path,
        "autoAdvance": run_raw.get("autoAdvance", True) is not False,
    }

    record = {
        "schema": CAMPAIGN_SCHEMA,
        "version": VERSION,
        "recordType": "experiment-campaign",
        "id": campaign_id,
        "title": _text(source.get("title"), 300) or campaign_id,
        "description": _text(source.get("description"), 4000),
        "workflowId": workflow_id,
        "projectId": _text(source.get("projectId"), 180) or "default",
        "parameterSpace": parameter_space,
        "objective": objective,
        "strategy": strategy,
        "budget": budget,
        "stopping": stopping,
        "resourceModel": resource_model,
        "run": run,
        "metadata": copy.deepcopy(source.get("metadata")) if isinstance(source.get("metadata"), dict) else {},
    }
    record["definitionHash"] = _hash({k: v for k, v in record.items() if k != "definitionHash"})
    return record


def policies(max_trials: int = 10000, max_campaigns: int = 1000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "workflow-backed-adaptive-sequential-experiment-campaigns",
        "strategies": sorted(STRATEGIES),
        "parameterTypes": sorted(PARAMETER_TYPES),
        "objectives": sorted(GOALS),
        "proposalSafety": {
            "deterministicSeeds": True,
            "duplicateParameterPrevention": True,
            "boundedProposalAttempts": True,
            "arbitraryCode": False,
            "arbitraryCallbacks": False,
        },
        "adaptation": {
            "initialExploration": True,
            "bestPointNeighborhoodSearch": True,
            "configurableExplorationRate": True,
            "sequentialObjectiveUpdates": True,
            "gaussianProcessSurrogate": True,
            "mixedParameterEncoding": True,
            "predictiveUncertainty": True,
            "activeLearning": True,
            "acquisitionPolicies": ["expected-improvement", "probability-improvement", "confidence-bound", "max-variance"],
        },
        "resourceAwareness": {
            "parameterCostModel": True,
            "categoricalCostModel": True,
            "perTrialCostLimit": True,
            "totalCostBudget": True,
            "costAdjustedAcquisition": True,
            "observedCostExtraction": True,
        },
        "execution": {
            "workflowBackedTrials": True,
            "parallelTrialLimit": True,
            "manualObservations": True,
            "automaticReconciliation": True,
            "automaticAdvance": True,
        },
        "stopping": {
            "trialBudget": True,
            "failureBudget": True,
            "targetObjective": True,
            "noImprovementPatience": True,
        },
        "provenance": {
            "campaignDefinitionHash": True,
            "proposalPolicy": True,
            "parameterHash": True,
            "workflowRunLineage": True,
            "objectiveExtractionPath": True,
            "eventTimeline": True,
        },
        "limits": {"maxTrialsPerCampaign": max_trials, "maxCampaigns": max_campaigns},
    }


class ExperimentCampaignManager:
    def __init__(self, db_path: str, workflows: Any, poll_seconds: float = 30.0, max_campaigns: int = 1000, max_trials: int = 10000, history_limit: int = 30000):
        self.db_path = str(db_path)
        self.workflows = workflows
        self.poll_seconds = max(1.0, min(3600.0, float(poll_seconds)))
        self.max_campaigns = max(1, int(max_campaigns))
        self.max_trials = max(1, int(max_trials))
        self.history_limit = max(100, int(history_limit))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
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
            CREATE TABLE IF NOT EXISTS experiment_campaign_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS experiment_campaigns(
              id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, project_id TEXT NOT NULL,
              title TEXT NOT NULL, status TEXT NOT NULL, definition_hash TEXT NOT NULL,
              definition_json TEXT NOT NULL, best_trial_id TEXT, best_objective REAL,
              no_improvement_count INTEGER NOT NULL DEFAULT 0, stop_reason TEXT,
              cumulative_cost REAL NOT NULL DEFAULT 0, model_json TEXT,
              created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS experiment_trials(
              id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL, sequence_no INTEGER NOT NULL,
              status TEXT NOT NULL, parameters_hash TEXT NOT NULL, parameters_json TEXT NOT NULL,
              proposal_json TEXT NOT NULL, workflow_run_id TEXT, objective_value REAL,
              objective_json TEXT, result_json TEXT, error_text TEXT,
              predicted_mean REAL, predicted_std REAL, acquisition_value REAL,
              estimated_cost REAL, observed_cost REAL, resource_json TEXT,
              created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL,
              FOREIGN KEY(campaign_id) REFERENCES experiment_campaigns(id) ON DELETE CASCADE,
              UNIQUE(campaign_id, sequence_no), UNIQUE(campaign_id, parameters_hash)
            );
            CREATE TABLE IF NOT EXISTS experiment_campaign_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id TEXT NOT NULL, trial_id TEXT,
              event_type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL,
              FOREIGN KEY(campaign_id) REFERENCES experiment_campaigns(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_campaign_status ON experiment_campaigns(status,updated_at);
            CREATE INDEX IF NOT EXISTS idx_trial_campaign_status ON experiment_trials(campaign_id,status,sequence_no);
            CREATE INDEX IF NOT EXISTS idx_campaign_event ON experiment_campaign_events(campaign_id,id);
            """)
            campaign_columns = {row[1] for row in con.execute("PRAGMA table_info(experiment_campaigns)")}
            for column, ddl in {
                "cumulative_cost": "ALTER TABLE experiment_campaigns ADD COLUMN cumulative_cost REAL NOT NULL DEFAULT 0",
                "model_json": "ALTER TABLE experiment_campaigns ADD COLUMN model_json TEXT",
            }.items():
                if column not in campaign_columns:
                    con.execute(ddl)
            trial_columns = {row[1] for row in con.execute("PRAGMA table_info(experiment_trials)")}
            for column, ddl in {
                "predicted_mean": "ALTER TABLE experiment_trials ADD COLUMN predicted_mean REAL",
                "predicted_std": "ALTER TABLE experiment_trials ADD COLUMN predicted_std REAL",
                "acquisition_value": "ALTER TABLE experiment_trials ADD COLUMN acquisition_value REAL",
                "estimated_cost": "ALTER TABLE experiment_trials ADD COLUMN estimated_cost REAL",
                "observed_cost": "ALTER TABLE experiment_trials ADD COLUMN observed_cost REAL",
                "resource_json": "ALTER TABLE experiment_trials ADD COLUMN resource_json TEXT",
            }.items():
                if column not in trial_columns:
                    con.execute(ddl)
            con.execute("INSERT OR REPLACE INTO experiment_campaign_meta(key,value) VALUES('schema_version',?)", (str(DB_SCHEMA_VERSION),))

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="sc-lab-experiment-campaigns", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=max(2.0, self.poll_seconds + 1.0))

    def _loop(self) -> None:
        while not self._stop.wait(self.poll_seconds):
            try:
                self.tick()
            except Exception:
                continue

    def _event(self, con: sqlite3.Connection, campaign_id: str, trial_id: str | None, event_type: str, payload: dict[str, Any]) -> None:
        con.execute("INSERT INTO experiment_campaign_events(campaign_id,trial_id,event_type,payload_json,created_at) VALUES(?,?,?,?,?)", (campaign_id, trial_id, event_type, _stable(payload), _now()))
        count = con.execute("SELECT COUNT(*) FROM experiment_campaign_events").fetchone()[0]
        if count > self.history_limit:
            con.execute("DELETE FROM experiment_campaign_events WHERE id IN (SELECT id FROM experiment_campaign_events ORDER BY id LIMIT ?)", (count - self.history_limit,))

    @staticmethod
    def _loads(value: str | None) -> Any:
        if not value:
            return None
        return json.loads(value)

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = normalize_campaign(payload, self.max_trials)
        try:
            self.workflows.get(record["workflowId"])
        except Exception as exc:
            detail = getattr(exc, "detail", str(exc))
            raise ExperimentCampaignError(f"Workflow validation failed: {detail}", 404) from exc
        return {"ok": True, "campaign": record}

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = self.validate(payload)["campaign"]
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute("SELECT * FROM experiment_campaigns WHERE id=?", (record["id"],)).fetchone()
            if not existing:
                count = con.execute("SELECT COUNT(*) FROM experiment_campaigns").fetchone()[0]
                if count >= self.max_campaigns:
                    con.execute("ROLLBACK")
                    raise ExperimentCampaignError("Experiment campaign capacity reached.", 429)
                con.execute("INSERT INTO experiment_campaigns(id,workflow_id,project_id,title,status,definition_hash,definition_json,created_at,updated_at) VALUES(?,?,?,?, 'draft',?,?,?,?)", (record["id"], record["workflowId"], record["projectId"], record["title"], record["definitionHash"], _stable(record), now, now))
                self._event(con, record["id"], None, "campaign-created", {"definitionHash": record["definitionHash"], "workflowId": record["workflowId"]})
                created = True
            else:
                if existing["status"] in {"running", "completed", "failed", "cancelled"}:
                    con.execute("ROLLBACK")
                    raise ExperimentCampaignError("Only draft or paused campaigns may be edited.", 409)
                trials = con.execute("SELECT COUNT(*) FROM experiment_trials WHERE campaign_id=?", (record["id"],)).fetchone()[0]
                if trials:
                    con.execute("ROLLBACK")
                    raise ExperimentCampaignError("A campaign with trials cannot change its definition. Create a new campaign ID.", 409)
                con.execute("UPDATE experiment_campaigns SET workflow_id=?,project_id=?,title=?,definition_hash=?,definition_json=?,updated_at=? WHERE id=?", (record["workflowId"], record["projectId"], record["title"], record["definitionHash"], _stable(record), now, record["id"]))
                self._event(con, record["id"], None, "campaign-updated", {"definitionHash": record["definitionHash"]})
                created = False
            con.execute("COMMIT")
        return {"ok": True, "created": created, "campaign": self.get(record["id"])["campaign"]}

    def _campaign_row(self, con: sqlite3.Connection, campaign_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM experiment_campaigns WHERE id=?", (_text(campaign_id, 180),)).fetchone()
        if not row:
            raise ExperimentCampaignError("Experiment campaign was not found.", 404)
        return row

    def _trial_item(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": TRIAL_SCHEMA, "version": VERSION, "recordType": "experiment-trial",
            "id": row["id"], "campaignId": row["campaign_id"], "sequence": int(row["sequence_no"]),
            "status": row["status"], "parameters": self._loads(row["parameters_json"]),
            "parametersHash": row["parameters_hash"], "proposal": self._loads(row["proposal_json"]),
            "workflowRunId": row["workflow_run_id"], "objectiveValue": row["objective_value"],
            "objective": self._loads(row["objective_json"]), "result": self._loads(row["result_json"]),
            "prediction": ({"mean": row["predicted_mean"], "standardDeviation": row["predicted_std"]} if row["predicted_mean"] is not None else None),
            "acquisitionValue": row["acquisition_value"], "estimatedCost": row["estimated_cost"],
            "observedCost": row["observed_cost"], "resource": self._loads(row["resource_json"]),
            "error": row["error_text"], "createdAt": row["created_at"], "startedAt": row["started_at"],
            "completedAt": row["completed_at"], "updatedAt": row["updated_at"],
        }

    def _campaign_item(self, con: sqlite3.Connection, row: sqlite3.Row, include_trials: bool = False) -> dict[str, Any]:
        definition = self._loads(row["definition_json"])
        counts = {state: 0 for state in TRIAL_STATES}
        for count_row in con.execute("SELECT status,COUNT(*) count FROM experiment_trials WHERE campaign_id=? GROUP BY status", (row["id"],)):
            counts[count_row["status"]] = int(count_row["count"])
        best = None
        if row["best_trial_id"]:
            best_row = con.execute("SELECT * FROM experiment_trials WHERE id=?", (row["best_trial_id"],)).fetchone()
            best = self._trial_item(best_row) if best_row else None
        item = {
            **definition,
            "status": row["status"], "bestTrialId": row["best_trial_id"], "bestObjective": row["best_objective"],
            "bestTrial": best, "noImprovementCount": int(row["no_improvement_count"] or 0),
            "stopReason": row["stop_reason"], "trialCounts": counts,
            "cumulativeCost": float(row["cumulative_cost"] or 0.0),
            "surrogate": self._loads(row["model_json"]),
            "createdAt": row["created_at"], "startedAt": row["started_at"], "completedAt": row["completed_at"], "updatedAt": row["updated_at"],
        }
        if include_trials:
            trial_rows = con.execute("SELECT * FROM experiment_trials WHERE campaign_id=? ORDER BY sequence_no", (row["id"],)).fetchall()
            item["trials"] = [self._trial_item(trial) for trial in trial_rows]
        return item

    def get(self, campaign_id: str, reconcile: bool = False) -> dict[str, Any]:
        if reconcile:
            self.reconcile(campaign_id, auto_advance=False)
        with self._connect() as con:
            row = self._campaign_row(con, campaign_id)
            return {"ok": True, "campaign": self._campaign_item(con, row, include_trials=True)}

    def list(self, project_id: str = "", status: str = "", limit: int = 100) -> dict[str, Any]:
        if status and status not in CAMPAIGN_STATES:
            raise ExperimentCampaignError("Unsupported campaign status.")
        clauses: list[str] = []
        params: list[Any] = []
        if project_id:
            clauses.append("project_id=?"); params.append(_text(project_id, 180))
        if status:
            clauses.append("status=?"); params.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM experiment_campaigns{where} ORDER BY updated_at DESC LIMIT ?", params).fetchall()
            items = [self._campaign_item(con, row, include_trials=False) for row in rows]
        return {"ok": True, "count": len(items), "campaigns": items}

    @staticmethod
    def _domain_values(spec: dict[str, Any], levels: int) -> list[Any]:
        if spec["type"] == "categorical":
            return list(spec["values"])
        if spec["type"] == "integer":
            return list(range(int(spec["min"]), int(spec["max"]) + 1, int(spec.get("step", 1))))
        if levels <= 1:
            return [(spec["min"] + spec["max"]) / 2]
        return [round(spec["min"] + (spec["max"] - spec["min"]) * i / (levels - 1), int(spec.get("precision", 8))) for i in range(levels)]

    def _random_parameters(self, definition: dict[str, Any], rng: random.Random) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name, spec in definition["parameterSpace"].items():
            if spec["type"] == "categorical":
                result[name] = copy.deepcopy(rng.choice(spec["values"]))
            elif spec["type"] == "integer":
                values = self._domain_values(spec, definition["strategy"]["gridLevels"])
                result[name] = int(rng.choice(values))
            else:
                result[name] = round(rng.uniform(float(spec["min"]), float(spec["max"])), int(spec.get("precision", 8)))
        return result

    def _grid_parameters(self, definition: dict[str, Any], sequence: int) -> dict[str, Any]:
        spaces = [(name, self._domain_values(spec, definition["strategy"]["gridLevels"])) for name, spec in definition["parameterSpace"].items()]
        index = max(0, sequence - 1)
        result: dict[str, Any] = {}
        for name, values in reversed(spaces):
            result[name] = copy.deepcopy(values[index % len(values)])
            index //= len(values)
        return {name: result[name] for name, _values in spaces}

    def _adaptive_parameters(self, definition: dict[str, Any], best: dict[str, Any] | None, rng: random.Random) -> tuple[dict[str, Any], str]:
        strategy = definition["strategy"]
        if not best or rng.random() < strategy["explorationRate"]:
            return self._random_parameters(definition, rng), "explore-random"
        result: dict[str, Any] = {}
        scale = strategy["neighborhoodScale"]
        for name, spec in definition["parameterSpace"].items():
            center = best.get(name)
            if spec["type"] == "categorical":
                if center in spec["values"] and rng.random() >= strategy["explorationRate"]:
                    result[name] = copy.deepcopy(center)
                else:
                    result[name] = copy.deepcopy(rng.choice(spec["values"]))
            elif spec["type"] == "integer":
                span = max(1.0, (spec["max"] - spec["min"]) * scale)
                proposed = int(round(float(center if center is not None else (spec["min"] + spec["max"]) / 2) + rng.gauss(0.0, span)))
                proposed = max(int(spec["min"]), min(int(spec["max"]), proposed))
                step = int(spec.get("step", 1))
                result[name] = int(spec["min"] + round((proposed - spec["min"]) / step) * step)
            else:
                span = (spec["max"] - spec["min"]) * scale
                proposed = float(center if center is not None else (spec["min"] + spec["max"]) / 2) + rng.gauss(0.0, span)
                proposed = max(float(spec["min"]), min(float(spec["max"]), proposed))
                result[name] = round(proposed, int(spec.get("precision", 8)))
        return result, "exploit-best-neighborhood"

    def _completed_observations(self, con: sqlite3.Connection, campaign_id: str) -> list[dict[str, Any]]:
        rows = con.execute("SELECT parameters_json,objective_value,observed_cost,estimated_cost FROM experiment_trials WHERE campaign_id=? AND status='completed' AND objective_value IS NOT NULL ORDER BY sequence_no", (campaign_id,)).fetchall()
        return [
            {
                "parameters": self._loads(row["parameters_json"]),
                "objective": float(row["objective_value"]),
                "cost": float(row["observed_cost"] if row["observed_cost"] is not None else (row["estimated_cost"] or 0.0)),
            }
            for row in rows
        ]

    def _best_parameters(self, con: sqlite3.Connection, campaign: sqlite3.Row) -> dict[str, Any] | None:
        if not campaign["best_trial_id"]:
            return None
        row = con.execute("SELECT parameters_json FROM experiment_trials WHERE id=?", (campaign["best_trial_id"],)).fetchone()
        return self._loads(row["parameters_json"]) if row else None

    def _proposal(self, con: sqlite3.Connection, campaign: sqlite3.Row, sequence: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
        definition = self._loads(campaign["definition_json"])
        existing = {row["parameters_hash"] for row in con.execute("SELECT parameters_hash FROM experiment_trials WHERE campaign_id=?", (campaign["id"],))}
        completed = con.execute("SELECT * FROM experiment_trials WHERE campaign_id=? AND status='completed' ORDER BY sequence_no", (campaign["id"],)).fetchall()
        best_parameters = self._best_parameters(con, campaign)
        seed = int(definition["strategy"]["randomSeed"]) + sequence * 104729
        rng = random.Random(seed)
        policy = definition["strategy"]["type"]
        if policy in {"bayesian-optimization", "active-learning", "resource-aware-bayesian"}:
            try:
                parameters, bayesian_proposal, diagnostics = propose_bayesian(
                    definition["parameterSpace"],
                    self._completed_observations(con, campaign["id"]),
                    definition["strategy"],
                    definition.get("resourceModel") or normalize_resource_model({}, definition["parameterSpace"]),
                    definition["objective"]["goal"],
                    seed,
                    existing,
                    best_parameters,
                )
            except BayesianOptimizationError as exc:
                raise ExperimentCampaignError(str(exc), 409) from exc
            proposal = {
                "strategy": policy,
                "seed": seed,
                "proposedAt": _now(),
                **bayesian_proposal,
            }
            return parameters, proposal, diagnostics
        for attempt in range(200):
            if policy == "grid":
                parameters = self._grid_parameters(definition, sequence + attempt)
                source = "grid-sequential"
            elif policy == "random" or len(completed) < definition["strategy"]["initialRandomTrials"]:
                parameters = self._random_parameters(definition, rng)
                source = "initial-random" if policy != "random" else "random"
            else:
                parameters, source = self._adaptive_parameters(definition, best_parameters, rng)
            parameter_hash = _hash(parameters)
            if parameter_hash not in existing:
                estimated_cost = estimate_cost(definition.get("resourceModel") or normalize_resource_model({}, definition["parameterSpace"]), definition["parameterSpace"], parameters)
                return parameters, {"strategy": policy, "source": source, "seed": seed, "attempt": attempt, "proposedAt": _now(), "estimatedCost": estimated_cost}, None
        raise ExperimentCampaignError("The parameter space is exhausted or no unique proposal could be generated.", 409)

    def preview_proposal(self, campaign_id: str) -> dict[str, Any]:
        with self._connect() as con:
            campaign = self._campaign_row(con, campaign_id)
            sequence = int(con.execute("SELECT COALESCE(MAX(sequence_no),0)+1 FROM experiment_trials WHERE campaign_id=?", (campaign_id,)).fetchone()[0])
            parameters, proposal, diagnostics = self._proposal(con, campaign, sequence)
        return {"ok": True, "campaignId": campaign_id, "sequence": sequence, "parameters": parameters, "parametersHash": _hash(parameters), "proposal": proposal, "surrogate": diagnostics}

    def surrogate(self, campaign_id: str) -> dict[str, Any]:
        with self._connect() as con:
            campaign = self._campaign_row(con, campaign_id)
            definition = self._loads(campaign["definition_json"])
            observations = self._completed_observations(con, campaign_id)
            model = self._loads(campaign["model_json"])
        return {
            "ok": True,
            "schema": SURROGATE_SCHEMA,
            "version": VERSION,
            "campaignId": campaign_id,
            "strategy": definition["strategy"],
            "resourceModel": definition.get("resourceModel"),
            "observationCount": len(observations),
            "observations": observations,
            "model": model,
        }

    def _build_run_payload(self, definition: dict[str, Any], trial_id: str, sequence: int, parameters: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
        inputs = copy.deepcopy(definition["run"]["baseInputs"])
        _deep_set(inputs, definition["run"]["parameterInputPath"], parameters)
        context = copy.deepcopy(definition["run"]["baseContext"])
        context["experimentCampaign"] = {
            "schema": CAMPAIGN_SCHEMA, "version": VERSION, "campaignId": definition["id"],
            "trialId": trial_id, "sequence": sequence, "definitionHash": definition["definitionHash"],
            "parameters": copy.deepcopy(parameters), "parametersHash": _hash(parameters), "proposal": copy.deepcopy(proposal),
        }
        return {"id": f"campaign-run-{definition['id']}-{sequence:06d}-{secrets.token_hex(3)}", "inputs": inputs, "context": context}

    def _launch_one(self, campaign_id: str) -> dict[str, Any]:
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            campaign = self._campaign_row(con, campaign_id)
            if campaign["status"] != "running":
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("Campaign must be running to launch trials.", 409)
            definition = self._loads(campaign["definition_json"])
            count = con.execute("SELECT COUNT(*) FROM experiment_trials WHERE campaign_id=?", (campaign_id,)).fetchone()[0]
            if count >= definition["budget"]["maxTrials"]:
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("Campaign trial budget is exhausted.", 409)
            sequence = int(con.execute("SELECT COALESCE(MAX(sequence_no),0)+1 FROM experiment_trials WHERE campaign_id=?", (campaign_id,)).fetchone()[0])
            parameters, proposal, diagnostics = self._proposal(con, campaign, sequence)
            estimated_cost = float(proposal.get("estimatedCost") or estimate_cost(definition.get("resourceModel") or normalize_resource_model({}, definition["parameterSpace"]), definition["parameterSpace"], parameters))
            reserved_cost = float(con.execute(
                "SELECT COALESCE(SUM(estimated_cost),0) FROM experiment_trials WHERE campaign_id=? AND status IN ('proposed','queued','running')",
                (campaign_id,),
            ).fetchone()[0] or 0.0)
            projected_cost = float(campaign["cumulative_cost"] or 0.0) + reserved_cost + estimated_cost
            if projected_cost > float((definition.get("resourceModel") or {}).get("maxTotalCost", 1e15)):
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("Campaign resource budget would be exceeded by active reservations and the next proposal.", 409)
            prediction = proposal.get("prediction") if isinstance(proposal.get("prediction"), dict) else {}
            acquisition = proposal.get("acquisition") if isinstance(proposal.get("acquisition"), dict) else {}
            trial_id = f"trial-{campaign_id}-{sequence:06d}"
            con.execute("INSERT INTO experiment_trials(id,campaign_id,sequence_no,status,parameters_hash,parameters_json,proposal_json,predicted_mean,predicted_std,acquisition_value,estimated_cost,resource_json,created_at,updated_at) VALUES(?,?,?, 'proposed',?,?,?,?,?,?,?,?,?,?)", (trial_id, campaign_id, sequence, _hash(parameters), _stable(parameters), _stable(proposal), prediction.get("mean"), prediction.get("standardDeviation"), acquisition.get("costAdjustedValue", acquisition.get("rawValue")), estimated_cost, _stable({"estimatedCost": estimated_cost, "modelHash": proposal.get("modelHash")}), now, now))
            if diagnostics:
                con.execute("UPDATE experiment_campaigns SET model_json=?,updated_at=? WHERE id=?", (_stable(diagnostics), now, campaign_id))
            self._event(con, campaign_id, trial_id, "trial-proposed", {"sequence": sequence, "parameters": parameters, "proposal": proposal, "surrogate": diagnostics})
            con.execute("COMMIT")
        try:
            run_payload = self._build_run_payload(definition, trial_id, sequence, parameters, proposal)
            run = self.workflows.start_run(definition["workflowId"], run_payload)["run"]
            with self._connect() as con:
                con.execute("UPDATE experiment_trials SET status=?,workflow_run_id=?,started_at=?,updated_at=? WHERE id=?", ("running" if run["status"] == "running" else "queued", run["id"], now, _now(), trial_id))
                self._event(con, campaign_id, trial_id, "trial-launched", {"workflowRunId": run["id"], "workflowStatus": run["status"]})
        except Exception as exc:
            detail = _text(getattr(exc, "detail", str(exc)), 2000)
            with self._connect() as con:
                con.execute("UPDATE experiment_trials SET status='failed',error_text=?,completed_at=?,updated_at=? WHERE id=?", (detail, _now(), _now(), trial_id))
                self._event(con, campaign_id, trial_id, "trial-launch-failed", {"error": detail})
        return self.trial(trial_id)

    def _objective_root(self, run: dict[str, Any]) -> dict[str, Any]:
        return {"run": run, "nodes": {node["nodeId"]: node for node in run.get("nodes", [])}}

    def _extract_objective(self, definition: dict[str, Any], run: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        found, value = _deep_get_optional(self._objective_root(run), definition["objective"]["path"])
        if not found:
            raise ExperimentCampaignError(f"Objective path was not found: {definition['objective']['path']}")
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ExperimentCampaignError("The extracted objective is not numeric.") from exc
        if not math.isfinite(numeric):
            raise ExperimentCampaignError("The extracted objective is not finite.")
        return numeric, {"path": definition["objective"]["path"], "goal": definition["objective"]["goal"], "value": numeric, "extractedAt": _now()}

    def _extract_resource_cost(self, definition: dict[str, Any], run: dict[str, Any], estimated: float | None) -> tuple[float, dict[str, Any]]:
        resource = definition.get("resourceModel") if isinstance(definition.get("resourceModel"), dict) else {}
        path = str(resource.get("resultCostPath") or "").strip()
        source = "estimated"
        value = estimated if estimated is not None else float(resource.get("baseCost", 1.0))
        if path:
            found, extracted = _deep_get_optional(self._objective_root(run), path)
            if found:
                try:
                    candidate = float(extracted)
                except (TypeError, ValueError):
                    candidate = value
                if math.isfinite(candidate) and candidate >= 0:
                    value = candidate
                    source = "workflow-result"
        numeric = max(0.0, float(value or 0.0))
        return numeric, {"value": numeric, "source": source, "path": path or None, "extractedAt": _now()}

    @staticmethod
    def _is_better(goal: str, candidate: float, best: float | None, minimum: float) -> bool:
        if best is None:
            return True
        return candidate < best - minimum if goal == "minimize" else candidate > best + minimum

    @staticmethod
    def _target_met(goal: str, value: float | None, target: float | None) -> bool:
        if value is None or target is None:
            return False
        return value <= target if goal == "minimize" else value >= target

    def _refresh_campaign_state(self, con: sqlite3.Connection, campaign_id: str) -> sqlite3.Row:
        campaign = self._campaign_row(con, campaign_id)
        definition = self._loads(campaign["definition_json"])
        counts = {row["status"]: int(row["count"]) for row in con.execute("SELECT status,COUNT(*) count FROM experiment_trials WHERE campaign_id=? GROUP BY status", (campaign_id,))}
        total = sum(counts.values())
        completed = counts.get("completed", 0)
        failures = counts.get("failed", 0)
        active = counts.get("proposed", 0) + counts.get("queued", 0) + counts.get("running", 0)
        reason = None
        status = campaign["status"]
        target = definition["stopping"].get("target")
        if status == "running":
            if self._target_met(definition["objective"]["goal"], campaign["best_objective"], target):
                status, reason = "completed", "target-objective-reached"
            elif failures >= definition["budget"]["maxFailures"]:
                status, reason = "failed", "failure-budget-exhausted"
            elif float(campaign["cumulative_cost"] or 0.0) >= float((definition.get("resourceModel") or {}).get("maxTotalCost", 1e15)) and active == 0:
                status, reason = "completed", "resource-budget-exhausted"
            elif total >= definition["budget"]["maxTrials"] and active == 0:
                status, reason = "completed", "trial-budget-exhausted"
            elif completed > 0 and campaign["no_improvement_count"] >= definition["stopping"]["patience"] and active == 0:
                status, reason = "completed", "no-improvement-patience"
        if status != campaign["status"]:
            completed_at = _now() if status in {"completed", "failed", "cancelled"} else None
            con.execute("UPDATE experiment_campaigns SET status=?,stop_reason=?,completed_at=?,updated_at=? WHERE id=?", (status, reason, completed_at, _now(), campaign_id))
            self._event(con, campaign_id, None, "campaign-stopped", {"status": status, "reason": reason})
        return self._campaign_row(con, campaign_id)

    def reconcile(self, campaign_id: str, auto_advance: bool = True) -> dict[str, Any]:
        with self._connect() as con:
            campaign = self._campaign_row(con, campaign_id)
            definition = self._loads(campaign["definition_json"])
            active = con.execute("SELECT * FROM experiment_trials WHERE campaign_id=? AND status IN ('queued','running') ORDER BY sequence_no", (campaign_id,)).fetchall()
        for trial_row in active:
            try:
                run = self.workflows.run(trial_row["workflow_run_id"], reconcile=True)["run"]
            except Exception as exc:
                with self._connect() as con:
                    self._event(con, campaign_id, trial_row["id"], "trial-reconcile-warning", {"error": _text(getattr(exc, "detail", str(exc)), 2000)})
                continue
            status = run["status"]
            if status in {"pending", "running"}:
                with self._connect() as con:
                    con.execute("UPDATE experiment_trials SET status='running',updated_at=? WHERE id=?", (_now(), trial_row["id"]))
                continue
            if status == "completed":
                try:
                    objective, objective_record = self._extract_objective(definition, run)
                    with self._connect() as con:
                        con.execute("BEGIN IMMEDIATE")
                        campaign = self._campaign_row(con, campaign_id)
                        better = self._is_better(definition["objective"]["goal"], objective, campaign["best_objective"], definition["stopping"]["minImprovement"])
                        observed_cost, resource_record = self._extract_resource_cost(definition, run, trial_row["estimated_cost"])
                        con.execute("UPDATE experiment_trials SET status='completed',objective_value=?,objective_json=?,result_json=?,observed_cost=?,resource_json=?,error_text=NULL,completed_at=?,updated_at=? WHERE id=?", (objective, _stable(objective_record), _stable(run), observed_cost, _stable(resource_record), _now(), _now(), trial_row["id"]))
                        if better:
                            con.execute("UPDATE experiment_campaigns SET best_trial_id=?,best_objective=?,no_improvement_count=0,cumulative_cost=cumulative_cost+?,updated_at=? WHERE id=?", (trial_row["id"], objective, observed_cost, _now(), campaign_id))
                        else:
                            con.execute("UPDATE experiment_campaigns SET no_improvement_count=no_improvement_count+1,cumulative_cost=cumulative_cost+?,updated_at=? WHERE id=?", (observed_cost, _now(), campaign_id))
                        self._event(con, campaign_id, trial_row["id"], "trial-completed", {"objective": objective_record, "resource": resource_record, "improvedBest": better, "workflowRunId": run["id"]})
                        self._refresh_campaign_state(con, campaign_id)
                        con.execute("COMMIT")
                except ExperimentCampaignError as exc:
                    with self._connect() as con:
                        con.execute("UPDATE experiment_trials SET status='failed',result_json=?,error_text=?,completed_at=?,updated_at=? WHERE id=?", (_stable(run), exc.detail, _now(), _now(), trial_row["id"]))
                        self._event(con, campaign_id, trial_row["id"], "trial-objective-failed", {"error": exc.detail, "workflowRunId": run["id"]})
            else:
                error = _text(run.get("error") or f"Workflow run ended with status {status}", 2000)
                with self._connect() as con:
                    con.execute("UPDATE experiment_trials SET status=?,result_json=?,error_text=?,completed_at=?,updated_at=? WHERE id=?", ("cancelled" if status == "cancelled" else "failed", _stable(run), error, _now(), _now(), trial_row["id"]))
                    self._event(con, campaign_id, trial_row["id"], "trial-failed", {"workflowStatus": status, "error": error, "workflowRunId": run["id"]})
                    self._refresh_campaign_state(con, campaign_id)
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            self._refresh_campaign_state(con, campaign_id)
            con.execute("COMMIT")
        if auto_advance:
            with self._connect() as con:
                campaign = self._campaign_row(con, campaign_id)
                definition = self._loads(campaign["definition_json"])
            if campaign["status"] == "running" and definition["run"]["autoAdvance"]:
                self.advance(campaign_id, reconcile_first=False)
        return self.get(campaign_id, reconcile=False)

    def advance(self, campaign_id: str, count: int | None = None, reconcile_first: bool = True) -> dict[str, Any]:
        if reconcile_first:
            self.reconcile(campaign_id, auto_advance=False)
        launched: list[dict[str, Any]] = []
        while True:
            with self._connect() as con:
                campaign = self._campaign_row(con, campaign_id)
                definition = self._loads(campaign["definition_json"])
                if campaign["status"] != "running":
                    break
                total = con.execute("SELECT COUNT(*) FROM experiment_trials WHERE campaign_id=?", (campaign_id,)).fetchone()[0]
                active = con.execute("SELECT COUNT(*) FROM experiment_trials WHERE campaign_id=? AND status IN ('proposed','queued','running')", (campaign_id,)).fetchone()[0]
                slots = min(definition["budget"]["maxConcurrentTrials"] - active, definition["budget"]["maxTrials"] - total)
                if count is not None:
                    slots = min(slots, max(0, int(count) - len(launched)))
            if slots <= 0:
                break
            launch_blocked = False
            for _ in range(slots):
                try:
                    launched.append(self._launch_one(campaign_id))
                except ExperimentCampaignError as exc:
                    detail_lower = exc.detail.lower()
                    if exc.status_code == 409 and (
                        "parameter space is exhausted" in detail_lower
                        or "no unique proposal" in detail_lower
                    ):
                        with self._connect() as con:
                            con.execute("UPDATE experiment_campaigns SET status='completed',stop_reason='parameter-space-exhausted',completed_at=?,updated_at=? WHERE id=?", (_now(), _now(), campaign_id))
                            self._event(con, campaign_id, None, "campaign-stopped", {"status": "completed", "reason": "parameter-space-exhausted"})
                        launch_blocked = True
                        break
                    if exc.status_code == 409 and "active reservations" in detail_lower:
                        launch_blocked = True
                        break
                    raise
            if launch_blocked:
                break
            if count is not None and len(launched) >= count:
                break
            if slots == 0:
                break
        result = self.get(campaign_id, reconcile=False)
        result["launched"] = launched
        result["launchedCount"] = len(launched)
        return result

    def start_campaign(self, campaign_id: str) -> dict[str, Any]:
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            campaign = self._campaign_row(con, campaign_id)
            if campaign["status"] in {"completed", "failed", "cancelled"}:
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("Terminal campaigns cannot be restarted. Create a new campaign ID.", 409)
            now = _now()
            con.execute("UPDATE experiment_campaigns SET status='running',started_at=COALESCE(started_at,?),stop_reason=NULL,completed_at=NULL,updated_at=? WHERE id=?", (now, now, campaign_id))
            self._event(con, campaign_id, None, "campaign-started", {"startedAt": now})
            con.execute("COMMIT")
        return self.advance(campaign_id, reconcile_first=False)

    def pause(self, campaign_id: str, reason: str = "operator pause") -> dict[str, Any]:
        with self._connect() as con:
            campaign = self._campaign_row(con, campaign_id)
            if campaign["status"] != "running":
                raise ExperimentCampaignError("Only running campaigns can be paused.", 409)
            con.execute("UPDATE experiment_campaigns SET status='paused',stop_reason=?,updated_at=? WHERE id=?", (_text(reason, 1000), _now(), campaign_id))
            self._event(con, campaign_id, None, "campaign-paused", {"reason": _text(reason, 1000)})
        return self.get(campaign_id)

    def resume(self, campaign_id: str) -> dict[str, Any]:
        with self._connect() as con:
            campaign = self._campaign_row(con, campaign_id)
            if campaign["status"] != "paused":
                raise ExperimentCampaignError("Only paused campaigns can be resumed.", 409)
            con.execute("UPDATE experiment_campaigns SET status='running',stop_reason=NULL,updated_at=? WHERE id=?", (_now(), campaign_id))
            self._event(con, campaign_id, None, "campaign-resumed", {})
        return self.advance(campaign_id, reconcile_first=True)

    def cancel(self, campaign_id: str, reason: str = "operator cancellation") -> dict[str, Any]:
        with self._connect() as con:
            campaign = self._campaign_row(con, campaign_id)
            active = con.execute("SELECT * FROM experiment_trials WHERE campaign_id=? AND status IN ('proposed','queued','running')", (campaign_id,)).fetchall()
        for trial_row in active:
            if trial_row["workflow_run_id"]:
                try:
                    self.workflows.cancel(trial_row["workflow_run_id"], {"reason": reason})
                except Exception:
                    pass
        with self._connect() as con:
            now = _now()
            con.execute("UPDATE experiment_trials SET status='cancelled',error_text=?,completed_at=?,updated_at=? WHERE campaign_id=? AND status IN ('proposed','queued','running')", (_text(reason, 1000), now, now, campaign_id))
            con.execute("UPDATE experiment_campaigns SET status='cancelled',stop_reason=?,completed_at=?,updated_at=? WHERE id=?", (_text(reason, 1000), now, now, campaign_id))
            self._event(con, campaign_id, None, "campaign-cancelled", {"reason": _text(reason, 1000), "cancelledTrials": len(active)})
        return self.get(campaign_id)

    def observe(self, campaign_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        parameters = payload.get("parameters") if isinstance(payload.get("parameters"), dict) else None
        if not parameters:
            raise ExperimentCampaignError("Manual observations require parameters.")
        try:
            objective = float(payload.get("objectiveValue"))
        except (TypeError, ValueError) as exc:
            raise ExperimentCampaignError("Manual observations require a numeric objectiveValue.") from exc
        if not math.isfinite(objective):
            raise ExperimentCampaignError("objectiveValue must be finite.")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            campaign = self._campaign_row(con, campaign_id)
            definition = self._loads(campaign["definition_json"])
            normalized_parameters: dict[str, Any] = {}
            for name, spec in definition["parameterSpace"].items():
                if name not in parameters:
                    con.execute("ROLLBACK")
                    raise ExperimentCampaignError(f"Manual observation is missing parameter: {name}")
                value = parameters[name]
                if spec["type"] == "categorical" and value not in spec["values"]:
                    con.execute("ROLLBACK"); raise ExperimentCampaignError(f"Invalid categorical value for {name}.")
                if spec["type"] == "integer": value = int(value)
                if spec["type"] == "continuous": value = float(value)
                normalized_parameters[name] = value
            sequence = int(con.execute("SELECT COALESCE(MAX(sequence_no),0)+1 FROM experiment_trials WHERE campaign_id=?", (campaign_id,)).fetchone()[0])
            trial_id = _text(payload.get("id"), 180) or f"trial-{campaign_id}-{sequence:06d}"
            now = _now()
            estimated_cost = estimate_cost(definition.get("resourceModel") or normalize_resource_model({}, definition["parameterSpace"]), definition["parameterSpace"], normalized_parameters)
            try:
                observed_cost = float(payload.get("costValue")) if payload.get("costValue") is not None else estimated_cost
            except (TypeError, ValueError) as exc:
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("Manual observation costValue must be numeric.") from exc
            if not math.isfinite(observed_cost) or observed_cost < 0:
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("Manual observation costValue must be finite and non-negative.")
            proposal = {"strategy": "manual-observation", "source": _text(payload.get("source"), 300) or "operator", "observedAt": now, "estimatedCost": estimated_cost}
            objective_record = {"path": "manual", "goal": definition["objective"]["goal"], "value": objective, "extractedAt": now}
            resource_record = {"value": observed_cost, "source": "manual-observation", "estimatedCost": estimated_cost, "recordedAt": now}
            try:
                con.execute("INSERT INTO experiment_trials(id,campaign_id,sequence_no,status,parameters_hash,parameters_json,proposal_json,objective_value,objective_json,result_json,estimated_cost,observed_cost,resource_json,created_at,started_at,completed_at,updated_at) VALUES(?,?,?, 'completed',?,?,?,?,?,?,?,?,?,?,?,?,?)", (trial_id, campaign_id, sequence, _hash(normalized_parameters), _stable(normalized_parameters), _stable(proposal), objective, _stable(objective_record), _stable(payload.get("result") if isinstance(payload.get("result"), dict) else {}), estimated_cost, observed_cost, _stable(resource_record), now, now, now, now))
            except sqlite3.IntegrityError as exc:
                con.execute("ROLLBACK")
                raise ExperimentCampaignError("That parameter set or trial ID already exists.", 409) from exc
            better = self._is_better(definition["objective"]["goal"], objective, campaign["best_objective"], definition["stopping"]["minImprovement"])
            if better:
                con.execute("UPDATE experiment_campaigns SET best_trial_id=?,best_objective=?,no_improvement_count=0,cumulative_cost=cumulative_cost+?,updated_at=? WHERE id=?", (trial_id, objective, observed_cost, now, campaign_id))
            else:
                con.execute("UPDATE experiment_campaigns SET no_improvement_count=no_improvement_count+1,cumulative_cost=cumulative_cost+?,updated_at=? WHERE id=?", (observed_cost, now, campaign_id))
            self._event(con, campaign_id, trial_id, "manual-observation-recorded", {"objective": objective_record, "resource": resource_record, "improvedBest": better})
            self._refresh_campaign_state(con, campaign_id)
            con.execute("COMMIT")
        return {"ok": True, "trial": self.trial(trial_id)["trial"], "campaign": self.get(campaign_id)["campaign"]}

    def trial(self, trial_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = con.execute("SELECT * FROM experiment_trials WHERE id=?", (_text(trial_id, 180),)).fetchone()
            if not row:
                raise ExperimentCampaignError("Experiment trial was not found.", 404)
            return {"ok": True, "trial": self._trial_item(row)}

    def trials(self, campaign_id: str, status: str = "", limit: int = 500) -> dict[str, Any]:
        if status and status not in TRIAL_STATES:
            raise ExperimentCampaignError("Unsupported trial status.")
        clauses = ["campaign_id=?"]
        params: list[Any] = [_text(campaign_id, 180)]
        if status:
            clauses.append("status=?"); params.append(status)
        params.append(max(1, min(5000, int(limit))))
        with self._connect() as con:
            self._campaign_row(con, campaign_id)
            rows = con.execute(f"SELECT * FROM experiment_trials WHERE {' AND '.join(clauses)} ORDER BY sequence_no LIMIT ?", params).fetchall()
        return {"ok": True, "count": len(rows), "trials": [self._trial_item(row) for row in rows]}

    def timeline(self, campaign_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            self._campaign_row(con, campaign_id)
            rows = con.execute("SELECT * FROM experiment_campaign_events WHERE campaign_id=? ORDER BY id DESC LIMIT ?", (_text(campaign_id, 180), max(1, min(5000, int(limit))))).fetchall()
        events = [{"schema": EVENT_SCHEMA, "id": row["id"], "campaignId": row["campaign_id"], "trialId": row["trial_id"], "type": row["event_type"], "payload": self._loads(row["payload_json"]), "createdAt": row["created_at"]} for row in reversed(rows)]
        return {"ok": True, "count": len(events), "events": events}

    def tick(self) -> dict[str, Any]:
        with self._connect() as con:
            ids = [row["id"] for row in con.execute("SELECT id FROM experiment_campaigns WHERE status='running' ORDER BY updated_at LIMIT 500")]
        results = []
        for campaign_id in ids:
            try:
                result = self.reconcile(campaign_id, auto_advance=True)
                results.append({"campaignId": campaign_id, "status": result["campaign"]["status"], "ok": True})
            except Exception as exc:
                results.append({"campaignId": campaign_id, "ok": False, "error": _text(getattr(exc, "detail", str(exc)), 2000)})
        return {"ok": all(item["ok"] for item in results), "checkedAt": _now(), "campaignCount": len(ids), "campaigns": results}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            campaign_counts = {row["status"]: int(row["count"]) for row in con.execute("SELECT status,COUNT(*) count FROM experiment_campaigns GROUP BY status")}
            trial_counts = {row["status"]: int(row["count"]) for row in con.execute("SELECT status,COUNT(*) count FROM experiment_trials GROUP BY status")}
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema_version = con.execute("SELECT value FROM experiment_campaign_meta WHERE key='schema_version'").fetchone()[0]
            surrogate_count = int(con.execute("SELECT COUNT(*) FROM experiment_campaigns WHERE model_json IS NOT NULL").fetchone()[0])
            total_cost = float(con.execute("SELECT COALESCE(SUM(cumulative_cost),0) FROM experiment_campaigns").fetchone()[0])
        return {
            "ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION,
            "schemaVersion": int(schema_version), "storage": "sqlite-wal", "databasePath": self.db_path,
            "campaignCounts": campaign_counts, "trialCounts": trial_counts,
            "surrogateCount": surrogate_count, "cumulativeObservedCost": total_cost,
            "gaussianProcessSurrogate": True, "predictiveUncertainty": True,
            "activeLearning": True, "resourceAwareSearch": True,
            "campaignThreadActive": bool(self._thread and self._thread.is_alive()), "pollSeconds": self.poll_seconds,
            "databaseIntegrity": integrity,
        }
