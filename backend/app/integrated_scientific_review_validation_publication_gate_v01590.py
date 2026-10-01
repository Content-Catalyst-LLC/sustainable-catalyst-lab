from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.159.0"
DOSSIER_SCHEMA = "sc-lab-integrated-scientific-review-dossier/0.159.0"
CHECK_SCHEMA = "sc-lab-review-validation-check/0.159.0"
FINDING_SCHEMA = "sc-lab-review-finding/0.159.0"
REVIEW_SCHEMA = "sc-lab-scientific-review-signoff/0.159.0"
SNAPSHOT_SCHEMA = "sc-lab-review-evidence-snapshot/0.159.0"
PACKET_SCHEMA = "sc-lab-publication-gate-packet/0.159.0"
MANIFEST_SCHEMA = "sc-lab-review-publication-manifest/0.159.0"

DOSSIER_STATES = {"draft", "under-review", "revisions-required", "review-complete", "publication-ready", "archived"}
CHECK_STATES = {"pending", "satisfied", "not-applicable", "needs-revision", "blocked"}
FINDING_SEVERITIES = {"advisory", "minor", "major", "blocker"}
FINDING_STATES = {"open", "resolved", "accepted-risk", "withdrawn"}
REVIEW_DECISIONS = {"approve", "revisions-required", "dissent", "abstain"}
REVIEW_ROLES = {"primary-reviewer", "methods-reviewer", "reproducibility-reviewer", "replication-reviewer", "publication-reviewer", "other"}
REQUIRED_CHECKS = (
    "provenance-completeness",
    "methods-and-protocol-review",
    "data-and-source-review",
    "computational-reproducibility-review",
    "statistical-diagnostics-review",
    "replication-evidence-review",
    "contradictions-and-alternatives-review",
    "limitations-and-boundaries-review",
    "reviewer-signoff-review",
    "publication-artifact-review",
)
BOUNDARY = (
    "The review gate records evidence, checklist states, findings, revisions, reviewer sign-offs, dissent and publication handoffs. "
    "It may determine procedural readiness from explicit records, but it does not infer scientific validity, truth, causality, replication success, publication merit, or reviewer agreement. "
    "Publication-ready status requires explicit human authorization."
)

class ScientificReviewGateError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _canonical(v: Any) -> bytes: return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
def _sha(v: Any) -> str: return hashlib.sha256(_canonical(v)).hexdigest()
def _id(v: Any, label: str) -> str:
    t=str(v or "").strip(); allowed="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not t or len(t)>180 or any(c not in allowed for c in t): raise ScientificReviewGateError(f"Invalid {label}.")
    return t

def _text(v: Any, label: str, maximum: int=12000, required: bool=False) -> str:
    t=str(v or "").strip()
    if required and not t: raise ScientificReviewGateError(f"{label} is required.")
    if len(t)>maximum: raise ScientificReviewGateError(f"{label} exceeds {maximum} characters.")
    return t

def _json(v: Any, label: str, maximum_bytes: int=1_000_000) -> Any:
    try: raw=_canonical(v)
    except Exception as exc: raise ScientificReviewGateError(f"{label} must be JSON serializable.") from exc
    if len(raw)>maximum_bytes: raise ScientificReviewGateError(f"{label} exceeds payload limit.",413)
    return json.loads(raw.decode("utf-8"))

def _dossier_definition(payload: dict[str,Any]) -> dict[str,Any]:
    return {
        "schema":DOSSIER_SCHEMA,"version":VERSION,
        "title":_text(payload.get("title"),"title",600,True),
        "researchObjectRef":_text(payload.get("researchObjectRef"),"researchObjectRef",500),
        "crossStudyWorkspaceId":_text(payload.get("crossStudyWorkspaceId"),"crossStudyWorkspaceId",180),
        "replicationNetworkId":_text(payload.get("replicationNetworkId"),"replicationNetworkId",180),
        "publicationTarget":_text(payload.get("publicationTarget"),"publicationTarget",500),
        "scope":_text(payload.get("scope"),"scope",12000),
        "requiredChecks":list(REQUIRED_CHECKS),
        "automaticScientificValidity":False,"automaticPublication":False,"automaticReplicationJudgment":False,
        "humanPublicationAuthorizationRequired":True,
    }

class IntegratedScientificReviewValidationPublicationGateManager:
    def __init__(self, db_path: str, cross_study: Any|None=None, replication_network: Any|None=None,
                 persistent_disk_mounted: bool=False, max_dossiers: int=10000, max_findings: int=100000, history_limit: int=300000):
        self.db_path=str(db_path); self.cross_study=cross_study; self.replication_network=replication_network
        self.persistent_disk_mounted=bool(persistent_disk_mounted); self.max_dossiers=max(1,int(max_dossiers)); self.max_findings=max(1,int(max_findings)); self.history_limit=max(100,int(history_limit)); self._lock=threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True,exist_ok=True); self._init_db()
    def _connect(self):
        class _ClosingConnection(sqlite3.Connection):
            def __exit__(self, exc_type, exc, tb):
                try: return super().__exit__(exc_type, exc, tb)
                finally: self.close()
        db=sqlite3.connect(self.db_path,timeout=30,check_same_thread=False,factory=_ClosingConnection); db.row_factory=sqlite3.Row; db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA foreign_keys=ON"); return db
    def _init_db(self):
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS rv_dossiers(id TEXT PRIMARY KEY, project_id TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rv_checks(id TEXT PRIMARY KEY, dossier_id TEXT NOT NULL, check_key TEXT NOT NULL, category TEXT NOT NULL, state TEXT NOT NULL, evidence_json TEXT NOT NULL, rationale TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL, UNIQUE(dossier_id,check_key));
            CREATE TABLE IF NOT EXISTS rv_findings(id TEXT PRIMARY KEY, dossier_id TEXT NOT NULL, severity TEXT NOT NULL, state TEXT NOT NULL, title TEXT NOT NULL, detail TEXT NOT NULL, source_ref TEXT NOT NULL, resolution TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rv_reviews(id TEXT PRIMARY KEY, dossier_id TEXT NOT NULL, reviewer_ref TEXT NOT NULL, role TEXT NOT NULL, decision TEXT NOT NULL, rationale TEXT NOT NULL, dissent TEXT NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rv_snapshots(id TEXT PRIMARY KEY, dossier_id TEXT NOT NULL, snapshot_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rv_events(seq INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL, dossier_id TEXT NOT NULL, kind TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL);
            """)
    def _count(self,db,table): return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    def _event(self,db,project_id,dossier_id,kind,payload,actor):
        db.execute("INSERT INTO rv_events(project_id,dossier_id,kind,payload_json,created_at,actor) VALUES(?,?,?,?,?,?)",(project_id,dossier_id,kind,json.dumps(payload,sort_keys=True),_now(),actor or "system"))
        excess=int(db.execute("SELECT COUNT(*) FROM rv_events").fetchone()[0])-self.history_limit
        if excess>0: db.execute("DELETE FROM rv_events WHERE seq IN (SELECT seq FROM rv_events ORDER BY seq LIMIT ?)",(excess,))
    def policies(self):
        return {"version":VERSION,"boundary":BOUNDARY,"requiredChecks":list(REQUIRED_CHECKS),"proceduralReadinessOnly":True,"automaticScientificValidity":False,"automaticPublication":False,"automaticReplicationJudgment":False,"automaticCausalInference":False,"humanPublicationAuthorizationRequired":True,"humanScientificReviewRequired":True}
    def health(self):
        return {"ok":True,"version":VERSION,"integratedScientificReviewValidationPublicationGate":True,"reviewDossiers":True,"validationChecklists":True,"findingsAndRevisionActions":True,"reviewerSignoffAndDissent":True,"crossStudyEvidenceSnapshots":True,"replicationNetworkEvidenceSnapshots":True,"proceduralReadinessEvaluation":True,"publicationPackets":True,"manifestVerification":True,"automaticScientificValidity":False,"automaticPublication":False,"automaticReplicationJudgment":False,"humanPublicationAuthorizationRequired":True,"storage":"persistent-disk" if self.persistent_disk_mounted else "instance-local","boundary":BOUNDARY}
    def create_dossier(self,project_id,payload,actor="human"):
        project_id=_id(project_id,"project_id"); definition=_dossier_definition(payload)
        if definition["crossStudyWorkspaceId"] and self.cross_study is not None: self.cross_study.get_workspace(definition["crossStudyWorkspaceId"])
        if definition["replicationNetworkId"] and self.replication_network is not None: self.replication_network.get_network(definition["replicationNetworkId"])
        did="review:"+uuid.uuid4().hex; now=_now(); digest=_sha(definition)
        with self._lock,self._connect() as db:
            if self._count(db,"rv_dossiers")>=self.max_dossiers: raise ScientificReviewGateError("Review dossier limit reached.",409)
            db.execute("INSERT INTO rv_dossiers VALUES(?,?,?,?,?,?,?)",(did,project_id,"draft",json.dumps(definition,sort_keys=True),digest,now,now))
            for key in REQUIRED_CHECKS:
                cid="check:"+uuid.uuid4().hex
                db.execute("INSERT INTO rv_checks VALUES(?,?,?,?,?,?,?,?,?)",(cid,did,key,key.split('-')[0],"pending","[]","",now,actor))
            self._event(db,project_id,did,"dossier.created",{"digest":digest},actor)
        return {"ok":True,"dossier":self.get_dossier(did)}
    def _dossier_row(self,r):
        return {"id":r["id"],"projectId":r["project_id"],"status":r["status"],"digest":r["digest"],"createdAt":r["created_at"],"updatedAt":r["updated_at"],**json.loads(r["definition_json"])}
    def get_dossier(self,dossier_id):
        dossier_id=_id(dossier_id,"dossier_id")
        with self._connect() as db:
            r=db.execute("SELECT * FROM rv_dossiers WHERE id=?",(dossier_id,)).fetchone()
            if not r: raise ScientificReviewGateError("Review dossier not found.",404)
            checks=db.execute("SELECT * FROM rv_checks WHERE dossier_id=? ORDER BY check_key",(dossier_id,)).fetchall()
            findings=db.execute("SELECT * FROM rv_findings WHERE dossier_id=? ORDER BY created_at",(dossier_id,)).fetchall()
            reviews=db.execute("SELECT * FROM rv_reviews WHERE dossier_id=? ORDER BY created_at",(dossier_id,)).fetchall()
        d=self._dossier_row(r)
        d["checks"]=[{"id":x["id"],"key":x["check_key"],"category":x["category"],"state":x["state"],"evidenceRefs":json.loads(x["evidence_json"]),"rationale":x["rationale"],"updatedAt":x["updated_at"],"actor":x["actor"]} for x in checks]
        d["findings"]=[{"id":x["id"],"severity":x["severity"],"state":x["state"],"title":x["title"],"detail":x["detail"],"sourceRef":x["source_ref"],"resolution":x["resolution"],"createdAt":x["created_at"],"updatedAt":x["updated_at"],"actor":x["actor"]} for x in findings]
        d["reviews"]=[{"id":x["id"],"reviewerRef":x["reviewer_ref"],"role":x["role"],"decision":x["decision"],"rationale":x["rationale"],"dissent":x["dissent"],"createdAt":x["created_at"],"actor":x["actor"]} for x in reviews]
        return d
    def list_dossiers(self,project_id,include_archived=False,limit=100):
        project_id=_id(project_id,"project_id"); limit=max(1,min(int(limit),1000)); sql="SELECT * FROM rv_dossiers WHERE project_id=?"; args=[project_id]
        if not include_archived: sql+=" AND status<>'archived'"
        sql+=" ORDER BY updated_at DESC LIMIT ?"; args.append(limit)
        with self._connect() as db: rows=db.execute(sql,args).fetchall()
        return {"ok":True,"dossiers":[self._dossier_row(r) for r in rows],"count":len(rows)}
    def evidence_snapshot(self,dossier_id,actor="human"):
        d=self.get_dossier(dossier_id); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"dossierId":dossier_id,"capturedAt":_now(),"crossStudy":None,"replicationNetwork":None,"interpretation":"descriptive-source-snapshot"}
        if d.get("crossStudyWorkspaceId") and self.cross_study is not None:
            wid=d["crossStudyWorkspaceId"]; snap["crossStudy"]={"workspace":self.cross_study.get_workspace(wid),"synthesis":self.cross_study.synthesis(wid),"replicationMatrix":self.cross_study.replication_matrix(wid)}
        if d.get("replicationNetworkId") and self.replication_network is not None:
            nid=d["replicationNetworkId"]; snap["replicationNetwork"]={"network":self.replication_network.get_network(nid),"coverage":self.replication_network.coverage(nid),"view":self.replication_network.network_view(nid)}
        sid="snapshot:"+uuid.uuid4().hex; digest=_sha(snap)
        with self._lock,self._connect() as db:
            db.execute("INSERT INTO rv_snapshots VALUES(?,?,?,?,?,?)",(sid,dossier_id,json.dumps(snap,sort_keys=True),digest,_now(),actor)); self._event(db,d["projectId"],dossier_id,"evidence.snapshot",{"snapshotId":sid,"digest":digest},actor)
        return {"ok":True,"snapshot":{"id":sid,"digest":digest,**snap}}
    def set_check(self,dossier_id,payload,actor="human"):
        d=self.get_dossier(dossier_id); key=_text(payload.get("key"),"key",180,True); state=str(payload.get("state") or "pending").strip().lower()
        if key not in REQUIRED_CHECKS: raise ScientificReviewGateError("Unsupported review check key.")
        if state not in CHECK_STATES: raise ScientificReviewGateError(f"Unsupported check state: {state}.")
        evidence=_json(payload.get("evidenceRefs") or [],"evidenceRefs",400000); rationale=_text(payload.get("rationale"),"rationale",12000); now=_now()
        with self._lock,self._connect() as db:
            db.execute("UPDATE rv_checks SET state=?,evidence_json=?,rationale=?,updated_at=?,actor=? WHERE dossier_id=? AND check_key=?",(state,json.dumps(evidence,sort_keys=True),rationale,now,actor,dossier_id,key)); self._event(db,d["projectId"],dossier_id,"check.updated",{"key":key,"state":state},actor)
        return {"ok":True,"dossier":self.get_dossier(dossier_id)}
    def add_finding(self,dossier_id,payload,actor="human"):
        d=self.get_dossier(dossier_id); severity=str(payload.get("severity") or "major").strip().lower()
        if severity not in FINDING_SEVERITIES: raise ScientificReviewGateError(f"Unsupported severity: {severity}.")
        fid="finding:"+uuid.uuid4().hex; now=_now(); title=_text(payload.get("title"),"title",600,True); detail=_text(payload.get("detail"),"detail",16000,True); source=_text(payload.get("sourceRef"),"sourceRef",500)
        with self._lock,self._connect() as db:
            if self._count(db,"rv_findings")>=self.max_findings: raise ScientificReviewGateError("Review finding limit reached.",409)
            db.execute("INSERT INTO rv_findings VALUES(?,?,?,?,?,?,?,?,?,?,?)",(fid,dossier_id,severity,"open",title,detail,source,"",now,now,actor)); self._event(db,d["projectId"],dossier_id,"finding.created",{"findingId":fid,"severity":severity},actor)
        return {"ok":True,"finding":next(x for x in self.get_dossier(dossier_id)["findings"] if x["id"]==fid)}
    def resolve_finding(self,dossier_id,finding_id,payload,actor="human"):
        d=self.get_dossier(dossier_id); finding_id=_id(finding_id,"finding_id"); state=str(payload.get("state") or "resolved").strip().lower()
        if state not in FINDING_STATES-{"open"}: raise ScientificReviewGateError("Finding resolution state must be resolved, accepted-risk, or withdrawn.")
        resolution=_text(payload.get("resolution"),"resolution",12000,True); now=_now()
        with self._lock,self._connect() as db:
            r=db.execute("SELECT id FROM rv_findings WHERE id=? AND dossier_id=?",(finding_id,dossier_id)).fetchone()
            if not r: raise ScientificReviewGateError("Review finding not found.",404)
            db.execute("UPDATE rv_findings SET state=?,resolution=?,updated_at=?,actor=? WHERE id=?",(state,resolution,now,actor,finding_id)); self._event(db,d["projectId"],dossier_id,"finding.resolved",{"findingId":finding_id,"state":state},actor)
        return {"ok":True,"dossier":self.get_dossier(dossier_id)}
    def record_review(self,dossier_id,payload,actor="human"):
        d=self.get_dossier(dossier_id); decision=str(payload.get("decision") or "abstain").strip().lower(); role=str(payload.get("role") or "other").strip().lower()
        if decision not in REVIEW_DECISIONS: raise ScientificReviewGateError(f"Unsupported review decision: {decision}.")
        if role not in REVIEW_ROLES: raise ScientificReviewGateError(f"Unsupported reviewer role: {role}.")
        record={"schema":REVIEW_SCHEMA,"version":VERSION,"reviewerRef":_text(payload.get("reviewerRef"),"reviewerRef",500,True),"role":role,"decision":decision,"rationale":_text(payload.get("rationale"),"rationale",16000,True),"dissent":_text(payload.get("dissent"),"dissent",16000),"humanAuthored":True,"automaticScientificJudgment":False}
        rid="signoff:"+uuid.uuid4().hex; now=_now()
        with self._lock,self._connect() as db:
            db.execute("INSERT INTO rv_reviews VALUES(?,?,?,?,?,?,?,?,?)",(rid,dossier_id,record["reviewerRef"],role,decision,record["rationale"],record["dissent"],now,actor)); self._event(db,d["projectId"],dossier_id,"review.recorded",{"reviewId":rid,"role":role,"decision":decision},actor)
        return {"ok":True,"review":{"id":rid,"dossierId":dossier_id,"createdAt":now,**record}}
    def evaluate_gate(self,dossier_id):
        d=self.get_dossier(dossier_id); blocking=[]
        for c in d["checks"]:
            if c["key"] in REQUIRED_CHECKS and c["state"] not in {"satisfied","not-applicable"}: blocking.append({"type":"check","key":c["key"],"state":c["state"]})
        for f in d["findings"]:
            if f["state"]=="open" and f["severity"] in {"major","blocker"}: blocking.append({"type":"finding","id":f["id"],"severity":f["severity"],"title":f["title"]})
        approvals=[r for r in d["reviews"] if r["decision"]=="approve"]
        revision_requests=[r for r in d["reviews"] if r["decision"]=="revisions-required"]
        procedural=(len(blocking)==0 and len(revision_requests)==0)
        return {"ok":True,"dossierId":dossier_id,"proceduralReady":procedural,"humanApprovalPresent":bool(approvals),"approvalCount":len(approvals),"revisionRequestCount":len(revision_requests),"blockingReasons":blocking,"scientificValidityDetermined":False,"publicationMeritDetermined":False,"replicationSuccessDetermined":False,"requiresExplicitHumanPublicationAuthorization":True,"boundary":BOUNDARY}
    def transition(self,dossier_id,payload,actor="human"):
        d=self.get_dossier(dossier_id); target=str(payload.get("targetState") or "").strip().lower(); human=bool(payload.get("humanAuthorization",False)); reason=_text(payload.get("reason"),"reason",12000,True)
        if target not in DOSSIER_STATES: raise ScientificReviewGateError(f"Unsupported dossier state: {target}.")
        allowed={"draft":{"under-review","archived"},"under-review":{"revisions-required","review-complete","archived"},"revisions-required":{"under-review","archived"},"review-complete":{"publication-ready","revisions-required","archived"},"publication-ready":{"revisions-required","archived"},"archived":set()}
        if target not in allowed.get(d["status"],set()): raise ScientificReviewGateError(f"Invalid transition {d['status']} -> {target}.",409)
        if target in {"review-complete","publication-ready"}:
            gate=self.evaluate_gate(dossier_id)
            if not gate["proceduralReady"]: raise ScientificReviewGateError("Procedural blockers remain; review cannot advance.",409)
        if target=="publication-ready":
            gate=self.evaluate_gate(dossier_id)
            if not gate["humanApprovalPresent"]: raise ScientificReviewGateError("At least one explicit human approval is required.",409)
            if not human: raise ScientificReviewGateError("Explicit humanAuthorization=true is required for publication-ready status.",409)
        with self._lock,self._connect() as db:
            db.execute("UPDATE rv_dossiers SET status=?,updated_at=? WHERE id=?",(target,_now(),dossier_id)); self._event(db,d["projectId"],dossier_id,"dossier.transition",{"from":d["status"],"to":target,"reason":reason,"humanAuthorization":human},actor)
        return {"ok":True,"dossier":self.get_dossier(dossier_id),"gate":self.evaluate_gate(dossier_id)}
    def publication_packet(self,dossier_id):
        d=self.get_dossier(dossier_id); gate=self.evaluate_gate(dossier_id)
        if d["status"]!="publication-ready": raise ScientificReviewGateError("Dossier must be publication-ready before a publication packet can be prepared.",409)
        packet={"schema":PACKET_SCHEMA,"version":VERSION,"dossierId":dossier_id,"projectId":d["projectId"],"researchObjectRef":d.get("researchObjectRef",""),"publicationTarget":d.get("publicationTarget",""),"crossStudyWorkspaceId":d.get("crossStudyWorkspaceId",""),"replicationNetworkId":d.get("replicationNetworkId",""),"reviewStatus":d["status"],"gate":gate,"checklist":d["checks"],"findings":d["findings"],"reviews":d["reviews"],"targetProduct":"sustainable-catalyst-publication-studio","automaticPublication":False,"requiresExplicitUserAction":True,"scientificValidityDetermined":False,"generatedAt":_now(),"boundary":BOUNDARY}
        packet["digest"]=_sha(packet); return {"ok":True,"packet":packet}
    def manifest(self,dossier_id):
        d=self.get_dossier(dossier_id); gate=self.evaluate_gate(dossier_id)
        with self._connect() as db: snaps=db.execute("SELECT id,digest,created_at FROM rv_snapshots WHERE dossier_id=? ORDER BY created_at",(dossier_id,)).fetchall()
        payload={"schema":MANIFEST_SCHEMA,"version":VERSION,"dossier":d,"gate":gate,"evidenceSnapshots":[{"id":x["id"],"digest":x["digest"],"createdAt":x["created_at"]} for x in snaps],"boundary":BOUNDARY}
        return {"ok":True,"manifest":payload,"digest":_sha(payload)}
    def verify_manifest(self,payload):
        if not isinstance(payload,dict): raise ScientificReviewGateError("Manifest verification payload must be an object.")
        manifest=payload.get("manifest"); digest=str(payload.get("digest") or "")
        if not isinstance(manifest,dict) or not digest: raise ScientificReviewGateError("manifest and digest are required.")
        actual=_sha(manifest); return {"ok":True,"verified":actual==digest,"expected":digest,"actual":actual}
    def timeline(self,dossier_id,limit=500):
        d=self.get_dossier(dossier_id)
        with self._connect() as db: rows=db.execute("SELECT seq,kind,payload_json,created_at,actor FROM rv_events WHERE dossier_id=? ORDER BY seq DESC LIMIT ?",(dossier_id,max(1,min(int(limit),5000)))).fetchall()
        return {"ok":True,"dossierId":dossier_id,"events":[{"seq":r["seq"],"kind":r["kind"],"payload":json.loads(r["payload_json"]),"createdAt":r["created_at"],"actor":r["actor"]} for r in rows]}
    def archive(self,dossier_id,actor="human"):
        d=self.get_dossier(dossier_id)
        if d["status"]=="archived": return {"ok":True,"dossier":d}
        with self._lock,self._connect() as db: db.execute("UPDATE rv_dossiers SET status='archived',updated_at=? WHERE id=?",(_now(),dossier_id)); self._event(db,d["projectId"],dossier_id,"dossier.archived",{},actor)
        return {"ok":True,"dossier":self.get_dossier(dossier_id)}
