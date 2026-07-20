from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.40.0"


class BetaPlatformError(ValueError):
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
    text = str(value or "").strip().lower()
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_.:"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise BetaPlatformError(f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 4000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise BetaPlatformError(f"{label} is required.")
    if len(text) > maximum:
        raise BetaPlatformError(f"{label} exceeds {maximum} characters.")
    return text


SENSITIVE_KEYS = {
    "secret", "password", "passwd", "credential", "token", "api_key", "apikey",
    "private_key", "access_key", "refresh_token", "authorization", "cookie",
    "raw_data", "dataset_bytes", "executable", "callback", "code",
}


def _reject_sensitive(value: Any, path: str = "payload", depth: int = 0) -> None:
    if depth > 20:
        raise BetaPlatformError("Payload nesting exceeds the beta safety boundary.")
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in SENSITIVE_KEYS or any(part in normalized for part in ("password", "secret", "private_key", "access_token")):
                raise BetaPlatformError(f"Sensitive field is not permitted in beta operations: {path}.{key}")
            _reject_sensitive(child, f"{path}.{key}", depth + 1)
    elif isinstance(value, list):
        if len(value) > 10000:
            raise BetaPlatformError("Payload contains too many list items.")
        for index, child in enumerate(value):
            _reject_sensitive(child, f"{path}[{index}]", depth + 1)
    elif isinstance(value, str):
        lowered = value.lower()
        if "-----begin private key-----" in lowered or "-----begin rsa private key-----" in lowered:
            raise BetaPlatformError("Private key material is not permitted in beta operations.")
        if len(value) > 200000:
            raise BetaPlatformError("Payload text exceeds the beta safety boundary.")


ONBOARDING_STAGES = (
    "institution", "identity", "workspace", "data", "workflow", "validation", "publication", "complete"
)
PROJECT_STAGES = (
    "define", "source", "design", "execute", "analyze", "review", "publish", "handoff", "monitor", "complete"
)

PROJECT_TEMPLATES: dict[str, dict[str, Any]] = {
    "evidence-to-experiment": {
        "title": "Evidence to Experiment",
        "description": "Move from research question and source evidence through a governed experiment, analysis, review, and publication handoff.",
        "recommendedModules": ["external-discovery-v0292", "research-provenance-v0290", "experiment-framework-v0300", "research-quality-v0291", "publication-studio-v0370"],
        "requiredOutputs": ["research-question", "evidence-record", "experiment-protocol", "experiment-run", "review", "publication"],
    },
    "instrument-to-publication": {
        "title": "Instrument to Publication",
        "description": "Capture governed observations, validate custody and methods, analyze results, and assemble a reproducible publication package.",
        "recommendedModules": ["laboratory-data-instrumentation-v0250", "instrumentation-validation-v0253", "dataset-registry-v0281", "reproducible-runs-v0282", "manuscript-assembly-v0371"],
        "requiredOutputs": ["instrument-record", "dataset", "analysis", "reproducibility-package", "manuscript"],
    },
    "scenario-to-decision": {
        "title": "Scenario to Decision",
        "description": "Build and validate a scientific scenario, quantify uncertainty, and hand a governed decision packet to Decision Studio.",
        "recommendedModules": ["model-registry-v0340", "ensemble-uncertainty-v0341", "surrogate-reduced-order-v0342", "typed-cross-product-handoffs-v0381"],
        "requiredOutputs": ["model", "scenario", "uncertainty-report", "decision-packet", "handoff-receipt"],
    },
}


def policies(persistent_disk_mounted: bool, telemetry_enabled: bool) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "releaseStage": "beta",
        "generalAvailabilityClaim": False,
        "persistentDiskMounted": bool(persistent_disk_mounted),
        "telemetryEnabled": bool(telemetry_enabled),
        "telemetryOptInRequired": True,
        "telemetryStoresRawIdentifiers": False,
        "telemetryStoresResearchPayloads": False,
        "productionMutation": False,
        "capabilities": {
            "institutionalBetaCohorts": True,
            "guidedResearchProjects": True,
            "privacyMinimizedTelemetry": True,
            "feedbackOperations": True,
            "knownLimitationsRegister": True,
            "supportAndIncidents": True,
            "releaseReadinessGate": True,
        },
        "onboardingStages": list(ONBOARDING_STAGES),
        "projectStages": list(PROJECT_STAGES),
    }


class ConnectedPlatformBetaManager:
    def __init__(
        self,
        db_path: str,
        persistent_disk_mounted: bool,
        telemetry_enabled: bool = False,
        history_limit: int = 250000,
        max_beta_records: int = 100000,
    ) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.telemetry_enabled = bool(telemetry_enabled)
        self.history_limit = max(100, int(history_limit))
        self.max_beta_records = max(100, int(max_beta_records))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS beta_cohorts(
              id TEXT PRIMARY KEY, name TEXT NOT NULL, institution_id TEXT NOT NULL,
              owner TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS onboarding_records(
              id TEXT PRIMARY KEY, cohort_id TEXT, institution_id TEXT NOT NULL,
              principal_id TEXT NOT NULL, workspace_id TEXT NOT NULL, stage TEXT NOT NULL,
              stage_index INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guided_projects(
              id TEXT PRIMARY KEY, template_id TEXT NOT NULL, title TEXT NOT NULL,
              cohort_id TEXT, workspace_id TEXT NOT NULL, owner TEXT NOT NULL,
              stage TEXT NOT NULL, stage_index INTEGER NOT NULL, status TEXT NOT NULL,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS telemetry_events(
              id TEXT PRIMARY KEY, event_type TEXT NOT NULL, occurred_at TEXT NOT NULL,
              actor_hash TEXT NOT NULL, workspace_hash TEXT NOT NULL,
              properties_json TEXT NOT NULL, event_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS beta_feedback(
              id TEXT PRIMARY KEY, category TEXT NOT NULL, severity TEXT NOT NULL,
              status TEXT NOT NULL, title TEXT NOT NULL, created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS known_limitations(
              id TEXT PRIMARY KEY, severity TEXT NOT NULL, status TEXT NOT NULL,
              title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS support_cases(
              id TEXT PRIMARY KEY, severity TEXT NOT NULL, status TEXT NOT NULL,
              title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS readiness_reports(
              id TEXT PRIMARY KEY, status TEXT NOT NULL, created_at TEXT NOT NULL,
              report_json TEXT NOT NULL, report_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS beta_events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
              actor TEXT NOT NULL, subject_type TEXT NOT NULL, subject_id TEXT NOT NULL,
              occurred_at TEXT NOT NULL, payload_json TEXT NOT NULL,
              previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
            );
            """)

    def _count(self, table: str) -> int:
        with self._connect() as db:
            return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    def _ensure_capacity(self, table: str) -> None:
        if self._count(table) >= self.max_beta_records:
            raise BetaPlatformError("The beta record capacity has been reached.", 429)

    def _event(self, db: sqlite3.Connection, event_type: str, actor: str, subject_type: str, subject_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        previous = db.execute("SELECT event_hash FROM beta_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous_hash = str(previous[0]) if previous else "0" * 64
        event = {
            "eventType": event_type,
            "actor": actor,
            "subjectType": subject_type,
            "subjectId": subject_id,
            "occurredAt": _now(),
            "payload": payload,
            "previousHash": previous_hash,
        }
        event_hash = _sha(event)
        db.execute(
            "INSERT INTO beta_events(event_type,actor,subject_type,subject_id,occurred_at,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (event_type, actor, subject_type, subject_id, event["occurredAt"], json.dumps(payload, sort_keys=True), previous_hash, event_hash),
        )
        return {**event, "eventHash": event_hash}

    @staticmethod
    def _row_payload(row: sqlite3.Row, key: str = "payload_json") -> dict[str, Any]:
        return json.loads(str(row[key]))

    def health(self) -> dict[str, Any]:
        try:
            with self._connect() as db:
                counts = {
                    "cohorts": db.execute("SELECT COUNT(*) FROM beta_cohorts").fetchone()[0],
                    "onboarding": db.execute("SELECT COUNT(*) FROM onboarding_records").fetchone()[0],
                    "projects": db.execute("SELECT COUNT(*) FROM guided_projects").fetchone()[0],
                    "feedback": db.execute("SELECT COUNT(*) FROM beta_feedback").fetchone()[0],
                    "limitations": db.execute("SELECT COUNT(*) FROM known_limitations").fetchone()[0],
                    "supportCases": db.execute("SELECT COUNT(*) FROM support_cases").fetchone()[0],
                    "readinessReports": db.execute("SELECT COUNT(*) FROM readiness_reports").fetchone()[0],
                }
            writable = True
        except sqlite3.Error:
            counts, writable = {}, False
        return {
            "ok": writable,
            "status": "beta-ready" if writable else "degraded",
            "serviceVersion": VERSION,
            "releaseStage": "beta",
            "storage": "persistent" if self.persistent_disk_mounted else "instance-local",
            "telemetryEnabled": self.telemetry_enabled,
            "generalAvailabilityClaim": False,
            "counts": counts,
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "onboardingStages": list(ONBOARDING_STAGES),
            "projectStages": list(PROJECT_STAGES),
            "projectTemplates": [{"id": key, **value} for key, value in PROJECT_TEMPLATES.items()],
            "feedbackCategories": ["bug", "usability", "documentation", "research-method", "integration", "accessibility", "security", "other"],
            "severities": ["low", "medium", "high", "critical"],
        }

    def create_cohort(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        self._ensure_capacity("beta_cohorts")
        cohort_id = _clean_id(payload.get("id") or f"cohort-{uuid.uuid4().hex[:12]}", "cohort id")
        status = _clean_id(payload.get("status", "planned"), "cohort status")
        if status not in {"planned", "active", "paused", "closed"}:
            raise BetaPlatformError("Unsupported cohort status.")
        record = {
            "id": cohort_id,
            "name": _clean_text(payload.get("name"), "Cohort name", 240),
            "institutionId": _clean_id(payload.get("institutionId"), "institution id"),
            "owner": _clean_text(payload.get("owner") or actor, "Cohort owner", 240),
            "status": status,
            "goals": [str(item)[:500] for item in (payload.get("goals") or [])[:25]],
            "startDate": str(payload.get("startDate") or ""),
            "endDate": str(payload.get("endDate") or ""),
            "createdAt": _now(),
            "updatedAt": _now(),
        }
        record_hash = _sha(record)
        with self._lock, self._connect() as db:
            try:
                db.execute("INSERT INTO beta_cohorts VALUES(?,?,?,?,?,?,?,?,?)", (cohort_id, record["name"], record["institutionId"], record["owner"], status, record["createdAt"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash))
            except sqlite3.IntegrityError as exc:
                raise BetaPlatformError("Cohort id already exists.", 409) from exc
            event = self._event(db, "beta.cohort.created", actor, "cohort", cohort_id, {"recordHash": record_hash})
        return {"ok": True, "cohort": {**record, "recordHash": record_hash}, "event": event}

    def list_cohorts(self, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT payload_json,record_hash FROM beta_cohorts ORDER BY created_at DESC LIMIT ?", (max(1, min(int(limit), 2000)),)).fetchall()
        return {"ok": True, "cohorts": [{**json.loads(row["payload_json"]), "recordHash": row["record_hash"]} for row in rows]}

    def start_onboarding(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        self._ensure_capacity("onboarding_records")
        record_id = _clean_id(payload.get("id") or f"onboarding-{uuid.uuid4().hex[:12]}", "onboarding id")
        record = {
            "id": record_id,
            "cohortId": _clean_id(payload["cohortId"], "cohort id") if payload.get("cohortId") else None,
            "institutionId": _clean_id(payload.get("institutionId"), "institution id"),
            "principalId": _clean_id(payload.get("principalId"), "principal id"),
            "workspaceId": _clean_id(payload.get("workspaceId"), "workspace id"),
            "stage": ONBOARDING_STAGES[0],
            "stageIndex": 0,
            "status": "in-progress",
            "completedItems": [],
            "notes": _clean_text(payload.get("notes", ""), "Notes", 4000, False),
            "createdAt": _now(),
            "updatedAt": _now(),
        }
        record_hash = _sha(record)
        with self._lock, self._connect() as db:
            try:
                db.execute("INSERT INTO onboarding_records VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (record_id, record["cohortId"], record["institutionId"], record["principalId"], record["workspaceId"], record["stage"], 0, record["status"], record["createdAt"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash))
            except sqlite3.IntegrityError as exc:
                raise BetaPlatformError("Onboarding id already exists.", 409) from exc
            event = self._event(db, "beta.onboarding.started", actor, "onboarding", record_id, {"recordHash": record_hash})
        return {"ok": True, "onboarding": {**record, "recordHash": record_hash}, "event": event}

    def advance_onboarding(self, record_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(record_id, "onboarding id")
        with self._lock, self._connect() as db:
            row = db.execute("SELECT payload_json FROM onboarding_records WHERE id=?", (record_id,)).fetchone()
            if not row:
                raise BetaPlatformError("Onboarding record not found.", 404)
            record = json.loads(row["payload_json"])
            current = int(record["stageIndex"])
            requested = payload.get("stage")
            next_index = current + 1 if requested is None else ONBOARDING_STAGES.index(_clean_id(requested, "onboarding stage")) if _clean_id(requested, "onboarding stage") in ONBOARDING_STAGES else -1
            if next_index != current + 1 or next_index >= len(ONBOARDING_STAGES):
                raise BetaPlatformError("Onboarding must advance exactly one stage at a time.", 409)
            record["stageIndex"] = next_index
            record["stage"] = ONBOARDING_STAGES[next_index]
            record["status"] = "complete" if record["stage"] == "complete" else "in-progress"
            completed = list(record.get("completedItems") or [])
            for item in payload.get("completedItems") or []:
                text = _clean_text(item, "Completed item", 300)
                if text not in completed:
                    completed.append(text)
            record["completedItems"] = completed[:200]
            if "notes" in payload:
                record["notes"] = _clean_text(payload.get("notes"), "Notes", 4000, False)
            record["updatedAt"] = _now()
            record_hash = _sha(record)
            db.execute("UPDATE onboarding_records SET stage=?,stage_index=?,status=?,updated_at=?,payload_json=?,record_hash=? WHERE id=?", (record["stage"], next_index, record["status"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash, record_id))
            event = self._event(db, "beta.onboarding.advanced", actor, "onboarding", record_id, {"stage": record["stage"], "recordHash": record_hash})
        return {"ok": True, "onboarding": {**record, "recordHash": record_hash}, "event": event}

    def list_onboarding(self, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT payload_json,record_hash FROM onboarding_records ORDER BY updated_at DESC LIMIT ?", (max(1, min(int(limit), 2000)),)).fetchall()
        return {"ok": True, "onboarding": [{**json.loads(row["payload_json"]), "recordHash": row["record_hash"]} for row in rows]}

    def create_project(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        self._ensure_capacity("guided_projects")
        project_id = _clean_id(payload.get("id") or f"beta-project-{uuid.uuid4().hex[:12]}", "project id")
        template_id = _clean_id(payload.get("templateId"), "template id")
        if template_id not in PROJECT_TEMPLATES:
            raise BetaPlatformError("Unknown guided project template.", 404)
        record = {
            "id": project_id,
            "templateId": template_id,
            "title": _clean_text(payload.get("title"), "Project title", 300),
            "cohortId": _clean_id(payload["cohortId"], "cohort id") if payload.get("cohortId") else None,
            "workspaceId": _clean_id(payload.get("workspaceId"), "workspace id"),
            "owner": _clean_text(payload.get("owner") or actor, "Project owner", 240),
            "stage": PROJECT_STAGES[0],
            "stageIndex": 0,
            "status": "active",
            "researchQuestion": _clean_text(payload.get("researchQuestion", ""), "Research question", 3000, False),
            "outputs": {},
            "handoffs": [],
            "createdAt": _now(),
            "updatedAt": _now(),
        }
        record_hash = _sha(record)
        with self._lock, self._connect() as db:
            try:
                db.execute("INSERT INTO guided_projects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (project_id, template_id, record["title"], record["cohortId"], record["workspaceId"], record["owner"], record["stage"], 0, record["status"], record["createdAt"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash))
            except sqlite3.IntegrityError as exc:
                raise BetaPlatformError("Project id already exists.", 409) from exc
            event = self._event(db, "beta.project.created", actor, "project", project_id, {"templateId": template_id, "recordHash": record_hash})
        return {"ok": True, "project": {**record, "recordHash": record_hash}, "event": event}

    def advance_project(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        project_id = _clean_id(project_id, "project id")
        with self._lock, self._connect() as db:
            row = db.execute("SELECT payload_json FROM guided_projects WHERE id=?", (project_id,)).fetchone()
            if not row:
                raise BetaPlatformError("Guided project not found.", 404)
            record = json.loads(row["payload_json"])
            current = int(record["stageIndex"])
            requested = payload.get("stage")
            if requested is None:
                next_index = current + 1
            else:
                stage = _clean_id(requested, "project stage")
                next_index = PROJECT_STAGES.index(stage) if stage in PROJECT_STAGES else -1
            if next_index != current + 1 or next_index >= len(PROJECT_STAGES):
                raise BetaPlatformError("Guided projects must advance exactly one stage at a time.", 409)
            outputs = dict(record.get("outputs") or {})
            for key, value in (payload.get("outputs") or {}).items():
                outputs[_clean_id(key, "output key")] = value
            handoffs = list(record.get("handoffs") or [])
            for handoff in payload.get("handoffs") or []:
                _reject_sensitive(handoff)
                handoffs.append(handoff)
            record["outputs"] = outputs
            record["handoffs"] = handoffs[:200]
            record["stageIndex"] = next_index
            record["stage"] = PROJECT_STAGES[next_index]
            record["status"] = "complete" if record["stage"] == "complete" else "active"
            record["updatedAt"] = _now()
            record_hash = _sha(record)
            db.execute("UPDATE guided_projects SET stage=?,stage_index=?,status=?,updated_at=?,payload_json=?,record_hash=? WHERE id=?", (record["stage"], next_index, record["status"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash, project_id))
            event = self._event(db, "beta.project.advanced", actor, "project", project_id, {"stage": record["stage"], "recordHash": record_hash})
        return {"ok": True, "project": {**record, "recordHash": record_hash}, "event": event}

    def list_projects(self, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT payload_json,record_hash FROM guided_projects ORDER BY updated_at DESC LIMIT ?", (max(1, min(int(limit), 2000)),)).fetchall()
        return {"ok": True, "projects": [{**json.loads(row["payload_json"]), "recordHash": row["record_hash"]} for row in rows]}

    def get_project(self, project_id: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project id")
        with self._connect() as db:
            row = db.execute("SELECT payload_json,record_hash FROM guided_projects WHERE id=?", (project_id,)).fetchone()
        if not row:
            raise BetaPlatformError("Guided project not found.", 404)
        return {"ok": True, "project": {**json.loads(row["payload_json"]), "recordHash": row["record_hash"]}}

    def record_telemetry(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        if not self.telemetry_enabled:
            raise BetaPlatformError("Beta telemetry is disabled.", 503)
        if payload.get("optIn") is not True:
            raise BetaPlatformError("Explicit telemetry opt-in is required.", 403)
        _reject_sensitive(payload)
        self._ensure_capacity("telemetry_events")
        event_id = _clean_id(payload.get("id") or f"telemetry-{uuid.uuid4().hex[:12]}", "telemetry event id")
        event_type = _clean_id(payload.get("eventType"), "telemetry event type")
        properties = payload.get("properties") or {}
        if not isinstance(properties, dict):
            raise BetaPlatformError("Telemetry properties must be an object.")
        actor_hash = hashlib.sha256(("actor:" + str(actor)).encode()).hexdigest()
        workspace_hash = hashlib.sha256(("workspace:" + str(payload.get("workspaceId") or "none")).encode()).hexdigest()
        event = {
            "id": event_id,
            "eventType": event_type,
            "occurredAt": str(payload.get("occurredAt") or _now()),
            "actorHash": actor_hash,
            "workspaceHash": workspace_hash,
            "properties": properties,
            "researchPayloadStored": False,
            "rawIdentifiersStored": False,
        }
        event_hash = _sha(event)
        with self._lock, self._connect() as db:
            try:
                db.execute("INSERT INTO telemetry_events VALUES(?,?,?,?,?,?,?)", (event_id, event_type, event["occurredAt"], actor_hash, workspace_hash, json.dumps(properties, sort_keys=True), event_hash))
            except sqlite3.IntegrityError as exc:
                existing = db.execute("SELECT event_hash FROM telemetry_events WHERE id=?", (event_id,)).fetchone()
                if existing and existing[0] == event_hash:
                    return {"ok": True, "idempotent": True, "telemetryEvent": {**event, "eventHash": event_hash}}
                raise BetaPlatformError("Telemetry event id already exists with different content.", 409) from exc
        return {"ok": True, "idempotent": False, "telemetryEvent": {**event, "eventHash": event_hash}}

    def telemetry_summary(self) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT event_type,COUNT(*) AS total FROM telemetry_events GROUP BY event_type ORDER BY total DESC,event_type").fetchall()
            total = db.execute("SELECT COUNT(*) FROM telemetry_events").fetchone()[0]
        return {"ok": True, "enabled": self.telemetry_enabled, "total": total, "events": [{"eventType": row["event_type"], "count": row["total"]} for row in rows], "rawIdentifiersStored": False, "researchPayloadsStored": False}

    def _create_issue(self, table: str, kind: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        self._ensure_capacity(table)
        issue_id = _clean_id(payload.get("id") or f"{kind}-{uuid.uuid4().hex[:12]}", f"{kind} id")
        severity = _clean_id(payload.get("severity", "medium"), "severity")
        if severity not in {"low", "medium", "high", "critical"}:
            raise BetaPlatformError("Unsupported severity.")
        category = _clean_id(payload.get("category", "other"), "category") if table == "beta_feedback" else None
        record = {
            "id": issue_id,
            "category": category,
            "severity": severity,
            "status": _clean_id(payload.get("status", "open"), "status"),
            "title": _clean_text(payload.get("title"), "Title", 300),
            "description": _clean_text(payload.get("description") or payload.get("summary"), "Description", 12000),
            "projectId": _clean_id(payload["projectId"], "project id") if payload.get("projectId") else None,
            "workspaceId": _clean_id(payload["workspaceId"], "workspace id") if payload.get("workspaceId") else None,
            "workaround": _clean_text(payload.get("workaround", ""), "Workaround", 6000, False),
            "targetRelease": _clean_text(payload.get("targetRelease", ""), "Target release", 100, False),
            "owner": _clean_text(payload.get("owner", ""), "Owner", 240, False),
            "reporterHash": hashlib.sha256(("reporter:" + actor).encode()).hexdigest(),
            "createdAt": _now(),
            "updatedAt": _now(),
        }
        record_hash = _sha(record)
        if table == "beta_feedback":
            values = (issue_id, category, severity, record["status"], record["title"], record["createdAt"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash)
        else:
            values = (issue_id, severity, record["status"], record["title"], record["createdAt"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash)
        placeholders = ",".join("?" for _ in values)
        with self._lock, self._connect() as db:
            try:
                db.execute(f"INSERT INTO {table} VALUES({placeholders})", values)
            except sqlite3.IntegrityError as exc:
                raise BetaPlatformError(f"{kind.replace('-', ' ').title()} id already exists.", 409) from exc
            event = self._event(db, f"beta.{kind}.created", actor, kind, issue_id, {"severity": severity, "recordHash": record_hash})
        return {"ok": True, kind.replace("-", "_"): {**record, "recordHash": record_hash}, "event": event}

    def _list_issues(self, table: str, response_key: str, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute(f"SELECT payload_json,record_hash FROM {table} ORDER BY updated_at DESC LIMIT ?", (max(1, min(int(limit), 2000)),)).fetchall()
        return {"ok": True, response_key: [{**json.loads(row["payload_json"]), "recordHash": row["record_hash"]} for row in rows]}

    def _update_issue(self, table: str, kind: str, issue_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        issue_id = _clean_id(issue_id, f"{kind} id")
        with self._lock, self._connect() as db:
            row = db.execute(f"SELECT payload_json FROM {table} WHERE id=?", (issue_id,)).fetchone()
            if not row:
                raise BetaPlatformError(f"{kind.replace('-', ' ').title()} not found.", 404)
            record = json.loads(row["payload_json"])
            for field in ("status", "owner", "workaround", "targetRelease"):
                if field in payload:
                    if field == "status":
                        record[field] = _clean_id(payload[field], "status")
                    else:
                        record[field] = _clean_text(payload[field], field, 6000, False)
            if "resolution" in payload:
                record["resolution"] = _clean_text(payload["resolution"], "Resolution", 12000, False)
            record["updatedAt"] = _now()
            record_hash = _sha(record)
            db.execute(f"UPDATE {table} SET status=?,updated_at=?,payload_json=?,record_hash=? WHERE id=?", (record["status"], record["updatedAt"], json.dumps(record, sort_keys=True), record_hash, issue_id))
            event = self._event(db, f"beta.{kind}.updated", actor, kind, issue_id, {"status": record["status"], "recordHash": record_hash})
        return {"ok": True, kind.replace("-", "_"): {**record, "recordHash": record_hash}, "event": event}

    def create_feedback(self, payload: dict[str, Any], actor: str) -> dict[str, Any]: return self._create_issue("beta_feedback", "feedback", payload, actor)
    def list_feedback(self, limit: int = 200) -> dict[str, Any]: return self._list_issues("beta_feedback", "feedback", limit)
    def update_feedback(self, issue_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]: return self._update_issue("beta_feedback", "feedback", issue_id, payload, actor)
    def create_limitation(self, payload: dict[str, Any], actor: str) -> dict[str, Any]: return self._create_issue("known_limitations", "limitation", payload, actor)
    def list_limitations(self, limit: int = 200) -> dict[str, Any]: return self._list_issues("known_limitations", "limitations", limit)
    def update_limitation(self, issue_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]: return self._update_issue("known_limitations", "limitation", issue_id, payload, actor)
    def create_support_case(self, payload: dict[str, Any], actor: str) -> dict[str, Any]: return self._create_issue("support_cases", "support-case", payload, actor)
    def list_support_cases(self, limit: int = 200) -> dict[str, Any]: return self._list_issues("support_cases", "supportCases", limit)
    def update_support_case(self, issue_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]: return self._update_issue("support_cases", "support-case", issue_id, payload, actor)

    def evaluate_readiness(self, payload: dict[str, Any], actor: str, component_snapshot: dict[str, Any]) -> dict[str, Any]:
        _reject_sensitive(payload)
        report_id = _clean_id(payload.get("id") or f"beta-readiness-{uuid.uuid4().hex[:12]}", "readiness report id")
        required = ["interoperability", "typedHandoffs", "publicIntegrations", "governance", "securityPrivacy", "recovery", "performanceValidation"]
        component_checks = []
        blockers = []
        for component in required:
            health = component_snapshot.get(component) or {}
            ok = bool(health.get("ok")) and str(health.get("status", "ready")) not in {"degraded", "error", "offline", "incomplete"}
            component_checks.append({"id": component, "ok": ok, "status": health.get("status", "unknown"), "version": health.get("serviceVersion") or health.get("version")})
            if not ok:
                blockers.append({"type": "component", "id": component, "detail": f"{component} is not ready"})
        with self._connect() as db:
            critical_feedback = db.execute("SELECT COUNT(*) FROM beta_feedback WHERE severity='critical' AND status NOT IN ('resolved','closed')").fetchone()[0]
            critical_limitations = db.execute("SELECT COUNT(*) FROM known_limitations WHERE severity='critical' AND status NOT IN ('resolved','closed')").fetchone()[0]
            critical_support = db.execute("SELECT COUNT(*) FROM support_cases WHERE severity='critical' AND status NOT IN ('resolved','closed')").fetchone()[0]
            active_cohorts = db.execute("SELECT COUNT(*) FROM beta_cohorts WHERE status='active'").fetchone()[0]
        for issue_type, total in (("critical-feedback", critical_feedback), ("critical-limitation", critical_limitations), ("critical-support", critical_support)):
            if total:
                blockers.append({"type": issue_type, "count": total})
        report = {
            "id": report_id,
            "releaseVersion": VERSION,
            "releaseStage": "beta",
            "createdAt": _now(),
            "createdBy": actor,
            "status": "ready" if not blockers else "blocked",
            "componentChecks": component_checks,
            "blockers": blockers,
            "activeCohorts": active_cohorts,
            "criticalOpenItems": critical_feedback + critical_limitations + critical_support,
            "generalAvailabilityClaim": False,
            "recommendation": "Proceed with controlled institutional beta" if not blockers else "Resolve blockers before expanding beta access",
        }
        report_hash = _sha(report)
        with self._lock, self._connect() as db:
            try:
                db.execute("INSERT INTO readiness_reports VALUES(?,?,?,?,?)", (report_id, report["status"], report["createdAt"], json.dumps(report, sort_keys=True), report_hash))
            except sqlite3.IntegrityError as exc:
                raise BetaPlatformError("Readiness report id already exists.", 409) from exc
            event = self._event(db, "beta.readiness.evaluated", actor, "readiness-report", report_id, {"status": report["status"], "reportHash": report_hash})
        return {"ok": True, "report": {**report, "reportHash": report_hash}, "event": event}

    def list_readiness_reports(self, limit: int = 100) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT report_json,report_hash FROM readiness_reports ORDER BY created_at DESC LIMIT ?", (max(1, min(int(limit), 1000)),)).fetchall()
        return {"ok": True, "reports": [{**json.loads(row["report_json"]), "reportHash": row["report_hash"]} for row in rows]}

    def timeline(self, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM beta_events ORDER BY seq DESC LIMIT ?", (max(1, min(int(limit), 5000)),)).fetchall()
        events = []
        for row in rows:
            events.append({"sequence": row["seq"], "eventType": row["event_type"], "actor": row["actor"], "subjectType": row["subject_type"], "subjectId": row["subject_id"], "occurredAt": row["occurred_at"], "payload": json.loads(row["payload_json"]), "previousHash": row["previous_hash"], "eventHash": row["event_hash"]})
        return {"ok": True, "events": events}

    def verify_timeline(self) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM beta_events ORDER BY seq ASC").fetchall()
        previous = "0" * 64
        for row in rows:
            event = {"eventType": row["event_type"], "actor": row["actor"], "subjectType": row["subject_type"], "subjectId": row["subject_id"], "occurredAt": row["occurred_at"], "payload": json.loads(row["payload_json"]), "previousHash": row["previous_hash"]}
            if row["previous_hash"] != previous or _sha(event) != row["event_hash"]:
                return {"ok": False, "valid": False, "failedSequence": row["seq"]}
            previous = row["event_hash"]
        return {"ok": True, "valid": True, "eventsVerified": len(rows), "headHash": previous}

    def dashboard(self) -> dict[str, Any]:
        with self._connect() as db:
            counts = {
                "cohorts": db.execute("SELECT COUNT(*) FROM beta_cohorts").fetchone()[0],
                "activeCohorts": db.execute("SELECT COUNT(*) FROM beta_cohorts WHERE status='active'").fetchone()[0],
                "onboarding": db.execute("SELECT COUNT(*) FROM onboarding_records").fetchone()[0],
                "completedOnboarding": db.execute("SELECT COUNT(*) FROM onboarding_records WHERE status='complete'").fetchone()[0],
                "projects": db.execute("SELECT COUNT(*) FROM guided_projects").fetchone()[0],
                "completedProjects": db.execute("SELECT COUNT(*) FROM guided_projects WHERE status='complete'").fetchone()[0],
                "telemetryEvents": db.execute("SELECT COUNT(*) FROM telemetry_events").fetchone()[0],
                "openFeedback": db.execute("SELECT COUNT(*) FROM beta_feedback WHERE status NOT IN ('resolved','closed')").fetchone()[0],
                "openLimitations": db.execute("SELECT COUNT(*) FROM known_limitations WHERE status NOT IN ('resolved','closed')").fetchone()[0],
                "openSupportCases": db.execute("SELECT COUNT(*) FROM support_cases WHERE status NOT IN ('resolved','closed')").fetchone()[0],
                "readinessReports": db.execute("SELECT COUNT(*) FROM readiness_reports").fetchone()[0],
            }
            latest = db.execute("SELECT report_json,report_hash FROM readiness_reports ORDER BY created_at DESC LIMIT 1").fetchone()
        return {"ok": True, "version": VERSION, "releaseStage": "beta", "counts": counts, "latestReadiness": ({**json.loads(latest["report_json"]), "reportHash": latest["report_hash"]} if latest else None), "telemetryEnabled": self.telemetry_enabled, "generalAvailabilityClaim": False}
