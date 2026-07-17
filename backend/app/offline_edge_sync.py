from __future__ import annotations

import copy
import hmac
import json
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.36.2"
DEVICE_SCHEMA = "sc-lab-edge-device/0.36.2"
PACKAGE_SCHEMA = "sc-lab-offline-work-package/0.36.2"
CHANGE_SCHEMA = "sc-lab-edge-change/0.36.2"
SESSION_SCHEMA = "sc-lab-edge-sync-session/0.36.2"
CONFLICT_SCHEMA = "sc-lab-edge-sync-conflict/0.36.2"
EVENT_SCHEMA = "sc-lab-edge-sync-event/0.36.2"

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
DEVICE_STATUSES = {"active", "suspended", "revoked", "retired"}
PACKAGE_STATUSES = {"draft", "sealed", "archived", "expired"}
OPERATIONS = {"upsert", "delete", "append"}
RESOLUTIONS = {"keep-local", "accept-edge", "retain-both", "dismiss"}
ROLE_RANK = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
FORBIDDEN_KEYS = {"code", "python", "shell", "command", "callbackurl", "executable", "script"}


class EdgeSyncError(ValueError):
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


def _id(value: Any, label: str = "identifier") -> str:
    clean = _text(value, 180)
    if not ID_RE.match(clean):
        raise EdgeSyncError(f"A valid {label} is required.")
    return clean


def _sha(value: Any, required: bool = True) -> str:
    clean = _text(value, 64).lower()
    if not clean and not required:
        return ""
    if not SHA_RE.match(clean):
        raise EdgeSyncError("A valid SHA-256 digest is required.")
    return clean


def _scan_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise EdgeSyncError("Executable code, shell commands, and unrestricted callbacks are not permitted.", 422)
            _scan_forbidden(child)
    elif isinstance(value, list):
        for child in value:
            _scan_forbidden(child)


def _json_object(value: Any, limit: int = 4194304) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise EdgeSyncError("The value must be a JSON object.")
    clone = copy.deepcopy(value)
    _scan_forbidden(clone)
    if len(_stable(clone).encode("utf-8")) > limit:
        raise EdgeSyncError("The JSON payload exceeds the configured limit.", 413)
    return clone


def policies(max_devices: int = 10000, max_packages: int = 100000, max_changes: int = 1000000, max_batch: int = 500) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-offline-edge-sync-policy/0.36.2",
        "schemas": {"device": DEVICE_SCHEMA, "package": PACKAGE_SCHEMA, "change": CHANGE_SCHEMA, "session": SESSION_SCHEMA, "conflict": CONFLICT_SCHEMA, "event": EVENT_SCHEMA},
        "limits": {"devices": max_devices, "packages": max_packages, "changes": max_changes, "batchChanges": max_batch},
        "capabilities": {
            "offlineWorkPackages": True,
            "resumableSynchronization": True,
            "signedChangeBatches": True,
            "cursorBasedDeltaExchange": True,
            "conflictSafeReconciliation": True,
            "fieldDeviceProvenance": True,
            "restrictedDataBytesInPackage": False,
            "automaticRemoteCallbacks": False,
            "arbitraryCode": False,
            "hardDelete": False,
        },
    }


class OfflineEdgeSyncManager:
    def __init__(
        self,
        db_path: str,
        workspaces: Any,
        institutional_nodes: Any | None = None,
        max_devices: int = 10000,
        max_packages: int = 100000,
        max_changes: int = 1000000,
        max_batch: int = 500,
        history_limit: int = 200000,
    ):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.institutional_nodes = institutional_nodes
        self.max_devices = max(1, int(max_devices))
        self.max_packages = max(1, int(max_packages))
        self.max_changes = max(100, int(max_changes))
        self.max_batch = max(1, min(5000, int(max_batch)))
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
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS edge_devices(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,node_id TEXT,title TEXT NOT NULL,
                  platform TEXT NOT NULL,app_version TEXT,status TEXT NOT NULL,secret TEXT NOT NULL,
                  capabilities_json TEXT NOT NULL,device_hash TEXT NOT NULL,created_by TEXT NOT NULL,
                  created_at TEXT NOT NULL,updated_at TEXT NOT NULL,last_seen_at TEXT,
                  last_pull_cursor INTEGER NOT NULL DEFAULT 0,last_push_cursor INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS offline_packages(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,node_id TEXT,title TEXT NOT NULL,
                  status TEXT NOT NULL,definition_json TEXT NOT NULL,package_hash TEXT NOT NULL,
                  base_cursor INTEGER NOT NULL DEFAULT 0,created_by TEXT NOT NULL,created_at TEXT NOT NULL,
                  sealed_at TEXT,expires_at TEXT,archived_at TEXT
                );
                CREATE TABLE IF NOT EXISTS package_assignments(
                  package_id TEXT NOT NULL,device_id TEXT NOT NULL,status TEXT NOT NULL,
                  assigned_by TEXT NOT NULL,assigned_at TEXT NOT NULL,last_downloaded_at TEXT,
                  PRIMARY KEY(package_id,device_id),
                  FOREIGN KEY(package_id) REFERENCES offline_packages(id),
                  FOREIGN KEY(device_id) REFERENCES edge_devices(id)
                );
                CREATE TABLE IF NOT EXISTS edge_changes(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,change_id TEXT NOT NULL UNIQUE,
                  workspace_id TEXT NOT NULL,package_id TEXT NOT NULL,device_id TEXT NOT NULL,
                  entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,operation TEXT NOT NULL,
                  payload_json TEXT NOT NULL,content_hash TEXT NOT NULL,base_hash TEXT,
                  device_created_at TEXT NOT NULL,ingested_at TEXT NOT NULL,
                  FOREIGN KEY(package_id) REFERENCES offline_packages(id),
                  FOREIGN KEY(device_id) REFERENCES edge_devices(id)
                );
                CREATE TABLE IF NOT EXISTS sync_sessions(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,package_id TEXT NOT NULL,device_id TEXT NOT NULL,
                  direction TEXT NOT NULL,status TEXT NOT NULL,base_cursor INTEGER NOT NULL,
                  server_cursor INTEGER NOT NULL,accepted_count INTEGER NOT NULL DEFAULT 0,
                  duplicate_count INTEGER NOT NULL DEFAULT 0,conflict_count INTEGER NOT NULL DEFAULT 0,
                  rejected_count INTEGER NOT NULL DEFAULT 0,bytes_received INTEGER NOT NULL DEFAULT 0,
                  resume_token_hash TEXT NOT NULL,started_at TEXT NOT NULL,updated_at TEXT NOT NULL,completed_at TEXT,
                  FOREIGN KEY(package_id) REFERENCES offline_packages(id),
                  FOREIGN KEY(device_id) REFERENCES edge_devices(id)
                );
                CREATE TABLE IF NOT EXISTS edge_conflicts(
                  id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,package_id TEXT NOT NULL,
                  entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,local_change_id TEXT,
                  edge_change_id TEXT NOT NULL,local_hash TEXT,edge_hash TEXT NOT NULL,
                  status TEXT NOT NULL,resolution TEXT,resolved_by TEXT,resolved_at TEXT,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS edge_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,workspace_id TEXT NOT NULL,
                  entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,event_type TEXT NOT NULL,
                  actor_id TEXT NOT NULL,details_json TEXT NOT NULL,event_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_edge_devices_workspace ON edge_devices(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_edge_packages_workspace ON offline_packages(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_edge_changes_package ON edge_changes(package_id,sequence);
                CREATE INDEX IF NOT EXISTS idx_edge_changes_entity ON edge_changes(package_id,entity_type,entity_id,sequence);
                CREATE INDEX IF NOT EXISTS idx_edge_sessions_device ON sync_sessions(device_id,status,updated_at);
                CREATE INDEX IF NOT EXISTS idx_edge_conflicts_workspace ON edge_conflicts(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_edge_events_workspace ON edge_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT INTO meta(key,value) VALUES('schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")

    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True) -> dict[str, Any]:
        try:
            body = self.workspaces.get(workspace_id, actor_id, include_members=False, include_resources=False)
        except Exception as exc:
            raise EdgeSyncError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 403)) from exc
        workspace = body["workspace"]
        if not allow_archived and workspace.get("status") == "archived":
            raise EdgeSyncError("The workspace is archived and read-only.", 409)
        role = ((workspace.get("currentMembership") or {}).get("role") or "viewer")
        if ROLE_RANK.get(role, 0) < ROLE_RANK[minimum]:
            raise EdgeSyncError(f"The {minimum} role or higher is required.", 403)
        return workspace

    def _node_exists(self, workspace_id: str, node_id: str, actor_id: str) -> None:
        if not node_id or not self.institutional_nodes:
            return
        try:
            nodes = self.institutional_nodes.list_nodes(workspace_id, actor_id)["nodes"]
        except Exception as exc:
            raise EdgeSyncError(str(getattr(exc, "detail", exc)), getattr(exc, "status_code", 400)) from exc
        if not any(node.get("id") == node_id for node in nodes):
            raise EdgeSyncError("Institutional node not found in this workspace.", 404)

    def _event(self, con: sqlite3.Connection, workspace_id: str, entity_type: str, entity_id: str, event_type: str, actor_id: str, details: dict[str, Any]) -> dict[str, Any]:
        created = _now()
        payload = {"schema": EVENT_SCHEMA, "version": VERSION, "workspaceId": workspace_id, "entityType": entity_type, "entityId": entity_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created}
        event_hash = _hash(payload)
        con.execute("INSERT INTO edge_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)", (workspace_id, entity_type, entity_id, event_type, actor_id, _stable(details), event_hash, created))
        return {**payload, "eventHash": event_hash}

    def _device(self, row: sqlite3.Row, include_secret: bool = False) -> dict[str, Any]:
        body = {"schema": DEVICE_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "nodeId": row["node_id"], "title": row["title"], "platform": row["platform"], "appVersion": row["app_version"], "status": row["status"], "capabilities": json.loads(row["capabilities_json"]), "deviceHash": row["device_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "lastSeenAt": row["last_seen_at"], "lastPullCursor": row["last_pull_cursor"], "lastPushCursor": row["last_push_cursor"]}
        if include_secret:
            body["deviceSecret"] = row["secret"]
        return body

    def _package(self, row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": PACKAGE_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "nodeId": row["node_id"], "title": row["title"], "status": row["status"], "definition": json.loads(row["definition_json"]), "packageHash": row["package_hash"], "baseCursor": row["base_cursor"], "createdBy": row["created_by"], "createdAt": row["created_at"], "sealedAt": row["sealed_at"], "expiresAt": row["expires_at"], "archivedAt": row["archived_at"]}

    def _change(self, row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": CHANGE_SCHEMA, "version": VERSION, "sequence": row["sequence"], "changeId": row["change_id"], "workspaceId": row["workspace_id"], "packageId": row["package_id"], "deviceId": row["device_id"], "entityType": row["entity_type"], "entityId": row["entity_id"], "operation": row["operation"], "payload": json.loads(row["payload_json"]), "contentHash": row["content_hash"], "baseHash": row["base_hash"], "deviceCreatedAt": row["device_created_at"], "ingestedAt": row["ingested_at"]}

    def _session(self, row: sqlite3.Row, token: str = "") -> dict[str, Any]:
        body = {"schema": SESSION_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "packageId": row["package_id"], "deviceId": row["device_id"], "direction": row["direction"], "status": row["status"], "baseCursor": row["base_cursor"], "serverCursor": row["server_cursor"], "acceptedCount": row["accepted_count"], "duplicateCount": row["duplicate_count"], "conflictCount": row["conflict_count"], "rejectedCount": row["rejected_count"], "bytesReceived": row["bytes_received"], "startedAt": row["started_at"], "updatedAt": row["updated_at"], "completedAt": row["completed_at"]}
        if token:
            body["resumeToken"] = token
        return body

    def _conflict(self, row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": CONFLICT_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "packageId": row["package_id"], "entityType": row["entity_type"], "entityId": row["entity_id"], "localChangeId": row["local_change_id"], "edgeChangeId": row["edge_change_id"], "localHash": row["local_hash"], "edgeHash": row["edge_hash"], "status": row["status"], "resolution": row["resolution"], "resolvedBy": row["resolved_by"], "resolvedAt": row["resolved_at"], "createdAt": row["created_at"]}

    @staticmethod
    def _verify_secret(row: sqlite3.Row, supplied: str) -> None:
        if not supplied or not hmac.compare_digest(row["secret"], supplied):
            raise EdgeSyncError("Edge device authentication failed.", 401)
        if row["status"] != "active":
            raise EdgeSyncError("Edge device is not active.", 409)

    def enroll_device(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        device_id = _id(payload.get("id") or ("edge-" + secrets.token_hex(8)), "edge device ID")
        node_id = _text(payload.get("nodeId"), 180)
        if node_id:
            node_id = _id(node_id, "institutional node ID")
            self._node_exists(workspace_id, node_id, actor_id)
        title = _text(payload.get("title"), 300) or device_id
        platform = _text(payload.get("platform"), 100) or "unknown"
        app_version = _text(payload.get("appVersion"), 80)
        capabilities = _json_object(payload.get("capabilities"), 262144)
        secret = secrets.token_urlsafe(36)
        created = _now()
        identity = {"id": device_id, "workspaceId": workspace_id, "nodeId": node_id or None, "title": title, "platform": platform, "appVersion": app_version, "capabilities": capabilities, "createdAt": created}
        device_hash = _hash(identity)
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM edge_devices").fetchone()[0] >= self.max_devices:
                raise EdgeSyncError("Edge device capacity has been reached.", 409)
            try:
                con.execute("INSERT INTO edge_devices(id,workspace_id,node_id,title,platform,app_version,status,secret,capabilities_json,device_hash,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (device_id, workspace_id, node_id or None, title, platform, app_version or None, "active", secret, _stable(capabilities), device_hash, actor_id, created, created))
            except sqlite3.IntegrityError as exc:
                raise EdgeSyncError("Edge device already exists.", 409) from exc
            self._event(con, workspace_id, "device", device_id, "edge-device-enrolled", actor_id, {"nodeId": node_id or None, "platform": platform, "deviceHash": device_hash})
            return {"ok": True, "device": self._device(con.execute("SELECT * FROM edge_devices WHERE id=?", (device_id,)).fetchone(), True)}

    def list_devices(self, workspace_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM edge_devices WHERE workspace_id=? ORDER BY updated_at DESC", (workspace_id,)).fetchall()
            return {"ok": True, "version": VERSION, "devices": [self._device(r) for r in rows]}

    def set_device_status(self, workspace_id: str, device_id: str, status: str, actor_id: str, reason: str = "") -> dict[str, Any]:
        workspace_id, device_id, actor_id = _id(workspace_id, "workspace ID"), _id(device_id, "device ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "administrator", False)
        status = _text(status, 30).lower()
        if status not in DEVICE_STATUSES:
            raise EdgeSyncError("Unsupported edge-device status.")
        with self._connect() as con:
            row = con.execute("SELECT * FROM edge_devices WHERE id=? AND workspace_id=?", (device_id, workspace_id)).fetchone()
            if not row:
                raise EdgeSyncError("Edge device not found.", 404)
            con.execute("UPDATE edge_devices SET status=?,updated_at=? WHERE id=?", (status, _now(), device_id))
            self._event(con, workspace_id, "device", device_id, "edge-device-status-changed", actor_id, {"previousStatus": row["status"], "status": status, "reason": _text(reason, 1000)})
            return {"ok": True, "device": self._device(con.execute("SELECT * FROM edge_devices WHERE id=?", (device_id,)).fetchone())}

    def create_package(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        package_id = _id(payload.get("id") or ("field-package-" + secrets.token_hex(8)), "offline package ID")
        node_id = _text(payload.get("nodeId"), 180)
        if node_id:
            node_id = _id(node_id, "institutional node ID")
            self._node_exists(workspace_id, node_id, actor_id)
        title = _text(payload.get("title"), 300) or package_id
        definition = _json_object(payload.get("definition"), 8388608)
        allowed_top = {"methods", "forms", "protocols", "dataAssetRefs", "artifactRefs", "instructions", "constraints", "metadata"}
        unknown = set(definition) - allowed_top
        if unknown:
            raise EdgeSyncError("Offline package definition contains unsupported fields: " + ", ".join(sorted(unknown)), 422)
        methods = definition.get("methods") or []
        if not isinstance(methods, list) or len(methods) > 100:
            raise EdgeSyncError("methods must be a bounded list.")
        definition["methods"] = [_id(x, "method ID") for x in methods]
        expires_at = _text(payload.get("expiresAt"), 60) or None
        created = _now()
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM offline_packages").fetchone()[0] >= self.max_packages:
                raise EdgeSyncError("Offline package capacity has been reached.", 409)
            cursor = con.execute("SELECT COALESCE(MAX(sequence),0) FROM edge_changes WHERE workspace_id=?", (workspace_id,)).fetchone()[0]
            identity = {"id": package_id, "workspaceId": workspace_id, "nodeId": node_id or None, "title": title, "definition": definition, "baseCursor": cursor, "createdAt": created, "expiresAt": expires_at}
            package_hash = _hash(identity)
            try:
                con.execute("INSERT INTO offline_packages(id,workspace_id,node_id,title,status,definition_json,package_hash,base_cursor,created_by,created_at,expires_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (package_id, workspace_id, node_id or None, title, "draft", _stable(definition), package_hash, cursor, actor_id, created, expires_at))
            except sqlite3.IntegrityError as exc:
                raise EdgeSyncError("Offline work package already exists.", 409) from exc
            self._event(con, workspace_id, "package", package_id, "offline-package-created", actor_id, {"nodeId": node_id or None, "packageHash": package_hash, "baseCursor": cursor})
            return {"ok": True, "package": self._package(con.execute("SELECT * FROM offline_packages WHERE id=?", (package_id,)).fetchone())}

    def seal_package(self, workspace_id: str, package_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, package_id, actor_id = _id(workspace_id, "workspace ID"), _id(package_id, "package ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        with self._connect() as con:
            row = con.execute("SELECT * FROM offline_packages WHERE id=? AND workspace_id=?", (package_id, workspace_id)).fetchone()
            if not row:
                raise EdgeSyncError("Offline work package not found.", 404)
            if row["status"] == "sealed":
                return {"ok": True, "idempotent": True, "package": self._package(row)}
            if row["status"] != "draft":
                raise EdgeSyncError("Only a draft package can be sealed.", 409)
            now = _now()
            con.execute("UPDATE offline_packages SET status='sealed',sealed_at=? WHERE id=?", (now, package_id))
            self._event(con, workspace_id, "package", package_id, "offline-package-sealed", actor_id, {"packageHash": row["package_hash"]})
            return {"ok": True, "idempotent": False, "package": self._package(con.execute("SELECT * FROM offline_packages WHERE id=?", (package_id,)).fetchone())}

    def assign_package(self, workspace_id: str, package_id: str, device_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, package_id, device_id, actor_id = _id(workspace_id, "workspace ID"), _id(package_id, "package ID"), _id(device_id, "device ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        now = _now()
        with self._connect() as con:
            package = con.execute("SELECT * FROM offline_packages WHERE id=? AND workspace_id=?", (package_id, workspace_id)).fetchone()
            device = con.execute("SELECT * FROM edge_devices WHERE id=? AND workspace_id=?", (device_id, workspace_id)).fetchone()
            if not package or not device:
                raise EdgeSyncError("Package or device not found.", 404)
            if package["status"] != "sealed":
                raise EdgeSyncError("Only sealed packages can be assigned.", 409)
            if device["status"] != "active":
                raise EdgeSyncError("Only active edge devices can receive packages.", 409)
            con.execute("INSERT INTO package_assignments(package_id,device_id,status,assigned_by,assigned_at) VALUES(?,?,?,?,?) ON CONFLICT(package_id,device_id) DO UPDATE SET status='assigned',assigned_by=excluded.assigned_by,assigned_at=excluded.assigned_at", (package_id, device_id, "assigned", actor_id, now))
            self._event(con, workspace_id, "package", package_id, "offline-package-assigned", actor_id, {"deviceId": device_id})
            return {"ok": True, "packageId": package_id, "deviceId": device_id, "status": "assigned", "assignedAt": now}

    def list_packages(self, workspace_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM offline_packages WHERE workspace_id=? ORDER BY created_at DESC", (workspace_id,)).fetchall()
            return {"ok": True, "version": VERSION, "packages": [self._package(r) for r in rows]}

    def pull_package(self, device_id: str, package_id: str, device_secret: str) -> dict[str, Any]:
        device_id, package_id = _id(device_id, "device ID"), _id(package_id, "package ID")
        with self._connect() as con:
            device = con.execute("SELECT * FROM edge_devices WHERE id=?", (device_id,)).fetchone()
            if not device:
                raise EdgeSyncError("Edge device not found.", 404)
            self._verify_secret(device, device_secret)
            assignment = con.execute("SELECT * FROM package_assignments WHERE package_id=? AND device_id=?", (package_id, device_id)).fetchone()
            package = con.execute("SELECT * FROM offline_packages WHERE id=? AND workspace_id=?", (package_id, device["workspace_id"])).fetchone()
            if not assignment or not package:
                raise EdgeSyncError("The package is not assigned to this device.", 403)
            if package["status"] != "sealed":
                raise EdgeSyncError("The assigned package is not available for offline use.", 409)
            now = _now()
            con.execute("UPDATE package_assignments SET status='downloaded',last_downloaded_at=? WHERE package_id=? AND device_id=?", (now, package_id, device_id))
            con.execute("UPDATE edge_devices SET last_seen_at=?,updated_at=? WHERE id=?", (now, now, device_id))
            self._event(con, device["workspace_id"], "package", package_id, "offline-package-downloaded", device_id, {"deviceId": device_id, "packageHash": package["package_hash"]})
            return {"ok": True, "package": self._package(package), "assignment": {"status": "downloaded", "lastDownloadedAt": now}, "constraints": {"containsRestrictedDataBytes": False, "arbitraryCode": False, "automaticCallbacks": False}}

    def begin_sync(self, device_id: str, package_id: str, payload: dict[str, Any], device_secret: str) -> dict[str, Any]:
        device_id, package_id = _id(device_id, "device ID"), _id(package_id, "package ID")
        direction = _text(payload.get("direction"), 30).lower() or "bidirectional"
        if direction not in {"push", "pull", "bidirectional"}:
            raise EdgeSyncError("Unsupported synchronization direction.")
        base_cursor = max(0, int(payload.get("baseCursor") or 0))
        with self._connect() as con:
            device = con.execute("SELECT * FROM edge_devices WHERE id=?", (device_id,)).fetchone()
            if not device:
                raise EdgeSyncError("Edge device not found.", 404)
            self._verify_secret(device, device_secret)
            assignment = con.execute("SELECT 1 FROM package_assignments WHERE package_id=? AND device_id=?", (package_id, device_id)).fetchone()
            package = con.execute("SELECT * FROM offline_packages WHERE id=? AND workspace_id=?", (package_id, device["workspace_id"])).fetchone()
            if not assignment or not package:
                raise EdgeSyncError("The package is not assigned to this device.", 403)
            token = secrets.token_urlsafe(36)
            session_id = "sync-" + secrets.token_hex(12)
            now = _now()
            server_cursor = con.execute("SELECT COALESCE(MAX(sequence),0) FROM edge_changes WHERE package_id=?", (package_id,)).fetchone()[0]
            con.execute("INSERT INTO sync_sessions(id,workspace_id,package_id,device_id,direction,status,base_cursor,server_cursor,resume_token_hash,started_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (session_id, device["workspace_id"], package_id, device_id, direction, "open", base_cursor, server_cursor, sha256(token.encode()).hexdigest(), now, now))
            self._event(con, device["workspace_id"], "sync-session", session_id, "edge-sync-started", device_id, {"packageId": package_id, "direction": direction, "baseCursor": base_cursor, "serverCursor": server_cursor})
            return {"ok": True, "session": self._session(con.execute("SELECT * FROM sync_sessions WHERE id=?", (session_id,)).fetchone(), token)}

    def _session_auth(self, con: sqlite3.Connection, device_id: str, session_id: str, device_secret: str, resume_token: str) -> tuple[sqlite3.Row, sqlite3.Row]:
        device = con.execute("SELECT * FROM edge_devices WHERE id=?", (device_id,)).fetchone()
        if not device:
            raise EdgeSyncError("Edge device not found.", 404)
        self._verify_secret(device, device_secret)
        session = con.execute("SELECT * FROM sync_sessions WHERE id=? AND device_id=?", (session_id, device_id)).fetchone()
        if not session:
            raise EdgeSyncError("Synchronization session not found.", 404)
        if not resume_token or not hmac.compare_digest(session["resume_token_hash"], sha256(resume_token.encode()).hexdigest()):
            raise EdgeSyncError("Synchronization resume token is invalid.", 401)
        if session["status"] != "open":
            raise EdgeSyncError("Synchronization session is not open.", 409)
        return device, session

    def push_changes(self, device_id: str, session_id: str, payload: dict[str, Any], device_secret: str, resume_token: str) -> dict[str, Any]:
        device_id, session_id = _id(device_id, "device ID"), _id(session_id, "session ID")
        changes = payload.get("changes") or []
        if not isinstance(changes, list) or len(changes) > self.max_batch:
            raise EdgeSyncError("changes must be a bounded list.", 413)
        signature = _text(payload.get("signature"), 128).lower()
        signed = {"sessionId": session_id, "deviceId": device_id, "changes": changes}
        expected = hmac.new(device_secret.encode(), _hash(signed).encode(), sha256).hexdigest()
        if not signature or not hmac.compare_digest(expected, signature):
            raise EdgeSyncError("Edge change-batch signature is invalid.", 401)
        accepted = duplicates = conflicts = rejected = bytes_received = 0
        accepted_records: list[dict[str, Any]] = []
        conflict_records: list[dict[str, Any]] = []
        with self._connect() as con:
            device, session = self._session_auth(con, device_id, session_id, device_secret, resume_token)
            if session["direction"] == "pull":
                raise EdgeSyncError("This synchronization session does not accept pushed changes.", 409)
            for raw in changes:
                try:
                    if not isinstance(raw, dict):
                        raise EdgeSyncError("Each change must be a JSON object.")
                    change_id = _id(raw.get("changeId"), "change ID")
                    entity_type = _id(raw.get("entityType"), "entity type")
                    entity_id = _id(raw.get("entityId"), "entity ID")
                    operation = _text(raw.get("operation"), 20).lower() or "upsert"
                    if operation not in OPERATIONS:
                        raise EdgeSyncError("Unsupported edge change operation.")
                    change_payload = _json_object(raw.get("payload"), 4194304)
                    base_hash = _sha(raw.get("baseHash"), False) or None
                    device_created = _text(raw.get("createdAt"), 60) or _now()
                    bytes_received += len(_stable(raw).encode("utf-8"))
                    existing = con.execute("SELECT * FROM edge_changes WHERE change_id=?", (change_id,)).fetchone()
                    if existing:
                        duplicates += 1
                        continue
                    if con.execute("SELECT COUNT(*) FROM edge_changes").fetchone()[0] >= self.max_changes:
                        raise EdgeSyncError("Edge change capacity has been reached.", 409)
                    latest = con.execute("SELECT * FROM edge_changes WHERE package_id=? AND entity_type=? AND entity_id=? ORDER BY sequence DESC LIMIT 1", (session["package_id"], entity_type, entity_id)).fetchone()
                    content = {"entityType": entity_type, "entityId": entity_id, "operation": operation, "payload": change_payload}
                    content_hash = _hash(content)
                    if latest and latest["content_hash"] != content_hash and (not base_hash or base_hash != latest["content_hash"]):
                        conflict_id = "conflict-" + secrets.token_hex(12)
                        now = _now()
                        con.execute("INSERT INTO edge_conflicts(id,workspace_id,package_id,entity_type,entity_id,local_change_id,edge_change_id,local_hash,edge_hash,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (conflict_id, session["workspace_id"], session["package_id"], entity_type, entity_id, latest["change_id"], change_id, latest["content_hash"], content_hash, "open", now))
                        con.execute("INSERT INTO edge_changes(change_id,workspace_id,package_id,device_id,entity_type,entity_id,operation,payload_json,content_hash,base_hash,device_created_at,ingested_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (change_id, session["workspace_id"], session["package_id"], device_id, entity_type, entity_id, operation, _stable(change_payload), content_hash, base_hash, device_created, now))
                        row = con.execute("SELECT * FROM edge_conflicts WHERE id=?", (conflict_id,)).fetchone()
                        conflict_records.append(self._conflict(row)); conflicts += 1
                        self._event(con, session["workspace_id"], "conflict", conflict_id, "edge-sync-conflict-created", device_id, {"packageId": session["package_id"], "entityType": entity_type, "entityId": entity_id, "localHash": latest["content_hash"], "edgeHash": content_hash})
                        continue
                    now = _now()
                    con.execute("INSERT INTO edge_changes(change_id,workspace_id,package_id,device_id,entity_type,entity_id,operation,payload_json,content_hash,base_hash,device_created_at,ingested_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (change_id, session["workspace_id"], session["package_id"], device_id, entity_type, entity_id, operation, _stable(change_payload), content_hash, base_hash, device_created, now))
                    row = con.execute("SELECT * FROM edge_changes WHERE change_id=?", (change_id,)).fetchone()
                    accepted_records.append(self._change(row)); accepted += 1
                except EdgeSyncError:
                    rejected += 1
            server_cursor = con.execute("SELECT COALESCE(MAX(sequence),0) FROM edge_changes WHERE package_id=?", (session["package_id"],)).fetchone()[0]
            now = _now()
            con.execute("UPDATE sync_sessions SET server_cursor=?,accepted_count=accepted_count+?,duplicate_count=duplicate_count+?,conflict_count=conflict_count+?,rejected_count=rejected_count+?,bytes_received=bytes_received+?,updated_at=? WHERE id=?", (server_cursor, accepted, duplicates, conflicts, rejected, bytes_received, now, session_id))
            con.execute("UPDATE edge_devices SET last_seen_at=?,last_push_cursor=?,updated_at=? WHERE id=?", (now, server_cursor, now, device_id))
            self._event(con, session["workspace_id"], "sync-session", session_id, "edge-change-batch-ingested", device_id, {"accepted": accepted, "duplicates": duplicates, "conflicts": conflicts, "rejected": rejected, "serverCursor": server_cursor})
            updated = con.execute("SELECT * FROM sync_sessions WHERE id=?", (session_id,)).fetchone()
            return {"ok": True, "accepted": accepted_records, "conflicts": conflict_records, "summary": {"accepted": accepted, "duplicates": duplicates, "conflicts": conflicts, "rejected": rejected}, "session": self._session(updated)}

    def pull_changes(self, device_id: str, session_id: str, since_cursor: int, device_secret: str, resume_token: str, limit: int = 500) -> dict[str, Any]:
        device_id, session_id = _id(device_id, "device ID"), _id(session_id, "session ID")
        since_cursor = max(0, int(since_cursor)); limit = max(1, min(self.max_batch, int(limit)))
        with self._connect() as con:
            device, session = self._session_auth(con, device_id, session_id, device_secret, resume_token)
            if session["direction"] == "push":
                raise EdgeSyncError("This synchronization session does not provide pulled changes.", 409)
            rows = con.execute("SELECT * FROM edge_changes WHERE package_id=? AND sequence>? ORDER BY sequence ASC LIMIT ?", (session["package_id"], since_cursor, limit)).fetchall()
            cursor = rows[-1]["sequence"] if rows else since_cursor
            now = _now()
            con.execute("UPDATE edge_devices SET last_seen_at=?,last_pull_cursor=?,updated_at=? WHERE id=?", (now, cursor, now, device_id))
            con.execute("UPDATE sync_sessions SET server_cursor=?,updated_at=? WHERE id=?", (max(session["server_cursor"], cursor), now, session_id))
            return {"ok": True, "changes": [self._change(r) for r in rows], "cursor": cursor, "hasMore": bool(rows and con.execute("SELECT 1 FROM edge_changes WHERE package_id=? AND sequence>? LIMIT 1", (session["package_id"], cursor)).fetchone())}

    def complete_sync(self, device_id: str, session_id: str, payload: dict[str, Any], device_secret: str, resume_token: str) -> dict[str, Any]:
        device_id, session_id = _id(device_id, "device ID"), _id(session_id, "session ID")
        final_cursor = max(0, int(payload.get("finalCursor") or 0))
        with self._connect() as con:
            device, session = self._session_auth(con, device_id, session_id, device_secret, resume_token)
            now = _now()
            server_cursor = max(session["server_cursor"], final_cursor)
            con.execute("UPDATE sync_sessions SET status='completed',server_cursor=?,updated_at=?,completed_at=? WHERE id=?", (server_cursor, now, now, session_id))
            con.execute("UPDATE edge_devices SET last_seen_at=?,last_pull_cursor=MAX(last_pull_cursor,?),last_push_cursor=MAX(last_push_cursor,?),updated_at=? WHERE id=?", (now, final_cursor, server_cursor, now, device_id))
            self._event(con, session["workspace_id"], "sync-session", session_id, "edge-sync-completed", device_id, {"finalCursor": final_cursor, "serverCursor": server_cursor})
            return {"ok": True, "session": self._session(con.execute("SELECT * FROM sync_sessions WHERE id=?", (session_id,)).fetchone())}

    def list_conflicts(self, workspace_id: str, actor_id: str, status: str = "open") -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "reviewer")
        with self._connect() as con:
            if status:
                rows = con.execute("SELECT * FROM edge_conflicts WHERE workspace_id=? AND status=? ORDER BY created_at DESC", (workspace_id, status)).fetchall()
            else:
                rows = con.execute("SELECT * FROM edge_conflicts WHERE workspace_id=? ORDER BY created_at DESC", (workspace_id,)).fetchall()
            return {"ok": True, "version": VERSION, "conflicts": [self._conflict(r) for r in rows]}

    def resolve_conflict(self, workspace_id: str, conflict_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, conflict_id, actor_id = _id(workspace_id, "workspace ID"), _id(conflict_id, "conflict ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        resolution = _text(payload.get("resolution"), 30).lower()
        if resolution not in RESOLUTIONS:
            raise EdgeSyncError("Unsupported conflict resolution.")
        with self._connect() as con:
            row = con.execute("SELECT * FROM edge_conflicts WHERE id=? AND workspace_id=?", (conflict_id, workspace_id)).fetchone()
            if not row:
                raise EdgeSyncError("Edge synchronization conflict not found.", 404)
            if row["status"] == "resolved":
                return {"ok": True, "idempotent": True, "conflict": self._conflict(row)}
            now = _now()
            con.execute("UPDATE edge_conflicts SET status='resolved',resolution=?,resolved_by=?,resolved_at=? WHERE id=?", (resolution, actor_id, now, conflict_id))
            self._event(con, workspace_id, "conflict", conflict_id, "edge-sync-conflict-resolved", actor_id, {"resolution": resolution, "entityType": row["entity_type"], "entityId": row["entity_id"]})
            return {"ok": True, "idempotent": False, "conflict": self._conflict(con.execute("SELECT * FROM edge_conflicts WHERE id=?", (conflict_id,)).fetchone())}

    def list_sessions(self, workspace_id: str, actor_id: str, limit: int = 200) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM sync_sessions WHERE workspace_id=? ORDER BY updated_at DESC LIMIT ?", (workspace_id, max(1, min(2000, int(limit))))).fetchall()
            return {"ok": True, "version": VERSION, "sessions": [self._session(r) for r in rows]}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM edge_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(5000, int(limit))))).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": r["sequence"], "workspaceId": r["workspace_id"], "entityType": r["entity_type"], "entityId": r["entity_id"], "eventType": r["event_type"], "actorId": r["actor_id"], "details": json.loads(r["details_json"]), "eventHash": r["event_hash"], "createdAt": r["created_at"]} for r in rows]
            return {"ok": True, "version": VERSION, "events": events}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema_version = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            counts = {
                "devices": con.execute("SELECT COUNT(*) FROM edge_devices").fetchone()[0],
                "activeDevices": con.execute("SELECT COUNT(*) FROM edge_devices WHERE status='active'").fetchone()[0],
                "packages": con.execute("SELECT COUNT(*) FROM offline_packages").fetchone()[0],
                "sealedPackages": con.execute("SELECT COUNT(*) FROM offline_packages WHERE status='sealed'").fetchone()[0],
                "changes": con.execute("SELECT COUNT(*) FROM edge_changes").fetchone()[0],
                "openSessions": con.execute("SELECT COUNT(*) FROM sync_sessions WHERE status='open'").fetchone()[0],
                "completedSessions": con.execute("SELECT COUNT(*) FROM sync_sessions WHERE status='completed'").fetchone()[0],
                "openConflicts": con.execute("SELECT COUNT(*) FROM edge_conflicts WHERE status='open'").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM edge_events").fetchone()[0],
            }
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schema": "sc-lab-offline-edge-sync-health/0.36.2", "database": {"path": self.db_path, "schemaVersion": schema_version, "integrity": integrity}, "counts": counts, "offlineWorkPackages": True, "resumableSynchronization": True, "restrictedDataBytesInPackage": False, "automaticRemoteCallbacks": False, "arbitraryCode": False, "time": _now()}
