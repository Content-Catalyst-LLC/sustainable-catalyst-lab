from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import statistics
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.157.0"
STUDY_SCHEMA = "sc-lab-cross-study-record/0.157.0"
STUDY_REVISION_SCHEMA = "sc-lab-cross-study-revision/0.157.0"
EFFECT_SCHEMA = "sc-lab-study-effect-record/0.157.0"
WORKSPACE_SCHEMA = "sc-lab-meta-experiment-workspace/0.157.0"
SYNTHESIS_SCHEMA = "sc-lab-cross-study-synthesis/0.157.0"
MANIFEST_SCHEMA = "sc-lab-cross-study-replication-manifest/0.157.0"
HANDOFF_SCHEMA = "sc-lab-replication-campaign-handoff/0.157.0"

STUDY_TYPES = {
    "primary",
    "direct-replication",
    "conceptual-replication",
    "methodological-replication",
    "secondary-analysis",
}
RELATION_TYPES = {
    "anchor",
    "direct-replication",
    "conceptual-replication",
    "methodological-replication",
    "related-study",
}
INCLUSION_STATES = {"pending", "included", "excluded"}
ASSESSMENT_STATES = {"unreviewed", "consistent", "inconsistent", "mixed", "not-assessable"}
BOUNDARY = (
    "Cross-study synthesis is descriptive and provenance-preserving. It does not automatically declare replication success or failure, "
    "establish causality, infer study independence, correct publication bias, establish statistical or scientific significance, or establish scientific validity. "
    "Human scientific review remains required for interpretation and consequential conclusions."
)


class CrossStudyReplicationError(ValueError):
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
        raise CrossStudyReplicationError(f"Invalid {label}.")
    return text


def _text(value: Any, label: str, maximum: int = 8000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise CrossStudyReplicationError(f"{label} is required.")
    if len(text) > maximum:
        raise CrossStudyReplicationError(f"{label} exceeds {maximum} characters.")
    return text


def _json(value: Any, label: str, maximum_bytes: int = 2_000_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise CrossStudyReplicationError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise CrossStudyReplicationError(f"{label} exceeds the payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


def _number(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise CrossStudyReplicationError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise CrossStudyReplicationError(f"{label} must be finite.")
    return out


def _positive(value: Any, label: str) -> float:
    out = _number(value, label)
    if out <= 0:
        raise CrossStudyReplicationError(f"{label} must be > 0.")
    return out


def _study_definition(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CrossStudyReplicationError("Study payload must be an object.")
    study_type = str(payload.get("studyType") or "primary").strip().lower().replace("_", "-")
    if study_type not in STUDY_TYPES:
        raise CrossStudyReplicationError(f"Unsupported study type: {study_type}.")
    return {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "title": _text(payload.get("title"), "title", 600, True),
        "studyType": study_type,
        "sourceRef": _text(payload.get("sourceRef"), "sourceRef", 500, False),
        "protocolRef": _text(payload.get("protocolRef"), "protocolRef", 500, False),
        "campaignRef": _text(payload.get("campaignRef"), "campaignRef", 500, False),
        "parentStudyRef": _text(payload.get("parentStudyRef"), "parentStudyRef", 500, False),
        "design": _text(payload.get("design"), "design", 1000, False),
        "population": _text(payload.get("population"), "population", 4000, False),
        "intervention": _text(payload.get("intervention"), "intervention", 4000, False),
        "comparator": _text(payload.get("comparator"), "comparator", 4000, False),
        "outcome": _text(payload.get("outcome"), "outcome", 4000, False),
        "context": _json(payload.get("context") or {}, "context", 500_000),
        "methodNotes": _text(payload.get("methodNotes"), "methodNotes", 12000, False),
        "independenceDocumented": bool(payload.get("independenceDocumented", False)),
        "independenceEvidence": _text(payload.get("independenceEvidence"), "independenceEvidence", 5000, False),
        "automaticReplicationJudgment": False,
        "causalInference": False,
        "humanReviewRequired": True,
    }


def _effect_record(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CrossStudyReplicationError("Effect payload must be an object.")
    estimate = _number(payload.get("estimate"), "estimate")
    if payload.get("variance") is not None:
        variance = _positive(payload.get("variance"), "variance")
        standard_error = math.sqrt(variance)
    else:
        standard_error = _positive(payload.get("standardError"), "standardError")
        variance = standard_error * standard_error
    sample_size = payload.get("sampleSize")
    if sample_size is not None:
        sample_size = int(sample_size)
        if sample_size <= 0:
            raise CrossStudyReplicationError("sampleSize must be > 0.")
    return {
        "schema": EFFECT_SCHEMA,
        "version": VERSION,
        "metricKey": _text(payload.get("metricKey"), "metricKey", 200, True),
        "effectMeasure": _text(payload.get("effectMeasure"), "effectMeasure", 200, True),
        "estimate": estimate,
        "standardError": standard_error,
        "variance": variance,
        "sampleSize": sample_size,
        "unit": _text(payload.get("unit"), "unit", 100, False),
        "outcomeDirection": str(payload.get("outcomeDirection") or "as-reported").strip().lower()[:80],
        "extractionSource": _text(payload.get("extractionSource"), "extractionSource", 1000, True),
        "notes": _text(payload.get("notes"), "notes", 5000, False),
        "harmonized": bool(payload.get("harmonized", False)),
        "harmonizationRef": _text(payload.get("harmonizationRef"), "harmonizationRef", 500, False),
        "immutable": True,
    }


def _ci(estimate: float, se: float, z: float = 1.96) -> dict[str, float]:
    return {"lower": estimate - z * se, "upper": estimate + z * se}


def _meta_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    if len(records) < 2:
        raise CrossStudyReplicationError("At least two included effect records are required for synthesis.")
    variances = [float(r["variance"]) for r in records]
    estimates = [float(r["estimate"]) for r in records]
    weights = [1.0 / v for v in variances]
    sum_w = sum(weights)
    fixed = sum(w * y for w, y in zip(weights, estimates)) / sum_w
    q = sum(w * ((y - fixed) ** 2) for w, y in zip(weights, estimates))
    df = len(records) - 1
    c = sum_w - (sum(w * w for w in weights) / sum_w)
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    random_weights = [1.0 / (v + tau2) for v in variances]
    sum_rw = sum(random_weights)
    random_estimate = sum(w * y for w, y in zip(random_weights, estimates)) / sum_rw
    fixed_se = math.sqrt(1.0 / sum_w)
    random_se = math.sqrt(1.0 / sum_rw)
    i2 = max(0.0, ((q - df) / q) * 100.0) if q > 0 else 0.0
    prediction_se = math.sqrt(max(0.0, tau2 + random_se * random_se))
    return {
        "k": len(records),
        "fixedEffect": {"estimate": fixed, "standardError": fixed_se, "confidenceInterval95": _ci(fixed, fixed_se)},
        "randomEffects": {"estimate": random_estimate, "standardError": random_se, "confidenceInterval95": _ci(random_estimate, random_se)},
        "heterogeneity": {"Q": q, "df": df, "I2Percent": i2, "tau2": tau2},
        "predictionInterval95": _ci(random_estimate, prediction_se),
    }


class CrossStudyReplicationMetaExperimentManager:
    def __init__(
        self,
        db_path: str,
        batch_campaigns: Any | None = None,
        distributed_coordination: Any | None = None,
        persistent_disk_mounted: bool = False,
        max_studies: int = 10000,
        max_workspaces: int = 5000,
        max_effects: int = 100000,
        history_limit: int = 200000,
    ) -> None:
        self.db_path = str(db_path)
        self.batch_campaigns = batch_campaigns
        self.distributed_coordination = distributed_coordination
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_studies = max(1, int(max_studies))
        self.max_workspaces = max(1, int(max_workspaces))
        self.max_effects = max(1, int(max_effects))
        self.history_limit = max(100, int(history_limit))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
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

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS csr_studies(
                  id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, study_type TEXT NOT NULL,
                  current_revision INTEGER NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  actor TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS csr_study_project_idx ON csr_studies(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS csr_study_revisions(
                  study_id TEXT NOT NULL, revision INTEGER NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL,
                  definition_json TEXT NOT NULL, definition_hash TEXT NOT NULL,
                  PRIMARY KEY(study_id, revision), FOREIGN KEY(study_id) REFERENCES csr_studies(id)
                );
                CREATE TABLE IF NOT EXISTS csr_effects(
                  id TEXT PRIMARY KEY, study_id TEXT NOT NULL, project_id TEXT NOT NULL, metric_key TEXT NOT NULL,
                  effect_measure TEXT NOT NULL, estimate REAL NOT NULL, standard_error REAL NOT NULL, variance REAL NOT NULL,
                  sample_size INTEGER, created_at TEXT NOT NULL, actor TEXT NOT NULL, effect_json TEXT NOT NULL,
                  effect_hash TEXT NOT NULL, FOREIGN KEY(study_id) REFERENCES csr_studies(id)
                );
                CREATE INDEX IF NOT EXISTS csr_effect_study_idx ON csr_effects(study_id, metric_key, created_at);
                CREATE TABLE IF NOT EXISTS csr_workspaces(
                  id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, question TEXT NOT NULL,
                  primary_metric_key TEXT NOT NULL, primary_effect_measure TEXT NOT NULL, status TEXT NOT NULL,
                  definition_json TEXT NOT NULL, definition_hash TEXT NOT NULL, frozen_at TEXT NOT NULL DEFAULT '',
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS csr_workspace_project_idx ON csr_workspaces(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS csr_workspace_studies(
                  workspace_id TEXT NOT NULL, study_id TEXT NOT NULL, relation_type TEXT NOT NULL,
                  inclusion_state TEXT NOT NULL, harmonization_json TEXT NOT NULL, added_at TEXT NOT NULL, actor TEXT NOT NULL,
                  PRIMARY KEY(workspace_id, study_id), FOREIGN KEY(workspace_id) REFERENCES csr_workspaces(id),
                  FOREIGN KEY(study_id) REFERENCES csr_studies(id)
                );
                CREATE TABLE IF NOT EXISTS csr_assessments(
                  workspace_id TEXT NOT NULL, study_id TEXT NOT NULL, assessment TEXT NOT NULL, rationale TEXT NOT NULL,
                  reviewed_at TEXT NOT NULL, actor TEXT NOT NULL, PRIMARY KEY(workspace_id, study_id)
                );
                CREATE TABLE IF NOT EXISTS csr_events(
                  seq INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT NOT NULL DEFAULT '', study_id TEXT NOT NULL DEFAULT '',
                  event_type TEXT NOT NULL, occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
                  payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
                );
                """
            )

    def _event(self, db: sqlite3.Connection, workspace_id: str, study_id: str, event_type: str, actor: str, payload: Any) -> None:
        row = db.execute("SELECT event_hash FROM csr_events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = str(row["event_hash"]) if row else ""
        occurred = _now()
        envelope = {"workspaceId": workspace_id, "studyId": study_id, "eventType": event_type, "occurredAt": occurred, "actor": actor, "payload": payload, "previousHash": previous}
        event_hash = _sha(envelope)
        db.execute(
            "INSERT INTO csr_events(workspace_id,study_id,event_type,occurred_at,actor,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (workspace_id, study_id, event_type, occurred, actor, json.dumps(payload, sort_keys=True), previous, event_hash),
        )
        db.execute("DELETE FROM csr_events WHERE seq NOT IN (SELECT seq FROM csr_events ORDER BY seq DESC LIMIT ?)", (self.history_limit,))

    def policies(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "studyTypes": sorted(STUDY_TYPES),
            "relationTypes": sorted(RELATION_TYPES),
            "immutableStudyRevisions": True,
            "immutableEffectRecords": True,
            "workspaceFreeze": True,
            "fixedEffectSynthesis": True,
            "randomEffectsSynthesis": True,
            "heterogeneityDiagnostics": ["Q", "I2", "tau2"],
            "leaveOneOutSensitivity": True,
            "automaticReplicationJudgment": False,
            "automaticCausalInference": False,
            "publicationBiasInference": False,
            "studyIndependenceInferred": False,
            "automaticScientificValidity": False,
            "humanScientificReviewRequired": True,
            "boundary": BOUNDARY,
        }

    def health(self) -> dict[str, Any]:
        with self._connect() as db:
            studies = int(db.execute("SELECT COUNT(*) n FROM csr_studies").fetchone()["n"])
            effects = int(db.execute("SELECT COUNT(*) n FROM csr_effects").fetchone()["n"])
            workspaces = int(db.execute("SELECT COUNT(*) n FROM csr_workspaces").fetchone()["n"])
        return {
            "ok": True,
            "status": "ready",
            "version": VERSION,
            "storage": "sqlite-wal",
            "persistentDiskMounted": self.persistent_disk_mounted,
            "studies": studies,
            "effects": effects,
            "workspaces": workspaces,
            "batchCampaignIntegration": self.batch_campaigns is not None,
            "distributedCoordinationIntegration": self.distributed_coordination is not None,
            **{k: v for k, v in self.policies().items() if k not in {"ok", "version"}},
        }

    @staticmethod
    def _study_row(row: sqlite3.Row, definition: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"], "projectId": row["project_id"], "title": row["title"], "studyType": row["study_type"],
            "currentRevision": int(row["current_revision"]), "createdAt": row["created_at"], "updatedAt": row["updated_at"],
            "actor": row["actor"], "archived": bool(row["archived"]), "definition": definition,
        }

    def create_study(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project_id")
        definition = _study_definition(payload)
        now = _now(); study_id = f"study:{uuid.uuid4()}"; digest = _sha(definition)
        with self._lock, self._connect() as db:
            if int(db.execute("SELECT COUNT(*) n FROM csr_studies").fetchone()["n"]) >= self.max_studies:
                raise CrossStudyReplicationError("Study registry limit reached.", 409)
            db.execute("INSERT INTO csr_studies(id,project_id,title,study_type,current_revision,created_at,updated_at,actor) VALUES(?,?,?,?,1,?,?,?)", (study_id, project_id, definition["title"], definition["studyType"], now, now, actor))
            db.execute("INSERT INTO csr_study_revisions(study_id,revision,created_at,actor,definition_json,definition_hash) VALUES(?,?,?,?,?,?)", (study_id, 1, now, actor, json.dumps(definition, sort_keys=True), digest))
            self._event(db, "", study_id, "study-created", actor, {"revision": 1, "definitionHash": digest})
        return self.get_study(study_id)

    def revise_study(self, study_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        study_id = _clean_id(study_id, "study_id")
        definition = _study_definition(payload); digest = _sha(definition); now = _now()
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM csr_studies WHERE id=?", (study_id,)).fetchone()
            if not row: raise CrossStudyReplicationError("Study not found.", 404)
            revision = int(row["current_revision"]) + 1
            db.execute("INSERT INTO csr_study_revisions(study_id,revision,created_at,actor,definition_json,definition_hash) VALUES(?,?,?,?,?,?)", (study_id, revision, now, actor, json.dumps(definition, sort_keys=True), digest))
            db.execute("UPDATE csr_studies SET title=?,study_type=?,current_revision=?,updated_at=? WHERE id=?", (definition["title"], definition["studyType"], revision, now, study_id))
            self._event(db, "", study_id, "study-revised", actor, {"revision": revision, "definitionHash": digest})
        return self.get_study(study_id)

    def get_study(self, study_id: str, revision: int | None = None) -> dict[str, Any]:
        study_id = _clean_id(study_id, "study_id")
        with self._connect() as db:
            row = db.execute("SELECT * FROM csr_studies WHERE id=?", (study_id,)).fetchone()
            if not row: raise CrossStudyReplicationError("Study not found.", 404)
            rev = int(revision or row["current_revision"])
            r = db.execute("SELECT * FROM csr_study_revisions WHERE study_id=? AND revision=?", (study_id, rev)).fetchone()
            if not r: raise CrossStudyReplicationError("Study revision not found.", 404)
            out = self._study_row(row, json.loads(r["definition_json"]))
            out["revision"] = {"revision": rev, "createdAt": r["created_at"], "actor": r["actor"], "definitionHash": r["definition_hash"], "schema": STUDY_REVISION_SCHEMA}
            out["effects"] = [self._effect_row(x) for x in db.execute("SELECT * FROM csr_effects WHERE study_id=? ORDER BY created_at,id", (study_id,)).fetchall()]
            return {"ok": True, "study": out}

    def list_studies(self, project_id: str, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        project_id = _clean_id(project_id, "project_id"); limit = max(1, min(1000, int(limit)))
        q = "SELECT * FROM csr_studies WHERE project_id=?" + ("" if include_archived else " AND archived=0") + " ORDER BY updated_at DESC LIMIT ?"
        with self._connect() as db:
            rows = db.execute(q, (project_id, limit)).fetchall(); studies=[]
            for row in rows:
                r=db.execute("SELECT * FROM csr_study_revisions WHERE study_id=? AND revision=?",(row["id"],row["current_revision"])).fetchone()
                studies.append(self._study_row(row,json.loads(r["definition_json"])))
        return {"ok": True, "studies": studies, "count": len(studies)}

    @staticmethod
    def _effect_row(row: sqlite3.Row) -> dict[str, Any]:
        payload = json.loads(row["effect_json"])
        return {"id": row["id"], "studyId": row["study_id"], "projectId": row["project_id"], "createdAt": row["created_at"], "actor": row["actor"], "effectHash": row["effect_hash"], **payload}

    def add_effect(self, study_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        study_id = _clean_id(study_id, "study_id"); effect = _effect_record(payload); digest = _sha(effect); effect_id=f"effect:{uuid.uuid4()}"; now=_now()
        with self._lock, self._connect() as db:
            study = db.execute("SELECT project_id FROM csr_studies WHERE id=?", (study_id,)).fetchone()
            if not study: raise CrossStudyReplicationError("Study not found.",404)
            if int(db.execute("SELECT COUNT(*) n FROM csr_effects").fetchone()["n"]) >= self.max_effects: raise CrossStudyReplicationError("Effect registry limit reached.",409)
            db.execute("INSERT INTO csr_effects(id,study_id,project_id,metric_key,effect_measure,estimate,standard_error,variance,sample_size,created_at,actor,effect_json,effect_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (effect_id,study_id,study["project_id"],effect["metricKey"],effect["effectMeasure"],effect["estimate"],effect["standardError"],effect["variance"],effect["sampleSize"],now,actor,json.dumps(effect,sort_keys=True),digest))
            self._event(db,"",study_id,"effect-recorded",actor,{"effectId":effect_id,"effectHash":digest,"metricKey":effect["metricKey"]})
            row=db.execute("SELECT * FROM csr_effects WHERE id=?",(effect_id,)).fetchone()
        return {"ok":True,"effect":self._effect_row(row)}

    def create_workspace(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id=_clean_id(project_id,"project_id")
        if not isinstance(payload,dict): raise CrossStudyReplicationError("Workspace payload must be an object.")
        definition={
            "schema":WORKSPACE_SCHEMA,"version":VERSION,
            "title":_text(payload.get("title"),"title",600,True),
            "question":_text(payload.get("question"),"question",12000,True),
            "primaryMetricKey":_text(payload.get("primaryMetricKey"),"primaryMetricKey",200,True),
            "primaryEffectMeasure":_text(payload.get("primaryEffectMeasure"),"primaryEffectMeasure",200,True),
            "hypothesis":_text(payload.get("hypothesis"),"hypothesis",12000,False),
            "inclusionCriteria":_json(payload.get("inclusionCriteria") or {},"inclusionCriteria",500000),
            "exclusionCriteria":_json(payload.get("exclusionCriteria") or {},"exclusionCriteria",500000),
            "analysisPlan":_json(payload.get("analysisPlan") or {"models":["fixed-effect","random-effects"],"heterogeneity":["Q","I2","tau2"],"leaveOneOut":True},"analysisPlan",500000),
            "automaticReplicationJudgment":False,"automaticScientificValidity":False,"humanReviewRequired":True,
        }
        now=_now(); workspace_id=f"meta:{uuid.uuid4()}"; digest=_sha(definition)
        with self._lock,self._connect() as db:
            if int(db.execute("SELECT COUNT(*) n FROM csr_workspaces").fetchone()["n"])>=self.max_workspaces: raise CrossStudyReplicationError("Workspace limit reached.",409)
            db.execute("INSERT INTO csr_workspaces(id,project_id,title,question,primary_metric_key,primary_effect_measure,status,definition_json,definition_hash,created_at,updated_at,actor) VALUES(?,?,?,?,?,?,'draft',?,?,?,?,?)",(workspace_id,project_id,definition["title"],definition["question"],definition["primaryMetricKey"],definition["primaryEffectMeasure"],json.dumps(definition,sort_keys=True),digest,now,now,actor))
            self._event(db,workspace_id,"","workspace-created",actor,{"definitionHash":digest})
        return self.get_workspace(workspace_id)

    def _workspace_row(self,row:sqlite3.Row)->dict[str,Any]:
        return {"id":row["id"],"projectId":row["project_id"],"title":row["title"],"question":row["question"],"primaryMetricKey":row["primary_metric_key"],"primaryEffectMeasure":row["primary_effect_measure"],"status":row["status"],"definition":json.loads(row["definition_json"]),"definitionHash":row["definition_hash"],"frozenAt":row["frozen_at"],"createdAt":row["created_at"],"updatedAt":row["updated_at"],"actor":row["actor"],"archived":bool(row["archived"])}

    def list_workspaces(self,project_id:str,include_archived:bool=False,limit:int=100)->dict[str,Any]:
        project_id=_clean_id(project_id,"project_id");limit=max(1,min(1000,int(limit)))
        q="SELECT * FROM csr_workspaces WHERE project_id=?"+("" if include_archived else " AND archived=0")+" ORDER BY updated_at DESC LIMIT ?"
        with self._connect() as db: rows=db.execute(q,(project_id,limit)).fetchall()
        workspaces=[self._workspace_row(x) for x in rows]
        return {"ok":True,"workspaces":workspaces,"count":len(workspaces)}

    def get_workspace(self,workspace_id:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id")
        with self._connect() as db:
            row=db.execute("SELECT * FROM csr_workspaces WHERE id=?",(workspace_id,)).fetchone()
            if not row: raise CrossStudyReplicationError("Meta-experiment workspace not found.",404)
            members=[]
            for m in db.execute("SELECT ws.*,s.title,s.study_type,s.current_revision FROM csr_workspace_studies ws JOIN csr_studies s ON s.id=ws.study_id WHERE ws.workspace_id=? ORDER BY ws.added_at,ws.study_id",(workspace_id,)).fetchall():
                a=db.execute("SELECT * FROM csr_assessments WHERE workspace_id=? AND study_id=?",(workspace_id,m["study_id"])).fetchone()
                members.append({"studyId":m["study_id"],"title":m["title"],"studyType":m["study_type"],"studyRevision":int(m["current_revision"]),"relationType":m["relation_type"],"inclusionState":m["inclusion_state"],"harmonization":json.loads(m["harmonization_json"]),"addedAt":m["added_at"],"assessment":({"state":a["assessment"],"rationale":a["rationale"],"reviewedAt":a["reviewed_at"],"actor":a["actor"]} if a else {"state":"unreviewed"})})
        return {"ok":True,"workspace":self._workspace_row(row),"studies":members}

    def add_study_to_workspace(self,workspace_id:str,payload:dict[str,Any],actor:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");study_id=_clean_id(payload.get("studyId"),"studyId")
        relation=str(payload.get("relationType") or "related-study").strip().lower().replace("_","-")
        inclusion=str(payload.get("inclusionState") or "pending").strip().lower()
        if relation not in RELATION_TYPES: raise CrossStudyReplicationError("Unsupported relationType.")
        if inclusion not in INCLUSION_STATES: raise CrossStudyReplicationError("Unsupported inclusionState.")
        harmonization=_json(payload.get("harmonization") or {},"harmonization",500000)
        now=_now()
        with self._lock,self._connect() as db:
            w=db.execute("SELECT * FROM csr_workspaces WHERE id=?",(workspace_id,)).fetchone();s=db.execute("SELECT * FROM csr_studies WHERE id=?",(study_id,)).fetchone()
            if not w: raise CrossStudyReplicationError("Meta-experiment workspace not found.",404)
            if not s: raise CrossStudyReplicationError("Study not found.",404)
            if w["project_id"]!=s["project_id"]: raise CrossStudyReplicationError("Study and workspace must belong to the same project.",409)
            if w["frozen_at"]: raise CrossStudyReplicationError("Workspace is frozen; study membership cannot change.",409)
            db.execute("INSERT INTO csr_workspace_studies(workspace_id,study_id,relation_type,inclusion_state,harmonization_json,added_at,actor) VALUES(?,?,?,?,?,?,?) ON CONFLICT(workspace_id,study_id) DO UPDATE SET relation_type=excluded.relation_type,inclusion_state=excluded.inclusion_state,harmonization_json=excluded.harmonization_json,actor=excluded.actor",(workspace_id,study_id,relation,inclusion,json.dumps(harmonization,sort_keys=True),now,actor))
            db.execute("UPDATE csr_workspaces SET updated_at=? WHERE id=?",(now,workspace_id));self._event(db,workspace_id,study_id,"study-membership-recorded",actor,{"relationType":relation,"inclusionState":inclusion,"harmonizationHash":_sha(harmonization)})
        return self.get_workspace(workspace_id)

    def freeze_workspace(self,workspace_id:str,actor:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");now=_now()
        with self._lock,self._connect() as db:
            row=db.execute("SELECT * FROM csr_workspaces WHERE id=?",(workspace_id,)).fetchone()
            if not row: raise CrossStudyReplicationError("Meta-experiment workspace not found.",404)
            if not row["frozen_at"]:
                snapshot={"definitionHash":row["definition_hash"],"members":[dict(x) for x in db.execute("SELECT study_id,relation_type,inclusion_state,harmonization_json FROM csr_workspace_studies WHERE workspace_id=? ORDER BY study_id",(workspace_id,)).fetchall()]}
                db.execute("UPDATE csr_workspaces SET frozen_at=?,status='frozen',updated_at=? WHERE id=?",(now,now,workspace_id));self._event(db,workspace_id,"","workspace-frozen",actor,{"snapshotHash":_sha(snapshot)})
        return self.get_workspace(workspace_id)

    def record_assessment(self,workspace_id:str,study_id:str,payload:dict[str,Any],actor:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");study_id=_clean_id(study_id,"study_id");state=str(payload.get("assessment") or "unreviewed").strip().lower()
        if state not in ASSESSMENT_STATES: raise CrossStudyReplicationError("Unsupported assessment.")
        rationale=_text(payload.get("rationale"),"rationale",12000,state!="unreviewed");now=_now()
        with self._lock,self._connect() as db:
            m=db.execute("SELECT 1 FROM csr_workspace_studies WHERE workspace_id=? AND study_id=?",(workspace_id,study_id)).fetchone()
            if not m: raise CrossStudyReplicationError("Study is not linked to this workspace.",404)
            db.execute("INSERT INTO csr_assessments(workspace_id,study_id,assessment,rationale,reviewed_at,actor) VALUES(?,?,?,?,?,?) ON CONFLICT(workspace_id,study_id) DO UPDATE SET assessment=excluded.assessment,rationale=excluded.rationale,reviewed_at=excluded.reviewed_at,actor=excluded.actor",(workspace_id,study_id,state,rationale,now,actor));self._event(db,workspace_id,study_id,"human-replication-assessment-recorded",actor,{"assessment":state,"rationale":rationale})
        return self.get_workspace(workspace_id)

    def _included_effects(self,workspace_id:str,metric_key:str|None=None)->tuple[sqlite3.Row,list[dict[str,Any]]]:
        with self._connect() as db:
            w=db.execute("SELECT * FROM csr_workspaces WHERE id=?",(workspace_id,)).fetchone()
            if not w: raise CrossStudyReplicationError("Meta-experiment workspace not found.",404)
            metric_key=metric_key or w["primary_metric_key"]
            rows=db.execute("""SELECT e.*,ws.relation_type,ws.harmonization_json,s.title,s.study_type,s.current_revision FROM csr_workspace_studies ws JOIN csr_studies s ON s.id=ws.study_id JOIN csr_effects e ON e.study_id=s.id WHERE ws.workspace_id=? AND ws.inclusion_state='included' AND e.metric_key=? ORDER BY s.id,e.created_at""",(workspace_id,metric_key)).fetchall()
            latest={}
            for r in rows: latest[r["study_id"]]=r
            records=[]
            for r in latest.values():
                x=self._effect_row(r);x.update({"relationType":r["relation_type"],"studyTitle":r["title"],"studyType":r["study_type"],"studyRevision":int(r["current_revision"]),"harmonization":json.loads(r["harmonization_json"])});records.append(x)
            return w,records

    def synthesis(self,workspace_id:str,metric_key:str|None=None)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");w,records=self._included_effects(workspace_id,metric_key)
        if len(records)<2: raise CrossStudyReplicationError("At least two included studies with the same metricKey are required.",409)
        measures={r["effectMeasure"] for r in records}
        if len(measures)!=1: raise CrossStudyReplicationError("Included effect records must share one effectMeasure or be explicitly harmonized before synthesis.",409)
        core=_meta_analysis(records)
        direction={"positive":sum(1 for r in records if r["estimate"]>0),"negative":sum(1 for r in records if r["estimate"]<0),"zero":sum(1 for r in records if r["estimate"]==0)}
        leave=[]
        if len(records)>=3:
            for omitted in records:
                subset=[r for r in records if r["id"]!=omitted["id"]];m=_meta_analysis(subset)
                leave.append({"omittedStudyId":omitted["studyId"],"omittedStudyTitle":omitted["studyTitle"],"randomEffectsEstimate":m["randomEffects"]["estimate"],"I2Percent":m["heterogeneity"]["I2Percent"],"tau2":m["heterogeneity"]["tau2"]})
        contributions=[]
        for r in records:
            contributions.append({"studyId":r["studyId"],"studyTitle":r["studyTitle"],"relationType":r["relationType"],"estimate":r["estimate"],"standardError":r["standardError"],"variance":r["variance"],"effectHash":r["effectHash"]})
        result={"schema":SYNTHESIS_SCHEMA,"version":VERSION,"workspaceId":workspace_id,"metricKey":records[0]["metricKey"],"effectMeasure":records[0]["effectMeasure"],**core,"directionCounts":direction,"studyContributions":contributions,"leaveOneOut":leave,"automaticReplicationJudgment":False,"automaticCausalInference":False,"publicationBiasInference":False,"studyIndependenceInferred":False,"humanScientificReviewRequired":True,"boundary":BOUNDARY}
        result["synthesisDigest"]=_sha({k:v for k,v in result.items() if k!="synthesisDigest"})
        return {"ok":True,"synthesis":result}

    def replication_matrix(self,workspace_id:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");body=self.get_workspace(workspace_id);w=body["workspace"]
        rows=[]
        with self._connect() as db:
            for m in body["studies"]:
                effects=[self._effect_row(x) for x in db.execute("SELECT * FROM csr_effects WHERE study_id=? ORDER BY metric_key,created_at",(m["studyId"],)).fetchall()]
                rows.append({**m,"effects":effects})
        return {"ok":True,"workspaceId":workspace_id,"question":w["question"],"rows":rows,"automaticReplicationJudgment":False,"humanScientificReviewRequired":True}

    def replication_campaign_handoff(self,workspace_id:str,study_id:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");study_id=_clean_id(study_id,"study_id");body=self.get_workspace(workspace_id)
        member=next((x for x in body["studies"] if x["studyId"]==study_id),None)
        if not member: raise CrossStudyReplicationError("Study is not linked to this workspace.",404)
        study=self.get_study(study_id)["study"]
        definition=study["definition"]
        handoff={"schema":HANDOFF_SCHEMA,"version":VERSION,"workspaceId":workspace_id,"studyId":study_id,"studyRevision":study["currentRevision"],"relationType":member["relationType"],"targetProduct":"sustainable-catalyst-lab.batch-experiment-sweep-ensemble","targetRelease":"0.155.0","campaignDraft":{"title":f"Replication run — {study['title']}","objective":body["workspace"]["question"],"mode":"repeated-trials","method":"registered-method-required","repeats":3,"baseSeed":157000,"inputs":{"studyRef":study_id,"studyRevision":study["currentRevision"],"protocolRef":definition.get("protocolRef") or "","sourceRef":definition.get("sourceRef") or ""},"metrics":[body["workspace"]["primaryMetricKey"]]},"automaticCreation":False,"automaticExecution":False,"humanApprovalRequired":True}
        handoff["handoffDigest"]=_sha({k:v for k,v in handoff.items() if k!="handoffDigest"})
        return {"ok":True,"handoff":handoff}

    def manifest(self,workspace_id:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");body=self.get_workspace(workspace_id);matrix=self.replication_matrix(workspace_id)
        synthesis=None
        try: synthesis=self.synthesis(workspace_id)["synthesis"]
        except CrossStudyReplicationError: synthesis=None
        manifest={"schema":MANIFEST_SCHEMA,"version":VERSION,"workspace":body["workspace"],"studies":matrix["rows"],"synthesis":synthesis,"generatedAt":_now(),"automaticReplicationJudgment":False,"automaticScientificValidity":False,"humanScientificReviewRequired":True}
        manifest["manifestDigest"]=_sha({k:v for k,v in manifest.items() if k!="manifestDigest"})
        return {"ok":True,"manifest":manifest}

    def verify_manifest(self,payload:dict[str,Any])->dict[str,Any]:
        if not isinstance(payload,dict): raise CrossStudyReplicationError("Manifest must be an object.")
        expected=str(payload.get("manifestDigest") or "");actual=_sha({k:v for k,v in payload.items() if k!="manifestDigest"})
        return {"ok":True,"verified":bool(expected) and expected==actual,"expectedDigest":expected,"actualDigest":actual,"schema":payload.get("schema")}

    def archive_workspace(self,workspace_id:str,actor:str)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");now=_now()
        with self._lock,self._connect() as db:
            row=db.execute("SELECT id FROM csr_workspaces WHERE id=?",(workspace_id,)).fetchone()
            if not row: raise CrossStudyReplicationError("Meta-experiment workspace not found.",404)
            db.execute("UPDATE csr_workspaces SET archived=1,status='archived',updated_at=? WHERE id=?",(now,workspace_id));self._event(db,workspace_id,"","workspace-archived",actor,{})
        return self.get_workspace(workspace_id)

    def timeline(self,workspace_id:str,limit:int=500)->dict[str,Any]:
        workspace_id=_clean_id(workspace_id,"workspace_id");limit=max(1,min(5000,int(limit)))
        with self._connect() as db:
            rows=db.execute("SELECT * FROM csr_events WHERE workspace_id=? ORDER BY seq DESC LIMIT ?",(workspace_id,limit)).fetchall()
        events=[{"seq":int(r["seq"]),"workspaceId":r["workspace_id"],"studyId":r["study_id"],"eventType":r["event_type"],"occurredAt":r["occurred_at"],"actor":r["actor"],"payload":json.loads(r["payload_json"]),"previousHash":r["previous_hash"],"eventHash":r["event_hash"]} for r in reversed(rows)]
        return {"ok":True,"workspaceId":workspace_id,"events":events,"count":len(events)}
