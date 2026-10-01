from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.158.0"
NODE_SCHEMA = "sc-lab-replication-network-node/0.158.0"
NETWORK_SCHEMA = "sc-lab-independent-replication-network/0.158.0"
PLAN_SCHEMA = "sc-lab-replication-plan/0.158.0"
RESULT_SCHEMA = "sc-lab-replication-result-receipt/0.158.0"
REVIEW_SCHEMA = "sc-lab-replication-review-record/0.158.0"
MANIFEST_SCHEMA = "sc-lab-replication-network-manifest/0.158.0"
HANDOFF_SCHEMA = "sc-lab-replication-execution-handoff/0.158.0"

NODE_TYPES = {"laboratory", "institution", "field-site", "computational-site", "consortium-node", "independent-researcher"}
NETWORK_STATES = {"draft", "frozen", "archived"}
PLAN_STATES = {"planned", "handoff-prepared", "in-progress", "completed", "cancelled"}
RESULT_STATES = {"completed", "partial", "failed", "withdrawn"}
REVIEW_STATES = {"unreviewed", "consistent", "inconsistent", "mixed", "not-assessable"}
BOUNDARY = (
    "Replication-network records preserve declared independence, protocol lineage, preregistration, execution handoffs, result references, deviations and human review. "
    "The system does not infer independence, automatically execute replications, label findings confirmed or refuted, establish causality or scientific validity, or replace human scientific review."
)

class ReplicationNetworkError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail = detail; self.status_code = status_code

def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _canonical(v: Any) -> bytes: return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
def _sha(v: Any) -> str: return hashlib.sha256(_canonical(v)).hexdigest()
def _id(v: Any, label: str) -> str:
    t=str(v or "").strip(); allowed="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not t or len(t)>180 or any(c not in allowed for c in t): raise ReplicationNetworkError(f"Invalid {label}.")
    return t

def _text(v: Any, label: str, maximum: int=8000, required: bool=False) -> str:
    t=str(v or "").strip()
    if required and not t: raise ReplicationNetworkError(f"{label} is required.")
    if len(t)>maximum: raise ReplicationNetworkError(f"{label} exceeds {maximum} characters.")
    return t

def _json(v: Any, label: str, maximum_bytes: int=1_000_000) -> Any:
    try: raw=_canonical(v)
    except Exception as exc: raise ReplicationNetworkError(f"{label} must be JSON serializable.") from exc
    if len(raw)>maximum_bytes: raise ReplicationNetworkError(f"{label} exceeds payload limit.",413)
    return json.loads(raw.decode("utf-8"))

def _bool(v: Any) -> bool: return bool(v)

def _node_definition(payload: dict[str,Any]) -> dict[str,Any]:
    kind=str(payload.get("nodeType") or "laboratory").strip().lower().replace("_","-")
    if kind not in NODE_TYPES: raise ReplicationNetworkError(f"Unsupported node type: {kind}.")
    declared=_bool(payload.get("independenceDeclared",False))
    evidence=_text(payload.get("independenceEvidence"),"independenceEvidence",8000,False)
    if declared and not evidence: raise ReplicationNetworkError("independenceEvidence is required when independenceDeclared is true.")
    return {"schema":NODE_SCHEMA,"version":VERSION,"name":_text(payload.get("name"),"name",600,True),"nodeType":kind,
            "institutionRef":_text(payload.get("institutionRef"),"institutionRef",500),"jurisdiction":_text(payload.get("jurisdiction"),"jurisdiction",300),
            "capabilityRefs":_json(payload.get("capabilityRefs") or [],"capabilityRefs",200000),"contactRef":_text(payload.get("contactRef"),"contactRef",500),
            "independenceDeclared":declared,"independenceEvidence":evidence,"conflictDisclosure":_text(payload.get("conflictDisclosure"),"conflictDisclosure",8000),
            "independenceInferred":False,"credentialsStored":False,"humanReviewRequired":True}

def _network_definition(payload: dict[str,Any]) -> dict[str,Any]:
    return {"schema":NETWORK_SCHEMA,"version":VERSION,"title":_text(payload.get("title"),"title",600,True),
            "researchQuestion":_text(payload.get("researchQuestion"),"researchQuestion",12000,True),
            "anchorStudyId":_text(payload.get("anchorStudyId"),"anchorStudyId",180),"metaExperimentId":_text(payload.get("metaExperimentId"),"metaExperimentId",180),
            "protocolRef":_text(payload.get("protocolRef"),"protocolRef",500),"eligibilityCriteria":_text(payload.get("eligibilityCriteria"),"eligibilityCriteria",12000),
            "coordinationModel":_text(payload.get("coordinationModel") or "independent-sites","coordinationModel",200),
            "automaticReplicationJudgment":False,"automaticScientificValidity":False,"independenceInferred":False,"humanReviewRequired":True}

def _plan_definition(payload: dict[str,Any]) -> dict[str,Any]:
    planned_metrics=_json(payload.get("plannedMetrics") or [],"plannedMetrics",300000)
    if not isinstance(planned_metrics,list): raise ReplicationNetworkError("plannedMetrics must be an array.")
    return {"schema":PLAN_SCHEMA,"version":VERSION,"title":_text(payload.get("title"),"title",600,True),
            "sourceStudyId":_text(payload.get("sourceStudyId"),"sourceStudyId",180,True),"nodeId":_text(payload.get("nodeId"),"nodeId",180,True),
            "protocolRef":_text(payload.get("protocolRef"),"protocolRef",500,True),"preregistrationRef":_text(payload.get("preregistrationRef"),"preregistrationRef",500,True),
            "plannedMetrics":planned_metrics,"samplePlan":_text(payload.get("samplePlan"),"samplePlan",10000),"deviationPolicy":_text(payload.get("deviationPolicy"),"deviationPolicy",10000),
            "executionProfile":_json(payload.get("executionProfile") or {},"executionProfile",300000),"independenceDeclarationRef":_text(payload.get("independenceDeclarationRef"),"independenceDeclarationRef",500),
            "immutable":True,"automaticExecution":False,"humanReviewRequired":True}

class ScientificReproductionIndependentReplicationNetworkManager:
    def __init__(self, db_path: str, cross_study: Any|None=None, batch_campaigns: Any|None=None, distributed_coordination: Any|None=None,
                 persistent_disk_mounted: bool=False, max_nodes: int=5000, max_networks: int=5000, max_plans: int=50000, history_limit: int=300000):
        self.db_path=str(db_path); self.cross_study=cross_study; self.batch_campaigns=batch_campaigns; self.distributed_coordination=distributed_coordination
        self.persistent_disk_mounted=bool(persistent_disk_mounted); self.max_nodes=max(1,int(max_nodes)); self.max_networks=max(1,int(max_networks)); self.max_plans=max(1,int(max_plans)); self.history_limit=max(100,int(history_limit)); self._lock=threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True,exist_ok=True); self._init_db()
    def _connect(self):
        db=sqlite3.connect(self.db_path,timeout=30,check_same_thread=False); db.row_factory=sqlite3.Row; db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA foreign_keys=ON"); return db
    def _init_db(self):
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS rn_nodes(id TEXT PRIMARY KEY, project_id TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rn_networks(id TEXT PRIMARY KEY, project_id TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, frozen_at TEXT);
            CREATE TABLE IF NOT EXISTS rn_memberships(network_id TEXT NOT NULL, node_id TEXT NOT NULL, role TEXT NOT NULL, joined_at TEXT NOT NULL, actor TEXT NOT NULL, PRIMARY KEY(network_id,node_id));
            CREATE TABLE IF NOT EXISTS rn_plans(id TEXT PRIMARY KEY, network_id TEXT NOT NULL, project_id TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rn_results(id TEXT PRIMARY KEY, plan_id TEXT NOT NULL, network_id TEXT NOT NULL, project_id TEXT NOT NULL, state TEXT NOT NULL, payload_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rn_reviews(id TEXT PRIMARY KEY, network_id TEXT NOT NULL, plan_id TEXT, state TEXT NOT NULL, payload_json TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rn_events(seq INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL, kind TEXT NOT NULL, object_id TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL, actor TEXT NOT NULL);
            """)
    def _count(self,db,table): return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    def _event(self,db,project_id,kind,object_id,payload,actor):
        db.execute("INSERT INTO rn_events(project_id,kind,object_id,payload_json,created_at,actor) VALUES(?,?,?,?,?,?)",(project_id,kind,object_id,json.dumps(payload,sort_keys=True),_now(),actor or "system"))
        excess=int(db.execute("SELECT COUNT(*) FROM rn_events").fetchone()[0])-self.history_limit
        if excess>0: db.execute("DELETE FROM rn_events WHERE seq IN (SELECT seq FROM rn_events ORDER BY seq LIMIT ?)",(excess,))
    def policies(self):
        return {"version":VERSION,"boundary":BOUNDARY,"independenceMustBeDeclared":True,"independenceInferred":False,"preregistrationReferenceRequired":True,"protocolReferenceRequired":True,
                "automaticExecution":False,"automaticReplicationJudgment":False,"automaticCausalInference":False,"automaticScientificValidity":False,"credentialsStored":False,"humanScientificReviewRequired":True}
    def health(self):
        with self._connect() as db:
            counts={"nodes":self._count(db,"rn_nodes"),"networks":self._count(db,"rn_networks"),"plans":self._count(db,"rn_plans"),"results":self._count(db,"rn_results"),"reviews":self._count(db,"rn_reviews")}
        return {"ok":True,"status":"ready","version":VERSION,"scientificReproductionIndependentReplicationNetwork":True,"storage":"persistent-disk" if self.persistent_disk_mounted else "instance-local","counts":counts,**self.policies()}
    def create_node(self, project_id, payload, actor="human"):
        project_id=_id(project_id,"project_id"); definition=_node_definition(payload); now=_now(); nid="node:"+uuid.uuid4().hex; digest=_sha(definition)
        with self._lock,self._connect() as db:
            if self._count(db,"rn_nodes")>=self.max_nodes: raise ReplicationNetworkError("Node registry limit reached.",409)
            db.execute("INSERT INTO rn_nodes VALUES(?,?,?,?,?,?,?)",(nid,project_id,"active",json.dumps(definition,sort_keys=True),digest,now,now)); self._event(db,project_id,"node.created",nid,{"digest":digest},actor)
        return {"ok":True,"node":self.get_node(nid)}
    def get_node(self,node_id):
        node_id=_id(node_id,"node_id")
        with self._connect() as db: r=db.execute("SELECT * FROM rn_nodes WHERE id=?",(node_id,)).fetchone()
        if not r: raise ReplicationNetworkError("Node not found.",404)
        d=json.loads(r["definition_json"]); return {"id":r["id"],"projectId":r["project_id"],"status":r["status"],"digest":r["digest"],"createdAt":r["created_at"],"updatedAt":r["updated_at"],**d}
    def list_nodes(self,project_id,include_archived=False,limit=100):
        project_id=_id(project_id,"project_id"); q="SELECT id FROM rn_nodes WHERE project_id=?"+("" if include_archived else " AND status<>'archived'")+" ORDER BY created_at DESC LIMIT ?"
        with self._connect() as db: ids=[r[0] for r in db.execute(q,(project_id,max(1,min(int(limit),1000)))).fetchall()]
        return {"ok":True,"nodes":[self.get_node(i) for i in ids],"count":len(ids)}
    def archive_node(self,node_id,actor="human"):
        node=self.get_node(node_id)
        with self._lock,self._connect() as db: db.execute("UPDATE rn_nodes SET status='archived',updated_at=? WHERE id=?",(_now(),node_id)); self._event(db,node["projectId"],"node.archived",node_id,{},actor)
        return {"ok":True,"node":self.get_node(node_id)}
    def create_network(self,project_id,payload,actor="human"):
        project_id=_id(project_id,"project_id"); definition=_network_definition(payload)
        if definition["anchorStudyId"] and self.cross_study is not None: self.cross_study.get_study(definition["anchorStudyId"])
        if definition["metaExperimentId"] and self.cross_study is not None: self.cross_study.get_workspace(definition["metaExperimentId"])
        nid="network:"+uuid.uuid4().hex; now=_now(); digest=_sha(definition)
        with self._lock,self._connect() as db:
            if self._count(db,"rn_networks")>=self.max_networks: raise ReplicationNetworkError("Replication network limit reached.",409)
            db.execute("INSERT INTO rn_networks VALUES(?,?,?,?,?,?,?,NULL)",(nid,project_id,"draft",json.dumps(definition,sort_keys=True),digest,now,now)); self._event(db,project_id,"network.created",nid,{"digest":digest},actor)
        return {"ok":True,"network":self.get_network(nid)}
    def get_network(self,network_id):
        network_id=_id(network_id,"network_id")
        with self._connect() as db:
            r=db.execute("SELECT * FROM rn_networks WHERE id=?",(network_id,)).fetchone()
            members=db.execute("SELECT node_id,role,joined_at,actor FROM rn_memberships WHERE network_id=? ORDER BY joined_at",(network_id,)).fetchall()
            plans=db.execute("SELECT id,status,definition_json,digest,created_at,updated_at FROM rn_plans WHERE network_id=? ORDER BY created_at",(network_id,)).fetchall()
        if not r: raise ReplicationNetworkError("Replication network not found.",404)
        d=json.loads(r["definition_json"]); return {"id":r["id"],"projectId":r["project_id"],"status":r["status"],"digest":r["digest"],"createdAt":r["created_at"],"updatedAt":r["updated_at"],"frozenAt":r["frozen_at"],**d,
            "members":[{"nodeId":x["node_id"],"role":x["role"],"joinedAt":x["joined_at"],"actor":x["actor"]} for x in members],
            "plans":[{"id":x["id"],"status":x["status"],"digest":x["digest"],"createdAt":x["created_at"],"updatedAt":x["updated_at"],**json.loads(x["definition_json"])} for x in plans]}
    def list_networks(self,project_id,include_archived=False,limit=100):
        project_id=_id(project_id,"project_id"); q="SELECT id FROM rn_networks WHERE project_id=?"+("" if include_archived else " AND status<>'archived'")+" ORDER BY created_at DESC LIMIT ?"
        with self._connect() as db: ids=[r[0] for r in db.execute(q,(project_id,max(1,min(int(limit),1000)))).fetchall()]
        return {"ok":True,"networks":[self.get_network(i) for i in ids],"count":len(ids)}
    def add_node(self,network_id,payload,actor="human"):
        net=self.get_network(network_id)
        if net["status"]!="draft": raise ReplicationNetworkError("Network membership is frozen.",409)
        node=self.get_node(payload.get("nodeId"));
        if node["projectId"]!=net["projectId"]: raise ReplicationNetworkError("Node and network must belong to the same project.",409)
        role=_text(payload.get("role") or "replication-site","role",120,True)
        with self._lock,self._connect() as db:
            db.execute("INSERT OR REPLACE INTO rn_memberships(network_id,node_id,role,joined_at,actor) VALUES(?,?,?,?,?)",(network_id,node["id"],role,_now(),actor)); self._event(db,net["projectId"],"network.node-linked",network_id,{"nodeId":node["id"],"role":role},actor)
        return {"ok":True,"network":self.get_network(network_id)}
    def freeze_network(self,network_id,actor="human"):
        net=self.get_network(network_id)
        if not net["members"]: raise ReplicationNetworkError("At least one replication node is required before freezing.",409)
        with self._lock,self._connect() as db: now=_now(); db.execute("UPDATE rn_networks SET status='frozen',frozen_at=?,updated_at=? WHERE id=?",(now,now,network_id)); self._event(db,net["projectId"],"network.frozen",network_id,{"memberCount":len(net["members"])},actor)
        return {"ok":True,"network":self.get_network(network_id)}
    def create_plan(self,network_id,payload,actor="human"):
        net=self.get_network(network_id); definition=_plan_definition(payload)
        if definition["nodeId"] not in {m["nodeId"] for m in net["members"]}: raise ReplicationNetworkError("Plan node must be a member of the network.",409)
        if self.cross_study is not None: self.cross_study.get_study(definition["sourceStudyId"])
        pid="plan:"+uuid.uuid4().hex; now=_now(); digest=_sha(definition)
        with self._lock,self._connect() as db:
            if self._count(db,"rn_plans")>=self.max_plans: raise ReplicationNetworkError("Replication plan limit reached.",409)
            db.execute("INSERT INTO rn_plans VALUES(?,?,?,?,?,?,?,?)",(pid,network_id,net["projectId"],"planned",json.dumps(definition,sort_keys=True),digest,now,now)); self._event(db,net["projectId"],"plan.created",pid,{"networkId":network_id,"digest":digest},actor)
        return {"ok":True,"plan":self.get_plan(pid)}
    def get_plan(self,plan_id):
        plan_id=_id(plan_id,"plan_id")
        with self._connect() as db: r=db.execute("SELECT * FROM rn_plans WHERE id=?",(plan_id,)).fetchone()
        if not r: raise ReplicationNetworkError("Replication plan not found.",404)
        return {"id":r["id"],"networkId":r["network_id"],"projectId":r["project_id"],"status":r["status"],"digest":r["digest"],"createdAt":r["created_at"],"updatedAt":r["updated_at"],**json.loads(r["definition_json"])}
    def execution_handoff(self,plan_id):
        p=self.get_plan(plan_id); handoff={"schema":HANDOFF_SCHEMA,"version":VERSION,"planId":p["id"],"networkId":p["networkId"],"projectId":p["projectId"],"sourceStudyId":p["sourceStudyId"],"nodeId":p["nodeId"],"protocolRef":p["protocolRef"],"preregistrationRef":p["preregistrationRef"],"plannedMetrics":p["plannedMetrics"],"executionProfile":p["executionProfile"],"targetProduct":"sustainable-catalyst-workspace","automaticDispatch":False,"requiresExplicitUserAction":True,"generatedAt":_now()}; handoff["digest"]=_sha(handoff)
        return {"ok":True,"handoff":handoff}
    def record_result(self,plan_id,payload,actor="human"):
        p=self.get_plan(plan_id); state=str(payload.get("state") or "completed").strip().lower()
        if state not in RESULT_STATES: raise ReplicationNetworkError(f"Unsupported result state: {state}.")
        study_id=_text(payload.get("replicationStudyId"),"replicationStudyId",180,True)
        if self.cross_study is not None:
            study=self.cross_study.get_study(study_id)
            if study.get("study",study).get("projectId",p["projectId"])!=p["projectId"]: raise ReplicationNetworkError("Replication study belongs to a different project.",409)
        record={"schema":RESULT_SCHEMA,"version":VERSION,"replicationStudyId":study_id,"state":state,"resultRefs":_json(payload.get("resultRefs") or [],"resultRefs",500000),"deviations":_text(payload.get("deviations"),"deviations",12000),"notes":_text(payload.get("notes"),"notes",12000),"automaticReplicationJudgment":False,"humanReviewRequired":True}
        rid="result:"+uuid.uuid4().hex; digest=_sha(record); now=_now()
        with self._lock,self._connect() as db:
            db.execute("INSERT INTO rn_results VALUES(?,?,?,?,?,?,?,?,?)",(rid,plan_id,p["networkId"],p["projectId"],state,json.dumps(record,sort_keys=True),digest,now,actor)); db.execute("UPDATE rn_plans SET status=?,updated_at=? WHERE id=?",("completed" if state=="completed" else "in-progress",now,plan_id)); self._event(db,p["projectId"],"result.recorded",rid,{"planId":plan_id,"state":state,"digest":digest},actor)
        return {"ok":True,"result":{"id":rid,"planId":plan_id,"networkId":p["networkId"],"projectId":p["projectId"],"digest":digest,"createdAt":now,**record}}
    def record_review(self,network_id,payload,actor="human"):
        net=self.get_network(network_id); state=str(payload.get("state") or "unreviewed").strip().lower()
        if state not in REVIEW_STATES: raise ReplicationNetworkError(f"Unsupported review state: {state}.")
        plan_id=_text(payload.get("planId"),"planId",180)
        if plan_id: self.get_plan(plan_id)
        record={"schema":REVIEW_SCHEMA,"version":VERSION,"state":state,"planId":plan_id,"rationale":_text(payload.get("rationale"),"rationale",12000,True),"reviewerRef":_text(payload.get("reviewerRef"),"reviewerRef",500),"automaticJudgment":False,"humanAuthored":True}
        rid="review:"+uuid.uuid4().hex; digest=_sha(record); now=_now()
        with self._lock,self._connect() as db: db.execute("INSERT INTO rn_reviews VALUES(?,?,?,?,?,?,?,?)",(rid,network_id,plan_id or None,state,json.dumps(record,sort_keys=True),digest,now,actor)); self._event(db,net["projectId"],"review.recorded",rid,{"networkId":network_id,"state":state},actor)
        return {"ok":True,"review":{"id":rid,"networkId":network_id,"digest":digest,"createdAt":now,**record}}
    def network_view(self,network_id):
        net=self.get_network(network_id)
        with self._connect() as db:
            results=db.execute("SELECT plan_id,state,payload_json,digest,created_at FROM rn_results WHERE network_id=? ORDER BY created_at",(network_id,)).fetchall(); reviews=db.execute("SELECT plan_id,state,payload_json,digest,created_at FROM rn_reviews WHERE network_id=? ORDER BY created_at",(network_id,)).fetchall()
        plan_by_id={p["id"]:p for p in net["plans"]}; nodes={m["nodeId"]:self.get_node(m["nodeId"]) for m in net["members"]}
        edges=[]
        for p in net["plans"]: edges.append({"type":"planned-replication","from":p["sourceStudyId"],"to":p["nodeId"],"planId":p["id"],"protocolRef":p["protocolRef"],"preregistrationRef":p["preregistrationRef"]})
        return {"ok":True,"schema":"sc-lab-independent-replication-network-view/0.158.0","network":net,"nodes":list(nodes.values()),"edges":edges,
                "results":[{"planId":r["plan_id"],"state":r["state"],"digest":r["digest"],"createdAt":r["created_at"],**json.loads(r["payload_json"])} for r in results],
                "reviews":[{"planId":r["plan_id"],"state":r["state"],"digest":r["digest"],"createdAt":r["created_at"],**json.loads(r["payload_json"])} for r in reviews],"boundary":BOUNDARY}
    def coverage(self,network_id):
        view=self.network_view(network_id); plans=view["network"]["plans"]; results=view["results"]
        done={r["planId"] for r in results if r["state"]=="completed"}; declared=sum(1 for n in view["nodes"] if n.get("independenceDeclared"))
        protocols=sorted({p["protocolRef"] for p in plans}); prereg=sorted({p["preregistrationRef"] for p in plans})
        return {"ok":True,"networkId":network_id,"nodeCount":len(view["nodes"]),"planCount":len(plans),"completedPlanCount":len(done),"independenceDeclaredNodeCount":declared,"protocolRefs":protocols,"preregistrationRefs":prereg,
                "completionFraction":(len(done)/len(plans) if plans else 0.0),"independenceCoverageFraction":(declared/len(view["nodes"]) if view["nodes"] else 0.0),"interpretation":"descriptive-only","boundary":BOUNDARY}
    def manifest(self,network_id):
        view=self.network_view(network_id); coverage=self.coverage(network_id)
        payload={"schema":MANIFEST_SCHEMA,"version":VERSION,"network":view["network"],"nodes":view["nodes"],"edges":view["edges"],"results":view["results"],"reviews":view["reviews"],"coverage":coverage,"boundary":BOUNDARY}
        digest=_sha(payload); return {"ok":True,"manifest":payload,"digest":digest}
    def verify_manifest(self,payload):
        if not isinstance(payload,dict): raise ReplicationNetworkError("Manifest verification payload must be an object.")
        manifest=payload.get("manifest"); digest=str(payload.get("digest") or "")
        if not isinstance(manifest,dict) or not digest: raise ReplicationNetworkError("manifest and digest are required.")
        actual=_sha(manifest); return {"ok":True,"verified":actual==digest,"expected":digest,"actual":actual}
    def timeline(self,network_id,limit=500):
        net=self.get_network(network_id)
        with self._connect() as db: rows=db.execute("SELECT seq,kind,object_id,payload_json,created_at,actor FROM rn_events WHERE project_id=? AND (object_id=? OR payload_json LIKE ?) ORDER BY seq DESC LIMIT ?",(net["projectId"],network_id,f"%{network_id}%",max(1,min(int(limit),5000)))).fetchall()
        return {"ok":True,"events":[{"seq":r["seq"],"kind":r["kind"],"objectId":r["object_id"],"payload":json.loads(r["payload_json"]),"createdAt":r["created_at"],"actor":r["actor"]} for r in rows]}
    def archive_network(self,network_id,actor="human"):
        net=self.get_network(network_id)
        with self._lock,self._connect() as db: db.execute("UPDATE rn_networks SET status='archived',updated_at=? WHERE id=?",(_now(),network_id)); self._event(db,net["projectId"],"network.archived",network_id,{},actor)
        return {"ok":True,"network":self.get_network(network_id)}
