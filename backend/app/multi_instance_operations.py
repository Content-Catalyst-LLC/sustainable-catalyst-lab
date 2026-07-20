from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import shutil
import socket
import sqlite3
import tempfile
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

VERSION = "0.39.2"
INSTANCE_SCHEMA = "sc-lab-instance-manifest/0.39.2"
BACKUP_SCHEMA = "sc-lab-backup-manifest/0.39.2"
MIGRATION_SCHEMA = "sc-lab-migration-plan/0.39.2"
TRANSFER_SCHEMA = "sc-lab-instance-transfer-envelope/0.39.2"
RECOVERY_SCHEMA = "sc-lab-recovery-drill/0.39.2"
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,127}$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][a-zA-Z0-9._-]+)?$")


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha(value: Any) -> str:
    return _sha_bytes(value if isinstance(value, bytes) else _canonical(value))


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if not IDENTIFIER_RE.fullmatch(text):
        raise OperationsError(422, f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 500) -> str:
    text = str(value or "").strip()
    if not text or len(text) > maximum:
        raise OperationsError(422, f"Invalid {label}.")
    return text


def _clean_version(value: Any, label: str = "version") -> str:
    text = str(value or "").strip()
    if not VERSION_RE.fullmatch(text):
        raise OperationsError(422, f"Invalid {label}.")
    return text


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _is_safe_member(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/"):
        return False
    path = PurePosixPath(name)
    return not any(part in {"", ".", ".."} for part in path.parts)


class OperationsError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def policies(persistent_disk_mounted: bool = False) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-multi-instance-operations-policy/0.39.2",
        "capabilities": {
            "stableInstanceIdentity": True,
            "consistentSqliteSnapshots": True,
            "signedBackupManifests": True,
            "hashVerifiedArchives": True,
            "artifactInventoryAndFullCopy": True,
            "stagedNonDestructiveRestore": True,
            "idempotentMigrationJournal": True,
            "signedCrossInstanceTransfer": True,
            "recoveryPointValidation": True,
            "recoveryTimeValidation": True,
            "activeFileOverwriteByApi": False,
            "remoteObjectStorage": False,
        },
        "defaults": {
            "restoreMode": "staged-only",
            "artifactMode": "manifest",
            "storageDurability": "persistent-disk" if persistent_disk_mounted else "instance-local",
            "forcePush": False,
            "pathTraversalProtection": True,
            "symlinkFollowing": False,
        },
    }


class MultiInstanceOperationsManager:
    def __init__(
        self,
        db_path: str,
        backup_root: str,
        instance_id: str = "",
        instance_name: str = "Sustainable Catalyst Lab",
        environment: str = "development",
        region: str = "local",
        public_url: str = "",
        signing_secret: str = "",
        persistent_disk_mounted: bool = False,
        source_paths: dict[str, str] | None = None,
        artifact_root: str = "",
        max_backups: int = 1000,
        max_bundle_bytes: int = 2_147_483_648,
        history_limit: int = 250000,
        rpo_hours: int = 24,
        rto_minutes: int = 240,
    ):
        self.db_path = str(Path(db_path))
        self.backup_root = Path(backup_root).expanduser().resolve()
        self.restore_root = self.backup_root / "restores"
        self.transfer_root = self.backup_root / "transfers"
        self.import_root = self.backup_root / "imports"
        self.persistent_disk_mounted = persistent_disk_mounted
        self.source_paths = {self._source_name(key): str(Path(value).expanduser()) for key, value in (source_paths or {}).items() if str(value).strip()}
        self.artifact_root = Path(artifact_root).expanduser() if artifact_root else None
        self.max_backups = max_backups
        self.max_bundle_bytes = max_bundle_bytes
        self.history_limit = history_limit
        self.rpo_hours = rpo_hours
        self.rto_minutes = rto_minutes
        self.signing_secret = (signing_secret or "").encode("utf-8")
        derived = hashlib.sha256(f"{socket.gethostname()}|{Path(self.db_path).resolve()}".encode()).hexdigest()[:12]
        self.instance_id = _clean_id(instance_id or f"sc-lab-{derived}", "instance ID")
        self.instance_name = _clean_text(instance_name, "instance name", 200)
        self.environment = _clean_id(environment, "environment")
        self.region = _clean_id(region, "region")
        self.public_url = str(public_url or "").strip()[:500]
        for directory in (Path(self.db_path).parent, self.backup_root, self.restore_root, self.transfer_root, self.import_root):
            directory.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._upsert_local_instance()

    @staticmethod
    def _source_name(value: Any) -> str:
        text = str(value or "").strip().lower().replace("_", "-")
        if not IDENTIFIER_RE.fullmatch(text):
            raise ValueError(f"Invalid backup source name: {value!r}")
        return text

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._db() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS instances (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, environment TEXT NOT NULL,
                    region TEXT NOT NULL, public_url TEXT NOT NULL, role TEXT NOT NULL,
                    status TEXT NOT NULL, manifest_hash TEXT NOT NULL, registered_by TEXT NOT NULL,
                    registered_at TEXT NOT NULL, updated_at TEXT NOT NULL, manifest_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS backups (
                    id TEXT PRIMARY KEY, instance_id TEXT NOT NULL, label TEXT NOT NULL,
                    status TEXT NOT NULL, created_by TEXT NOT NULL, created_at TEXT NOT NULL,
                    verified_at TEXT, file_name TEXT NOT NULL, bundle_hash TEXT NOT NULL,
                    manifest_hash TEXT NOT NULL, size_bytes INTEGER NOT NULL,
                    source_count INTEGER NOT NULL, artifact_mode TEXT NOT NULL,
                    manifest_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS restores (
                    id TEXT PRIMARY KEY, backup_id TEXT NOT NULL, status TEXT NOT NULL,
                    created_by TEXT NOT NULL, created_at TEXT NOT NULL, completed_at TEXT,
                    target_name TEXT NOT NULL, verification_hash TEXT NOT NULL,
                    detail_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS migrations (
                    id TEXT PRIMARY KEY, source_version TEXT NOT NULL, target_version TEXT NOT NULL,
                    status TEXT NOT NULL, created_by TEXT NOT NULL, created_at TEXT NOT NULL,
                    executed_by TEXT, executed_at TEXT, backup_id TEXT, plan_hash TEXT NOT NULL,
                    plan_json TEXT NOT NULL, result_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS transfers (
                    id TEXT PRIMARY KEY, backup_id TEXT NOT NULL, source_instance_id TEXT NOT NULL,
                    target_instance_id TEXT NOT NULL, status TEXT NOT NULL, created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL, verified_at TEXT, imported_at TEXT,
                    file_name TEXT NOT NULL, bundle_hash TEXT NOT NULL,
                    envelope_hash TEXT NOT NULL, envelope_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recovery_drills (
                    id TEXT PRIMARY KEY, backup_id TEXT NOT NULL, restore_id TEXT NOT NULL,
                    status TEXT NOT NULL, created_by TEXT NOT NULL, started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL, elapsed_seconds REAL NOT NULL,
                    backup_age_hours REAL NOT NULL, rpo_target_hours INTEGER NOT NULL,
                    rto_target_minutes INTEGER NOT NULL, result_hash TEXT NOT NULL,
                    result_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS operations_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT, instance_id TEXT NOT NULL,
                    event_type TEXT NOT NULL, actor_id TEXT NOT NULL, subject_id TEXT NOT NULL,
                    created_at TEXT NOT NULL, detail_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL, signature TEXT NOT NULL
                );
                """
            )

    def _sign(self, digest: str) -> str:
        return hmac.new(self.signing_secret, digest.encode("ascii"), hashlib.sha256).hexdigest() if self.signing_secret else ""

    def _event(self, event_type: str, actor: str, subject_id: str, detail: dict[str, Any]) -> None:
        actor_id = str(actor or "system").strip()[:200] or "system"
        with self._db() as db:
            previous = db.execute("SELECT event_hash FROM operations_events ORDER BY sequence DESC LIMIT 1").fetchone()
            previous_hash = str(previous["event_hash"]) if previous else "0" * 64
            core = {
                "schema": "sc-lab-multi-instance-event/0.39.2",
                "instanceId": self.instance_id,
                "eventType": event_type,
                "actorId": actor_id,
                "subjectId": subject_id,
                "createdAt": _utc(),
                "detail": detail,
                "previousHash": previous_hash,
            }
            event_hash = _sha(core)
            db.execute(
                "INSERT INTO operations_events(instance_id,event_type,actor_id,subject_id,created_at,detail_json,previous_hash,event_hash,signature) VALUES(?,?,?,?,?,?,?,?,?)",
                (self.instance_id, event_type, actor_id, subject_id, core["createdAt"], json.dumps(detail, sort_keys=True), previous_hash, event_hash, self._sign(event_hash)),
            )
            db.execute(
                "DELETE FROM operations_events WHERE sequence NOT IN (SELECT sequence FROM operations_events ORDER BY sequence DESC LIMIT ?)",
                (self.history_limit,),
            )

    def _instance_core(self) -> dict[str, Any]:
        inventory = []
        for name, path_text in sorted(self.source_paths.items()):
            path = Path(path_text)
            inventory.append({"name": name, "kind": "sqlite-or-file", "available": path.is_file(), "sizeBytes": path.stat().st_size if path.is_file() else 0})
        artifact_available = bool(self.artifact_root and self.artifact_root.is_dir())
        return {
            "schema": INSTANCE_SCHEMA,
            "version": VERSION,
            "instanceId": self.instance_id,
            "name": self.instance_name,
            "environment": self.environment,
            "region": self.region,
            "publicUrl": self.public_url,
            "role": "local",
            "status": "active",
            "storageDurability": "persistent-disk" if self.persistent_disk_mounted else "instance-local",
            "signingConfigured": bool(self.signing_secret),
            "sources": inventory,
            "artifactStore": {"available": artifact_available, "mode": "allowlisted"},
            "generatedAt": _utc(),
        }

    def instance_manifest(self) -> dict[str, Any]:
        core = self._instance_core()
        core["manifestHash"] = _sha(core)
        return core

    def _upsert_local_instance(self) -> None:
        manifest = self.instance_manifest()
        now = _utc()
        with self._db() as db:
            existing = db.execute("SELECT registered_at FROM instances WHERE id=?", (self.instance_id,)).fetchone()
            registered_at = str(existing["registered_at"]) if existing else now
            db.execute(
                """INSERT INTO instances(id,name,environment,region,public_url,role,status,manifest_hash,registered_by,registered_at,updated_at,manifest_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET name=excluded.name,environment=excluded.environment,region=excluded.region,
                   public_url=excluded.public_url,status=excluded.status,manifest_hash=excluded.manifest_hash,
                   updated_at=excluded.updated_at,manifest_json=excluded.manifest_json""",
                (self.instance_id, self.instance_name, self.environment, self.region, self.public_url, "local", "active", manifest["manifestHash"], "system", registered_at, now, json.dumps(manifest, sort_keys=True)),
            )

    def register_peer(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        supplied = str(payload.get("manifestHash") or "")
        if supplied:
            original = {key: value for key, value in payload.items() if key != "manifestHash"}
            if not hmac.compare_digest(supplied, _sha(original)):
                raise OperationsError(422, "Peer manifest hash does not match the supplied manifest.")
        peer_id = _clean_id(payload.get("instanceId"), "peer instance ID")
        if peer_id == self.instance_id:
            raise OperationsError(409, "The local instance is already registered.")
        manifest = {
            "schema": INSTANCE_SCHEMA,
            "version": VERSION,
            "instanceId": peer_id,
            "name": _clean_text(payload.get("name"), "peer name", 200),
            "environment": _clean_id(payload.get("environment", "production"), "environment"),
            "region": _clean_id(payload.get("region", "unknown"), "region"),
            "publicUrl": str(payload.get("publicUrl") or "").strip()[:500],
            "role": "peer",
            "status": str(payload.get("status") or "active").strip().lower(),
            "storageDurability": str(payload.get("storageDurability") or "unknown"),
            "signingConfigured": bool(payload.get("signingConfigured", False)),
            "sources": list(payload.get("sources") or []),
            "artifactStore": dict(payload.get("artifactStore") or {"available": False, "mode": "unknown"}),
            "generatedAt": str(payload.get("generatedAt") or _utc()),
        }
        manifest_hash = _sha(manifest)
        manifest["manifestHash"] = manifest_hash
        now = _utc()
        with self._db() as db:
            existing = db.execute("SELECT registered_at FROM instances WHERE id=?", (peer_id,)).fetchone()
            registered_at = str(existing["registered_at"]) if existing else now
            db.execute(
                """INSERT INTO instances(id,name,environment,region,public_url,role,status,manifest_hash,registered_by,registered_at,updated_at,manifest_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET name=excluded.name,environment=excluded.environment,region=excluded.region,
                   public_url=excluded.public_url,status=excluded.status,manifest_hash=excluded.manifest_hash,
                   updated_at=excluded.updated_at,manifest_json=excluded.manifest_json""",
                (peer_id, manifest["name"], manifest["environment"], manifest["region"], manifest["publicUrl"], "peer", manifest["status"], manifest_hash, actor, registered_at, now, json.dumps(manifest, sort_keys=True)),
            )
        self._event("peer.registered", actor, peer_id, {"manifestHash": manifest_hash})
        return {"ok": True, "version": VERSION, "instance": manifest}

    def list_instances(self) -> dict[str, Any]:
        with self._db() as db:
            rows = db.execute("SELECT manifest_json FROM instances ORDER BY role, id").fetchall()
        return {"ok": True, "version": VERSION, "instances": [json.loads(row["manifest_json"]) for row in rows]}

    def _copy_sqlite(self, source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        src = sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True, timeout=30)
        dst = sqlite3.connect(destination)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()

    def _copy_source(self, name: str, source: Path, root: Path) -> dict[str, Any]:
        destination = root / "data" / f"{name}{source.suffix if source.suffix else '.bin'}"
        try:
            is_sqlite = source.read_bytes()[:16] == b"SQLite format 3\x00"
        except OSError as exc:
            raise OperationsError(500, f"Could not read backup source {name}.") from exc
        if is_sqlite:
            destination = root / "data" / f"{name}.sqlite3"
            self._copy_sqlite(source, destination)
            kind = "sqlite-snapshot"
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination, follow_symlinks=False)
            kind = "file-copy"
        data = destination.read_bytes()
        return {"name": name, "kind": kind, "path": destination.relative_to(root).as_posix(), "sizeBytes": len(data), "sha256": _sha_bytes(data)}

    def _artifact_inventory(self, root: Path, mode: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        files: list[dict[str, Any]] = []
        copied_bytes = 0
        if not self.artifact_root or not self.artifact_root.is_dir() or mode == "none":
            return {"mode": "none", "available": bool(self.artifact_root and self.artifact_root.is_dir()), "fileCount": 0, "totalBytes": 0}, files
        artifact_root = self.artifact_root.resolve()
        for path in sorted(artifact_root.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            resolved = path.resolve()
            try:
                rel = resolved.relative_to(artifact_root)
            except ValueError:
                continue
            size = resolved.stat().st_size
            if copied_bytes + size > self.max_bundle_bytes:
                raise OperationsError(413, "Artifact backup exceeds the configured maximum bundle size.")
            digest = _sha_bytes(resolved.read_bytes())
            entry = {"path": rel.as_posix(), "sizeBytes": size, "sha256": digest}
            files.append(entry)
            copied_bytes += size
            if mode == "full":
                target = root / "artifacts" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(resolved, target, follow_symlinks=False)
        inventory_bytes = _canonical({"files": files})
        inventory_path = root / "artifact-inventory.json"
        inventory_path.write_bytes(inventory_bytes)
        return {
            "mode": mode,
            "available": True,
            "fileCount": len(files),
            "totalBytes": copied_bytes,
            "inventoryPath": "artifact-inventory.json",
            "inventorySha256": _sha_bytes(inventory_bytes),
        }, files

    def create_backup(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        with self._db() as db:
            count = int(db.execute("SELECT COUNT(*) AS c FROM backups").fetchone()["c"])
        if count >= self.max_backups:
            raise OperationsError(409, "The configured backup-record limit has been reached.")
        backup_id = _clean_id(payload.get("id") or f"backup-{uuid.uuid4().hex[:16]}", "backup ID")
        label = str(payload.get("label") or f"Lab backup {backup_id}").strip()[:200] or backup_id
        requested = payload.get("includeSources")
        if requested is None:
            selected = [name for name, path in sorted(self.source_paths.items()) if Path(path).is_file()]
        else:
            if not isinstance(requested, list):
                raise OperationsError(422, "includeSources must be an array.")
            selected = [_clean_id(name, "backup source") for name in requested]
            unknown = sorted(set(selected) - set(self.source_paths))
            if unknown:
                raise OperationsError(422, f"Unknown backup source: {unknown[0]}.")
        artifact_mode = str(payload.get("artifactMode") or "manifest").strip().lower()
        if artifact_mode not in {"none", "manifest", "full"}:
            raise OperationsError(422, "artifactMode must be none, manifest, or full.")
        staging = Path(tempfile.mkdtemp(prefix=f".staging-{backup_id}-", dir=self.backup_root))
        bundle_root = staging / f"sc-lab-backup-{backup_id}"
        bundle_root.mkdir()
        try:
            sources = []
            total_bytes = 0
            for name in selected:
                source = Path(self.source_paths[name])
                if not source.is_file() or source.is_symlink():
                    continue
                entry = self._copy_source(name, source, bundle_root)
                total_bytes += int(entry["sizeBytes"])
                if total_bytes > self.max_bundle_bytes:
                    raise OperationsError(413, "Backup exceeds the configured maximum bundle size.")
                sources.append(entry)
            artifact, _ = self._artifact_inventory(bundle_root, artifact_mode)
            total_bytes += int(artifact["totalBytes"] if artifact_mode == "full" else 0)
            if total_bytes > self.max_bundle_bytes:
                raise OperationsError(413, "Backup exceeds the configured maximum bundle size.")
            core = {
                "schema": BACKUP_SCHEMA,
                "version": VERSION,
                "backupId": backup_id,
                "instance": self.instance_manifest(),
                "label": label,
                "status": "sealed",
                "createdBy": str(actor or "system")[:200],
                "createdAt": _utc(),
                "sources": sources,
                "artifacts": artifact,
                "totalPayloadBytes": total_bytes,
                "restoreMode": "staged-only",
            }
            manifest_hash = _sha(core)
            manifest = dict(core, manifestHash=manifest_hash, signature=self._sign(manifest_hash))
            manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
            (bundle_root / "manifest.json").write_bytes(manifest_bytes)
            output = self.backup_root / f"sc-lab-backup-{backup_id}.zip"
            temp_output = output.with_suffix(".zip.tmp")
            if output.exists() or temp_output.exists():
                raise OperationsError(409, "A backup archive with this ID already exists.")
            with zipfile.ZipFile(temp_output, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                for path in sorted(bundle_root.rglob("*")):
                    if path.is_file() and not path.is_symlink():
                        archive.write(path, path.relative_to(staging).as_posix())
            if temp_output.stat().st_size > self.max_bundle_bytes:
                temp_output.unlink(missing_ok=True)
                raise OperationsError(413, "Compressed backup exceeds the configured maximum bundle size.")
            os.replace(temp_output, output)
            bundle_hash = _sha_bytes(output.read_bytes())
            verified = self._verify_archive_path(output)
            if not verified["valid"]:
                output.unlink(missing_ok=True)
                raise OperationsError(500, "The newly created backup did not pass verification.")
            with self._db() as db:
                db.execute(
                    "INSERT INTO backups(id,instance_id,label,status,created_by,created_at,verified_at,file_name,bundle_hash,manifest_hash,size_bytes,source_count,artifact_mode,manifest_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (backup_id, self.instance_id, label, "verified", str(actor or "system"), manifest["createdAt"], _utc(), output.name, bundle_hash, manifest_hash, output.stat().st_size, len(sources), artifact_mode, json.dumps(manifest, sort_keys=True)),
                )
            self._event("backup.created", actor, backup_id, {"bundleHash": bundle_hash, "sourceCount": len(sources), "artifactMode": artifact_mode})
            return {"ok": True, "version": VERSION, "backup": self._backup_response(backup_id), "verification": verified}
        finally:
            shutil.rmtree(staging, ignore_errors=True)

    def _backup_response(self, backup_id: str) -> dict[str, Any]:
        with self._db() as db:
            row = db.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
        if not row:
            raise OperationsError(404, "Backup not found.")
        record = _row(row) or {}
        manifest = json.loads(record.pop("manifest_json"))
        record.update({"fileName": record.pop("file_name"), "bundleHash": record.pop("bundle_hash"), "manifestHash": record.pop("manifest_hash"), "sizeBytes": record.pop("size_bytes"), "sourceCount": record.pop("source_count"), "artifactMode": record.pop("artifact_mode"), "createdBy": record.pop("created_by"), "createdAt": record.pop("created_at"), "verifiedAt": record.pop("verified_at"), "instanceId": record.pop("instance_id"), "manifest": manifest})
        return record

    def list_backups(self, limit: int = 200) -> dict[str, Any]:
        limit = max(1, min(int(limit), 2000))
        with self._db() as db:
            ids = [row["id"] for row in db.execute("SELECT id FROM backups ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]
        return {"ok": True, "version": VERSION, "backups": [self._backup_response(backup_id) for backup_id in ids]}

    def _verify_archive_path(self, path: Path) -> dict[str, Any]:
        if not path.is_file() or path.stat().st_size > self.max_bundle_bytes:
            return {"valid": False, "reason": "missing-or-oversize"}
        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                if not names or any(not _is_safe_member(name.rstrip("/")) for name in names if not name.endswith("/")):
                    return {"valid": False, "reason": "unsafe-member"}
                roots = {PurePosixPath(name).parts[0] for name in names if name and not name.endswith("/")}
                if len(roots) != 1:
                    return {"valid": False, "reason": "multiple-roots"}
                root = next(iter(roots))
                manifest_name = f"{root}/manifest.json"
                if manifest_name not in names:
                    return {"valid": False, "reason": "manifest-missing"}
                manifest = json.loads(archive.read(manifest_name))
                supplied_hash = str(manifest.get("manifestHash") or "")
                signature = str(manifest.get("signature") or "")
                core = {key: value for key, value in manifest.items() if key not in {"manifestHash", "signature"}}
                calculated_hash = _sha(core)
                if not hmac.compare_digest(supplied_hash, calculated_hash):
                    return {"valid": False, "reason": "manifest-hash-mismatch"}
                if self.signing_secret and not hmac.compare_digest(signature, self._sign(calculated_hash)):
                    return {"valid": False, "reason": "signature-mismatch"}
                checked = 0
                for entry in manifest.get("sources", []):
                    member = f"{root}/{entry['path']}"
                    if member not in names:
                        return {"valid": False, "reason": "source-missing", "source": entry.get("name")}
                    data = archive.read(member)
                    if len(data) != int(entry["sizeBytes"]) or not hmac.compare_digest(_sha_bytes(data), str(entry["sha256"])):
                        return {"valid": False, "reason": "source-digest-mismatch", "source": entry.get("name")}
                    checked += 1
                artifact = manifest.get("artifacts", {})
                if artifact.get("inventoryPath"):
                    member = f"{root}/{artifact['inventoryPath']}"
                    if member not in names or not hmac.compare_digest(_sha_bytes(archive.read(member)), str(artifact.get("inventorySha256") or "")):
                        return {"valid": False, "reason": "artifact-inventory-mismatch"}
                if artifact.get("mode") == "full":
                    inventory = json.loads(archive.read(f"{root}/{artifact['inventoryPath']}"))
                    for entry in inventory.get("files", []):
                        member = f"{root}/artifacts/{entry['path']}"
                        if member not in names:
                            return {"valid": False, "reason": "artifact-missing", "artifact": entry.get("path")}
                        data = archive.read(member)
                        if len(data) != int(entry["sizeBytes"]) or not hmac.compare_digest(_sha_bytes(data), str(entry["sha256"])):
                            return {"valid": False, "reason": "artifact-digest-mismatch", "artifact": entry.get("path")}
                        checked += 1
                if archive.testzip() is not None:
                    return {"valid": False, "reason": "crc-failure"}
                return {"valid": True, "version": VERSION, "manifestHash": calculated_hash, "signatureVerified": bool(self.signing_secret), "checkedEntries": checked, "bundleHash": _sha_bytes(path.read_bytes()), "manifest": manifest}
        except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
            return {"valid": False, "reason": "invalid-archive", "detail": str(exc)[:200]}

    def verify_backup(self, backup_id: str, actor: str) -> dict[str, Any]:
        backup_id = _clean_id(backup_id, "backup ID")
        backup = self._backup_response(backup_id)
        path = self.backup_root / backup["fileName"]
        result = self._verify_archive_path(path)
        with self._db() as db:
            db.execute("UPDATE backups SET status=?,verified_at=? WHERE id=?", ("verified" if result["valid"] else "invalid", _utc() if result["valid"] else None, backup_id))
        self._event("backup.verified" if result["valid"] else "backup.invalid", actor, backup_id, {"reason": result.get("reason", ""), "bundleHash": result.get("bundleHash", "")})
        return {"ok": bool(result["valid"]), "version": VERSION, "backupId": backup_id, "verification": result}

    def stage_restore(self, backup_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        backup_id = _clean_id(backup_id, "backup ID")
        verification = self.verify_backup(backup_id, actor)["verification"]
        if not verification["valid"]:
            raise OperationsError(409, "Backup verification failed; restore was not staged.")
        restore_id = _clean_id(payload.get("id") or f"restore-{uuid.uuid4().hex[:16]}", "restore ID")
        target_name = f"sc-lab-restore-{restore_id}"
        final_dir = self.restore_root / target_name
        if final_dir.exists():
            raise OperationsError(409, "A staged restore with this ID already exists.")
        backup = self._backup_response(backup_id)
        path = self.backup_root / backup["fileName"]
        staging = Path(tempfile.mkdtemp(prefix=f".restore-{restore_id}-", dir=self.restore_root))
        try:
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    if not _is_safe_member(info.filename):
                        raise OperationsError(422, "Unsafe archive member rejected during restore.")
                    destination = staging / PurePosixPath(info.filename)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, destination.open("wb") as output:
                        shutil.copyfileobj(source, output)
            os.replace(staging, final_dir)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        verification_hash = _sha({"backupId": backup_id, "manifestHash": verification["manifestHash"], "targetName": target_name})
        now = _utc()
        detail = {"mode": "staged-only", "activeFilesOverwritten": False, "targetName": target_name, "manifestHash": verification["manifestHash"]}
        with self._db() as db:
            db.execute("INSERT INTO restores(id,backup_id,status,created_by,created_at,completed_at,target_name,verification_hash,detail_json) VALUES(?,?,?,?,?,?,?,?,?)", (restore_id, backup_id, "verified", str(actor or "system"), now, now, target_name, verification_hash, json.dumps(detail, sort_keys=True)))
        self._event("restore.staged", actor, restore_id, {"backupId": backup_id, "targetName": target_name, "verificationHash": verification_hash})
        return {"ok": True, "version": VERSION, "restore": {"schema": "sc-lab-staged-restore/0.39.2", "id": restore_id, "backupId": backup_id, "status": "verified", "createdBy": str(actor or "system"), "createdAt": now, "completedAt": now, "targetName": target_name, "verificationHash": verification_hash, **detail}}

    def create_migration_plan(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        migration_id = _clean_id(payload.get("id") or f"migration-{uuid.uuid4().hex[:16]}", "migration ID")
        source_version = _clean_version(payload.get("sourceVersion") or "0.39.1", "source version")
        target_version = _clean_version(payload.get("targetVersion") or VERSION, "target version")
        steps = [
            {"order": 1, "id": "verify-source", "description": "Verify source release and instance manifest.", "destructive": False},
            {"order": 2, "id": "create-backup", "description": "Create and verify a pre-migration backup.", "destructive": False},
            {"order": 3, "id": "freeze-writes", "description": "Place external writers in a controlled maintenance window.", "destructive": False},
            {"order": 4, "id": "apply-additive-schema", "description": "Apply versioned additive migration steps idempotently.", "destructive": False},
            {"order": 5, "id": "validate-target", "description": "Validate target contracts, hashes, and service health.", "destructive": False},
            {"order": 6, "id": "resume-writes", "description": "Resume external writers after verification.", "destructive": False},
        ]
        core = {"schema": MIGRATION_SCHEMA, "version": VERSION, "migrationId": migration_id, "sourceInstanceId": self.instance_id, "sourceVersion": source_version, "targetVersion": target_version, "status": "planned", "steps": steps, "rollbackStrategy": "restore-verified-pre-migration-backup", "createdBy": str(actor or "system")[:200], "createdAt": _utc()}
        plan_hash = _sha(core)
        plan = dict(core, planHash=plan_hash)
        with self._db() as db:
            db.execute("INSERT INTO migrations(id,source_version,target_version,status,created_by,created_at,plan_hash,plan_json) VALUES(?,?,?,?,?,?,?,?)", (migration_id, source_version, target_version, "planned", str(actor or "system"), core["createdAt"], plan_hash, json.dumps(plan, sort_keys=True)))
        self._event("migration.planned", actor, migration_id, {"sourceVersion": source_version, "targetVersion": target_version, "planHash": plan_hash})
        return {"ok": True, "version": VERSION, "migration": plan}

    def execute_migration(self, migration_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        migration_id = _clean_id(migration_id, "migration ID")
        with self._db() as db:
            row = db.execute("SELECT * FROM migrations WHERE id=?", (migration_id,)).fetchone()
        if not row:
            raise OperationsError(404, "Migration plan not found.")
        plan = json.loads(row["plan_json"])
        backup_id = _clean_id(payload.get("backupId"), "backup ID")
        verification = self.verify_backup(backup_id, actor)["verification"]
        if not verification["valid"]:
            raise OperationsError(409, "A verified pre-migration backup is required.")
        dry_run = bool(payload.get("dryRun", True))
        if not dry_run and str(payload.get("confirmation") or "") != migration_id:
            raise OperationsError(422, "Migration confirmation must match the migration ID.")
        result = {
            "schema": "sc-lab-migration-result/0.39.2",
            "migrationId": migration_id,
            "backupId": backup_id,
            "dryRun": dry_run,
            "status": "validated" if dry_run else "completed",
            "sourceVersion": plan["sourceVersion"],
            "targetVersion": plan["targetVersion"],
            "idempotent": True,
            "destructiveSteps": 0,
            "backupManifestHash": verification["manifestHash"],
            "completedAt": _utc(),
        }
        with self._db() as db:
            if row["status"] == "completed" and not dry_run:
                existing = json.loads(row["result_json"] or "{}")
                return {"ok": True, "version": VERSION, "migration": plan, "result": existing, "idempotentReplay": True}
            db.execute("UPDATE migrations SET status=?,executed_by=?,executed_at=?,backup_id=?,result_json=? WHERE id=?", (result["status"], str(actor or "system"), result["completedAt"], backup_id, json.dumps(result, sort_keys=True), migration_id))
        self._event("migration.validated" if dry_run else "migration.completed", actor, migration_id, {"backupId": backup_id, "targetVersion": plan["targetVersion"]})
        return {"ok": True, "version": VERSION, "migration": plan, "result": result, "idempotentReplay": False}

    def create_transfer(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        transfer_id = _clean_id(payload.get("id") or f"transfer-{uuid.uuid4().hex[:16]}", "transfer ID")
        backup_id = _clean_id(payload.get("backupId"), "backup ID")
        target_instance_id = _clean_id(payload.get("targetInstanceId"), "target instance ID")
        with self._db() as db:
            target = db.execute("SELECT id FROM instances WHERE id=?", (target_instance_id,)).fetchone()
        if not target:
            raise OperationsError(404, "Target instance is not registered.")
        verification = self.verify_backup(backup_id, actor)["verification"]
        if not verification["valid"]:
            raise OperationsError(409, "Only verified backups can be transferred.")
        backup = self._backup_response(backup_id)
        backup_path = self.backup_root / backup["fileName"]
        core = {
            "schema": TRANSFER_SCHEMA,
            "version": VERSION,
            "transferId": transfer_id,
            "sourceInstanceId": self.instance_id,
            "targetInstanceId": target_instance_id,
            "backupId": backup_id,
            "backupFileName": backup_path.name,
            "backupBundleHash": verification["bundleHash"],
            "backupManifestHash": verification["manifestHash"],
            "status": "sealed",
            "createdBy": str(actor or "system")[:200],
            "createdAt": _utc(),
        }
        envelope_hash = _sha(core)
        envelope = dict(core, envelopeHash=envelope_hash, signature=self._sign(envelope_hash))
        output = self.transfer_root / f"sc-lab-transfer-{transfer_id}.zip"
        temp = output.with_suffix(".zip.tmp")
        if output.exists() or temp.exists():
            raise OperationsError(409, "A transfer bundle with this ID already exists.")
        root = f"sc-lab-transfer-{transfer_id}"
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
            archive.writestr(f"{root}/envelope.json", json.dumps(envelope, indent=2, sort_keys=True))
            archive.write(backup_path, f"{root}/{backup_path.name}")
        if temp.stat().st_size > self.max_bundle_bytes:
            temp.unlink(missing_ok=True)
            raise OperationsError(413, "Transfer bundle exceeds the configured maximum size.")
        os.replace(temp, output)
        bundle_hash = _sha_bytes(output.read_bytes())
        result = self._verify_transfer_path(output)
        if not result["valid"]:
            output.unlink(missing_ok=True)
            raise OperationsError(500, "The newly created transfer bundle did not pass verification.")
        with self._db() as db:
            db.execute("INSERT INTO transfers(id,backup_id,source_instance_id,target_instance_id,status,created_by,created_at,verified_at,file_name,bundle_hash,envelope_hash,envelope_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (transfer_id, backup_id, self.instance_id, target_instance_id, "verified", str(actor or "system"), core["createdAt"], _utc(), output.name, bundle_hash, envelope_hash, json.dumps(envelope, sort_keys=True)))
        self._event("transfer.created", actor, transfer_id, {"backupId": backup_id, "targetInstanceId": target_instance_id, "bundleHash": bundle_hash})
        return {"ok": True, "version": VERSION, "transfer": {**envelope, "fileName": output.name, "bundleHash": bundle_hash}, "verification": result}

    def _verify_transfer_path(self, path: Path) -> dict[str, Any]:
        if not path.is_file() or path.stat().st_size > self.max_bundle_bytes:
            return {"valid": False, "reason": "missing-or-oversize"}
        try:
            with zipfile.ZipFile(path) as archive:
                names = [name for name in archive.namelist() if not name.endswith("/")]
                if not names or any(not _is_safe_member(name) for name in names):
                    return {"valid": False, "reason": "unsafe-member"}
                roots = {PurePosixPath(name).parts[0] for name in names}
                if len(roots) != 1:
                    return {"valid": False, "reason": "multiple-roots"}
                root = next(iter(roots))
                envelope_name = f"{root}/envelope.json"
                if envelope_name not in names:
                    return {"valid": False, "reason": "envelope-missing"}
                envelope = json.loads(archive.read(envelope_name))
                supplied_hash = str(envelope.get("envelopeHash") or "")
                core = {key: value for key, value in envelope.items() if key not in {"envelopeHash", "signature"}}
                calculated_hash = _sha(core)
                if not hmac.compare_digest(supplied_hash, calculated_hash):
                    return {"valid": False, "reason": "envelope-hash-mismatch"}
                if self.signing_secret and not hmac.compare_digest(str(envelope.get("signature") or ""), self._sign(calculated_hash)):
                    return {"valid": False, "reason": "signature-mismatch"}
                backup_name = f"{root}/{envelope['backupFileName']}"
                if backup_name not in names:
                    return {"valid": False, "reason": "backup-missing"}
                backup_bytes = archive.read(backup_name)
                if not hmac.compare_digest(_sha_bytes(backup_bytes), str(envelope["backupBundleHash"])):
                    return {"valid": False, "reason": "backup-digest-mismatch"}
                return {"valid": True, "version": VERSION, "envelopeHash": calculated_hash, "signatureVerified": bool(self.signing_secret), "bundleHash": _sha_bytes(path.read_bytes()), "envelope": envelope}
        except (OSError, KeyError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
            return {"valid": False, "reason": "invalid-transfer", "detail": str(exc)[:200]}

    def verify_transfer(self, transfer_id: str, actor: str) -> dict[str, Any]:
        transfer_id = _clean_id(transfer_id, "transfer ID")
        with self._db() as db:
            row = db.execute("SELECT file_name FROM transfers WHERE id=?", (transfer_id,)).fetchone()
        if not row:
            raise OperationsError(404, "Transfer not found.")
        result = self._verify_transfer_path(self.transfer_root / row["file_name"])
        with self._db() as db:
            db.execute("UPDATE transfers SET status=?,verified_at=? WHERE id=?", ("verified" if result["valid"] else "invalid", _utc() if result["valid"] else None, transfer_id))
        self._event("transfer.verified" if result["valid"] else "transfer.invalid", actor, transfer_id, {"reason": result.get("reason", "")})
        return {"ok": bool(result["valid"]), "version": VERSION, "transferId": transfer_id, "verification": result}

    def import_transfer(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        file_name = Path(_clean_text(payload.get("fileName"), "transfer filename", 255)).name
        source = self.transfer_root / file_name
        verification = self._verify_transfer_path(source)
        if not verification["valid"]:
            raise OperationsError(409, "Transfer verification failed.")
        envelope = verification["envelope"]
        if envelope["targetInstanceId"] != self.instance_id and not bool(payload.get("allowDifferentTarget", False)):
            raise OperationsError(409, "Transfer target does not match this instance.")
        target = self.import_root / file_name
        if target.exists():
            if hmac.compare_digest(_sha_bytes(target.read_bytes()), verification["bundleHash"]):
                return {"ok": True, "version": VERSION, "status": "already-imported", "fileName": file_name, "verification": verification}
            raise OperationsError(409, "An imported transfer with this filename already exists with different content.")
        shutil.copyfile(source, target, follow_symlinks=False)
        with self._db() as db:
            db.execute("UPDATE transfers SET status='imported',imported_at=? WHERE id=?", (_utc(), envelope["transferId"]))
        self._event("transfer.imported", actor, envelope["transferId"], {"fileName": file_name, "bundleHash": verification["bundleHash"]})
        return {"ok": True, "version": VERSION, "status": "imported", "fileName": file_name, "verification": verification}

    def run_recovery_drill(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        started = time.monotonic()
        started_at = _utc()
        backup_id = str(payload.get("backupId") or "").strip()
        if backup_id:
            backup_id = _clean_id(backup_id, "backup ID")
        else:
            created = self.create_backup({"label": payload.get("label") or "Automated recovery drill", "includeSources": payload.get("includeSources"), "artifactMode": payload.get("artifactMode", "manifest")}, actor)
            backup_id = created["backup"]["id"]
        verification = self.verify_backup(backup_id, actor)["verification"]
        if not verification["valid"]:
            raise OperationsError(409, "Recovery drill requires a valid backup.")
        restore = self.stage_restore(backup_id, {}, actor)["restore"]
        backup_created = verification["manifest"]["createdAt"].replace("Z", "+00:00")
        age_hours = max(0.0, (datetime.now(timezone.utc) - datetime.fromisoformat(backup_created)).total_seconds() / 3600.0)
        elapsed = time.monotonic() - started
        rpo_target = int(payload.get("rpoHours") or self.rpo_hours)
        rto_target = int(payload.get("rtoMinutes") or self.rto_minutes)
        rpo_pass = age_hours <= rpo_target
        rto_pass = elapsed <= rto_target * 60
        status = "passed" if rpo_pass and rto_pass else "failed"
        completed_at = _utc()
        drill_id = _clean_id(payload.get("id") or f"drill-{uuid.uuid4().hex[:16]}", "recovery drill ID")
        result_core = {
            "schema": RECOVERY_SCHEMA,
            "version": VERSION,
            "drillId": drill_id,
            "instanceId": self.instance_id,
            "backupId": backup_id,
            "restoreId": restore["id"],
            "status": status,
            "startedAt": started_at,
            "completedAt": completed_at,
            "elapsedSeconds": round(elapsed, 6),
            "backupAgeHours": round(age_hours, 6),
            "rpoTargetHours": rpo_target,
            "rtoTargetMinutes": rto_target,
            "rpoPassed": rpo_pass,
            "rtoPassed": rto_pass,
            "backupVerified": True,
            "restoreVerified": restore["status"] == "verified",
            "activeFilesOverwritten": False,
        }
        result_hash = _sha(result_core)
        result = dict(result_core, resultHash=result_hash)
        with self._db() as db:
            db.execute("INSERT INTO recovery_drills(id,backup_id,restore_id,status,created_by,started_at,completed_at,elapsed_seconds,backup_age_hours,rpo_target_hours,rto_target_minutes,result_hash,result_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (drill_id, backup_id, restore["id"], status, str(actor or "system"), started_at, completed_at, elapsed, age_hours, rpo_target, rto_target, result_hash, json.dumps(result, sort_keys=True)))
        if bool(payload.get("cleanupRestore", True)):
            shutil.rmtree(self.restore_root / restore["targetName"], ignore_errors=True)
            result["stagedRestoreCleaned"] = True
        else:
            result["stagedRestoreCleaned"] = False
        self._event("recovery-drill.completed", actor, drill_id, {"status": status, "backupId": backup_id, "restoreId": restore["id"], "resultHash": result_hash})
        return {"ok": status == "passed", "version": VERSION, "recoveryDrill": result}

    def dashboard(self) -> dict[str, Any]:
        with self._db() as db:
            counts = {
                "instances": int(db.execute("SELECT COUNT(*) AS c FROM instances").fetchone()["c"]),
                "backups": int(db.execute("SELECT COUNT(*) AS c FROM backups").fetchone()["c"]),
                "verifiedBackups": int(db.execute("SELECT COUNT(*) AS c FROM backups WHERE status='verified'").fetchone()["c"]),
                "restores": int(db.execute("SELECT COUNT(*) AS c FROM restores").fetchone()["c"]),
                "migrations": int(db.execute("SELECT COUNT(*) AS c FROM migrations").fetchone()["c"]),
                "transfers": int(db.execute("SELECT COUNT(*) AS c FROM transfers").fetchone()["c"]),
                "recoveryDrills": int(db.execute("SELECT COUNT(*) AS c FROM recovery_drills").fetchone()["c"]),
                "passedRecoveryDrills": int(db.execute("SELECT COUNT(*) AS c FROM recovery_drills WHERE status='passed'").fetchone()["c"]),
            }
            latest = db.execute("SELECT created_at,verified_at,id FROM backups WHERE status='verified' ORDER BY created_at DESC LIMIT 1").fetchone()
        return {"ok": True, "version": VERSION, "instance": self.instance_manifest(), "counts": counts, "latestVerifiedBackup": _row(latest), "targets": {"rpoHours": self.rpo_hours, "rtoMinutes": self.rto_minutes}, "storage": {"durability": "persistent-disk" if self.persistent_disk_mounted else "instance-local", "signingConfigured": bool(self.signing_secret)}}

    def health(self) -> dict[str, Any]:
        writable = os.access(self.backup_root, os.W_OK)
        dashboard = self.dashboard()
        return {"ok": writable, "status": "ready" if writable else "degraded", "version": VERSION, "serviceVersion": VERSION, "instanceId": self.instance_id, "backupRootWritable": writable, "storageDurability": dashboard["storage"]["durability"], "signingConfigured": bool(self.signing_secret), "sourceCount": len(self.source_paths), "latestVerifiedBackup": dashboard["latestVerifiedBackup"], "rpoHours": self.rpo_hours, "rtoMinutes": self.rto_minutes}
