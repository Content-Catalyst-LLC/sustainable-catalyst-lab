from __future__ import annotations

import json
import re
import secrets
import sqlite3
from hashlib import sha256
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

VERSION = "0.35.1"
THREAD_SCHEMA = "sc-lab-review-thread/0.35.1"
COMMENT_SCHEMA = "sc-lab-review-comment/0.35.1"
ASSIGNMENT_SCHEMA = "sc-lab-review-assignment/0.35.1"
APPROVAL_SCHEMA = "sc-lab-approval-request/0.35.1"
DECISION_SCHEMA = "sc-lab-approval-decision/0.35.1"
SIGNOFF_SCHEMA = "sc-lab-scientific-signoff/0.35.1"
EVENT_SCHEMA = "sc-lab-review-event/0.35.1"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
ROLES = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
THREAD_STATUSES = {"open", "resolved", "locked"}
ASSIGNMENT_STATUSES = {"assigned", "in-review", "approved", "changes-requested", "withdrawn"}
DECISIONS = {"approve", "reject", "request-changes", "abstain"}
APPROVAL_STATUSES = {"pending", "changes-requested", "approved", "rejected", "cancelled", "signed"}


class WorkspaceReviewError(ValueError):
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
        raise WorkspaceReviewError(f"A valid {label} is required.")
    return clean


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-workspace-review-policy/0.35.1",
        "capabilities": {
            "appendOnlyComments": True,
            "nestedComments": True,
            "reviewAssignments": True,
            "approvalGates": True,
            "optimisticConcurrency": True,
            "immutableDecisions": True,
            "immutableScientificSignoff": True,
            "openThreadGate": True,
            "assignmentCompletionGate": True,
            "hardDelete": False,
            "arbitraryCode": False,
        },
        "roles": {
            "comment": ["reviewer", "contributor", "editor", "administrator", "owner"],
            "decide": ["reviewer", "editor", "administrator", "owner"],
            "manage": ["editor", "administrator", "owner"],
            "signoff": ["administrator", "owner"],
        },
        "threadStatuses": sorted(THREAD_STATUSES),
        "assignmentStatuses": sorted(ASSIGNMENT_STATUSES),
        "approvalStatuses": sorted(APPROVAL_STATUSES),
        "decisions": sorted(DECISIONS),
    }


class WorkspaceReviewManager:
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
                CREATE TABLE IF NOT EXISTS review_threads(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, resource_link_id TEXT,
                  title TEXT NOT NULL, status TEXT NOT NULL, created_by TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, resolved_by TEXT,
                  resolved_at TEXT, resolution TEXT, revision INTEGER NOT NULL DEFAULT 1,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(resource_link_id) REFERENCES resource_links(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS review_comments(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, thread_id TEXT NOT NULL,
                  parent_comment_id TEXT, actor_id TEXT NOT NULL, body TEXT NOT NULL,
                  status TEXT NOT NULL, comment_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  withdrawn_at TEXT, withdrawal_reason TEXT,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(thread_id) REFERENCES review_threads(id) ON DELETE CASCADE,
                  FOREIGN KEY(parent_comment_id) REFERENCES review_comments(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS review_assignments(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, resource_link_id TEXT NOT NULL,
                  reviewer_id TEXT NOT NULL, status TEXT NOT NULL, instructions TEXT,
                  due_at TEXT, assigned_by TEXT NOT NULL, created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL, completed_at TEXT, revision INTEGER NOT NULL DEFAULT 1,
                  UNIQUE(workspace_id, resource_link_id, reviewer_id),
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(resource_link_id) REFERENCES resource_links(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS approval_requests(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, resource_link_id TEXT NOT NULL,
                  title TEXT NOT NULL, status TEXT NOT NULL, required_approvals INTEGER NOT NULL,
                  require_no_open_threads INTEGER NOT NULL, require_assignments_complete INTEGER NOT NULL,
                  signoff_minimum_role TEXT NOT NULL, requested_by TEXT NOT NULL,
                  request_hash TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  revision INTEGER NOT NULL DEFAULT 1, summary_json TEXT NOT NULL DEFAULT '{}',
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(resource_link_id) REFERENCES resource_links(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS approval_decisions(
                  id TEXT PRIMARY KEY, approval_id TEXT NOT NULL, workspace_id TEXT NOT NULL,
                  reviewer_id TEXT NOT NULL, decision TEXT NOT NULL, rationale TEXT NOT NULL,
                  evidence_json TEXT NOT NULL, decision_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  UNIQUE(approval_id, reviewer_id),
                  FOREIGN KEY(approval_id) REFERENCES approval_requests(id) ON DELETE CASCADE,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS scientific_signoffs(
                  id TEXT PRIMARY KEY, approval_id TEXT NOT NULL UNIQUE, workspace_id TEXT NOT NULL,
                  resource_link_id TEXT NOT NULL, signed_by TEXT NOT NULL, statement TEXT NOT NULL,
                  record_json TEXT NOT NULL, signoff_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  FOREIGN KEY(approval_id) REFERENCES approval_requests(id) ON DELETE CASCADE,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                  FOREIGN KEY(resource_link_id) REFERENCES resource_links(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS review_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL,
                  event_type TEXT NOT NULL, actor_id TEXT NOT NULL, details_json TEXT NOT NULL,
                  event_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_review_threads_workspace ON review_threads(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_review_comments_thread ON review_comments(thread_id,created_at);
                CREATE INDEX IF NOT EXISTS idx_review_assignments_workspace ON review_assignments(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_approval_workspace ON approval_requests(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_review_events_workspace ON review_events(workspace_id,sequence);
                """
            )
            con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version','1')")
            current = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            if current < 2:
                con.execute("UPDATE meta SET value='2' WHERE key='schema_version'")

    def _event(self, con: sqlite3.Connection, workspace_id: str, event_type: str, actor_id: str, details: dict[str, Any]) -> None:
        created_at = _now()
        event_hash = _hash({"workspaceId": workspace_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created_at})
        con.execute("INSERT INTO review_events(workspace_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?)", (workspace_id, event_type, actor_id, _stable(details), event_hash, created_at))

    def _workspace_member(self, con: sqlite3.Connection, workspace_id: str, actor_id: str, allow_archived: bool = True) -> tuple[sqlite3.Row, sqlite3.Row]:
        workspace = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
        if not workspace:
            raise WorkspaceReviewError("Workspace not found.", 404)
        if not allow_archived and workspace["status"] == "archived":
            raise WorkspaceReviewError("The workspace is archived and read-only.", 409)
        member = con.execute("SELECT * FROM memberships WHERE workspace_id=? AND actor_id=? AND status='active'", (workspace_id, actor_id)).fetchone()
        if not member:
            raise WorkspaceReviewError("Workspace membership is required.", 403)
        return workspace, member

    @staticmethod
    def _has(role: str, capability: str) -> bool:
        if capability == "read":
            return role in ROLES
        if capability == "comment":
            return role in {"reviewer", "contributor", "editor", "administrator", "owner"}
        if capability == "decide":
            return role in {"reviewer", "editor", "administrator", "owner"}
        if capability == "manage":
            return role in {"editor", "administrator", "owner"}
        if capability == "signoff":
            return role in {"administrator", "owner"}
        return False

    def _require(self, con: sqlite3.Connection, workspace_id: str, actor_id: str, capability: str = "read", allow_archived: bool = True) -> tuple[sqlite3.Row, sqlite3.Row]:
        workspace, member = self._workspace_member(con, workspace_id, actor_id, allow_archived)
        if not self._has(member["role"], capability):
            raise WorkspaceReviewError(f"The workspace role cannot perform {capability} operations.", 403)
        return workspace, member

    def _resource(self, con: sqlite3.Connection, workspace_id: str, link_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM resource_links WHERE id=? AND workspace_id=?", (link_id, workspace_id)).fetchone()
        if not row:
            raise WorkspaceReviewError("Workspace resource link not found.", 404)
        return row

    def _member_can_review(self, con: sqlite3.Connection, workspace_id: str, actor_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM memberships WHERE workspace_id=? AND actor_id=? AND status='active'", (workspace_id, actor_id)).fetchone()
        if not row or not self._has(row["role"], "decide"):
            raise WorkspaceReviewError("The assigned actor must have a reviewer-capable role.", 409)
        return row

    @staticmethod
    def _expect_revision(payload: dict[str, Any], current: int) -> int:
        if "expectedRevision" not in payload:
            raise WorkspaceReviewError("expectedRevision is required for conflict-safe updates.")
        expected = int(payload.get("expectedRevision"))
        if expected != current:
            raise WorkspaceReviewError(f"Revision conflict: expected {expected}, current {current}.", 409)
        return expected

    def _thread_record(self, con: sqlite3.Connection, row: sqlite3.Row, include_comments: bool = True) -> dict[str, Any]:
        record = {"schema": THREAD_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "resourceLinkId": row["resource_link_id"], "title": row["title"], "status": row["status"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "resolvedBy": row["resolved_by"], "resolvedAt": row["resolved_at"], "resolution": row["resolution"], "revision": row["revision"]}
        if include_comments:
            comments = con.execute("SELECT * FROM review_comments WHERE thread_id=? ORDER BY created_at,id", (row["id"],)).fetchall()
            record["comments"] = [self._comment_record(c) for c in comments]
        return record

    @staticmethod
    def _comment_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": COMMENT_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "threadId": row["thread_id"], "parentCommentId": row["parent_comment_id"], "actorId": row["actor_id"], "body": row["body"], "status": row["status"], "commentHash": row["comment_hash"], "createdAt": row["created_at"], "withdrawnAt": row["withdrawn_at"], "withdrawalReason": row["withdrawal_reason"]}

    @staticmethod
    def _assignment_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": ASSIGNMENT_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "resourceLinkId": row["resource_link_id"], "reviewerId": row["reviewer_id"], "status": row["status"], "instructions": row["instructions"], "dueAt": row["due_at"], "assignedBy": row["assigned_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "completedAt": row["completed_at"], "revision": row["revision"]}

    def _approval_record(self, con: sqlite3.Connection, row: sqlite3.Row, include_decisions: bool = True) -> dict[str, Any]:
        record = {"schema": APPROVAL_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "resourceLinkId": row["resource_link_id"], "title": row["title"], "status": row["status"], "requiredApprovals": row["required_approvals"], "requireNoOpenThreads": bool(row["require_no_open_threads"]), "requireAssignmentsComplete": bool(row["require_assignments_complete"]), "signoffMinimumRole": row["signoff_minimum_role"], "requestedBy": row["requested_by"], "requestHash": row["request_hash"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "revision": row["revision"], "summary": json.loads(row["summary_json"] or "{}")}
        if include_decisions:
            rows = con.execute("SELECT * FROM approval_decisions WHERE approval_id=? ORDER BY created_at,id", (row["id"],)).fetchall()
            record["decisions"] = [self._decision_record(d) for d in rows]
            signoff = con.execute("SELECT * FROM scientific_signoffs WHERE approval_id=?", (row["id"],)).fetchone()
            record["signoff"] = self._signoff_record(signoff) if signoff else None
        return record

    @staticmethod
    def _decision_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": DECISION_SCHEMA, "version": VERSION, "id": row["id"], "approvalId": row["approval_id"], "workspaceId": row["workspace_id"], "reviewerId": row["reviewer_id"], "decision": row["decision"], "rationale": row["rationale"], "evidence": json.loads(row["evidence_json"]), "decisionHash": row["decision_hash"], "createdAt": row["created_at"]}

    @staticmethod
    def _signoff_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": SIGNOFF_SCHEMA, "version": VERSION, "id": row["id"], "approvalId": row["approval_id"], "workspaceId": row["workspace_id"], "resourceLinkId": row["resource_link_id"], "signedBy": row["signed_by"], "statement": row["statement"], "record": json.loads(row["record_json"]), "signoffHash": row["signoff_hash"], "createdAt": row["created_at"]}

    def create_thread(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "comment", False)
            resource_id = _text(payload.get("resourceLinkId"), 180) or None
            if resource_id:
                resource_id = _id(resource_id, "resource link ID"); self._resource(con, workspace_id, resource_id)
            thread_id = _id(payload.get("id") or f"thread-{secrets.token_hex(8)}", "thread ID")
            title = _text(payload.get("title"), 300)
            if not title:
                raise WorkspaceReviewError("A review-thread title is required.")
            now = _now()
            try:
                con.execute("INSERT INTO review_threads(id,workspace_id,resource_link_id,title,status,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)", (thread_id, workspace_id, resource_id, title, "open", actor_id, now, now))
            except sqlite3.IntegrityError as exc:
                raise WorkspaceReviewError("The review-thread ID already exists.", 409) from exc
            self._event(con, workspace_id, "review-thread-created", actor_id, {"threadId": thread_id, "resourceLinkId": resource_id, "title": title})
            row = con.execute("SELECT * FROM review_threads WHERE id=?", (thread_id,)).fetchone()
            return {"ok": True, "thread": self._thread_record(con, row)}

    def list_threads(self, workspace_id: str, actor_id: str, status: str | None = None, resource_link_id: str | None = None, limit: int = 200) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id, "workspace ID"), _id(actor_id, "actor ID")
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            clauses, params = ["workspace_id=?"], [workspace_id]
            if status:
                if status not in THREAD_STATUSES: raise WorkspaceReviewError("Unsupported thread status.")
                clauses.append("status=?"); params.append(status)
            if resource_link_id:
                clauses.append("resource_link_id=?"); params.append(_id(resource_link_id, "resource link ID"))
            params.append(max(1, min(1000, int(limit))))
            rows = con.execute(f"SELECT * FROM review_threads WHERE {' AND '.join(clauses)} ORDER BY updated_at DESC LIMIT ?", params).fetchall()
            return {"ok": True, "version": VERSION, "threads": [self._thread_record(con, r, False) for r in rows]}

    def get_thread(self, workspace_id: str, thread_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, thread_id, actor_id = _id(workspace_id), _id(thread_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            row = con.execute("SELECT * FROM review_threads WHERE id=? AND workspace_id=?", (thread_id, workspace_id)).fetchone()
            if not row: raise WorkspaceReviewError("Review thread not found.", 404)
            return {"ok": True, "thread": self._thread_record(con, row)}

    def add_comment(self, workspace_id: str, thread_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, thread_id, actor_id = _id(workspace_id), _id(thread_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "comment", False)
            thread = con.execute("SELECT * FROM review_threads WHERE id=? AND workspace_id=?", (thread_id, workspace_id)).fetchone()
            if not thread: raise WorkspaceReviewError("Review thread not found.", 404)
            if thread["status"] != "open": raise WorkspaceReviewError("Comments can be added only to an open review thread.", 409)
            parent = _text(payload.get("parentCommentId"), 180) or None
            if parent:
                parent = _id(parent, "parent comment ID")
                if not con.execute("SELECT 1 FROM review_comments WHERE id=? AND thread_id=?", (parent, thread_id)).fetchone():
                    raise WorkspaceReviewError("Parent comment not found in this thread.", 404)
            body = _text(payload.get("body"), 10000)
            if not body: raise WorkspaceReviewError("Comment body is required.")
            comment_id = _id(payload.get("id") or f"comment-{secrets.token_hex(8)}", "comment ID")
            now = _now(); digest = _hash({"workspaceId": workspace_id, "threadId": thread_id, "parentCommentId": parent, "actorId": actor_id, "body": body, "createdAt": now})
            con.execute("INSERT INTO review_comments(id,workspace_id,thread_id,parent_comment_id,actor_id,body,status,comment_hash,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (comment_id, workspace_id, thread_id, parent, actor_id, body, "active", digest, now))
            con.execute("UPDATE review_threads SET updated_at=?,revision=revision+1 WHERE id=?", (now, thread_id))
            self._event(con, workspace_id, "review-comment-added", actor_id, {"threadId": thread_id, "commentId": comment_id, "parentCommentId": parent, "commentHash": digest})
            return {"ok": True, "comment": self._comment_record(con.execute("SELECT * FROM review_comments WHERE id=?", (comment_id,)).fetchone())}

    def withdraw_comment(self, workspace_id: str, comment_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, comment_id, actor_id = _id(workspace_id), _id(comment_id), _id(actor_id)
        with self._connect() as con:
            _, member = self._require(con, workspace_id, actor_id, "comment", False)
            row = con.execute("SELECT * FROM review_comments WHERE id=? AND workspace_id=?", (comment_id, workspace_id)).fetchone()
            if not row: raise WorkspaceReviewError("Review comment not found.", 404)
            if row["status"] != "active": raise WorkspaceReviewError("The comment is already withdrawn.", 409)
            if row["actor_id"] != actor_id and member["role"] not in {"administrator", "owner"}:
                raise WorkspaceReviewError("Only the author or a workspace administrator may withdraw a comment.", 403)
            reason = _text(payload.get("reason"), 1000)
            if not reason: raise WorkspaceReviewError("A withdrawal reason is required.")
            now = _now(); con.execute("UPDATE review_comments SET status='withdrawn',withdrawn_at=?,withdrawal_reason=? WHERE id=?", (now, reason, comment_id))
            self._event(con, workspace_id, "review-comment-withdrawn", actor_id, {"commentId": comment_id, "reason": reason})
            return {"ok": True, "comment": self._comment_record(con.execute("SELECT * FROM review_comments WHERE id=?", (comment_id,)).fetchone())}

    def set_thread_status(self, workspace_id: str, thread_id: str, payload: dict[str, Any], actor_id: str, status: str) -> dict[str, Any]:
        workspace_id, thread_id, actor_id = _id(workspace_id), _id(thread_id), _id(actor_id)
        if status not in {"open", "resolved", "locked"}: raise WorkspaceReviewError("Unsupported thread status.")
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "manage", False)
            row = con.execute("SELECT * FROM review_threads WHERE id=? AND workspace_id=?", (thread_id, workspace_id)).fetchone()
            if not row: raise WorkspaceReviewError("Review thread not found.", 404)
            self._expect_revision(payload, row["revision"])
            resolution = _text(payload.get("resolution"), 4000)
            now = _now(); resolved_by = actor_id if status == "resolved" else None; resolved_at = now if status == "resolved" else None
            updated = con.execute("UPDATE review_threads SET status=?,updated_at=?,resolved_by=?,resolved_at=?,resolution=?,revision=revision+1 WHERE id=? AND revision=?", (status, now, resolved_by, resolved_at, resolution or None, thread_id, row["revision"]))
            if updated.rowcount != 1: raise WorkspaceReviewError("The review thread changed before this update.", 409)
            self._event(con, workspace_id, f"review-thread-{status}", actor_id, {"threadId": thread_id, "resolution": resolution})
            return {"ok": True, "thread": self._thread_record(con, con.execute("SELECT * FROM review_threads WHERE id=?", (thread_id,)).fetchone())}

    def create_assignment(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "manage", False)
            resource_id = _id(payload.get("resourceLinkId"), "resource link ID"); self._resource(con, workspace_id, resource_id)
            reviewer_id = _id(payload.get("reviewerId"), "reviewer ID"); self._member_can_review(con, workspace_id, reviewer_id)
            assignment_id = _id(payload.get("id") or f"assignment-{secrets.token_hex(8)}", "assignment ID")
            now = _now(); instructions = _text(payload.get("instructions"), 4000); due_at = _text(payload.get("dueAt"), 80) or None
            try:
                con.execute("INSERT INTO review_assignments(id,workspace_id,resource_link_id,reviewer_id,status,instructions,due_at,assigned_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (assignment_id, workspace_id, resource_id, reviewer_id, "assigned", instructions or None, due_at, actor_id, now, now))
            except sqlite3.IntegrityError as exc:
                raise WorkspaceReviewError("This reviewer already has an assignment for the resource.", 409) from exc
            self._event(con, workspace_id, "review-assigned", actor_id, {"assignmentId": assignment_id, "resourceLinkId": resource_id, "reviewerId": reviewer_id})
            return {"ok": True, "assignment": self._assignment_record(con.execute("SELECT * FROM review_assignments WHERE id=?", (assignment_id,)).fetchone())}

    def list_assignments(self, workspace_id: str, actor_id: str, status: str | None = None) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            if status and status not in ASSIGNMENT_STATUSES: raise WorkspaceReviewError("Unsupported assignment status.")
            rows = con.execute("SELECT * FROM review_assignments WHERE workspace_id=?" + (" AND status=?" if status else "") + " ORDER BY updated_at DESC", (workspace_id, status) if status else (workspace_id,)).fetchall()
            return {"ok": True, "version": VERSION, "assignments": [self._assignment_record(r) for r in rows]}

    def update_assignment(self, workspace_id: str, assignment_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, assignment_id, actor_id = _id(workspace_id), _id(assignment_id), _id(actor_id)
        target = _text(payload.get("status"), 40)
        if target not in ASSIGNMENT_STATUSES: raise WorkspaceReviewError("Unsupported assignment status.")
        with self._connect() as con:
            _, member = self._require(con, workspace_id, actor_id, "read", False)
            row = con.execute("SELECT * FROM review_assignments WHERE id=? AND workspace_id=?", (assignment_id, workspace_id)).fetchone()
            if not row: raise WorkspaceReviewError("Review assignment not found.", 404)
            self._expect_revision(payload, row["revision"])
            manager = self._has(member["role"], "manage")
            if actor_id != row["reviewer_id"] and not manager: raise WorkspaceReviewError("Only the assigned reviewer or a workspace manager may update this assignment.", 403)
            if target == "withdrawn" and not manager: raise WorkspaceReviewError("Only a workspace manager may withdraw an assignment.", 403)
            if target in {"approved", "changes-requested"} and actor_id != row["reviewer_id"] and member["role"] != "owner": raise WorkspaceReviewError("The assigned reviewer must complete the review.", 403)
            completed = _now() if target in {"approved", "changes-requested", "withdrawn"} else None
            now = _now(); updated = con.execute("UPDATE review_assignments SET status=?,updated_at=?,completed_at=?,revision=revision+1 WHERE id=? AND revision=?", (target, now, completed, assignment_id, row["revision"]))
            if updated.rowcount != 1: raise WorkspaceReviewError("The assignment changed before this update.", 409)
            self._event(con, workspace_id, "review-assignment-updated", actor_id, {"assignmentId": assignment_id, "status": target})
            return {"ok": True, "assignment": self._assignment_record(con.execute("SELECT * FROM review_assignments WHERE id=?", (assignment_id,)).fetchone())}

    def create_approval(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "manage", False)
            resource_id = _id(payload.get("resourceLinkId"), "resource link ID"); resource = self._resource(con, workspace_id, resource_id)
            approval_id = _id(payload.get("id") or f"approval-{secrets.token_hex(8)}", "approval request ID")
            title = _text(payload.get("title"), 300) or f"Approval for {resource['title'] or resource['resource_id']}"
            required = max(1, min(20, int(payload.get("requiredApprovals", 1))))
            no_open = 1 if payload.get("requireNoOpenThreads", True) else 0
            assignments = 1 if payload.get("requireAssignmentsComplete", True) else 0
            signoff_role = _text(payload.get("signoffMinimumRole"), 40).lower() or "administrator"
            if signoff_role not in {"administrator", "owner"}: raise WorkspaceReviewError("Sign-off minimum role must be administrator or owner.")
            now = _now(); request_data = {"workspaceId": workspace_id, "resourceLinkId": resource_id, "title": title, "requiredApprovals": required, "requireNoOpenThreads": bool(no_open), "requireAssignmentsComplete": bool(assignments), "signoffMinimumRole": signoff_role, "requestedBy": actor_id, "createdAt": now}
            digest = _hash(request_data)
            con.execute("INSERT INTO approval_requests(id,workspace_id,resource_link_id,title,status,required_approvals,require_no_open_threads,require_assignments_complete,signoff_minimum_role,requested_by,request_hash,created_at,updated_at,summary_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (approval_id, workspace_id, resource_id, title, "pending", required, no_open, assignments, signoff_role, actor_id, digest, now, now, "{}"))
            self._event(con, workspace_id, "approval-requested", actor_id, {"approvalId": approval_id, "resourceLinkId": resource_id, "requiredApprovals": required, "requestHash": digest})
            row = con.execute("SELECT * FROM approval_requests WHERE id=?", (approval_id,)).fetchone()
            return {"ok": True, "approval": self._approval_record(con, row)}

    def _gate_summary(self, con: sqlite3.Connection, approval: sqlite3.Row) -> dict[str, Any]:
        decisions = con.execute("SELECT decision,COUNT(*) c FROM approval_decisions WHERE approval_id=? GROUP BY decision", (approval["id"],)).fetchall()
        counts = {row["decision"]: row["c"] for row in decisions}
        open_threads = con.execute("SELECT COUNT(*) FROM review_threads WHERE workspace_id=? AND resource_link_id=? AND status='open'", (approval["workspace_id"], approval["resource_link_id"])).fetchone()[0]
        assignment_rows = con.execute("SELECT status FROM review_assignments WHERE workspace_id=? AND resource_link_id=?", (approval["workspace_id"], approval["resource_link_id"])).fetchall()
        assignment_statuses = [r["status"] for r in assignment_rows]
        assignments_complete = bool(assignment_rows) and all(s in {"approved", "withdrawn"} for s in assignment_statuses)
        gates = {
            "approvalCount": counts.get("approve", 0),
            "rejectionCount": counts.get("reject", 0),
            "changesRequestedCount": counts.get("request-changes", 0),
            "abstentionCount": counts.get("abstain", 0),
            "requiredApprovals": approval["required_approvals"],
            "openThreadCount": open_threads,
            "noOpenThreadsSatisfied": (not approval["require_no_open_threads"]) or open_threads == 0,
            "assignmentCount": len(assignment_statuses),
            "assignmentsComplete": (not approval["require_assignments_complete"]) or assignments_complete,
        }
        gates["readyForApproval"] = gates["approvalCount"] >= gates["requiredApprovals"] and gates["rejectionCount"] == 0 and gates["changesRequestedCount"] == 0 and gates["noOpenThreadsSatisfied"] and gates["assignmentsComplete"]
        return gates

    def _recompute_approval(self, con: sqlite3.Connection, approval_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM approval_requests WHERE id=?", (approval_id,)).fetchone()
        if row["status"] in {"cancelled", "signed"}: return row
        summary = self._gate_summary(con, row)
        if summary["rejectionCount"]:
            status = "rejected"
        elif summary["changesRequestedCount"]:
            status = "changes-requested"
        elif summary["readyForApproval"]:
            status = "approved"
        else:
            status = "pending"
        con.execute("UPDATE approval_requests SET status=?,summary_json=?,updated_at=? WHERE id=?", (status, _stable(summary), _now(), approval_id))
        return con.execute("SELECT * FROM approval_requests WHERE id=?", (approval_id,)).fetchone()

    def list_approvals(self, workspace_id: str, actor_id: str, status: str | None = None) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            if status and status not in APPROVAL_STATUSES: raise WorkspaceReviewError("Unsupported approval status.")
            rows = con.execute("SELECT * FROM approval_requests WHERE workspace_id=?" + (" AND status=?" if status else "") + " ORDER BY updated_at DESC", (workspace_id, status) if status else (workspace_id,)).fetchall()
            return {"ok": True, "version": VERSION, "approvals": [self._approval_record(con, r, False) for r in rows]}

    def get_approval(self, workspace_id: str, approval_id: str, actor_id: str) -> dict[str, Any]:
        workspace_id, approval_id, actor_id = _id(workspace_id), _id(approval_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            row = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (approval_id, workspace_id)).fetchone()
            if not row: raise WorkspaceReviewError("Approval request not found.", 404)
            row = self._recompute_approval(con, approval_id)
            return {"ok": True, "approval": self._approval_record(con, row)}

    def evaluate_approval(self, workspace_id: str, approval_id: str, actor_id: str) -> dict[str, Any]:
        body = self.get_approval(workspace_id, approval_id, actor_id)
        return {"ok": True, "version": VERSION, "approvalId": approval_id, "status": body["approval"]["status"], "revision": body["approval"]["revision"], "gates": body["approval"]["summary"]}

    def decide(self, workspace_id: str, approval_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, approval_id, actor_id = _id(workspace_id), _id(approval_id), _id(actor_id)
        decision = _text(payload.get("decision"), 40).lower()
        if decision not in DECISIONS: raise WorkspaceReviewError("Unsupported approval decision.")
        rationale = _text(payload.get("rationale"), 5000)
        if not rationale: raise WorkspaceReviewError("A decision rationale is required.")
        evidence = payload.get("evidence") if isinstance(payload.get("evidence"), list) else []
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "decide", False)
            approval = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (approval_id, workspace_id)).fetchone()
            if not approval: raise WorkspaceReviewError("Approval request not found.", 404)
            if approval["status"] in {"cancelled", "signed"}: raise WorkspaceReviewError("This approval request is closed.", 409)
            self._expect_revision(payload, approval["revision"])
            assignment = con.execute("SELECT * FROM review_assignments WHERE workspace_id=? AND resource_link_id=? AND reviewer_id=?", (workspace_id, approval["resource_link_id"], actor_id)).fetchone()
            member = con.execute("SELECT role FROM memberships WHERE workspace_id=? AND actor_id=?", (workspace_id, actor_id)).fetchone()
            if not assignment and member["role"] not in {"administrator", "owner"}:
                raise WorkspaceReviewError("A matching review assignment is required to decide this request.", 403)
            if con.execute("SELECT 1 FROM approval_decisions WHERE approval_id=? AND reviewer_id=?", (approval_id, actor_id)).fetchone():
                raise WorkspaceReviewError("Approval decisions are immutable; this reviewer has already decided.", 409)
            decision_id = _id(payload.get("id") or f"decision-{secrets.token_hex(8)}", "decision ID")
            now = _now(); decision_data = {"approvalId": approval_id, "workspaceId": workspace_id, "reviewerId": actor_id, "decision": decision, "rationale": rationale, "evidence": evidence, "createdAt": now}; digest = _hash(decision_data)
            con.execute("INSERT INTO approval_decisions(id,approval_id,workspace_id,reviewer_id,decision,rationale,evidence_json,decision_hash,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (decision_id, approval_id, workspace_id, actor_id, decision, rationale, _stable(evidence), digest, now))
            con.execute("UPDATE approval_requests SET revision=revision+1,updated_at=? WHERE id=? AND revision=?", (now, approval_id, approval["revision"]))
            if assignment:
                assignment_status = "approved" if decision == "approve" else "changes-requested" if decision in {"reject", "request-changes"} else "in-review"
                con.execute("UPDATE review_assignments SET status=?,updated_at=?,completed_at=?,revision=revision+1 WHERE id=?", (assignment_status, now, now if assignment_status in {"approved", "changes-requested"} else None, assignment["id"]))
            approval = self._recompute_approval(con, approval_id)
            self._event(con, workspace_id, "approval-decision-recorded", actor_id, {"approvalId": approval_id, "decisionId": decision_id, "decision": decision, "decisionHash": digest, "status": approval["status"]})
            return {"ok": True, "decision": self._decision_record(con.execute("SELECT * FROM approval_decisions WHERE id=?", (decision_id,)).fetchone()), "approval": self._approval_record(con, approval)}

    def cancel_approval(self, workspace_id: str, approval_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, approval_id, actor_id = _id(workspace_id), _id(approval_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "manage", False)
            row = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (approval_id, workspace_id)).fetchone()
            if not row: raise WorkspaceReviewError("Approval request not found.", 404)
            if row["status"] in {"signed", "cancelled"}: raise WorkspaceReviewError("This approval request is already closed.", 409)
            self._expect_revision(payload, row["revision"]); reason = _text(payload.get("reason"), 2000)
            if not reason: raise WorkspaceReviewError("A cancellation reason is required.")
            updated = con.execute("UPDATE approval_requests SET status='cancelled',updated_at=?,revision=revision+1,summary_json=? WHERE id=? AND revision=?", (_now(), _stable({"cancellationReason": reason}), approval_id, row["revision"]))
            if updated.rowcount != 1: raise WorkspaceReviewError("The approval request changed before cancellation.", 409)
            self._event(con, workspace_id, "approval-cancelled", actor_id, {"approvalId": approval_id, "reason": reason})
            return {"ok": True, "approval": self._approval_record(con, con.execute("SELECT * FROM approval_requests WHERE id=?", (approval_id,)).fetchone())}

    def signoff(self, workspace_id: str, approval_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id, approval_id, actor_id = _id(workspace_id), _id(approval_id), _id(actor_id)
        statement = _text(payload.get("statement"), 5000)
        if not statement: raise WorkspaceReviewError("A scientific sign-off statement is required.")
        with self._connect() as con:
            _, member = self._require(con, workspace_id, actor_id, "signoff", False)
            approval = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (approval_id, workspace_id)).fetchone()
            if not approval: raise WorkspaceReviewError("Approval request not found.", 404)
            self._expect_revision(payload, approval["revision"])
            approval = self._recompute_approval(con, approval_id)
            if approval["status"] != "approved": raise WorkspaceReviewError("All approval gates must pass before scientific sign-off.", 409)
            if ROLES[member["role"]] < ROLES[approval["signoff_minimum_role"]]: raise WorkspaceReviewError("The configured sign-off role is required.", 403)
            if con.execute("SELECT 1 FROM scientific_signoffs WHERE approval_id=?", (approval_id,)).fetchone(): raise WorkspaceReviewError("Scientific sign-off is immutable and already exists.", 409)
            decisions = [self._decision_record(r) for r in con.execute("SELECT * FROM approval_decisions WHERE approval_id=? ORDER BY created_at,id", (approval_id,)).fetchall()]
            resource = self._resource(con, workspace_id, approval["resource_link_id"])
            workspace = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
            now = _now(); record = {"approval": self._approval_record(con, approval, False), "decisions": decisions, "resource": {"linkId": resource["id"], "resourceType": resource["resource_type"], "resourceId": resource["resource_id"], "title": resource["title"], "metadata": json.loads(resource["metadata_json"])}, "workspace": {"id": workspace_id, "title": workspace["title"], "workspaceHash": workspace["workspace_hash"]}, "signedBy": actor_id, "signatoryRole": member["role"], "statement": statement, "createdAt": now}
            digest = _hash(record); signoff_id = _id(payload.get("id") or f"signoff-{secrets.token_hex(8)}", "sign-off ID")
            con.execute("INSERT INTO scientific_signoffs(id,approval_id,workspace_id,resource_link_id,signed_by,statement,record_json,signoff_hash,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (signoff_id, approval_id, workspace_id, approval["resource_link_id"], actor_id, statement, _stable(record), digest, now))
            updated = con.execute("UPDATE approval_requests SET status='signed',updated_at=?,revision=revision+1,summary_json=? WHERE id=? AND revision=?", (now, _stable({**self._gate_summary(con, approval), "signoffHash": digest}), approval_id, approval["revision"]))
            if updated.rowcount != 1: raise WorkspaceReviewError("The approval request changed before sign-off.", 409)
            self._event(con, workspace_id, "scientific-signoff-recorded", actor_id, {"approvalId": approval_id, "signoffId": signoff_id, "signoffHash": digest})
            return {"ok": True, "signoff": self._signoff_record(con.execute("SELECT * FROM scientific_signoffs WHERE id=?", (signoff_id,)).fetchone()), "approval": self._approval_record(con, con.execute("SELECT * FROM approval_requests WHERE id=?", (approval_id,)).fetchone())}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        workspace_id, actor_id = _id(workspace_id), _id(actor_id)
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            rows = con.execute("SELECT * FROM review_events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, max(1, min(self.history_limit, int(limit))))).fetchall()
            events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": r["sequence"], "workspaceId": r["workspace_id"], "eventType": r["event_type"], "actorId": r["actor_id"], "details": json.loads(r["details_json"]), "eventHash": r["event_hash"], "createdAt": r["created_at"]} for r in reversed(rows)]
            return {"ok": True, "version": VERSION, "workspaceId": workspace_id, "events": events}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            counts = {
                "threads": con.execute("SELECT COUNT(*) FROM review_threads").fetchone()[0],
                "openThreads": con.execute("SELECT COUNT(*) FROM review_threads WHERE status='open'").fetchone()[0],
                "comments": con.execute("SELECT COUNT(*) FROM review_comments").fetchone()[0],
                "assignments": con.execute("SELECT COUNT(*) FROM review_assignments").fetchone()[0],
                "pendingApprovals": con.execute("SELECT COUNT(*) FROM approval_requests WHERE status IN ('pending','changes-requested','approved')").fetchone()[0],
                "signedApprovals": con.execute("SELECT COUNT(*) FROM approval_requests WHERE status='signed'").fetchone()[0],
                "decisions": con.execute("SELECT COUNT(*) FROM approval_decisions").fetchone()[0],
                "signoffs": con.execute("SELECT COUNT(*) FROM scientific_signoffs").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM review_events").fetchone()[0],
            }
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema_version = int(con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
        path = Path(self.db_path)
        return {"ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION, "database": {"path": self.db_path, "schemaVersion": schema_version, "journalMode": "wal", "integrity": integrity, "bytes": path.stat().st_size if path.exists() else 0}, "counts": counts, "appendOnlyComments": True, "immutableDecisions": True, "immutableSignoff": True, "hardDelete": False}
