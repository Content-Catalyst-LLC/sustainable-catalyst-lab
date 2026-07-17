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
from typing import Any, Callable

VERSION = "0.36.1"
NODE_SCHEMA = "sc-lab-institutional-node/0.36.1"
DATA_SCHEMA = "sc-lab-local-data-asset/0.36.1"
REQUEST_SCHEMA = "sc-lab-local-execution-request/0.36.1"
RECEIPT_SCHEMA = "sc-lab-local-execution-receipt/0.36.1"
EVENT_SCHEMA = "sc-lab-node-federation-event/0.36.1"

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
NODE_STATUSES = {"active", "suspended", "retired"}
DATA_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
EXPORT_POLICIES = {"aggregate-only", "summary-only", "artifact-allowed"}
REQUEST_STATUSES = {"queued", "claimed", "completed", "failed", "cancelled"}
ROLE_RANK = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}


class InstitutionalNodeError(ValueError):
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
        raise InstitutionalNodeError(f"A valid {label} is required.")
    return clean


def _sha(value: Any, required: bool = True) -> str:
    clean = _text(value, 64).lower()
    if not clean and not required:
        return ""
    if not SHA_RE.match(clean):
        raise InstitutionalNodeError("A valid SHA-256 digest is required.")
    return clean


def _json_object(value: Any, limit: int = 1048576) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise InstitutionalNodeError("The value must be a JSON object.")
    clone = copy.deepcopy(value)
    if len(_stable(clone).encode("utf-8")) > limit:
        raise InstitutionalNodeError("The JSON payload exceeds the configured limit.", 413)
    forbidden = {"code", "python", "shell", "command", "callbackUrl", "callbackURL", "executable", "script"}
    if forbidden.intersection(clone):
        raise InstitutionalNodeError("Executable code, shell commands, and unrestricted callbacks are not permitted.", 422)
    return clone


def policies(max_nodes: int = 1000, max_data_assets: int = 100000, max_requests: int = 250000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-institutional-node-federation-policy/0.36.1",
        "schemas": {"node": NODE_SCHEMA, "dataAsset": DATA_SCHEMA, "request": REQUEST_SCHEMA, "receipt": RECEIPT_SCHEMA, "event": EVENT_SCHEMA},
        "classifications": sorted(DATA_CLASSIFICATIONS),
        "exportPolicies": sorted(EXPORT_POLICIES),
        "limits": {"nodes": max_nodes, "dataAssets": max_data_assets, "requests": max_requests},
        "capabilities": {
            "localDataExecution": True,
            "signedExecutionEnvelopes": True,
            "nodeAttestations": True,
            "restrictedDataStaysLocal": True,
            "aggregateResultReturn": True,
            "workspaceGovernance": True,
            "automaticRemoteCallbacks": False,
            "arbitraryCode": False,
            "rawRestrictedDataExport": False,
            "hardDelete": False,
        },
    }


class InstitutionalNodeFederation:
    def __init__(
        self,
        db_path: str,
        workspaces: Any,
        method_lookup: Callable[[str], Any] | None = None,
        coordinator_secret: str = "",
        max_nodes: int = 1000,
        max_data_assets: int = 100000,
        max_requests: int = 250000,
        history_limit: int = 100000,
    ):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.method_lookup = method_lookup
        self.coordinator_secret = coordinator_secret or "sc-lab-local-development-secret"
        self.max_nodes = max(1, int(max_nodes))
        self.max_data_assets = max(1, int(max_data_assets))
        self.max_requests = max(1, int(max_requests))
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
                CREATE TABLE IF NOT EXISTS nodes(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, title TEXT NOT NULL,
                  institution TEXT NOT NULL, status TEXT NOT NULL, endpoint_url TEXT,
                  secret TEXT NOT NULL, capabilities_json TEXT NOT NULL, allowed_methods_json TEXT NOT NULL,
                  classifications_json TEXT NOT NULL, max_concurrent INTEGER NOT NULL,
                  node_hash TEXT NOT NULL, created_by TEXT NOT NULL, created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL, last_seen_at TEXT
                );
                CREATE TABLE IF NOT EXISTS local_data_assets(
                  id TEXT PRIMARY KEY, node_id TEXT NOT NULL, workspace_id TEXT NOT NULL,
                  title TEXT NOT NULL, classification TEXT NOT NULL, export_policy TEXT NOT NULL,
                  schema_hash TEXT NOT NULL, content_hash TEXT, row_count INTEGER,
                  metadata_json TEXT NOT NULL, status TEXT NOT NULL, asset_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  FOREIGN KEY(node_id) REFERENCES nodes(id), UNIQUE(node_id,id)
                );
                CREATE TABLE IF NOT EXISTS execution_requests(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, node_id TEXT NOT NULL,
                  method_id TEXT NOT NULL, data_asset_ids_json TEXT NOT NULL,
                  parameters_json TEXT NOT NULL, output_policy TEXT NOT NULL,
                  status TEXT NOT NULL, priority INTEGER NOT NULL, envelope_json TEXT NOT NULL,
                  envelope_hash TEXT NOT NULL, coordinator_signature TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, claimed_at TEXT,
                  completed_at TEXT, cancelled_at TEXT, failure_reason TEXT,
                  FOREIGN KEY(node_id) REFERENCES nodes(id)
                );
                CREATE TABLE IF NOT EXISTS execution_receipts(
                  id TEXT PRIMARY KEY, request_id TEXT NOT NULL UNIQUE, node_id TEXT NOT NULL,
                  status TEXT NOT NULL, result_summary_json TEXT NOT NULL, result_hash TEXT NOT NULL,
                  data_access_digest TEXT NOT NULL, environment_hash TEXT NOT NULL,
                  artifact_refs_json TEXT NOT NULL, attestation_signature TEXT NOT NULL,
                  receipt_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  FOREIGN KEY(request_id) REFERENCES execution_requests(id)
                );
                CREATE TABLE IF NOT EXISTS node_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL,
                  entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, event_type TEXT NOT NULL,
                  actor_id TEXT NOT NULL, details_json TEXT NOT NULL, event_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_nodes_workspace ON nodes(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_node_data ON local_data_assets(node_id,status);
                CREATE INDEX IF NOT EXISTS idx_node_requests ON execution_requests(node_id,status,created_at);
                CREATE INDEX IF NOT EXISTS idx_node_events ON node_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT INTO meta(key,value) VALUES('schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")

    def _workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True) -> dict[str, Any]:
        try:
            body = self.workspaces.get(workspace_id, actor_id, include_members=False, include_resources=False)
        except Exception as exc:
            status = getattr(exc, "status_code", 403)
            raise InstitutionalNodeError(str(getattr(exc, "detail", exc)), status) from exc
        workspace = body["workspace"]
        if not allow_archived and workspace.get("status") == "archived":
            raise InstitutionalNodeError("The workspace is archived and read-only.", 409)
        role = ((workspace.get("currentMembership") or {}).get("role") or "viewer")
        if ROLE_RANK.get(role, 0) < ROLE_RANK[minimum]:
            raise InstitutionalNodeError(f"The {minimum} role or higher is required.", 403)
        return workspace

    def _event(self, con: sqlite3.Connection, workspace_id: str, entity_type: str, entity_id: str, event_type: str, actor_id: str, details: dict[str, Any]) -> dict[str, Any]:
        created = _now()
        payload = {"schema": EVENT_SCHEMA, "version": VERSION, "workspaceId": workspace_id, "entityType": entity_type, "entityId": entity_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created}
        event_hash = _hash(payload)
        cur = con.execute("INSERT INTO node_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)", (workspace_id, entity_type, entity_id, event_type, actor_id, _stable(details), event_hash, created))
        payload.update({"sequence": cur.lastrowid, "eventHash": event_hash})
        return payload

    @staticmethod
    def _node_record(row: sqlite3.Row, include_secret: bool = False) -> dict[str, Any]:
        record = {"schema": NODE_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "title": row["title"], "institution": row["institution"], "status": row["status"], "endpointUrl": row["endpoint_url"], "capabilities": json.loads(row["capabilities_json"]), "allowedMethods": json.loads(row["allowed_methods_json"]), "classifications": json.loads(row["classifications_json"]), "maxConcurrent": row["max_concurrent"], "nodeHash": row["node_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "lastSeenAt": row["last_seen_at"]}
        if include_secret:
            record["nodeSecret"] = row["secret"]
            record["secretNotice"] = "Store this node secret securely. It authenticates local execution claims and attestations."
        return record

    @staticmethod
    def _asset_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": DATA_SCHEMA, "version": VERSION, "id": row["id"], "nodeId": row["node_id"], "workspaceId": row["workspace_id"], "title": row["title"], "classification": row["classification"], "exportPolicy": row["export_policy"], "schemaHash": row["schema_hash"], "contentHash": row["content_hash"], "rowCount": row["row_count"], "metadata": json.loads(row["metadata_json"]), "status": row["status"], "assetHash": row["asset_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]}

    @staticmethod
    def _request_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": REQUEST_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "nodeId": row["node_id"], "methodId": row["method_id"], "dataAssetIds": json.loads(row["data_asset_ids_json"]), "parameters": json.loads(row["parameters_json"]), "outputPolicy": row["output_policy"], "status": row["status"], "priority": row["priority"], "envelope": json.loads(row["envelope_json"]), "envelopeHash": row["envelope_hash"], "coordinatorSignature": row["coordinator_signature"], "createdBy": row["created_by"], "createdAt": row["created_at"], "claimedAt": row["claimed_at"], "completedAt": row["completed_at"], "cancelledAt": row["cancelled_at"], "failureReason": row["failure_reason"]}

    @staticmethod
    def _receipt_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": RECEIPT_SCHEMA, "version": VERSION, "id": row["id"], "requestId": row["request_id"], "nodeId": row["node_id"], "status": row["status"], "resultSummary": json.loads(row["result_summary_json"]), "resultHash": row["result_hash"], "dataAccessDigest": row["data_access_digest"], "environmentHash": row["environment_hash"], "artifactRefs": json.loads(row["artifact_refs_json"]), "attestationSignature": row["attestation_signature"], "receiptHash": row["receipt_hash"], "createdAt": row["created_at"]}

    def register_node(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "administrator", False)
        node_id = _id(payload.get("id") or ("node-" + secrets.token_hex(8)), "node ID")
        title = _text(payload.get("title"), 300) or node_id
        institution = _text(payload.get("institution"), 300)
        if not institution:
            raise InstitutionalNodeError("Institution is required.")
        endpoint = _text(payload.get("endpointUrl"), 1000) or None
        if endpoint and not endpoint.startswith("https://"):
            raise InstitutionalNodeError("Institutional node endpoints must use HTTPS.")
        capabilities = _json_object(payload.get("capabilities") or {"localExecution": True, "resultAttestation": True})
        allowed = sorted({_id(item, "method ID") for item in (payload.get("allowedMethods") or [])})
        classifications = sorted(set(payload.get("classifications") or ["public", "internal"]))
        if not set(classifications).issubset(DATA_CLASSIFICATIONS):
            raise InstitutionalNodeError("Unsupported data classification.")
        max_concurrent = max(1, min(1000, int(payload.get("maxConcurrent") or 2)))
        secret = secrets.token_urlsafe(32)
        created = _now()
        identity = {"id": node_id, "workspaceId": workspace_id, "institution": institution, "endpointUrl": endpoint, "capabilities": capabilities, "allowedMethods": allowed, "classifications": classifications, "maxConcurrent": max_concurrent}
        node_hash = _hash(identity)
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] >= self.max_nodes:
                raise InstitutionalNodeError("Institutional node capacity has been reached.", 409)
            if con.execute("SELECT 1 FROM nodes WHERE id=?", (node_id,)).fetchone():
                raise InstitutionalNodeError("Institutional node already exists.", 409)
            con.execute("INSERT INTO nodes(id,workspace_id,title,institution,status,endpoint_url,secret,capabilities_json,allowed_methods_json,classifications_json,max_concurrent,node_hash,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (node_id, workspace_id, title, institution, "active", endpoint, secret, _stable(capabilities), _stable(allowed), _stable(classifications), max_concurrent, node_hash, actor_id, created, created))
            self._event(con, workspace_id, "node", node_id, "node-registered", actor_id, {"institution": institution, "nodeHash": node_hash})
            row = con.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
            return {"ok": True, "node": self._node_record(row, True)}

    def list_nodes(self, workspace_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM nodes WHERE workspace_id=? ORDER BY updated_at DESC", (workspace_id,)).fetchall()
            return {"ok": True, "version": VERSION, "nodes": [self._node_record(r) for r in rows]}

    def set_node_status(self, workspace_id: str, node_id: str, status: str, actor_id: str, reason: str = "") -> dict[str, Any]:
        workspace_id, node_id, actor_id = _id(workspace_id, "workspace ID"), _id(node_id, "node ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "administrator", False)
        if status not in NODE_STATUSES:
            raise InstitutionalNodeError("Unsupported node status.")
        reason = _text(reason, 1000)
        with self._connect() as con:
            row = con.execute("SELECT * FROM nodes WHERE id=? AND workspace_id=?", (node_id, workspace_id)).fetchone()
            if not row:
                raise InstitutionalNodeError("Institutional node not found.", 404)
            con.execute("UPDATE nodes SET status=?,updated_at=? WHERE id=?", (status, _now(), node_id))
            self._event(con, workspace_id, "node", node_id, "node-status-changed", actor_id, {"previousStatus": row["status"], "status": status, "reason": reason})
            return {"ok": True, "node": self._node_record(con.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone())}

    def register_data_asset(self, workspace_id: str, node_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, node_id, actor_id = _id(workspace_id, "workspace ID"), _id(node_id, "node ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        asset_id = _id(payload.get("id") or ("data-" + secrets.token_hex(8)), "local data asset ID")
        title = _text(payload.get("title"), 300) or asset_id
        classification = _text(payload.get("classification"), 30).lower() or "internal"
        export_policy = _text(payload.get("exportPolicy"), 30).lower() or "aggregate-only"
        if classification not in DATA_CLASSIFICATIONS or export_policy not in EXPORT_POLICIES:
            raise InstitutionalNodeError("Unsupported data classification or export policy.")
        schema_hash = _sha(payload.get("schemaHash"))
        content_hash = _sha(payload.get("contentHash"), False) or None
        row_count = payload.get("rowCount")
        if row_count is not None:
            row_count = max(0, int(row_count))
        metadata = _json_object(payload.get("metadata"))
        with self._connect() as con:
            node = con.execute("SELECT * FROM nodes WHERE id=? AND workspace_id=?", (node_id, workspace_id)).fetchone()
            if not node:
                raise InstitutionalNodeError("Institutional node not found.", 404)
            if classification not in json.loads(node["classifications_json"]):
                raise InstitutionalNodeError("The node is not approved for this data classification.", 422)
            if con.execute("SELECT COUNT(*) FROM local_data_assets").fetchone()[0] >= self.max_data_assets:
                raise InstitutionalNodeError("Local data asset capacity has been reached.", 409)
            created = _now()
            identity = {"id": asset_id, "nodeId": node_id, "workspaceId": workspace_id, "classification": classification, "exportPolicy": export_policy, "schemaHash": schema_hash, "contentHash": content_hash, "rowCount": row_count, "metadata": metadata}
            asset_hash = _hash(identity)
            try:
                con.execute("INSERT INTO local_data_assets(id,node_id,workspace_id,title,classification,export_policy,schema_hash,content_hash,row_count,metadata_json,status,asset_hash,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (asset_id, node_id, workspace_id, title, classification, export_policy, schema_hash, content_hash, row_count, _stable(metadata), "active", asset_hash, actor_id, created, created))
            except sqlite3.IntegrityError as exc:
                raise InstitutionalNodeError("Local data asset already exists.", 409) from exc
            self._event(con, workspace_id, "data-asset", asset_id, "local-data-registered", actor_id, {"nodeId": node_id, "classification": classification, "assetHash": asset_hash})
            return {"ok": True, "dataAsset": self._asset_record(con.execute("SELECT * FROM local_data_assets WHERE id=?", (asset_id,)).fetchone())}

    def list_data_assets(self, workspace_id: str, node_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, node_id, actor_id = _id(workspace_id, "workspace ID"), _id(node_id, "node ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM local_data_assets WHERE workspace_id=? AND node_id=? ORDER BY updated_at DESC", (workspace_id, node_id)).fetchall()
            return {"ok": True, "version": VERSION, "dataAssets": [self._asset_record(r) for r in rows]}

    def create_execution(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "contributor", False)
        node_id = _id(payload.get("nodeId"), "node ID")
        method_id = _id(payload.get("methodId"), "method ID")
        data_ids = [_id(x, "local data asset ID") for x in (payload.get("dataAssetIds") or [])]
        if not data_ids:
            raise InstitutionalNodeError("At least one local data asset is required.")
        parameters = _json_object(payload.get("parameters"), 2097152)
        output_policy = _text(payload.get("outputPolicy"), 30).lower() or "aggregate-only"
        if output_policy not in EXPORT_POLICIES:
            raise InstitutionalNodeError("Unsupported output policy.")
        if self.method_lookup:
            try:
                self.method_lookup(method_id)
            except Exception as exc:
                raise InstitutionalNodeError("The requested compute method is not registered.", 422) from exc
        priority = max(0, min(100, int(payload.get("priority") or 50)))
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM execution_requests").fetchone()[0] >= self.max_requests:
                raise InstitutionalNodeError("Local execution request capacity has been reached.", 409)
            node = con.execute("SELECT * FROM nodes WHERE id=? AND workspace_id=?", (node_id, workspace_id)).fetchone()
            if not node:
                raise InstitutionalNodeError("Institutional node not found.", 404)
            if node["status"] != "active":
                raise InstitutionalNodeError("Institutional node is not active.", 409)
            allowed = json.loads(node["allowed_methods_json"])
            if allowed and method_id not in allowed:
                raise InstitutionalNodeError("The method is not allowed on this institutional node.", 403)
            placeholders = ",".join("?" for _ in data_ids)
            rows = con.execute(f"SELECT * FROM local_data_assets WHERE workspace_id=? AND node_id=? AND id IN ({placeholders})", [workspace_id, node_id, *data_ids]).fetchall()
            if len(rows) != len(set(data_ids)):
                raise InstitutionalNodeError("One or more local data assets were not found.", 404)
            if any(r["status"] != "active" for r in rows):
                raise InstitutionalNodeError("All local data assets must be active.", 409)
            if any(r["classification"] in {"confidential", "restricted"} for r in rows) and output_policy == "artifact-allowed":
                raise InstitutionalNodeError("Confidential or restricted local data cannot be exported as an artifact.", 422)
            request_id = _id(payload.get("id") or ("local-run-" + secrets.token_hex(10)), "execution request ID")
            created = _now()
            envelope = {"schema": REQUEST_SCHEMA, "version": VERSION, "id": request_id, "workspaceId": workspace_id, "nodeId": node_id, "methodId": method_id, "dataAssetIds": data_ids, "dataAssetHashes": [r["asset_hash"] for r in rows], "parameters": parameters, "outputPolicy": output_policy, "priority": priority, "createdBy": actor_id, "createdAt": created, "constraints": {"rawDataExport": False, "arbitraryCode": False, "callbacks": False}}
            envelope_hash = _hash(envelope)
            signature = hmac.new(self.coordinator_secret.encode(), envelope_hash.encode(), sha256).hexdigest()
            con.execute("INSERT INTO execution_requests(id,workspace_id,node_id,method_id,data_asset_ids_json,parameters_json,output_policy,status,priority,envelope_json,envelope_hash,coordinator_signature,created_by,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (request_id, workspace_id, node_id, method_id, _stable(data_ids), _stable(parameters), output_policy, "queued", priority, _stable(envelope), envelope_hash, signature, actor_id, created))
            self._event(con, workspace_id, "execution", request_id, "local-execution-requested", actor_id, {"nodeId": node_id, "methodId": method_id, "dataAssetIds": data_ids, "envelopeHash": envelope_hash})
            return {"ok": True, "request": self._request_record(con.execute("SELECT * FROM execution_requests WHERE id=?", (request_id,)).fetchone())}

    def _verify_node_secret(self, row: sqlite3.Row, supplied: str) -> None:
        if not supplied or not hmac.compare_digest(row["secret"], supplied):
            raise InstitutionalNodeError("Institutional node authentication failed.", 401)

    def claim_execution(self, node_id: str, node_secret: str) -> dict[str, Any]:
        node_id = _id(node_id, "node ID")
        with self._connect() as con:
            node = con.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
            if not node:
                raise InstitutionalNodeError("Institutional node not found.", 404)
            self._verify_node_secret(node, node_secret)
            if node["status"] != "active":
                raise InstitutionalNodeError("Institutional node is not active.", 409)
            active = con.execute("SELECT COUNT(*) FROM execution_requests WHERE node_id=? AND status='claimed'", (node_id,)).fetchone()[0]
            if active >= node["max_concurrent"]:
                return {"ok": True, "request": None, "reason": "concurrency-limit"}
            row = con.execute("SELECT * FROM execution_requests WHERE node_id=? AND status='queued' ORDER BY priority DESC,created_at ASC LIMIT 1", (node_id,)).fetchone()
            now = _now()
            con.execute("UPDATE nodes SET last_seen_at=?,updated_at=? WHERE id=?", (now, now, node_id))
            if not row:
                return {"ok": True, "request": None, "reason": "queue-empty"}
            con.execute("UPDATE execution_requests SET status='claimed',claimed_at=? WHERE id=? AND status='queued'", (now, row["id"]))
            row = con.execute("SELECT * FROM execution_requests WHERE id=?", (row["id"],)).fetchone()
            self._event(con, row["workspace_id"], "execution", row["id"], "local-execution-claimed", node_id, {"nodeId": node_id})
            return {"ok": True, "request": self._request_record(row)}

    def complete_execution(self, node_id: str, request_id: str, payload: dict[str, Any], node_secret: str) -> dict[str, Any]:
        node_id, request_id = _id(node_id, "node ID"), _id(request_id, "execution request ID")
        status = _text(payload.get("status"), 30).lower() or "completed"
        if status not in {"completed", "failed"}:
            raise InstitutionalNodeError("Completion status must be completed or failed.")
        summary = _json_object(payload.get("resultSummary"), 1048576)
        result_hash = _sha(payload.get("resultHash"))
        data_access_digest = _sha(payload.get("dataAccessDigest"))
        environment_hash = _sha(payload.get("environmentHash"))
        artifact_refs = payload.get("artifactRefs") or []
        if not isinstance(artifact_refs, list) or len(artifact_refs) > 100:
            raise InstitutionalNodeError("artifactRefs must be a bounded list.")
        artifact_refs = [_id(x, "artifact reference") for x in artifact_refs]
        signature = _text(payload.get("attestationSignature"), 128).lower()
        with self._connect() as con:
            node = con.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
            if not node:
                raise InstitutionalNodeError("Institutional node not found.", 404)
            self._verify_node_secret(node, node_secret)
            request = con.execute("SELECT * FROM execution_requests WHERE id=? AND node_id=?", (request_id, node_id)).fetchone()
            if not request:
                raise InstitutionalNodeError("Execution request not found.", 404)
            existing = con.execute("SELECT * FROM execution_receipts WHERE request_id=?", (request_id,)).fetchone()
            if existing:
                return {"ok": True, "idempotent": True, "receipt": self._receipt_record(existing)}
            if request["status"] != "claimed":
                raise InstitutionalNodeError("Only a claimed execution can be completed.", 409)
            if request["output_policy"] != "artifact-allowed" and artifact_refs:
                raise InstitutionalNodeError("This execution policy does not allow result artifact export.", 422)
            attestation = {"requestId": request_id, "nodeId": node_id, "status": status, "resultHash": result_hash, "dataAccessDigest": data_access_digest, "environmentHash": environment_hash, "artifactRefs": artifact_refs, "resultSummary": summary}
            expected = hmac.new(node["secret"].encode(), _hash(attestation).encode(), sha256).hexdigest()
            if not signature or not hmac.compare_digest(expected, signature):
                raise InstitutionalNodeError("Execution attestation signature is invalid.", 401)
            receipt_id = "receipt-" + secrets.token_hex(12)
            created = _now()
            receipt_hash = _hash({**attestation, "id": receipt_id, "createdAt": created})
            con.execute("INSERT INTO execution_receipts(id,request_id,node_id,status,result_summary_json,result_hash,data_access_digest,environment_hash,artifact_refs_json,attestation_signature,receipt_hash,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (receipt_id, request_id, node_id, status, _stable(summary), result_hash, data_access_digest, environment_hash, _stable(artifact_refs), signature, receipt_hash, created))
            con.execute("UPDATE execution_requests SET status=?,completed_at=?,failure_reason=? WHERE id=?", (status, created, _text(payload.get("failureReason"), 2000) or None, request_id))
            self._event(con, request["workspace_id"], "execution", request_id, "local-execution-attested", node_id, {"status": status, "resultHash": result_hash, "receiptHash": receipt_hash})
            return {"ok": True, "idempotent": False, "receipt": self._receipt_record(con.execute("SELECT * FROM execution_receipts WHERE id=?", (receipt_id,)).fetchone())}

    def list_executions(self, workspace_id: str, actor_id: str, node_id: str = "", status: str = "", limit: int = 200) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        clauses, args = ["workspace_id=?"], [workspace_id]
        if node_id:
            clauses.append("node_id=?"); args.append(_id(node_id, "node ID"))
        if status:
            if status not in REQUEST_STATUSES:
                raise InstitutionalNodeError("Unsupported execution status.")
            clauses.append("status=?"); args.append(status)
        args.append(max(1, min(2000, int(limit))))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM execution_requests WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT ?", args).fetchall()
            records = []
            for row in rows:
                record = self._request_record(row)
                receipt = con.execute("SELECT * FROM execution_receipts WHERE request_id=?", (row["id"],)).fetchone()
                record["receipt"] = self._receipt_record(receipt) if receipt else None
                records.append(record)
            return {"ok": True, "version": VERSION, "requests": records}

    def cancel_execution(self, workspace_id: str, request_id: str, actor_id: str, reason: str) -> dict[str, Any]:
        workspace_id, request_id, actor_id = _id(workspace_id, "workspace ID"), _id(request_id, "execution request ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "editor", False)
        reason = _text(reason, 1000)
        if not reason:
            raise InstitutionalNodeError("A cancellation reason is required.")
        with self._connect() as con:
            row = con.execute("SELECT * FROM execution_requests WHERE id=? AND workspace_id=?", (request_id, workspace_id)).fetchone()
            if not row:
                raise InstitutionalNodeError("Execution request not found.", 404)
            if row["status"] not in {"queued", "claimed"}:
                raise InstitutionalNodeError("Only queued or claimed requests can be cancelled.", 409)
            now = _now()
            con.execute("UPDATE execution_requests SET status='cancelled',cancelled_at=?,failure_reason=? WHERE id=?", (now, reason, request_id))
            self._event(con, workspace_id, "execution", request_id, "local-execution-cancelled", actor_id, {"reason": reason})
            return {"ok": True, "request": self._request_record(con.execute("SELECT * FROM execution_requests WHERE id=?", (request_id,)).fetchone())}

    def verify_envelope(self, payload: dict[str, Any]) -> dict[str, Any]:
        envelope = payload.get("envelope")
        if not isinstance(envelope, dict):
            raise InstitutionalNodeError("An execution envelope is required.")
        envelope_hash = _sha(payload.get("envelopeHash"))
        signature = _text(payload.get("coordinatorSignature"), 128).lower()
        calculated = _hash(envelope)
        expected = hmac.new(self.coordinator_secret.encode(), calculated.encode(), sha256).hexdigest()
        return {"ok": calculated == envelope_hash and hmac.compare_digest(expected, signature), "calculatedHash": calculated, "declaredHash": envelope_hash, "signatureValid": hmac.compare_digest(expected, signature)}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        self._workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM node_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(5000, int(limit))))).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": r["sequence"], "workspaceId": r["workspace_id"], "entityType": r["entity_type"], "entityId": r["entity_id"], "eventType": r["event_type"], "actorId": r["actor_id"], "details": json.loads(r["details_json"]), "eventHash": r["event_hash"], "createdAt": r["created_at"]} for r in rows]
            return {"ok": True, "version": VERSION, "events": events}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema_version = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            counts = {
                "nodes": con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0],
                "activeNodes": con.execute("SELECT COUNT(*) FROM nodes WHERE status='active'").fetchone()[0],
                "dataAssets": con.execute("SELECT COUNT(*) FROM local_data_assets").fetchone()[0],
                "queuedRequests": con.execute("SELECT COUNT(*) FROM execution_requests WHERE status='queued'").fetchone()[0],
                "claimedRequests": con.execute("SELECT COUNT(*) FROM execution_requests WHERE status='claimed'").fetchone()[0],
                "completedRequests": con.execute("SELECT COUNT(*) FROM execution_requests WHERE status='completed'").fetchone()[0],
                "receipts": con.execute("SELECT COUNT(*) FROM execution_receipts").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM node_events").fetchone()[0],
            }
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schema": "sc-lab-institutional-node-federation-health/0.36.1", "database": {"path": self.db_path, "schemaVersion": schema_version, "integrity": integrity}, "counts": counts, "localDataExecution": True, "restrictedDataStaysLocal": True, "automaticRemoteCallbacks": False, "arbitraryCode": False, "time": _now()}
