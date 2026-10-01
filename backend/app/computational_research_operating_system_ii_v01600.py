from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.160.0"
PROJECT_SCHEMA = "sc-lab-computational-research-os-project/0.160.0"
OBJECT_SCHEMA = "sc-lab-research-lifecycle-object-link/0.160.0"
PACKAGE_SCHEMA = "sc-lab-reproducible-research-package/0.160.0"
HANDOFF_SCHEMA = "sc-lab-research-os-handoff/0.160.0"
MANIFEST_SCHEMA = "sc-lab-computational-research-os-manifest/0.160.0"

STAGES = (
    "question",
    "protocol",
    "notebook",
    "workflow",
    "campaign",
    "compute",
    "results",
    "synthesis",
    "replication",
    "review",
    "publication-package",
    "archived",
)

OBJECT_TYPES = {
    "research-question",
    "protocol",
    "notebook",
    "workflow",
    "dataset",
    "model",
    "campaign",
    "execution-plan",
    "result",
    "claim",
    "evidence",
    "cross-study-workspace",
    "replication-network",
    "review-dossier",
    "publication-packet",
    "reproducibility-package",
}

OBJECT_STATUS = {"active", "stale", "superseded", "withdrawn"}

STAGE_REQUIREMENTS: dict[str, tuple[tuple[str, ...], ...]] = {
    "protocol": (("protocol",),),
    "notebook": (("protocol",), ("notebook",)),
    "workflow": (("protocol",), ("notebook",), ("workflow",)),
    "campaign": (("workflow",), ("campaign",)),
    "compute": (("campaign", "workflow"), ("execution-plan", "campaign")),
    "results": (("result",),),
    "synthesis": (("result",), ("cross-study-workspace",)),
    "replication": (("cross-study-workspace",), ("replication-network",)),
    "review": (("review-dossier",),),
    "publication-package": (("review-dossier",),),
}

BOUNDARY = (
    "Computational Research Operating System II coordinates research lifecycle state, references, dependency integrity, "
    "reproducible package composition and explicit handoffs. It does not execute scientific workloads, infer scientific "
    "validity, infer causality, judge replication success, publish automatically, or advance lifecycle stages without "
    "explicit human authorization. Platform Core remains canonical object authority and Workspace remains execution authority."
)


class ResearchOSError(ValueError):
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
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise ResearchOSError(f"Invalid {label}.")
    return text


def _text(value: Any, label: str, maximum: int = 12000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ResearchOSError(f"{label} is required.")
    if len(text) > maximum:
        raise ResearchOSError(f"{label} exceeds {maximum} characters.")
    return text


def _json(value: Any, label: str, maximum_bytes: int = 1_000_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise ResearchOSError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise ResearchOSError(f"{label} exceeds payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


class ComputationalResearchOperatingSystemIIManager:
    def __init__(
        self,
        db_path: str,
        batch_campaigns: Any | None = None,
        cross_study: Any | None = None,
        replication_network: Any | None = None,
        review_gate: Any | None = None,
        persistent_disk_mounted: bool = False,
        max_projects: int = 10000,
        max_object_links: int = 250000,
        max_packages: int = 50000,
        history_limit: int = 500000,
    ):
        self.db_path = str(db_path)
        self.batch_campaigns = batch_campaigns
        self.cross_study = cross_study
        self.replication_network = replication_network
        self.review_gate = review_gate
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_projects = max(1, int(max_projects))
        self.max_object_links = max(1, int(max_object_links))
        self.max_packages = max(1, int(max_packages))
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

        db = sqlite3.connect(
            self.db_path,
            timeout=30,
            check_same_thread=False,
            factory=_ClosingConnection,
        )
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self):
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS os_projects(
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    question TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS os_objects(
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    object_type TEXT NOT NULL,
                    object_ref TEXT NOT NULL,
                    source_layer TEXT NOT NULL,
                    role TEXT NOT NULL,
                    expected_digest TEXT NOT NULL,
                    observed_digest TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    linked_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    UNIQUE(project_id, object_type, object_ref, role)
                );
                CREATE TABLE IF NOT EXISTS os_transitions(
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    from_stage TEXT NOT NULL,
                    to_stage TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    human_authorization INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS os_packages(
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    package_json TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS os_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                """
            )

    def _count(self, db: sqlite3.Connection, table: str) -> int:
        return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    def _event(self, db, project_id, kind, object_id, payload, actor):
        db.execute(
            "INSERT INTO os_events(project_id,kind,object_id,payload_json,created_at,actor) VALUES(?,?,?,?,?,?)",
            (project_id, kind, object_id, json.dumps(payload, sort_keys=True), _now(), actor or "human"),
        )
        excess = int(db.execute("SELECT COUNT(*) FROM os_events").fetchone()[0]) - self.history_limit
        if excess > 0:
            db.execute("DELETE FROM os_events WHERE seq IN (SELECT seq FROM os_events ORDER BY seq LIMIT ?)", (excess,))

    def policies(self):
        return {
            "version": VERSION,
            "stages": list(STAGES),
            "objectTypes": sorted(OBJECT_TYPES),
            "referenceFirst": True,
            "platformCoreCanonicalAuthority": True,
            "workspaceExecutionAuthority": True,
            "labLifecycleCoordinationAuthority": True,
            "automaticStageAdvancement": False,
            "automaticExecution": False,
            "automaticScientificValidity": False,
            "automaticCausalInference": False,
            "automaticReplicationJudgment": False,
            "automaticPublication": False,
            "humanAuthorizationRequired": True,
            "boundary": BOUNDARY,
        }

    def health(self):
        return {
            "ok": True,
            "version": VERSION,
            "computationalResearchOperatingSystemII": True,
            "unifiedResearchProjectGraph": True,
            "lifecycleStateMachine": True,
            "researchCommandCenter": True,
            "crossModuleObjectResolution": True,
            "researchPackageComposer": True,
            "dependencyIntegrityValidation": True,
            "humanAuthorizationLayer": True,
            "operatingSystemHealthContract": True,
            "referenceFirst": True,
            "automaticStageAdvancement": False,
            "automaticExecution": False,
            "automaticScientificValidity": False,
            "automaticPublication": False,
            "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local",
            "boundary": BOUNDARY,
        }

    def create_project(self, payload: dict[str, Any], actor: str = "human"):
        title = _text(payload.get("title"), "title", 600, True)
        question = _text(payload.get("question"), "question", 16000, True)
        objective = _text(payload.get("objective"), "objective", 16000)
        project_id = _id(payload.get("projectId") or ("research:" + uuid.uuid4().hex), "projectId")
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "os_projects") >= self.max_projects:
                raise ResearchOSError("Research OS project limit reached.", 409)
            if db.execute("SELECT id FROM os_projects WHERE id=?", (project_id,)).fetchone():
                raise ResearchOSError("Research OS project already exists.", 409)
            db.execute(
                "INSERT INTO os_projects VALUES(?,?,?,?,?,?,?,?)",
                (project_id, title, question, objective, "question", now, now, actor),
            )
            self._event(db, project_id, "project.created", project_id, {"stage": "question"}, actor)
        return {"ok": True, "project": self.get_project(project_id)}

    @staticmethod
    def _project_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": PROJECT_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "title": row["title"],
            "question": row["question"],
            "objective": row["objective"],
            "stage": row["stage"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    @staticmethod
    def _object_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": OBJECT_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "projectId": row["project_id"],
            "objectType": row["object_type"],
            "objectRef": row["object_ref"],
            "sourceLayer": row["source_layer"],
            "role": row["role"],
            "expectedDigest": row["expected_digest"],
            "observedDigest": row["observed_digest"],
            "status": row["status"],
            "metadata": json.loads(row["metadata_json"]),
            "linkedAt": row["linked_at"],
            "updatedAt": row["updated_at"],
            "actor": row["actor"],
        }

    def get_project(self, project_id: str):
        project_id = _id(project_id, "project_id")
        with self._connect() as db:
            row = db.execute("SELECT * FROM os_projects WHERE id=?", (project_id,)).fetchone()
            if not row:
                raise ResearchOSError("Research OS project not found.", 404)
            objects = db.execute("SELECT * FROM os_objects WHERE project_id=? ORDER BY linked_at,id", (project_id,)).fetchall()
            packages = db.execute("SELECT id,digest,created_at,actor FROM os_packages WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        out = self._project_row(row)
        out["objects"] = [self._object_row(x) for x in objects]
        out["packages"] = [
            {"id": x["id"], "digest": x["digest"], "createdAt": x["created_at"], "actor": x["actor"]}
            for x in packages
        ]
        return out

    def list_projects(self, include_archived: bool = False, limit: int = 100):
        limit = max(1, min(int(limit), 1000))
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM os_projects WHERE (?=1 OR stage<>'archived') ORDER BY updated_at DESC LIMIT ?",
                (1 if include_archived else 0, limit),
            ).fetchall()
        return {"ok": True, "projects": [self._project_row(x) for x in rows], "count": len(rows)}

    def _verify_known_reference(self, object_type: str, object_ref: str):
        try:
            if object_type == "campaign" and self.batch_campaigns is not None:
                self.batch_campaigns.get(object_ref)
            elif object_type == "cross-study-workspace" and self.cross_study is not None:
                self.cross_study.get_workspace(object_ref)
            elif object_type == "replication-network" and self.replication_network is not None:
                self.replication_network.get_network(object_ref)
            elif object_type == "review-dossier" and self.review_gate is not None:
                self.review_gate.get_dossier(object_ref)
        except Exception as exc:
            raise ResearchOSError(f"Referenced {object_type} could not be resolved: {object_ref}.", 409) from exc

    def link_object(self, project_id: str, payload: dict[str, Any], actor: str = "human"):
        project = self.get_project(project_id)
        if project["stage"] == "archived":
            raise ResearchOSError("Archived projects cannot accept new object links.", 409)
        object_type = str(payload.get("objectType") or "").strip().lower()
        if object_type not in OBJECT_TYPES:
            raise ResearchOSError(f"Unsupported objectType: {object_type}.")
        object_ref = _text(payload.get("objectRef"), "objectRef", 500, True)
        source_layer = _text(payload.get("sourceLayer") or "external", "sourceLayer", 200, True)
        role = _text(payload.get("role") or "primary", "role", 200, True)
        expected = _text(payload.get("expectedDigest"), "expectedDigest", 128)
        observed = _text(payload.get("observedDigest"), "observedDigest", 128)
        metadata = _json(payload.get("metadata") or {}, "metadata", 500000)
        self._verify_known_reference(object_type, object_ref)
        status = "stale" if expected and observed and expected != observed else "active"
        oid = "link:" + uuid.uuid4().hex
        now = _now()
        with self._lock, self._connect() as db:
            if self._count(db, "os_objects") >= self.max_object_links:
                raise ResearchOSError("Research OS object-link limit reached.", 409)
            try:
                db.execute(
                    "INSERT INTO os_objects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (oid, project_id, object_type, object_ref, source_layer, role, expected, observed, status, json.dumps(metadata, sort_keys=True), now, now, actor),
                )
            except sqlite3.IntegrityError as exc:
                raise ResearchOSError("That research object is already linked in this role.", 409) from exc
            self._event(db, project_id, "object.linked", oid, {"objectType": object_type, "objectRef": object_ref, "status": status}, actor)
        return {"ok": True, "object": next(x for x in self.get_project(project_id)["objects"] if x["id"] == oid)}

    def observe_object(self, project_id: str, object_id: str, payload: dict[str, Any], actor: str = "human"):
        self.get_project(project_id)
        object_id = _id(object_id, "object_id")
        observed = _text(payload.get("observedDigest"), "observedDigest", 128, True)
        status_override = str(payload.get("status") or "").strip().lower()
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM os_objects WHERE id=? AND project_id=?", (object_id, project_id)).fetchone()
            if not row:
                raise ResearchOSError("Research object link not found.", 404)
            status = "stale" if row["expected_digest"] and row["expected_digest"] != observed else "active"
            if status_override:
                if status_override not in OBJECT_STATUS:
                    raise ResearchOSError("Unsupported object status.")
                status = status_override
            now = _now()
            db.execute("UPDATE os_objects SET observed_digest=?,status=?,updated_at=?,actor=? WHERE id=?", (observed, status, now, actor, object_id))
            self._event(db, project_id, "object.observed", object_id, {"observedDigest": observed, "status": status}, actor)
        return {"ok": True, "object": next(x for x in self.get_project(project_id)["objects"] if x["id"] == object_id)}

    @staticmethod
    def _requirements_for(stage: str) -> list[list[str]]:
        return [list(group) for group in STAGE_REQUIREMENTS.get(stage, ())]

    def validate_project(self, project_id: str, target_stage: str | None = None):
        project = self.get_project(project_id)
        target = str(target_stage or project["stage"]).strip().lower()
        if target not in STAGES:
            raise ResearchOSError(f"Unsupported lifecycle stage: {target}.")
        active_types = {x["objectType"] for x in project["objects"] if x["status"] == "active"}
        requirements = self._requirements_for(target)
        missing = [group for group in requirements if not any(kind in active_types for kind in group)]
        stale = [x for x in project["objects"] if x["status"] == "stale"]
        withdrawn = [x for x in project["objects"] if x["status"] == "withdrawn"]
        blockers: list[dict[str, Any]] = []
        for group in missing:
            blockers.append({"type": "missing-object", "acceptableObjectTypes": group})
        for obj in stale:
            blockers.append({"type": "stale-object", "objectId": obj["id"], "objectType": obj["objectType"], "objectRef": obj["objectRef"]})
        for obj in withdrawn:
            blockers.append({"type": "withdrawn-object", "objectId": obj["id"], "objectType": obj["objectType"], "objectRef": obj["objectRef"]})
        review_status = None
        if target == "publication-package" and self.review_gate is not None:
            reviews = [x for x in project["objects"] if x["objectType"] == "review-dossier" and x["status"] == "active"]
            if reviews:
                try:
                    dossier = self.review_gate.get_dossier(reviews[-1]["objectRef"])
                    review_status = dossier.get("status")
                    if review_status != "publication-ready":
                        blockers.append({"type": "review-gate", "requiredStatus": "publication-ready", "observedStatus": review_status})
                except Exception:
                    blockers.append({"type": "review-gate", "requiredStatus": "publication-ready", "observedStatus": "unresolved"})
        return {
            "ok": True,
            "projectId": project_id,
            "targetStage": target,
            "proceduralReady": len(blockers) == 0,
            "requiredObjectGroups": requirements,
            "activeObjectTypes": sorted(active_types),
            "reviewDossierStatus": review_status,
            "blockingReasons": blockers,
            "scientificValidityDetermined": False,
            "replicationSuccessDetermined": False,
            "causalityDetermined": False,
            "boundary": BOUNDARY,
        }

    def transition(self, project_id: str, payload: dict[str, Any], actor: str = "human"):
        project = self.get_project(project_id)
        target = str(payload.get("targetStage") or "").strip().lower()
        if target not in STAGES:
            raise ResearchOSError(f"Unsupported lifecycle stage: {target}.")
        if project["stage"] == "archived":
            raise ResearchOSError("Archived projects cannot transition.", 409)
        if target == "archived":
            return self.archive(project_id, actor, _text(payload.get("reason") or "Archived by human operator.", "reason", 12000, True))
        human = bool(payload.get("humanAuthorization", False))
        if not human:
            raise ResearchOSError("Explicit humanAuthorization=true is required for lifecycle transitions.", 409)
        reason = _text(payload.get("reason"), "reason", 12000, True)
        current_index = STAGES.index(project["stage"])
        target_index = STAGES.index(target)
        if target_index == current_index:
            raise ResearchOSError("Project is already at that lifecycle stage.", 409)
        if target_index > current_index + 1:
            raise ResearchOSError("Lifecycle stages must advance one stage at a time.", 409)
        validation = self.validate_project(project_id, target)
        if target_index > current_index and not validation["proceduralReady"]:
            raise ResearchOSError("Lifecycle prerequisites are incomplete; inspect validation blockers.", 409)
        now = _now()
        tid = "transition:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute("UPDATE os_projects SET stage=?,updated_at=? WHERE id=?", (target, now, project_id))
            db.execute("INSERT INTO os_transitions VALUES(?,?,?,?,?,?,?,?)", (tid, project_id, project["stage"], target, reason, 1, now, actor))
            self._event(db, project_id, "lifecycle.transition", tid, {"from": project["stage"], "to": target, "humanAuthorization": True}, actor)
        return {"ok": True, "project": self.get_project(project_id), "validation": validation}

    def command_center(self, project_id: str):
        project = self.get_project(project_id)
        validation = self.validate_project(project_id, project["stage"])
        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for obj in project["objects"]:
            by_type[obj["objectType"]] = by_type.get(obj["objectType"], 0) + 1
            by_status[obj["status"]] = by_status.get(obj["status"], 0) + 1
        next_stage = None
        idx = STAGES.index(project["stage"])
        if idx + 1 < len(STAGES) and STAGES[idx + 1] != "archived":
            next_stage = STAGES[idx + 1]
        next_validation = self.validate_project(project_id, next_stage) if next_stage else None
        return {
            "ok": True,
            "project": {k: project[k] for k in ("id", "title", "question", "objective", "stage", "createdAt", "updatedAt")},
            "objectCountsByType": by_type,
            "objectCountsByStatus": by_status,
            "currentStageValidation": validation,
            "nextStage": next_stage,
            "nextStageValidation": next_validation,
            "packageCount": len(project["packages"]),
            "automaticActionsTaken": 0,
            "humanControl": True,
            "boundary": BOUNDARY,
        }

    def compose_package(self, project_id: str, payload: dict[str, Any], actor: str = "human"):
        project = self.get_project(project_id)
        if project["stage"] != "publication-package":
            raise ResearchOSError("Project must be at publication-package stage before composing a research package.", 409)
        if not bool(payload.get("humanAuthorization", False)):
            raise ResearchOSError("Explicit humanAuthorization=true is required to compose the final research package.", 409)
        validation = self.validate_project(project_id, "publication-package")
        if not validation["proceduralReady"]:
            raise ResearchOSError("Publication-package prerequisites are incomplete.", 409)
        review_packet = None
        review_refs = [x for x in project["objects"] if x["objectType"] == "review-dossier" and x["status"] == "active"]
        if review_refs and self.review_gate is not None:
            try:
                review_packet = self.review_gate.publication_packet(review_refs[-1]["objectRef"]).get("packet")
            except Exception as exc:
                raise ResearchOSError("Review-gate publication packet could not be prepared.", 409) from exc
        package = {
            "schema": PACKAGE_SCHEMA,
            "version": VERSION,
            "project": {k: project[k] for k in ("id", "title", "question", "objective", "stage", "createdAt", "updatedAt")},
            "objectReferences": project["objects"],
            "reviewGatePacket": review_packet,
            "validation": validation,
            "referenceFirst": True,
            "embeddedRestrictedData": False,
            "automaticPublication": False,
            "automaticScientificValidity": False,
            "requiresExplicitDownstreamAction": True,
            "generatedAt": _now(),
            "boundary": BOUNDARY,
        }
        package_id = "package:" + uuid.uuid4().hex
        digest = _sha(package)
        with self._lock, self._connect() as db:
            if self._count(db, "os_packages") >= self.max_packages:
                raise ResearchOSError("Research package limit reached.", 409)
            db.execute("INSERT INTO os_packages VALUES(?,?,?,?,?,?)", (package_id, project_id, json.dumps(package, sort_keys=True), digest, _now(), actor))
            self._event(db, project_id, "package.composed", package_id, {"digest": digest}, actor)
        return {"ok": True, "packageId": package_id, "digest": digest, "package": package}

    def get_package(self, package_id: str):
        package_id = _id(package_id, "package_id")
        with self._connect() as db:
            row = db.execute("SELECT * FROM os_packages WHERE id=?", (package_id,)).fetchone()
        if not row:
            raise ResearchOSError("Research package not found.", 404)
        return {"ok": True, "packageId": row["id"], "projectId": row["project_id"], "digest": row["digest"], "createdAt": row["created_at"], "actor": row["actor"], "package": json.loads(row["package_json"])}

    def prepare_handoff(self, package_id: str, payload: dict[str, Any], actor: str = "human"):
        pkg = self.get_package(package_id)
        if not bool(payload.get("humanAuthorization", False)):
            raise ResearchOSError("Explicit humanAuthorization=true is required to prepare a downstream handoff.", 409)
        target = _text(payload.get("targetProduct") or "sustainable-catalyst-publication-studio", "targetProduct", 300, True)
        handoff = {
            "schema": HANDOFF_SCHEMA,
            "version": VERSION,
            "packageId": package_id,
            "packageDigest": pkg["digest"],
            "projectId": pkg["projectId"],
            "targetProduct": target,
            "executionRequested": False,
            "publicationRequested": False,
            "requiresExplicitUserAction": True,
            "humanAuthorization": True,
            "preparedAt": _now(),
            "boundary": BOUNDARY,
        }
        handoff["digest"] = _sha(handoff)
        with self._lock, self._connect() as db:
            self._event(db, pkg["projectId"], "handoff.prepared", package_id, {"targetProduct": target, "digest": handoff["digest"]}, actor)
        return {"ok": True, "handoff": handoff}

    def manifest(self, project_id: str):
        project = self.get_project(project_id)
        validation = self.validate_project(project_id, project["stage"])
        with self._connect() as db:
            transitions = db.execute("SELECT * FROM os_transitions WHERE project_id=? ORDER BY created_at,id", (project_id,)).fetchall()
            packages = db.execute("SELECT id,digest,created_at FROM os_packages WHERE project_id=? ORDER BY created_at,id", (project_id,)).fetchall()
        payload = {
            "schema": MANIFEST_SCHEMA,
            "version": VERSION,
            "project": project,
            "validation": validation,
            "transitions": [
                {
                    "id": x["id"],
                    "fromStage": x["from_stage"],
                    "toStage": x["to_stage"],
                    "reason": x["reason"],
                    "humanAuthorization": bool(x["human_authorization"]),
                    "createdAt": x["created_at"],
                    "actor": x["actor"],
                }
                for x in transitions
            ],
            "packages": [{"id": x["id"], "digest": x["digest"], "createdAt": x["created_at"]} for x in packages],
            "boundary": BOUNDARY,
        }
        return {"ok": True, "manifest": payload, "digest": _sha(payload)}

    def verify_manifest(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            raise ResearchOSError("Manifest verification payload must be an object.")
        manifest = payload.get("manifest")
        digest = str(payload.get("digest") or "")
        if not isinstance(manifest, dict) or not digest:
            raise ResearchOSError("manifest and digest are required.")
        actual = _sha(manifest)
        return {"ok": True, "verified": actual == digest, "expected": digest, "actual": actual}

    def timeline(self, project_id: str, limit: int = 500):
        self.get_project(project_id)
        limit = max(1, min(int(limit), 5000))
        with self._connect() as db:
            rows = db.execute("SELECT * FROM os_events WHERE project_id=? ORDER BY seq DESC LIMIT ?", (project_id, limit)).fetchall()
        return {
            "ok": True,
            "projectId": project_id,
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

    def archive(self, project_id: str, actor: str = "human", reason: str = "Archived by human operator."):
        project = self.get_project(project_id)
        if project["stage"] == "archived":
            return {"ok": True, "project": project}
        now = _now()
        tid = "transition:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute("UPDATE os_projects SET stage='archived',updated_at=? WHERE id=?", (now, project_id))
            db.execute("INSERT INTO os_transitions VALUES(?,?,?,?,?,?,?,?)", (tid, project_id, project["stage"], "archived", reason, 1, now, actor))
            self._event(db, project_id, "project.archived", tid, {"from": project["stage"], "reason": reason}, actor)
        return {"ok": True, "project": self.get_project(project_id)}
