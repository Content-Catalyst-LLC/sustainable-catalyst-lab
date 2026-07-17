from __future__ import annotations

import copy
import json
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.35.2"
BRANCH_SCHEMA = "sc-lab-workspace-branch/0.35.2"
SNAPSHOT_SCHEMA = "sc-lab-workspace-snapshot/0.35.2"
COMPARE_SCHEMA = "sc-lab-workspace-version-compare/0.35.2"
MERGE_SCHEMA = "sc-lab-workspace-merge-request/0.35.2"
CONFLICT_SCHEMA = "sc-lab-workspace-merge-conflict/0.35.2"
EVENT_SCHEMA = "sc-lab-workspace-version-event/0.35.2"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
BRANCH_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,119}$")
ROLES = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
BRANCH_STATUSES = {"active", "merged", "archived"}
MERGE_STATUSES = {"open", "conflicted", "ready", "merged", "cancelled"}
RESOLUTIONS = {"source", "target", "base", "custom"}
_MISSING = object()


class WorkspaceVersionError(ValueError):
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


def _text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, label: str = "identifier") -> str:
    clean = _text(value, 180)
    if not ID_RE.match(clean):
        raise WorkspaceVersionError(f"A valid {label} is required.")
    return clean


def _branch_name(value: Any) -> str:
    clean = _text(value, 120)
    if not BRANCH_NAME_RE.match(clean) or clean.startswith("/") or clean.endswith("/") or "//" in clean:
        raise WorkspaceVersionError("A valid branch name is required.")
    return clean


def _tree(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise WorkspaceVersionError("Snapshot trees must be JSON objects keyed by stable resource paths.")
    if len(value) > 10000:
        raise WorkspaceVersionError("Snapshot tree exceeds the 10,000-path limit.", 413)
    normalized: dict[str, Any] = {}
    for raw_path, raw_value in value.items():
        path = _text(raw_path, 500)
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise WorkspaceVersionError("Snapshot paths must be relative and cannot contain '..'.")
        try:
            json.dumps(raw_value, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise WorkspaceVersionError(f"Snapshot path {path!r} is not JSON serializable.") from exc
        normalized[path] = copy.deepcopy(raw_value)
    return {key: normalized[key] for key in sorted(normalized)}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-workspace-version-policy/0.35.2",
        "capabilities": {
            "immutableSnapshots": True,
            "namedBranches": True,
            "threeWayMerge": True,
            "pathLevelConflicts": True,
            "conflictResolutionRecords": True,
            "protectedBranches": True,
            "signedApprovalGate": True,
            "restoreCreatesNewSnapshot": True,
            "optimisticHeadChecks": True,
            "hardDelete": False,
            "historyRewrite": False,
            "arbitraryCode": False,
        },
        "roles": {
            "read": ["viewer", "reviewer", "contributor", "editor", "administrator", "owner"],
            "snapshot": ["contributor", "editor", "administrator", "owner"],
            "branch": ["editor", "administrator", "owner"],
            "reviewMerge": ["reviewer", "editor", "administrator", "owner"],
            "merge": ["editor", "administrator", "owner"],
            "protect": ["administrator", "owner"],
        },
        "branchStatuses": sorted(BRANCH_STATUSES),
        "mergeStatuses": sorted(MERGE_STATUSES),
        "resolutions": sorted(RESOLUTIONS),
    }


class WorkspaceVersionManager:
    def __init__(self, db_path: str, history_limit: int = 100000):
        self.db_path = str(db_path)
        self.history_limit = max(100, int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS workspace_branches(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL,
                  status TEXT NOT NULL, protected INTEGER NOT NULL DEFAULT 0,
                  base_snapshot_id TEXT, head_snapshot_id TEXT, created_by TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, merged_at TEXT,
                  revision INTEGER NOT NULL DEFAULT 1,
                  UNIQUE(workspace_id,name),
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS workspace_snapshots(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, branch_id TEXT NOT NULL,
                  parent_snapshot_id TEXT, merge_parent_snapshot_id TEXT,
                  message TEXT NOT NULL, tree_json TEXT NOT NULL, tree_hash TEXT NOT NULL,
                  author_id TEXT NOT NULL, metadata_json TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(branch_id) REFERENCES workspace_branches(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS workspace_merge_requests(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL,
                  source_branch_id TEXT NOT NULL, target_branch_id TEXT NOT NULL,
                  base_snapshot_id TEXT, source_snapshot_id TEXT, target_snapshot_id TEXT,
                  result_snapshot_id TEXT, title TEXT NOT NULL, description TEXT,
                  status TEXT NOT NULL, approval_request_id TEXT, created_by TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, merged_by TEXT,
                  merged_at TEXT, cancelled_by TEXT, cancelled_at TEXT, cancel_reason TEXT,
                  revision INTEGER NOT NULL DEFAULT 1,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(source_branch_id) REFERENCES workspace_branches(id) ON DELETE CASCADE,
                  FOREIGN KEY(target_branch_id) REFERENCES workspace_branches(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS workspace_merge_conflicts(
                  id TEXT PRIMARY KEY, merge_request_id TEXT NOT NULL, workspace_id TEXT NOT NULL,
                  path TEXT NOT NULL, base_json TEXT, source_json TEXT, target_json TEXT,
                  status TEXT NOT NULL, resolution TEXT, resolved_json TEXT,
                  conflict_hash TEXT NOT NULL, resolved_by TEXT, resolved_at TEXT,
                  UNIQUE(merge_request_id,path),
                  FOREIGN KEY(merge_request_id) REFERENCES workspace_merge_requests(id) ON DELETE CASCADE,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS workspace_version_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL,
                  event_type TEXT NOT NULL, actor_id TEXT NOT NULL, details_json TEXT NOT NULL,
                  event_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_workspace_branches ON workspace_branches(workspace_id,status,name);
                CREATE INDEX IF NOT EXISTS idx_workspace_snapshots ON workspace_snapshots(workspace_id,branch_id,created_at);
                CREATE INDEX IF NOT EXISTS idx_workspace_merges ON workspace_merge_requests(workspace_id,status,updated_at);
                CREATE INDEX IF NOT EXISTS idx_workspace_conflicts ON workspace_merge_conflicts(merge_request_id,status,path);
                CREATE INDEX IF NOT EXISTS idx_workspace_version_events ON workspace_version_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version','1')")
            current = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            if current < 3:
                con.execute("UPDATE meta SET value='3' WHERE key='schema_version'")

    def _event(self, con: sqlite3.Connection, workspace_id: str, event_type: str, actor_id: str, details: dict[str, Any]) -> None:
        created_at = _now()
        event_hash = _hash({"workspaceId": workspace_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created_at})
        con.execute(
            "INSERT INTO workspace_version_events(workspace_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?)",
            (workspace_id, event_type, actor_id, _stable(details), event_hash, created_at),
        )

    @staticmethod
    def _has(role: str, capability: str) -> bool:
        rank = ROLES.get(role, 0)
        minimum = {"read": 10, "review": 30, "snapshot": 50, "branch": 70, "merge": 70, "protect": 90}.get(capability, 10)
        return rank >= minimum

    def _require(self, con: sqlite3.Connection, workspace_id: str, actor_id: str, capability: str = "read", allow_archived: bool = True) -> tuple[sqlite3.Row, sqlite3.Row]:
        workspace = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
        if not workspace:
            raise WorkspaceVersionError("Workspace not found.", 404)
        if not allow_archived and workspace["status"] == "archived":
            raise WorkspaceVersionError("The workspace is archived and read-only.", 409)
        member = con.execute("SELECT * FROM memberships WHERE workspace_id=? AND actor_id=? AND status='active'", (workspace_id, actor_id)).fetchone()
        if not member:
            raise WorkspaceVersionError("Workspace membership is required.", 403)
        if not self._has(member["role"], capability):
            raise WorkspaceVersionError(f"The workspace role cannot perform {capability} operations.", 403)
        return workspace, member

    def _branch(self, con: sqlite3.Connection, workspace_id: str, branch_ref: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM workspace_branches WHERE workspace_id=? AND (id=? OR name=?)", (workspace_id, branch_ref, branch_ref)).fetchone()
        if not row:
            raise WorkspaceVersionError("Workspace branch not found.", 404)
        return row

    def _snapshot(self, con: sqlite3.Connection, workspace_id: str, snapshot_id: str | None) -> sqlite3.Row | None:
        if not snapshot_id:
            return None
        row = con.execute("SELECT * FROM workspace_snapshots WHERE id=? AND workspace_id=?", (snapshot_id, workspace_id)).fetchone()
        if not row:
            raise WorkspaceVersionError("Workspace snapshot not found.", 404)
        return row

    @staticmethod
    def _branch_record(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": BRANCH_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"],
            "name": row["name"], "status": row["status"], "protected": bool(row["protected"]),
            "baseSnapshotId": row["base_snapshot_id"], "headSnapshotId": row["head_snapshot_id"],
            "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
            "mergedAt": row["merged_at"], "revision": row["revision"],
        }

    @staticmethod
    def _snapshot_record(row: sqlite3.Row, include_tree: bool = True) -> dict[str, Any]:
        record = {
            "schema": SNAPSHOT_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"],
            "branchId": row["branch_id"], "parentSnapshotId": row["parent_snapshot_id"],
            "mergeParentSnapshotId": row["merge_parent_snapshot_id"], "message": row["message"],
            "treeHash": row["tree_hash"], "authorId": row["author_id"], "metadata": json.loads(row["metadata_json"]),
            "createdAt": row["created_at"],
        }
        if include_tree:
            record["tree"] = json.loads(row["tree_json"])
        return record

    @staticmethod
    def _conflict_record(row: sqlite3.Row) -> dict[str, Any]:
        def load(value: str | None) -> Any:
            if value is None:
                return None
            return json.loads(value)
        return {
            "schema": CONFLICT_SCHEMA, "version": VERSION, "id": row["id"], "mergeRequestId": row["merge_request_id"],
            "workspaceId": row["workspace_id"], "path": row["path"], "base": load(row["base_json"]),
            "source": load(row["source_json"]), "target": load(row["target_json"]), "status": row["status"],
            "resolution": row["resolution"], "resolvedValue": load(row["resolved_json"]),
            "conflictHash": row["conflict_hash"], "resolvedBy": row["resolved_by"], "resolvedAt": row["resolved_at"],
        }

    def _merge_record(self, con: sqlite3.Connection, row: sqlite3.Row, include_conflicts: bool = True) -> dict[str, Any]:
        record = {
            "schema": MERGE_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"],
            "sourceBranchId": row["source_branch_id"], "targetBranchId": row["target_branch_id"],
            "baseSnapshotId": row["base_snapshot_id"], "sourceSnapshotId": row["source_snapshot_id"],
            "targetSnapshotId": row["target_snapshot_id"], "resultSnapshotId": row["result_snapshot_id"],
            "title": row["title"], "description": row["description"], "status": row["status"],
            "approvalRequestId": row["approval_request_id"], "createdBy": row["created_by"],
            "createdAt": row["created_at"], "updatedAt": row["updated_at"], "mergedBy": row["merged_by"],
            "mergedAt": row["merged_at"], "cancelledBy": row["cancelled_by"], "cancelledAt": row["cancelled_at"],
            "cancelReason": row["cancel_reason"], "revision": row["revision"],
        }
        if include_conflicts:
            conflicts = con.execute("SELECT * FROM workspace_merge_conflicts WHERE merge_request_id=? ORDER BY path", (row["id"],)).fetchall()
            record["conflicts"] = [self._conflict_record(item) for item in conflicts]
        return record

    def _ensure_main(self, con: sqlite3.Connection, workspace_id: str, actor_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM workspace_branches WHERE workspace_id=? AND name='main'", (workspace_id,)).fetchone()
        if row:
            return row
        now = _now()
        branch_id = f"branch-{secrets.token_hex(8)}"
        con.execute(
            "INSERT INTO workspace_branches(id,workspace_id,name,status,protected,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
            (branch_id, workspace_id, "main", "active", 1, actor_id, now, now),
        )
        self._event(con, workspace_id, "branch-created", actor_id, {"branchId": branch_id, "name": "main", "protected": True, "automatic": True})
        return con.execute("SELECT * FROM workspace_branches WHERE id=?", (branch_id,)).fetchone()

    def _tree_for_snapshot(self, row: sqlite3.Row | None) -> dict[str, Any]:
        return json.loads(row["tree_json"]) if row else {}

    @staticmethod
    def _expect_revision(payload: dict[str, Any], current: int) -> None:
        if "expectedRevision" not in payload:
            raise WorkspaceVersionError("expectedRevision is required for conflict-safe updates.")
        if int(payload.get("expectedRevision")) != int(current):
            raise WorkspaceVersionError(f"Revision conflict: expected {payload.get('expectedRevision')}, current {current}.", 409)

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            counts = {
                "branches": con.execute("SELECT COUNT(*) FROM workspace_branches").fetchone()[0],
                "snapshots": con.execute("SELECT COUNT(*) FROM workspace_snapshots").fetchone()[0],
                "mergeRequests": con.execute("SELECT COUNT(*) FROM workspace_merge_requests").fetchone()[0],
                "openConflicts": con.execute("SELECT COUNT(*) FROM workspace_merge_conflicts WHERE status='open'").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM workspace_version_events").fetchone()[0],
            }
            schema = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            return {"ok": integrity == "ok", "version": VERSION, "database": {"path": self.db_path, "schemaVersion": schema, "integrity": integrity}, "counts": counts}

    def bootstrap(self, workspace_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "read")
            branch = self._ensure_main(con, workspace_id, actor_id)
            return {"ok": True, "branch": self._branch_record(branch)}

    def list_branches(self, workspace_id: str, actor_id: str, status: str | None = None) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            self._ensure_main(con, workspace_id, actor_id)
            clauses, params = ["workspace_id=?"], [workspace_id]
            if status:
                if status not in BRANCH_STATUSES:
                    raise WorkspaceVersionError("Unsupported branch status.")
                clauses.append("status=?"); params.append(status)
            rows = con.execute(f"SELECT * FROM workspace_branches WHERE {' AND '.join(clauses)} ORDER BY name", params).fetchall()
            return {"ok": True, "version": VERSION, "branches": [self._branch_record(row) for row in rows]}

    def create_branch(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "branch", False)
            main = self._ensure_main(con, workspace_id, actor_id)
            name = _branch_name(payload.get("name"))
            source_ref = _text(payload.get("sourceBranchId") or payload.get("sourceBranch") or main["id"], 180)
            source = self._branch(con, workspace_id, source_ref)
            source_snapshot_id = _text(payload.get("sourceSnapshotId"), 180) or source["head_snapshot_id"]
            if source_snapshot_id:
                self._snapshot(con, workspace_id, source_snapshot_id)
            protected = bool(payload.get("protected", False))
            if protected and not self._has(self._require(con, workspace_id, actor_id, "branch", False)[1]["role"], "protect"):
                raise WorkspaceVersionError("Only workspace administrators and owners may create protected branches.", 403)
            branch_id = _id(payload.get("id") or f"branch-{secrets.token_hex(8)}", "branch ID")
            now = _now()
            try:
                con.execute(
                    "INSERT INTO workspace_branches(id,workspace_id,name,status,protected,base_snapshot_id,head_snapshot_id,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (branch_id, workspace_id, name, "active", int(protected), source_snapshot_id, source_snapshot_id, actor_id, now, now),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkspaceVersionError("The branch ID or branch name already exists.", 409) from exc
            self._event(con, workspace_id, "branch-created", actor_id, {"branchId": branch_id, "name": name, "sourceBranchId": source["id"], "sourceSnapshotId": source_snapshot_id, "protected": protected})
            row = con.execute("SELECT * FROM workspace_branches WHERE id=?", (branch_id,)).fetchone()
            return {"ok": True, "branch": self._branch_record(row)}

    def set_branch(self, workspace_id: str, branch_ref: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            _, member = self._require(con, workspace_id, actor_id, "branch", False)
            branch = self._branch(con, workspace_id, branch_ref)
            self._expect_revision(payload, branch["revision"])
            name = _branch_name(payload.get("name") or branch["name"])
            status = _text(payload.get("status") or branch["status"], 40).lower()
            if status not in BRANCH_STATUSES:
                raise WorkspaceVersionError("Unsupported branch status.")
            protected = bool(payload["protected"]) if "protected" in payload else bool(branch["protected"])
            if protected != bool(branch["protected"]) and not self._has(member["role"], "protect"):
                raise WorkspaceVersionError("Only workspace administrators and owners may change branch protection.", 403)
            if branch["name"] == "main" and (name != "main" or status != "active"):
                raise WorkspaceVersionError("The main branch cannot be renamed, merged, or archived.", 409)
            now = _now()
            try:
                con.execute("UPDATE workspace_branches SET name=?,status=?,protected=?,updated_at=?,revision=revision+1 WHERE id=?", (name, status, int(protected), now, branch["id"]))
            except sqlite3.IntegrityError as exc:
                raise WorkspaceVersionError("The branch name already exists.", 409) from exc
            self._event(con, workspace_id, "branch-updated", actor_id, {"branchId": branch["id"], "name": name, "status": status, "protected": protected, "previousRevision": branch["revision"]})
            row = con.execute("SELECT * FROM workspace_branches WHERE id=?", (branch["id"],)).fetchone()
            return {"ok": True, "branch": self._branch_record(row)}

    def create_snapshot(self, workspace_id: str, branch_ref: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "snapshot", False)
            branch = self._branch(con, workspace_id, branch_ref)
            if branch["status"] != "active":
                raise WorkspaceVersionError("Snapshots can be created only on active branches.", 409)
            expected = payload.get("expectedHeadSnapshotId", _MISSING)
            if expected is _MISSING:
                raise WorkspaceVersionError("expectedHeadSnapshotId is required for conflict-safe snapshots.")
            if (expected or None) != branch["head_snapshot_id"]:
                raise WorkspaceVersionError(f"Branch head conflict: expected {expected!r}, current {branch['head_snapshot_id']!r}.", 409)
            parent = self._snapshot(con, workspace_id, branch["head_snapshot_id"])
            base_tree = self._tree_for_snapshot(parent)
            if "tree" in payload:
                tree = _tree(payload.get("tree"))
            else:
                tree = copy.deepcopy(base_tree)
                changes = payload.get("changes")
                if not isinstance(changes, list) or not changes:
                    raise WorkspaceVersionError("A complete tree or a non-empty changes list is required.")
                for change in changes:
                    if not isinstance(change, dict):
                        raise WorkspaceVersionError("Each snapshot change must be an object.")
                    operation = _text(change.get("operation") or "set", 20).lower()
                    path = _text(change.get("path"), 500)
                    if not path or path.startswith("/") or ".." in path.split("/"):
                        raise WorkspaceVersionError("A valid relative change path is required.")
                    if operation == "set":
                        tree[path] = copy.deepcopy(change.get("value"))
                    elif operation == "remove":
                        tree.pop(path, None)
                    else:
                        raise WorkspaceVersionError("Snapshot changes support only set and remove operations.")
                tree = _tree(tree)
            tree_hash = _hash(tree)
            if parent and tree_hash == parent["tree_hash"]:
                raise WorkspaceVersionError("The snapshot tree is unchanged from the branch head.", 409)
            snapshot_id = _id(payload.get("id") or f"snapshot-{secrets.token_hex(12)}", "snapshot ID")
            message = _text(payload.get("message"), 500)
            if not message:
                raise WorkspaceVersionError("A snapshot message is required.")
            metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
            now = _now()
            try:
                con.execute(
                    "INSERT INTO workspace_snapshots(id,workspace_id,branch_id,parent_snapshot_id,message,tree_json,tree_hash,author_id,metadata_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (snapshot_id, workspace_id, branch["id"], branch["head_snapshot_id"], message, _stable(tree), tree_hash, actor_id, _stable(metadata), now),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkspaceVersionError("The snapshot ID already exists.", 409) from exc
            con.execute("UPDATE workspace_branches SET head_snapshot_id=?,updated_at=?,revision=revision+1 WHERE id=?", (snapshot_id, now, branch["id"]))
            self._event(con, workspace_id, "snapshot-created", actor_id, {"snapshotId": snapshot_id, "branchId": branch["id"], "parentSnapshotId": branch["head_snapshot_id"], "treeHash": tree_hash, "message": message})
            row = con.execute("SELECT * FROM workspace_snapshots WHERE id=?", (snapshot_id,)).fetchone()
            updated_branch = con.execute("SELECT * FROM workspace_branches WHERE id=?", (branch["id"],)).fetchone()
            return {"ok": True, "snapshot": self._snapshot_record(row), "branch": self._branch_record(updated_branch)}

    def restore_snapshot(self, workspace_id: str, branch_ref: str, snapshot_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id, snapshot_id = _id(workspace_id), _id(actor_id), _id(snapshot_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "snapshot", False)
            branch = self._branch(con, workspace_id, branch_ref)
            source = self._snapshot(con, workspace_id, snapshot_id)
            payload = dict(payload or {})
            payload["tree"] = json.loads(source["tree_json"])
            payload["message"] = _text(payload.get("message"), 500) or f"Restore snapshot {snapshot_id}"
            payload["metadata"] = {**(payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}), "restoredFromSnapshotId": snapshot_id}
            payload["expectedHeadSnapshotId"] = payload.get("expectedHeadSnapshotId", branch["head_snapshot_id"])
        return self.create_snapshot(workspace_id, branch_ref, payload, actor_id)

    def list_snapshots(self, workspace_id: str, branch_ref: str, actor_id: str, limit: int = 200) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            branch = self._branch(con, workspace_id, branch_ref)
            rows = con.execute("SELECT * FROM workspace_snapshots WHERE workspace_id=? AND branch_id=? ORDER BY created_at DESC,id DESC LIMIT ?", (workspace_id, branch["id"], max(1, min(5000, int(limit))))).fetchall()
            return {"ok": True, "branch": self._branch_record(branch), "snapshots": [self._snapshot_record(row, False) for row in rows]}

    def get_snapshot(self, workspace_id: str, snapshot_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id, snapshot_id = _id(workspace_id), _id(actor_id), _id(snapshot_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            row = self._snapshot(con, workspace_id, snapshot_id)
            return {"ok": True, "snapshot": self._snapshot_record(row)}

    def compare(self, workspace_id: str, from_snapshot_id: str | None, to_snapshot_id: str | None, actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            left = self._snapshot(con, workspace_id, from_snapshot_id) if from_snapshot_id else None
            right = self._snapshot(con, workspace_id, to_snapshot_id) if to_snapshot_id else None
            left_tree, right_tree = self._tree_for_snapshot(left), self._tree_for_snapshot(right)
            added, removed, changed, unchanged = [], [], [], []
            for path in sorted(set(left_tree) | set(right_tree)):
                before = left_tree.get(path, _MISSING); after = right_tree.get(path, _MISSING)
                if before is _MISSING:
                    added.append({"path": path, "value": after})
                elif after is _MISSING:
                    removed.append({"path": path, "value": before})
                elif before != after:
                    changed.append({"path": path, "before": before, "after": after})
                else:
                    unchanged.append(path)
            body = {
                "schema": COMPARE_SCHEMA, "version": VERSION, "workspaceId": workspace_id,
                "fromSnapshotId": from_snapshot_id, "toSnapshotId": to_snapshot_id,
                "added": added, "removed": removed, "changed": changed,
                "unchangedPathCount": len(unchanged), "differenceCount": len(added) + len(removed) + len(changed),
            }
            body["compareHash"] = _hash(body)
            return {"ok": True, "comparison": body}

    def _ancestors(self, con: sqlite3.Connection, workspace_id: str, snapshot_id: str | None) -> dict[str, int]:
        distances: dict[str, int] = {}
        queue: list[tuple[str, int]] = [(snapshot_id, 0)] if snapshot_id else []
        while queue and len(distances) < 10000:
            current, distance = queue.pop(0)
            if current in distances and distances[current] <= distance:
                continue
            distances[current] = distance
            row = self._snapshot(con, workspace_id, current)
            for parent in (row["parent_snapshot_id"], row["merge_parent_snapshot_id"]):
                if parent:
                    queue.append((parent, distance + 1))
        return distances

    def _merge_base(self, con: sqlite3.Connection, workspace_id: str, source_id: str | None, target_id: str | None) -> str | None:
        if not source_id or not target_id:
            return None
        source = self._ancestors(con, workspace_id, source_id)
        target = self._ancestors(con, workspace_id, target_id)
        common = set(source) & set(target)
        if not common:
            return None
        return min(common, key=lambda item: (source[item] + target[item], max(source[item], target[item]), item))

    @staticmethod
    def _value(tree: dict[str, Any], path: str) -> Any:
        return tree[path] if path in tree else _MISSING

    @staticmethod
    def _json_or_none(value: Any) -> str | None:
        return None if value is _MISSING else _stable(value)

    def _three_way(self, base: dict[str, Any], source: dict[str, Any], target: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        merged: dict[str, Any] = {}
        conflicts: list[dict[str, Any]] = []
        for path in sorted(set(base) | set(source) | set(target)):
            b, s, t = self._value(base, path), self._value(source, path), self._value(target, path)
            if s == t:
                chosen = s
            elif s == b:
                chosen = t
            elif t == b:
                chosen = s
            else:
                conflicts.append({"path": path, "base": b, "source": s, "target": t})
                continue
            if chosen is not _MISSING:
                merged[path] = copy.deepcopy(chosen)
        return _tree(merged), conflicts

    def create_merge_request(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "snapshot", False)
            source = self._branch(con, workspace_id, _text(payload.get("sourceBranchId") or payload.get("sourceBranch"), 180))
            target = self._branch(con, workspace_id, _text(payload.get("targetBranchId") or payload.get("targetBranch") or "main", 180))
            if source["id"] == target["id"]:
                raise WorkspaceVersionError("Source and target branches must be different.")
            if source["status"] != "active" or target["status"] != "active":
                raise WorkspaceVersionError("Merge requests require active source and target branches.", 409)
            if not source["head_snapshot_id"]:
                raise WorkspaceVersionError("The source branch has no snapshots to merge.", 409)
            existing = con.execute("SELECT id FROM workspace_merge_requests WHERE source_branch_id=? AND target_branch_id=? AND status IN ('open','conflicted','ready')", (source["id"], target["id"])).fetchone()
            if existing:
                raise WorkspaceVersionError("An active merge request already exists for these branches.", 409)
            base_id = self._merge_base(con, workspace_id, source["head_snapshot_id"], target["head_snapshot_id"])
            base = self._snapshot(con, workspace_id, base_id) if base_id else None
            source_snapshot = self._snapshot(con, workspace_id, source["head_snapshot_id"])
            target_snapshot = self._snapshot(con, workspace_id, target["head_snapshot_id"]) if target["head_snapshot_id"] else None
            merged, conflicts = self._three_way(self._tree_for_snapshot(base), self._tree_for_snapshot(source_snapshot), self._tree_for_snapshot(target_snapshot))
            status = "conflicted" if conflicts else "ready"
            merge_id = _id(payload.get("id") or f"merge-{secrets.token_hex(10)}", "merge request ID")
            title = _text(payload.get("title"), 300) or f"Merge {source['name']} into {target['name']}"
            description = _text(payload.get("description"), 2000)
            approval_id = _text(payload.get("approvalRequestId"), 180) or None
            if approval_id:
                approval = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (approval_id, workspace_id)).fetchone()
                if not approval:
                    raise WorkspaceVersionError("Approval request not found in this workspace.", 404)
            now = _now()
            con.execute(
                "INSERT INTO workspace_merge_requests(id,workspace_id,source_branch_id,target_branch_id,base_snapshot_id,source_snapshot_id,target_snapshot_id,title,description,status,approval_request_id,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (merge_id, workspace_id, source["id"], target["id"], base_id, source["head_snapshot_id"], target["head_snapshot_id"], title, description, status, approval_id, actor_id, now, now),
            )
            for item in conflicts:
                conflict_id = f"conflict-{secrets.token_hex(10)}"
                conflict_hash = _hash({"mergeRequestId": merge_id, "path": item["path"], "base": None if item["base"] is _MISSING else item["base"], "source": None if item["source"] is _MISSING else item["source"], "target": None if item["target"] is _MISSING else item["target"]})
                con.execute(
                    "INSERT INTO workspace_merge_conflicts(id,merge_request_id,workspace_id,path,base_json,source_json,target_json,status,conflict_hash) VALUES(?,?,?,?,?,?,?,?,?)",
                    (conflict_id, merge_id, workspace_id, item["path"], self._json_or_none(item["base"]), self._json_or_none(item["source"]), self._json_or_none(item["target"]), "open", conflict_hash),
                )
            self._event(con, workspace_id, "merge-request-created", actor_id, {"mergeRequestId": merge_id, "sourceBranchId": source["id"], "targetBranchId": target["id"], "baseSnapshotId": base_id, "sourceSnapshotId": source["head_snapshot_id"], "targetSnapshotId": target["head_snapshot_id"], "status": status, "conflictCount": len(conflicts), "cleanTreeHash": _hash(merged)})
            row = con.execute("SELECT * FROM workspace_merge_requests WHERE id=?", (merge_id,)).fetchone()
            return {"ok": True, "mergeRequest": self._merge_record(con, row)}

    def list_merge_requests(self, workspace_id: str, actor_id: str, status: str | None = None, limit: int = 200) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            clauses, params = ["workspace_id=?"], [workspace_id]
            if status:
                if status not in MERGE_STATUSES:
                    raise WorkspaceVersionError("Unsupported merge status.")
                clauses.append("status=?"); params.append(status)
            params.append(max(1, min(5000, int(limit))))
            rows = con.execute(f"SELECT * FROM workspace_merge_requests WHERE {' AND '.join(clauses)} ORDER BY updated_at DESC,id DESC LIMIT ?", params).fetchall()
            return {"ok": True, "version": VERSION, "mergeRequests": [self._merge_record(con, row, False) for row in rows]}

    def get_merge_request(self, workspace_id: str, merge_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, merge_id, actor_id = _id(workspace_id), _id(merge_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            row = con.execute("SELECT * FROM workspace_merge_requests WHERE id=? AND workspace_id=?", (merge_id, workspace_id)).fetchone()
            if not row:
                raise WorkspaceVersionError("Merge request not found.", 404)
            return {"ok": True, "mergeRequest": self._merge_record(con, row)}

    def resolve_conflict(self, workspace_id: str, merge_id: str, conflict_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, merge_id, conflict_id, actor_id = _id(workspace_id), _id(merge_id), _id(conflict_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "review", False)
            merge = con.execute("SELECT * FROM workspace_merge_requests WHERE id=? AND workspace_id=?", (merge_id, workspace_id)).fetchone()
            if not merge:
                raise WorkspaceVersionError("Merge request not found.", 404)
            self._expect_revision(payload, merge["revision"])
            if merge["status"] not in {"conflicted", "ready"}:
                raise WorkspaceVersionError("This merge request no longer accepts conflict resolutions.", 409)
            conflict = con.execute("SELECT * FROM workspace_merge_conflicts WHERE id=? AND merge_request_id=?", (conflict_id, merge_id)).fetchone()
            if not conflict:
                raise WorkspaceVersionError("Merge conflict not found.", 404)
            if conflict["status"] == "resolved":
                raise WorkspaceVersionError("The merge conflict is already resolved.", 409)
            resolution = _text(payload.get("resolution"), 20).lower()
            if resolution not in RESOLUTIONS:
                raise WorkspaceVersionError("Unsupported conflict resolution.")
            mapping = {"base": conflict["base_json"], "source": conflict["source_json"], "target": conflict["target_json"]}
            resolved_json = _stable(payload.get("value")) if resolution == "custom" else mapping[resolution]
            now = _now()
            con.execute("UPDATE workspace_merge_conflicts SET status='resolved',resolution=?,resolved_json=?,resolved_by=?,resolved_at=? WHERE id=?", (resolution, resolved_json, actor_id, now, conflict_id))
            remaining = con.execute("SELECT COUNT(*) FROM workspace_merge_conflicts WHERE merge_request_id=? AND status='open'", (merge_id,)).fetchone()[0]
            new_status = "ready" if remaining == 0 else "conflicted"
            con.execute("UPDATE workspace_merge_requests SET status=?,updated_at=?,revision=revision+1 WHERE id=?", (new_status, now, merge_id))
            self._event(con, workspace_id, "merge-conflict-resolved", actor_id, {"mergeRequestId": merge_id, "conflictId": conflict_id, "path": conflict["path"], "resolution": resolution, "remainingConflicts": remaining})
            updated = con.execute("SELECT * FROM workspace_merge_requests WHERE id=?", (merge_id,)).fetchone()
            return {"ok": True, "mergeRequest": self._merge_record(con, updated)}

    def attach_approval(self, workspace_id: str, merge_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, merge_id, actor_id = _id(workspace_id), _id(merge_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "branch", False)
            merge = con.execute("SELECT * FROM workspace_merge_requests WHERE id=? AND workspace_id=?", (merge_id, workspace_id)).fetchone()
            if not merge:
                raise WorkspaceVersionError("Merge request not found.", 404)
            self._expect_revision(payload, merge["revision"])
            if merge["status"] not in {"open", "conflicted", "ready"}:
                raise WorkspaceVersionError("Approval cannot be changed after a merge closes.", 409)
            approval_id = _id(payload.get("approvalRequestId"), "approval request ID")
            approval = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (approval_id, workspace_id)).fetchone()
            if not approval:
                raise WorkspaceVersionError("Approval request not found in this workspace.", 404)
            now = _now()
            con.execute("UPDATE workspace_merge_requests SET approval_request_id=?,updated_at=?,revision=revision+1 WHERE id=?", (approval_id, now, merge_id))
            self._event(con, workspace_id, "merge-approval-attached", actor_id, {"mergeRequestId": merge_id, "approvalRequestId": approval_id, "approvalStatus": approval["status"]})
            updated = con.execute("SELECT * FROM workspace_merge_requests WHERE id=?", (merge_id,)).fetchone()
            return {"ok": True, "mergeRequest": self._merge_record(con, updated)}

    def _merge_tree(self, con: sqlite3.Connection, merge: sqlite3.Row) -> dict[str, Any]:
        base = self._snapshot(con, merge["workspace_id"], merge["base_snapshot_id"]) if merge["base_snapshot_id"] else None
        source = self._snapshot(con, merge["workspace_id"], merge["source_snapshot_id"])
        target = self._snapshot(con, merge["workspace_id"], merge["target_snapshot_id"]) if merge["target_snapshot_id"] else None
        merged, conflicts = self._three_way(self._tree_for_snapshot(base), self._tree_for_snapshot(source), self._tree_for_snapshot(target))
        conflict_rows = con.execute("SELECT * FROM workspace_merge_conflicts WHERE merge_request_id=?", (merge["id"],)).fetchall()
        resolution_by_path = {row["path"]: row for row in conflict_rows}
        for conflict in conflicts:
            row = resolution_by_path.get(conflict["path"])
            if not row or row["status"] != "resolved":
                raise WorkspaceVersionError("All merge conflicts must be resolved before finalization.", 409)
            if row["resolved_json"] is not None:
                merged[row["path"]] = json.loads(row["resolved_json"])
            else:
                merged.pop(row["path"], None)
        return _tree(merged)

    def finalize_merge(self, workspace_id: str, merge_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, merge_id, actor_id = _id(workspace_id), _id(merge_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "merge", False)
            merge = con.execute("SELECT * FROM workspace_merge_requests WHERE id=? AND workspace_id=?", (merge_id, workspace_id)).fetchone()
            if not merge:
                raise WorkspaceVersionError("Merge request not found.", 404)
            self._expect_revision(payload, merge["revision"])
            if merge["status"] != "ready":
                raise WorkspaceVersionError("Only a ready merge request can be finalized.", 409)
            source = self._branch(con, workspace_id, merge["source_branch_id"])
            target = self._branch(con, workspace_id, merge["target_branch_id"])
            if source["head_snapshot_id"] != merge["source_snapshot_id"] or target["head_snapshot_id"] != merge["target_snapshot_id"]:
                raise WorkspaceVersionError("A branch head changed after the merge request was opened. Open a new merge request.", 409)
            if target["protected"]:
                if not merge["approval_request_id"]:
                    raise WorkspaceVersionError("Protected branches require an attached signed scientific approval.", 409)
                approval = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (merge["approval_request_id"], workspace_id)).fetchone()
                signoff = con.execute("SELECT * FROM scientific_signoffs WHERE approval_id=? AND workspace_id=?", (merge["approval_request_id"], workspace_id)).fetchone()
                if not approval or approval["status"] != "signed" or not signoff:
                    raise WorkspaceVersionError("The attached scientific approval must be signed before merging to a protected branch.", 409)
            tree = self._merge_tree(con, merge)
            result_id = _id(payload.get("snapshotId") or f"snapshot-{secrets.token_hex(12)}", "result snapshot ID")
            message = _text(payload.get("message"), 500) or f"Merge {source['name']} into {target['name']}"
            now = _now()
            metadata = {"mergeRequestId": merge_id, "sourceBranchId": source["id"], "targetBranchId": target["id"], "approvalRequestId": merge["approval_request_id"]}
            con.execute(
                "INSERT INTO workspace_snapshots(id,workspace_id,branch_id,parent_snapshot_id,merge_parent_snapshot_id,message,tree_json,tree_hash,author_id,metadata_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (result_id, workspace_id, target["id"], target["head_snapshot_id"], source["head_snapshot_id"], message, _stable(tree), _hash(tree), actor_id, _stable(metadata), now),
            )
            con.execute("UPDATE workspace_branches SET head_snapshot_id=?,updated_at=?,revision=revision+1 WHERE id=?", (result_id, now, target["id"]))
            if source["name"] != "main":
                con.execute("UPDATE workspace_branches SET status='merged',merged_at=?,updated_at=?,revision=revision+1 WHERE id=?", (now, now, source["id"]))
            con.execute("UPDATE workspace_merge_requests SET status='merged',result_snapshot_id=?,merged_by=?,merged_at=?,updated_at=?,revision=revision+1 WHERE id=?", (result_id, actor_id, now, now, merge_id))
            self._event(con, workspace_id, "merge-finalized", actor_id, {"mergeRequestId": merge_id, "sourceBranchId": source["id"], "targetBranchId": target["id"], "resultSnapshotId": result_id, "treeHash": _hash(tree), "approvalRequestId": merge["approval_request_id"]})
            updated = con.execute("SELECT * FROM workspace_merge_requests WHERE id=?", (merge_id,)).fetchone()
            snapshot = con.execute("SELECT * FROM workspace_snapshots WHERE id=?", (result_id,)).fetchone()
            return {"ok": True, "mergeRequest": self._merge_record(con, updated), "snapshot": self._snapshot_record(snapshot)}

    def cancel_merge(self, workspace_id: str, merge_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, merge_id, actor_id = _id(workspace_id), _id(merge_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "branch", False)
            merge = con.execute("SELECT * FROM workspace_merge_requests WHERE id=? AND workspace_id=?", (merge_id, workspace_id)).fetchone()
            if not merge:
                raise WorkspaceVersionError("Merge request not found.", 404)
            self._expect_revision(payload, merge["revision"])
            if merge["status"] in {"merged", "cancelled"}:
                raise WorkspaceVersionError("The merge request is already closed.", 409)
            reason = _text(payload.get("reason"), 1000)
            if not reason:
                raise WorkspaceVersionError("A cancellation reason is required.")
            now = _now()
            con.execute("UPDATE workspace_merge_requests SET status='cancelled',cancelled_by=?,cancelled_at=?,cancel_reason=?,updated_at=?,revision=revision+1 WHERE id=?", (actor_id, now, reason, now, merge_id))
            self._event(con, workspace_id, "merge-cancelled", actor_id, {"mergeRequestId": merge_id, "reason": reason})
            updated = con.execute("SELECT * FROM workspace_merge_requests WHERE id=?", (merge_id,)).fetchone()
            return {"ok": True, "mergeRequest": self._merge_record(con, updated)}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            rows = con.execute("SELECT * FROM workspace_version_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(self.history_limit, int(limit))))).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "workspaceId": row["workspace_id"], "eventType": row["event_type"], "actorId": row["actor_id"], "details": json.loads(row["details_json"]), "eventHash": row["event_hash"], "createdAt": row["created_at"]} for row in reversed(rows)]
            return {"ok": True, "version": VERSION, "events": events}
