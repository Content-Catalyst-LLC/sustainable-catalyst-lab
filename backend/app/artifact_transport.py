from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
from typing import Any

VERSION = "0.31.3"
ARTIFACT_SCHEMA = "sc-lab-artifact-record/0.31.3"
UPLOAD_SCHEMA = "sc-lab-artifact-upload-session/0.31.3"
MANIFEST_SCHEMA = "sc-lab-artifact-manifest/0.31.3"
ALLOWED_KINDS = {"input", "result", "checkpoint", "log", "report", "dataset", "provenance"}


class ArtifactTransportError(RuntimeError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _now() -> str:
    return _now_dt().isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _text(value: Any, limit: int = 500) -> str:
    return str(value or "").strip()[:limit]


def _safe_filename(value: Any) -> str:
    raw = Path(_text(value, 240) or "artifact.bin").name
    clean = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in raw).strip(".-")
    return clean[:180] or "artifact.bin"


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


class ArtifactStore:
    def __init__(
        self,
        root: str,
        db_path: str = "",
        max_artifact_bytes: int = 268435456,
        chunk_bytes: int = 1048576,
        upload_ttl_seconds: int = 86400,
        default_retention_seconds: int = 2592000,
    ):
        self.root = Path(root).expanduser().resolve()
        self.blob_root = self.root / "blobs"
        self.temp_root = self.root / "uploads"
        self.db_path = str(Path(db_path).expanduser().resolve()) if db_path else str(self.root / "artifact-index.sqlite3")
        self.max_artifact_bytes = max(1024, int(max_artifact_bytes))
        self.chunk_bytes = max(65536, min(int(chunk_bytes), 8388608))
        self.upload_ttl_seconds = max(300, int(upload_ttl_seconds))
        self.default_retention_seconds = max(3600, int(default_retention_seconds))
        self.root.mkdir(parents=True, exist_ok=True)
        self.blob_root.mkdir(parents=True, exist_ok=True)
        self.temp_root.mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _initialize(self) -> None:
        with self._connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS artifact_upload_sessions (
                    id TEXT PRIMARY KEY,
                    worker_id TEXT,
                    kind TEXT NOT NULL,
                    project_id TEXT,
                    queue_id TEXT,
                    contract_id TEXT,
                    filename TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    expected_sha256 TEXT,
                    expected_size INTEGER,
                    bytes_received INTEGER NOT NULL DEFAULT 0,
                    temp_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    schema_name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    project_id TEXT,
                    queue_id TEXT,
                    contract_id TEXT,
                    worker_id TEXT,
                    filename TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    blob_path TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    retention_until TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    deleted_at TEXT
                );
                CREATE UNIQUE INDEX IF NOT EXISTS artifacts_identity
                    ON artifacts(sha256, project_id, kind, deleted_at);
                CREATE INDEX IF NOT EXISTS artifacts_project_idx ON artifacts(project_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS artifacts_queue_idx ON artifacts(queue_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS artifact_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def _event(self, con: sqlite3.Connection, entity_type: str, entity_id: str, event_type: str, payload: dict[str, Any]) -> None:
        con.execute(
            "INSERT INTO artifact_events(entity_type,entity_id,event_type,payload_json,created_at) VALUES(?,?,?,?,?)",
            (entity_type, entity_id, event_type, _stable(payload), _now()),
        )

    def policies(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "architecture": "content-addressed-resumable-artifact-transport",
            "schemas": {"artifact": ARTIFACT_SCHEMA, "upload": UPLOAD_SCHEMA, "manifest": MANIFEST_SCHEMA},
            "kinds": sorted(ALLOWED_KINDS),
            "contentAddressed": True,
            "sha256RequiredAtFinalize": True,
            "resumableSequentialChunks": True,
            "deduplication": True,
            "workerScopedUploads": True,
            "leaseBoundInputAccess": True,
            "retentionControls": True,
            "maxArtifactBytes": self.max_artifact_bytes,
            "recommendedChunkBytes": self.chunk_bytes,
        }

    def health(self) -> dict[str, Any]:
        self.cleanup_expired_sessions()
        with self._connect() as con:
            artifacts = con.execute("SELECT COUNT(*) FROM artifacts WHERE deleted_at IS NULL").fetchone()[0]
            sessions = con.execute("SELECT COUNT(*) FROM artifact_upload_sessions WHERE status='open'").fetchone()[0]
            bytes_total = con.execute("SELECT COALESCE(SUM(size_bytes),0) FROM artifacts WHERE deleted_at IS NULL").fetchone()[0]
            quarantined = con.execute("SELECT COUNT(*) FROM artifact_upload_sessions WHERE status='quarantined'").fetchone()[0]
        return {
            "ok": True,
            "status": "ready",
            "version": VERSION,
            "storage": "filesystem-content-addressed+sqlite-wal",
            "root": str(self.root),
            "database": self.db_path,
            "artifactCount": artifacts,
            "openUploadSessions": sessions,
            "quarantinedSessions": quarantined,
            "storedBytes": bytes_total,
            "recommendedChunkBytes": self.chunk_bytes,
            "maxArtifactBytes": self.max_artifact_bytes,
        }

    def create_upload(self, payload: dict[str, Any], worker_id: str = "") -> dict[str, Any]:
        kind = _text(payload.get("kind"), 40).lower()
        if kind not in ALLOWED_KINDS:
            raise ArtifactTransportError("Unsupported artifact kind.")
        expected_size = payload.get("sizeBytes")
        if expected_size is not None:
            try:
                expected_size = int(expected_size)
            except (TypeError, ValueError) as exc:
                raise ArtifactTransportError("Artifact size must be an integer.") from exc
            if expected_size < 0 or expected_size > self.max_artifact_bytes:
                raise ArtifactTransportError("Artifact size exceeds the configured limit.", 413)
        expected_hash = _text(payload.get("sha256"), 64).lower()
        if expected_hash and (len(expected_hash) != 64 or any(ch not in "0123456789abcdef" for ch in expected_hash)):
            raise ArtifactTransportError("Artifact SHA-256 is invalid.")
        now = _now()
        session_id = f"artifact-upload-{secrets.token_hex(12)}"
        temp_path = self.temp_root / f"{session_id}.part"
        temp_path.touch(mode=0o600)
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        expires_at = (_now_dt() + timedelta(seconds=self.upload_ttl_seconds)).isoformat()
        with self._connect() as con:
            con.execute(
                """INSERT INTO artifact_upload_sessions
                (id,worker_id,kind,project_id,queue_id,contract_id,filename,media_type,expected_sha256,expected_size,bytes_received,temp_path,status,metadata_json,expires_at,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,0,?,'open',?,?,?,?)""",
                (
                    session_id,
                    _text(worker_id, 180) or None,
                    kind,
                    _text(payload.get("projectId"), 180) or None,
                    _text(payload.get("queueId"), 180) or None,
                    _text(payload.get("contractId"), 180) or None,
                    _safe_filename(payload.get("filename")),
                    _text(payload.get("mediaType"), 160) or "application/octet-stream",
                    expected_hash or None,
                    expected_size,
                    str(temp_path),
                    _stable(metadata),
                    expires_at,
                    now,
                    now,
                ),
            )
            self._event(con, "upload", session_id, "created", {"workerId": worker_id, "kind": kind})
        return {
            "ok": True,
            "schema": UPLOAD_SCHEMA,
            "version": VERSION,
            "sessionId": session_id,
            "status": "open",
            "bytesReceived": 0,
            "nextOffset": 0,
            "recommendedChunkBytes": self.chunk_bytes,
            "expiresAt": expires_at,
        }

    def _session(self, con: sqlite3.Connection, session_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM artifact_upload_sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            raise ArtifactTransportError("Artifact upload session was not found.", 404)
        return row

    def append_chunk(self, session_id: str, offset: int, data: bytes, worker_id: str = "", chunk_sha256: str = "") -> dict[str, Any]:
        if not data:
            raise ArtifactTransportError("Artifact chunk is empty.")
        if len(data) > self.chunk_bytes:
            raise ArtifactTransportError("Artifact chunk exceeds the configured chunk limit.", 413)
        if chunk_sha256:
            actual = sha256(data).hexdigest()
            if not secrets.compare_digest(actual, chunk_sha256.lower()):
                raise ArtifactTransportError("Artifact chunk SHA-256 verification failed.", 422)
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = self._session(con, session_id)
            if row["status"] != "open":
                con.execute("ROLLBACK")
                raise ArtifactTransportError("Artifact upload session is not open.", 409)
            if worker_id and row["worker_id"] and row["worker_id"] != worker_id:
                con.execute("ROLLBACK")
                raise ArtifactTransportError("Artifact upload session belongs to a different worker.", 403)
            if int(offset) != int(row["bytes_received"]):
                con.execute("ROLLBACK")
                raise ArtifactTransportError(f"Artifact chunk offset mismatch; expected {row['bytes_received']}.", 409)
            new_size = int(row["bytes_received"]) + len(data)
            if new_size > self.max_artifact_bytes or (row["expected_size"] is not None and new_size > int(row["expected_size"])):
                con.execute("ROLLBACK")
                raise ArtifactTransportError("Artifact exceeds its declared or configured size limit.", 413)
            path = Path(row["temp_path"])
            with path.open("ab") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            now = _now()
            con.execute("UPDATE artifact_upload_sessions SET bytes_received=?,updated_at=? WHERE id=?", (new_size, now, session_id))
            self._event(con, "upload", session_id, "chunk-appended", {"offset": offset, "size": len(data), "bytesReceived": new_size})
            con.execute("COMMIT")
        return {"ok": True, "sessionId": session_id, "bytesReceived": new_size, "nextOffset": new_size, "chunkSha256": sha256(data).hexdigest()}

    def finalize(self, session_id: str, payload: dict[str, Any] | None = None, worker_id: str = "") -> dict[str, Any]:
        payload = payload or {}
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = self._session(con, session_id)
            if row["status"] == "completed":
                artifact_id = _text(json.loads(row["metadata_json"]).get("artifactId"), 180)
                existing = con.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,)).fetchone() if artifact_id else None
                con.execute("COMMIT")
                if existing:
                    return {"ok": True, "idempotent": True, "artifact": self._artifact_dict(existing)}
                raise ArtifactTransportError("Completed upload is missing its artifact record.", 500)
            if row["status"] != "open":
                con.execute("ROLLBACK")
                raise ArtifactTransportError("Artifact upload session cannot be finalized.", 409)
            if worker_id and row["worker_id"] and row["worker_id"] != worker_id:
                con.execute("ROLLBACK")
                raise ArtifactTransportError("Artifact upload session belongs to a different worker.", 403)
            path = Path(row["temp_path"])
            size = path.stat().st_size if path.exists() else -1
            expected_size = row["expected_size"] if row["expected_size"] is not None else payload.get("sizeBytes")
            if expected_size is not None and size != int(expected_size):
                con.execute("UPDATE artifact_upload_sessions SET status='quarantined',updated_at=? WHERE id=?", (_now(), session_id))
                self._event(con, "upload", session_id, "quarantined", {"reason": "size-mismatch", "actual": size, "expected": expected_size})
                con.execute("COMMIT")
                raise ArtifactTransportError("Artifact size verification failed.", 422)
            digest = _file_sha256(path)
            expected_hash = _text(row["expected_sha256"] or payload.get("sha256"), 64).lower()
            if expected_hash and not secrets.compare_digest(digest, expected_hash):
                con.execute("UPDATE artifact_upload_sessions SET status='quarantined',updated_at=? WHERE id=?", (_now(), session_id))
                self._event(con, "upload", session_id, "quarantined", {"reason": "sha256-mismatch", "actual": digest, "expected": expected_hash})
                con.execute("COMMIT")
                raise ArtifactTransportError("Artifact SHA-256 verification failed.", 422)
            existing = con.execute(
                "SELECT * FROM artifacts WHERE sha256=? AND COALESCE(project_id,'')=COALESCE(?, '') AND kind=? AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1",
                (digest, row["project_id"], row["kind"]),
            ).fetchone()
            if existing:
                path.unlink(missing_ok=True)
                artifact = self._artifact_dict(existing)
                metadata = json.loads(row["metadata_json"])
                metadata["artifactId"] = artifact["id"]
                con.execute("UPDATE artifact_upload_sessions SET status='completed',metadata_json=?,updated_at=? WHERE id=?", (_stable(metadata), _now(), session_id))
                self._event(con, "upload", session_id, "deduplicated", {"artifactId": artifact["id"], "sha256": digest})
                con.execute("COMMIT")
                return {"ok": True, "idempotent": False, "deduplicated": True, "artifact": artifact}
            blob_path = self.blob_root / digest[:2] / digest[2:4] / digest
            blob_path.parent.mkdir(parents=True, exist_ok=True)
            if blob_path.exists():
                path.unlink(missing_ok=True)
            else:
                shutil.move(str(path), str(blob_path))
                blob_path.chmod(0o600)
            artifact_id = f"artifact-{digest[:20]}-{secrets.token_hex(4)}"
            metadata = json.loads(row["metadata_json"])
            metadata.update(payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {})
            retention_seconds = int(payload.get("retentionSeconds") or metadata.get("retentionSeconds") or self.default_retention_seconds)
            retention_seconds = max(3600, min(retention_seconds, 31536000))
            retention_until = (_now_dt() + timedelta(seconds=retention_seconds)).isoformat()
            created_at = _now()
            con.execute(
                """INSERT INTO artifacts(id,schema_name,kind,project_id,queue_id,contract_id,worker_id,filename,media_type,sha256,size_bytes,blob_path,metadata_json,retention_until,created_at,deleted_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
                (
                    artifact_id, ARTIFACT_SCHEMA, row["kind"], row["project_id"], row["queue_id"], row["contract_id"], row["worker_id"],
                    row["filename"], row["media_type"], digest, size, str(blob_path), _stable(metadata), retention_until, created_at,
                ),
            )
            metadata_for_session = json.loads(row["metadata_json"])
            metadata_for_session["artifactId"] = artifact_id
            con.execute("UPDATE artifact_upload_sessions SET status='completed',metadata_json=?,updated_at=? WHERE id=?", (_stable(metadata_for_session), created_at, session_id))
            self._event(con, "artifact", artifact_id, "finalized", {"sha256": digest, "sizeBytes": size, "workerId": row["worker_id"]})
            artifact_row = con.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,)).fetchone()
            con.execute("COMMIT")
        return {"ok": True, "idempotent": False, "deduplicated": False, "artifact": self._artifact_dict(artifact_row)}

    def _artifact_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": row["schema_name"], "version": VERSION, "id": row["id"], "recordType": "artifact",
            "kind": row["kind"], "projectId": row["project_id"], "queueId": row["queue_id"], "contractId": row["contract_id"],
            "workerId": row["worker_id"], "filename": row["filename"], "mediaType": row["media_type"], "sha256": row["sha256"],
            "sizeBytes": row["size_bytes"], "metadata": json.loads(row["metadata_json"]), "retentionUntil": row["retention_until"],
            "createdAt": row["created_at"], "deletedAt": row["deleted_at"], "contentAddressed": True,
        }

    def get(self, artifact_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row = con.execute("SELECT * FROM artifacts WHERE id=? AND deleted_at IS NULL", (artifact_id,)).fetchone()
        if not row:
            raise ArtifactTransportError("Artifact was not found.", 404)
        return self._artifact_dict(row)

    def read(self, artifact_id: str, offset: int = 0, length: int | None = None) -> tuple[dict[str, Any], bytes]:
        with self._connect() as con:
            row = con.execute("SELECT * FROM artifacts WHERE id=? AND deleted_at IS NULL", (artifact_id,)).fetchone()
        if not row:
            raise ArtifactTransportError("Artifact was not found.", 404)
        path = Path(row["blob_path"])
        if not path.is_file():
            raise ArtifactTransportError("Artifact content is unavailable.", 410)
        size = int(row["size_bytes"])
        offset = max(0, int(offset))
        if offset > size:
            raise ArtifactTransportError("Artifact read offset exceeds the content length.", 416)
        length = size - offset if length is None else max(0, min(int(length), size - offset))
        with path.open("rb") as handle:
            handle.seek(offset)
            data = handle.read(length)
        return self._artifact_dict(row), data

    def list(self, project_id: str = "", queue_id: str = "", kind: str = "", limit: int = 100) -> dict[str, Any]:
        conditions = ["deleted_at IS NULL"]
        params: list[Any] = []
        if project_id:
            conditions.append("project_id=?"); params.append(project_id)
        if queue_id:
            conditions.append("queue_id=?"); params.append(queue_id)
        if kind:
            conditions.append("kind=?"); params.append(kind)
        params.append(max(1, min(int(limit), 1000)))
        with self._connect() as con:
            rows = con.execute(f"SELECT * FROM artifacts WHERE {' AND '.join(conditions)} ORDER BY created_at DESC LIMIT ?", params).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "artifacts": [self._artifact_dict(row) for row in rows]}

    def sessions(self, limit: int = 100) -> dict[str, Any]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM artifact_upload_sessions ORDER BY created_at DESC LIMIT ?", (max(1, min(int(limit), 1000)),)).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "sessions": [{
            "schema": UPLOAD_SCHEMA, "id": row["id"], "workerId": row["worker_id"], "kind": row["kind"], "filename": row["filename"],
            "status": row["status"], "bytesReceived": row["bytes_received"], "expectedSize": row["expected_size"], "expiresAt": row["expires_at"],
            "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        } for row in rows]}

    def delete(self, artifact_id: str, reason: str = "retention cleanup") -> dict[str, Any]:
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM artifacts WHERE id=? AND deleted_at IS NULL", (artifact_id,)).fetchone()
            if not row:
                con.execute("ROLLBACK")
                raise ArtifactTransportError("Artifact was not found.", 404)
            now = _now()
            con.execute("UPDATE artifacts SET deleted_at=? WHERE id=?", (now, artifact_id))
            remaining = con.execute("SELECT COUNT(*) FROM artifacts WHERE sha256=? AND deleted_at IS NULL", (row["sha256"],)).fetchone()[0]
            if remaining == 0:
                Path(row["blob_path"]).unlink(missing_ok=True)
            self._event(con, "artifact", artifact_id, "deleted", {"reason": _text(reason, 1000), "blobRetained": remaining > 0})
            con.execute("COMMIT")
        return {"ok": True, "artifactId": artifact_id, "deletedAt": now, "blobRetained": remaining > 0}

    def cleanup_expired_sessions(self) -> dict[str, Any]:
        now = _now()
        removed = 0
        with self._connect() as con:
            rows = con.execute("SELECT id,temp_path FROM artifact_upload_sessions WHERE status='open' AND expires_at<?", (now,)).fetchall()
            for row in rows:
                Path(row["temp_path"]).unlink(missing_ok=True)
                con.execute("UPDATE artifact_upload_sessions SET status='expired',updated_at=? WHERE id=?", (now, row["id"]))
                self._event(con, "upload", row["id"], "expired", {})
                removed += 1
        return {"ok": True, "expiredSessions": removed}

    def cleanup_retention(self) -> dict[str, Any]:
        now = _now()
        with self._connect() as con:
            rows = con.execute("SELECT id FROM artifacts WHERE deleted_at IS NULL AND retention_until<?", (now,)).fetchall()
        deleted = 0
        for row in rows:
            self.delete(row["id"], "retention expired")
            deleted += 1
        sessions = self.cleanup_expired_sessions()["expiredSessions"]
        return {"ok": True, "deletedArtifacts": deleted, "expiredSessions": sessions}

    def manifest(self, artifact_ids: list[str]) -> dict[str, Any]:
        artifacts = [self.get(item) for item in artifact_ids]
        body = {"schema": MANIFEST_SCHEMA, "version": VERSION, "recordType": "artifact-manifest", "createdAt": _now(), "artifacts": artifacts}
        body["manifestSha256"] = sha256(_stable(body).encode("utf-8")).hexdigest()
        return body
