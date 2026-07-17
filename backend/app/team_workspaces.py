from __future__ import annotations

import copy
import json
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.35.0"
WORKSPACE_SCHEMA = "sc-lab-team-workspace/0.35.0"
MEMBERSHIP_SCHEMA = "sc-lab-workspace-membership/0.35.0"
INVITATION_SCHEMA = "sc-lab-workspace-invitation/0.35.0"
RESOURCE_SCHEMA = "sc-lab-workspace-resource-link/0.35.0"
EVENT_SCHEMA = "sc-lab-workspace-event/0.35.0"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
ROLES = {"viewer": 10, "reviewer": 30, "contributor": 50, "editor": 70, "administrator": 90, "owner": 100}
RESOURCE_TYPES = {
    "project", "dataset", "workflow", "workflow-run", "experiment", "campaign",
    "model", "surrogate", "ensemble", "artifact", "artifact-collection", "federated-source", "notebook", "source", "evidence", "report",
}
WORKSPACE_STATUSES = {"active", "archived"}


class TeamWorkspaceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _now() -> str:
    return _now_dt().isoformat().replace("+00:00", "Z")


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 500) -> str:
    return str(value or "").strip()[:limit]


def _id(value: Any, name: str = "identifier") -> str:
    clean = _text(value, 180)
    if not ID_RE.match(clean):
        raise TeamWorkspaceError(f"A valid {name} is required.")
    return clean


def _role(value: Any, default: str = "viewer", allow_owner: bool = True) -> str:
    clean = _text(value, 40).lower() or default
    if clean not in ROLES or (not allow_owner and clean == "owner"):
        raise TeamWorkspaceError("Unsupported workspace role.")
    return clean


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-team-workspace-policy/0.35.0",
        "roles": [{"id": key, "rank": rank} for key, rank in ROLES.items()],
        "resourceTypes": sorted(RESOURCE_TYPES),
        "capabilities": {
            "privateTeamWorkspaces": True,
            "roleBasedAccess": True,
            "singleUseInvitations": True,
            "workspaceResourceLinks": True,
            "resourceMinimumRoles": True,
            "ownershipTransfer": True,
            "archiveWithoutDeletion": True,
            "durableActivityTimeline": True,
            "reviewComments": False,
            "scientificApprovals": False,
            "arbitraryCode": False,
        },
        "roleCapabilities": {
            "viewer": ["workspace.read", "members.read", "resources.read", "timeline.read"],
            "reviewer": ["workspace.read", "members.read", "resources.read", "timeline.read", "resource.review"],
            "contributor": ["workspace.read", "members.read", "resources.read", "timeline.read", "resource.review", "resource.link"],
            "editor": ["workspace.update", "resource.link", "resource.unlink"],
            "administrator": ["member.invite", "member.update", "member.remove", "workspace.archive"],
            "owner": ["ownership.transfer"],
        },
    }


class TeamWorkspaceManager:
    def __init__(self, db_path: str, max_workspaces: int = 5000, max_members: int = 100000, history_limit: int = 100000):
        self.db_path = str(db_path)
        self.max_workspaces = max(1, int(max_workspaces))
        self.max_members = max(10, int(max_members))
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
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS workspaces(
                  id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT,
                  owner_id TEXT NOT NULL, status TEXT NOT NULL, primary_project_id TEXT,
                  settings_json TEXT NOT NULL, workspace_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, archived_at TEXT
                );
                CREATE TABLE IF NOT EXISTS memberships(
                  workspace_id TEXT NOT NULL, actor_id TEXT NOT NULL, display_name TEXT,
                  role TEXT NOT NULL, status TEXT NOT NULL, invited_by TEXT,
                  joined_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  PRIMARY KEY(workspace_id, actor_id),
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS invitations(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
                  invitee_actor_id TEXT, invitee_label TEXT, role TEXT NOT NULL, status TEXT NOT NULL,
                  created_by TEXT NOT NULL, accepted_by TEXT, created_at TEXT NOT NULL,
                  expires_at TEXT NOT NULL, accepted_at TEXT, revoked_at TEXT,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS resource_links(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, resource_type TEXT NOT NULL,
                  resource_id TEXT NOT NULL, title TEXT, minimum_role TEXT NOT NULL,
                  metadata_json TEXT NOT NULL, linked_by TEXT NOT NULL, linked_at TEXT NOT NULL,
                  UNIQUE(workspace_id, resource_type, resource_id),
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL,
                  event_type TEXT NOT NULL, actor_id TEXT NOT NULL, details_json TEXT NOT NULL,
                  event_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                  FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_members_actor ON memberships(actor_id, status);
                CREATE INDEX IF NOT EXISTS idx_invites_workspace ON invitations(workspace_id, status);
                CREATE INDEX IF NOT EXISTS idx_resources_workspace ON resource_links(workspace_id, resource_type);
                CREATE INDEX IF NOT EXISTS idx_events_workspace ON events(workspace_id, sequence);
                """
            )
            con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version','1')")

    def _event(self, con: sqlite3.Connection, workspace_id: str, event_type: str, actor_id: str, details: dict[str, Any]) -> None:
        created_at = _now()
        event_hash = _hash({"workspaceId": workspace_id, "eventType": event_type, "actorId": actor_id, "details": details, "createdAt": created_at})
        con.execute(
            "INSERT INTO events(workspace_id,event_type,actor_id,details_json,event_hash,created_at) VALUES(?,?,?,?,?,?)",
            (workspace_id, event_type, actor_id, _stable(details), event_hash, created_at),
        )

    def _membership(self, con: sqlite3.Connection, workspace_id: str, actor_id: str) -> sqlite3.Row | None:
        return con.execute(
            "SELECT * FROM memberships WHERE workspace_id=? AND actor_id=? AND status='active'",
            (workspace_id, actor_id),
        ).fetchone()

    def _require(self, con: sqlite3.Connection, workspace_id: str, actor_id: str, minimum: str = "viewer", allow_archived: bool = True) -> tuple[sqlite3.Row, sqlite3.Row]:
        workspace = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
        if not workspace:
            raise TeamWorkspaceError("Workspace not found.", 404)
        if not allow_archived and workspace["status"] == "archived":
            raise TeamWorkspaceError("The workspace is archived and read-only.", 409)
        member = self._membership(con, workspace_id, actor_id)
        if not member:
            raise TeamWorkspaceError("Workspace membership is required.", 403)
        if ROLES[member["role"]] < ROLES[minimum]:
            raise TeamWorkspaceError(f"The {minimum} role or higher is required.", 403)
        return workspace, member

    def _workspace_record(self, con: sqlite3.Connection, row: sqlite3.Row, actor_id: str, include_members: bool = False, include_resources: bool = False) -> dict[str, Any]:
        member = self._membership(con, row["id"], actor_id)
        record: dict[str, Any] = {
            "schema": WORKSPACE_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "ownerId": row["owner_id"],
            "status": row["status"],
            "primaryProjectId": row["primary_project_id"],
            "settings": json.loads(row["settings_json"]),
            "workspaceHash": row["workspace_hash"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "archivedAt": row["archived_at"],
            "currentMembership": self._membership_record(member) if member else None,
        }
        if include_members:
            rows = con.execute("SELECT * FROM memberships WHERE workspace_id=? ORDER BY CASE role WHEN 'owner' THEN 0 WHEN 'administrator' THEN 1 WHEN 'editor' THEN 2 WHEN 'contributor' THEN 3 WHEN 'reviewer' THEN 4 ELSE 5 END, actor_id", (row["id"],)).fetchall()
            record["members"] = [self._membership_record(item) for item in rows]
        if include_resources:
            rows = con.execute("SELECT * FROM resource_links WHERE workspace_id=? ORDER BY linked_at DESC", (row["id"],)).fetchall()
            role = member["role"] if member else "viewer"
            record["resources"] = [self._resource_record(item) for item in rows if ROLES[role] >= ROLES[item["minimum_role"]]]
        return record

    @staticmethod
    def _membership_record(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return {
            "schema": MEMBERSHIP_SCHEMA,
            "version": VERSION,
            "workspaceId": row["workspace_id"],
            "actorId": row["actor_id"],
            "displayName": row["display_name"],
            "role": row["role"],
            "status": row["status"],
            "invitedBy": row["invited_by"],
            "joinedAt": row["joined_at"],
            "updatedAt": row["updated_at"],
        }

    @staticmethod
    def _resource_record(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": RESOURCE_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "workspaceId": row["workspace_id"],
            "resourceType": row["resource_type"],
            "resourceId": row["resource_id"],
            "title": row["title"],
            "minimumRole": row["minimum_role"],
            "metadata": json.loads(row["metadata_json"]),
            "linkedBy": row["linked_by"],
            "linkedAt": row["linked_at"],
        }

    def create(self, payload: dict[str, Any], actor_id: str, display_name: str | None = None) -> dict[str, Any]:
        actor_id = _id(actor_id, "actor ID")
        source = payload.get("workspace") if isinstance(payload.get("workspace"), dict) else payload
        workspace_id = _id(source.get("id"), "workspace ID")
        title = _text(source.get("title"), 300) or workspace_id
        description = _text(source.get("description"), 4000) or None
        primary_project = _text(source.get("primaryProjectId"), 180) or None
        if primary_project and not ID_RE.match(primary_project):
            raise TeamWorkspaceError("primaryProjectId must be a valid identifier.")
        settings = copy.deepcopy(source.get("settings")) if isinstance(source.get("settings"), dict) else {}
        settings = {
            "resourceDefaultRole": _role(settings.get("resourceDefaultRole"), "viewer", allow_owner=False),
            "invitationExpiryHours": max(1, min(720, int(settings.get("invitationExpiryHours") or 168))),
            "memberDiscovery": settings.get("memberDiscovery", "workspace-only") if settings.get("memberDiscovery") in {"workspace-only", "disabled"} else "workspace-only",
        }
        created_at = _now()
        workspace_hash = _hash({"id": workspace_id, "title": title, "description": description, "ownerId": actor_id, "primaryProjectId": primary_project, "settings": settings, "createdAt": created_at})
        with self._connect() as con:
            count = con.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0]
            if count >= self.max_workspaces:
                raise TeamWorkspaceError("Workspace capacity has been reached.", 409)
            try:
                con.execute(
                    "INSERT INTO workspaces(id,title,description,owner_id,status,primary_project_id,settings_json,workspace_hash,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (workspace_id, title, description, actor_id, "active", primary_project, _stable(settings), workspace_hash, created_at, created_at),
                )
            except sqlite3.IntegrityError as exc:
                raise TeamWorkspaceError("A workspace with this ID already exists.", 409) from exc
            con.execute(
                "INSERT INTO memberships(workspace_id,actor_id,display_name,role,status,invited_by,joined_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                (workspace_id, actor_id, _text(display_name, 200) or actor_id, "owner", "active", actor_id, created_at, created_at),
            )
            self._event(con, workspace_id, "workspace-created", actor_id, {"workspaceHash": workspace_hash, "primaryProjectId": primary_project})
            row = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
            return {"ok": True, "workspace": self._workspace_record(con, row, actor_id, True, True)}

    def list(self, actor_id: str, status: str | None = None, limit: int = 100) -> dict[str, Any]:
        actor_id = _id(actor_id, "actor ID")
        limit = max(1, min(1000, int(limit)))
        args: list[Any] = [actor_id]
        where = "m.actor_id=? AND m.status='active'"
        if status:
            if status not in WORKSPACE_STATUSES:
                raise TeamWorkspaceError("Unsupported workspace status.")
            where += " AND w.status=?"
            args.append(status)
        args.append(limit)
        with self._connect() as con:
            rows = con.execute(f"SELECT w.* FROM workspaces w JOIN memberships m ON m.workspace_id=w.id WHERE {where} ORDER BY w.updated_at DESC LIMIT ?", args).fetchall()
            return {"ok": True, "version": VERSION, "workspaces": [self._workspace_record(con, row, actor_id) for row in rows]}

    def get(self, workspace_id: str, actor_id: str, include_members: bool = True, include_resources: bool = True) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        with self._connect() as con:
            row, _ = self._require(con, workspace_id, actor_id)
            return {"ok": True, "workspace": self._workspace_record(con, row, actor_id, include_members, include_resources)}

    def update(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        with self._connect() as con:
            row, _ = self._require(con, workspace_id, actor_id, "editor", allow_archived=False)
            title = _text(payload.get("title"), 300) or row["title"]
            description = _text(payload.get("description"), 4000) if "description" in payload else row["description"]
            primary_project = _text(payload.get("primaryProjectId"), 180) if "primaryProjectId" in payload else row["primary_project_id"]
            if primary_project and not ID_RE.match(primary_project):
                raise TeamWorkspaceError("primaryProjectId must be a valid identifier.")
            settings = json.loads(row["settings_json"])
            if isinstance(payload.get("settings"), dict):
                proposed = payload["settings"]
                if "resourceDefaultRole" in proposed:
                    settings["resourceDefaultRole"] = _role(proposed["resourceDefaultRole"], "viewer", allow_owner=False)
                if "invitationExpiryHours" in proposed:
                    settings["invitationExpiryHours"] = max(1, min(720, int(proposed["invitationExpiryHours"])))
            updated_at = _now()
            workspace_hash = _hash({"id": workspace_id, "title": title, "description": description, "ownerId": row["owner_id"], "primaryProjectId": primary_project, "settings": settings, "createdAt": row["created_at"]})
            con.execute("UPDATE workspaces SET title=?,description=?,primary_project_id=?,settings_json=?,workspace_hash=?,updated_at=? WHERE id=?", (title, description, primary_project, _stable(settings), workspace_hash, updated_at, workspace_id))
            self._event(con, workspace_id, "workspace-updated", actor_id, {"workspaceHash": workspace_hash})
            updated = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
            return {"ok": True, "workspace": self._workspace_record(con, updated, actor_id, True, True)}

    def archive(self, workspace_id: str, actor_id: str, reason: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        reason = _text(reason, 1000)
        if not reason:
            raise TeamWorkspaceError("An archive reason is required.")
        with self._connect() as con:
            row, _ = self._require(con, workspace_id, actor_id, "administrator")
            if row["status"] == "archived":
                return {"ok": True, "workspace": self._workspace_record(con, row, actor_id, True, True)}
            now = _now()
            con.execute("UPDATE workspaces SET status='archived',archived_at=?,updated_at=? WHERE id=?", (now, now, workspace_id))
            con.execute("UPDATE invitations SET status='revoked',revoked_at=? WHERE workspace_id=? AND status='pending'", (now, workspace_id))
            self._event(con, workspace_id, "workspace-archived", actor_id, {"reason": reason})
            updated = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
            return {"ok": True, "workspace": self._workspace_record(con, updated, actor_id, True, True)}

    def invite(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        role = _role(payload.get("role"), "viewer", allow_owner=False)
        target = _text(payload.get("inviteeActorId"), 180) or None
        if target and not ID_RE.match(target):
            raise TeamWorkspaceError("inviteeActorId must be a valid identifier.")
        label = _text(payload.get("inviteeLabel"), 200) or target
        with self._connect() as con:
            workspace, _ = self._require(con, workspace_id, actor_id, "administrator", allow_archived=False)
            if target and self._membership(con, workspace_id, target):
                raise TeamWorkspaceError("The invitee is already a workspace member.", 409)
            member_count = con.execute("SELECT COUNT(*) FROM memberships").fetchone()[0]
            if member_count >= self.max_members:
                raise TeamWorkspaceError("Workspace membership capacity has been reached.", 409)
            settings = json.loads(workspace["settings_json"])
            expires_hours = max(1, min(720, int(payload.get("expiresHours") or settings.get("invitationExpiryHours") or 168)))
            token = secrets.token_urlsafe(32)
            invitation_id = "invite-" + secrets.token_hex(12)
            created_at = _now()
            expires_at = (_now_dt() + timedelta(hours=expires_hours)).isoformat().replace("+00:00", "Z")
            con.execute(
                "INSERT INTO invitations(id,workspace_id,token_hash,invitee_actor_id,invitee_label,role,status,created_by,created_at,expires_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (invitation_id, workspace_id, sha256(token.encode()).hexdigest(), target, label, role, "pending", actor_id, created_at, expires_at),
            )
            self._event(con, workspace_id, "member-invited", actor_id, {"invitationId": invitation_id, "inviteeActorId": target, "role": role, "expiresAt": expires_at})
            return {
                "ok": True,
                "invitation": {
                    "schema": INVITATION_SCHEMA, "version": VERSION, "id": invitation_id,
                    "workspaceId": workspace_id, "inviteeActorId": target, "inviteeLabel": label,
                    "role": role, "status": "pending", "createdBy": actor_id,
                    "createdAt": created_at, "expiresAt": expires_at,
                    "token": token,
                    "tokenNotice": "The invitation token is returned once and is stored only as a SHA-256 digest.",
                },
            }

    def accept_invitation(self, payload: dict[str, Any], actor_id: str, display_name: str | None = None) -> dict[str, Any]:
        actor_id = _id(actor_id, "actor ID")
        token = _text(payload.get("token"), 500)
        if not token:
            raise TeamWorkspaceError("An invitation token is required.")
        token_hash = sha256(token.encode()).hexdigest()
        with self._connect() as con:
            row = con.execute("SELECT * FROM invitations WHERE token_hash=?", (token_hash,)).fetchone()
            if not row:
                raise TeamWorkspaceError("Invitation not found.", 404)
            if row["status"] != "pending":
                raise TeamWorkspaceError("The invitation is no longer available.", 409)
            if datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) <= _now_dt():
                con.execute("UPDATE invitations SET status='expired' WHERE id=?", (row["id"],))
                raise TeamWorkspaceError("The invitation has expired.", 410)
            if row["invitee_actor_id"] and row["invitee_actor_id"] != actor_id:
                raise TeamWorkspaceError("This invitation is assigned to a different actor.", 403)
            workspace = con.execute("SELECT * FROM workspaces WHERE id=?", (row["workspace_id"],)).fetchone()
            if not workspace or workspace["status"] != "active":
                raise TeamWorkspaceError("The workspace is not accepting members.", 409)
            now = _now()
            con.execute(
                "INSERT INTO memberships(workspace_id,actor_id,display_name,role,status,invited_by,joined_at,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(workspace_id,actor_id) DO UPDATE SET display_name=excluded.display_name,role=excluded.role,status='active',invited_by=excluded.invited_by,updated_at=excluded.updated_at",
                (row["workspace_id"], actor_id, _text(display_name, 200) or actor_id, row["role"], "active", row["created_by"], now, now),
            )
            con.execute("UPDATE invitations SET status='accepted',accepted_by=?,accepted_at=? WHERE id=?", (actor_id, now, row["id"]))
            self._event(con, row["workspace_id"], "member-joined", actor_id, {"invitationId": row["id"], "role": row["role"]})
            workspace = con.execute("SELECT * FROM workspaces WHERE id=?", (row["workspace_id"],)).fetchone()
            return {"ok": True, "workspace": self._workspace_record(con, workspace, actor_id, True, True)}

    def set_member_role(self, workspace_id: str, member_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        member_id = _id(member_id, "member actor ID")
        actor_id = _id(actor_id, "actor ID")
        role = _role(payload.get("role"), "viewer", allow_owner=False)
        with self._connect() as con:
            workspace, actor_member = self._require(con, workspace_id, actor_id, "administrator", allow_archived=False)
            target = self._membership(con, workspace_id, member_id)
            if not target:
                raise TeamWorkspaceError("Workspace member not found.", 404)
            if target["role"] == "owner" or member_id == workspace["owner_id"]:
                raise TeamWorkspaceError("Use ownership transfer to change the owner role.", 409)
            if actor_member["role"] != "owner" and ROLES[role] >= ROLES["administrator"]:
                raise TeamWorkspaceError("Only the owner can assign administrator access.", 403)
            now = _now()
            con.execute("UPDATE memberships SET role=?,updated_at=? WHERE workspace_id=? AND actor_id=?", (role, now, workspace_id, member_id))
            self._event(con, workspace_id, "member-role-changed", actor_id, {"memberId": member_id, "previousRole": target["role"], "role": role})
            updated = self._membership(con, workspace_id, member_id)
            return {"ok": True, "membership": self._membership_record(updated)}

    def remove_member(self, workspace_id: str, member_id: str, actor_id: str, reason: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        member_id = _id(member_id, "member actor ID")
        actor_id = _id(actor_id, "actor ID")
        reason = _text(reason, 1000)
        if not reason:
            raise TeamWorkspaceError("A removal reason is required.")
        with self._connect() as con:
            workspace, actor_member = self._require(con, workspace_id, actor_id, "administrator", allow_archived=False)
            target = self._membership(con, workspace_id, member_id)
            if not target:
                raise TeamWorkspaceError("Workspace member not found.", 404)
            if member_id == workspace["owner_id"] or target["role"] == "owner":
                raise TeamWorkspaceError("The owner cannot be removed.", 409)
            if actor_member["role"] != "owner" and target["role"] == "administrator":
                raise TeamWorkspaceError("Only the owner can remove an administrator.", 403)
            now = _now()
            con.execute("UPDATE memberships SET status='removed',updated_at=? WHERE workspace_id=? AND actor_id=?", (now, workspace_id, member_id))
            self._event(con, workspace_id, "member-removed", actor_id, {"memberId": member_id, "previousRole": target["role"], "reason": reason})
            return {"ok": True, "workspaceId": workspace_id, "memberId": member_id, "status": "removed"}

    def transfer_ownership(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        new_owner = _id(payload.get("newOwnerId"), "new owner ID")
        reason = _text(payload.get("reason"), 1000)
        if not reason:
            raise TeamWorkspaceError("An ownership-transfer reason is required.")
        with self._connect() as con:
            workspace, actor_member = self._require(con, workspace_id, actor_id, "owner", allow_archived=False)
            if actor_member["role"] != "owner" or workspace["owner_id"] != actor_id:
                raise TeamWorkspaceError("Only the current owner can transfer ownership.", 403)
            target = self._membership(con, workspace_id, new_owner)
            if not target:
                raise TeamWorkspaceError("The new owner must already be an active member.", 409)
            now = _now()
            con.execute("UPDATE memberships SET role='administrator',updated_at=? WHERE workspace_id=? AND actor_id=?", (now, workspace_id, actor_id))
            con.execute("UPDATE memberships SET role='owner',updated_at=? WHERE workspace_id=? AND actor_id=?", (now, workspace_id, new_owner))
            con.execute("UPDATE workspaces SET owner_id=?,updated_at=? WHERE id=?", (new_owner, now, workspace_id))
            self._event(con, workspace_id, "ownership-transferred", actor_id, {"previousOwnerId": actor_id, "newOwnerId": new_owner, "reason": reason})
            updated = con.execute("SELECT * FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
            return {"ok": True, "workspace": self._workspace_record(con, updated, actor_id, True, True)}

    def link_resource(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        resource_type = _text(payload.get("resourceType"), 80).lower()
        if resource_type not in RESOURCE_TYPES:
            raise TeamWorkspaceError("Unsupported workspace resource type.")
        resource_id = _id(payload.get("resourceId"), "resource ID")
        minimum_role = _role(payload.get("minimumRole"), "viewer", allow_owner=False)
        title = _text(payload.get("title"), 300) or resource_id
        metadata = copy.deepcopy(payload.get("metadata")) if isinstance(payload.get("metadata"), dict) else {}
        with self._connect() as con:
            _, member = self._require(con, workspace_id, actor_id, "contributor", allow_archived=False)
            if ROLES[minimum_role] > ROLES[member["role"]]:
                raise TeamWorkspaceError("A resource cannot require a role higher than the linking member's role.", 403)
            link_id = "link-" + _hash([workspace_id, resource_type, resource_id])[:24]
            now = _now()
            try:
                con.execute("INSERT INTO resource_links(id,workspace_id,resource_type,resource_id,title,minimum_role,metadata_json,linked_by,linked_at) VALUES(?,?,?,?,?,?,?,?,?)", (link_id, workspace_id, resource_type, resource_id, title, minimum_role, _stable(metadata), actor_id, now))
            except sqlite3.IntegrityError as exc:
                raise TeamWorkspaceError("This resource is already linked to the workspace.", 409) from exc
            self._event(con, workspace_id, "resource-linked", actor_id, {"linkId": link_id, "resourceType": resource_type, "resourceId": resource_id, "minimumRole": minimum_role})
            row = con.execute("SELECT * FROM resource_links WHERE id=?", (link_id,)).fetchone()
            return {"ok": True, "resource": self._resource_record(row)}

    def unlink_resource(self, workspace_id: str, link_id: str, actor_id: str, reason: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        link_id = _id(link_id, "resource link ID")
        actor_id = _id(actor_id, "actor ID")
        reason = _text(reason, 1000)
        if not reason:
            raise TeamWorkspaceError("A resource-unlink reason is required.")
        with self._connect() as con:
            self._require(con, workspace_id, actor_id, "editor", allow_archived=False)
            row = con.execute("SELECT * FROM resource_links WHERE id=? AND workspace_id=?", (link_id, workspace_id)).fetchone()
            if not row:
                raise TeamWorkspaceError("Workspace resource link not found.", 404)
            con.execute("DELETE FROM resource_links WHERE id=?", (link_id,))
            self._event(con, workspace_id, "resource-unlinked", actor_id, {"linkId": link_id, "resourceType": row["resource_type"], "resourceId": row["resource_id"], "reason": reason})
            return {"ok": True, "workspaceId": workspace_id, "linkId": link_id, "status": "unlinked"}

    def authorize(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        action = _text(payload.get("action"), 120).lower()
        action_roles = {
            "workspace.read": "viewer", "members.read": "viewer", "resources.read": "viewer", "timeline.read": "viewer",
            "resource.review": "reviewer", "resource.link": "contributor", "workspace.update": "editor", "resource.unlink": "editor",
            "member.invite": "administrator", "member.update": "administrator", "member.remove": "administrator", "workspace.archive": "administrator",
            "ownership.transfer": "owner",
        }
        if action not in action_roles:
            raise TeamWorkspaceError("Unsupported workspace action.")
        with self._connect() as con:
            workspace, member = self._require(con, workspace_id, actor_id)
            required = action_roles[action]
            allowed = workspace["status"] == "active" or action in {"workspace.read", "members.read", "resources.read", "timeline.read"}
            allowed = allowed and ROLES[member["role"]] >= ROLES[required]
            resource = None
            link_id = _text(payload.get("resourceLinkId"), 180)
            if link_id:
                resource = con.execute("SELECT * FROM resource_links WHERE id=? AND workspace_id=?", (link_id, workspace_id)).fetchone()
                if not resource:
                    raise TeamWorkspaceError("Workspace resource link not found.", 404)
                allowed = allowed and ROLES[member["role"]] >= ROLES[resource["minimum_role"]]
            decision = {
                "workspaceId": workspace_id,
                "actorId": actor_id,
                "role": member["role"],
                "action": action,
                "requiredRole": required,
                "resourceMinimumRole": resource["minimum_role"] if resource else None,
                "allowed": bool(allowed),
                "workspaceStatus": workspace["status"],
                "decidedAt": _now(),
            }
            decision["decisionHash"] = _hash(decision)
            self._event(con, workspace_id, "access-decision", actor_id, {key: decision[key] for key in ("action", "requiredRole", "resourceMinimumRole", "allowed", "decisionHash")})
            return {"ok": True, "decision": decision}

    def timeline(self, workspace_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        workspace_id = _id(workspace_id, "workspace ID")
        actor_id = _id(actor_id, "actor ID")
        limit = max(1, min(self.history_limit, int(limit)))
        with self._connect() as con:
            self._require(con, workspace_id, actor_id)
            rows = con.execute("SELECT * FROM events WHERE workspace_id=? ORDER BY sequence DESC LIMIT ?", (workspace_id, limit)).fetchall()
            events = [{
                "schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "workspaceId": row["workspace_id"],
                "eventType": row["event_type"], "actorId": row["actor_id"], "details": json.loads(row["details_json"]),
                "eventHash": row["event_hash"], "createdAt": row["created_at"],
            } for row in reversed(rows)]
            return {"ok": True, "version": VERSION, "workspaceId": workspace_id, "events": events}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            counts = {
                "workspaces": con.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0],
                "activeWorkspaces": con.execute("SELECT COUNT(*) FROM workspaces WHERE status='active'").fetchone()[0],
                "members": con.execute("SELECT COUNT(*) FROM memberships WHERE status='active'").fetchone()[0],
                "pendingInvitations": con.execute("SELECT COUNT(*) FROM invitations WHERE status='pending'").fetchone()[0],
                "resourceLinks": con.execute("SELECT COUNT(*) FROM resource_links").fetchone()[0],
                "events": con.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            }
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            schema_version = con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]
        path = Path(self.db_path)
        return {
            "ok": integrity == "ok", "status": "ready" if integrity == "ok" else "degraded", "version": VERSION,
            "database": {"path": self.db_path, "schemaVersion": int(schema_version), "journalMode": "wal", "integrity": integrity, "bytes": path.stat().st_size if path.exists() else 0},
            "counts": counts, "roles": list(ROLES), "singleUseInvitationTokens": True, "hardDelete": False,
        }
