from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.40.1"


class InterfaceFinalizationError(ValueError):
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
        raise InterfaceFinalizationError(f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 4000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise InterfaceFinalizationError(f"{label} is required.")
    if len(text) > maximum:
        raise InterfaceFinalizationError(f"{label} exceeds {maximum} characters.")
    return text


SENSITIVE_KEYS = {
    "secret", "password", "passwd", "credential", "token", "api_key", "apikey",
    "private_key", "access_key", "refresh_token", "authorization", "cookie",
    "raw_data", "dataset_bytes", "binary", "blob", "content", "executable",
    "callback", "code", "html", "script",
}


def _reject_sensitive(value: Any, path: str = "payload", depth: int = 0) -> None:
    if depth > 20:
        raise InterfaceFinalizationError("Payload nesting exceeds the interface safety boundary.")
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            compact = normalized.replace("_", "")
            if normalized in SENSITIVE_KEYS or any(part in normalized for part in ("password", "secret", "private_key", "access_token")) or any(part in compact for part in ("password", "secret", "credential", "accesstoken", "refreshtoken", "privatekey", "apikey")):
                raise InterfaceFinalizationError(f"Sensitive or executable field is not permitted: {path}.{key}")
            _reject_sensitive(child, f"{path}.{key}", depth + 1)
    elif isinstance(value, list):
        if len(value) > 10000:
            raise InterfaceFinalizationError("Payload contains too many list items.")
        for index, child in enumerate(value):
            _reject_sensitive(child, f"{path}[{index}]", depth + 1)
    elif isinstance(value, str):
        lowered = value.lower()
        if "-----begin private key-----" in lowered or "<script" in lowered or "javascript:" in lowered:
            raise InterfaceFinalizationError("Executable or private-key material is not permitted.")
        if len(value) > 200000:
            raise InterfaceFinalizationError("Payload text exceeds the interface safety boundary.")


VIEWPORT_PROFILES = {
    "phone": {"width": 390, "height": 844},
    "tablet": {"width": 820, "height": 1180},
    "desktop": {"width": 1440, "height": 1000},
}
REQUIRED_CHECKS = (
    "no-horizontal-overflow", "touch-targets", "keyboard-navigation", "visible-focus",
    "accessible-names", "live-regions", "dialog-semantics", "table-alternatives",
    "visualization-alternatives", "reduced-motion", "forced-colors", "text-zoom",
)
ALLOWED_OPERATIONS = {"create", "update", "delete", "advance-stage", "save-draft", "attach-reference"}
ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential"}


def policies(persistent_disk_mounted: bool, offline_shell_enabled: bool, max_snapshot_assets: int, max_queue_records: int) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "releaseStage": "beta-interface-finalization",
        "persistentDiskMounted": bool(persistent_disk_mounted),
        "offlineShellEnabled": bool(offline_shell_enabled),
        "offlineShellOptInRequired": True,
        "restrictedDataMayBeCached": False,
        "rawResearchPayloadsStoredByBackend": False,
        "maxSnapshotAssets": int(max_snapshot_assets),
        "maxQueueRecords": int(max_queue_records),
        "viewportProfiles": VIEWPORT_PROFILES,
        "requiredChecks": list(REQUIRED_CHECKS),
        "capabilities": {
            "responsiveReadinessAudits": True,
            "accessibilityPreferenceProfiles": True,
            "browserLocalProjectSnapshots": True,
            "idempotentOfflineQueue": True,
            "explicitConflictReconciliation": True,
            "connectionStateCommunication": True,
            "optInOfflineShell": True,
        },
    }


class InterfaceFinalizationManager:
    def __init__(self, db_path: str, persistent_disk_mounted: bool, offline_shell_enabled: bool = True,
                 history_limit: int = 250000, max_snapshot_assets: int = 5000, max_queue_records: int = 100000) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.offline_shell_enabled = bool(offline_shell_enabled)
        self.history_limit = max(100, int(history_limit))
        self.max_snapshot_assets = max(1, int(max_snapshot_assets))
        self.max_queue_records = max(100, int(max_queue_records))
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
            CREATE TABLE IF NOT EXISTS interface_audits(
              id TEXT PRIMARY KEY, profile TEXT NOT NULL, status TEXT NOT NULL,
              score REAL NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL,
              payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS preference_profiles(
              id TEXT PRIMARY KEY, updated_at TEXT NOT NULL, actor TEXT NOT NULL,
              payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS offline_snapshots(
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL, workspace_id TEXT NOT NULL,
              classification TEXT NOT NULL, asset_count INTEGER NOT NULL,
              total_bytes INTEGER NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL,
              payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS offline_operations(
              id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
              workspace_id TEXT NOT NULL, project_id TEXT NOT NULL, operation TEXT NOT NULL,
              status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              actor TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reconciliation_receipts(
              id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL,
              applied_count INTEGER NOT NULL, conflict_count INTEGER NOT NULL,
              rejected_count INTEGER NOT NULL, payload_json TEXT NOT NULL, receipt_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS interface_events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
              actor TEXT NOT NULL, subject_type TEXT NOT NULL, subject_id TEXT NOT NULL,
              occurred_at TEXT NOT NULL, payload_json TEXT NOT NULL,
              previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
            );
            """)

    def _event(self, db: sqlite3.Connection, event_type: str, actor: str, subject_type: str, subject_id: str, payload: Any) -> None:
        row = db.execute("SELECT event_hash FROM interface_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = str(row["event_hash"]) if row else ""
        occurred = _now()
        envelope = {"eventType": event_type, "actor": actor, "subjectType": subject_type,
                    "subjectId": subject_id, "occurredAt": occurred, "payload": payload, "previousHash": previous}
        event_hash = _sha(envelope)
        db.execute("INSERT INTO interface_events(event_type,actor,subject_type,subject_id,occurred_at,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
                   (event_type, actor, subject_type, subject_id, occurred, json.dumps(payload, sort_keys=True), previous, event_hash))
        db.execute("DELETE FROM interface_events WHERE seq NOT IN (SELECT seq FROM interface_events ORDER BY seq DESC LIMIT ?)", (self.history_limit,))

    @staticmethod
    def _audit_row(row: sqlite3.Row) -> dict[str, Any]:
        value = json.loads(row["payload_json"]); value["recordHash"] = row["record_hash"]; return value

    def health(self) -> dict[str, Any]:
        dashboard = self.dashboard()
        return {"ok": True, "status": "ready", "version": VERSION, "serviceVersion": VERSION,
                "storage": "persistent" if self.persistent_disk_mounted else "instance-local",
                "offlineShellEnabled": self.offline_shell_enabled,
                "restrictedDataMayBeCached": False, "counts": dashboard["counts"]}

    def catalog(self) -> dict[str, Any]:
        return {"ok": True, "version": VERSION, "viewportProfiles": VIEWPORT_PROFILES,
                "requiredChecks": list(REQUIRED_CHECKS), "allowedOfflineOperations": sorted(ALLOWED_OPERATIONS),
                "allowedOfflineClassifications": sorted(ALLOWED_CLASSIFICATIONS)}

    def create_audit(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        audit_id = _clean_id(payload.get("id") or f"audit-{uuid.uuid4().hex}", "audit id")
        profile = _clean_id(payload.get("profile") or "desktop", "viewport profile")
        if profile not in VIEWPORT_PROFILES:
            raise InterfaceFinalizationError("Unknown viewport profile.")
        checks = payload.get("checks")
        if not isinstance(checks, list) or not checks:
            raise InterfaceFinalizationError("checks must be a non-empty array.")
        normalized: list[dict[str, Any]] = []
        seen = set()
        for item in checks[:200]:
            if not isinstance(item, dict):
                raise InterfaceFinalizationError("Each check must be an object.")
            check_id = _clean_id(item.get("id"), "check id")
            if check_id in seen: raise InterfaceFinalizationError("Duplicate check id.")
            seen.add(check_id)
            status = str(item.get("status") or "fail").strip().lower()
            if status not in {"pass", "fail", "warning", "not-applicable"}:
                raise InterfaceFinalizationError("Invalid check status.")
            normalized.append({"id": check_id, "status": status,
                               "count": max(0, int(item.get("count") or 0)),
                               "detail": _clean_text(item.get("detail"), "check detail", 1000, False)})
        by_id = {item["id"]: item for item in normalized}
        missing = [check for check in REQUIRED_CHECKS if check not in by_id]
        required = [by_id[c] for c in REQUIRED_CHECKS if c in by_id]
        passed = sum(1 for item in required if item["status"] in {"pass", "not-applicable"})
        score = round(100.0 * passed / len(REQUIRED_CHECKS), 2)
        failures = [item["id"] for item in required if item["status"] == "fail"]
        status = "ready" if not missing and not failures and score == 100.0 else "needs-attention"
        created = _now()
        record = {"id": audit_id, "schema": "sc-lab-interface-finalization-audit/0.40.1", "profile": profile,
                  "viewport": VIEWPORT_PROFILES[profile], "status": status, "score": score,
                  "missingChecks": missing, "failedChecks": failures, "checks": normalized,
                  "createdAt": created, "actor": _clean_text(actor, "actor", 180)}
        digest = _sha(record); record["recordHash"] = digest
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO interface_audits(id,profile,status,score,created_at,actor,payload_json,record_hash) VALUES(?,?,?,?,?,?,?,?)",
                       (audit_id, profile, status, score, created, record["actor"], json.dumps(record, sort_keys=True), digest))
            self._event(db, "interface.audit-created", record["actor"], "interface-audit", audit_id, {"profile": profile, "status": status, "score": score})
        return {"ok": True, "audit": record}

    def list_audits(self, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM interface_audits ORDER BY created_at DESC LIMIT ?", (max(1, min(int(limit), 2000)),)).fetchall()
        return {"ok": True, "audits": [self._audit_row(row) for row in rows]}

    def save_preferences(self, profile_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        profile_id = _clean_id(profile_id, "preference profile id")
        profile = {"id": profile_id, "schema": "sc-lab-accessibility-preferences/0.40.1",
                   "reducedMotion": bool(payload.get("reducedMotion", False)),
                   "increasedContrast": bool(payload.get("increasedContrast", False)),
                   "largeText": bool(payload.get("largeText", False)),
                   "dataSaver": bool(payload.get("dataSaver", False)),
                   "touchTargetMinimumPx": max(44, min(int(payload.get("touchTargetMinimumPx") or 44), 72)),
                   "updatedAt": _now(), "actor": _clean_text(actor, "actor", 180)}
        digest = _sha(profile); profile["recordHash"] = digest
        with self._lock, self._connect() as db:
            db.execute("INSERT OR REPLACE INTO preference_profiles(id,updated_at,actor,payload_json,record_hash) VALUES(?,?,?,?,?)",
                       (profile_id, profile["updatedAt"], profile["actor"], json.dumps(profile, sort_keys=True), digest))
            self._event(db, "preferences.saved", profile["actor"], "preference-profile", profile_id, {"recordHash": digest})
        return {"ok": True, "profile": profile}

    def get_preferences(self, profile_id: str) -> dict[str, Any]:
        profile_id = _clean_id(profile_id, "preference profile id")
        with self._connect() as db: row = db.execute("SELECT payload_json,record_hash FROM preference_profiles WHERE id=?", (profile_id,)).fetchone()
        if not row: raise InterfaceFinalizationError("Preference profile not found.", 404)
        value = json.loads(row["payload_json"]); value["recordHash"] = row["record_hash"]
        return {"ok": True, "profile": value}

    def create_snapshot(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        snapshot_id = _clean_id(payload.get("id") or f"snapshot-{uuid.uuid4().hex}", "snapshot id")
        project_id = _clean_id(payload.get("projectId"), "project id")
        workspace_id = _clean_id(payload.get("workspaceId"), "workspace id")
        classification = str(payload.get("classification") or "internal").strip().lower()
        if classification not in ALLOWED_CLASSIFICATIONS:
            raise InterfaceFinalizationError("Restricted or unknown classifications cannot be prepared for browser-offline access.")
        assets = payload.get("assets") or []
        if not isinstance(assets, list) or len(assets) > self.max_snapshot_assets:
            raise InterfaceFinalizationError("assets exceeds the offline snapshot limit.")
        normalized = []
        total = 0
        for item in assets:
            if not isinstance(item, dict): raise InterfaceFinalizationError("Each asset must be an object.")
            asset_class = str(item.get("classification") or classification).strip().lower()
            if asset_class not in ALLOWED_CLASSIFICATIONS:
                raise InterfaceFinalizationError("Restricted assets cannot be cached offline.")
            digest = str(item.get("sha256") or "").strip().lower()
            if not re_full_sha256(digest): raise InterfaceFinalizationError("Each asset requires a lowercase SHA-256 digest.")
            size = max(0, int(item.get("sizeBytes") or 0)); total += size
            normalized.append({"id": _clean_id(item.get("id"), "asset id"),
                               "url": _clean_text(item.get("url"), "asset url", 2000),
                               "sha256": digest, "sizeBytes": size,
                               "mediaType": _clean_text(item.get("mediaType"), "media type", 200, False) or "application/octet-stream",
                               "classification": asset_class})
        created = _now()
        snapshot = {"id": snapshot_id, "schema": "sc-lab-offline-project-snapshot/0.40.1",
                    "projectId": project_id, "workspaceId": workspace_id, "classification": classification,
                    "assets": normalized, "assetCount": len(normalized), "totalBytes": total,
                    "browserLocalPayloadRequired": True, "backendStoresRawPayload": False,
                    "createdAt": created, "actor": _clean_text(actor, "actor", 180)}
        digest = _sha(snapshot); snapshot["recordHash"] = digest
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO offline_snapshots(id,project_id,workspace_id,classification,asset_count,total_bytes,created_at,actor,payload_json,record_hash) VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (snapshot_id, project_id, workspace_id, classification, len(normalized), total, created, snapshot["actor"], json.dumps(snapshot, sort_keys=True), digest))
            self._event(db, "offline.snapshot-created", snapshot["actor"], "offline-snapshot", snapshot_id, {"assetCount": len(normalized), "totalBytes": total})
        return {"ok": True, "snapshot": snapshot}

    def list_snapshots(self, limit: int = 200) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT payload_json,record_hash FROM offline_snapshots ORDER BY created_at DESC LIMIT ?", (max(1,min(int(limit),2000)),)).fetchall()
        values=[]
        for row in rows:
            value=json.loads(row["payload_json"]); value["recordHash"]=row["record_hash"]; values.append(value)
        return {"ok": True, "snapshots": values}

    def queue_operation(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        operation_id = _clean_id(payload.get("id") or f"offline-op-{uuid.uuid4().hex}", "operation id")
        idem = _clean_id(payload.get("idempotencyKey") or operation_id, "idempotency key")
        operation = str(payload.get("operation") or "").strip().lower()
        if operation not in ALLOWED_OPERATIONS: raise InterfaceFinalizationError("Unsupported offline operation.")
        data = payload.get("payload") or {}
        if not isinstance(data, dict): raise InterfaceFinalizationError("payload must be an object.")
        if len(_canonical(data)) > 100000: raise InterfaceFinalizationError("Offline operation payload exceeds 100 KB.")
        record = {"id": operation_id, "schema": "sc-lab-offline-operation/0.40.1", "idempotencyKey": idem,
                  "workspaceId": _clean_id(payload.get("workspaceId"), "workspace id"),
                  "projectId": _clean_id(payload.get("projectId"), "project id"),
                  "operation": operation, "baseVersion": _clean_text(payload.get("baseVersion"), "base version", 180, False),
                  "payload": data, "payloadHash": _sha(data), "status": "pending", "createdAt": _now(),
                  "updatedAt": _now(), "actor": _clean_text(actor, "actor", 180)}
        digest = _sha(record); record["recordHash"] = digest
        with self._lock, self._connect() as db:
            existing = db.execute("SELECT payload_json,record_hash FROM offline_operations WHERE idempotency_key=?", (idem,)).fetchone()
            if existing:
                value=json.loads(existing["payload_json"]); value["recordHash"]=existing["record_hash"]
                if value.get("payloadHash") != record["payloadHash"] or value.get("operation") != operation:
                    raise InterfaceFinalizationError("Idempotency key already belongs to a different operation.", 409)
                return {"ok": True, "idempotent": True, "operation": value}
            count=int(db.execute("SELECT COUNT(*) FROM offline_operations").fetchone()[0])
            if count >= self.max_queue_records: raise InterfaceFinalizationError("Offline queue capacity reached.", 429)
            db.execute("INSERT INTO offline_operations(id,idempotency_key,workspace_id,project_id,operation,status,created_at,updated_at,actor,payload_json,record_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                       (operation_id, idem, record["workspaceId"], record["projectId"], operation, "pending", record["createdAt"], record["updatedAt"], record["actor"], json.dumps(record, sort_keys=True), digest))
            self._event(db, "offline.operation-queued", record["actor"], "offline-operation", operation_id, {"operation": operation, "payloadHash": record["payloadHash"]})
        return {"ok": True, "idempotent": False, "operation": record}

    def list_operations(self, status: str = "", limit: int = 500) -> dict[str, Any]:
        params=[]; where=""
        if status:
            status=str(status).strip().lower()
            if status not in {"pending","applied","conflict","rejected"}: raise InterfaceFinalizationError("Invalid operation status.")
            where=" WHERE status=?"; params.append(status)
        params.append(max(1,min(int(limit),5000)))
        with self._connect() as db:
            rows=db.execute(f"SELECT payload_json,record_hash FROM offline_operations{where} ORDER BY created_at ASC LIMIT ?", params).fetchall()
        values=[]
        for row in rows:
            value=json.loads(row["payload_json"]); value["recordHash"]=row["record_hash"]; values.append(value)
        return {"ok": True, "operations": values}

    def reconcile(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        _reject_sensitive(payload)
        decisions=payload.get("decisions")
        if not isinstance(decisions,list) or not decisions: raise InterfaceFinalizationError("decisions must be a non-empty array.")
        receipt_id=_clean_id(payload.get("id") or f"reconcile-{uuid.uuid4().hex}", "receipt id")
        normalized=[]; counts={"applied":0,"conflict":0,"rejected":0}
        with self._lock, self._connect() as db:
            for item in decisions[:5000]:
                if not isinstance(item,dict): raise InterfaceFinalizationError("Each decision must be an object.")
                op_id=_clean_id(item.get("operationId"), "operation id")
                status=str(item.get("status") or "").strip().lower()
                if status not in counts: raise InterfaceFinalizationError("Invalid reconciliation status.")
                row=db.execute("SELECT payload_json FROM offline_operations WHERE id=?",(op_id,)).fetchone()
                if not row: raise InterfaceFinalizationError(f"Offline operation not found: {op_id}",404)
                record=json.loads(row["payload_json"])
                if record.get("status") != "pending":
                    normalized.append({"operationId":op_id,"status":record.get("status"),"idempotent":True}); continue
                record["status"]=status; record["updatedAt"]=_now()
                record["remoteVersion"]=_clean_text(item.get("remoteVersion"),"remote version",180,False)
                record["resolution"]=_clean_text(item.get("resolution"),"resolution",2000,False)
                digest=_sha({k:v for k,v in record.items() if k!='recordHash'}); record["recordHash"]=digest
                db.execute("UPDATE offline_operations SET status=?,updated_at=?,payload_json=?,record_hash=? WHERE id=?",(status,record["updatedAt"],json.dumps(record,sort_keys=True),digest,op_id))
                counts[status]+=1; normalized.append({"operationId":op_id,"status":status,"recordHash":digest})
            receipt={"id":receipt_id,"schema":"sc-lab-offline-reconciliation-receipt/0.40.1","createdAt":_now(),
                     "actor":_clean_text(actor,"actor",180),"decisions":normalized,
                     "appliedCount":counts["applied"],"conflictCount":counts["conflict"],"rejectedCount":counts["rejected"]}
            digest=_sha(receipt); receipt["receiptHash"]=digest
            db.execute("INSERT INTO reconciliation_receipts(id,created_at,actor,applied_count,conflict_count,rejected_count,payload_json,receipt_hash) VALUES(?,?,?,?,?,?,?,?)",
                       (receipt_id,receipt["createdAt"],receipt["actor"],counts["applied"],counts["conflict"],counts["rejected"],json.dumps(receipt,sort_keys=True),digest))
            self._event(db,"offline.reconciled",receipt["actor"],"reconciliation-receipt",receipt_id,counts)
        return {"ok":True,"receipt":receipt}

    def verify_timeline(self) -> dict[str, Any]:
        with self._connect() as db: rows=db.execute("SELECT * FROM interface_events ORDER BY seq ASC").fetchall()
        previous=""; failures=[]
        for row in rows:
            payload=json.loads(row["payload_json"])
            envelope={"eventType":row["event_type"],"actor":row["actor"],"subjectType":row["subject_type"],"subjectId":row["subject_id"],"occurredAt":row["occurred_at"],"payload":payload,"previousHash":row["previous_hash"]}
            if row["previous_hash"] != previous or _sha(envelope) != row["event_hash"]: failures.append(int(row["seq"]))
            previous=row["event_hash"]
        return {"ok":not failures,"valid":not failures,"eventCount":len(rows),"failedSequences":failures,"headHash":previous}

    def dashboard(self) -> dict[str, Any]:
        with self._connect() as db:
            counts={
                "audits":int(db.execute("SELECT COUNT(*) FROM interface_audits").fetchone()[0]),
                "readyAudits":int(db.execute("SELECT COUNT(*) FROM interface_audits WHERE status='ready'").fetchone()[0]),
                "preferenceProfiles":int(db.execute("SELECT COUNT(*) FROM preference_profiles").fetchone()[0]),
                "offlineSnapshots":int(db.execute("SELECT COUNT(*) FROM offline_snapshots").fetchone()[0]),
                "pendingOperations":int(db.execute("SELECT COUNT(*) FROM offline_operations WHERE status='pending'").fetchone()[0]),
                "conflicts":int(db.execute("SELECT COUNT(*) FROM offline_operations WHERE status='conflict'").fetchone()[0]),
                "reconciliationReceipts":int(db.execute("SELECT COUNT(*) FROM reconciliation_receipts").fetchone()[0]),
            }
        return {"ok":True,"version":VERSION,"counts":counts,"timeline":self.verify_timeline(),
                "offlineShellEnabled":self.offline_shell_enabled,"restrictedDataMayBeCached":False}


def re_full_sha256(value: str) -> bool:
    return len(value)==64 and all(ch in "0123456789abcdef" for ch in value)
