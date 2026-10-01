from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.154.0"
PROTOCOL_SCHEMA = "sc-lab-reproducible-protocol/0.154.0"
PROTOCOL_REVISION_SCHEMA = "sc-lab-reproducible-protocol-revision/0.154.0"
NOTEBOOK_SCHEMA = "sc-lab-computational-notebook/0.154.0"
NOTEBOOK_REVISION_SCHEMA = "sc-lab-computational-notebook-revision/0.154.0"
MANIFEST_SCHEMA = "sc-lab-notebook-reproduction-manifest/0.154.0"
BOUNDARY = (
    "Protocols and notebooks preserve declared methods, parameters, registered compute-call specifications, "
    "result references, workspace references, and immutable revisions. They do not establish evidence, causality, "
    "statistical significance, calibration, or scientific validity, and they do not execute arbitrary code."
)


class ProtocolNotebookError(ValueError):
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
    text = str(value or "").strip()
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise ProtocolNotebookError(f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int = 5000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ProtocolNotebookError(f"{label} is required.")
    if len(text) > maximum:
        raise ProtocolNotebookError(f"{label} exceeds {maximum} characters.")
    return text


def _bounded(value: Any, label: str, maximum_bytes: int = 1_500_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise ProtocolNotebookError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise ProtocolNotebookError(f"{label} exceeds the payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


def _normalize_string_list(value: Any, limit: int, max_len: int) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:limit]:
        text = str(item or "").strip()
        if text:
            out.append(text[:max_len])
    return out


def _normalize_refs(value: Any, limit: int = 200) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value[:limit]:
        if isinstance(item, str):
            ref = item.strip()
            if ref:
                out.append({"ref": ref[:300]})
        elif isinstance(item, dict):
            ref = str(item.get("ref") or item.get("id") or item.get("assetId") or item.get("runId") or item.get("resultId") or "").strip()
            if not ref:
                continue
            row: dict[str, Any] = {"ref": ref[:300]}
            for key in ("kind", "method", "digest", "revision", "createdAt"):
                if item.get(key) is not None:
                    row[key] = str(item.get(key))[:300]
            out.append(row)
    return out


def _normalize_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    purpose = _clean_text(payload.get("purpose"), "purpose", 12000, True)
    steps = _normalize_string_list(payload.get("steps"), 200, 4000)
    if not steps:
        raise ProtocolNotebookError("At least one protocol step is required.")
    methods = _normalize_string_list(payload.get("methodRefs"), 100, 300)
    acceptance = _normalize_string_list(payload.get("acceptanceCriteria"), 100, 2000)
    inputs = _normalize_refs(payload.get("inputRefs"), 200)
    workspaces = _normalize_refs(payload.get("workspaceRefs"), 100)
    parameters = _bounded(payload.get("parameters") or {}, "parameters", 250_000)
    return {
        "purpose": purpose,
        "steps": steps,
        "methodRefs": methods,
        "acceptanceCriteria": acceptance,
        "inputRefs": inputs,
        "workspaceRefs": workspaces,
        "parameters": parameters,
    }


def _normalize_cells(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ProtocolNotebookError("Notebook cells must be an array.")
    allowed_types = {"markdown", "parameter", "compute-call", "result-ref", "figure-ref", "protocol-ref", "workspace-ref"}
    out: list[dict[str, Any]] = []
    for idx, raw in enumerate(value[:500]):
        if not isinstance(raw, dict):
            raise ProtocolNotebookError(f"Notebook cell {idx + 1} must be an object.")
        kind = str(raw.get("type") or "markdown").strip()
        if kind not in allowed_types:
            raise ProtocolNotebookError(f"Unsupported notebook cell type: {kind}.")
        cell: dict[str, Any] = {"id": str(raw.get("id") or f"cell:{uuid.uuid4().hex}")[:180], "type": kind}
        if kind == "compute-call":
            method = _clean_text(raw.get("method"), "compute method", 300, True)
            inputs = _bounded(raw.get("inputs") or {}, "compute cell inputs", 400_000)
            parameters = _bounded(raw.get("parameters") or {}, "compute cell parameters", 250_000)
            requested_outputs = _normalize_string_list(raw.get("requested_outputs") or raw.get("requestedOutputs"), 100, 150)
            cell.update({"method": method, "inputs": inputs, "parameters": parameters, "requestedOutputs": requested_outputs})
        elif kind in {"result-ref", "figure-ref", "protocol-ref", "workspace-ref"}:
            ref = _clean_text(raw.get("ref"), "cell reference", 500, True)
            cell.update({"ref": ref, "label": _clean_text(raw.get("label"), "cell label", 500, False)})
        elif kind == "parameter":
            name = _clean_text(raw.get("name"), "parameter name", 200, True)
            value = _bounded(raw.get("value"), "parameter value", 100_000)
            cell.update({"name": name, "value": value, "units": _clean_text(raw.get("units"), "parameter units", 120, False)})
        else:
            cell["text"] = _clean_text(raw.get("text"), "cell text", 50000, False)
        if raw.get("resultRef"):
            cell["resultRef"] = str(raw.get("resultRef"))[:500]
        out.append(cell)
    return out


class ProtocolNotebookWorkspaceManager:
    def __init__(self, db_path: str, persistent_disk_mounted: bool = False, max_protocols_per_project: int = 500, max_notebooks_per_project: int = 500, history_limit: int = 100000) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_protocols_per_project = max(1, int(max_protocols_per_project))
        self.max_notebooks_per_project = max(1, int(max_notebooks_per_project))
        self.history_limit = max(100, int(history_limit))
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
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS rpn_protocols(
                  id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL,
                  latest_revision_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL,
                  protocol_hash TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS rpn_protocol_project_idx ON rpn_protocols(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS rpn_protocol_revisions(
                  id TEXT PRIMARY KEY, protocol_id TEXT NOT NULL, revision_no INTEGER NOT NULL,
                  created_at TEXT NOT NULL, actor TEXT NOT NULL, content_json TEXT NOT NULL, revision_hash TEXT NOT NULL,
                  UNIQUE(protocol_id, revision_no), FOREIGN KEY(protocol_id) REFERENCES rpn_protocols(id)
                );
                CREATE INDEX IF NOT EXISTS rpn_protocol_revision_idx ON rpn_protocol_revisions(protocol_id, revision_no DESC);
                CREATE TABLE IF NOT EXISTS rpn_notebooks(
                  id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL,
                  protocol_id TEXT, latest_revision_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  actor TEXT NOT NULL, notebook_hash TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS rpn_notebook_project_idx ON rpn_notebooks(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS rpn_notebook_revisions(
                  id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, revision_no INTEGER NOT NULL,
                  created_at TEXT NOT NULL, actor TEXT NOT NULL, cells_json TEXT NOT NULL,
                  workspace_refs_json TEXT NOT NULL, compute_refs_json TEXT NOT NULL, notes_json TEXT NOT NULL,
                  revision_hash TEXT NOT NULL, UNIQUE(notebook_id, revision_no),
                  FOREIGN KEY(notebook_id) REFERENCES rpn_notebooks(id)
                );
                CREATE INDEX IF NOT EXISTS rpn_notebook_revision_idx ON rpn_notebook_revisions(notebook_id, revision_no DESC);
                CREATE TABLE IF NOT EXISTS rpn_events(
                  seq INTEGER PRIMARY KEY AUTOINCREMENT, object_id TEXT NOT NULL, project_id TEXT NOT NULL,
                  event_type TEXT NOT NULL, occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
                  payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
                );
                """
            )

    def _event(self, db: sqlite3.Connection, object_id: str, project_id: str, event_type: str, actor: str, payload: Any) -> None:
        row = db.execute("SELECT event_hash FROM rpn_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = str(row["event_hash"]) if row else ""
        occurred = _now()
        envelope = {"objectId": object_id, "projectId": project_id, "eventType": event_type, "occurredAt": occurred, "actor": actor, "payload": payload, "previousHash": previous}
        event_hash = _sha(envelope)
        db.execute(
            "INSERT INTO rpn_events(object_id,project_id,event_type,occurred_at,actor,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (object_id, project_id, event_type, occurred, actor, json.dumps(payload, sort_keys=True), previous, event_hash),
        )
        db.execute("DELETE FROM rpn_events WHERE seq NOT IN (SELECT seq FROM rpn_events ORDER BY seq DESC LIMIT ?)", (self.history_limit,))

    @staticmethod
    def _protocol_row(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": PROTOCOL_SCHEMA, "id": row["id"], "projectId": row["project_id"], "title": row["title"], "status": row["status"], "latestRevisionId": row["latest_revision_id"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"], "protocolHash": row["protocol_hash"]}

    @staticmethod
    def _protocol_revision_row(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": PROTOCOL_REVISION_SCHEMA, "id": row["id"], "protocolId": row["protocol_id"], "revision": int(row["revision_no"]), "createdAt": row["created_at"], "actor": row["actor"], "content": json.loads(row["content_json"] or "{}"), "revisionHash": row["revision_hash"]}

    @staticmethod
    def _notebook_row(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": NOTEBOOK_SCHEMA, "id": row["id"], "projectId": row["project_id"], "title": row["title"], "status": row["status"], "protocolId": row["protocol_id"], "latestRevisionId": row["latest_revision_id"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"], "notebookHash": row["notebook_hash"]}

    @staticmethod
    def _notebook_revision_row(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": NOTEBOOK_REVISION_SCHEMA, "id": row["id"], "notebookId": row["notebook_id"], "revision": int(row["revision_no"]), "createdAt": row["created_at"], "actor": row["actor"], "cells": json.loads(row["cells_json"] or "[]"), "workspaceRefs": json.loads(row["workspace_refs_json"] or "[]"), "computeRefs": json.loads(row["compute_refs_json"] or "[]"), "notes": json.loads(row["notes_json"] or "{}"), "revisionHash": row["revision_hash"]}

    def health(self) -> dict[str, Any]:
        with self._connect() as db:
            protocols = int(db.execute("SELECT COUNT(*) AS n FROM rpn_protocols").fetchone()["n"])
            notebooks = int(db.execute("SELECT COUNT(*) AS n FROM rpn_notebooks").fetchone()["n"])
            protocol_revisions = int(db.execute("SELECT COUNT(*) AS n FROM rpn_protocol_revisions").fetchone()["n"])
            notebook_revisions = int(db.execute("SELECT COUNT(*) AS n FROM rpn_notebook_revisions").fetchone()["n"])
        return {
            "ok": True, "status": "ready", "version": VERSION,
            "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local-volume",
            "protocolSchema": PROTOCOL_SCHEMA, "notebookSchema": NOTEBOOK_SCHEMA, "manifestSchema": MANIFEST_SCHEMA,
            "immutableProtocolRevisions": True, "immutableNotebookRevisions": True,
            "registeredComputeCells": True, "arbitraryCodeExecution": False,
            "explicitComputeExecution": True, "automaticCompute": False, "automaticScientificValidity": False,
            "counts": {"protocols": protocols, "protocolRevisions": protocol_revisions, "notebooks": notebooks, "notebookRevisions": notebook_revisions},
            "boundary": BOUNDARY,
        }

    def policies(self) -> dict[str, Any]:
        return {
            "ok": True, "version": VERSION,
            "maxProtocolsPerProject": self.max_protocols_per_project,
            "maxNotebooksPerProject": self.max_notebooks_per_project,
            "maxProtocolSteps": 200, "maxNotebookCells": 500, "maxComputeRefs": 200,
            "archiveInsteadOfDelete": True, "revisionsImmutable": True,
            "computeCellMode": "registered-method-specification-only", "arbitraryCodeExecution": False,
            "automaticExecution": False, "automaticCoreSubmission": False, "boundary": BOUNDARY,
        }

    def create_protocol(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project ID")
        title = _clean_text(payload.get("title"), "protocol title", 200, True)
        content = _normalize_protocol(payload)
        protocol_id = _clean_id(payload.get("protocolId") or f"protocol:{uuid.uuid4().hex}", "protocol ID")
        stamp = _now()
        with self._lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) AS n FROM rpn_protocols WHERE project_id=? AND status!='archived'", (project_id,)).fetchone()["n"])
            if count >= self.max_protocols_per_project:
                raise ProtocolNotebookError("Project protocol limit reached.", 409)
            if db.execute("SELECT 1 FROM rpn_protocols WHERE id=?", (protocol_id,)).fetchone():
                raise ProtocolNotebookError("Protocol already exists.", 409)
            rev_id = f"protocolrev:{uuid.uuid4().hex}"
            rev_hash = _sha({"protocolId": protocol_id, "revision": 1, "content": content})
            protocol_hash = _sha({"id": protocol_id, "projectId": project_id, "title": title, "createdAt": stamp})
            db.execute("INSERT INTO rpn_protocols(id,project_id,title,status,latest_revision_id,created_at,updated_at,actor,protocol_hash) VALUES(?,?,?,?,?,?,?,?,?)", (protocol_id, project_id, title, "active", rev_id, stamp, stamp, actor, protocol_hash))
            db.execute("INSERT INTO rpn_protocol_revisions(id,protocol_id,revision_no,created_at,actor,content_json,revision_hash) VALUES(?,?,?,?,?,?,?)", (rev_id, protocol_id, 1, stamp, actor, json.dumps(content, sort_keys=True), rev_hash))
            self._event(db, protocol_id, project_id, "protocol-created", actor, {"revisionId": rev_id})
            db.commit()
        return self.get_protocol(protocol_id)

    def list_protocols(self, project_id: str, limit: int = 100, include_archived: bool = False) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project ID"); limit = max(1, min(500, int(limit)))
        with self._connect() as db:
            sql = "SELECT * FROM rpn_protocols WHERE project_id=?" + ("" if include_archived else " AND status!='archived'") + " ORDER BY updated_at DESC LIMIT ?"
            rows = db.execute(sql, (project_id, limit)).fetchall()
        return {"ok": True, "version": VERSION, "projectId": project_id, "protocols": [self._protocol_row(r) for r in rows], "count": len(rows), "boundary": BOUNDARY}

    def get_protocol(self, protocol_id: str) -> dict[str, Any]:
        protocol_id = _clean_id(protocol_id, "protocol ID")
        with self._connect() as db:
            row = db.execute("SELECT * FROM rpn_protocols WHERE id=?", (protocol_id,)).fetchone()
            if not row: raise ProtocolNotebookError("Protocol not found.", 404)
            revs = db.execute("SELECT * FROM rpn_protocol_revisions WHERE protocol_id=? ORDER BY revision_no DESC", (protocol_id,)).fetchall()
        return {"ok": True, "version": VERSION, "protocol": self._protocol_row(row), "revisions": [self._protocol_revision_row(r) for r in revs], "boundary": BOUNDARY}

    def revise_protocol(self, protocol_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        protocol_id = _clean_id(protocol_id, "protocol ID"); content = _normalize_protocol(payload); title = _clean_text(payload.get("title"), "protocol title", 200, False)
        with self._lock, self._connect() as db:
            protocol = db.execute("SELECT * FROM rpn_protocols WHERE id=?", (protocol_id,)).fetchone()
            if not protocol: raise ProtocolNotebookError("Protocol not found.", 404)
            if protocol["status"] == "archived": raise ProtocolNotebookError("Archived protocols cannot receive revisions.", 409)
            rev_no = int(db.execute("SELECT COALESCE(MAX(revision_no),0)+1 AS n FROM rpn_protocol_revisions WHERE protocol_id=?", (protocol_id,)).fetchone()["n"])
            stamp = _now(); rev_id = f"protocolrev:{uuid.uuid4().hex}"; rev_hash = _sha({"protocolId": protocol_id, "revision": rev_no, "content": content})
            db.execute("INSERT INTO rpn_protocol_revisions(id,protocol_id,revision_no,created_at,actor,content_json,revision_hash) VALUES(?,?,?,?,?,?,?)", (rev_id, protocol_id, rev_no, stamp, actor, json.dumps(content, sort_keys=True), rev_hash))
            db.execute("UPDATE rpn_protocols SET latest_revision_id=?,updated_at=?,actor=?,title=? WHERE id=?", (rev_id, stamp, actor, title or protocol["title"], protocol_id))
            self._event(db, protocol_id, protocol["project_id"], "protocol-revision-created", actor, {"revisionId": rev_id, "revision": rev_no})
            db.commit()
        return self.get_protocol(protocol_id)

    def archive_protocol(self, protocol_id: str, actor: str) -> dict[str, Any]:
        protocol_id = _clean_id(protocol_id, "protocol ID")
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM rpn_protocols WHERE id=?", (protocol_id,)).fetchone()
            if not row: raise ProtocolNotebookError("Protocol not found.", 404)
            stamp = _now(); db.execute("UPDATE rpn_protocols SET status='archived',updated_at=?,actor=? WHERE id=?", (stamp, actor, protocol_id)); self._event(db, protocol_id, row["project_id"], "protocol-archived", actor, {}); db.commit()
        return self.get_protocol(protocol_id)

    def create_notebook(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project ID"); title = _clean_text(payload.get("title"), "notebook title", 200, True)
        protocol_id = str(payload.get("protocolId") or "").strip() or None
        if protocol_id: protocol_id = _clean_id(protocol_id, "protocol ID")
        cells = _normalize_cells(payload.get("cells") or [])
        workspace_refs = _normalize_refs(payload.get("workspaceRefs"), 100); compute_refs = _normalize_refs(payload.get("computeRefs"), 200); notes = _bounded(payload.get("notes") or {}, "notes", 250_000)
        notebook_id = _clean_id(payload.get("notebookId") or f"notebook:{uuid.uuid4().hex}", "notebook ID"); stamp = _now()
        with self._lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) AS n FROM rpn_notebooks WHERE project_id=? AND status!='archived'", (project_id,)).fetchone()["n"])
            if count >= self.max_notebooks_per_project: raise ProtocolNotebookError("Project notebook limit reached.", 409)
            if protocol_id:
                p = db.execute("SELECT * FROM rpn_protocols WHERE id=?", (protocol_id,)).fetchone()
                if not p or p["project_id"] != project_id: raise ProtocolNotebookError("Linked protocol does not exist in this project.", 404)
            rev_id = f"notebookrev:{uuid.uuid4().hex}"; rev_hash = _sha({"notebookId": notebook_id, "revision": 1, "cells": cells, "workspaceRefs": workspace_refs, "computeRefs": compute_refs, "notes": notes}); notebook_hash = _sha({"id": notebook_id, "projectId": project_id, "title": title, "createdAt": stamp})
            db.execute("INSERT INTO rpn_notebooks(id,project_id,title,status,protocol_id,latest_revision_id,created_at,updated_at,actor,notebook_hash) VALUES(?,?,?,?,?,?,?,?,?,?)", (notebook_id, project_id, title, "active", protocol_id, rev_id, stamp, stamp, actor, notebook_hash))
            db.execute("INSERT INTO rpn_notebook_revisions(id,notebook_id,revision_no,created_at,actor,cells_json,workspace_refs_json,compute_refs_json,notes_json,revision_hash) VALUES(?,?,?,?,?,?,?,?,?,?)", (rev_id, notebook_id, 1, stamp, actor, json.dumps(cells, sort_keys=True), json.dumps(workspace_refs, sort_keys=True), json.dumps(compute_refs, sort_keys=True), json.dumps(notes, sort_keys=True), rev_hash))
            self._event(db, notebook_id, project_id, "notebook-created", actor, {"revisionId": rev_id, "protocolId": protocol_id}); db.commit()
        return self.get_notebook(notebook_id)

    def list_notebooks(self, project_id: str, limit: int = 100, include_archived: bool = False) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project ID"); limit = max(1, min(500, int(limit)))
        with self._connect() as db:
            sql = "SELECT * FROM rpn_notebooks WHERE project_id=?" + ("" if include_archived else " AND status!='archived'") + " ORDER BY updated_at DESC LIMIT ?"
            rows = db.execute(sql, (project_id, limit)).fetchall()
        return {"ok": True, "version": VERSION, "projectId": project_id, "notebooks": [self._notebook_row(r) for r in rows], "count": len(rows), "boundary": BOUNDARY}

    def get_notebook(self, notebook_id: str) -> dict[str, Any]:
        notebook_id = _clean_id(notebook_id, "notebook ID")
        with self._connect() as db:
            row = db.execute("SELECT * FROM rpn_notebooks WHERE id=?", (notebook_id,)).fetchone()
            if not row: raise ProtocolNotebookError("Notebook not found.", 404)
            revs = db.execute("SELECT * FROM rpn_notebook_revisions WHERE notebook_id=? ORDER BY revision_no DESC", (notebook_id,)).fetchall()
        return {"ok": True, "version": VERSION, "notebook": self._notebook_row(row), "revisions": [self._notebook_revision_row(r) for r in revs], "boundary": BOUNDARY}

    def revise_notebook(self, notebook_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        notebook_id = _clean_id(notebook_id, "notebook ID"); cells = _normalize_cells(payload.get("cells") or []); workspace_refs = _normalize_refs(payload.get("workspaceRefs"), 100); compute_refs = _normalize_refs(payload.get("computeRefs"), 200); notes = _bounded(payload.get("notes") or {}, "notes", 250_000); title = _clean_text(payload.get("title"), "notebook title", 200, False)
        protocol_id = str(payload.get("protocolId") or "").strip() or None
        if protocol_id: protocol_id = _clean_id(protocol_id, "protocol ID")
        with self._lock, self._connect() as db:
            nb = db.execute("SELECT * FROM rpn_notebooks WHERE id=?", (notebook_id,)).fetchone()
            if not nb: raise ProtocolNotebookError("Notebook not found.", 404)
            if nb["status"] == "archived": raise ProtocolNotebookError("Archived notebooks cannot receive revisions.", 409)
            if protocol_id:
                p = db.execute("SELECT * FROM rpn_protocols WHERE id=?", (protocol_id,)).fetchone()
                if not p or p["project_id"] != nb["project_id"]: raise ProtocolNotebookError("Linked protocol does not exist in this project.", 404)
            rev_no = int(db.execute("SELECT COALESCE(MAX(revision_no),0)+1 AS n FROM rpn_notebook_revisions WHERE notebook_id=?", (notebook_id,)).fetchone()["n"])
            stamp = _now(); rev_id = f"notebookrev:{uuid.uuid4().hex}"; rev_hash = _sha({"notebookId": notebook_id, "revision": rev_no, "cells": cells, "workspaceRefs": workspace_refs, "computeRefs": compute_refs, "notes": notes})
            db.execute("INSERT INTO rpn_notebook_revisions(id,notebook_id,revision_no,created_at,actor,cells_json,workspace_refs_json,compute_refs_json,notes_json,revision_hash) VALUES(?,?,?,?,?,?,?,?,?,?)", (rev_id, notebook_id, rev_no, stamp, actor, json.dumps(cells, sort_keys=True), json.dumps(workspace_refs, sort_keys=True), json.dumps(compute_refs, sort_keys=True), json.dumps(notes, sort_keys=True), rev_hash))
            db.execute("UPDATE rpn_notebooks SET latest_revision_id=?,updated_at=?,actor=?,title=?,protocol_id=? WHERE id=?", (rev_id, stamp, actor, title or nb["title"], protocol_id, notebook_id)); self._event(db, notebook_id, nb["project_id"], "notebook-revision-created", actor, {"revisionId": rev_id, "revision": rev_no, "protocolId": protocol_id}); db.commit()
        return self.get_notebook(notebook_id)

    def archive_notebook(self, notebook_id: str, actor: str) -> dict[str, Any]:
        notebook_id = _clean_id(notebook_id, "notebook ID")
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM rpn_notebooks WHERE id=?", (notebook_id,)).fetchone()
            if not row: raise ProtocolNotebookError("Notebook not found.", 404)
            stamp = _now(); db.execute("UPDATE rpn_notebooks SET status='archived',updated_at=?,actor=? WHERE id=?", (stamp, actor, notebook_id)); self._event(db, notebook_id, row["project_id"], "notebook-archived", actor, {}); db.commit()
        return self.get_notebook(notebook_id)

    def reproduction_manifest(self, notebook_id: str) -> dict[str, Any]:
        nb = self.get_notebook(notebook_id); latest = nb["revisions"][0]; protocol = None
        if nb["notebook"].get("protocolId"):
            protocol = self.get_protocol(nb["notebook"]["protocolId"])
        protocol_rev = protocol["revisions"][0] if protocol and protocol.get("revisions") else None
        body = {
            "schema": MANIFEST_SCHEMA, "version": VERSION, "createdAt": _now(),
            "projectId": nb["notebook"]["projectId"], "notebook": {"id": nb["notebook"]["id"], "title": nb["notebook"]["title"], "revisionId": latest["id"], "revision": latest["revision"], "revisionHash": latest["revisionHash"]},
            "protocol": None if not protocol_rev else {"id": protocol["protocol"]["id"], "title": protocol["protocol"]["title"], "revisionId": protocol_rev["id"], "revision": protocol_rev["revision"], "revisionHash": protocol_rev["revisionHash"]},
            "workspaceRefs": latest["workspaceRefs"], "computeRefs": latest["computeRefs"],
            "computeCellMethods": sorted({str(c.get("method")) for c in latest["cells"] if c.get("type") == "compute-call" and c.get("method")}),
            "arbitraryCodeExecution": False, "automaticCompute": False, "boundary": BOUNDARY,
        }
        body["manifestDigest"] = _sha(body)
        return {"ok": True, "manifest": body}

    def verify_manifest(self, payload: dict[str, Any]) -> dict[str, Any]:
        manifest = _bounded(payload.get("manifest") or payload, "manifest", 1_000_000)
        claimed = str(manifest.get("manifestDigest") or "")
        unsigned = dict(manifest); unsigned.pop("manifestDigest", None)
        actual = _sha(unsigned)
        return {"ok": bool(claimed) and claimed == actual, "version": VERSION, "schema": MANIFEST_SCHEMA, "claimedDigest": claimed or None, "computedDigest": actual, "arbitraryCodeExecution": False, "boundary": BOUNDARY}
