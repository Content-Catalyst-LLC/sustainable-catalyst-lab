from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.0.0"
RELEASE_STAGE = "general-availability"
SUPPORTED_UPGRADE_BASELINES = (
    "0.31.0", "0.31.1", "0.38.0", "0.38.1", "0.38.2", "0.39.0",
    "0.39.1", "0.39.2", "0.39.3", "0.40.0", "0.40.1", "0.40.2",
)
REQUIRED_GA_EVIDENCE = (
    "stableContracts", "upgradePath", "cleanInstall", "backupRestore",
    "identityGovernance", "securityPrivacy", "loadResilience", "accessibility",
    "monitoring", "apiSdkDocumentation", "crossProductHandoffs",
    "supportLifecycle", "incidentReadiness", "licensing", "reproducibleArchives",
)
REQUIRED_INCIDENT_CHECKS = (
    "incident-owner", "severity-model", "communications-path", "rollback-path",
    "backup-restore-path", "audit-preservation", "support-intake", "post-incident-review",
)
VALID_SUPPORT_STATES = {"supported", "maintenance", "security-only", "end-of-life"}


class ConnectedPlatformError(ValueError):
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
        raise ConnectedPlatformError(f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 8000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ConnectedPlatformError(f"{label} is required.")
    if len(text) > maximum:
        raise ConnectedPlatformError(f"{label} exceeds {maximum} characters.")
    return text


def _reject_sensitive(value: Any, path: str = "payload", depth: int = 0) -> None:
    if depth > 20:
        raise ConnectedPlatformError("Payload nesting exceeds the stable-platform boundary.")
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"(?<!^)(?=[A-Z])", "_", str(key)).lower().replace("-", "_")
            if any(part in normalized for part in (
                "password", "secret", "credential", "private_key", "access_token",
                "refresh_token", "authorization", "cookie", "raw_data", "dataset_bytes",
                "executable", "callback", "script",
            )):
                raise ConnectedPlatformError(f"Sensitive or executable field is not permitted: {path}.{key}")
            _reject_sensitive(child, f"{path}.{key}", depth + 1)
    elif isinstance(value, list):
        if len(value) > 10000:
            raise ConnectedPlatformError("Payload contains too many list items.")
        for index, child in enumerate(value):
            _reject_sensitive(child, f"{path}[{index}]", depth + 1)
    elif isinstance(value, str):
        lowered = value.lower()
        if "-----begin private key-----" in lowered or "<script" in lowered or "javascript:" in lowered:
            raise ConnectedPlatformError("Executable or private-key material is not permitted.")
        if len(value) > 250000:
            raise ConnectedPlatformError("Payload text exceeds the stable-platform boundary.")


def policies(persistent_disk_mounted: bool) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "releaseStage": RELEASE_STAGE,
        "persistentDiskMounted": bool(persistent_disk_mounted),
        "semanticVersioning": True,
        "stablePublicContracts": True,
        "forcePushPermitted": False,
        "productionFilesMayBeOverwrittenByApi": False,
        "supportedUpgradeBaselines": list(SUPPORTED_UPGRADE_BASELINES),
        "requiredGeneralAvailabilityEvidence": list(REQUIRED_GA_EVIDENCE),
        "requiredIncidentChecks": list(REQUIRED_INCIDENT_CHECKS),
        "capabilities": {
            "contractRegistry": True,
            "supportLifecycle": True,
            "upgradeCertification": True,
            "productionAttestation": True,
            "incidentReadiness": True,
            "generalAvailabilityCertification": True,
        },
    }


class ConnectedScientificPlatform:
    TABLES = {
        "contracts": "stable_contracts",
        "support-lifecycles": "support_lifecycles",
        "upgrade-certifications": "upgrade_certifications",
        "production-attestations": "production_attestations",
        "incident-readiness": "incident_readiness",
        "ga-certifications": "ga_certifications",
    }

    def __init__(self, db_path: str, persistent_disk_mounted: bool, history_limit: int = 250000) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.history_limit = max(100, int(history_limit))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS stable_contracts(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,record_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS support_lifecycles(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,record_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS upgrade_certifications(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,record_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS production_attestations(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,record_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS incident_readiness(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,record_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS ga_certifications(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,record_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS stable_platform_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,actor TEXT NOT NULL,subject_type TEXT NOT NULL,subject_id TEXT NOT NULL,occurred_at TEXT NOT NULL,payload_json TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL);
                """
            )

    def _event(self, db, event_type: str, actor: str, subject_type: str, subject_id: str, payload: dict[str, Any]) -> None:
        row = db.execute("SELECT event_hash FROM stable_platform_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = str(row["event_hash"]) if row else ""
        occurred = _now()
        envelope = {
            "eventType": event_type,
            "actor": actor,
            "subjectType": subject_type,
            "subjectId": subject_id,
            "occurredAt": occurred,
            "payload": payload,
            "previousHash": previous,
        }
        event_hash = _sha(envelope)
        db.execute(
            "INSERT INTO stable_platform_events(event_type,actor,subject_type,subject_id,occurred_at,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (event_type, actor, subject_type, subject_id, occurred, json.dumps(payload, sort_keys=True), previous, event_hash),
        )
        db.execute(
            "DELETE FROM stable_platform_events WHERE seq NOT IN (SELECT seq FROM stable_platform_events ORDER BY seq DESC LIMIT ?)",
            (self.history_limit,),
        )

    def _store(self, table: str, record: dict[str, Any], actor: str, status: str, event_type: str) -> dict[str, Any]:
        record = dict(record)
        record_hash = _sha(record)
        record["recordHash"] = record_hash
        with self._lock, self._connect() as db:
            db.execute(
                f"INSERT INTO {table}(id,created_at,actor,status,payload_json,record_hash) VALUES(?,?,?,?,?,?)",
                (record["id"], record["createdAt"], actor, status, json.dumps(record, sort_keys=True), record_hash),
            )
            self._event(db, event_type, actor, table, record["id"], {"status": status, "recordHash": record_hash})
        return record

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "status": "stable-platform-ready",
            "serviceVersion": VERSION,
            "releaseStage": RELEASE_STAGE,
            "persistentDiskMounted": self.persistent_disk_mounted,
            "stablePublicContracts": True,
            "generalAvailability": True,
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "recordKinds": sorted(self.TABLES),
            "supportStates": sorted(VALID_SUPPORT_STATES),
            "requiredEvidence": list(REQUIRED_GA_EVIDENCE),
            "requiredIncidentChecks": list(REQUIRED_INCIDENT_CHECKS),
        }

    def list_records(self, kind: str, limit: int = 200) -> dict[str, Any]:
        table = self.TABLES.get(kind)
        if not table:
            raise ConnectedPlatformError("Unknown stable-platform record kind.", 404)
        with self._connect() as db:
            rows = db.execute(
                f"SELECT payload_json FROM {table} ORDER BY created_at DESC LIMIT ?",
                (max(1, min(int(limit), 5000)),),
            ).fetchall()
        return {"ok": True, "kind": kind, "records": [json.loads(row["payload_json"]) for row in rows]}

    def register_contract(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(payload.get("id") or f"contract-{uuid.uuid4().hex[:12]}", "contract id")
        status = str(payload.get("status", "stable")).strip().lower()
        if status not in {"stable", "deprecated", "retired"}:
            raise ConnectedPlatformError("Invalid contract status.")
        versions = payload.get("versions") or []
        if not isinstance(versions, list) or not versions:
            raise ConnectedPlatformError("versions must be a non-empty list.")
        record = {
            "id": record_id,
            "schema": "sc-lab-stable-contract/1.0.0",
            "createdAt": _now(),
            "releaseVersion": VERSION,
            "name": _clean_text(payload.get("name"), "name", 500),
            "status": status,
            "versions": [str(value)[:80] for value in versions],
            "compatibilityPolicy": _clean_text(payload.get("compatibilityPolicy", "semantic-versioning"), "compatibilityPolicy", 2000),
            "breakingChangesRequireMajorVersion": True,
        }
        return {"ok": True, "contract": self._store("stable_contracts", record, actor, status, "stable-contract.registered")}

    def declare_support_lifecycle(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(payload.get("id") or f"support-{uuid.uuid4().hex[:12]}", "support lifecycle id")
        state = str(payload.get("status", "supported")).strip().lower()
        if state not in VALID_SUPPORT_STATES:
            raise ConnectedPlatformError("Invalid support lifecycle status.")
        record = {
            "id": record_id,
            "schema": "sc-lab-support-lifecycle/1.0.0",
            "createdAt": _now(),
            "releaseVersion": str(payload.get("releaseVersion", VERSION)).strip(),
            "status": state,
            "supportStart": _clean_text(payload.get("supportStart"), "supportStart", 100),
            "maintenanceEnd": _clean_text(payload.get("maintenanceEnd"), "maintenanceEnd", 100, False),
            "securityEnd": _clean_text(payload.get("securityEnd"), "securityEnd", 100, False),
            "migrationGuidance": _clean_text(payload.get("migrationGuidance"), "migrationGuidance", 6000, False),
        }
        return {"ok": True, "lifecycle": self._store("support_lifecycles", record, actor, state, "support-lifecycle.declared")}

    def certify_upgrade(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(payload.get("id") or f"upgrade-{uuid.uuid4().hex[:12]}", "upgrade certification id")
        baseline = str(payload.get("baselineVersion", "")).strip()
        blockers: list[str] = []
        if baseline not in SUPPORTED_UPGRADE_BASELINES:
            blockers.append("unsupported-baseline")
        for field, label in (
            ("backupVerified", "backup-not-verified"),
            ("rollbackVerified", "rollback-not-verified"),
            ("migrationPassed", "migration-not-passed"),
            ("packageParityVerified", "package-parity-not-verified"),
        ):
            if not bool(payload.get(field, False)):
                blockers.append(label)
        record = {
            "id": record_id,
            "schema": "sc-lab-upgrade-certification/1.0.0",
            "createdAt": _now(),
            "baselineVersion": baseline,
            "targetVersion": VERSION,
            "backupVerified": bool(payload.get("backupVerified", False)),
            "rollbackVerified": bool(payload.get("rollbackVerified", False)),
            "migrationPassed": bool(payload.get("migrationPassed", False)),
            "packageParityVerified": bool(payload.get("packageParityVerified", False)),
            "blockers": blockers,
            "forcePushRequired": False,
        }
        status = "certified" if not blockers else "blocked"
        record["status"] = status
        return {"ok": True, "certification": self._store("upgrade_certifications", record, actor, status, "upgrade.certified")}

    def attest_production_readiness(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(payload.get("id") or f"production-{uuid.uuid4().hex[:12]}", "production attestation id")
        components = payload.get("components") or {}
        if not isinstance(components, dict) or not components:
            raise ConnectedPlatformError("components must be a non-empty object.")
        normalized: dict[str, Any] = {}
        blockers: list[str] = []
        for key, value in components.items():
            component_id = _clean_id(key, "component id")
            state = str(value.get("status", "unknown") if isinstance(value, dict) else value).strip().lower()
            normalized[component_id] = {"status": state}
            if state not in {"pass", "ready", "healthy", "verified", "supported"}:
                blockers.append(component_id)
        monitoring_enabled = bool(payload.get("monitoringEnabled", False))
        persistent_storage_verified = bool(payload.get("persistentStorageVerified", False))
        if not monitoring_enabled:
            blockers.append("monitoring-not-enabled")
        if not persistent_storage_verified:
            blockers.append("persistent-storage-not-verified")
        blockers = sorted(set(blockers))
        record = {
            "id": record_id,
            "schema": "sc-lab-production-readiness-attestation/1.0.0",
            "createdAt": _now(),
            "releaseVersion": VERSION,
            "components": normalized,
            "monitoringEnabled": monitoring_enabled,
            "persistentStorageVerified": persistent_storage_verified,
            "blockers": blockers,
        }
        status = "production-ready" if not blockers else "blocked"
        record["status"] = status
        return {"ok": True, "attestation": self._store("production_attestations", record, actor, status, "production-readiness.attested")}

    def attest_incident_readiness(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(payload.get("id") or f"incident-{uuid.uuid4().hex[:12]}", "incident readiness id")
        checks = payload.get("checks") or []
        if not isinstance(checks, list):
            raise ConnectedPlatformError("checks must be a list.")
        seen: dict[str, str] = {}
        for item in checks:
            if isinstance(item, dict):
                seen[_clean_id(item.get("id"), "incident check id")] = str(item.get("status", "")).strip().lower()
        missing = [item for item in REQUIRED_INCIDENT_CHECKS if item not in seen]
        failed = [key for key, value in seen.items() if value not in {"pass", "ready", "verified", "complete"}]
        blockers = sorted(set(missing + failed))
        record = {
            "id": record_id,
            "schema": "sc-lab-incident-readiness/1.0.0",
            "createdAt": _now(),
            "releaseVersion": VERSION,
            "checks": [{"id": key, "status": value} for key, value in sorted(seen.items())],
            "blockers": blockers,
        }
        status = "ready" if not blockers else "blocked"
        record["status"] = status
        return {"ok": True, "attestation": self._store("incident_readiness", record, actor, status, "incident-readiness.attested")}

    def certify_general_availability(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        record_id = _clean_id(payload.get("id") or f"ga-{uuid.uuid4().hex[:12]}", "general availability certification id")
        evidence = payload.get("evidence") or {}
        if not isinstance(evidence, dict):
            raise ConnectedPlatformError("evidence must be an object.")
        normalized: dict[str, Any] = {}
        blockers: list[str] = []
        for key in REQUIRED_GA_EVIDENCE:
            value = evidence.get(key)
            state = str(value.get("status", "missing") if isinstance(value, dict) else ("pass" if value is True else value or "missing")).strip().lower()
            normalized[key] = {"status": state}
            if state not in {"pass", "passed", "ready", "verified", "complete", "supported", "healthy", "certified"}:
                blockers.append(key)
        critical = [str(value)[:500] for value in (payload.get("criticalDefects") or [])]
        high = [str(value)[:500] for value in (payload.get("highDefects") or [])]
        if critical:
            blockers.append("critical-defects")
        if high:
            blockers.append("high-defects")
        blockers = sorted(set(blockers))
        record = {
            "id": record_id,
            "schema": "sc-lab-general-availability-certification/1.0.0",
            "createdAt": _now(),
            "releaseVersion": VERSION,
            "releaseStage": RELEASE_STAGE,
            "evidence": normalized,
            "criticalDefects": critical,
            "highDefects": high,
            "blockers": blockers,
            "stablePublicContracts": True,
            "generalAvailabilityClaim": not blockers,
        }
        status = "general-availability-certified" if not blockers else "blocked"
        record["status"] = status
        return {"ok": True, "certification": self._store("ga_certifications", record, actor, status, "general-availability.certified")}

    def verify_timeline(self) -> dict[str, Any]:
        previous = ""
        with self._connect() as db:
            rows = db.execute("SELECT * FROM stable_platform_events ORDER BY seq").fetchall()
        for row in rows:
            payload = json.loads(row["payload_json"])
            envelope = {
                "eventType": row["event_type"],
                "actor": row["actor"],
                "subjectType": row["subject_type"],
                "subjectId": row["subject_id"],
                "occurredAt": row["occurred_at"],
                "payload": payload,
                "previousHash": row["previous_hash"],
            }
            if row["previous_hash"] != previous or _sha(envelope) != row["event_hash"]:
                return {"ok": False, "valid": False, "failedSequence": row["seq"]}
            previous = row["event_hash"]
        return {"ok": True, "valid": True, "events": len(rows), "headHash": previous}

    def dashboard(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        with self._connect() as db:
            for kind, table in self.TABLES.items():
                counts[kind] = int(db.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])
            ga_count = int(db.execute("SELECT COUNT(*) AS n FROM ga_certifications WHERE status='general-availability-certified'").fetchone()["n"])
        return {
            "ok": True,
            "version": VERSION,
            "releaseStage": RELEASE_STAGE,
            "counts": counts,
            "generalAvailabilityCertifications": ga_count,
            "timeline": self.verify_timeline(),
        }
