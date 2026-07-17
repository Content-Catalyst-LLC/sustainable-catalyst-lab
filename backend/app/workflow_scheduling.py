from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import copy
import hmac
import json
from pathlib import Path
import re
import secrets
import sqlite3
from threading import Event, Thread
from typing import Any

from .workflow_orchestration import WorkflowError

VERSION = "0.32.2"
SCHEDULE_SCHEMA = "sc-lab-workflow-schedule/0.32.2"
EVENT_SCHEMA = "sc-lab-workflow-trigger-event/0.32.2"
FIRING_SCHEMA = "sc-lab-workflow-schedule-firing/0.32.2"
DB_SCHEMA_VERSION = 2
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")
TRIGGER_TYPES = {"interval", "cron", "once", "event"}
MISFIRE_POLICIES = {"skip", "catch-up-one", "catch-up-all"}
CONCURRENCY_POLICIES = {"allow", "forbid", "replace"}
FIRING_STATES = {"started", "completed", "failed", "cancelled", "skipped"}


class WorkflowScheduleError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now_dt()).astimezone(timezone.utc).isoformat()


def _parse_dt(value: Any, field: str = "timestamp") -> datetime:
    text = str(value or "").strip()
    if not text:
        raise WorkflowScheduleError(f"{field} is required.")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise WorkflowScheduleError(f"{field} must be an ISO-8601 timestamp.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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


def _deep_get(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    if not path:
        return True, current
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def _parse_cron_atom(atom: str, minimum: int, maximum: int, field: str) -> set[int]:
    atom = atom.strip()
    if not atom:
        raise WorkflowScheduleError(f"Cron {field} contains an empty value.")
    step = 1
    base = atom
    if "/" in atom:
        base, raw_step = atom.split("/", 1)
        try:
            step = int(raw_step)
        except ValueError as exc:
            raise WorkflowScheduleError(f"Cron {field} step is invalid.") from exc
        if step < 1:
            raise WorkflowScheduleError(f"Cron {field} step must be positive.")
    if base == "*":
        start, end = minimum, maximum
    elif "-" in base:
        raw_start, raw_end = base.split("-", 1)
        try:
            start, end = int(raw_start), int(raw_end)
        except ValueError as exc:
            raise WorkflowScheduleError(f"Cron {field} range is invalid.") from exc
    else:
        try:
            start = end = int(base)
        except ValueError as exc:
            raise WorkflowScheduleError(f"Cron {field} value is invalid.") from exc
    if start < minimum or end > maximum or start > end:
        raise WorkflowScheduleError(f"Cron {field} must be between {minimum} and {maximum}.")
    return set(range(start, end + 1, step))


def parse_cron(expression: str) -> tuple[set[int], set[int], set[int], set[int], set[int]]:
    parts = _text(expression, 120).split()
    if len(parts) != 5:
        raise WorkflowScheduleError("Cron expressions require five fields: minute hour day-of-month month day-of-week.")
    ranges = ((0, 59, "minute"), (0, 23, "hour"), (1, 31, "day-of-month"), (1, 12, "month"), (0, 6, "day-of-week"))
    parsed: list[set[int]] = []
    for part, (low, high, name) in zip(parts, ranges):
        values: set[int] = set()
        for atom in part.split(","):
            values.update(_parse_cron_atom(atom, low, high, name))
        parsed.append(values)
    return tuple(parsed)  # type: ignore[return-value]


def cron_matches(expression: str, moment: datetime) -> bool:
    minute, hour, dom, month, dow = parse_cron(expression)
    utc = moment.astimezone(timezone.utc)
    cron_dow = (utc.weekday() + 1) % 7
    return utc.minute in minute and utc.hour in hour and utc.day in dom and utc.month in month and cron_dow in dow


def next_cron_after(expression: str, after: datetime) -> datetime:
    candidate = after.astimezone(timezone.utc).replace(second=0, microsecond=0) + timedelta(minutes=1)
    for _ in range(60 * 24 * 370):
        if cron_matches(expression, candidate):
            return candidate
        candidate += timedelta(minutes=1)
    raise WorkflowScheduleError("Cron expression did not produce an occurrence within 370 days.")


def verify_event_signature(payload: dict[str, Any], timestamp: str, signature: str, secret: str, tolerance_seconds: int = 300, now: datetime | None = None) -> bool:
    if not secret:
        return True
    try:
        event_time = _parse_dt(timestamp, "event signature timestamp")
    except WorkflowScheduleError:
        return False
    current = (now or _now_dt()).astimezone(timezone.utc)
    if abs((current - event_time).total_seconds()) > max(30, tolerance_seconds):
        return False
    supplied = _text(signature, 200)
    if supplied.startswith("sha256="):
        supplied = supplied[7:]
    expected = hmac.new(secret.encode("utf-8"), f"{timestamp}.{_stable(payload)}".encode("utf-8"), sha256).hexdigest()
    return hmac.compare_digest(expected, supplied)


def policies(max_catch_up_runs: int = 10) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "durable-scheduled-and-event-driven-workflow-automation",
        "triggers": {"interval": True, "cronUtc": True, "once": True, "authenticatedEvents": True, "eventDeduplication": True},
        "scheduling": {"durableNextFireTime": True, "startupMisfireRecovery": True, "manualTick": True, "maximumCatchUpRuns": max_catch_up_runs},
        "misfirePolicies": sorted(MISFIRE_POLICIES),
        "concurrencyPolicies": sorted(CONCURRENCY_POLICIES),
        "security": {"computeAuthenticationRequired": True, "optionalEventHmac": True, "arbitraryCallbacks": False, "arbitraryCode": False},
        "provenance": {"firingHistory": True, "eventReceipts": True, "workflowRunLinkage": True, "definitionHashes": True},
    }


def normalize_schedule(payload: dict[str, Any], max_catch_up_runs: int = 10) -> dict[str, Any]:
    source = payload.get("schedule") if isinstance(payload.get("schedule"), dict) else payload
    schedule_id = _text(source.get("id"), 180) or f"workflow-schedule-{secrets.token_hex(8)}"
    if not ID_RE.match(schedule_id):
        raise WorkflowScheduleError("Schedule ID must contain only letters, numbers, dots, underscores, and hyphens.")
    workflow_id = _text(source.get("workflowId") or source.get("workflow_id"), 180)
    if not workflow_id or not ID_RE.match(workflow_id):
        raise WorkflowScheduleError("A valid workflowId is required.")
    raw_trigger = source.get("trigger") if isinstance(source.get("trigger"), dict) else {}
    trigger_type = _text(raw_trigger.get("type") or source.get("triggerType"), 40).lower()
    if trigger_type not in TRIGGER_TYPES:
        raise WorkflowScheduleError("Trigger type must be interval, cron, once, or event.")
    trigger: dict[str, Any] = {"type": trigger_type}
    if trigger_type == "interval":
        trigger["everySeconds"] = _int(raw_trigger.get("everySeconds"), 3600, 1, 31536000)
        trigger["anchorAt"] = _iso(_parse_dt(raw_trigger["anchorAt"], "trigger.anchorAt")) if raw_trigger.get("anchorAt") else _iso()
    elif trigger_type == "cron":
        expression = _text(raw_trigger.get("expression"), 120)
        parse_cron(expression)
        timezone_name = _text(raw_trigger.get("timezone"), 60) or "UTC"
        if timezone_name.upper() not in {"UTC", "ETC/UTC", "GMT"}:
            raise WorkflowScheduleError("v0.32.2 cron schedules use UTC. Convert local times to UTC before saving.")
        trigger.update({"expression": expression, "timezone": "UTC"})
    elif trigger_type == "once":
        trigger["at"] = _iso(_parse_dt(raw_trigger.get("at"), "trigger.at"))
    else:
        event_type = _text(raw_trigger.get("eventType") or raw_trigger.get("event"), 180)
        if not event_type or not ID_RE.match(event_type):
            raise WorkflowScheduleError("Event triggers require a valid eventType.")
        filters = raw_trigger.get("filters") if isinstance(raw_trigger.get("filters"), dict) else {}
        if len(filters) > 64:
            raise WorkflowScheduleError("Event triggers may define at most 64 filters.")
        trigger.update({"eventType": event_type, "filters": copy.deepcopy(filters)})
    run = source.get("run") if isinstance(source.get("run"), dict) else {}
    misfire = _text(run.get("misfirePolicy") or source.get("misfirePolicy"), 40) or "catch-up-one"
    if misfire not in MISFIRE_POLICIES:
        raise WorkflowScheduleError("Unsupported misfirePolicy.")
    concurrency = _text(run.get("concurrencyPolicy") or source.get("concurrencyPolicy"), 40) or "forbid"
    if concurrency not in CONCURRENCY_POLICIES:
        raise WorkflowScheduleError("Unsupported concurrencyPolicy.")
    record = {
        "schema": SCHEDULE_SCHEMA,
        "version": VERSION,
        "recordType": "workflow-schedule",
        "id": schedule_id,
        "title": _text(source.get("title"), 300) or schedule_id.replace("-", " ").title(),
        "description": _text(source.get("description"), 2000),
        "workflowId": workflow_id,
        "enabled": source.get("enabled", True) is not False,
        "trigger": trigger,
        "run": {
            "inputs": copy.deepcopy(run.get("inputs")) if isinstance(run.get("inputs"), dict) else {},
            "context": copy.deepcopy(run.get("context")) if isinstance(run.get("context"), dict) else {},
            "misfirePolicy": misfire,
            "misfireGraceSeconds": _int(run.get("misfireGraceSeconds"), 300, 0, 86400),
            "maxCatchUpRuns": _int(run.get("maxCatchUpRuns"), min(10, max_catch_up_runs), 1, max_catch_up_runs),
            "concurrencyPolicy": concurrency,
            "maxConcurrentRuns": _int(run.get("maxConcurrentRuns"), 1, 1, 100),
        },
        "metadata": copy.deepcopy(source.get("metadata")) if isinstance(source.get("metadata"), dict) else {},
        "createdAt": source.get("createdAt") or _iso(),
    }
    record["definitionHash"] = _hash({key: value for key, value in record.items() if key not in {"createdAt", "definitionHash"}})
    return record


class WorkflowScheduler:
    def __init__(self, db_path: str, orchestrator: Any, poll_seconds: float = 30.0, max_catch_up_runs: int = 10, history_limit: int = 20000):
        self.db_path = str(db_path)
        self.orchestrator = orchestrator
        self.poll_seconds = max(1.0, min(3600.0, float(poll_seconds)))
        self.max_catch_up_runs = max(1, min(100, int(max_catch_up_runs)))
        self.history_limit = max(100, min(1000000, int(history_limit)))
        self._stop = Event()
        self._thread: Thread | None = None
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _migrate(self) -> None:
        with self._connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS workflow_schedule_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS workflow_schedules(
              id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, trigger_type TEXT NOT NULL,
              enabled INTEGER NOT NULL, definition_hash TEXT NOT NULL, definition_json TEXT NOT NULL,
              next_fire_at TEXT, last_fire_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_schedules_due ON workflow_schedules(enabled,trigger_type,next_fire_at);
            CREATE INDEX IF NOT EXISTS idx_workflow_schedules_workflow ON workflow_schedules(workflow_id,updated_at DESC);
            CREATE TABLE IF NOT EXISTS workflow_schedule_firings(
              id TEXT PRIMARY KEY, schedule_id TEXT NOT NULL REFERENCES workflow_schedules(id) ON DELETE CASCADE,
              occurrence_at TEXT NOT NULL, source TEXT NOT NULL, event_id TEXT, workflow_run_id TEXT,
              status TEXT NOT NULL, reason TEXT, payload_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              dedupe_key TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_schedule_firings_schedule ON workflow_schedule_firings(schedule_id,created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_workflow_schedule_firings_run ON workflow_schedule_firings(workflow_run_id);
            CREATE TABLE IF NOT EXISTS workflow_trigger_events(
              event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, payload_hash TEXT NOT NULL,
              payload_json TEXT NOT NULL, received_at TEXT NOT NULL, processed_at TEXT,
              status TEXT NOT NULL, result_json TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_trigger_events_type ON workflow_trigger_events(event_type,received_at DESC);
            """)
            columns = {row["name"] for row in con.execute("PRAGMA table_info(workflow_schedule_firings)").fetchall()}
            if "dedupe_key" not in columns:
                con.execute("ALTER TABLE workflow_schedule_firings ADD COLUMN dedupe_key TEXT")
            con.execute(
                "UPDATE workflow_schedule_firings SET dedupe_key=schedule_id || '|' || occurrence_at || '|' || source || '|' || COALESCE(event_id,'') WHERE dedupe_key IS NULL OR dedupe_key=''"
            )
            con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_workflow_schedule_firings_dedupe ON workflow_schedule_firings(dedupe_key)")
            con.execute("INSERT INTO workflow_schedule_meta(key,value) VALUES('schema_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(DB_SCHEMA_VERSION),))

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._loop, name="sc-lab-workflow-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=max(2.0, self.poll_seconds + 1.0))
        self._thread = None

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.tick()
            except Exception:
                pass
            self._stop.wait(self.poll_seconds)

    def _next_after(self, schedule: dict[str, Any], after: datetime) -> datetime | None:
        trigger = schedule["trigger"]
        kind = trigger["type"]
        if kind == "event":
            return None
        if kind == "once":
            at = _parse_dt(trigger["at"])
            return at if at > after else None
        if kind == "cron":
            return next_cron_after(trigger["expression"], after)
        anchor = _parse_dt(trigger["anchorAt"])
        seconds = int(trigger["everySeconds"])
        if after < anchor:
            return anchor
        elapsed = int((after - anchor).total_seconds())
        return anchor + timedelta(seconds=((elapsed // seconds) + 1) * seconds)

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        schedule = normalize_schedule(payload, self.max_catch_up_runs)
        try:
            self.orchestrator.get(schedule["workflowId"])
        except WorkflowError as exc:
            raise WorkflowScheduleError(f"Referenced workflow was not found: {schedule['workflowId']}", 404) from exc
        if not schedule["enabled"] or schedule["trigger"]["type"] == "event":
            next_fire = None
        elif schedule["trigger"]["type"] == "once":
            next_fire = _parse_dt(schedule["trigger"]["at"])
        else:
            next_fire = self._next_after(schedule, _now_dt() - timedelta(microseconds=1))
        return {"ok": True, "valid": True, "schedule": schedule, "nextFireAt": _iso(next_fire) if next_fire else None}

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self.validate(payload)
        schedule = validated["schedule"]
        now = _iso()
        with self._connect() as con:
            old = con.execute("SELECT created_at FROM workflow_schedules WHERE id=?", (schedule["id"],)).fetchone()
            created = old["created_at"] if old else schedule["createdAt"]
            con.execute(
                """INSERT INTO workflow_schedules(id,workflow_id,trigger_type,enabled,definition_hash,definition_json,next_fire_at,last_fire_at,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET workflow_id=excluded.workflow_id,trigger_type=excluded.trigger_type,
                enabled=excluded.enabled,definition_hash=excluded.definition_hash,definition_json=excluded.definition_json,next_fire_at=excluded.next_fire_at,updated_at=excluded.updated_at""",
                (schedule["id"], schedule["workflowId"], schedule["trigger"]["type"], 1 if schedule["enabled"] else 0, schedule["definitionHash"], _stable(schedule), validated["nextFireAt"], None, created, now),
            )
        return {"ok": True, "created": old is None, "schedule": self.get(schedule["id"])["schedule"]}

    def _row_item(self, row: sqlite3.Row) -> dict[str, Any]:
        item = json.loads(row["definition_json"])
        item.update({"enabled": bool(row["enabled"]), "nextFireAt": row["next_fire_at"], "lastFireAt": row["last_fire_at"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]})
        return item

    def get(self, schedule_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = con.execute("SELECT * FROM workflow_schedules WHERE id=?", (_text(schedule_id, 180),)).fetchone()
        if not row:
            raise WorkflowScheduleError("Workflow schedule was not found.", 404)
        return {"ok": True, "schedule": self._row_item(row)}

    def list(self, workflow_id: str = "", enabled: bool | None = None, limit: int = 100) -> dict[str, Any]:
        clauses: list[str] = []
        params: list[Any] = []
        if workflow_id:
            clauses.append("workflow_id=?")
            params.append(_text(workflow_id, 180))
        if enabled is not None:
            clauses.append("enabled=?")
            params.append(1 if enabled else 0)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM workflow_schedules{where} ORDER BY updated_at DESC LIMIT ?", params).fetchall()
        schedules = [self._row_item(row) for row in rows]
        return {"ok": True, "count": len(schedules), "schedules": schedules}

    def set_enabled(self, schedule_id: str, enabled: bool) -> dict[str, Any]:
        current = self.get(schedule_id)["schedule"]
        now_dt = _now_dt()
        if not enabled:
            next_fire = None
        elif current["trigger"]["type"] == "once":
            # Preserve a missed one-time occurrence so the configured misfire policy can decide what to do.
            next_fire = _parse_dt(current["trigger"]["at"])
        else:
            next_fire = self._next_after(current, now_dt - timedelta(microseconds=1))
        with self._connect() as con:
            con.execute("UPDATE workflow_schedules SET enabled=?,next_fire_at=?,updated_at=? WHERE id=?", (1 if enabled else 0, _iso(next_fire) if next_fire else None, _iso(), current["id"]))
        return self.get(current["id"])

    def delete(self, schedule_id: str) -> dict[str, Any]:
        with self._connect() as con:
            count = con.execute("DELETE FROM workflow_schedules WHERE id=?", (_text(schedule_id, 180),)).rowcount
        if not count:
            raise WorkflowScheduleError("Workflow schedule was not found.", 404)
        return {"ok": True, "deleted": schedule_id}

    def _refresh_firings(self, con: sqlite3.Connection) -> None:
        rows = con.execute("SELECT * FROM workflow_schedule_firings WHERE status='started' AND workflow_run_id IS NOT NULL ORDER BY created_at LIMIT 500").fetchall()
        for row in rows:
            try:
                run = self.orchestrator.run(row["workflow_run_id"], reconcile=True)["run"]
            except WorkflowError:
                continue
            if run["status"] in {"completed", "failed", "cancelled"}:
                con.execute("UPDATE workflow_schedule_firings SET status=?,reason=?,updated_at=? WHERE id=?", (run["status"], run.get("error"), _iso(), row["id"]))

    def _active_runs(self, con: sqlite3.Connection, schedule_id: str) -> list[sqlite3.Row]:
        self._refresh_firings(con)
        return con.execute("SELECT * FROM workflow_schedule_firings WHERE schedule_id=? AND status='started' AND workflow_run_id IS NOT NULL ORDER BY created_at", (schedule_id,)).fetchall()

    def _record_firing(self, con: sqlite3.Connection, schedule_id: str, occurrence: datetime, source: str, status: str, payload: dict[str, Any], event_id: str | None = None, run_id: str | None = None, reason: str = "") -> dict[str, Any]:
        firing_id = f"workflow-firing-{secrets.token_hex(10)}"
        now = _iso()
        occurrence_at = _iso(occurrence)
        dedupe_key = f"{schedule_id}|{occurrence_at}|{source}|{event_id or ''}"
        con.execute(
            "INSERT INTO workflow_schedule_firings(id,schedule_id,occurrence_at,source,event_id,workflow_run_id,status,reason,payload_json,created_at,updated_at,dedupe_key) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (firing_id, schedule_id, occurrence_at, source, event_id, run_id, status, _text(reason, 2000), _stable(payload), now, now, dedupe_key),
        )
        return {"schema": FIRING_SCHEMA, "id": firing_id, "scheduleId": schedule_id, "occurrenceAt": _iso(occurrence), "source": source, "eventId": event_id, "workflowRunId": run_id, "status": status, "reason": reason, "payload": payload, "createdAt": now, "updatedAt": now}

    def _fire(self, con: sqlite3.Connection, schedule: dict[str, Any], occurrence: datetime, source: str, event: dict[str, Any] | None = None, override: dict[str, Any] | None = None) -> dict[str, Any]:
        run_policy = schedule["run"]
        active = self._active_runs(con, schedule["id"])
        if active and run_policy["concurrencyPolicy"] == "forbid":
            return self._record_firing(con, schedule["id"], occurrence, source, "skipped", {"activeRuns": [row["workflow_run_id"] for row in active]}, event.get("id") if event else None, reason="concurrency-forbid")
        if active and run_policy["concurrencyPolicy"] == "replace":
            for row in active:
                try:
                    self.orchestrator.cancel(row["workflow_run_id"], {"operatorId": "workflow-scheduler", "reason": f"replaced by schedule {schedule['id']}"})
                    con.execute("UPDATE workflow_schedule_firings SET status='cancelled',reason=?,updated_at=? WHERE id=?", ("replaced by newer occurrence", _iso(), row["id"]))
                except WorkflowError:
                    pass
        elif len(active) >= int(run_policy["maxConcurrentRuns"]):
            return self._record_firing(con, schedule["id"], occurrence, source, "skipped", {"activeRuns": [row["workflow_run_id"] for row in active]}, event.get("id") if event else None, reason="maximum-concurrent-runs")
        override = override if isinstance(override, dict) else {}
        inputs = copy.deepcopy(run_policy["inputs"])
        if isinstance(override.get("inputs"), dict):
            inputs.update(copy.deepcopy(override["inputs"]))
        context = copy.deepcopy(run_policy["context"])
        context["automation"] = {"scheduleId": schedule["id"], "occurrenceAt": _iso(occurrence), "source": source, "definitionHash": schedule["definitionHash"]}
        if event:
            inputs["event"] = copy.deepcopy(event)
            context["automation"]["eventId"] = event["id"]
            context["automation"]["eventType"] = event["type"]
        if isinstance(override.get("context"), dict):
            context.update(copy.deepcopy(override["context"]))
        run_id = f"scheduled-run-{secrets.token_hex(10)}"
        try:
            run = self.orchestrator.start_run(schedule["workflowId"], {"id": run_id, "inputs": inputs, "context": context})["run"]
        except WorkflowError as exc:
            return self._record_firing(con, schedule["id"], occurrence, source, "failed", {"inputs": inputs, "context": context}, event.get("id") if event else None, reason=exc.detail)
        return self._record_firing(con, schedule["id"], occurrence, source, "started", {"inputs": inputs, "context": context}, event.get("id") if event else None, run_id=run["id"])

    def trigger(self, schedule_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        schedule = self.get(schedule_id)["schedule"]
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            firing = self._fire(con, schedule, _now_dt(), "manual", override=payload or {})
            con.execute("COMMIT")
        return {"ok": True, "firing": firing}

    def _due_occurrences(self, schedule: dict[str, Any], next_fire: datetime, now: datetime) -> tuple[list[datetime], datetime | None, int]:
        due: list[datetime] = []
        cursor: datetime | None = next_fire
        hard_limit = max(self.max_catch_up_runs * 20, 100)
        scanned = 0
        while cursor is not None and cursor <= now and scanned < hard_limit:
            due.append(cursor)
            cursor = self._next_after(schedule, cursor)
            scanned += 1
        return due, cursor, scanned

    def tick(self, now: datetime | None = None) -> dict[str, Any]:
        current = (now or _now_dt()).astimezone(timezone.utc)
        results: list[dict[str, Any]] = []
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            self._refresh_firings(con)
            rows = con.execute("SELECT * FROM workflow_schedules WHERE enabled=1 AND trigger_type!='event' AND next_fire_at IS NOT NULL AND next_fire_at<=? ORDER BY next_fire_at LIMIT 500", (_iso(current),)).fetchall()
            for row in rows:
                schedule = self._row_item(row)
                next_fire = _parse_dt(row["next_fire_at"])
                due, following, scanned = self._due_occurrences(schedule, next_fire, current)
                policy = schedule["run"]["misfirePolicy"]
                grace = int(schedule["run"]["misfireGraceSeconds"])
                selected: list[datetime] = []
                skipped: list[datetime] = []
                if policy == "catch-up-all":
                    selected = due[-int(schedule["run"]["maxCatchUpRuns"]):]
                    skipped = due[:-len(selected)] if selected else due
                elif policy == "catch-up-one":
                    selected = due[-1:] if due else []
                    skipped = due[:-1]
                else:
                    for occurrence in due:
                        if (current - occurrence).total_seconds() <= grace:
                            selected = [occurrence]
                        else:
                            skipped.append(occurrence)
                for occurrence in skipped:
                    try:
                        results.append(self._record_firing(con, schedule["id"], occurrence, "schedule", "skipped", {"misfirePolicy": policy}, reason="missed-occurrence"))
                    except sqlite3.IntegrityError:
                        pass
                for occurrence in selected:
                    try:
                        results.append(self._fire(con, schedule, occurrence, "schedule"))
                    except sqlite3.IntegrityError:
                        pass
                con.execute("UPDATE workflow_schedules SET next_fire_at=?,last_fire_at=?,updated_at=? WHERE id=?", (_iso(following) if following else None, _iso(due[-1]) if due else row["last_fire_at"], _iso(), schedule["id"]))
            con.execute("COMMIT")
        return {"ok": True, "checkedAt": _iso(current), "dueSchedules": len(rows), "firings": results, "firingCount": len(results)}

    def _event_matches(self, schedule: dict[str, Any], event: dict[str, Any]) -> bool:
        if schedule["trigger"]["eventType"] != event["type"]:
            return False
        root = {"event": event, "payload": event["payload"], "metadata": event.get("metadata", {})}
        for path, expected in schedule["trigger"].get("filters", {}).items():
            found, actual = _deep_get(root, _text(path, 500))
            if not found or actual != expected:
                return False
        return True

    def ingest_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_id = _text(payload.get("id") or payload.get("eventId"), 180) or f"workflow-event-{secrets.token_hex(10)}"
        event_type = _text(payload.get("type") or payload.get("eventType"), 180)
        if not ID_RE.match(event_id) or not event_type or not ID_RE.match(event_type):
            raise WorkflowScheduleError("Event id and type must use letters, numbers, dots, underscores, and hyphens.")
        event = {"schema": EVENT_SCHEMA, "id": event_id, "type": event_type, "occurredAt": _iso(_parse_dt(payload["occurredAt"], "occurredAt")) if payload.get("occurredAt") else _iso(), "payload": copy.deepcopy(payload.get("payload")) if isinstance(payload.get("payload"), dict) else {}, "metadata": copy.deepcopy(payload.get("metadata")) if isinstance(payload.get("metadata"), dict) else {}}
        received = _iso()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute("SELECT * FROM workflow_trigger_events WHERE event_id=?", (event_id,)).fetchone()
            if existing:
                result = json.loads(existing["result_json"]) if existing["result_json"] else {"firings": []}
                con.execute("COMMIT")
                return {"ok": True, "duplicate": True, "event": event, **result}
            con.execute("INSERT INTO workflow_trigger_events(event_id,event_type,payload_hash,payload_json,received_at,status) VALUES(?,?,?,?,?,'processing')", (event_id, event_type, _hash(event), _stable(event), received))
            rows = con.execute("SELECT * FROM workflow_schedules WHERE enabled=1 AND trigger_type='event' ORDER BY updated_at").fetchall()
            firings: list[dict[str, Any]] = []
            for row in rows:
                schedule = self._row_item(row)
                if self._event_matches(schedule, event):
                    firings.append(self._fire(con, schedule, _parse_dt(event["occurredAt"]), "event", event=event))
            result = {"matchedSchedules": len(firings), "firings": firings}
            con.execute("UPDATE workflow_trigger_events SET processed_at=?,status='processed',result_json=? WHERE event_id=?", (_iso(), _stable(result), event_id))
            con.execute("COMMIT")
        return {"ok": True, "duplicate": False, "event": event, **result}

    def firings(self, schedule_id: str = "", status: str = "", limit: int = 100) -> dict[str, Any]:
        if status and status not in FIRING_STATES:
            raise WorkflowScheduleError("Unsupported firing status.")
        clauses: list[str] = []
        params: list[Any] = []
        if schedule_id:
            clauses.append("schedule_id=?")
            params.append(_text(schedule_id, 180))
        if status:
            clauses.append("status=?")
            params.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            self._refresh_firings(con)
            rows = con.execute(f"SELECT * FROM workflow_schedule_firings{where} ORDER BY created_at DESC LIMIT ?", params).fetchall()
        items = [{"schema": FIRING_SCHEMA, "id": row["id"], "scheduleId": row["schedule_id"], "occurrenceAt": row["occurrence_at"], "source": row["source"], "eventId": row["event_id"], "workflowRunId": row["workflow_run_id"], "status": row["status"], "reason": row["reason"], "payload": json.loads(row["payload_json"]), "createdAt": row["created_at"], "updatedAt": row["updated_at"]} for row in rows]
        return {"ok": True, "count": len(items), "firings": items}

    def events(self, event_type: str = "", limit: int = 100) -> dict[str, Any]:
        params: list[Any] = []
        where = ""
        if event_type:
            where = " WHERE event_type=?"
            params.append(_text(event_type, 180))
        params.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM workflow_trigger_events{where} ORDER BY received_at DESC LIMIT ?", params).fetchall()
        items = [{"schema": EVENT_SCHEMA, **json.loads(row["payload_json"]), "receivedAt": row["received_at"], "processedAt": row["processed_at"], "status": row["status"], "result": json.loads(row["result_json"]) if row["result_json"] else None} for row in rows]
        return {"ok": True, "count": len(items), "events": items}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            self._refresh_firings(con)
            counts = {row["trigger_type"]: int(row["count"]) for row in con.execute("SELECT trigger_type,COUNT(*) count FROM workflow_schedules GROUP BY trigger_type")}
            enabled = int(con.execute("SELECT COUNT(*) FROM workflow_schedules WHERE enabled=1").fetchone()[0])
            due = int(con.execute("SELECT COUNT(*) FROM workflow_schedules WHERE enabled=1 AND next_fire_at IS NOT NULL AND next_fire_at<=?", (_iso(),)).fetchone()[0])
            firing_counts = {row["status"]: int(row["count"]) for row in con.execute("SELECT status,COUNT(*) count FROM workflow_schedule_firings GROUP BY status")}
            event_count = int(con.execute("SELECT COUNT(*) FROM workflow_trigger_events").fetchone()[0])
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schemaVersion": DB_SCHEMA_VERSION, "storage": "sqlite-wal", "databasePath": self.db_path, "schedulerThreadActive": bool(self._thread and self._thread.is_alive()), "pollSeconds": self.poll_seconds, "scheduleCounts": counts, "enabledSchedules": enabled, "dueSchedules": due, "firingCounts": firing_counts, "eventReceipts": event_count, "databaseIntegrity": integrity}
