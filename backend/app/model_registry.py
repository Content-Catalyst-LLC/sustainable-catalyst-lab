from __future__ import annotations

import copy
import json
import os
import platform
import re
import secrets
import sqlite3
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.34.0"
MODEL_SCHEMA = "sc-lab-scientific-model/0.34.0"
MODEL_VERSION_SCHEMA = "sc-lab-scientific-model-version/0.34.0"
ENVIRONMENT_SCHEMA = "sc-lab-reproduction-environment/0.34.0"
REPRODUCTION_SCHEMA = "sc-lab-model-reproduction-manifest/0.34.0"
EVENT_SCHEMA = "sc-lab-model-registry-event/0.34.0"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,179}$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
CHANNELS = {"draft", "candidate", "production", "deprecated", "archived"}
MODEL_TYPES = {"registered-method", "workflow", "surrogate", "calibrated-model", "external-artifact"}


class ModelRegistryError(ValueError):
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


def _normalize_dependencies(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ModelRegistryError("environment.dependencies must be an array.")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        if isinstance(item, str):
            name, _, version = item.partition("==")
            entry = {"name": _text(name, 180), "version": _text(version, 120) or None, "hashes": []}
        elif isinstance(item, dict):
            hashes = sorted({_text(v, 180) for v in item.get("hashes", []) if _text(v, 180)})
            entry = {
                "name": _text(item.get("name"), 180),
                "version": _text(item.get("version"), 120) or None,
                "source": _text(item.get("source"), 300) or None,
                "hashes": hashes,
            }
        else:
            raise ModelRegistryError("Each dependency must be a string or object.")
        if not entry["name"] or not ID_RE.match(entry["name"].replace("/", "-")):
            raise ModelRegistryError("Dependency names contain unsupported characters.")
        key = entry["name"].lower()
        if key in seen:
            raise ModelRegistryError(f"Duplicate dependency: {entry['name']}")
        seen.add(key)
        result.append(entry)
    return sorted(result, key=lambda item: item["name"].lower())


def capture_environment(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    source = payload or {}
    env_id = _text(source.get("id"), 180) or f"env-{secrets.token_hex(8)}"
    if not ID_RE.match(env_id):
        raise ModelRegistryError("Environment ID contains unsupported characters.")
    dependencies = _normalize_dependencies(source.get("dependencies"))
    runtime = source.get("runtime") if isinstance(source.get("runtime"), dict) else {}
    system = source.get("system") if isinstance(source.get("system"), dict) else {}
    record = {
        "schema": ENVIRONMENT_SCHEMA,
        "version": VERSION,
        "id": env_id,
        "title": _text(source.get("title"), 300) or env_id,
        "runtime": {
            "implementation": _text(runtime.get("implementation"), 80) or platform.python_implementation(),
            "pythonVersion": _text(runtime.get("pythonVersion"), 80) or platform.python_version(),
            "executable": _text(runtime.get("executable"), 500) or sys.executable,
        },
        "system": {
            "os": _text(system.get("os"), 120) or platform.system(),
            "release": _text(system.get("release"), 120) or platform.release(),
            "machine": _text(system.get("machine"), 120) or platform.machine(),
            "architecture": _text(system.get("architecture"), 120) or platform.architecture()[0],
        },
        "container": {
            "image": _text((source.get("container") or {}).get("image"), 500) if isinstance(source.get("container"), dict) else "",
            "digest": _text((source.get("container") or {}).get("digest"), 180) if isinstance(source.get("container"), dict) else "",
        },
        "dependencies": dependencies,
        "environmentVariables": sorted({_text(v, 180) for v in source.get("environmentVariables", []) if _text(v, 180)}),
        "sourceRevision": _text(source.get("sourceRevision"), 180) or None,
        "buildId": _text(source.get("buildId"), 180) or None,
        "notes": _text(source.get("notes"), 2000) or None,
        "capturedAt": _now(),
    }
    lock_basis = {
        "runtime": record["runtime"],
        "system": record["system"],
        "container": record["container"],
        "dependencies": dependencies,
        "sourceRevision": record["sourceRevision"],
        "buildId": record["buildId"],
    }
    record["lockHash"] = _hash(lock_basis)
    record["recordHash"] = _hash(record)
    return record


def normalize_model_version(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("model") if isinstance(payload.get("model"), dict) else payload
    model_id = _text(source.get("id") or source.get("modelId"), 180)
    version = _text(source.get("modelVersion") or source.get("version"), 120)
    if not ID_RE.match(model_id):
        raise ModelRegistryError("A valid model ID is required.")
    if not SEMVER_RE.match(version):
        raise ModelRegistryError("modelVersion must be semantic version syntax such as 1.0.0.")
    model_type = _text(source.get("type"), 80) or "registered-method"
    if model_type not in MODEL_TYPES:
        raise ModelRegistryError("Unsupported model type.")
    method_id = _text(source.get("methodId"), 180) or None
    workflow_id = _text(source.get("workflowId"), 180) or None
    if model_type == "registered-method" and not method_id:
        raise ModelRegistryError("registered-method models require methodId.")
    if model_type == "workflow" and not workflow_id:
        raise ModelRegistryError("workflow models require workflowId.")
    environment_raw = source.get("environment") if isinstance(source.get("environment"), dict) else {}
    environment = capture_environment(environment_raw)
    artifacts = sorted({_text(v, 220) for v in source.get("artifactIds", []) if _text(v, 220)})
    record = {
        "schema": MODEL_VERSION_SCHEMA,
        "version": VERSION,
        "modelId": model_id,
        "modelVersion": version,
        "title": _text(source.get("title"), 300) or f"{model_id} {version}",
        "description": _text(source.get("description"), 4000) or None,
        "projectId": _text(source.get("projectId"), 180) or "default",
        "type": model_type,
        "methodId": method_id,
        "workflowId": workflow_id,
        "sourceRevision": _text(source.get("sourceRevision"), 180) or environment.get("sourceRevision"),
        "artifactIds": artifacts,
        "inputSchema": copy.deepcopy(source.get("inputSchema")) if isinstance(source.get("inputSchema"), dict) else {"type": "object"},
        "outputSchema": copy.deepcopy(source.get("outputSchema")) if isinstance(source.get("outputSchema"), dict) else {"type": "object"},
        "defaultInputs": copy.deepcopy(source.get("defaultInputs")) if isinstance(source.get("defaultInputs"), dict) else {},
        "parameters": copy.deepcopy(source.get("parameters")) if isinstance(source.get("parameters"), dict) else {},
        "environment": environment,
        "provenance": copy.deepcopy(source.get("provenance")) if isinstance(source.get("provenance"), dict) else {},
        "metadata": copy.deepcopy(source.get("metadata")) if isinstance(source.get("metadata"), dict) else {},
        "createdAt": _now(),
    }
    model_basis = {k: copy.deepcopy(v) for k, v in record.items() if k not in {"createdAt", "environment"}}
    model_basis["environment"] = {
        "lockHash": environment["lockHash"],
        "runtime": environment["runtime"],
        "system": environment["system"],
        "container": environment["container"],
        "dependencies": environment["dependencies"],
        "sourceRevision": environment.get("sourceRevision"),
        "buildId": environment.get("buildId"),
    }
    record["modelHash"] = _hash(model_basis)
    return record


def policies(max_models: int = 5000, max_versions: int = 50000) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "scientific-model-registry-environment-reproduction",
        "modelTypes": sorted(MODEL_TYPES),
        "channels": sorted(CHANNELS),
        "immutableVersions": True,
        "contentHashes": ["sha256"],
        "dependencyLocking": True,
        "environmentCapture": True,
        "promotionWorkflow": True,
        "deprecationHistory": True,
        "arbitraryCode": False,
        "registeredMethodsOnly": True,
        "limits": {"maxModels": max_models, "maxVersions": max_versions},
    }


class ScientificModelRegistry:
    def __init__(self, db_path: str, max_models: int = 5000, max_versions: int = 50000, history_limit: int = 50000):
        self.db_path = str(db_path)
        self.max_models = max(1, int(max_models))
        self.max_versions = max(1, int(max_versions))
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
            con.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS models (
              id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT, project_id TEXT NOT NULL,
              model_type TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS environments (
              id TEXT PRIMARY KEY, lock_hash TEXT NOT NULL UNIQUE, record_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS model_versions (
              model_id TEXT NOT NULL, model_version TEXT NOT NULL, model_hash TEXT NOT NULL UNIQUE,
              environment_id TEXT NOT NULL, record_json TEXT NOT NULL, channel TEXT NOT NULL,
              deprecated_reason TEXT, created_at TEXT NOT NULL, promoted_at TEXT,
              PRIMARY KEY(model_id, model_version),
              FOREIGN KEY(model_id) REFERENCES models(id) ON DELETE CASCADE,
              FOREIGN KEY(environment_id) REFERENCES environments(id)
            );
            CREATE TABLE IF NOT EXISTS aliases (
              model_id TEXT NOT NULL, alias TEXT NOT NULL, model_version TEXT NOT NULL,
              updated_at TEXT NOT NULL, PRIMARY KEY(model_id, alias),
              FOREIGN KEY(model_id, model_version) REFERENCES model_versions(model_id, model_version) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS events (
              sequence INTEGER PRIMARY KEY AUTOINCREMENT, model_id TEXT NOT NULL, model_version TEXT,
              event_type TEXT NOT NULL, actor TEXT, reason TEXT, details_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_models_project ON models(project_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_versions_channel ON model_versions(channel, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_events_model ON events(model_id, sequence DESC);
            """)
            con.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('schema_version','1')")

    def _event(self, con: sqlite3.Connection, model_id: str, version: str | None, event_type: str, actor: str, reason: str, details: dict[str, Any]) -> None:
        con.execute(
            "INSERT INTO events(model_id,model_version,event_type,actor,reason,details_json,created_at) VALUES(?,?,?,?,?,?,?)",
            (model_id, version, event_type, actor or "system", reason or "", _stable(details), _now()),
        )
        con.execute("DELETE FROM events WHERE sequence NOT IN (SELECT sequence FROM events ORDER BY sequence DESC LIMIT ?)", (self.history_limit,))

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = normalize_model_version(payload)
        return {"ok": True, "model": record, "policies": policies(self.max_models, self.max_versions)}

    def register(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        record = normalize_model_version(payload)
        channel = _text(payload.get("channel") or (payload.get("model") or {}).get("channel"), 40) or "draft"
        if channel not in CHANNELS:
            raise ModelRegistryError("Unsupported channel.")
        with self._connect() as con:
            model_count = con.execute("SELECT COUNT(*) FROM models").fetchone()[0]
            version_count = con.execute("SELECT COUNT(*) FROM model_versions").fetchone()[0]
            exists = con.execute("SELECT 1 FROM models WHERE id=?", (record["modelId"],)).fetchone()
            if not exists and model_count >= self.max_models:
                raise ModelRegistryError("Model registry capacity reached.", 409)
            if version_count >= self.max_versions:
                raise ModelRegistryError("Model version capacity reached.", 409)
            duplicate = con.execute("SELECT record_json FROM model_versions WHERE model_id=? AND model_version=?", (record["modelId"], record["modelVersion"])).fetchone()
            if duplicate:
                existing = json.loads(duplicate["record_json"])
                if existing.get("modelHash") == record["modelHash"]:
                    return {"ok": True, "created": False, "model": self.get(record["modelId"], record["modelVersion"])}
                raise ModelRegistryError("Model versions are immutable; choose a new semantic version.", 409)
            now = _now()
            con.execute(
                "INSERT INTO models(id,title,description,project_id,model_type,created_at,updated_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,description=excluded.description,updated_at=excluded.updated_at",
                (record["modelId"], record["title"], record.get("description"), record["projectId"], record["type"], now, now),
            )
            env = record["environment"]
            existing_environment = con.execute(
                "SELECT id,lock_hash FROM environments WHERE id=?", (env["id"],)
            ).fetchone()
            if existing_environment and existing_environment["lock_hash"] != env["lockHash"]:
                raise ModelRegistryError(
                    "Environment IDs are immutable; use a new environment ID for a different lock.", 409
                )
            environment_by_lock = con.execute(
                "SELECT id FROM environments WHERE lock_hash=?", (env["lockHash"],)
            ).fetchone()
            if environment_by_lock:
                environment_id = environment_by_lock["id"]
            else:
                con.execute(
                    "INSERT INTO environments(id,lock_hash,record_json,created_at) VALUES(?,?,?,?)",
                    (env["id"], env["lockHash"], _stable(env), now),
                )
                environment_id = env["id"]
            record["environment"]["id"] = environment_id
            con.execute(
                "INSERT INTO model_versions(model_id,model_version,model_hash,environment_id,record_json,channel,created_at) VALUES(?,?,?,?,?,?,?)",
                (record["modelId"], record["modelVersion"], record["modelHash"], environment_id, _stable(record), channel, now),
            )
            self._event(con, record["modelId"], record["modelVersion"], "model-version-registered", actor, "", {"channel": channel, "modelHash": record["modelHash"], "environmentLockHash": env["lockHash"]})
        return {"ok": True, "created": True, "model": self.get(record["modelId"], record["modelVersion"])}

    def list(self, project_id: str = "", channel: str = "", limit: int = 100) -> dict[str, Any]:
        clauses: list[str] = []
        args: list[Any] = []
        if project_id:
            clauses.append("m.project_id=?"); args.append(project_id)
        if channel:
            if channel not in CHANNELS:
                raise ModelRegistryError("Unsupported channel.")
            clauses.append("v.channel=?"); args.append(channel)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        sql = "SELECT m.id,m.title,m.project_id,m.model_type,m.updated_at,v.model_version,v.channel,v.model_hash,v.created_at FROM models m JOIN model_versions v ON v.model_id=m.id" + where + " ORDER BY v.created_at DESC LIMIT ?"
        args.append(max(1, min(1000, int(limit))))
        with self._connect() as con:
            rows = [dict(row) for row in con.execute(sql, args).fetchall()]
        return {"ok": True, "models": rows, "count": len(rows)}

    def get(self, model_id: str, version_or_alias: str = "") -> dict[str, Any]:
        with self._connect() as con:
            version = version_or_alias
            if not version:
                alias = con.execute("SELECT model_version FROM aliases WHERE model_id=? AND alias='production'", (model_id,)).fetchone()
                if alias:
                    version = alias["model_version"]
                else:
                    row = con.execute("SELECT model_version FROM model_versions WHERE model_id=? ORDER BY created_at DESC LIMIT 1", (model_id,)).fetchone()
                    version = row["model_version"] if row else ""
            elif not SEMVER_RE.match(version):
                alias = con.execute("SELECT model_version FROM aliases WHERE model_id=? AND alias=?", (model_id, version)).fetchone()
                version = alias["model_version"] if alias else version
            row = con.execute("SELECT record_json,channel,deprecated_reason,promoted_at FROM model_versions WHERE model_id=? AND model_version=?", (model_id, version)).fetchone()
            if not row:
                raise ModelRegistryError("Model version not found.", 404)
            record = json.loads(row["record_json"])
            record["channel"] = row["channel"]
            record["deprecatedReason"] = row["deprecated_reason"]
            record["promotedAt"] = row["promoted_at"]
            aliases = [dict(r) for r in con.execute("SELECT alias,model_version,updated_at FROM aliases WHERE model_id=? ORDER BY alias", (model_id,)).fetchall()]
        return {"ok": True, "model": record, "aliases": aliases}

    def promote(self, model_id: str, version: str, channel: str, actor: str = "operator", reason: str = "") -> dict[str, Any]:
        if channel not in {"candidate", "production", "archived"}:
            raise ModelRegistryError("Promotion channel must be candidate, production, or archived.")
        with self._connect() as con:
            row = con.execute("SELECT 1 FROM model_versions WHERE model_id=? AND model_version=?", (model_id, version)).fetchone()
            if not row:
                raise ModelRegistryError("Model version not found.", 404)
            now = _now()
            con.execute("UPDATE model_versions SET channel=?,promoted_at=? WHERE model_id=? AND model_version=?", (channel, now, model_id, version))
            con.execute("INSERT INTO aliases(model_id,alias,model_version,updated_at) VALUES(?,?,?,?) ON CONFLICT(model_id,alias) DO UPDATE SET model_version=excluded.model_version,updated_at=excluded.updated_at", (model_id, channel, version, now))
            self._event(con, model_id, version, "model-version-promoted", actor, reason, {"channel": channel})
        return self.get(model_id, version)

    def deprecate(self, model_id: str, version: str, actor: str = "operator", reason: str = "") -> dict[str, Any]:
        if not reason.strip():
            raise ModelRegistryError("A deprecation reason is required.")
        with self._connect() as con:
            row = con.execute("SELECT 1 FROM model_versions WHERE model_id=? AND model_version=?", (model_id, version)).fetchone()
            if not row:
                raise ModelRegistryError("Model version not found.", 404)
            con.execute("UPDATE model_versions SET channel='deprecated',deprecated_reason=? WHERE model_id=? AND model_version=?", (reason, model_id, version))
            con.execute("DELETE FROM aliases WHERE model_id=? AND model_version=?", (model_id, version))
            self._event(con, model_id, version, "model-version-deprecated", actor, reason, {})
        return self.get(model_id, version)

    def reproduction_manifest(self, model_id: str, version_or_alias: str = "") -> dict[str, Any]:
        model = self.get(model_id, version_or_alias)["model"]
        manifest = {
            "schema": REPRODUCTION_SCHEMA,
            "version": VERSION,
            "id": f"reproduction-{model_id}-{model['modelVersion']}-{secrets.token_hex(4)}",
            "model": {"id": model_id, "version": model["modelVersion"], "hash": model["modelHash"], "type": model["type"], "methodId": model.get("methodId"), "workflowId": model.get("workflowId")},
            "environment": copy.deepcopy(model["environment"]),
            "artifacts": copy.deepcopy(model.get("artifactIds", [])),
            "inputs": {"schema": copy.deepcopy(model.get("inputSchema", {})), "defaults": copy.deepcopy(model.get("defaultInputs", {})), "parameters": copy.deepcopy(model.get("parameters", {}))},
            "sourceRevision": model.get("sourceRevision"),
            "provenance": copy.deepcopy(model.get("provenance", {})),
            "createdAt": _now(),
            "execution": {"arbitraryCode": False, "registeredMethodsOnly": True, "reproducibleEnvironmentRequired": True},
        }
        manifest["manifestHash"] = _hash({k: v for k, v in manifest.items() if k not in {"id", "createdAt"}})
        return {"ok": True, "manifest": manifest}

    def verify_reproduction(self, payload: dict[str, Any]) -> dict[str, Any]:
        manifest = payload.get("manifest") if isinstance(payload.get("manifest"), dict) else payload
        model_ref = manifest.get("model") if isinstance(manifest.get("model"), dict) else {}
        current = self.get(_text(model_ref.get("id"), 180), _text(model_ref.get("version"), 120))["model"]
        checks = {
            "modelHash": model_ref.get("hash") == current.get("modelHash"),
            "environmentLockHash": ((manifest.get("environment") or {}).get("lockHash") == current.get("environment", {}).get("lockHash")),
            "sourceRevision": manifest.get("sourceRevision") == current.get("sourceRevision"),
            "artifactSet": sorted(manifest.get("artifacts") or []) == sorted(current.get("artifactIds") or []),
        }
        supplied_hash = manifest.get("manifestHash")
        if supplied_hash:
            basis = {k: v for k, v in manifest.items() if k not in {"id", "createdAt", "manifestHash"}}
            checks["manifestHash"] = supplied_hash == _hash(basis)
        return {"ok": all(checks.values()), "checks": checks, "model": {"id": current["modelId"], "version": current["modelVersion"], "hash": current["modelHash"]}}

    def compare_environments(self, payload: dict[str, Any]) -> dict[str, Any]:
        left = capture_environment(payload.get("left") if isinstance(payload.get("left"), dict) else {})
        right = capture_environment(payload.get("right") if isinstance(payload.get("right"), dict) else {})
        left_deps = {item["name"]: item for item in left["dependencies"]}
        right_deps = {item["name"]: item for item in right["dependencies"]}
        added = sorted(set(right_deps) - set(left_deps)); removed = sorted(set(left_deps) - set(right_deps))
        changed = sorted(name for name in set(left_deps) & set(right_deps) if left_deps[name] != right_deps[name])
        return {"ok": True, "identical": left["lockHash"] == right["lockHash"], "leftLockHash": left["lockHash"], "rightLockHash": right["lockHash"], "dependencyDiff": {"added": added, "removed": removed, "changed": changed}, "runtimeChanged": left["runtime"] != right["runtime"], "systemChanged": left["system"] != right["system"], "containerChanged": left["container"] != right["container"]}

    def timeline(self, model_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            rows = []
            for row in con.execute("SELECT * FROM events WHERE model_id=? ORDER BY sequence DESC LIMIT ?", (model_id, max(1, min(5000, int(limit))))).fetchall():
                item = dict(row); item["details"] = json.loads(item.pop("details_json")); rows.append(item)
        return {"ok": True, "events": rows, "count": len(rows)}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            counts = {
                "models": con.execute("SELECT COUNT(*) FROM models").fetchone()[0],
                "versions": con.execute("SELECT COUNT(*) FROM model_versions").fetchone()[0],
                "environments": con.execute("SELECT COUNT(*) FROM environments").fetchone()[0],
                "production": con.execute("SELECT COUNT(*) FROM model_versions WHERE channel='production'").fetchone()[0],
                "deprecated": con.execute("SELECT COUNT(*) FROM model_versions WHERE channel='deprecated'").fetchone()[0],
            }
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "schemaVersion": 1, "storage": "sqlite-wal", "databasePath": self.db_path, "integrity": integrity, "counts": counts, "policies": policies(self.max_models, self.max_versions)}
