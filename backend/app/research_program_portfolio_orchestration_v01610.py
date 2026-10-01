from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.161.0"
PROGRAM_SCHEMA = "sc-lab-research-program/0.161.0"
PORTFOLIO_SCHEMA = "sc-lab-research-portfolio/0.161.0"
MEMBERSHIP_SCHEMA = "sc-lab-research-program-project-membership/0.161.0"
OBJECTIVE_SCHEMA = "sc-lab-research-program-objective/0.161.0"
MILESTONE_SCHEMA = "sc-lab-research-program-milestone/0.161.0"
MANIFEST_SCHEMA = "sc-lab-research-program-portfolio-manifest/0.161.0"
SNAPSHOT_SCHEMA = "sc-lab-research-program-portfolio-snapshot/0.161.0"

STATES = ("draft", "active", "review", "completed", "archived")
MEMBERSHIP_ROLES = {"primary", "supporting", "replication", "validation", "publication", "infrastructure"}
OBJECTIVE_STATUSES = {"planned", "active", "complete", "blocked", "withdrawn"}
MILESTONE_STATUSES = {"planned", "in-progress", "complete", "blocked", "withdrawn"}

BOUNDARY = (
    "Research Program & Portfolio Orchestration coordinates explicit program and portfolio structures above Computational "
    "Research Operating System II projects. It aggregates project lifecycle state, objectives, milestones, and human-authored "
    "program governance records. It does not rank projects, allocate funding or resources, create or execute scientific work, "
    "infer scientific validity, judge replication success, publish automatically, or advance program/portfolio state without "
    "explicit human authorization. Platform Core remains canonical object authority, Workspace remains execution authority, "
    "and Research OS v0.160.0 remains the project-lifecycle authority."
)


class ResearchProgramPortfolioError(ValueError):
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


def _id(value: Any, label: str) -> str:
    text = str(value or "").strip()
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:."
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise ResearchProgramPortfolioError(f"Invalid {label}.")
    return text


def _text(value: Any, label: str, maximum: int = 16000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ResearchProgramPortfolioError(f"{label} is required.")
    if len(text) > maximum:
        raise ResearchProgramPortfolioError(f"{label} exceeds {maximum} characters.")
    return text


def _json(value: Any, label: str, maximum_bytes: int = 1_000_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise ResearchProgramPortfolioError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise ResearchProgramPortfolioError(f"{label} exceeds payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


class ResearchProgramPortfolioOrchestrationManager:
    def __init__(
        self,
        db_path: str,
        research_os: Any | None = None,
        persistent_disk_mounted: bool = False,
        max_programs: int = 10000,
        max_portfolios: int = 5000,
        max_memberships: int = 250000,
        max_objectives: int = 250000,
        max_milestones: int = 250000,
        max_snapshots: int = 100000,
        history_limit: int = 500000,
    ):
        self.db_path = str(db_path)
        self.research_os = research_os
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_programs = max(1, int(max_programs))
        self.max_portfolios = max(1, int(max_portfolios))
        self.max_memberships = max(1, int(max_memberships))
        self.max_objectives = max(1, int(max_objectives))
        self.max_milestones = max(1, int(max_milestones))
        self.max_snapshots = max(1, int(max_snapshots))
        self.history_limit = max(100, int(history_limit))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        class _ClosingConnection(sqlite3.Connection):
            def __exit__(self, exc_type, exc, tb):
                try:
                    return super().__exit__(exc_type, exc, tb)
                finally:
                    self.close()

        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False, factory=_ClosingConnection)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self):
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS rppo_programs(
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    state TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rppo_portfolios(
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    state TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rppo_program_projects(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    workstream TEXT NOT NULL,
                    contribution TEXT NOT NULL,
                    status TEXT NOT NULL,
                    joined_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    UNIQUE(program_id, project_id)
                );
                CREATE TABLE IF NOT EXISTS rppo_objectives(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    owner_ref TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rppo_objective_projects(
                    id TEXT PRIMARY KEY,
                    objective_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    contribution TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    UNIQUE(objective_id, project_id)
                );
                CREATE TABLE IF NOT EXISTS rppo_milestones(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    target_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_ref TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rppo_portfolio_programs(
                    id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    program_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    joined_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    UNIQUE(portfolio_id, program_id)
                );
                CREATE TABLE IF NOT EXISTS rppo_transitions(
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    from_state TEXT NOT NULL,
                    to_state TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    human_authorization INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rppo_snapshots(
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rppo_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope_type TEXT NOT NULL,
                    scope_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _count(db: sqlite3.Connection, table: str) -> int:
        return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    def _event(self, db, scope_type: str, scope_id: str, kind: str, object_id: str, payload: Any, actor: str):
        db.execute(
            "INSERT INTO rppo_events(scope_type,scope_id,kind,object_id,payload_json,created_at,actor) VALUES(?,?,?,?,?,?,?)",
            (scope_type, scope_id, kind, object_id, json.dumps(payload, sort_keys=True), _now(), actor or "human"),
        )
        excess = int(db.execute("SELECT COUNT(*) FROM rppo_events").fetchone()[0]) - self.history_limit
        if excess > 0:
            db.execute("DELETE FROM rppo_events WHERE seq IN (SELECT seq FROM rppo_events ORDER BY seq LIMIT ?)", (excess,))

    def policies(self):
        return {
            "version": VERSION,
            "states": list(STATES),
            "membershipRoles": sorted(MEMBERSHIP_ROLES),
            "objectiveStatuses": sorted(OBJECTIVE_STATUSES),
            "milestoneStatuses": sorted(MILESTONE_STATUSES),
            "programAggregationIsDescriptive": True,
            "portfolioAggregationIsDescriptive": True,
            "researchOSProjectReferences": True,
            "platformCoreCanonicalAuthority": True,
            "workspaceExecutionAuthority": True,
            "researchOSProjectLifecycleAuthority": True,
            "automaticProjectCreation": False,
            "automaticProjectRanking": False,
            "automaticFundingAllocation": False,
            "automaticResourceAllocation": False,
            "automaticScientificValidity": False,
            "automaticStageAdvancement": False,
            "automaticPublication": False,
            "humanAuthorizationRequired": True,
            "boundary": BOUNDARY,
        }

    def health(self):
        return {
            "ok": True,
            "version": VERSION,
            "researchProgramPortfolioOrchestration": True,
            "programRegistry": True,
            "portfolioRegistry": True,
            "researchOSProjectMembership": True,
            "programObjectives": True,
            "programMilestones": True,
            "objectiveProjectAllocation": True,
            "humanControlledProgramLifecycle": True,
            "humanControlledPortfolioLifecycle": True,
            "programCommandCenter": True,
            "portfolioCommandCenter": True,
            "immutableSnapshots": True,
            "manifestDigestVerification": True,
            "descriptiveAggregationOnly": True,
            "automaticProjectRanking": False,
            "automaticFundingAllocation": False,
            "automaticResourceAllocation": False,
            "automaticScientificValidity": False,
            "automaticPublication": False,
            "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local",
            "boundary": BOUNDARY,
        }

    def _resolve_project(self, project_id: str) -> dict[str, Any]:
        project_id = _id(project_id, "projectId")
        if self.research_os is None:
            raise ResearchProgramPortfolioError("Research OS v0.160.0 is unavailable for project reference resolution.", 503)
        try:
            project = self.research_os.get_project(project_id)
        except Exception as exc:
            raise ResearchProgramPortfolioError(f"Research OS project could not be resolved: {project_id}.", 409) from exc
        if not isinstance(project, dict) or str(project.get("id") or "") != project_id:
            raise ResearchProgramPortfolioError(f"Research OS project reference is invalid: {project_id}.", 409)
        return project

    @staticmethod
    def _program_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": PROGRAM_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "title": row["title"],
            "purpose": row["purpose"],
            "state": row["state"],
            "metadata": json.loads(row["metadata_json"]),
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    @staticmethod
    def _portfolio_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": PORTFOLIO_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "title": row["title"],
            "purpose": row["purpose"],
            "state": row["state"],
            "metadata": json.loads(row["metadata_json"]),
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    @staticmethod
    def _membership_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": MEMBERSHIP_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "programId": row["program_id"],
            "projectId": row["project_id"],
            "role": row["role"],
            "workstream": row["workstream"],
            "contribution": row["contribution"],
            "status": row["status"],
            "joinedAt": row["joined_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    @staticmethod
    def _objective_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": OBJECTIVE_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "programId": row["program_id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "ownerRef": row["owner_ref"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    @staticmethod
    def _milestone_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": MILESTONE_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "programId": row["program_id"],
            "title": row["title"],
            "description": row["description"],
            "targetDate": row["target_date"],
            "status": row["status"],
            "evidenceRef": row["evidence_ref"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    def create_program(self, payload: dict[str, Any], actor: str = "human"):
        title = _text(payload.get("title"), "title", 600, True)
        purpose = _text(payload.get("purpose"), "purpose", 16000, True)
        metadata = _json(payload.get("metadata") or {}, "metadata", 500000)
        program_id = _id(payload.get("programId") or ("program:" + uuid.uuid4().hex), "programId")
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_programs") >= self.max_programs:
                raise ResearchProgramPortfolioError("Research program limit reached.", 409)
            if db.execute("SELECT id FROM rppo_programs WHERE id=?", (program_id,)).fetchone():
                raise ResearchProgramPortfolioError("Research program already exists.", 409)
            db.execute("INSERT INTO rppo_programs VALUES(?,?,?,?,?,?,?,?)", (program_id, title, purpose, "draft", json.dumps(metadata, sort_keys=True), now, now, actor))
            self._event(db, "program", program_id, "program.created", program_id, {"state": "draft"}, actor)
        return {"ok": True, "program": self.get_program(program_id)}

    def list_programs(self, include_archived: bool = False, limit: int = 100):
        limit = max(1, min(int(limit), 1000))
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM rppo_programs WHERE (?=1 OR state<>'archived') ORDER BY updated_at DESC LIMIT ?",
                (1 if include_archived else 0, limit),
            ).fetchall()
        return {"ok": True, "programs": [self._program_row(x) for x in rows], "count": len(rows)}

    def get_program(self, program_id: str):
        program_id = _id(program_id, "programId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM rppo_programs WHERE id=?", (program_id,)).fetchone()
            if not row:
                raise ResearchProgramPortfolioError("Research program not found.", 404)
            memberships = db.execute("SELECT * FROM rppo_program_projects WHERE program_id=? ORDER BY joined_at,id", (program_id,)).fetchall()
            objectives = db.execute("SELECT * FROM rppo_objectives WHERE program_id=? ORDER BY created_at,id", (program_id,)).fetchall()
            milestones = db.execute("SELECT * FROM rppo_milestones WHERE program_id=? ORDER BY created_at,id", (program_id,)).fetchall()
            allocations = db.execute(
                "SELECT op.* FROM rppo_objective_projects op JOIN rppo_objectives o ON o.id=op.objective_id WHERE o.program_id=? ORDER BY op.created_at,op.id",
                (program_id,),
            ).fetchall()
        out = self._program_row(row)
        out["projects"] = [self._membership_row(x) for x in memberships]
        out["objectives"] = [self._objective_row(x) for x in objectives]
        out["milestones"] = [self._milestone_row(x) for x in milestones]
        out["objectiveProjectAllocations"] = [
            {
                "id": x["id"],
                "objectiveId": x["objective_id"],
                "projectId": x["project_id"],
                "contribution": x["contribution"],
                "createdAt": x["created_at"],
                "actor": x["actor"],
            }
            for x in allocations
        ]
        return out

    def add_project(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        program = self.get_program(program_id)
        if program["state"] == "archived":
            raise ResearchProgramPortfolioError("Archived programs cannot accept project memberships.", 409)
        project_id = _id(payload.get("projectId"), "projectId")
        self._resolve_project(project_id)
        role = str(payload.get("role") or "primary").strip().lower()
        if role not in MEMBERSHIP_ROLES:
            raise ResearchProgramPortfolioError("Unsupported program project role.")
        workstream = _text(payload.get("workstream") or "general", "workstream", 500, True)
        contribution = _text(payload.get("contribution"), "contribution", 8000)
        now = _now()
        membership_id = "membership:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_program_projects") >= self.max_memberships:
                raise ResearchProgramPortfolioError("Program project-membership limit reached.", 409)
            try:
                db.execute(
                    "INSERT INTO rppo_program_projects VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (membership_id, program_id, project_id, role, workstream, contribution, "active", now, now, actor),
                )
            except sqlite3.IntegrityError as exc:
                raise ResearchProgramPortfolioError("Research OS project is already a member of this program.", 409) from exc
            db.execute("UPDATE rppo_programs SET updated_at=? WHERE id=?", (now, program_id))
            self._event(db, "program", program_id, "project.membership.added", membership_id, {"projectId": project_id, "role": role, "workstream": workstream}, actor)
        return {"ok": True, "program": self.get_program(program_id)}

    def set_project_membership_status(self, program_id: str, membership_id: str, payload: dict[str, Any], actor: str = "human"):
        self.get_program(program_id)
        membership_id = _id(membership_id, "membershipId")
        status = str(payload.get("status") or "").strip().lower()
        if status not in {"active", "withdrawn"}:
            raise ResearchProgramPortfolioError("Membership status must be active or withdrawn.")
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM rppo_program_projects WHERE id=? AND program_id=?", (membership_id, program_id)).fetchone()
            if not row:
                raise ResearchProgramPortfolioError("Program project membership not found.", 404)
            now = _now()
            db.execute("UPDATE rppo_program_projects SET status=?,updated_at=?,actor=? WHERE id=?", (status, now, actor, membership_id))
            db.execute("UPDATE rppo_programs SET updated_at=? WHERE id=?", (now, program_id))
            self._event(db, "program", program_id, "project.membership.status", membership_id, {"status": status}, actor)
        return {"ok": True, "program": self.get_program(program_id)}

    def create_objective(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        program = self.get_program(program_id)
        if program["state"] == "archived":
            raise ResearchProgramPortfolioError("Archived programs cannot accept objectives.", 409)
        title = _text(payload.get("title"), "objective title", 600, True)
        description = _text(payload.get("description"), "objective description", 16000, True)
        owner_ref = _text(payload.get("ownerRef"), "ownerRef", 500)
        status = str(payload.get("status") or "planned").strip().lower()
        if status not in OBJECTIVE_STATUSES:
            raise ResearchProgramPortfolioError("Unsupported objective status.")
        objective_id = _id(payload.get("objectiveId") or ("objective:" + uuid.uuid4().hex), "objectiveId")
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_objectives") >= self.max_objectives:
                raise ResearchProgramPortfolioError("Program objective limit reached.", 409)
            if db.execute("SELECT id FROM rppo_objectives WHERE id=?", (objective_id,)).fetchone():
                raise ResearchProgramPortfolioError("Program objective already exists.", 409)
            db.execute("INSERT INTO rppo_objectives VALUES(?,?,?,?,?,?,?,?,?)", (objective_id, program_id, title, description, status, owner_ref, now, now, actor))
            db.execute("UPDATE rppo_programs SET updated_at=? WHERE id=?", (now, program_id))
            self._event(db, "program", program_id, "objective.created", objective_id, {"status": status}, actor)
        return {"ok": True, "objective": next(x for x in self.get_program(program_id)["objectives"] if x["id"] == objective_id)}

    def allocate_objective_project(self, program_id: str, objective_id: str, payload: dict[str, Any], actor: str = "human"):
        program = self.get_program(program_id)
        objective_id = _id(objective_id, "objectiveId")
        objective = next((x for x in program["objectives"] if x["id"] == objective_id), None)
        if not objective:
            raise ResearchProgramPortfolioError("Program objective not found.", 404)
        project_id = _id(payload.get("projectId"), "projectId")
        self._resolve_project(project_id)
        active_members = {x["projectId"] for x in program["projects"] if x["status"] == "active"}
        if project_id not in active_members:
            raise ResearchProgramPortfolioError("Objective project must be an active member of the program.", 409)
        contribution = _text(payload.get("contribution"), "contribution", 8000, True)
        allocation_id = "allocation:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            try:
                db.execute("INSERT INTO rppo_objective_projects VALUES(?,?,?,?,?,?)", (allocation_id, objective_id, project_id, contribution, _now(), actor))
            except sqlite3.IntegrityError as exc:
                raise ResearchProgramPortfolioError("Project is already allocated to this objective.", 409) from exc
            self._event(db, "program", program_id, "objective.project.allocated", allocation_id, {"objectiveId": objective_id, "projectId": project_id}, actor)
        return {"ok": True, "program": self.get_program(program_id)}

    def set_objective_status(self, program_id: str, objective_id: str, payload: dict[str, Any], actor: str = "human"):
        self.get_program(program_id)
        objective_id = _id(objective_id, "objectiveId")
        status = str(payload.get("status") or "").strip().lower()
        if status not in OBJECTIVE_STATUSES:
            raise ResearchProgramPortfolioError("Unsupported objective status.")
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM rppo_objectives WHERE id=? AND program_id=?", (objective_id, program_id)).fetchone()
            if not row:
                raise ResearchProgramPortfolioError("Program objective not found.", 404)
            now = _now()
            db.execute("UPDATE rppo_objectives SET status=?,updated_at=?,actor=? WHERE id=?", (status, now, actor, objective_id))
            db.execute("UPDATE rppo_programs SET updated_at=? WHERE id=?", (now, program_id))
            self._event(db, "program", program_id, "objective.status", objective_id, {"status": status}, actor)
        return {"ok": True, "objective": next(x for x in self.get_program(program_id)["objectives"] if x["id"] == objective_id)}

    def create_milestone(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        program = self.get_program(program_id)
        if program["state"] == "archived":
            raise ResearchProgramPortfolioError("Archived programs cannot accept milestones.", 409)
        title = _text(payload.get("title"), "milestone title", 600, True)
        description = _text(payload.get("description"), "milestone description", 16000)
        target_date = _text(payload.get("targetDate"), "targetDate", 80)
        evidence_ref = _text(payload.get("evidenceRef"), "evidenceRef", 500)
        status = str(payload.get("status") or "planned").strip().lower()
        if status not in MILESTONE_STATUSES:
            raise ResearchProgramPortfolioError("Unsupported milestone status.")
        milestone_id = _id(payload.get("milestoneId") or ("milestone:" + uuid.uuid4().hex), "milestoneId")
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_milestones") >= self.max_milestones:
                raise ResearchProgramPortfolioError("Program milestone limit reached.", 409)
            if db.execute("SELECT id FROM rppo_milestones WHERE id=?", (milestone_id,)).fetchone():
                raise ResearchProgramPortfolioError("Program milestone already exists.", 409)
            db.execute("INSERT INTO rppo_milestones VALUES(?,?,?,?,?,?,?,?,?,?)", (milestone_id, program_id, title, description, target_date, status, evidence_ref, now, now, actor))
            db.execute("UPDATE rppo_programs SET updated_at=? WHERE id=?", (now, program_id))
            self._event(db, "program", program_id, "milestone.created", milestone_id, {"status": status, "targetDate": target_date}, actor)
        return {"ok": True, "milestone": next(x for x in self.get_program(program_id)["milestones"] if x["id"] == milestone_id)}

    def set_milestone_status(self, program_id: str, milestone_id: str, payload: dict[str, Any], actor: str = "human"):
        self.get_program(program_id)
        milestone_id = _id(milestone_id, "milestoneId")
        status = str(payload.get("status") or "").strip().lower()
        if status not in MILESTONE_STATUSES:
            raise ResearchProgramPortfolioError("Unsupported milestone status.")
        evidence_ref = _text(payload.get("evidenceRef"), "evidenceRef", 500)
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM rppo_milestones WHERE id=? AND program_id=?", (milestone_id, program_id)).fetchone()
            if not row:
                raise ResearchProgramPortfolioError("Program milestone not found.", 404)
            now = _now()
            db.execute(
                "UPDATE rppo_milestones SET status=?,evidence_ref=?,updated_at=?,actor=? WHERE id=?",
                (status, evidence_ref or row["evidence_ref"], now, actor, milestone_id),
            )
            db.execute("UPDATE rppo_programs SET updated_at=? WHERE id=?", (now, program_id))
            self._event(db, "program", program_id, "milestone.status", milestone_id, {"status": status, "evidenceRef": evidence_ref or row["evidence_ref"]}, actor)
        return {"ok": True, "milestone": next(x for x in self.get_program(program_id)["milestones"] if x["id"] == milestone_id)}

    def _project_stage_snapshot(self, program: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        resolved: list[dict[str, Any]] = []
        unresolved: list[dict[str, Any]] = []
        for membership in program["projects"]:
            if membership["status"] != "active":
                continue
            try:
                project = self._resolve_project(membership["projectId"])
                resolved.append(
                    {
                        "projectId": membership["projectId"],
                        "role": membership["role"],
                        "workstream": membership["workstream"],
                        "title": project.get("title", ""),
                        "stage": project.get("stage", "unknown"),
                        "updatedAt": project.get("updatedAt", ""),
                    }
                )
            except ResearchProgramPortfolioError as exc:
                unresolved.append({"projectId": membership["projectId"], "detail": exc.detail})
        return resolved, unresolved

    def evaluate_program(self, program_id: str, target_state: str | None = None):
        program = self.get_program(program_id)
        target = str(target_state or program["state"]).strip().lower()
        if target not in STATES:
            raise ResearchProgramPortfolioError("Unsupported program state.")
        active_projects = [x for x in program["projects"] if x["status"] == "active"]
        active_objectives = [x for x in program["objectives"] if x["status"] != "withdrawn"]
        active_milestones = [x for x in program["milestones"] if x["status"] != "withdrawn"]
        blockers: list[dict[str, Any]] = []
        if target in {"active", "review", "completed"}:
            if not active_projects:
                blockers.append({"type": "missing-active-project"})
            if not active_objectives:
                blockers.append({"type": "missing-objective"})
        if target == "review":
            if not any(x["status"] == "complete" for x in active_objectives):
                blockers.append({"type": "no-completed-objective"})
        if target == "completed":
            for objective in active_objectives:
                if objective["status"] != "complete":
                    blockers.append({"type": "objective-incomplete", "objectiveId": objective["id"], "status": objective["status"]})
            for milestone in active_milestones:
                if milestone["status"] != "complete":
                    blockers.append({"type": "milestone-incomplete", "milestoneId": milestone["id"], "status": milestone["status"]})
        resolved, unresolved = self._project_stage_snapshot(program)
        for item in unresolved:
            blockers.append({"type": "unresolved-research-os-project", **item})
        return {
            "ok": True,
            "programId": program_id,
            "currentState": program["state"],
            "targetState": target,
            "proceduralReady": len(blockers) == 0,
            "blockers": blockers,
            "activeProjectCount": len(active_projects),
            "objectiveCount": len(active_objectives),
            "milestoneCount": len(active_milestones),
            "researchOSProjects": resolved,
            "automaticScientificValidity": False,
            "automaticProjectRanking": False,
            "humanAuthorizationRequired": True,
            "boundary": BOUNDARY,
        }

    def transition_program(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        program = self.get_program(program_id)
        if not bool(payload.get("humanAuthorization", False)):
            raise ResearchProgramPortfolioError("Explicit humanAuthorization=true is required for program state transitions.", 409)
        target = str(payload.get("targetState") or "").strip().lower()
        reason = _text(payload.get("reason"), "reason", 8000, True)
        if target not in STATES:
            raise ResearchProgramPortfolioError("Unsupported program state.")
        current_index = STATES.index(program["state"])
        target_index = STATES.index(target)
        if program["state"] == "archived":
            raise ResearchProgramPortfolioError("Archived programs cannot transition.", 409)
        if target == "archived":
            pass
        elif target_index < current_index:
            raise ResearchProgramPortfolioError("Program state cannot move backward.", 409)
        elif target_index > current_index + 1:
            raise ResearchProgramPortfolioError("Program states must advance one stage at a time.", 409)
        validation = self.evaluate_program(program_id, target)
        if target != "archived" and target_index > current_index and not validation["proceduralReady"]:
            raise ResearchProgramPortfolioError("Program prerequisites are incomplete; inspect validation blockers.", 409)
        now = _now()
        tid = "transition:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute("UPDATE rppo_programs SET state=?,updated_at=? WHERE id=?", (target, now, program_id))
            db.execute("INSERT INTO rppo_transitions VALUES(?,?,?,?,?,?,?,?,?)", (tid, "program", program_id, program["state"], target, reason, 1, now, actor))
            self._event(db, "program", program_id, "program.transition", tid, {"from": program["state"], "to": target, "humanAuthorization": True}, actor)
        return {"ok": True, "program": self.get_program(program_id), "validation": validation}

    def program_command_center(self, program_id: str):
        program = self.get_program(program_id)
        resolved, unresolved = self._project_stage_snapshot(program)
        stage_counts: dict[str, int] = {}
        for item in resolved:
            stage = str(item.get("stage") or "unknown")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        objective_counts: dict[str, int] = {}
        for item in program["objectives"]:
            objective_counts[item["status"]] = objective_counts.get(item["status"], 0) + 1
        milestone_counts: dict[str, int] = {}
        for item in program["milestones"]:
            milestone_counts[item["status"]] = milestone_counts.get(item["status"], 0) + 1
        next_state = None
        idx = STATES.index(program["state"])
        if idx + 1 < len(STATES) and STATES[idx + 1] != "archived":
            next_state = STATES[idx + 1]
        return {
            "ok": True,
            "program": {k: program[k] for k in ("id", "title", "purpose", "state", "createdAt", "updatedAt")},
            "researchOSProjects": resolved,
            "unresolvedProjects": unresolved,
            "projectStageCounts": stage_counts,
            "objectiveStatusCounts": objective_counts,
            "milestoneStatusCounts": milestone_counts,
            "currentStateEvaluation": self.evaluate_program(program_id, program["state"]),
            "nextState": next_state,
            "nextStateEvaluation": self.evaluate_program(program_id, next_state) if next_state else None,
            "automaticPrioritization": False,
            "automaticFundingAllocation": False,
            "automaticResourceAllocation": False,
            "humanControl": True,
            "boundary": BOUNDARY,
        }

    def create_portfolio(self, payload: dict[str, Any], actor: str = "human"):
        title = _text(payload.get("title"), "title", 600, True)
        purpose = _text(payload.get("purpose"), "purpose", 16000, True)
        metadata = _json(payload.get("metadata") or {}, "metadata", 500000)
        portfolio_id = _id(payload.get("portfolioId") or ("portfolio:" + uuid.uuid4().hex), "portfolioId")
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_portfolios") >= self.max_portfolios:
                raise ResearchProgramPortfolioError("Research portfolio limit reached.", 409)
            if db.execute("SELECT id FROM rppo_portfolios WHERE id=?", (portfolio_id,)).fetchone():
                raise ResearchProgramPortfolioError("Research portfolio already exists.", 409)
            db.execute("INSERT INTO rppo_portfolios VALUES(?,?,?,?,?,?,?,?)", (portfolio_id, title, purpose, "draft", json.dumps(metadata, sort_keys=True), now, now, actor))
            self._event(db, "portfolio", portfolio_id, "portfolio.created", portfolio_id, {"state": "draft"}, actor)
        return {"ok": True, "portfolio": self.get_portfolio(portfolio_id)}

    def list_portfolios(self, include_archived: bool = False, limit: int = 100):
        limit = max(1, min(int(limit), 1000))
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM rppo_portfolios WHERE (?=1 OR state<>'archived') ORDER BY updated_at DESC LIMIT ?",
                (1 if include_archived else 0, limit),
            ).fetchall()
        return {"ok": True, "portfolios": [self._portfolio_row(x) for x in rows], "count": len(rows)}

    def get_portfolio(self, portfolio_id: str):
        portfolio_id = _id(portfolio_id, "portfolioId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM rppo_portfolios WHERE id=?", (portfolio_id,)).fetchone()
            if not row:
                raise ResearchProgramPortfolioError("Research portfolio not found.", 404)
            memberships = db.execute("SELECT * FROM rppo_portfolio_programs WHERE portfolio_id=? ORDER BY joined_at,id", (portfolio_id,)).fetchall()
        out = self._portfolio_row(row)
        out["programs"] = [
            {
                "id": x["id"],
                "portfolioId": x["portfolio_id"],
                "programId": x["program_id"],
                "role": x["role"],
                "status": x["status"],
                "joinedAt": x["joined_at"],
                "updatedAt": x["updated_at"],
                "actor": x["actor"],
            }
            for x in memberships
        ]
        return out

    def add_program_to_portfolio(self, portfolio_id: str, payload: dict[str, Any], actor: str = "human"):
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio["state"] == "archived":
            raise ResearchProgramPortfolioError("Archived portfolios cannot accept program memberships.", 409)
        program_id = _id(payload.get("programId"), "programId")
        self.get_program(program_id)
        role = _text(payload.get("role") or "member", "role", 200, True)
        membership_id = "portfolio-membership:" + uuid.uuid4().hex
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_portfolio_programs") >= self.max_memberships:
                raise ResearchProgramPortfolioError("Portfolio program-membership limit reached.", 409)
            try:
                db.execute("INSERT INTO rppo_portfolio_programs VALUES(?,?,?,?,?,?,?,?)", (membership_id, portfolio_id, program_id, role, "active", now, now, actor))
            except sqlite3.IntegrityError as exc:
                raise ResearchProgramPortfolioError("Research program is already a member of this portfolio.", 409) from exc
            db.execute("UPDATE rppo_portfolios SET updated_at=? WHERE id=?", (now, portfolio_id))
            self._event(db, "portfolio", portfolio_id, "program.membership.added", membership_id, {"programId": program_id, "role": role}, actor)
        return {"ok": True, "portfolio": self.get_portfolio(portfolio_id)}

    def evaluate_portfolio(self, portfolio_id: str, target_state: str | None = None):
        portfolio = self.get_portfolio(portfolio_id)
        target = str(target_state or portfolio["state"]).strip().lower()
        if target not in STATES:
            raise ResearchProgramPortfolioError("Unsupported portfolio state.")
        active_memberships = [x for x in portfolio["programs"] if x["status"] == "active"]
        programs = [self.get_program(x["programId"]) for x in active_memberships]
        blockers: list[dict[str, Any]] = []
        if target in {"active", "review", "completed"} and not programs:
            blockers.append({"type": "missing-active-program"})
        if target == "review" and not any(x["state"] in {"review", "completed"} for x in programs):
            blockers.append({"type": "no-program-at-review-or-completed"})
        if target == "completed":
            for program in programs:
                if program["state"] != "completed":
                    blockers.append({"type": "program-incomplete", "programId": program["id"], "state": program["state"]})
        return {
            "ok": True,
            "portfolioId": portfolio_id,
            "currentState": portfolio["state"],
            "targetState": target,
            "proceduralReady": len(blockers) == 0,
            "blockers": blockers,
            "programCount": len(programs),
            "programStates": {state: sum(1 for p in programs if p["state"] == state) for state in STATES},
            "automaticPrioritization": False,
            "automaticFundingAllocation": False,
            "automaticResourceAllocation": False,
            "humanAuthorizationRequired": True,
            "boundary": BOUNDARY,
        }

    def transition_portfolio(self, portfolio_id: str, payload: dict[str, Any], actor: str = "human"):
        portfolio = self.get_portfolio(portfolio_id)
        if not bool(payload.get("humanAuthorization", False)):
            raise ResearchProgramPortfolioError("Explicit humanAuthorization=true is required for portfolio state transitions.", 409)
        target = str(payload.get("targetState") or "").strip().lower()
        reason = _text(payload.get("reason"), "reason", 8000, True)
        if target not in STATES:
            raise ResearchProgramPortfolioError("Unsupported portfolio state.")
        current_index = STATES.index(portfolio["state"])
        target_index = STATES.index(target)
        if portfolio["state"] == "archived":
            raise ResearchProgramPortfolioError("Archived portfolios cannot transition.", 409)
        if target == "archived":
            pass
        elif target_index < current_index:
            raise ResearchProgramPortfolioError("Portfolio state cannot move backward.", 409)
        elif target_index > current_index + 1:
            raise ResearchProgramPortfolioError("Portfolio states must advance one stage at a time.", 409)
        validation = self.evaluate_portfolio(portfolio_id, target)
        if target != "archived" and target_index > current_index and not validation["proceduralReady"]:
            raise ResearchProgramPortfolioError("Portfolio prerequisites are incomplete; inspect validation blockers.", 409)
        now = _now()
        tid = "transition:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute("UPDATE rppo_portfolios SET state=?,updated_at=? WHERE id=?", (target, now, portfolio_id))
            db.execute("INSERT INTO rppo_transitions VALUES(?,?,?,?,?,?,?,?,?)", (tid, "portfolio", portfolio_id, portfolio["state"], target, reason, 1, now, actor))
            self._event(db, "portfolio", portfolio_id, "portfolio.transition", tid, {"from": portfolio["state"], "to": target, "humanAuthorization": True}, actor)
        return {"ok": True, "portfolio": self.get_portfolio(portfolio_id), "validation": validation}

    def portfolio_command_center(self, portfolio_id: str):
        portfolio = self.get_portfolio(portfolio_id)
        programs = [self.get_program(x["programId"]) for x in portfolio["programs"] if x["status"] == "active"]
        program_state_counts: dict[str, int] = {}
        project_ids: set[str] = set()
        project_stage_counts: dict[str, int] = {}
        unresolved: list[dict[str, Any]] = []
        for program in programs:
            program_state_counts[program["state"]] = program_state_counts.get(program["state"], 0) + 1
            resolved, missing = self._project_stage_snapshot(program)
            unresolved.extend({"programId": program["id"], **x} for x in missing)
            for project in resolved:
                if project["projectId"] in project_ids:
                    continue
                project_ids.add(project["projectId"])
                stage = str(project.get("stage") or "unknown")
                project_stage_counts[stage] = project_stage_counts.get(stage, 0) + 1
        next_state = None
        idx = STATES.index(portfolio["state"])
        if idx + 1 < len(STATES) and STATES[idx + 1] != "archived":
            next_state = STATES[idx + 1]
        return {
            "ok": True,
            "portfolio": {k: portfolio[k] for k in ("id", "title", "purpose", "state", "createdAt", "updatedAt")},
            "programStateCounts": program_state_counts,
            "uniqueProjectCount": len(project_ids),
            "projectStageCounts": project_stage_counts,
            "unresolvedProjects": unresolved,
            "currentStateEvaluation": self.evaluate_portfolio(portfolio_id, portfolio["state"]),
            "nextState": next_state,
            "nextStateEvaluation": self.evaluate_portfolio(portfolio_id, next_state) if next_state else None,
            "automaticPrioritization": False,
            "automaticFundingAllocation": False,
            "automaticResourceAllocation": False,
            "humanControl": True,
            "boundary": BOUNDARY,
        }

    def _manifest_payload(self, entity_type: str, entity_id: str):
        if entity_type == "program":
            entity = self.get_program(entity_id)
            command = self.program_command_center(entity_id)
        elif entity_type == "portfolio":
            entity = self.get_portfolio(entity_id)
            command = self.portfolio_command_center(entity_id)
        else:
            raise ResearchProgramPortfolioError("entityType must be program or portfolio.")
        with self._connect() as db:
            transitions = db.execute("SELECT * FROM rppo_transitions WHERE entity_type=? AND entity_id=? ORDER BY created_at,id", (entity_type, entity_id)).fetchall()
        return {
            "schema": MANIFEST_SCHEMA,
            "version": VERSION,
            "entityType": entity_type,
            "entity": entity,
            "commandCenter": command,
            "transitions": [
                {
                    "id": x["id"],
                    "fromState": x["from_state"],
                    "toState": x["to_state"],
                    "reason": x["reason"],
                    "humanAuthorization": bool(x["human_authorization"]),
                    "createdAt": x["created_at"],
                    "actor": x["actor"],
                }
                for x in transitions
            ],
            "descriptiveAggregationOnly": True,
            "automaticScientificValidity": False,
            "automaticPrioritization": False,
            "boundary": BOUNDARY,
        }

    def manifest(self, entity_type: str, entity_id: str):
        payload = self._manifest_payload(entity_type, entity_id)
        return {"ok": True, "manifest": payload, "digest": _sha(payload)}

    def verify_manifest(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            raise ResearchProgramPortfolioError("Manifest verification payload must be an object.")
        manifest = payload.get("manifest")
        digest = str(payload.get("digest") or "")
        if not isinstance(manifest, dict) or not digest:
            raise ResearchProgramPortfolioError("manifest and digest are required.")
        actual = _sha(manifest)
        return {"ok": True, "verified": actual == digest, "expected": digest, "actual": actual}

    def snapshot(self, entity_type: str, entity_id: str, payload: dict[str, Any], actor: str = "human"):
        if not bool(payload.get("humanAuthorization", False)):
            raise ResearchProgramPortfolioError("Explicit humanAuthorization=true is required to freeze a program/portfolio snapshot.", 409)
        manifest = self._manifest_payload(entity_type, entity_id)
        snap = {
            "schema": SNAPSHOT_SCHEMA,
            "version": VERSION,
            "entityType": entity_type,
            "entityId": entity_id,
            "manifest": manifest,
            "frozenAt": _now(),
            "humanAuthorization": True,
            "immutable": True,
            "boundary": BOUNDARY,
        }
        digest = _sha(snap)
        snapshot_id = "snapshot:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            if self._count(db, "rppo_snapshots") >= self.max_snapshots:
                raise ResearchProgramPortfolioError("Program/portfolio snapshot limit reached.", 409)
            db.execute("INSERT INTO rppo_snapshots VALUES(?,?,?,?,?,?,?)", (snapshot_id, entity_type, entity_id, json.dumps(snap, sort_keys=True), digest, _now(), actor))
            self._event(db, entity_type, entity_id, "snapshot.frozen", snapshot_id, {"digest": digest}, actor)
        return {"ok": True, "snapshotId": snapshot_id, "digest": digest, "snapshot": snap}

    def get_snapshot(self, snapshot_id: str):
        snapshot_id = _id(snapshot_id, "snapshotId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM rppo_snapshots WHERE id=?", (snapshot_id,)).fetchone()
        if not row:
            raise ResearchProgramPortfolioError("Program/portfolio snapshot not found.", 404)
        return {"ok": True, "snapshotId": row["id"], "entityType": row["entity_type"], "entityId": row["entity_id"], "digest": row["digest"], "createdAt": row["created_at"], "actor": row["actor"], "snapshot": json.loads(row["snapshot_json"])}

    def timeline(self, entity_type: str, entity_id: str, limit: int = 500):
        if entity_type == "program":
            self.get_program(entity_id)
        elif entity_type == "portfolio":
            self.get_portfolio(entity_id)
        else:
            raise ResearchProgramPortfolioError("entityType must be program or portfolio.")
        limit = max(1, min(int(limit), 5000))
        with self._connect() as db:
            rows = db.execute("SELECT * FROM rppo_events WHERE scope_type=? AND scope_id=? ORDER BY seq DESC LIMIT ?", (entity_type, entity_id, limit)).fetchall()
        return {
            "ok": True,
            "entityType": entity_type,
            "entityId": entity_id,
            "events": [
                {
                    "seq": x["seq"],
                    "kind": x["kind"],
                    "objectId": x["object_id"],
                    "payload": json.loads(x["payload_json"]),
                    "createdAt": x["created_at"],
                    "actor": x["actor"],
                }
                for x in rows
            ],
        }
