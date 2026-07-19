from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

VERSION = "0.39.0"
INSTITUTION_SCHEMA = "sc-lab-institution/0.39.0"
UNIT_SCHEMA = "sc-lab-organizational-unit/0.39.0"
PRINCIPAL_SCHEMA = "sc-lab-institutional-principal/0.39.0"
BINDING_SCHEMA = "sc-lab-institutional-role-binding/0.39.0"
RETENTION_SCHEMA = "sc-lab-retention-policy/0.39.0"
WORKSPACE_GOVERNANCE_SCHEMA = "sc-lab-workspace-governance/0.39.0"
DECISION_SCHEMA = "sc-lab-governance-decision/0.39.0"
APPROVAL_REQUEST_SCHEMA = "sc-lab-governance-approval-request/0.39.0"
APPROVAL_DECISION_SCHEMA = "sc-lab-governance-approval-decision/0.39.0"
EVENT_SCHEMA = "sc-lab-institutional-governance-event/0.39.0"

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,179}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PRINCIPAL_TYPES = {"human", "service"}
PRINCIPAL_STATUSES = {"active", "suspended", "disabled"}
INSTITUTION_STATUSES = {"active", "suspended", "archived"}
CLASSIFICATIONS = {"public": 10, "internal": 30, "confidential": 60, "restricted": 90}
INSTITUTION_ROLES = {
    "institution-viewer": 10,
    "researcher": 30,
    "steward": 50,
    "approver": 70,
    "auditor": 75,
    "institution-admin": 90,
    "institution-owner": 100,
}
APPROVAL_STATUSES = {"pending", "approved", "rejected", "changes-requested", "cancelled"}
APPROVAL_DECISIONS = {"approve", "reject", "request-changes"}
RESOURCE_TYPES = {
    "dataset", "workflow", "experiment", "model", "artifact", "publication",
    "reproducibility-package", "research-handoff", "decision-packet", "evidence-record",
}
ACTIONS = {
    "research.read", "research.create", "research.update", "research.export",
    "research.publish", "research.share", "research.delete-reference", "governance.approve",
    "governance.audit", "governance.administer",
}
ROLE_CAPABILITIES = {
    "institution-viewer": {"research.read"},
    "researcher": {"research.read", "research.create", "research.update"},
    "steward": {"research.read", "research.create", "research.update", "research.export", "research.share"},
    "approver": {"research.read", "research.export", "research.publish", "research.share", "governance.approve"},
    "auditor": {"research.read", "governance.audit"},
    "institution-admin": set(ACTIONS) - {"research.delete-reference"},
    "institution-owner": set(ACTIONS),
}


class InstitutionalGovernanceError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _id(value: Any, label: str = "identifier") -> str:
    clean = str(value or "").strip()
    if not ID_RE.fullmatch(clean):
        raise InstitutionalGovernanceError(f"A valid {label} is required.")
    return clean


def _text(value: Any, limit: int = 500) -> str:
    return str(value or "").strip()[:limit]


def _json(value: Any, label: str = "metadata") -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise InstitutionalGovernanceError(f"{label.capitalize()} must be an object.")
    encoded = _stable(value)
    if len(encoded.encode("utf-8")) > 262144:
        raise InstitutionalGovernanceError(f"{label.capitalize()} exceeds the 256 KiB limit.", 413)
    return json.loads(encoded)


def policies(persistent: bool = False) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-institutional-governance-policy/0.39.0",
        "institutionRoles": [
            {"id": role, "rank": rank, "capabilities": sorted(ROLE_CAPABILITIES[role])}
            for role, rank in INSTITUTION_ROLES.items()
        ],
        "principalTypes": sorted(PRINCIPAL_TYPES),
        "classifications": [{"id": key, "rank": rank} for key, rank in CLASSIFICATIONS.items()],
        "resourceTypes": sorted(RESOURCE_TYPES),
        "actions": sorted(ACTIONS),
        "approvalDecisions": sorted(APPROVAL_DECISIONS),
        "capabilities": {
            "institutions": True,
            "organizationalUnits": True,
            "humanPrincipals": True,
            "credentialFreeServicePrincipals": True,
            "institutionRoleBindings": True,
            "workspaceGovernanceProfiles": True,
            "classificationPolicy": True,
            "retentionPolicy": True,
            "approvalWorkflow": True,
            "policyEvaluation": True,
            "immutableGovernanceTimeline": True,
            "singleSignOn": False,
            "secretStorage": False,
            "automaticDestructiveDeletion": False,
        },
        "durability": "persistent-disk" if persistent else "instance-local",
    }


class InstitutionalGovernanceManager:
    def __init__(
        self,
        db_path: str,
        workspaces: Any,
        persistent_disk_mounted: bool = False,
        max_institutions: int = 1000,
        max_principals: int = 250000,
        history_limit: int = 250000,
    ):
        self.db_path = str(db_path)
        self.workspaces = workspaces
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_institutions = max(1, int(max_institutions))
        self.max_principals = max(100, int(max_principals))
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
                CREATE TABLE IF NOT EXISTS institutions(
                  id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, status TEXT NOT NULL,
                  domains_json TEXT NOT NULL, settings_json TEXT NOT NULL, institution_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS organizational_units(
                  id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, parent_id TEXT, title TEXT NOT NULL,
                  code TEXT, status TEXT NOT NULL, metadata_json TEXT NOT NULL, unit_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  FOREIGN KEY(institution_id) REFERENCES institutions(id),
                  FOREIGN KEY(parent_id) REFERENCES organizational_units(id)
                );
                CREATE TABLE IF NOT EXISTS principals(
                  id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, principal_type TEXT NOT NULL,
                  display_name TEXT NOT NULL, email TEXT, external_subject TEXT, status TEXT NOT NULL,
                  metadata_json TEXT NOT NULL, principal_hash TEXT NOT NULL, created_by TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  UNIQUE(institution_id, external_subject),
                  FOREIGN KEY(institution_id) REFERENCES institutions(id)
                );
                CREATE TABLE IF NOT EXISTS role_bindings(
                  id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, principal_id TEXT NOT NULL,
                  role TEXT NOT NULL, unit_id TEXT, workspace_id TEXT, status TEXT NOT NULL,
                  granted_by TEXT NOT NULL, rationale TEXT, created_at TEXT NOT NULL, revoked_at TEXT,
                  FOREIGN KEY(institution_id) REFERENCES institutions(id),
                  FOREIGN KEY(principal_id) REFERENCES principals(id),
                  FOREIGN KEY(unit_id) REFERENCES organizational_units(id)
                );
                CREATE TABLE IF NOT EXISTS retention_policies(
                  id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, title TEXT NOT NULL,
                  retention_days INTEGER NOT NULL, review_interval_days INTEGER NOT NULL,
                  disposition TEXT NOT NULL, legal_hold INTEGER NOT NULL,
                  metadata_json TEXT NOT NULL, policy_hash TEXT NOT NULL,
                  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  FOREIGN KEY(institution_id) REFERENCES institutions(id)
                );
                CREATE TABLE IF NOT EXISTS workspace_governance(
                  workspace_id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, unit_id TEXT,
                  classification TEXT NOT NULL, retention_policy_id TEXT,
                  approval_actions_json TEXT NOT NULL, approval_quorum INTEGER NOT NULL,
                  external_sharing INTEGER NOT NULL, status TEXT NOT NULL,
                  metadata_json TEXT NOT NULL, governance_hash TEXT NOT NULL,
                  configured_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  FOREIGN KEY(institution_id) REFERENCES institutions(id),
                  FOREIGN KEY(unit_id) REFERENCES organizational_units(id),
                  FOREIGN KEY(retention_policy_id) REFERENCES retention_policies(id)
                );
                CREATE TABLE IF NOT EXISTS approval_requests(
                  id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, institution_id TEXT NOT NULL,
                  request_type TEXT NOT NULL, action TEXT NOT NULL, resource_type TEXT NOT NULL,
                  resource_id TEXT NOT NULL, resource_classification TEXT NOT NULL,
                  status TEXT NOT NULL, required_decisions INTEGER NOT NULL,
                  request_json TEXT NOT NULL, request_hash TEXT NOT NULL,
                  requested_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  resolved_at TEXT, FOREIGN KEY(institution_id) REFERENCES institutions(id)
                );
                CREATE TABLE IF NOT EXISTS approval_decisions(
                  id TEXT PRIMARY KEY, request_id TEXT NOT NULL, actor_id TEXT NOT NULL,
                  decision TEXT NOT NULL, rationale TEXT, decision_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL, UNIQUE(request_id, actor_id),
                  FOREIGN KEY(request_id) REFERENCES approval_requests(id)
                );
                CREATE TABLE IF NOT EXISTS governance_events(
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, institution_id TEXT NOT NULL,
                  workspace_id TEXT, event_type TEXT NOT NULL, actor_id TEXT NOT NULL,
                  details_json TEXT NOT NULL, previous_hash TEXT, event_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL, FOREIGN KEY(institution_id) REFERENCES institutions(id)
                );
                CREATE INDEX IF NOT EXISTS idx_units_institution ON organizational_units(institution_id,status);
                CREATE INDEX IF NOT EXISTS idx_principals_institution ON principals(institution_id,status);
                CREATE INDEX IF NOT EXISTS idx_bindings_principal ON role_bindings(institution_id,principal_id,status);
                CREATE INDEX IF NOT EXISTS idx_bindings_workspace ON role_bindings(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_approvals_workspace ON approval_requests(workspace_id,status);
                CREATE INDEX IF NOT EXISTS idx_events_institution ON governance_events(institution_id,sequence);
                """
            )
            con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version','1')")

    def _event(self, con: sqlite3.Connection, institution_id: str, workspace_id: str | None, event_type: str, actor_id: str, details: dict[str, Any]) -> None:
        previous = con.execute(
            "SELECT event_hash FROM governance_events WHERE institution_id=? ORDER BY sequence DESC LIMIT 1",
            (institution_id,),
        ).fetchone()
        created_at = _now()
        previous_hash = previous["event_hash"] if previous else None
        event_hash = _hash({"institutionId": institution_id, "workspaceId": workspace_id, "eventType": event_type, "actorId": actor_id, "details": details, "previousHash": previous_hash, "createdAt": created_at})
        con.execute(
            "INSERT INTO governance_events(institution_id,workspace_id,event_type,actor_id,details_json,previous_hash,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (institution_id, workspace_id, event_type, actor_id, _stable(details), previous_hash, event_hash, created_at),
        )
        count = con.execute("SELECT COUNT(*) AS count FROM governance_events").fetchone()["count"]
        if count > self.history_limit:
            con.execute("DELETE FROM governance_events WHERE sequence IN (SELECT sequence FROM governance_events ORDER BY sequence ASC LIMIT ?)", (count - self.history_limit,))

    def _institution(self, con: sqlite3.Connection, institution_id: str) -> sqlite3.Row:
        row = con.execute("SELECT * FROM institutions WHERE id=?", (_id(institution_id, "institution identifier"),)).fetchone()
        if not row:
            raise InstitutionalGovernanceError("Institution not found.", 404)
        return row

    def _principal_for_actor(self, con: sqlite3.Connection, institution_id: str, actor_id: str) -> sqlite3.Row | None:
        return con.execute(
            "SELECT * FROM principals WHERE institution_id=? AND id=? AND status='active'",
            (institution_id, actor_id),
        ).fetchone()

    def _actor_roles(self, con: sqlite3.Connection, institution_id: str, actor_id: str, workspace_id: str = "", unit_id: str = "") -> list[str]:
        principal = self._principal_for_actor(con, institution_id, actor_id)
        principal_id = principal["id"] if principal else actor_id
        rows = con.execute(
            "SELECT role,workspace_id,unit_id FROM role_bindings WHERE institution_id=? AND principal_id=? AND status='active'",
            (institution_id, principal_id),
        ).fetchall()
        roles = []
        for row in rows:
            if row["workspace_id"] and row["workspace_id"] != workspace_id:
                continue
            if row["unit_id"] and row["unit_id"] != unit_id:
                continue
            roles.append(row["role"])
        return sorted(set(roles), key=lambda role: INSTITUTION_ROLES[role])

    def _require_institution(self, con: sqlite3.Connection, institution_id: str, actor_id: str, minimum: str = "institution-viewer", workspace_id: str = "", unit_id: str = "") -> tuple[sqlite3.Row, list[str]]:
        institution = self._institution(con, institution_id)
        roles = self._actor_roles(con, institution_id, actor_id, workspace_id, unit_id)
        if not roles or max(INSTITUTION_ROLES[role] for role in roles) < INSTITUTION_ROLES[minimum]:
            raise InstitutionalGovernanceError(f"The {minimum} institutional role or higher is required.", 403)
        return institution, roles

    def _require_workspace(self, workspace_id: str, actor_id: str, minimum: str = "viewer") -> None:
        try:
            with self.workspaces._connect() as con:
                self.workspaces._require(con, workspace_id, actor_id, minimum, allow_archived=True)
        except Exception as exc:
            status = getattr(exc, "status_code", 403)
            detail = getattr(exc, "detail", str(exc))
            raise InstitutionalGovernanceError(detail, status) from exc

    @staticmethod
    def _institution_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": INSTITUTION_SCHEMA, "version": VERSION, "id": row["id"], "name": row["name"], "description": row["description"], "status": row["status"], "domains": json.loads(row["domains_json"]), "settings": json.loads(row["settings_json"]), "institutionHash": row["institution_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]}

    @staticmethod
    def _unit_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": UNIT_SCHEMA, "version": VERSION, "id": row["id"], "institutionId": row["institution_id"], "parentId": row["parent_id"], "title": row["title"], "code": row["code"], "status": row["status"], "metadata": json.loads(row["metadata_json"]), "unitHash": row["unit_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]}

    @staticmethod
    def _principal_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": PRINCIPAL_SCHEMA, "version": VERSION, "id": row["id"], "institutionId": row["institution_id"], "principalType": row["principal_type"], "displayName": row["display_name"], "email": row["email"], "externalSubject": row["external_subject"], "status": row["status"], "metadata": json.loads(row["metadata_json"]), "principalHash": row["principal_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "credentialsStored": False}

    @staticmethod
    def _binding_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": BINDING_SCHEMA, "version": VERSION, "id": row["id"], "institutionId": row["institution_id"], "principalId": row["principal_id"], "role": row["role"], "unitId": row["unit_id"], "workspaceId": row["workspace_id"], "status": row["status"], "grantedBy": row["granted_by"], "rationale": row["rationale"], "createdAt": row["created_at"], "revokedAt": row["revoked_at"]}

    @staticmethod
    def _retention_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": RETENTION_SCHEMA, "version": VERSION, "id": row["id"], "institutionId": row["institution_id"], "title": row["title"], "retentionDays": row["retention_days"], "reviewIntervalDays": row["review_interval_days"], "disposition": row["disposition"], "legalHold": bool(row["legal_hold"]), "metadata": json.loads(row["metadata_json"]), "policyHash": row["policy_hash"], "createdBy": row["created_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]}

    @staticmethod
    def _workspace_governance_record(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": WORKSPACE_GOVERNANCE_SCHEMA, "version": VERSION, "workspaceId": row["workspace_id"], "institutionId": row["institution_id"], "unitId": row["unit_id"], "classification": row["classification"], "retentionPolicyId": row["retention_policy_id"], "approvalActions": json.loads(row["approval_actions_json"]), "approvalQuorum": row["approval_quorum"], "externalSharing": bool(row["external_sharing"]), "status": row["status"], "metadata": json.loads(row["metadata_json"]), "governanceHash": row["governance_hash"], "configuredBy": row["configured_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]}

    @staticmethod
    def _approval_request_record(con: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
        decisions = con.execute("SELECT * FROM approval_decisions WHERE request_id=? ORDER BY created_at", (row["id"],)).fetchall()
        return {"schema": APPROVAL_REQUEST_SCHEMA, "version": VERSION, "id": row["id"], "workspaceId": row["workspace_id"], "institutionId": row["institution_id"], "requestType": row["request_type"], "action": row["action"], "resourceType": row["resource_type"], "resourceId": row["resource_id"], "resourceClassification": row["resource_classification"], "status": row["status"], "requiredDecisions": row["required_decisions"], "request": json.loads(row["request_json"]), "requestHash": row["request_hash"], "requestedBy": row["requested_by"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "resolvedAt": row["resolved_at"], "decisions": [{"schema": APPROVAL_DECISION_SCHEMA, "version": VERSION, "id": d["id"], "requestId": d["request_id"], "actorId": d["actor_id"], "decision": d["decision"], "rationale": d["rationale"], "decisionHash": d["decision_hash"], "createdAt": d["created_at"]} for d in decisions]}

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            counts = {
                "institutions": con.execute("SELECT COUNT(*) AS count FROM institutions").fetchone()["count"],
                "principals": con.execute("SELECT COUNT(*) AS count FROM principals").fetchone()["count"],
                "roleBindings": con.execute("SELECT COUNT(*) AS count FROM role_bindings WHERE status='active'").fetchone()["count"],
                "governedWorkspaces": con.execute("SELECT COUNT(*) AS count FROM workspace_governance WHERE status='active'").fetchone()["count"],
                "pendingApprovals": con.execute("SELECT COUNT(*) AS count FROM approval_requests WHERE status='pending'").fetchone()["count"],
            }
        return {"ok": True, "status": "ready", "version": VERSION, "schema": "sc-lab-institutional-governance-health/0.39.0", "counts": counts, "policy": policies(self.persistent_disk_mounted)}

    def create_institution(self, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        institution_id = _id(payload.get("id"), "institution identifier")
        name = _text(payload.get("name"), 200)
        if not name:
            raise InstitutionalGovernanceError("Institution name is required.")
        domains = sorted({_text(item, 253).lower() for item in payload.get("domains", []) if _text(item, 253)})
        settings = _json(payload.get("settings"), "settings")
        now = _now()
        body = {"id": institution_id, "name": name, "description": _text(payload.get("description"), 2000), "status": "active", "domains": domains, "settings": settings}
        with self._connect() as con:
            if con.execute("SELECT COUNT(*) AS count FROM institutions").fetchone()["count"] >= self.max_institutions:
                raise InstitutionalGovernanceError("Institution limit reached.", 409)
            if con.execute("SELECT 1 FROM institutions WHERE id=?", (institution_id,)).fetchone():
                raise InstitutionalGovernanceError("Institution already exists.", 409)
            con.execute("INSERT INTO institutions VALUES(?,?,?,?,?,?,?,?,?,?)", (institution_id, name, body["description"], "active", _stable(domains), _stable(settings), _hash(body), actor_id, now, now))
            principal_body = {"id": actor_id, "institutionId": institution_id, "principalType": "human", "displayName": actor_id, "email": None, "externalSubject": actor_id, "status": "active", "metadata": {"bootstrapOwner": True}}
            con.execute("INSERT INTO principals VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (actor_id, institution_id, "human", actor_id, None, actor_id, "active", _stable(principal_body["metadata"]), _hash(principal_body), actor_id, now, now))
            binding_id = f"binding:{institution_id}:{actor_id}:owner"
            con.execute("INSERT INTO role_bindings VALUES(?,?,?,?,?,?,?,?,?,?,?)", (binding_id, institution_id, actor_id, "institution-owner", None, None, "active", actor_id, "Institution creator", now, None))
            self._event(con, institution_id, None, "institution.created", actor_id, {"institutionId": institution_id, "ownerPrincipalId": actor_id})
            row = con.execute("SELECT * FROM institutions WHERE id=?", (institution_id,)).fetchone()
        return {"ok": True, "institution": self._institution_record(row)}

    def list_institutions(self, actor_id: str) -> dict[str, Any]:
        with self._connect() as con:
            rows = con.execute("SELECT DISTINCT i.* FROM institutions i JOIN role_bindings b ON b.institution_id=i.id WHERE b.principal_id=? AND b.status='active' ORDER BY i.name", (actor_id,)).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "institutions": [self._institution_record(row) for row in rows]}

    def get_institution(self, institution_id: str, actor_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row, roles = self._require_institution(con, institution_id, actor_id)
            record = self._institution_record(row)
            record["currentRoles"] = roles
        return {"ok": True, "institution": record}

    def create_unit(self, institution_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        unit_id = _id(payload.get("id"), "organizational unit identifier")
        title = _text(payload.get("title"), 200)
        if not title:
            raise InstitutionalGovernanceError("Organizational unit title is required.")
        parent_id = _id(payload.get("parentId"), "parent unit identifier") if payload.get("parentId") else None
        metadata = _json(payload.get("metadata"))
        now = _now()
        body = {"id": unit_id, "institutionId": institution_id, "parentId": parent_id, "title": title, "code": _text(payload.get("code"), 80) or None, "status": "active", "metadata": metadata}
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id, "institution-admin")
            if parent_id and not con.execute("SELECT 1 FROM organizational_units WHERE id=? AND institution_id=?", (parent_id, institution_id)).fetchone():
                raise InstitutionalGovernanceError("Parent organizational unit not found.", 404)
            if con.execute("SELECT 1 FROM organizational_units WHERE id=?", (unit_id,)).fetchone():
                raise InstitutionalGovernanceError("Organizational unit already exists.", 409)
            con.execute("INSERT INTO organizational_units VALUES(?,?,?,?,?,?,?,?,?,?,?)", (unit_id, institution_id, parent_id, title, body["code"], "active", _stable(metadata), _hash(body), actor_id, now, now))
            self._event(con, institution_id, None, "organizational-unit.created", actor_id, {"unitId": unit_id, "parentId": parent_id})
            row = con.execute("SELECT * FROM organizational_units WHERE id=?", (unit_id,)).fetchone()
        return {"ok": True, "unit": self._unit_record(row)}

    def list_units(self, institution_id: str, actor_id: str) -> dict[str, Any]:
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id)
            rows = con.execute("SELECT * FROM organizational_units WHERE institution_id=? ORDER BY title", (institution_id,)).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "units": [self._unit_record(row) for row in rows]}

    def register_principal(self, institution_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        principal_id = _id(payload.get("id"), "principal identifier")
        principal_type = _text(payload.get("principalType") or "human", 20).lower()
        if principal_type not in PRINCIPAL_TYPES:
            raise InstitutionalGovernanceError("Unsupported principal type.")
        display_name = _text(payload.get("displayName"), 200)
        if not display_name:
            raise InstitutionalGovernanceError("Principal display name is required.")
        email = _text(payload.get("email"), 320).lower() or None
        if email and not EMAIL_RE.fullmatch(email):
            raise InstitutionalGovernanceError("A valid principal email address is required.")
        external_subject = _text(payload.get("externalSubject"), 500) or None
        metadata = _json(payload.get("metadata"))
        now = _now()
        body = {"id": principal_id, "institutionId": institution_id, "principalType": principal_type, "displayName": display_name, "email": email, "externalSubject": external_subject, "status": "active", "metadata": metadata}
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id, "institution-admin")
            if con.execute("SELECT COUNT(*) AS count FROM principals").fetchone()["count"] >= self.max_principals:
                raise InstitutionalGovernanceError("Principal limit reached.", 409)
            if con.execute("SELECT 1 FROM principals WHERE id=?", (principal_id,)).fetchone():
                raise InstitutionalGovernanceError("Principal already exists.", 409)
            con.execute("INSERT INTO principals VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (principal_id, institution_id, principal_type, display_name, email, external_subject, "active", _stable(metadata), _hash(body), actor_id, now, now))
            self._event(con, institution_id, None, "principal.registered", actor_id, {"principalId": principal_id, "principalType": principal_type})
            row = con.execute("SELECT * FROM principals WHERE id=?", (principal_id,)).fetchone()
        return {"ok": True, "principal": self._principal_record(row)}

    def list_principals(self, institution_id: str, actor_id: str, status: str = "") -> dict[str, Any]:
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id)
            params: list[Any] = [institution_id]
            query = "SELECT * FROM principals WHERE institution_id=?"
            if status:
                query += " AND status=?"; params.append(status)
            rows = con.execute(query + " ORDER BY display_name", params).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "principals": [self._principal_record(row) for row in rows]}

    def grant_role(self, institution_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        principal_id = _id(payload.get("principalId"), "principal identifier")
        role = _text(payload.get("role"), 40).lower()
        if role not in INSTITUTION_ROLES:
            raise InstitutionalGovernanceError("Unsupported institutional role.")
        unit_id = _id(payload.get("unitId"), "organizational unit identifier") if payload.get("unitId") else None
        workspace_id = _id(payload.get("workspaceId"), "workspace identifier") if payload.get("workspaceId") else None
        now = _now()
        binding_id = _id(payload.get("id") or f"binding:{institution_id}:{principal_id}:{role}:{_hash([unit_id, workspace_id])[:10]}", "role binding identifier")
        with self._connect() as con:
            _, actor_roles = self._require_institution(con, institution_id, actor_id, "institution-admin")
            if role == "institution-owner" and "institution-owner" not in actor_roles:
                raise InstitutionalGovernanceError("Only an institution owner may grant the institution-owner role.", 403)
            if not con.execute("SELECT 1 FROM principals WHERE id=? AND institution_id=?", (principal_id, institution_id)).fetchone():
                raise InstitutionalGovernanceError("Principal not found.", 404)
            if unit_id and not con.execute("SELECT 1 FROM organizational_units WHERE id=? AND institution_id=?", (unit_id, institution_id)).fetchone():
                raise InstitutionalGovernanceError("Organizational unit not found.", 404)
            if workspace_id:
                self._require_workspace(workspace_id, actor_id, "administrator")
            con.execute("INSERT INTO role_bindings VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status='active',revoked_at=NULL,rationale=excluded.rationale", (binding_id, institution_id, principal_id, role, unit_id, workspace_id, "active", actor_id, _text(payload.get("rationale"), 1000) or None, now, None))
            self._event(con, institution_id, workspace_id, "role-binding.granted", actor_id, {"bindingId": binding_id, "principalId": principal_id, "role": role, "unitId": unit_id})
            row = con.execute("SELECT * FROM role_bindings WHERE id=?", (binding_id,)).fetchone()
        return {"ok": True, "binding": self._binding_record(row)}

    def revoke_role(self, institution_id: str, binding_id: str, actor_id: str) -> dict[str, Any]:
        now = _now()
        with self._connect() as con:
            _, actor_roles = self._require_institution(con, institution_id, actor_id, "institution-admin")
            row = con.execute("SELECT * FROM role_bindings WHERE id=? AND institution_id=?", (_id(binding_id, "role binding identifier"), institution_id)).fetchone()
            if not row:
                raise InstitutionalGovernanceError("Role binding not found.", 404)
            if row["role"] == "institution-owner" and "institution-owner" not in actor_roles:
                raise InstitutionalGovernanceError("Only an institution owner may revoke an owner binding.", 403)
            active_owners = con.execute("SELECT COUNT(*) AS count FROM role_bindings WHERE institution_id=? AND role='institution-owner' AND status='active'", (institution_id,)).fetchone()["count"]
            if row["role"] == "institution-owner" and active_owners <= 1:
                raise InstitutionalGovernanceError("The final institution owner binding cannot be revoked.", 409)
            con.execute("UPDATE role_bindings SET status='revoked',revoked_at=? WHERE id=?", (now, row["id"]))
            self._event(con, institution_id, row["workspace_id"], "role-binding.revoked", actor_id, {"bindingId": row["id"], "principalId": row["principal_id"], "role": row["role"]})
            updated = con.execute("SELECT * FROM role_bindings WHERE id=?", (row["id"],)).fetchone()
        return {"ok": True, "binding": self._binding_record(updated)}

    def list_bindings(self, institution_id: str, actor_id: str, principal_id: str = "", workspace_id: str = "") -> dict[str, Any]:
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id)
            query = "SELECT * FROM role_bindings WHERE institution_id=?"; params: list[Any] = [institution_id]
            if principal_id: query += " AND principal_id=?"; params.append(principal_id)
            if workspace_id: query += " AND workspace_id=?"; params.append(workspace_id)
            rows = con.execute(query + " ORDER BY created_at DESC", params).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "bindings": [self._binding_record(row) for row in rows]}

    def create_retention_policy(self, institution_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        policy_id = _id(payload.get("id"), "retention policy identifier")
        title = _text(payload.get("title"), 200)
        if not title:
            raise InstitutionalGovernanceError("Retention policy title is required.")
        retention_days = max(1, min(int(payload.get("retentionDays", 3650)), 36500))
        review_days = max(1, min(int(payload.get("reviewIntervalDays", 365)), retention_days))
        disposition = _text(payload.get("disposition") or "review", 40).lower()
        if disposition not in {"retain", "archive", "review", "delete-reference"}:
            raise InstitutionalGovernanceError("Unsupported retention disposition.")
        metadata = _json(payload.get("metadata"))
        now = _now()
        body = {"id": policy_id, "institutionId": institution_id, "title": title, "retentionDays": retention_days, "reviewIntervalDays": review_days, "disposition": disposition, "legalHold": bool(payload.get("legalHold", False)), "metadata": metadata}
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id, "steward")
            con.execute("INSERT INTO retention_policies VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (policy_id, institution_id, title, retention_days, review_days, disposition, int(body["legalHold"]), _stable(metadata), _hash(body), actor_id, now, now))
            self._event(con, institution_id, None, "retention-policy.created", actor_id, {"policyId": policy_id, "disposition": disposition, "legalHold": body["legalHold"]})
            row = con.execute("SELECT * FROM retention_policies WHERE id=?", (policy_id,)).fetchone()
        return {"ok": True, "retentionPolicy": self._retention_record(row)}

    def list_retention_policies(self, institution_id: str, actor_id: str) -> dict[str, Any]:
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id)
            rows = con.execute("SELECT * FROM retention_policies WHERE institution_id=? ORDER BY title", (institution_id,)).fetchall()
        return {"ok": True, "version": VERSION, "count": len(rows), "retentionPolicies": [self._retention_record(row) for row in rows]}

    def govern_workspace(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        institution_id = _id(payload.get("institutionId"), "institution identifier")
        unit_id = _id(payload.get("unitId"), "organizational unit identifier") if payload.get("unitId") else None
        classification = _text(payload.get("classification") or "internal", 40).lower()
        if classification not in CLASSIFICATIONS:
            raise InstitutionalGovernanceError("Unsupported workspace classification.")
        retention_policy_id = _id(payload.get("retentionPolicyId"), "retention policy identifier") if payload.get("retentionPolicyId") else None
        approval_actions = sorted(set(payload.get("approvalActions") or ["research.publish", "research.share"]))
        if any(action not in ACTIONS for action in approval_actions):
            raise InstitutionalGovernanceError("Unsupported approval action.")
        approval_quorum = max(1, min(int(payload.get("approvalQuorum", 1)), 20))
        metadata = _json(payload.get("metadata"))
        now = _now()
        body = {"workspaceId": workspace_id, "institutionId": institution_id, "unitId": unit_id, "classification": classification, "retentionPolicyId": retention_policy_id, "approvalActions": approval_actions, "approvalQuorum": approval_quorum, "externalSharing": bool(payload.get("externalSharing", classification in {"public", "internal"})), "status": "active", "metadata": metadata}
        self._require_workspace(workspace_id, actor_id, "administrator")
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id, "institution-admin", workspace_id, unit_id or "")
            if unit_id and not con.execute("SELECT 1 FROM organizational_units WHERE id=? AND institution_id=?", (unit_id, institution_id)).fetchone():
                raise InstitutionalGovernanceError("Organizational unit not found.", 404)
            if retention_policy_id and not con.execute("SELECT 1 FROM retention_policies WHERE id=? AND institution_id=?", (retention_policy_id, institution_id)).fetchone():
                raise InstitutionalGovernanceError("Retention policy not found.", 404)
            existing = con.execute("SELECT created_at FROM workspace_governance WHERE workspace_id=?", (workspace_id,)).fetchone()
            created_at = existing["created_at"] if existing else now
            con.execute("""INSERT INTO workspace_governance VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(workspace_id) DO UPDATE SET institution_id=excluded.institution_id,unit_id=excluded.unit_id,classification=excluded.classification,retention_policy_id=excluded.retention_policy_id,approval_actions_json=excluded.approval_actions_json,approval_quorum=excluded.approval_quorum,external_sharing=excluded.external_sharing,status='active',metadata_json=excluded.metadata_json,governance_hash=excluded.governance_hash,configured_by=excluded.configured_by,updated_at=excluded.updated_at""",
                (workspace_id, institution_id, unit_id, classification, retention_policy_id, _stable(approval_actions), approval_quorum, int(body["externalSharing"]), "active", _stable(metadata), _hash(body), actor_id, created_at, now))
            self._event(con, institution_id, workspace_id, "workspace-governance.configured", actor_id, {"classification": classification, "retentionPolicyId": retention_policy_id, "approvalActions": approval_actions, "approvalQuorum": approval_quorum})
            row = con.execute("SELECT * FROM workspace_governance WHERE workspace_id=?", (workspace_id,)).fetchone()
        return {"ok": True, "workspaceGovernance": self._workspace_governance_record(row)}

    def get_workspace_governance(self, workspace_id: str, actor_id: str) -> dict[str, Any]:
        self._require_workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            row = con.execute("SELECT * FROM workspace_governance WHERE workspace_id=?", (workspace_id,)).fetchone()
            if not row:
                raise InstitutionalGovernanceError("Workspace governance is not configured.", 404)
            self._require_institution(con, row["institution_id"], actor_id, "institution-viewer", workspace_id, row["unit_id"] or "")
        return {"ok": True, "workspaceGovernance": self._workspace_governance_record(row)}

    def evaluate(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        action = _text(payload.get("action"), 80)
        if action not in ACTIONS:
            raise InstitutionalGovernanceError("Unsupported governance action.")
        resource_type = _text(payload.get("resourceType") or "dataset", 80)
        if resource_type not in RESOURCE_TYPES:
            raise InstitutionalGovernanceError("Unsupported resource type.")
        requested_classification = _text(payload.get("classification") or "", 40).lower()
        self._require_workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            governance = con.execute("SELECT * FROM workspace_governance WHERE workspace_id=? AND status='active'", (workspace_id,)).fetchone()
            if not governance:
                decision = {"workspaceId": workspace_id, "actorId": actor_id, "action": action, "resourceType": resource_type, "resourceId": _text(payload.get("resourceId"), 180), "allowed": False, "requiresApproval": False, "reasons": ["Workspace governance is not configured."], "institutionRoles": [], "effectiveClassification": requested_classification or "internal", "evaluatedAt": _now()}
                decision["decisionHash"] = _hash(decision)
                return {"ok": True, "decision": {"schema": DECISION_SCHEMA, "version": VERSION, **decision}}
            roles = self._actor_roles(con, governance["institution_id"], actor_id, workspace_id, governance["unit_id"] or "")
            capabilities = set().union(*(ROLE_CAPABILITIES[role] for role in roles)) if roles else set()
            effective_classification = requested_classification or governance["classification"]
            reasons: list[str] = []
            allowed = action in capabilities
            if not roles: reasons.append("No applicable institutional role binding was found.")
            if action not in capabilities: reasons.append(f"Institutional role bindings do not grant {action}.")
            if action == "research.share" and not governance["external_sharing"]: allowed = False; reasons.append("External sharing is disabled for this workspace.")
            if CLASSIFICATIONS[effective_classification] >= CLASSIFICATIONS["restricted"] and action in {"research.share", "research.export"} and "institution-owner" not in roles:
                allowed = False; reasons.append("Restricted research export or sharing requires an institution owner.")
            approval_actions = set(json.loads(governance["approval_actions_json"]))
            requires_approval = allowed and action in approval_actions and "approver" not in roles and "institution-admin" not in roles and "institution-owner" not in roles
            if requires_approval: reasons.append("The workspace governance profile requires approval for this action.")
            if allowed and not reasons: reasons.append("Applicable role and workspace policies permit the action.")
            decision = {"workspaceId": workspace_id, "institutionId": governance["institution_id"], "actorId": actor_id, "action": action, "resourceType": resource_type, "resourceId": _text(payload.get("resourceId"), 180), "allowed": allowed, "requiresApproval": requires_approval, "reasons": reasons, "institutionRoles": roles, "effectiveClassification": effective_classification, "approvalQuorum": governance["approval_quorum"] if requires_approval else 0, "evaluatedAt": _now()}
            decision["decisionHash"] = _hash(decision)
            self._event(con, governance["institution_id"], workspace_id, "policy.evaluated", actor_id, {"action": action, "resourceType": resource_type, "allowed": allowed, "requiresApproval": requires_approval, "decisionHash": decision["decisionHash"]})
        return {"ok": True, "decision": {"schema": DECISION_SCHEMA, "version": VERSION, **decision}}

    def create_approval(self, workspace_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        evaluation = self.evaluate(workspace_id, payload, actor_id)["decision"]
        if not evaluation["allowed"]:
            raise InstitutionalGovernanceError("The requested action is not permitted by policy.", 403)
        request_id = _id(payload.get("id") or f"approval:{_hash([workspace_id, actor_id, payload, _now()])[:24]}", "approval request identifier")
        request_type = _text(payload.get("requestType") or "research-action", 80)
        resource_id = _id(payload.get("resourceId"), "resource identifier")
        request_payload = _json(payload.get("request"), "approval request")
        now = _now()
        with self._connect() as con:
            governance = con.execute("SELECT * FROM workspace_governance WHERE workspace_id=?", (workspace_id,)).fetchone()
            if not governance:
                raise InstitutionalGovernanceError("Workspace governance is not configured.", 409)
            body = {"id": request_id, "workspaceId": workspace_id, "institutionId": governance["institution_id"], "requestType": request_type, "action": evaluation["action"], "resourceType": evaluation["resourceType"], "resourceId": resource_id, "resourceClassification": evaluation["effectiveClassification"], "request": request_payload, "requestedBy": actor_id}
            con.execute("INSERT INTO approval_requests VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (request_id, workspace_id, governance["institution_id"], request_type, evaluation["action"], evaluation["resourceType"], resource_id, evaluation["effectiveClassification"], "pending", max(1, int(governance["approval_quorum"])), _stable(request_payload), _hash(body), actor_id, now, now, None))
            self._event(con, governance["institution_id"], workspace_id, "approval.requested", actor_id, {"requestId": request_id, "action": evaluation["action"], "resourceType": evaluation["resourceType"], "resourceId": resource_id})
            row = con.execute("SELECT * FROM approval_requests WHERE id=?", (request_id,)).fetchone()
            record = self._approval_request_record(con, row)
        return {"ok": True, "approvalRequest": record}

    def list_approvals(self, workspace_id: str, actor_id: str, status: str = "") -> dict[str, Any]:
        self._require_workspace(workspace_id, actor_id, "viewer")
        with self._connect() as con:
            governance = con.execute("SELECT * FROM workspace_governance WHERE workspace_id=?", (workspace_id,)).fetchone()
            if not governance:
                raise InstitutionalGovernanceError("Workspace governance is not configured.", 404)
            self._require_institution(con, governance["institution_id"], actor_id, "institution-viewer", workspace_id, governance["unit_id"] or "")
            query = "SELECT * FROM approval_requests WHERE workspace_id=?"; params: list[Any] = [workspace_id]
            if status: query += " AND status=?"; params.append(status)
            rows = con.execute(query + " ORDER BY created_at DESC", params).fetchall()
            records = [self._approval_request_record(con, row) for row in rows]
        return {"ok": True, "version": VERSION, "count": len(records), "approvalRequests": records}

    def decide_approval(self, workspace_id: str, request_id: str, payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
        decision = _text(payload.get("decision"), 40).lower()
        if decision not in APPROVAL_DECISIONS:
            raise InstitutionalGovernanceError("Unsupported approval decision.")
        now = _now()
        self._require_workspace(workspace_id, actor_id, "reviewer")
        with self._connect() as con:
            row = con.execute("SELECT * FROM approval_requests WHERE id=? AND workspace_id=?", (_id(request_id, "approval request identifier"), workspace_id)).fetchone()
            if not row:
                raise InstitutionalGovernanceError("Approval request not found.", 404)
            if row["status"] not in {"pending", "changes-requested"}:
                raise InstitutionalGovernanceError("The approval request is already resolved.", 409)
            governance = con.execute("SELECT unit_id FROM workspace_governance WHERE workspace_id=?", (workspace_id,)).fetchone()
            _, roles = self._require_institution(con, row["institution_id"], actor_id, "approver", workspace_id, (governance["unit_id"] if governance else "") or "")
            if not any(role in {"approver", "institution-admin", "institution-owner"} for role in roles):
                raise InstitutionalGovernanceError("An approver, institution administrator, or owner role is required.", 403)
            decision_id = f"decision:{row['id']}:{actor_id}"
            decision_body = {"id": decision_id, "requestId": row["id"], "actorId": actor_id, "decision": decision, "rationale": _text(payload.get("rationale"), 2000) or None, "createdAt": now}
            try:
                con.execute("INSERT INTO approval_decisions VALUES(?,?,?,?,?,?,?)", (decision_id, row["id"], actor_id, decision, decision_body["rationale"], _hash(decision_body), now))
            except sqlite3.IntegrityError as exc:
                raise InstitutionalGovernanceError("This actor has already decided the approval request.", 409) from exc
            decisions = con.execute("SELECT decision FROM approval_decisions WHERE request_id=?", (row["id"],)).fetchall()
            values = [item["decision"] for item in decisions]
            status = "pending"
            resolved_at = None
            if "reject" in values: status = "rejected"; resolved_at = now
            elif "request-changes" in values: status = "changes-requested"
            elif values.count("approve") >= row["required_decisions"]: status = "approved"; resolved_at = now
            con.execute("UPDATE approval_requests SET status=?,updated_at=?,resolved_at=? WHERE id=?", (status, now, resolved_at, row["id"]))
            self._event(con, row["institution_id"], workspace_id, "approval.decided", actor_id, {"requestId": row["id"], "decision": decision, "status": status})
            updated = con.execute("SELECT * FROM approval_requests WHERE id=?", (row["id"],)).fetchone()
            record = self._approval_request_record(con, updated)
        return {"ok": True, "approvalRequest": record}

    def dashboard(self, institution_id: str, actor_id: str) -> dict[str, Any]:
        with self._connect() as con:
            _, roles = self._require_institution(con, institution_id, actor_id)
            counts = {
                "units": con.execute("SELECT COUNT(*) AS count FROM organizational_units WHERE institution_id=? AND status='active'", (institution_id,)).fetchone()["count"],
                "principals": con.execute("SELECT COUNT(*) AS count FROM principals WHERE institution_id=? AND status='active'", (institution_id,)).fetchone()["count"],
                "servicePrincipals": con.execute("SELECT COUNT(*) AS count FROM principals WHERE institution_id=? AND principal_type='service' AND status='active'", (institution_id,)).fetchone()["count"],
                "activeBindings": con.execute("SELECT COUNT(*) AS count FROM role_bindings WHERE institution_id=? AND status='active'", (institution_id,)).fetchone()["count"],
                "governedWorkspaces": con.execute("SELECT COUNT(*) AS count FROM workspace_governance WHERE institution_id=? AND status='active'", (institution_id,)).fetchone()["count"],
                "retentionPolicies": con.execute("SELECT COUNT(*) AS count FROM retention_policies WHERE institution_id=?", (institution_id,)).fetchone()["count"],
                "pendingApprovals": con.execute("SELECT COUNT(*) AS count FROM approval_requests WHERE institution_id=? AND status='pending'", (institution_id,)).fetchone()["count"],
            }
            classifications = {row["classification"]: row["count"] for row in con.execute("SELECT classification,COUNT(*) AS count FROM workspace_governance WHERE institution_id=? GROUP BY classification", (institution_id,)).fetchall()}
        return {"ok": True, "version": VERSION, "institutionId": institution_id, "currentRoles": roles, "counts": counts, "workspaceClassifications": classifications, "durability": "persistent-disk" if self.persistent_disk_mounted else "instance-local"}

    def timeline(self, institution_id: str, actor_id: str, limit: int = 500) -> dict[str, Any]:
        with self._connect() as con:
            self._require_institution(con, institution_id, actor_id, "auditor")
            rows = con.execute("SELECT * FROM governance_events WHERE institution_id=? ORDER BY sequence DESC LIMIT ?", (institution_id, max(1, min(int(limit), 5000)))).fetchall()
        events = [{"schema": EVENT_SCHEMA, "version": VERSION, "sequence": row["sequence"], "institutionId": row["institution_id"], "workspaceId": row["workspace_id"], "eventType": row["event_type"], "actorId": row["actor_id"], "details": json.loads(row["details_json"]), "previousHash": row["previous_hash"], "eventHash": row["event_hash"], "createdAt": row["created_at"]} for row in rows]
        return {"ok": True, "version": VERSION, "count": len(events), "events": events}
