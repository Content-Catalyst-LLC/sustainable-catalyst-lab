from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.162.0"
DEPENDENCY_SCHEMA = "sc-lab-cross-project-dependency/0.162.0"
RESOURCE_SCHEMA = "sc-lab-research-resource/0.162.0"
REQUIREMENT_SCHEMA = "sc-lab-project-resource-requirement/0.162.0"
PLAN_SCHEMA = "sc-lab-research-resource-plan/0.162.0"
MANIFEST_SCHEMA = "sc-lab-cross-project-resource-plan-manifest/0.162.0"
SNAPSHOT_SCHEMA = "sc-lab-cross-project-resource-plan-snapshot/0.162.0"

DEPENDENCY_TYPES = {
    "data", "model", "protocol", "evidence", "compute", "software-runtime",
    "instrument", "facility", "personnel-role", "milestone", "publication", "other"
}
DEPENDENCY_STATUSES = {"planned", "active", "satisfied", "blocked", "withdrawn"}
RESOURCE_TYPES = {
    "dataset", "model", "protocol", "compute-profile", "software-runtime", "instrument",
    "facility", "personnel-role", "storage", "network", "publication-service", "other"
}
RESOURCE_STATES = {"available", "limited", "unavailable", "retired"}
REQUIREMENT_STATUSES = {"requested", "acknowledged", "satisfied", "blocked", "withdrawn"}
PLAN_STATES = {"draft", "review", "approved", "archived"}

BOUNDARY = (
    "Cross-Project Dependency & Research Resource Planning records explicit dependencies, shared-resource declarations, "
    "project requirements, descriptive capacity conflicts, and human-authored planning scenarios within v0.161.0 research "
    "programs. It does not infer hidden dependencies, rank projects, optimize schedules, allocate resources or funding, reserve "
    "compute, create scientific work, infer scientific validity, judge replication success, or authorize publication. Platform "
    "Core remains canonical object authority, Workspace remains execution authority, Research OS v0.160.0 remains project-"
    "lifecycle authority, and v0.161.0 remains program/portfolio authority."
)


class CrossProjectResourcePlanningError(ValueError):
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
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:.'"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise CrossProjectResourcePlanningError(f"Invalid {label}.")
    return text


def _text(value: Any, label: str, maximum: int = 16000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise CrossProjectResourcePlanningError(f"{label} is required.")
    if len(text) > maximum:
        raise CrossProjectResourcePlanningError(f"{label} exceeds {maximum} characters.")
    return text


def _number(value: Any, label: str, minimum: float = 0.0) -> float:
    try:
        out = float(value)
    except Exception as exc:
        raise CrossProjectResourcePlanningError(f"{label} must be numeric.") from exc
    if out < minimum:
        raise CrossProjectResourcePlanningError(f"{label} must be >= {minimum}.")
    return out


def _json(value: Any, label: str, maximum_bytes: int = 1_000_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise CrossProjectResourcePlanningError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise CrossProjectResourcePlanningError(f"{label} exceeds payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


class CrossProjectDependencyResearchResourcePlanningManager:
    def __init__(
        self,
        db_path: str,
        program_portfolio: Any | None = None,
        persistent_disk_mounted: bool = False,
        max_dependencies: int = 500000,
        max_resources: int = 250000,
        max_requirements: int = 1000000,
        max_plans: int = 100000,
        max_snapshots: int = 100000,
        history_limit: int = 750000,
    ):
        self.db_path = str(db_path)
        self.program_portfolio = program_portfolio
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_dependencies = max(1, int(max_dependencies))
        self.max_resources = max(1, int(max_resources))
        self.max_requirements = max(1, int(max_requirements))
        self.max_plans = max(1, int(max_plans))
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
                CREATE TABLE IF NOT EXISTS cprp_dependencies(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    from_project_id TEXT NOT NULL,
                    to_project_id TEXT NOT NULL,
                    dependency_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    required_state TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_ref TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cprp_resources(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    capacity REAL NOT NULL,
                    state TEXT NOT NULL,
                    canonical_ref TEXT NOT NULL,
                    availability_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cprp_requirements(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    window_start TEXT NOT NULL,
                    window_end TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cprp_plans(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    state TEXT NOT NULL,
                    assumptions_json TEXT NOT NULL,
                    analysis_digest TEXT NOT NULL,
                    human_authorization INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cprp_transitions(
                    id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    from_state TEXT NOT NULL,
                    to_state TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    human_authorization INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cprp_snapshots(
                    id TEXT PRIMARY KEY,
                    program_id TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cprp_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_id TEXT NOT NULL,
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

    def _event(self, db, program_id: str, kind: str, object_id: str, payload: Any, actor: str):
        db.execute(
            "INSERT INTO cprp_events(program_id,kind,object_id,payload_json,created_at,actor) VALUES(?,?,?,?,?,?)",
            (program_id, kind, object_id, json.dumps(payload, sort_keys=True), _now(), actor or "human"),
        )
        excess = int(db.execute("SELECT COUNT(*) FROM cprp_events").fetchone()[0]) - self.history_limit
        if excess > 0:
            db.execute("DELETE FROM cprp_events WHERE seq IN (SELECT seq FROM cprp_events ORDER BY seq LIMIT ?)", (excess,))

    def _program(self, program_id: str) -> dict[str, Any]:
        program_id = _id(program_id, "programId")
        if self.program_portfolio is None:
            raise CrossProjectResourcePlanningError("Research Program & Portfolio Orchestration v0.161.0 is unavailable.", 503)
        try:
            program = self.program_portfolio.get_program(program_id)
        except Exception as exc:
            raise CrossProjectResourcePlanningError(f"Research program could not be resolved: {program_id}.", 409) from exc
        if not isinstance(program, dict) or str(program.get("id") or "") != program_id:
            raise CrossProjectResourcePlanningError(f"Research program reference is invalid: {program_id}.", 409)
        return program

    @staticmethod
    def _project_ids(program: dict[str, Any]) -> set[str]:
        return {str(x.get("projectId")) for x in (program.get("projects") or []) if x.get("status") == "active" and x.get("projectId")}

    def _project(self, program_id: str, project_id: str) -> str:
        program = self._program(program_id)
        project_id = _id(project_id, "projectId")
        if project_id not in self._project_ids(program):
            raise CrossProjectResourcePlanningError("Project must be an active member of the research program.", 409)
        return project_id

    def policies(self):
        return {
            "version": VERSION,
            "dependencyTypes": sorted(DEPENDENCY_TYPES),
            "dependencyStatuses": sorted(DEPENDENCY_STATUSES),
            "resourceTypes": sorted(RESOURCE_TYPES),
            "resourceStates": sorted(RESOURCE_STATES),
            "requirementStatuses": sorted(REQUIREMENT_STATUSES),
            "planStates": sorted(PLAN_STATES),
            "explicitDependenciesOnly": True,
            "descriptiveCapacityAnalysisOnly": True,
            "humanApprovedPlans": True,
            "programAuthorityVersion": "0.161.0",
            "researchOSProjectLifecycleAuthority": True,
            "platformCoreCanonicalAuthority": True,
            "workspaceExecutionAuthority": True,
            "automaticDependencyInference": False,
            "automaticScheduling": False,
            "automaticResourceAllocation": False,
            "automaticFundingAllocation": False,
            "automaticProjectRanking": False,
            "automaticScientificValidity": False,
            "automaticExecution": False,
            "automaticPublication": False,
            "boundary": BOUNDARY,
        }

    def health(self):
        return {
            "ok": True,
            "version": VERSION,
            "crossProjectDependencyResearchResourcePlanning": True,
            "explicitDependencyGraph": True,
            "sharedResourceRegistry": True,
            "projectResourceRequirements": True,
            "descriptiveCapacityConflictDetection": True,
            "dependencyBlockerAnalysis": True,
            "humanApprovedPlanningScenarios": True,
            "programPlanningCommandCenter": True,
            "immutableSnapshots": True,
            "manifestDigestVerification": True,
            "automaticDependencyInference": False,
            "automaticScheduling": False,
            "automaticResourceAllocation": False,
            "automaticFundingAllocation": False,
            "automaticProjectRanking": False,
            "automaticScientificValidity": False,
            "automaticExecution": False,
            "automaticPublication": False,
            "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local",
            "boundary": BOUNDARY,
        }

    @staticmethod
    def _dependency_row(row):
        return {
            "schema": DEPENDENCY_SCHEMA, "version": VERSION, "id": row["id"], "programId": row["program_id"],
            "fromProjectId": row["from_project_id"], "toProjectId": row["to_project_id"], "dependencyType": row["dependency_type"],
            "description": row["description"], "requiredState": row["required_state"], "status": row["status"],
            "evidenceRef": row["evidence_ref"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"],
        }

    @staticmethod
    def _resource_row(row):
        return {
            "schema": RESOURCE_SCHEMA, "version": VERSION, "id": row["id"], "programId": row["program_id"],
            "resourceType": row["resource_type"], "title": row["title"], "description": row["description"], "unit": row["unit"],
            "capacity": row["capacity"], "state": row["state"], "canonicalRef": row["canonical_ref"],
            "availability": json.loads(row["availability_json"]), "metadata": json.loads(row["metadata_json"]),
            "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"],
        }

    @staticmethod
    def _requirement_row(row):
        return {
            "schema": REQUIREMENT_SCHEMA, "version": VERSION, "id": row["id"], "programId": row["program_id"],
            "projectId": row["project_id"], "resourceId": row["resource_id"], "quantity": row["quantity"],
            "windowStart": row["window_start"], "windowEnd": row["window_end"], "purpose": row["purpose"], "status": row["status"],
            "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"],
        }

    @staticmethod
    def _plan_row(row):
        return {
            "schema": PLAN_SCHEMA, "version": VERSION, "id": row["id"], "programId": row["program_id"], "title": row["title"],
            "description": row["description"], "state": row["state"], "assumptions": json.loads(row["assumptions_json"]),
            "analysisDigest": row["analysis_digest"], "humanAuthorization": bool(row["human_authorization"]),
            "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"],
        }

    def create_dependency(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id)
        from_id = self._project(program_id, payload.get("fromProjectId"))
        to_id = self._project(program_id, payload.get("toProjectId"))
        if from_id == to_id:
            raise CrossProjectResourcePlanningError("Cross-project dependency must reference two different projects.")
        dep_type = str(payload.get("dependencyType") or "other").strip().lower()
        if dep_type not in DEPENDENCY_TYPES:
            raise CrossProjectResourcePlanningError("Unsupported dependencyType.")
        description = _text(payload.get("description"), "description", 8000, True)
        required_state = _text(payload.get("requiredState") or "available", "requiredState", 500, True)
        evidence_ref = _text(payload.get("evidenceRef"), "evidenceRef", 1000)
        now = _now(); dep_id = "dependency:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            if self._count(db, "cprp_dependencies") >= self.max_dependencies:
                raise CrossProjectResourcePlanningError("Cross-project dependency limit reached.", 409)
            db.execute("INSERT INTO cprp_dependencies VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (dep_id, program_id, from_id, to_id, dep_type, description, required_state, "planned", evidence_ref, now, now, actor))
            self._event(db, program_id, "dependency.created", dep_id, {"fromProjectId": from_id, "toProjectId": to_id, "dependencyType": dep_type}, actor)
        return {"ok": True, "dependency": self.get_dependency(dep_id)}

    def get_dependency(self, dependency_id: str):
        dependency_id = _id(dependency_id, "dependencyId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM cprp_dependencies WHERE id=?", (dependency_id,)).fetchone()
        if not row: raise CrossProjectResourcePlanningError("Dependency not found.", 404)
        return self._dependency_row(row)

    def list_dependencies(self, program_id: str, limit: int = 1000):
        self._program(program_id); limit=max(1,min(int(limit),5000))
        with self._connect() as db: rows=db.execute("SELECT * FROM cprp_dependencies WHERE program_id=? ORDER BY created_at,id LIMIT ?",(program_id,limit)).fetchall()
        return {"ok":True,"dependencies":[self._dependency_row(x) for x in rows],"count":len(rows)}

    def set_dependency_status(self, program_id: str, dependency_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id); dependency_id=_id(dependency_id,"dependencyId"); status=str(payload.get("status") or "").strip().lower()
        if status not in DEPENDENCY_STATUSES: raise CrossProjectResourcePlanningError("Unsupported dependency status.")
        with self._lock,self._connect() as db:
            row=db.execute("SELECT * FROM cprp_dependencies WHERE id=? AND program_id=?",(dependency_id,program_id)).fetchone()
            if not row: raise CrossProjectResourcePlanningError("Dependency not found.",404)
            db.execute("UPDATE cprp_dependencies SET status=?,updated_at=?,actor=? WHERE id=?",(status,_now(),actor,dependency_id))
            self._event(db,program_id,"dependency.status",dependency_id,{"status":status},actor)
        return {"ok":True,"dependency":self.get_dependency(dependency_id)}

    def create_resource(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id)
        resource_id=_id(payload.get("resourceId") or ("resource:"+uuid.uuid4().hex),"resourceId")
        rtype=str(payload.get("resourceType") or "other").strip().lower()
        if rtype not in RESOURCE_TYPES: raise CrossProjectResourcePlanningError("Unsupported resourceType.")
        title=_text(payload.get("title"),"title",1000,True); description=_text(payload.get("description"),"description",8000)
        unit=_text(payload.get("unit") or "unit","unit",100,True); capacity=_number(payload.get("capacity",1),"capacity",0.0)
        state=str(payload.get("state") or "available").strip().lower()
        if state not in RESOURCE_STATES: raise CrossProjectResourcePlanningError("Unsupported resource state.")
        canonical_ref=_text(payload.get("canonicalRef"),"canonicalRef",1000)
        availability=_json(payload.get("availability") or {},"availability"); metadata=_json(payload.get("metadata") or {},"metadata")
        now=_now()
        with self._lock,self._connect() as db:
            if self._count(db,"cprp_resources")>=self.max_resources: raise CrossProjectResourcePlanningError("Resource registry limit reached.",409)
            try: db.execute("INSERT INTO cprp_resources VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(resource_id,program_id,rtype,title,description,unit,capacity,state,canonical_ref,json.dumps(availability,sort_keys=True),json.dumps(metadata,sort_keys=True),now,now,actor))
            except sqlite3.IntegrityError as exc: raise CrossProjectResourcePlanningError("Resource id already exists.",409) from exc
            self._event(db,program_id,"resource.created",resource_id,{"resourceType":rtype,"capacity":capacity,"unit":unit},actor)
        return {"ok":True,"resource":self.get_resource(resource_id)}

    def get_resource(self, resource_id: str):
        resource_id=_id(resource_id,"resourceId")
        with self._connect() as db: row=db.execute("SELECT * FROM cprp_resources WHERE id=?",(resource_id,)).fetchone()
        if not row: raise CrossProjectResourcePlanningError("Resource not found.",404)
        return self._resource_row(row)

    def list_resources(self, program_id: str, limit: int = 1000):
        self._program(program_id);limit=max(1,min(int(limit),5000))
        with self._connect() as db: rows=db.execute("SELECT * FROM cprp_resources WHERE program_id=? ORDER BY created_at,id LIMIT ?",(program_id,limit)).fetchall()
        return {"ok":True,"resources":[self._resource_row(x) for x in rows],"count":len(rows)}

    def set_resource_state(self, program_id: str, resource_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id);resource_id=_id(resource_id,"resourceId");state=str(payload.get("state") or "").strip().lower()
        if state not in RESOURCE_STATES: raise CrossProjectResourcePlanningError("Unsupported resource state.")
        with self._lock,self._connect() as db:
            row=db.execute("SELECT * FROM cprp_resources WHERE id=? AND program_id=?",(resource_id,program_id)).fetchone()
            if not row: raise CrossProjectResourcePlanningError("Resource not found.",404)
            db.execute("UPDATE cprp_resources SET state=?,updated_at=?,actor=? WHERE id=?",(state,_now(),actor,resource_id));self._event(db,program_id,"resource.state",resource_id,{"state":state},actor)
        return {"ok":True,"resource":self.get_resource(resource_id)}

    def create_requirement(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id); project_id=self._project(program_id,payload.get("projectId")); resource_id=_id(payload.get("resourceId"),"resourceId")
        resource=self.get_resource(resource_id)
        if resource["programId"]!=program_id: raise CrossProjectResourcePlanningError("Resource is not registered in this program.",409)
        quantity=_number(payload.get("quantity",1),"quantity",0.0);start=_text(payload.get("windowStart"),"windowStart",100);end=_text(payload.get("windowEnd"),"windowEnd",100);purpose=_text(payload.get("purpose"),"purpose",8000,True)
        rid="requirement:"+uuid.uuid4().hex;now=_now()
        with self._lock,self._connect() as db:
            if self._count(db,"cprp_requirements")>=self.max_requirements: raise CrossProjectResourcePlanningError("Resource requirement limit reached.",409)
            db.execute("INSERT INTO cprp_requirements VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(rid,program_id,project_id,resource_id,quantity,start,end,purpose,"requested",now,now,actor));self._event(db,program_id,"requirement.created",rid,{"projectId":project_id,"resourceId":resource_id,"quantity":quantity},actor)
        return {"ok":True,"requirement":self.get_requirement(rid)}

    def get_requirement(self, requirement_id: str):
        requirement_id=_id(requirement_id,"requirementId")
        with self._connect() as db: row=db.execute("SELECT * FROM cprp_requirements WHERE id=?",(requirement_id,)).fetchone()
        if not row: raise CrossProjectResourcePlanningError("Requirement not found.",404)
        return self._requirement_row(row)

    def list_requirements(self, program_id: str, limit: int = 5000):
        self._program(program_id);limit=max(1,min(int(limit),10000))
        with self._connect() as db: rows=db.execute("SELECT * FROM cprp_requirements WHERE program_id=? ORDER BY created_at,id LIMIT ?",(program_id,limit)).fetchall()
        return {"ok":True,"requirements":[self._requirement_row(x) for x in rows],"count":len(rows)}

    def set_requirement_status(self, program_id: str, requirement_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id);requirement_id=_id(requirement_id,"requirementId");status=str(payload.get("status") or "").strip().lower()
        if status not in REQUIREMENT_STATUSES: raise CrossProjectResourcePlanningError("Unsupported requirement status.")
        with self._lock,self._connect() as db:
            row=db.execute("SELECT * FROM cprp_requirements WHERE id=? AND program_id=?",(requirement_id,program_id)).fetchone()
            if not row: raise CrossProjectResourcePlanningError("Requirement not found.",404)
            db.execute("UPDATE cprp_requirements SET status=?,updated_at=?,actor=? WHERE id=?",(status,_now(),actor,requirement_id));self._event(db,program_id,"requirement.status",requirement_id,{"status":status},actor)
        return {"ok":True,"requirement":self.get_requirement(requirement_id)}

    def analyze_program(self, program_id: str):
        program=self._program(program_id);deps=self.list_dependencies(program_id,5000)["dependencies"];resources=self.list_resources(program_id,5000)["resources"];reqs=self.list_requirements(program_id,10000)["requirements"]
        unresolved=[d for d in deps if d["status"] in {"planned","active","blocked"}]
        blocked=[d for d in deps if d["status"]=="blocked"]
        resource_map={r["id"]:r for r in resources}; unavailable=[r for r in resources if r["state"] in {"unavailable","retired"}]
        open_reqs=[r for r in reqs if r["status"] in {"requested","acknowledged","blocked"}]
        conflicts=[]
        by_resource={}
        for req in open_reqs: by_resource.setdefault(req["resourceId"],[]).append(req)
        for resource_id,items in by_resource.items():
            resource=resource_map.get(resource_id)
            if not resource: continue
            total=sum(float(x["quantity"]) for x in items)
            capacity=float(resource["capacity"])
            if resource["state"]!="available" or total>capacity:
                conflicts.append({"resourceId":resource_id,"resourceState":resource["state"],"declaredCapacity":capacity,"requestedQuantity":total,"requirementIds":[x["id"] for x in items],"descriptiveOnly":True})
        project_ids=sorted(self._project_ids(program))
        graph={"nodes":[{"projectId":p} for p in project_ids],"edges":[{"id":d["id"],"fromProjectId":d["fromProjectId"],"toProjectId":d["toProjectId"],"dependencyType":d["dependencyType"],"status":d["status"]} for d in deps]}
        analysis={"programId":program_id,"projectCount":len(project_ids),"dependencyCount":len(deps),"unresolvedDependencyCount":len(unresolved),"blockedDependencyCount":len(blocked),"resourceCount":len(resources),"unavailableResourceCount":len(unavailable),"requirementCount":len(reqs),"openRequirementCount":len(open_reqs),"capacityConflictCount":len(conflicts),"capacityConflicts":conflicts,"dependencyGraph":graph,"descriptiveOnly":True,"automaticScheduling":False,"automaticResourceAllocation":False,"automaticProjectRanking":False}
        analysis["digest"]=_sha(analysis)
        return {"ok":True,"analysis":analysis}

    def create_plan(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id);title=_text(payload.get("title"),"title",1000,True);description=_text(payload.get("description"),"description",8000);assumptions=_json(payload.get("assumptions") or {},"assumptions")
        analysis=self.analyze_program(program_id)["analysis"];plan_id="resource-plan:"+uuid.uuid4().hex;now=_now()
        with self._lock,self._connect() as db:
            if self._count(db,"cprp_plans")>=self.max_plans: raise CrossProjectResourcePlanningError("Resource-plan limit reached.",409)
            db.execute("INSERT INTO cprp_plans VALUES(?,?,?,?,?,?,?,?,?,?,?)",(plan_id,program_id,title,description,"draft",json.dumps(assumptions,sort_keys=True),analysis["digest"],0,now,now,actor));self._event(db,program_id,"plan.created",plan_id,{"analysisDigest":analysis["digest"]},actor)
        return {"ok":True,"plan":self.get_plan(plan_id),"analysis":analysis}

    def get_plan(self, plan_id: str):
        plan_id=_id(plan_id,"planId")
        with self._connect() as db: row=db.execute("SELECT * FROM cprp_plans WHERE id=?",(plan_id,)).fetchone()
        if not row: raise CrossProjectResourcePlanningError("Resource plan not found.",404)
        return self._plan_row(row)

    def list_plans(self, program_id: str, limit: int = 1000):
        self._program(program_id);limit=max(1,min(int(limit),5000))
        with self._connect() as db: rows=db.execute("SELECT * FROM cprp_plans WHERE program_id=? ORDER BY created_at,id LIMIT ?",(program_id,limit)).fetchall()
        return {"ok":True,"plans":[self._plan_row(x) for x in rows],"count":len(rows)}

    def evaluate_plan(self, plan_id: str):
        plan=self.get_plan(plan_id);analysis=self.analyze_program(plan["programId"])["analysis"]
        blockers=[]
        if analysis["blockedDependencyCount"]: blockers.append({"code":"blocked-dependencies","count":analysis["blockedDependencyCount"]})
        if analysis["capacityConflictCount"]: blockers.append({"code":"capacity-conflicts","count":analysis["capacityConflictCount"]})
        if analysis["unavailableResourceCount"]: blockers.append({"code":"unavailable-resources","count":analysis["unavailableResourceCount"]})
        return {"ok":True,"planId":plan_id,"state":plan["state"],"analysis":analysis,"blockers":blockers,"procedurallyClear":len(blockers)==0,"scientificValidityDetermined":False,"automaticApproval":False}

    def transition_plan(self, plan_id: str, payload: dict[str, Any], actor: str = "human"):
        plan=self.get_plan(plan_id);target=str(payload.get("targetState") or "").strip().lower();reason=_text(payload.get("reason"),"reason",8000,True);authorized=payload.get("humanAuthorization") is True
        if target not in PLAN_STATES: raise CrossProjectResourcePlanningError("Unsupported plan state.")
        allowed={"draft":{"review","archived"},"review":{"draft","approved","archived"},"approved":{"review","archived"},"archived":set()}
        if target not in allowed.get(plan["state"],set()): raise CrossProjectResourcePlanningError(f"Invalid plan transition {plan['state']} -> {target}.",409)
        if not authorized: raise CrossProjectResourcePlanningError("Explicit humanAuthorization=true is required for plan transitions.",409)
        if target=="approved":
            evaluation=self.evaluate_plan(plan_id)
            if not evaluation["procedurallyClear"]: raise CrossProjectResourcePlanningError("Plan has unresolved procedural blockers and cannot be approved.",409)
        now=_now();tid="plan-transition:"+uuid.uuid4().hex
        with self._lock,self._connect() as db:
            db.execute("UPDATE cprp_plans SET state=?,human_authorization=1,updated_at=?,actor=? WHERE id=?",(target,now,actor,plan_id));db.execute("INSERT INTO cprp_transitions VALUES(?,?,?,?,?,?,?,?)",(tid,plan_id,plan["state"],target,reason,1,now,actor));self._event(db,plan["programId"],"plan.transition",plan_id,{"fromState":plan["state"],"toState":target,"reason":reason},actor)
        return {"ok":True,"plan":self.get_plan(plan_id)}

    def command_center(self, program_id: str):
        program=self._program(program_id);analysis=self.analyze_program(program_id)["analysis"];plans=self.list_plans(program_id,1000)["plans"]
        return {"ok":True,"version":VERSION,"program":{"id":program["id"],"title":program["title"],"state":program["state"]},"analysis":analysis,"plans":plans,"boundary":BOUNDARY}

    def _manifest_payload(self, program_id: str):
        program=self._program(program_id);deps=self.list_dependencies(program_id,5000)["dependencies"];resources=self.list_resources(program_id,5000)["resources"];reqs=self.list_requirements(program_id,10000)["requirements"];plans=self.list_plans(program_id,5000)["plans"];analysis=self.analyze_program(program_id)["analysis"]
        return {"schema":MANIFEST_SCHEMA,"version":VERSION,"program":{"id":program["id"],"state":program["state"]},"dependencies":deps,"resources":resources,"requirements":reqs,"plans":plans,"analysis":analysis,"boundary":BOUNDARY}

    def manifest(self, program_id: str):
        payload=self._manifest_payload(program_id);return {"ok":True,"manifest":payload,"digest":_sha(payload)}

    def verify_manifest(self, payload: dict[str, Any]):
        manifest=payload.get("manifest");digest=str(payload.get("digest") or "")
        if not isinstance(manifest,dict) or not digest: raise CrossProjectResourcePlanningError("manifest and digest are required.")
        actual=_sha(manifest);return {"ok":True,"valid":actual==digest,"expectedDigest":digest,"actualDigest":actual}

    def snapshot(self, program_id: str, payload: dict[str, Any], actor: str = "human"):
        self._program(program_id)
        if payload.get("humanAuthorization") is not True: raise CrossProjectResourcePlanningError("Explicit humanAuthorization=true is required to freeze a planning snapshot.",409)
        body=self._manifest_payload(program_id);digest=_sha(body);sid="planning-snapshot:"+uuid.uuid4().hex;now=_now()
        with self._lock,self._connect() as db:
            if self._count(db,"cprp_snapshots")>=self.max_snapshots: raise CrossProjectResourcePlanningError("Snapshot limit reached.",409)
            db.execute("INSERT INTO cprp_snapshots VALUES(?,?,?,?,?,?)",(sid,program_id,json.dumps(body,sort_keys=True),digest,now,actor));self._event(db,program_id,"snapshot.frozen",sid,{"digest":digest},actor)
        return {"ok":True,"snapshot":{"schema":SNAPSHOT_SCHEMA,"version":VERSION,"id":sid,"programId":program_id,"digest":digest,"createdAt":now,"actor":actor}}

    def get_snapshot(self, snapshot_id: str):
        snapshot_id=_id(snapshot_id,"snapshotId")
        with self._connect() as db: row=db.execute("SELECT * FROM cprp_snapshots WHERE id=?",(snapshot_id,)).fetchone()
        if not row: raise CrossProjectResourcePlanningError("Snapshot not found.",404)
        return {"ok":True,"snapshot":{"schema":SNAPSHOT_SCHEMA,"version":VERSION,"id":row["id"],"programId":row["program_id"],"body":json.loads(row["snapshot_json"]),"digest":row["digest"],"createdAt":row["created_at"],"actor":row["actor"]}}

    def timeline(self, program_id: str, limit: int = 500):
        self._program(program_id);limit=max(1,min(int(limit),5000))
        with self._connect() as db: rows=db.execute("SELECT * FROM cprp_events WHERE program_id=? ORDER BY seq DESC LIMIT ?",(program_id,limit)).fetchall()
        return {"ok":True,"events":[{"seq":x["seq"],"kind":x["kind"],"objectId":x["object_id"],"payload":json.loads(x["payload_json"]),"createdAt":x["created_at"],"actor":x["actor"]} for x in rows],"count":len(rows)}
