from __future__ import annotations

import copy
import json
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

VERSION = "0.36.0"
COLLECTION_SCHEMA = "sc-lab-artifact-collection/0.36.0"
RECORD_SCHEMA = "sc-lab-repository-artifact/0.36.0"
SOURCE_SCHEMA = "sc-lab-federated-source/0.36.0"
MANIFEST_SCHEMA = "sc-lab-federation-manifest/0.36.0"
SYNC_SCHEMA = "sc-lab-federation-sync/0.36.0"
CONFLICT_SCHEMA = "sc-lab-federation-conflict/0.36.0"
EVENT_SCHEMA = "sc-lab-artifact-repository-event/0.36.0"

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SEMVER_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){0,3}(?:[-+][A-Za-z0-9._-]+)?$")
ARTIFACT_TYPES = {
    "dataset", "result", "checkpoint", "model", "surrogate", "ensemble",
    "notebook", "report", "figure", "source", "evidence", "provenance",
    "workflow", "environment", "software", "other",
}
VISIBILITIES = {"private", "workspace", "public"}
SOURCE_TYPES = {"sc-lab-node", "institutional-repository", "object-store", "manifest-feed"}
TRUST_MODES = {"strict", "hash-verified", "manual-review"}
CONFLICT_POLICIES = {"reject", "retain-both", "prefer-newer"}


class ArtifactRepositoryError(ValueError):
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
        raise ArtifactRepositoryError(f"A valid {label} is required.")
    return clean


def _sha(value: Any, required: bool = True) -> str:
    clean = _text(value, 64).lower()
    if not clean and not required:
        return ""
    if not SHA_RE.match(clean):
        raise ArtifactRepositoryError("A valid SHA-256 digest is required.")
    return clean


def _version(value: Any) -> str:
    clean = _text(value, 80) or "1.0.0"
    if not SEMVER_RE.match(clean):
        raise ArtifactRepositoryError("Artifact version must use a numeric semantic-version form.")
    return clean


def _safe_json(value: Any, max_bytes: int = 262144) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ArtifactRepositoryError("Metadata and provenance values must be JSON objects.")
    clone = copy.deepcopy(value)
    if len(_stable(clone).encode("utf-8")) > max_bytes:
        raise ArtifactRepositoryError("The JSON metadata payload exceeds the configured limit.", 413)
    return clone


def policies(max_collections: int = 5000, max_records: int = 250000, max_manifest_records: int = 10000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-artifact-repository-policy/0.36.0",
        "schemas": {
            "collection": COLLECTION_SCHEMA,
            "record": RECORD_SCHEMA,
            "source": SOURCE_SCHEMA,
            "manifest": MANIFEST_SCHEMA,
            "sync": SYNC_SCHEMA,
            "conflict": CONFLICT_SCHEMA,
            "event": EVENT_SCHEMA,
        },
        "artifactTypes": sorted(ARTIFACT_TYPES),
        "sourceTypes": sorted(SOURCE_TYPES),
        "trustModes": sorted(TRUST_MODES),
        "conflictPolicies": sorted(CONFLICT_POLICIES),
        "limits": {"collections": max_collections, "records": max_records, "manifestRecords": max_manifest_records},
        "capabilities": {
            "contentAddressedReferences": True,
            "immutableVersionRecords": True,
            "workspaceGovernance": True,
            "collectionManifests": True,
            "manifestFederation": True,
            "deltaSynchronization": True,
            "tombstones": True,
            "conflictRecords": True,
            "integrityVerification": True,
            "automaticRemoteCallbacks": False,
            "arbitraryCode": False,
            "hardDelete": False,
        },
    }


class ScientificArtifactRepository:
    def __init__(
        self,
        db_path: str,
        workspaces: Any,
        artifact_lookup: Callable[[str], dict[str, Any]] | None = None,
        max_collections: int = 5000,
        max_records: int = 250000,
        max_manifest_records: int = 10000,
        history_limit: int = 100000,
    ):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.artifact_lookup = artifact_lookup
        self.max_collections = max(1, int(max_collections))
        self.max_records = max(100, int(max_records))
        self.max_manifest_records = max(1, int(max_manifest_records))
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
                CREATE TABLE IF NOT EXISTS collections(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, title TEXT NOT NULL,
                  description TEXT, visibility TEXT NOT NULL, status TEXT NOT NULL,
                  metadata_json TEXT NOT NULL, collection_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  archived_at TEXT
                );
                CREATE TABLE IF NOT EXISTS repository_artifacts(
                  id TEXT PRIMARY KEY, collection_id TEXT NOT NULL, workspace_id TEXT NOT NULL,
                  transport_artifact_id TEXT, title TEXT NOT NULL, artifact_type TEXT NOT NULL,
                  version TEXT NOT NULL, media_type TEXT NOT NULL, sha256 TEXT NOT NULL,
                  size_bytes INTEGER NOT NULL, canonical_uri TEXT, origin_node_id TEXT,
                  source_id TEXT, remote_id TEXT, remote_version TEXT,
                  provenance_json TEXT NOT NULL, metadata_json TEXT NOT NULL,
                  status TEXT NOT NULL, integrity_state TEXT NOT NULL, record_hash TEXT NOT NULL,
                  modified_at TEXT, created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  FOREIGN KEY(collection_id) REFERENCES collections(id),
                  UNIQUE(collection_id,canonical_uri,version),
                  UNIQUE(source_id,remote_id,remote_version)
                );
                CREATE TABLE IF NOT EXISTS federated_sources(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, title TEXT NOT NULL,
                  node_id TEXT NOT NULL, source_type TEXT NOT NULL, endpoint_url TEXT,
                  trust_mode TEXT NOT NULL, conflict_policy TEXT NOT NULL, status TEXT NOT NULL,
                  metadata_json TEXT NOT NULL, source_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  last_sync_at TEXT
                );
                CREATE TABLE IF NOT EXISTS sync_runs(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, source_id TEXT NOT NULL,
                  manifest_hash TEXT NOT NULL, cursor_value TEXT, status TEXT NOT NULL,
                  imported_count INTEGER NOT NULL, updated_count INTEGER NOT NULL,
                  unchanged_count INTEGER NOT NULL, conflict_count INTEGER NOT NULL,
                  tombstoned_count INTEGER NOT NULL, details_json TEXT NOT NULL,
                  run_hash TEXT NOT NULL, started_by TEXT NOT NULL, started_at TEXT NOT NULL,
                  completed_at TEXT NOT NULL,
                  FOREIGN KEY(source_id) REFERENCES federated_sources(id)
                );
                CREATE TABLE IF NOT EXISTS federation_conflicts(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, source_id TEXT NOT NULL,
                  collection_id TEXT NOT NULL, canonical_uri TEXT NOT NULL,
                  local_artifact_id TEXT, incoming_json TEXT NOT NULL, reason TEXT NOT NULL,
                  status TEXT NOT NULL, resolution TEXT, resolved_by TEXT, resolved_at TEXT,
                  conflict_hash TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS repository_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL,
                  entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, event_type TEXT NOT NULL,
                  actor_id TEXT NOT NULL, details_json TEXT NOT NULL, event_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_repo_collections_workspace ON collections(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_repo_artifacts_collection ON repository_artifacts(collection_id,status,created_at);
                CREATE INDEX IF NOT EXISTS idx_repo_artifacts_source ON repository_artifacts(source_id,remote_id,remote_version);
                CREATE INDEX IF NOT EXISTS idx_repo_sources_workspace ON federated_sources(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_repo_sync_source ON sync_runs(source_id,started_at);
                CREATE INDEX IF NOT EXISTS idx_repo_conflicts_workspace ON federation_conflicts(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_repo_events_workspace ON repository_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version','1')")

    def _authorize(self, workspace_id: str, actor_id: str, action: str) -> None:
        try:
            decision = self.workspaces.authorize(workspace_id, {"action": action}, actor_id)["decision"]
        except Exception as exc:
            status = getattr(exc, "status_code", 403)
            detail = getattr(exc, "detail", str(exc))
            raise ArtifactRepositoryError(detail, status) from exc
        if not decision.get("allowed"):
            raise ArtifactRepositoryError("Workspace permission is required for this repository operation.", 403)

    def _event(self, con: sqlite3.Connection, workspace_id: str, entity_type: str, entity_id: str, event_type: str, actor_id: str, details: dict[str, Any]) -> None:
        created_at = _now()
        event_hash = _hash({"workspaceId": workspace_id, "entityType": entity_type, "entityId": entity_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created_at})
        con.execute(
            "INSERT INTO repository_events(workspace_id,entity_type,entity_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (workspace_id, entity_type, entity_id, event_type, actor_id, _stable(details), event_hash, created_at),
        )

    @staticmethod
    def _collection(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": COLLECTION_SCHEMA, "version": VERSION, "id": row["id"],
            "workspaceId": row["workspace_id"], "title": row["title"],
            "description": row["description"], "visibility": row["visibility"],
            "status": row["status"], "metadata": json.loads(row["metadata_json"]),
            "collectionHash": row["collection_hash"], "createdBy": row["created_by"],
            "createdAt": row["created_at"], "updatedAt": row["updated_at"],
            "archivedAt": row["archived_at"],
        }

    @staticmethod
    def _record(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": RECORD_SCHEMA, "version": VERSION, "id": row["id"],
            "collectionId": row["collection_id"], "workspaceId": row["workspace_id"],
            "transportArtifactId": row["transport_artifact_id"], "title": row["title"],
            "artifactType": row["artifact_type"], "artifactVersion": row["version"],
            "mediaType": row["media_type"], "sha256": row["sha256"],
            "sizeBytes": row["size_bytes"], "canonicalUri": row["canonical_uri"],
            "originNodeId": row["origin_node_id"], "sourceId": row["source_id"],
            "remoteId": row["remote_id"], "remoteVersion": row["remote_version"],
            "provenance": json.loads(row["provenance_json"]), "metadata": json.loads(row["metadata_json"]),
            "status": row["status"], "integrityState": row["integrity_state"],
            "recordHash": row["record_hash"], "modifiedAt": row["modified_at"],
            "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        }

    @staticmethod
    def _source(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": SOURCE_SCHEMA, "version": VERSION, "id": row["id"],
            "workspaceId": row["workspace_id"], "title": row["title"], "nodeId": row["node_id"],
            "sourceType": row["source_type"], "endpointUrl": row["endpoint_url"],
            "trustMode": row["trust_mode"], "conflictPolicy": row["conflict_policy"],
            "status": row["status"], "metadata": json.loads(row["metadata_json"]),
            "sourceHash": row["source_hash"], "createdBy": row["created_by"],
            "createdAt": row["created_at"], "updatedAt": row["updated_at"], "lastSyncAt": row["last_sync_at"],
        }

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            counts = {
                "collections": con.execute("SELECT COUNT(*) FROM collections").fetchone()[0],
                "artifacts": con.execute("SELECT COUNT(*) FROM repository_artifacts").fetchone()[0],
                "activeArtifacts": con.execute("SELECT COUNT(*) FROM repository_artifacts WHERE status='active'").fetchone()[0],
                "sources": con.execute("SELECT COUNT(*) FROM federated_sources").fetchone()[0],
                "syncRuns": con.execute("SELECT COUNT(*) FROM sync_runs").fetchone()[0],
                "openConflicts": con.execute("SELECT COUNT(*) FROM federation_conflicts WHERE status='open'").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM repository_events").fetchone()[0],
            }
            schema_version = con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]
        return {"ok": True, "status": "ready", "version": VERSION, "database": {"path": self.db_path, "schemaVersion": int(schema_version), "journalMode": "WAL"}, "counts": counts}

    def create_collection(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "resource.link")
        title = _text(payload.get("title"), 300)
        if not title:
            raise ArtifactRepositoryError("A collection title is required.")
        collection_id = _id(payload.get("id") or f"collection-{secrets.token_hex(8)}", "collection ID")
        visibility = _text(payload.get("visibility"), 40).lower() or "workspace"
        if visibility not in VISIBILITIES:
            raise ArtifactRepositoryError("Unsupported collection visibility.")
        metadata = _safe_json(payload.get("metadata"))
        description = _text(payload.get("description"), 4000)
        now = _now()
        collection_hash = _hash({"id": collection_id, "workspaceId": workspace_id, "title": title, "description": description, "visibility": visibility, "metadata": metadata})
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) FROM collections").fetchone()[0] >= self.max_collections:
                raise ArtifactRepositoryError("The artifact collection limit has been reached.", 409)
            try:
                con.execute("INSERT INTO collections(id,workspace_id,title,description,visibility,status,metadata_json,collection_hash,created_by,created_at,updated_at,archived_at) VALUES(?,?,?,?,?,'active',?,?,?,?,?,NULL)", (collection_id, workspace_id, title, description, visibility, _stable(metadata), collection_hash, actor_id, now, now))
            except sqlite3.IntegrityError as exc:
                raise ArtifactRepositoryError("The collection ID already exists.", 409) from exc
            self._event(con, workspace_id, "collection", collection_id, "collection-created", actor_id, {"collectionHash": collection_hash, "visibility": visibility})
            row = con.execute("SELECT * FROM collections WHERE id=?", (collection_id,)).fetchone()
        try:
            self.workspaces.link_resource(workspace_id, {"resourceType": "artifact-collection", "resourceId": collection_id, "title": title, "minimumRole": "viewer", "metadata": {"collectionHash": collection_hash}}, actor_id)
        except Exception:
            pass
        return {"ok": True, "collection": self._collection(row)}

    def list_collections(self, workspace_id: str, actor_id: str, status: str = "", limit: int = 100) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        sql = "SELECT * FROM collections WHERE workspace_id=?"; params: list[Any] = [workspace_id]
        if status:
            sql += " AND status=?"; params.append(_text(status, 40).lower())
        sql += " ORDER BY updated_at DESC LIMIT ?"; params.append(max(1, min(int(limit), 1000)))
        with self._connect() as con:
            rows = con.execute(sql, params).fetchall()
        return {"ok": True, "collections": [self._collection(row) for row in rows]}

    def get_collection(self, workspace_id: str, collection_id: str, actor_id: str, include_artifacts: bool = True) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); collection_id = _id(collection_id, "collection ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        with self._connect() as con:
            row = con.execute("SELECT * FROM collections WHERE id=? AND workspace_id=?", (collection_id, workspace_id)).fetchone()
            if not row:
                raise ArtifactRepositoryError("Artifact collection not found.", 404)
            result = {"ok": True, "collection": self._collection(row)}
            if include_artifacts:
                records = con.execute("SELECT * FROM repository_artifacts WHERE collection_id=? ORDER BY created_at DESC LIMIT 5000", (collection_id,)).fetchall()
                result["artifacts"] = [self._record(item) for item in records]
            return result

    def archive_collection(self, workspace_id: str, collection_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); collection_id = _id(collection_id, "collection ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.update")
        reason = _text(payload.get("reason"), 1000)
        if not reason:
            raise ArtifactRepositoryError("An archive reason is required.")
        now = _now()
        with self._connect() as con:
            row = con.execute("SELECT * FROM collections WHERE id=? AND workspace_id=?", (collection_id, workspace_id)).fetchone()
            if not row:
                raise ArtifactRepositoryError("Artifact collection not found.", 404)
            con.execute("UPDATE collections SET status='archived',archived_at=?,updated_at=? WHERE id=?", (now, now, collection_id))
            self._event(con, workspace_id, "collection", collection_id, "collection-archived", actor_id, {"reason": reason})
            updated = con.execute("SELECT * FROM collections WHERE id=?", (collection_id,)).fetchone()
        return {"ok": True, "collection": self._collection(updated)}

    def _normalize_record(self, collection: sqlite3.Row, payload: dict[str, Any], actor_id: str, source_id: str = "") -> dict[str, Any]:
        artifact_type = _text(payload.get("artifactType"), 80).lower() or "other"
        if artifact_type not in ARTIFACT_TYPES:
            raise ArtifactRepositoryError("Unsupported repository artifact type.")
        transport_id = _text(payload.get("transportArtifactId"), 180)
        transport_record: dict[str, Any] | None = None
        if transport_id:
            if not self.artifact_lookup:
                raise ArtifactRepositoryError("Artifact transport lookup is unavailable.", 503)
            try:
                response = self.artifact_lookup(transport_id)
                transport_record = response.get("artifact", response)
            except Exception as exc:
                raise ArtifactRepositoryError("The referenced transport artifact was not found.", 404) from exc
        digest = _sha(payload.get("sha256") or (transport_record or {}).get("sha256"))
        size_bytes = payload.get("sizeBytes", (transport_record or {}).get("sizeBytes"))
        try:
            size_bytes = int(size_bytes)
        except (TypeError, ValueError) as exc:
            raise ArtifactRepositoryError("Artifact size must be an integer.") from exc
        if size_bytes < 0:
            raise ArtifactRepositoryError("Artifact size cannot be negative.")
        if transport_record:
            if digest != transport_record.get("sha256") or size_bytes != int(transport_record.get("sizeBytes", -1)):
                raise ArtifactRepositoryError("Repository metadata does not match the transport artifact.", 422)
        title = _text(payload.get("title"), 300) or _text((transport_record or {}).get("filename"), 300) or digest[:16]
        version = _version(payload.get("artifactVersion") or payload.get("version"))
        media_type = _text(payload.get("mediaType") or (transport_record or {}).get("mediaType"), 160) or "application/octet-stream"
        canonical_uri = _text(payload.get("canonicalUri"), 1000) or f"urn:sha256:{digest}"
        modified_at = _text(payload.get("modifiedAt"), 80) or None
        metadata = _safe_json(payload.get("metadata")); provenance = _safe_json(payload.get("provenance"))
        normalized = {
            "collectionId": collection["id"], "workspaceId": collection["workspace_id"],
            "transportArtifactId": transport_id or None, "title": title, "artifactType": artifact_type,
            "artifactVersion": version, "mediaType": media_type, "sha256": digest,
            "sizeBytes": size_bytes, "canonicalUri": canonical_uri,
            "originNodeId": _text(payload.get("originNodeId"), 180) or None,
            "sourceId": source_id or _text(payload.get("sourceId"), 180) or None,
            "remoteId": _text(payload.get("remoteId"), 180) or None,
            "remoteVersion": _text(payload.get("remoteVersion"), 80) or None,
            "provenance": provenance, "metadata": metadata, "status": _text(payload.get("status"), 40).lower() or "active",
            "integrityState": "transport-verified" if transport_record else "metadata-verified",
            "modifiedAt": modified_at, "createdBy": actor_id,
        }
        normalized["recordHash"] = _hash(normalized)
        return normalized

    def register_artifact(self, workspace_id: str, collection_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); collection_id = _id(collection_id, "collection ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "resource.link")
        with self._connect() as con:
            collection = con.execute("SELECT * FROM collections WHERE id=? AND workspace_id=?", (collection_id, workspace_id)).fetchone()
            if not collection:
                raise ArtifactRepositoryError("Artifact collection not found.", 404)
            if collection["status"] != "active":
                raise ArtifactRepositoryError("Archived collections are read-only.", 409)
            if con.execute("SELECT COUNT(*) FROM repository_artifacts").fetchone()[0] >= self.max_records:
                raise ArtifactRepositoryError("The repository artifact limit has been reached.", 409)
            record = self._normalize_record(collection, payload, actor_id)
            artifact_id = _id(payload.get("id") or f"repo-{record['sha256'][:20]}-{secrets.token_hex(4)}", "repository artifact ID")
            now = _now()
            try:
                con.execute(
                    """INSERT INTO repository_artifacts(id,collection_id,workspace_id,transport_artifact_id,title,artifact_type,version,media_type,sha256,size_bytes,canonical_uri,origin_node_id,source_id,remote_id,remote_version,provenance_json,metadata_json,status,integrity_state,record_hash,modified_at,created_by,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (artifact_id, collection_id, workspace_id, record["transportArtifactId"], record["title"], record["artifactType"], record["artifactVersion"], record["mediaType"], record["sha256"], record["sizeBytes"], record["canonicalUri"], record["originNodeId"], record["sourceId"], record["remoteId"], record["remoteVersion"], _stable(record["provenance"]), _stable(record["metadata"]), record["status"], record["integrityState"], record["recordHash"], record["modifiedAt"], actor_id, now, now),
                )
            except sqlite3.IntegrityError as exc:
                existing = con.execute("SELECT * FROM repository_artifacts WHERE collection_id=? AND canonical_uri=? AND version=?", (collection_id, record["canonicalUri"], record["artifactVersion"])).fetchone()
                if existing and existing["record_hash"] == record["recordHash"]:
                    return {"ok": True, "idempotent": True, "artifact": self._record(existing)}
                raise ArtifactRepositoryError("An artifact version with this canonical URI already exists.", 409) from exc
            self._event(con, workspace_id, "artifact", artifact_id, "artifact-registered", actor_id, {"collectionId": collection_id, "recordHash": record["recordHash"], "sha256": record["sha256"]})
            row = con.execute("SELECT * FROM repository_artifacts WHERE id=?", (artifact_id,)).fetchone()
        return {"ok": True, "idempotent": False, "artifact": self._record(row)}

    def verify_artifact(self, workspace_id: str, artifact_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); artifact_id = _id(artifact_id, "artifact ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        with self._connect() as con:
            row = con.execute("SELECT * FROM repository_artifacts WHERE id=? AND workspace_id=?", (artifact_id, workspace_id)).fetchone()
            if not row:
                raise ArtifactRepositoryError("Repository artifact not found.", 404)
            record = self._record(row)
            expected_hash = record.pop("recordHash")
            canonical = {
                "collectionId": record["collectionId"], "workspaceId": record["workspaceId"], "transportArtifactId": record["transportArtifactId"],
                "title": record["title"], "artifactType": record["artifactType"], "artifactVersion": record["artifactVersion"], "mediaType": record["mediaType"],
                "sha256": record["sha256"], "sizeBytes": record["sizeBytes"], "canonicalUri": record["canonicalUri"], "originNodeId": record["originNodeId"],
                "sourceId": record["sourceId"], "remoteId": record["remoteId"], "remoteVersion": record["remoteVersion"], "provenance": record["provenance"],
                "metadata": record["metadata"], "status": record["status"], "integrityState": record["integrityState"], "modifiedAt": record["modifiedAt"], "createdBy": record["createdBy"],
            }
            record_hash_ok = _hash(canonical) == expected_hash
            transport_ok: bool | None = None
            if row["transport_artifact_id"] and self.artifact_lookup:
                try:
                    lookup = self.artifact_lookup(row["transport_artifact_id"]); transport = lookup.get("artifact", lookup)
                    transport_ok = transport.get("sha256") == row["sha256"] and int(transport.get("sizeBytes", -1)) == row["size_bytes"]
                except Exception:
                    transport_ok = False
            verified = record_hash_ok and transport_ok is not False
            result = {"artifactId": artifact_id, "recordHashVerified": record_hash_ok, "transportVerified": transport_ok, "verified": verified, "verifiedAt": _now()}
            result["verificationHash"] = _hash(result)
            self._event(con, workspace_id, "artifact", artifact_id, "artifact-verified", actor_id, result)
            return {"ok": True, "verification": result}

    def export_manifest(self, workspace_id: str, collection_id: str, actor_id: str, node_id: str = "local-node") -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); collection_id = _id(collection_id, "collection ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        with self._connect() as con:
            collection = con.execute("SELECT * FROM collections WHERE id=? AND workspace_id=?", (collection_id, workspace_id)).fetchone()
            if not collection:
                raise ArtifactRepositoryError("Artifact collection not found.", 404)
            rows = con.execute("SELECT * FROM repository_artifacts WHERE collection_id=? ORDER BY canonical_uri,version,id", (collection_id,)).fetchall()
        manifest = {
            "schema": MANIFEST_SCHEMA, "version": VERSION, "nodeId": _id(node_id, "node ID"),
            "generatedAt": _now(), "cursor": str(len(rows)),
            "collection": {"id": collection_id, "title": collection["title"], "visibility": collection["visibility"], "collectionHash": collection["collection_hash"]},
            "artifacts": [
                {
                    "remoteId": row["id"], "artifactVersion": row["version"], "title": row["title"], "artifactType": row["artifact_type"],
                    "mediaType": row["media_type"], "sha256": row["sha256"], "sizeBytes": row["size_bytes"], "canonicalUri": row["canonical_uri"],
                    "modifiedAt": row["modified_at"], "status": row["status"], "originNodeId": row["origin_node_id"] or _id(node_id, "node ID"),
                    "provenance": json.loads(row["provenance_json"]), "metadata": json.loads(row["metadata_json"]),
                } for row in rows
            ],
        }
        manifest["manifestHash"] = _hash(manifest)
        return {"ok": True, "manifest": manifest}

    def register_source(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "member.invite")
        source_id = _id(payload.get("id") or f"source-{secrets.token_hex(8)}", "source ID")
        title = _text(payload.get("title"), 300)
        if not title:
            raise ArtifactRepositoryError("A federated source title is required.")
        node_id = _id(payload.get("nodeId"), "federated node ID")
        source_type = _text(payload.get("sourceType"), 80).lower() or "manifest-feed"
        trust_mode = _text(payload.get("trustMode"), 40).lower() or "strict"
        conflict_policy = _text(payload.get("conflictPolicy"), 40).lower() or "reject"
        if source_type not in SOURCE_TYPES or trust_mode not in TRUST_MODES or conflict_policy not in CONFLICT_POLICIES:
            raise ArtifactRepositoryError("Unsupported federated-source policy.")
        endpoint_url = _text(payload.get("endpointUrl"), 1000)
        if endpoint_url and not endpoint_url.startswith("https://"):
            raise ArtifactRepositoryError("Federated source endpoints must use HTTPS.")
        metadata = _safe_json(payload.get("metadata")); now = _now()
        source_hash = _hash({"id": source_id, "workspaceId": workspace_id, "title": title, "nodeId": node_id, "sourceType": source_type, "endpointUrl": endpoint_url, "trustMode": trust_mode, "conflictPolicy": conflict_policy, "metadata": metadata})
        with self._connect() as con:
            try:
                con.execute("INSERT INTO federated_sources(id,workspace_id,title,node_id,source_type,endpoint_url,trust_mode,conflict_policy,status,metadata_json,source_hash,created_by,created_at,updated_at,last_sync_at) VALUES(?,?,?,?,?,?,?,?, 'active',?,?,?,?,?,NULL)", (source_id, workspace_id, title, node_id, source_type, endpoint_url or None, trust_mode, conflict_policy, _stable(metadata), source_hash, actor_id, now, now))
            except sqlite3.IntegrityError as exc:
                raise ArtifactRepositoryError("The federated source ID already exists.", 409) from exc
            self._event(con, workspace_id, "source", source_id, "source-registered", actor_id, {"sourceHash": source_hash, "trustMode": trust_mode, "conflictPolicy": conflict_policy})
            row = con.execute("SELECT * FROM federated_sources WHERE id=?", (source_id,)).fetchone()
        try:
            self.workspaces.link_resource(workspace_id, {"resourceType": "federated-source", "resourceId": source_id, "title": title, "minimumRole": "reviewer", "metadata": {"sourceHash": source_hash}}, actor_id)
        except Exception:
            pass
        return {"ok": True, "source": self._source(row)}

    def list_sources(self, workspace_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM federated_sources WHERE workspace_id=? ORDER BY updated_at DESC", (workspace_id,)).fetchall()
        return {"ok": True, "sources": [self._source(row) for row in rows]}

    def _manifest_hash(self, manifest: dict[str, Any]) -> str:
        clone = copy.deepcopy(manifest); clone.pop("manifestHash", None)
        return _hash(clone)

    def sync_manifest(self, workspace_id: str, source_id: str, collection_id: str, manifest: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); source_id = _id(source_id, "source ID"); collection_id = _id(collection_id, "collection ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "resource.link")
        if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("version") != VERSION:
            raise ArtifactRepositoryError("The federation manifest schema is not supported.")
        records = manifest.get("artifacts")
        if not isinstance(records, list):
            raise ArtifactRepositoryError("The federation manifest must contain an artifact list.")
        if len(records) > self.max_manifest_records:
            raise ArtifactRepositoryError("The federation manifest exceeds the configured record limit.", 413)
        calculated_hash = self._manifest_hash(manifest)
        provided_hash = _text(manifest.get("manifestHash"), 64).lower()
        with self._connect() as con:
            source = con.execute("SELECT * FROM federated_sources WHERE id=? AND workspace_id=?", (source_id, workspace_id)).fetchone()
            collection = con.execute("SELECT * FROM collections WHERE id=? AND workspace_id=?", (collection_id, workspace_id)).fetchone()
            if not source or not collection:
                raise ArtifactRepositoryError("The federated source or target collection was not found.", 404)
            if source["status"] != "active" or collection["status"] != "active":
                raise ArtifactRepositoryError("The source and target collection must both be active.", 409)
            if manifest.get("nodeId") != source["node_id"]:
                raise ArtifactRepositoryError("The federation manifest node does not match the registered source.", 422)
            if source["trust_mode"] in {"strict", "hash-verified"} and (not provided_hash or not secrets.compare_digest(provided_hash, calculated_hash)):
                raise ArtifactRepositoryError("Federation manifest hash verification failed.", 422)
            run_id = f"sync-{secrets.token_hex(10)}"; started = _now()
            counts = {"imported": 0, "updated": 0, "unchanged": 0, "conflicts": 0, "tombstoned": 0}
            conflict_ids: list[str] = []
            for raw in records:
                if not isinstance(raw, dict):
                    raise ArtifactRepositoryError("Every federation artifact record must be an object.")
                remote_id = _id(raw.get("remoteId"), "remote artifact ID")
                remote_version = _version(raw.get("artifactVersion") or raw.get("version"))
                digest = _sha(raw.get("sha256")); canonical_uri = _text(raw.get("canonicalUri"), 1000) or f"urn:sha256:{digest}"
                status = _text(raw.get("status"), 40).lower() or "active"
                existing = con.execute("SELECT * FROM repository_artifacts WHERE source_id=? AND remote_id=? AND remote_version=?", (source_id, remote_id, remote_version)).fetchone()
                if status in {"tombstoned", "deleted"}:
                    if existing and existing["status"] != "tombstoned":
                        con.execute("UPDATE repository_artifacts SET status='tombstoned',updated_at=? WHERE id=?", (_now(), existing["id"])); counts["tombstoned"] += 1
                    else:
                        counts["unchanged"] += 1
                    continue
                payload = copy.deepcopy(raw)
                payload.update({"sourceId": source_id, "remoteId": remote_id, "remoteVersion": remote_version, "originNodeId": raw.get("originNodeId") or source["node_id"], "artifactVersion": remote_version})
                normalized = self._normalize_record(collection, payload, actor_id, source_id)
                if existing:
                    if existing["record_hash"] == normalized["recordHash"]:
                        counts["unchanged"] += 1; continue
                    if source["conflict_policy"] == "prefer-newer" and normalized["modifiedAt"] > (existing["modified_at"] or ""):
                        con.execute("UPDATE repository_artifacts SET title=?,artifact_type=?,media_type=?,sha256=?,size_bytes=?,canonical_uri=?,origin_node_id=?,provenance_json=?,metadata_json=?,status='active',integrity_state=?,record_hash=?,modified_at=?,updated_at=? WHERE id=?", (normalized["title"], normalized["artifactType"], normalized["mediaType"], normalized["sha256"], normalized["sizeBytes"], normalized["canonicalUri"], normalized["originNodeId"], _stable(normalized["provenance"]), _stable(normalized["metadata"]), normalized["integrityState"], normalized["recordHash"], normalized["modifiedAt"], _now(), existing["id"])); counts["updated"] += 1; continue
                    conflict_id = self._create_conflict(con, workspace_id, source_id, collection_id, canonical_uri, existing["id"], raw, "remote-version-content-changed")
                    conflict_ids.append(conflict_id); counts["conflicts"] += 1
                    if source["conflict_policy"] == "retain-both":
                        payload["canonicalUri"] = canonical_uri + "#federated-" + normalized["recordHash"][:12]
                    else:
                        continue
                collision = con.execute("SELECT * FROM repository_artifacts WHERE collection_id=? AND canonical_uri=? AND version=? AND sha256<>?", (collection_id, canonical_uri, remote_version, digest)).fetchone()
                if collision:
                    conflict_id = self._create_conflict(con, workspace_id, source_id, collection_id, canonical_uri, collision["id"], raw, "canonical-uri-hash-conflict")
                    conflict_ids.append(conflict_id); counts["conflicts"] += 1
                    if source["conflict_policy"] != "retain-both":
                        continue
                    payload["canonicalUri"] = canonical_uri + "#federated-" + digest[:12]
                    normalized = self._normalize_record(collection, payload, actor_id, source_id)
                artifact_id = f"fed-{_hash([source_id, remote_id, remote_version, normalized['recordHash']])[:28]}"
                now = _now()
                con.execute("INSERT INTO repository_artifacts(id,collection_id,workspace_id,transport_artifact_id,title,artifact_type,version,media_type,sha256,size_bytes,canonical_uri,origin_node_id,source_id,remote_id,remote_version,provenance_json,metadata_json,status,integrity_state,record_hash,modified_at,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (artifact_id, collection_id, workspace_id, None, normalized["title"], normalized["artifactType"], normalized["artifactVersion"], normalized["mediaType"], normalized["sha256"], normalized["sizeBytes"], normalized["canonicalUri"], normalized["originNodeId"], source_id, remote_id, remote_version, _stable(normalized["provenance"]), _stable(normalized["metadata"]), "active", "manifest-verified", normalized["recordHash"], normalized["modifiedAt"], actor_id, now, now))
                counts["imported"] += 1
            completed = _now(); status = "completed-with-conflicts" if counts["conflicts"] else "completed"
            details = {"collectionId": collection_id, "conflictIds": conflict_ids, "recordCount": len(records)}
            run = {"id": run_id, "workspaceId": workspace_id, "sourceId": source_id, "manifestHash": calculated_hash, "cursor": _text(manifest.get("cursor"), 200), "status": status, **counts, "details": details, "startedBy": actor_id, "startedAt": started, "completedAt": completed}
            run_hash = _hash(run)
            con.execute("INSERT INTO sync_runs(id,workspace_id,source_id,manifest_hash,cursor_value,status,imported_count,updated_count,unchanged_count,conflict_count,tombstoned_count,details_json,run_hash,started_by,started_at,completed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (run_id, workspace_id, source_id, calculated_hash, run["cursor"], status, counts["imported"], counts["updated"], counts["unchanged"], counts["conflicts"], counts["tombstoned"], _stable(details), run_hash, actor_id, started, completed))
            con.execute("UPDATE federated_sources SET last_sync_at=?,updated_at=? WHERE id=?", (completed, completed, source_id))
            self._event(con, workspace_id, "sync", run_id, "manifest-synchronized", actor_id, {**counts, "manifestHash": calculated_hash, "sourceId": source_id, "collectionId": collection_id, "runHash": run_hash})
        run.update({"schema": SYNC_SCHEMA, "version": VERSION, "runHash": run_hash})
        return {"ok": True, "sync": run}

    def _create_conflict(self, con: sqlite3.Connection, workspace_id: str, source_id: str, collection_id: str, canonical_uri: str, local_id: str | None, incoming: dict[str, Any], reason: str) -> str:
        conflict_id = f"conflict-{secrets.token_hex(10)}"; created = _now()
        body = {"workspaceId": workspace_id, "sourceId": source_id, "collectionId": collection_id, "canonicalUri": canonical_uri, "localArtifactId": local_id, "incoming": incoming, "reason": reason, "createdAt": created}
        conflict_hash = _hash(body)
        con.execute("INSERT INTO federation_conflicts(id,workspace_id,source_id,collection_id,canonical_uri,local_artifact_id,incoming_json,reason,status,resolution,resolved_by,resolved_at,conflict_hash,created_at) VALUES(?,?,?,?,?,?,?,?,'open',NULL,NULL,NULL,?,?)", (conflict_id, workspace_id, source_id, collection_id, canonical_uri, local_id, _stable(incoming), reason, conflict_hash, created))
        return conflict_id

    def list_conflicts(self, workspace_id: str, actor_id: str, status: str = "open") -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        sql = "SELECT * FROM federation_conflicts WHERE workspace_id=?"; params: list[Any] = [workspace_id]
        if status:
            sql += " AND status=?"; params.append(_text(status, 40).lower())
        sql += " ORDER BY created_at DESC LIMIT 1000"
        with self._connect() as con:
            rows = con.execute(sql, params).fetchall()
        conflicts = [{"schema": CONFLICT_SCHEMA, "version": VERSION, "id": r["id"], "workspaceId": r["workspace_id"], "sourceId": r["source_id"], "collectionId": r["collection_id"], "canonicalUri": r["canonical_uri"], "localArtifactId": r["local_artifact_id"], "incoming": json.loads(r["incoming_json"]), "reason": r["reason"], "status": r["status"], "resolution": r["resolution"], "resolvedBy": r["resolved_by"], "resolvedAt": r["resolved_at"], "conflictHash": r["conflict_hash"], "createdAt": r["created_at"]} for r in rows]
        return {"ok": True, "conflicts": conflicts}

    def resolve_conflict(self, workspace_id: str, conflict_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); conflict_id = _id(conflict_id, "conflict ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.update")
        resolution = _text(payload.get("resolution"), 40).lower()
        if resolution not in {"keep-local", "accept-remote", "retain-both", "dismiss"}:
            raise ArtifactRepositoryError("Unsupported conflict resolution.")
        with self._connect() as con:
            conflict = con.execute("SELECT * FROM federation_conflicts WHERE id=? AND workspace_id=?", (conflict_id, workspace_id)).fetchone()
            if not conflict:
                raise ArtifactRepositoryError("Federation conflict not found.", 404)
            if conflict["status"] != "open":
                raise ArtifactRepositoryError("The federation conflict is already resolved.", 409)
            incoming = json.loads(conflict["incoming_json"])
            if resolution in {"accept-remote", "retain-both"}:
                collection = con.execute("SELECT * FROM collections WHERE id=?", (conflict["collection_id"],)).fetchone()
                payload_record = copy.deepcopy(incoming)
                payload_record.update({"sourceId": conflict["source_id"], "remoteId": incoming.get("remoteId"), "remoteVersion": incoming.get("artifactVersion") or incoming.get("version"), "artifactVersion": incoming.get("artifactVersion") or incoming.get("version")})
                if resolution == "retain-both":
                    payload_record["canonicalUri"] = conflict["canonical_uri"] + "#resolved-" + conflict["conflict_hash"][:12]
                    payload_record["remoteVersion"] = str(payload_record.get("remoteVersion") or payload_record.get("artifactVersion") or "1.0.0") + "+conflict." + conflict["conflict_hash"][:8]
                normalized = self._normalize_record(collection, payload_record, actor_id, conflict["source_id"])
                now = _now()
                if resolution == "accept-remote" and conflict["local_artifact_id"]:
                    con.execute("UPDATE repository_artifacts SET title=?,artifact_type=?,version=?,media_type=?,sha256=?,size_bytes=?,canonical_uri=?,origin_node_id=?,remote_version=?,provenance_json=?,metadata_json=?,status='active',integrity_state='manifest-verified',record_hash=?,modified_at=?,updated_at=? WHERE id=?", (normalized["title"], normalized["artifactType"], normalized["artifactVersion"], normalized["mediaType"], normalized["sha256"], normalized["sizeBytes"], normalized["canonicalUri"], normalized["originNodeId"], normalized["remoteVersion"], _stable(normalized["provenance"]), _stable(normalized["metadata"]), normalized["recordHash"], normalized["modifiedAt"], now, conflict["local_artifact_id"]))
                else:
                    artifact_id = f"fed-{_hash([conflict_id, resolution, normalized['recordHash']])[:28]}"
                    con.execute("INSERT INTO repository_artifacts(id,collection_id,workspace_id,transport_artifact_id,title,artifact_type,version,media_type,sha256,size_bytes,canonical_uri,origin_node_id,source_id,remote_id,remote_version,provenance_json,metadata_json,status,integrity_state,record_hash,modified_at,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (artifact_id, collection["id"], workspace_id, None, normalized["title"], normalized["artifactType"], normalized["artifactVersion"], normalized["mediaType"], normalized["sha256"], normalized["sizeBytes"], normalized["canonicalUri"], normalized["originNodeId"], conflict["source_id"], normalized["remoteId"], normalized["remoteVersion"], _stable(normalized["provenance"]), _stable(normalized["metadata"]), "active", "manifest-verified", normalized["recordHash"], normalized["modifiedAt"], actor_id, now, now))
            resolved_at = _now()
            con.execute("UPDATE federation_conflicts SET status='resolved',resolution=?,resolved_by=?,resolved_at=? WHERE id=?", (resolution, actor_id, resolved_at, conflict_id))
            self._event(con, workspace_id, "conflict", conflict_id, "conflict-resolved", actor_id, {"resolution": resolution})
        return {"ok": True, "conflictId": conflict_id, "status": "resolved", "resolution": resolution, "resolvedAt": resolved_at}

    def sync_history(self, workspace_id: str, actor_id: str, source_id: str = "", limit: int = 200) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "workspace.read")
        sql = "SELECT * FROM sync_runs WHERE workspace_id=?"; params: list[Any] = [workspace_id]
        if source_id:
            sql += " AND source_id=?"; params.append(_id(source_id, "source ID"))
        sql += " ORDER BY started_at DESC LIMIT ?"; params.append(max(1, min(int(limit), 2000)))
        with self._connect() as con:
            rows = con.execute(sql, params).fetchall()
        return {"ok": True, "syncRuns": [{"schema": SYNC_SCHEMA, "version": VERSION, "id": r["id"], "workspaceId": r["workspace_id"], "sourceId": r["source_id"], "manifestHash": r["manifest_hash"], "cursor": r["cursor_value"], "status": r["status"], "imported": r["imported_count"], "updated": r["updated_count"], "unchanged": r["unchanged_count"], "conflicts": r["conflict_count"], "tombstoned": r["tombstoned_count"], "details": json.loads(r["details_json"]), "runHash": r["run_hash"], "startedBy": r["started_by"], "startedAt": r["started_at"], "completedAt": r["completed_at"]} for r in rows]}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID"); actor_id = _id(actor_id, "actor ID")
        self._authorize(workspace_id, actor_id, "timeline.read")
        with self._connect() as con:
            rows = con.execute("SELECT * FROM repository_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(int(limit), 5000)))).fetchall()
        return {"ok": True, "events": [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": r["sequence"], "workspaceId": r["workspace_id"], "entityType": r["entity_type"], "entityId": r["entity_id"], "eventType": r["event_type"], "actorId": r["actor_id"], "details": json.loads(r["details_json"]), "eventHash": r["event_hash"], "createdAt": r["created_at"]} for r in rows]}
