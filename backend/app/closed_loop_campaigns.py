from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import copy
import hmac
import json
import math
from pathlib import Path
import re
import secrets
import sqlite3
import threading
from typing import Any

VERSION = "0.33.2"
LOOP_SCHEMA = "sc-lab-closed-loop-campaign/0.33.2"
MEASUREMENT_SCHEMA = "sc-lab-closed-loop-measurement/0.33.2"
COMMAND_SCHEMA = "sc-lab-closed-loop-command/0.33.2"
EVENT_SCHEMA = "sc-lab-closed-loop-event/0.33.2"
DB_SCHEMA_VERSION = 1
LOOP_STATES = {"draft", "running", "paused", "completed", "failed", "cancelled", "emergency-stopped"}
COMMAND_STATES = {"pending-approval", "ready", "dispatched", "acknowledged", "rejected", "cancelled"}
MODES = {"simulation", "instrument", "hybrid"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")


class ClosedLoopError(ValueError):
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


def _deep_get(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    for part in [item for item in str(path).split(".") if item]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, copy.deepcopy(current)


def _normalize_limits(raw: Any, label: str) -> dict[str, dict[str, float]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ClosedLoopError(f"{label} must be an object.")
    result: dict[str, dict[str, float]] = {}
    for name, spec in raw.items():
        key = _text(name, 180)
        if not ID_RE.match(key) or not isinstance(spec, dict):
            raise ClosedLoopError(f"Invalid {label} entry: {name}")
        minimum = _float(spec.get("min"), -1e300, -1e300, 1e300)
        maximum = _float(spec.get("max"), 1e300, -1e300, 1e300)
        if maximum < minimum:
            raise ClosedLoopError(f"{label}.{key} requires max greater than or equal to min.")
        item = {"min": minimum, "max": maximum}
        if spec.get("maxStepDelta") is not None:
            item["maxStepDelta"] = _float(spec.get("maxStepDelta"), 0.0, 0.0, 1e300)
        result[key] = item
    return result


def normalize_loop(payload: dict[str, Any], max_cycles_limit: int = 100000) -> dict[str, Any]:
    source = payload.get("loop") if isinstance(payload.get("loop"), dict) else payload
    loop_id = _text(source.get("id"), 180) or f"closed-loop-{secrets.token_hex(8)}"
    campaign_id = _text(source.get("campaignId"), 180)
    if not ID_RE.match(loop_id):
        raise ClosedLoopError("Loop ID contains unsupported characters.")
    if not campaign_id or not ID_RE.match(campaign_id):
        raise ClosedLoopError("A valid campaignId is required.")
    mode = _text(source.get("mode"), 40) or "simulation"
    if mode not in MODES:
        raise ClosedLoopError("mode must be simulation, instrument, or hybrid.")

    adapter_raw = source.get("adapter") if isinstance(source.get("adapter"), dict) else {}
    gateway_id = _text(adapter_raw.get("gatewayId"), 180)
    if mode in {"instrument", "hybrid"} and (not gateway_id or not ID_RE.match(gateway_id)):
        raise ClosedLoopError("Instrument and hybrid loops require adapter.gatewayId.")
    protocol = _text(adapter_raw.get("protocol"), 80) or "signed-envelope-v1"
    if protocol not in {"signed-envelope-v1", "manual-envelope-v1", "simulation-workflow-v1"}:
        raise ClosedLoopError("Unsupported adapter protocol.")
    adapter = {
        "type": "simulation-workflow" if mode == "simulation" else "instrument-gateway",
        "gatewayId": gateway_id or None,
        "protocol": protocol,
        "capabilities": sorted({_text(item, 120) for item in (adapter_raw.get("capabilities") or []) if _text(item, 120)}),
        "directNetworkCallbacks": False,
    }

    safety_raw = source.get("safety") if isinstance(source.get("safety"), dict) else {}
    emergency = [_text(item, 180) for item in (safety_raw.get("emergencyStopSignals") or [])]
    emergency = sorted({item for item in emergency if ID_RE.match(item)})
    safety = {
        "signalLimits": _normalize_limits(safety_raw.get("signalLimits"), "signalLimits"),
        "parameterLimits": _normalize_limits(safety_raw.get("parameterLimits"), "parameterLimits"),
        "emergencyStopSignals": emergency,
        "requireCommandApproval": safety_raw.get("requireCommandApproval", mode != "simulation") is not False,
        "maxConsecutiveFailures": _int(safety_raw.get("maxConsecutiveFailures"), 3, 1, 100),
        "staleMeasurementSeconds": _int(safety_raw.get("staleMeasurementSeconds"), 300, 1, 86400),
        "rejectOutOfRange": safety_raw.get("rejectOutOfRange", True) is not False,
    }

    observation_raw = source.get("observation") if isinstance(source.get("observation"), dict) else {}
    objective_path = _text(observation_raw.get("objectivePath"), 500) or "objectiveValue"
    if not re.match(r"^[A-Za-z0-9_.-]+$", objective_path):
        raise ClosedLoopError("observation.objectivePath contains unsupported characters.")
    observation = {
        "objectivePath": objective_path,
        "parameterPath": _text(observation_raw.get("parameterPath"), 500) or "parameters",
        "signalsPath": _text(observation_raw.get("signalsPath"), 500) or "signals",
        "requireSignature": observation_raw.get("requireSignature", False) is True,
    }

    control_raw = source.get("control") if isinstance(source.get("control"), dict) else {}
    control = {
        "autoAdvance": control_raw.get("autoAdvance", True) is not False,
        "maxCycles": _int(control_raw.get("maxCycles"), 25, 1, max_cycles_limit),
        "settlingSeconds": _int(control_raw.get("settlingSeconds"), 0, 0, 86400),
        "stopOnCampaignCompletion": control_raw.get("stopOnCampaignCompletion", True) is not False,
    }
    record = {
        "schema": LOOP_SCHEMA,
        "version": VERSION,
        "id": loop_id,
        "title": _text(source.get("title"), 300) or loop_id,
        "projectId": _text(source.get("projectId"), 180) or "default",
        "campaignId": campaign_id,
        "mode": mode,
        "adapter": adapter,
        "safety": safety,
        "observation": observation,
        "control": control,
        "metadata": copy.deepcopy(source.get("metadata")) if isinstance(source.get("metadata"), dict) else {},
    }
    record["definitionHash"] = _hash(record)
    return record


def policies(max_loops: int = 1000, max_cycles: int = 100000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "closed-loop-simulation-instrument-campaigns",
        "modes": sorted(MODES),
        "adapterProtocols": ["simulation-workflow-v1", "signed-envelope-v1", "manual-envelope-v1"],
        "measurementIntegrity": {"canonicalSha256": True, "optionalHmacSha256": True, "deduplication": True},
        "safety": {"signalLimits": True, "parameterLimits": True, "maxStepDelta": True, "emergencyStop": True, "operatorApproval": True, "directDeviceExecution": False},
        "limits": {"maxLoops": max_loops, "maxCycles": max_cycles},
    }


def sign_measurement(secret: str, payload: dict[str, Any]) -> str:
    if not secret:
        raise ClosedLoopError("A measurement signing secret is not configured.", 503)
    body = copy.deepcopy(payload)
    body.pop("signature", None)
    return hmac.new(secret.encode("utf-8"), _stable(body).encode("utf-8"), sha256).hexdigest()


def verify_measurement_signature(secret: str, payload: dict[str, Any]) -> bool:
    supplied = _text(payload.get("signature"), 256)
    if not secret or not supplied:
        return False
    try:
        expected = sign_measurement(secret, payload)
    except ClosedLoopError:
        return False
    return hmac.compare_digest(supplied, expected)


class ClosedLoopCampaignManager:
    def __init__(self, db_path: str, campaigns: Any, poll_seconds: float = 30.0, max_loops: int = 1000, max_cycles: int = 100000, history_limit: int = 30000, measurement_secret: str = ""):
        self.db_path = str(db_path)
        self.campaigns = campaigns
        self.poll_seconds = max(1.0, min(3600.0, float(poll_seconds)))
        self.max_loops = max(1, int(max_loops))
        self.max_cycles = max(1, int(max_cycles))
        self.history_limit = max(100, int(history_limit))
        self.measurement_secret = str(measurement_secret or "")
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
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS loops (
              id TEXT PRIMARY KEY, definition_json TEXT NOT NULL, definition_hash TEXT NOT NULL,
              title TEXT NOT NULL, project_id TEXT NOT NULL, campaign_id TEXT NOT NULL, mode TEXT NOT NULL,
              status TEXT NOT NULL, cycle_count INTEGER NOT NULL DEFAULT 0, failure_count INTEGER NOT NULL DEFAULT 0,
              last_measurement_at TEXT, last_command_id TEXT, stop_reason TEXT,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cycles (
              id TEXT PRIMARY KEY, loop_id TEXT NOT NULL, sequence INTEGER NOT NULL, source TEXT NOT NULL,
              campaign_trial_id TEXT, workflow_run_id TEXT, command_id TEXT, measurement_id TEXT,
              parameters_json TEXT, signals_json TEXT, objective_value REAL, safety_json TEXT NOT NULL,
              status TEXT NOT NULL, started_at TEXT NOT NULL, completed_at TEXT,
              UNIQUE(loop_id, sequence), FOREIGN KEY(loop_id) REFERENCES loops(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS commands (
              id TEXT PRIMARY KEY, loop_id TEXT NOT NULL, sequence INTEGER NOT NULL, parameters_json TEXT NOT NULL,
              parameters_hash TEXT NOT NULL, status TEXT NOT NULL, safety_json TEXT NOT NULL,
              source_trial_id TEXT, issued_at TEXT NOT NULL, approved_at TEXT, dispatched_at TEXT,
              acknowledged_at TEXT, operator TEXT, reason TEXT, FOREIGN KEY(loop_id) REFERENCES loops(id) ON DELETE CASCADE
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_commands_loop_hash_active ON commands(loop_id, parameters_hash, sequence);
            CREATE TABLE IF NOT EXISTS measurements (
              id TEXT PRIMARY KEY, loop_id TEXT NOT NULL, command_id TEXT, gateway_id TEXT, sequence INTEGER NOT NULL,
              payload_hash TEXT NOT NULL UNIQUE, payload_json TEXT NOT NULL, parameters_json TEXT NOT NULL,
              signals_json TEXT NOT NULL, objective_value REAL NOT NULL, signature_valid INTEGER NOT NULL,
              safety_json TEXT NOT NULL, received_at TEXT NOT NULL, FOREIGN KEY(loop_id) REFERENCES loops(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS events (
              sequence INTEGER PRIMARY KEY AUTOINCREMENT, loop_id TEXT NOT NULL, entity_id TEXT,
              event_type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_events_loop_sequence ON events(loop_id, sequence DESC);
            """)
            con.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('schema_version',?)", (str(DB_SCHEMA_VERSION),))

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="sc-lab-closed-loop", daemon=True)
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

    @staticmethod
    def _loads(value: str | None) -> Any:
        return json.loads(value) if value else None

    def _event(self, con: sqlite3.Connection, loop_id: str, entity_id: str | None, event_type: str, payload: dict[str, Any]) -> None:
        con.execute("INSERT INTO events(loop_id,entity_id,event_type,payload_json,created_at) VALUES(?,?,?,?,?)", (loop_id, entity_id, event_type, _stable(payload), _now()))
        count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        excess = count - self.history_limit
        if excess > 0:
            con.execute("DELETE FROM events WHERE sequence IN (SELECT sequence FROM events ORDER BY sequence ASC LIMIT ?)", (excess,))

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        definition = normalize_loop(payload, self.max_cycles)
        try:
            campaign = self.campaigns.get(definition["campaignId"])
        except Exception as exc:
            raise ClosedLoopError(f"Referenced campaign is unavailable: {definition['campaignId']}", 404) from exc
        return {"ok": True, "version": VERSION, "loop": definition, "campaign": campaign.get("campaign", campaign)}

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self.validate(payload)
        definition = validated["loop"]
        now = _now()
        with self._connect() as con:
            total = con.execute("SELECT COUNT(*) FROM loops").fetchone()[0]
            existing = con.execute("SELECT id,status FROM loops WHERE id=?", (definition["id"],)).fetchone()
            if not existing and total >= self.max_loops:
                raise ClosedLoopError("Closed-loop campaign capacity has been reached.", 409)
            if existing and existing["status"] in {"running", "emergency-stopped"}:
                raise ClosedLoopError("A running or emergency-stopped loop cannot be overwritten.", 409)
            created = now if not existing else con.execute("SELECT created_at FROM loops WHERE id=?", (definition["id"],)).fetchone()[0]
            con.execute("""INSERT OR REPLACE INTO loops(id,definition_json,definition_hash,title,project_id,campaign_id,mode,status,cycle_count,failure_count,last_measurement_at,last_command_id,stop_reason,created_at,updated_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (definition["id"], _stable(definition), definition["definitionHash"], definition["title"], definition["projectId"], definition["campaignId"], definition["mode"], "draft", 0, 0, None, None, None, created, now))
            self._event(con, definition["id"], definition["id"], "loop-saved", {"definitionHash": definition["definitionHash"], "mode": definition["mode"]})
        return self.get(definition["id"])

    def _loop_row(self, con: sqlite3.Connection, loop_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM loops WHERE id=?", (loop_id,)).fetchone()
        if not row:
            raise ClosedLoopError(f"Closed-loop campaign not found: {loop_id}", 404)
        return row

    def _command_item(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": COMMAND_SCHEMA, "version": VERSION, "id": row["id"], "loopId": row["loop_id"], "sequence": row["sequence"],
            "parameters": self._loads(row["parameters_json"]), "parametersHash": row["parameters_hash"], "status": row["status"],
            "safety": self._loads(row["safety_json"]), "sourceTrialId": row["source_trial_id"], "issuedAt": row["issued_at"],
            "approvedAt": row["approved_at"], "dispatchedAt": row["dispatched_at"], "acknowledgedAt": row["acknowledged_at"],
            "operator": row["operator"], "reason": row["reason"],
        }

    def _measurement_item(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": MEASUREMENT_SCHEMA, "version": VERSION, "id": row["id"], "loopId": row["loop_id"], "commandId": row["command_id"],
            "gatewayId": row["gateway_id"], "sequence": row["sequence"], "payloadHash": row["payload_hash"],
            "payload": self._loads(row["payload_json"]), "parameters": self._loads(row["parameters_json"]), "signals": self._loads(row["signals_json"]),
            "objectiveValue": row["objective_value"], "signatureValid": bool(row["signature_valid"]), "safety": self._loads(row["safety_json"]), "receivedAt": row["received_at"],
        }

    def _cycle_item(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"], "loopId": row["loop_id"], "sequence": row["sequence"], "source": row["source"],
            "campaignTrialId": row["campaign_trial_id"], "workflowRunId": row["workflow_run_id"], "commandId": row["command_id"], "measurementId": row["measurement_id"],
            "parameters": self._loads(row["parameters_json"]), "signals": self._loads(row["signals_json"]), "objectiveValue": row["objective_value"],
            "safety": self._loads(row["safety_json"]), "status": row["status"], "startedAt": row["started_at"], "completedAt": row["completed_at"],
        }

    def _item(self, con: sqlite3.Connection, row: sqlite3.Row, include_records: bool = True) -> dict[str, Any]:
        definition = self._loads(row["definition_json"])
        item = {
            "schema": LOOP_SCHEMA, "version": VERSION, "id": row["id"], "title": row["title"], "projectId": row["project_id"],
            "campaignId": row["campaign_id"], "mode": row["mode"], "status": row["status"], "cycleCount": row["cycle_count"],
            "failureCount": row["failure_count"], "lastMeasurementAt": row["last_measurement_at"], "lastCommandId": row["last_command_id"],
            "stopReason": row["stop_reason"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "definition": definition,
        }
        if include_records:
            item["commands"] = [self._command_item(r) for r in con.execute("SELECT * FROM commands WHERE loop_id=? ORDER BY sequence DESC LIMIT 100", (row["id"],)).fetchall()]
            item["measurements"] = [self._measurement_item(r) for r in con.execute("SELECT * FROM measurements WHERE loop_id=? ORDER BY sequence DESC LIMIT 100", (row["id"],)).fetchall()]
            item["cycles"] = [self._cycle_item(r) for r in con.execute("SELECT * FROM cycles WHERE loop_id=? ORDER BY sequence DESC LIMIT 100", (row["id"],)).fetchall()]
        return item

    def get(self, loop_id: str, reconcile: bool = False) -> dict[str, Any]:
        if reconcile:
            return self.reconcile(loop_id)
        with self._connect() as con:
            return {"ok": True, "loop": self._item(con, self._loop_row(con, loop_id))}

    def list(self, project_id: str = "", status: str = "", limit: int = 100) -> dict[str, Any]:
        clauses, values = [], []
        if project_id:
            clauses.append("project_id=?"); values.append(project_id)
        if status:
            clauses.append("status=?"); values.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM loops{where} ORDER BY updated_at DESC LIMIT ?", (*values, max(1, min(1000, int(limit))))).fetchall()
            return {"ok": True, "count": len(rows), "loops": [self._item(con, row, False) for row in rows]}

    @staticmethod
    def _limits_check(values: dict[str, Any], limits: dict[str, dict[str, float]], previous: dict[str, Any] | None = None) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        for name, spec in limits.items():
            if name not in values:
                continue
            try:
                number = float(values[name])
            except (TypeError, ValueError):
                violations.append({"field": name, "reason": "non-numeric", "value": values[name]})
                continue
            if not math.isfinite(number) or number < spec["min"] or number > spec["max"]:
                violations.append({"field": name, "reason": "out-of-range", "value": number, "min": spec["min"], "max": spec["max"]})
            if previous and name in previous and "maxStepDelta" in spec:
                try:
                    delta = abs(number - float(previous[name]))
                except (TypeError, ValueError):
                    delta = math.inf
                if delta > spec["maxStepDelta"]:
                    violations.append({"field": name, "reason": "step-delta", "delta": delta, "maxStepDelta": spec["maxStepDelta"]})
        return {"ok": not violations, "violations": violations}

    def _previous_parameters(self, con: sqlite3.Connection, loop_id: str) -> dict[str, Any] | None:
        row = con.execute("SELECT parameters_json FROM commands WHERE loop_id=? AND status IN ('ready','dispatched','acknowledged') ORDER BY sequence DESC LIMIT 1", (loop_id,)).fetchone()
        return self._loads(row[0]) if row else None

    def _issue_command(self, con: sqlite3.Connection, loop_row: sqlite3.Row, parameters: dict[str, Any], source_trial_id: str | None = None) -> dict[str, Any]:
        definition = self._loads(loop_row["definition_json"])
        safety = self._limits_check(parameters, definition["safety"]["parameterLimits"], self._previous_parameters(con, loop_row["id"]))
        if not safety["ok"] and definition["safety"]["rejectOutOfRange"]:
            self._event(con, loop_row["id"], None, "command-rejected-by-interlock", safety)
            raise ClosedLoopError("Proposed setpoint violates a closed-loop safety interlock.", 409)
        sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM commands WHERE loop_id=?", (loop_row["id"],)).fetchone()[0]
        command_id = f"command-{loop_row['id']}-{sequence}-{secrets.token_hex(4)}"
        status = "pending-approval" if definition["safety"]["requireCommandApproval"] else "ready"
        now = _now()
        con.execute("INSERT INTO commands(id,loop_id,sequence,parameters_json,parameters_hash,status,safety_json,source_trial_id,issued_at) VALUES(?,?,?,?,?,?,?,?,?)", (command_id, loop_row["id"], sequence, _stable(parameters), _hash(parameters), status, _stable(safety), source_trial_id, now))
        con.execute("UPDATE loops SET last_command_id=?,updated_at=? WHERE id=?", (command_id, now, loop_row["id"]))
        self._event(con, loop_row["id"], command_id, "command-issued", {"status": status, "parametersHash": _hash(parameters), "safety": safety})
        return self._command_item(con.execute("SELECT * FROM commands WHERE id=?", (command_id,)).fetchone())

    def preview_command(self, loop_id: str) -> dict[str, Any]:
        with self._connect() as con:
            loop_row = self._loop_row(con, loop_id)
            definition = self._loads(loop_row["definition_json"])
            if definition["mode"] == "simulation":
                raise ClosedLoopError("Simulation-only loops launch workflow trials rather than instrument commands.", 409)
            preview = self.campaigns.preview_proposal(definition["campaignId"])
            parameters = preview.get("parameters") or preview.get("proposal", {}).get("parameters")
            if not isinstance(parameters, dict):
                raise ClosedLoopError("The campaign did not provide a commandable parameter proposal.", 409)
            safety = self._limits_check(parameters, definition["safety"]["parameterLimits"], self._previous_parameters(con, loop_id))
            return {"ok": True, "version": VERSION, "parameters": parameters, "proposal": preview, "safety": safety}

    def issue_next_command(self, loop_id: str) -> dict[str, Any]:
        preview = self.preview_command(loop_id)
        with self._connect() as con:
            row = self._loop_row(con, loop_id)
            if row["status"] != "running":
                raise ClosedLoopError("Commands can be issued only while the loop is running.", 409)
            active = con.execute("SELECT * FROM commands WHERE loop_id=? AND status IN ('pending-approval','ready','dispatched') ORDER BY sequence DESC LIMIT 1", (loop_id,)).fetchone()
            if active:
                return {"ok": True, "created": False, "command": self._command_item(active)}
            command = self._issue_command(con, row, preview["parameters"])
            return {"ok": True, "created": True, "command": command, "proposal": preview["proposal"]}

    def start_loop(self, loop_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = self._loop_row(con, loop_id)
            if row["status"] not in {"draft", "paused"}:
                raise ClosedLoopError("Only draft or paused loops can be started.", 409)
            con.execute("UPDATE loops SET status='running',stop_reason=NULL,updated_at=? WHERE id=?", (_now(), loop_id))
            self._event(con, loop_id, loop_id, "loop-started", {"mode": row["mode"]})
            definition = self._loads(row["definition_json"])
        launched = None
        command = None
        if definition["mode"] in {"simulation", "hybrid"}:
            try:
                launched = self.campaigns.start_campaign(definition["campaignId"])
            except Exception:
                launched = self.campaigns.advance(definition["campaignId"], count=1, reconcile_first=True)
        if definition["mode"] == "instrument":
            command = self.issue_next_command(loop_id)
        return {**self.get(loop_id), "campaign": launched, "command": command}

    def pause(self, loop_id: str, reason: str = "operator pause") -> dict[str, Any]:
        with self._connect() as con:
            row = self._loop_row(con, loop_id)
            if row["status"] != "running":
                raise ClosedLoopError("Only running loops can be paused.", 409)
            con.execute("UPDATE loops SET status='paused',stop_reason=?,updated_at=? WHERE id=?", (_text(reason, 1000), _now(), loop_id))
            self._event(con, loop_id, loop_id, "loop-paused", {"reason": reason})
        return self.get(loop_id)

    def resume(self, loop_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = self._loop_row(con, loop_id)
            if row["status"] != "paused":
                raise ClosedLoopError("Only paused loops can be resumed.", 409)
            con.execute("UPDATE loops SET status='running',stop_reason=NULL,updated_at=? WHERE id=?", (_now(), loop_id))
            self._event(con, loop_id, loop_id, "loop-resumed", {})
        return self.reconcile(loop_id)

    def cancel(self, loop_id: str, reason: str = "operator cancellation") -> dict[str, Any]:
        with self._connect() as con:
            self._loop_row(con, loop_id)
            now = _now()
            con.execute("UPDATE loops SET status='cancelled',stop_reason=?,updated_at=? WHERE id=?", (_text(reason, 1000), now, loop_id))
            con.execute("UPDATE commands SET status='cancelled',reason=? WHERE loop_id=? AND status IN ('pending-approval','ready','dispatched')", (_text(reason, 1000), loop_id))
            self._event(con, loop_id, loop_id, "loop-cancelled", {"reason": reason})
        return self.get(loop_id)

    def emergency_stop(self, loop_id: str, reason: str = "safety interlock") -> dict[str, Any]:
        with self._connect() as con:
            self._loop_row(con, loop_id)
            now = _now()
            con.execute("UPDATE loops SET status='emergency-stopped',stop_reason=?,updated_at=? WHERE id=?", (_text(reason, 1000), now, loop_id))
            con.execute("UPDATE commands SET status='rejected',reason=? WHERE loop_id=? AND status IN ('pending-approval','ready','dispatched')", (_text(reason, 1000), loop_id))
            self._event(con, loop_id, loop_id, "emergency-stop", {"reason": reason})
        return self.get(loop_id)

    def approve_command(self, loop_id: str, command_id: str, operator: str = "operator", reason: str = "approved") -> dict[str, Any]:
        with self._connect() as con:
            self._loop_row(con, loop_id)
            row = con.execute("SELECT * FROM commands WHERE id=? AND loop_id=?", (command_id, loop_id)).fetchone()
            if not row:
                raise ClosedLoopError("Command not found.", 404)
            if row["status"] != "pending-approval":
                raise ClosedLoopError("Only pending commands can be approved.", 409)
            con.execute("UPDATE commands SET status='ready',approved_at=?,operator=?,reason=? WHERE id=?", (_now(), _text(operator, 180), _text(reason, 1000), command_id))
            self._event(con, loop_id, command_id, "command-approved", {"operator": operator, "reason": reason})
            return {"ok": True, "command": self._command_item(con.execute("SELECT * FROM commands WHERE id=?", (command_id,)).fetchone())}

    def dispatch_command(self, loop_id: str, command_id: str) -> dict[str, Any]:
        with self._connect() as con:
            loop_row = self._loop_row(con, loop_id)
            definition = self._loads(loop_row["definition_json"])
            row = con.execute("SELECT * FROM commands WHERE id=? AND loop_id=?", (command_id, loop_id)).fetchone()
            if not row:
                raise ClosedLoopError("Command not found.", 404)
            if row["status"] != "ready":
                raise ClosedLoopError("Only ready commands can be dispatched.", 409)
            now = _now()
            con.execute("UPDATE commands SET status='dispatched',dispatched_at=? WHERE id=?", (now, command_id))
            envelope = {"schema": COMMAND_SCHEMA, "version": VERSION, "commandId": command_id, "loopId": loop_id, "gatewayId": definition["adapter"]["gatewayId"], "sequence": row["sequence"], "parameters": self._loads(row["parameters_json"]), "issuedAt": row["issued_at"], "dispatchedAt": now}
            envelope["envelopeHash"] = _hash(envelope)
            self._event(con, loop_id, command_id, "command-dispatched", {"envelopeHash": envelope["envelopeHash"]})
            return {"ok": True, "command": self._command_item(con.execute("SELECT * FROM commands WHERE id=?", (command_id,)).fetchone()), "envelope": envelope}

    def _normalize_measurement(self, definition: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        gateway = _text(payload.get("gatewayId"), 180)
        expected_gateway = definition["adapter"].get("gatewayId")
        if expected_gateway and gateway != expected_gateway:
            raise ClosedLoopError("Measurement gateway does not match the configured adapter.", 403)
        signature_valid = verify_measurement_signature(self.measurement_secret, payload)
        if definition["observation"]["requireSignature"] and not signature_valid:
            raise ClosedLoopError("A valid measurement HMAC signature is required.", 401)
        ok_params, parameters = _deep_get(payload, definition["observation"]["parameterPath"])
        ok_signals, signals = _deep_get(payload, definition["observation"]["signalsPath"])
        ok_obj, objective = _deep_get(payload, definition["observation"]["objectivePath"])
        if not ok_params or not isinstance(parameters, dict):
            raise ClosedLoopError("Measurement parameters are missing or invalid.")
        if not ok_signals or not isinstance(signals, dict):
            raise ClosedLoopError("Measurement signals are missing or invalid.")
        if not ok_obj:
            raise ClosedLoopError("Measurement objective value is missing.")
        try:
            objective_value = float(objective)
        except (TypeError, ValueError) as exc:
            raise ClosedLoopError("Measurement objective value must be numeric.") from exc
        if not math.isfinite(objective_value):
            raise ClosedLoopError("Measurement objective value must be finite.")
        clean = copy.deepcopy(payload)
        clean.pop("signature", None)
        return {"gatewayId": gateway, "parameters": parameters, "signals": signals, "objectiveValue": objective_value, "signatureValid": signature_valid, "payload": clean, "payloadHash": _hash(clean)}

    def ingest_measurement(self, loop_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as con:
            loop_row = self._loop_row(con, loop_id)
            definition = self._loads(loop_row["definition_json"])
            if loop_row["status"] != "running":
                raise ClosedLoopError("Measurements can be ingested only while the loop is running.", 409)
            normalized = self._normalize_measurement(definition, payload)
            existing = con.execute("SELECT * FROM measurements WHERE payload_hash=?", (normalized["payloadHash"],)).fetchone()
            if existing:
                return {"ok": True, "deduplicated": True, "measurement": self._measurement_item(existing), "loop": self._item(con, loop_row)}
            signal_safety = self._limits_check(normalized["signals"], definition["safety"]["signalLimits"])
            emergency_hits = [name for name in definition["safety"]["emergencyStopSignals"] if bool(normalized["signals"].get(name))]
            safety = {"ok": signal_safety["ok"] and not emergency_hits, "violations": signal_safety["violations"], "emergencySignals": emergency_hits}
            if not safety["ok"]:
                now = _now()
                con.execute("UPDATE loops SET status='emergency-stopped',stop_reason=?,updated_at=? WHERE id=?", ("measurement safety interlock", now, loop_id))
                con.execute("UPDATE commands SET status='rejected',reason='measurement safety interlock' WHERE loop_id=? AND status IN ('pending-approval','ready','dispatched')", (loop_id,))
                self._event(con, loop_id, None, "measurement-rejected-by-interlock", safety)
                con.commit()
                raise ClosedLoopError("Measurement triggered a safety interlock; the loop was emergency-stopped.", 409)
            command_id = _text(payload.get("commandId"), 220) or None
            command_row = con.execute("SELECT * FROM commands WHERE id=? AND loop_id=?", (command_id, loop_id)).fetchone() if command_id else None
            if command_id and not command_row:
                raise ClosedLoopError("Measurement references an unknown command.", 404)
            sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM measurements WHERE loop_id=?", (loop_id,)).fetchone()[0]
            measurement_id = _text(payload.get("id"), 220) or f"measurement-{loop_id}-{sequence}-{secrets.token_hex(4)}"
            now = _now()
            con.execute("INSERT INTO measurements(id,loop_id,command_id,gateway_id,sequence,payload_hash,payload_json,parameters_json,signals_json,objective_value,signature_valid,safety_json,received_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (measurement_id, loop_id, command_id, normalized["gatewayId"], sequence, normalized["payloadHash"], _stable(normalized["payload"]), _stable(normalized["parameters"]), _stable(normalized["signals"]), normalized["objectiveValue"], int(normalized["signatureValid"]), _stable(safety), now))
            if command_row:
                con.execute("UPDATE commands SET status='acknowledged',acknowledged_at=? WHERE id=?", (now, command_id))
            self._event(con, loop_id, measurement_id, "measurement-ingested", {"payloadHash": normalized["payloadHash"], "objectiveValue": normalized["objectiveValue"], "signatureValid": normalized["signatureValid"]})
        observed = self.campaigns.observe(definition["campaignId"], {"parameters": normalized["parameters"], "objectiveValue": normalized["objectiveValue"], "source": f"closed-loop:{loop_id}:{normalized['gatewayId'] or 'manual'}", "result": {"signals": normalized["signals"], "measurementId": measurement_id}})
        with self._connect() as con:
            loop_row = self._loop_row(con, loop_id)
            cycle_sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM cycles WHERE loop_id=?", (loop_id,)).fetchone()[0]
            cycle_id = f"cycle-{loop_id}-{cycle_sequence}"
            trial = observed.get("trial", {})
            con.execute("INSERT INTO cycles(id,loop_id,sequence,source,campaign_trial_id,command_id,measurement_id,parameters_json,signals_json,objective_value,safety_json,status,started_at,completed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (cycle_id, loop_id, cycle_sequence, "instrument", trial.get("id"), command_id, measurement_id, _stable(normalized["parameters"]), _stable(normalized["signals"]), normalized["objectiveValue"], _stable(safety), "completed", now, now))
            con.execute("UPDATE loops SET cycle_count=cycle_count+1,failure_count=0,last_measurement_at=?,updated_at=? WHERE id=?", (now, now, loop_id))
            self._event(con, loop_id, cycle_id, "instrument-cycle-completed", {"measurementId": measurement_id, "trialId": trial.get("id"), "objectiveValue": normalized["objectiveValue"]})
        result = self.reconcile(loop_id)
        result.update({"deduplicated": False, "measurement": self.measurement(measurement_id), "observation": observed})
        return result

    def _import_simulation_trials(self, con: sqlite3.Connection, loop_row: sqlite3.Row, campaign: dict[str, Any]) -> int:
        imported = 0
        for trial in campaign.get("trials", []):
            if trial.get("status") != "completed":
                continue
            trial_id = trial.get("id")
            if not trial_id or con.execute("SELECT 1 FROM cycles WHERE loop_id=? AND campaign_trial_id=?", (loop_row["id"], trial_id)).fetchone():
                continue
            sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM cycles WHERE loop_id=?", (loop_row["id"],)).fetchone()[0]
            cycle_id = f"cycle-{loop_row['id']}-{sequence}"
            now = _now()
            con.execute("INSERT INTO cycles(id,loop_id,sequence,source,campaign_trial_id,workflow_run_id,parameters_json,signals_json,objective_value,safety_json,status,started_at,completed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (cycle_id, loop_row["id"], sequence, "simulation", trial_id, trial.get("workflowRunId"), _stable(trial.get("parameters") or {}), _stable({}), trial.get("objectiveValue"), _stable({"ok": True, "violations": []}), "completed", trial.get("createdAt") or now, trial.get("completedAt") or now))
            con.execute("UPDATE loops SET cycle_count=cycle_count+1,failure_count=0,updated_at=? WHERE id=?", (now, loop_row["id"]))
            self._event(con, loop_row["id"], cycle_id, "simulation-cycle-completed", {"trialId": trial_id, "workflowRunId": trial.get("workflowRunId"), "objectiveValue": trial.get("objectiveValue")})
            imported += 1
        return imported

    def reconcile(self, loop_id: str) -> dict[str, Any]:
        with self._connect() as con:
            loop_row = self._loop_row(con, loop_id)
            definition = self._loads(loop_row["definition_json"])
        campaign_result = self.campaigns.reconcile(definition["campaignId"], auto_advance=False)
        campaign = campaign_result.get("campaign", campaign_result)
        command = None
        with self._connect() as con:
            loop_row = self._loop_row(con, loop_id)
            imported = self._import_simulation_trials(con, loop_row, campaign)
            loop_row = self._loop_row(con, loop_id)
            status = loop_row["status"]
            if status == "running" and loop_row["cycle_count"] >= definition["control"]["maxCycles"]:
                con.execute("UPDATE loops SET status='completed',stop_reason='maximum-cycles-reached',updated_at=? WHERE id=?", (_now(), loop_id))
                self._event(con, loop_id, loop_id, "loop-completed", {"reason": "maximum-cycles-reached"})
                status = "completed"
            if status == "running" and definition["control"]["stopOnCampaignCompletion"] and campaign.get("status") == "completed":
                con.execute("UPDATE loops SET status='completed',stop_reason='campaign-completed',updated_at=? WHERE id=?", (_now(), loop_id))
                self._event(con, loop_id, loop_id, "loop-completed", {"reason": "campaign-completed"})
                status = "completed"
            loop_item = self._item(con, self._loop_row(con, loop_id))
        if loop_item["status"] == "running" and definition["control"]["autoAdvance"]:
            active_trials = [item for item in campaign.get("trials", []) if item.get("status") in {"proposed", "queued", "running"}]
            if definition["mode"] == "simulation" and not active_trials:
                try:
                    campaign_result = self.campaigns.advance(definition["campaignId"], count=1, reconcile_first=False)
                except Exception:
                    pass
            elif definition["mode"] == "instrument":
                try:
                    command = self.issue_next_command(loop_id)
                except ClosedLoopError as exc:
                    if exc.status_code != 409:
                        raise
            elif definition["mode"] == "hybrid":
                active_commands = [item for item in loop_item.get("commands", []) if item["status"] in {"pending-approval", "ready", "dispatched"}]
                if imported and not active_commands:
                    try:
                        command = self.issue_next_command(loop_id)
                    except ClosedLoopError:
                        command = None
                elif not active_trials and not active_commands:
                    try:
                        campaign_result = self.campaigns.advance(definition["campaignId"], count=1, reconcile_first=False)
                    except Exception:
                        pass
        return {**self.get(loop_id), "campaign": campaign_result, "command": command, "importedSimulationCycles": imported}

    def measurement(self, measurement_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = con.execute("SELECT * FROM measurements WHERE id=?", (measurement_id,)).fetchone()
            if not row:
                raise ClosedLoopError("Measurement not found.", 404)
            return self._measurement_item(row)

    def measurements(self, loop_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            self._loop_row(con, loop_id)
            rows = con.execute("SELECT * FROM measurements WHERE loop_id=? ORDER BY sequence DESC LIMIT ?", (loop_id, max(1, min(5000, int(limit))))).fetchall()
            return {"ok": True, "count": len(rows), "measurements": [self._measurement_item(row) for row in rows]}

    def commands(self, loop_id: str, status: str = "", limit: int = 500) -> dict[str, Any]:
        if status and status not in COMMAND_STATES:
            raise ClosedLoopError("Unsupported command status.")
        with self._connect() as con:
            self._loop_row(con, loop_id)
            query = "SELECT * FROM commands WHERE loop_id=?"
            values: list[Any] = [loop_id]
            if status:
                query += " AND status=?"; values.append(status)
            query += " ORDER BY sequence DESC LIMIT ?"; values.append(max(1, min(5000, int(limit))))
            rows = con.execute(query, values).fetchall()
            return {"ok": True, "count": len(rows), "commands": [self._command_item(row) for row in rows]}

    def timeline(self, loop_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            self._loop_row(con, loop_id)
            rows = con.execute("SELECT * FROM events WHERE loop_id=? ORDER BY sequence DESC LIMIT ?", (loop_id, max(1, min(5000, int(limit))))).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "loopId": row["loop_id"], "entityId": row["entity_id"], "eventType": row["event_type"], "payload": self._loads(row["payload_json"]), "createdAt": row["created_at"]} for row in rows]
            return {"ok": True, "count": len(events), "events": events}

    def tick(self) -> dict[str, Any]:
        with self._connect() as con:
            ids = [row[0] for row in con.execute("SELECT id FROM loops WHERE status='running' ORDER BY updated_at ASC LIMIT 100").fetchall()]
        results, failures = [], []
        for loop_id in ids:
            try:
                results.append({"loopId": loop_id, "result": self.reconcile(loop_id)})
            except Exception as exc:
                failures.append({"loopId": loop_id, "error": str(exc)})
                with self._connect() as con:
                    row = self._loop_row(con, loop_id)
                    definition = self._loads(row["definition_json"])
                    count = row["failure_count"] + 1
                    status = "failed" if count >= definition["safety"]["maxConsecutiveFailures"] else row["status"]
                    con.execute("UPDATE loops SET failure_count=?,status=?,stop_reason=?,updated_at=? WHERE id=?", (count, status, str(exc)[:1000] if status == "failed" else row["stop_reason"], _now(), loop_id))
                    self._event(con, loop_id, loop_id, "loop-reconcile-failed", {"error": str(exc), "failureCount": count, "status": status})
        return {"ok": not failures, "processed": len(ids), "succeeded": len(results), "failed": len(failures), "results": results, "failures": failures}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            schema = int(con.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()[0])
            counts = {row["status"]: row["count"] for row in con.execute("SELECT status,COUNT(*) AS count FROM loops GROUP BY status").fetchall()}
            commands = {row["status"]: row["count"] for row in con.execute("SELECT status,COUNT(*) AS count FROM commands GROUP BY status").fetchall()}
            return {"ok": True, "status": "ready", "version": VERSION, "schemaVersion": schema, "storage": "sqlite-wal", "dbPath": self.db_path, "pollSeconds": self.poll_seconds, "loopCounts": counts, "commandCounts": commands, "measurementSignatureConfigured": bool(self.measurement_secret), "directDeviceExecution": False}
