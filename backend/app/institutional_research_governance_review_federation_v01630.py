from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.163.0"
INSTITUTION_SCHEMA = "sc-lab-institutional-research-node/0.163.0"
BODY_SCHEMA = "sc-lab-governance-review-body/0.163.0"
FEDERATION_SCHEMA = "sc-lab-governance-federation-link/0.163.0"
CASE_SCHEMA = "sc-lab-institutional-review-case/0.163.0"
ASSIGNMENT_SCHEMA = "sc-lab-federated-review-assignment/0.163.0"
DECISION_SCHEMA = "sc-lab-human-review-decision/0.163.0"
ATTESTATION_SCHEMA = "sc-lab-governance-attestation/0.163.0"
MANIFEST_SCHEMA = "sc-lab-institutional-governance-manifest/0.163.0"
SNAPSHOT_SCHEMA = "sc-lab-institutional-governance-snapshot/0.163.0"

INSTITUTION_STATES = {"active", "limited", "inactive", "retired"}
BODY_TYPES = {"scientific-review-board", "methods-review-board", "ethics-review-board", "data-governance-board", "replication-review-board", "publication-review-board", "other"}
BODY_STATES = {"active", "inactive", "retired"}
FEDERATION_TYPES = {"external-review", "review-reciprocity", "methods-review", "replication-review", "data-governance", "publication-review", "research-collaboration", "other"}
FEDERATION_STATES = {"proposed", "active", "suspended", "closed"}
CASE_TYPES = {"scientific", "methods", "ethics", "data-governance", "replication", "publication", "program-governance", "other"}
CASE_STATES = {"draft", "submitted", "under-review", "revisions-required", "approved", "declined", "closed"}
REVIEWER_ROLES = {"primary", "secondary", "external", "methods", "data-governance", "ethics", "replication", "publication", "observer"}
ASSIGNMENT_STATES = {"assigned", "accepted", "completed", "recused", "withdrawn"}
DECISION_OUTCOMES = {"approve", "revisions-required", "request-more-evidence", "decline", "abstain", "dissent"}
ATTESTATION_TYPES = {"conflict-of-interest", "reviewer-independence", "policy-compliance", "data-governance", "ethics-scope", "publication-boundary", "institutional-signoff", "other"}

BOUNDARY = (
    "Institutional Research Governance & Review Federation records explicit institutions, governance bodies, federated review "
    "relationships, reviewer assignments, independence declarations, human decisions, dissent, sign-off boundaries, and policy "
    "attestations. It does not select reviewers, infer independence, approve ethics, determine scientific validity, resolve dissent, "
    "approve cases automatically, allocate resources or funding, execute research, publish, or exchange credentials. Platform Core "
    "remains canonical object authority; Workspace remains execution authority; Research OS v0.160.0 remains project-lifecycle "
    "authority; v0.161.0 remains program/portfolio authority; and v0.162.0 remains cross-project dependency/resource-planning authority."
)

class InstitutionalGovernanceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _canonical(value: Any) -> bytes: return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
def _sha(value: Any) -> str: return hashlib.sha256(_canonical(value)).hexdigest()
def _id(value: Any, label: str) -> str:
    text=str(value or "").strip(); allowed="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:.'"
    if not text or len(text)>180 or any(ch not in allowed for ch in text): raise InstitutionalGovernanceError(f"Invalid {label}.")
    return text
def _text(value: Any,label:str,maximum:int=16000,required:bool=False)->str:
    text=str(value or "").strip()
    if required and not text: raise InstitutionalGovernanceError(f"{label} is required.")
    if len(text)>maximum: raise InstitutionalGovernanceError(f"{label} exceeds {maximum} characters.")
    return text
def _json(value:Any,label:str,maximum_bytes:int=1_000_000)->Any:
    try: raw=_canonical(value)
    except Exception as exc: raise InstitutionalGovernanceError(f"{label} must be JSON serializable.") from exc
    if len(raw)>maximum_bytes: raise InstitutionalGovernanceError(f"{label} exceeds payload limit.",413)
    return json.loads(raw.decode("utf-8"))

class InstitutionalResearchGovernanceReviewFederationManager:
    def __init__(self,db_path:str,program_portfolio:Any|None=None,resource_planning:Any|None=None,persistent_disk_mounted:bool=False,max_institutions:int=100000,max_bodies:int=250000,max_links:int=250000,max_cases:int=500000,max_assignments:int=1500000,max_decisions:int=2000000,max_attestations:int=2000000,max_snapshots:int=100000,history_limit:int=1000000):
        self.db_path=str(db_path); self.program_portfolio=program_portfolio; self.resource_planning=resource_planning; self.persistent_disk_mounted=bool(persistent_disk_mounted)
        self.max_institutions=max(1,int(max_institutions)); self.max_bodies=max(1,int(max_bodies)); self.max_links=max(1,int(max_links)); self.max_cases=max(1,int(max_cases)); self.max_assignments=max(1,int(max_assignments)); self.max_decisions=max(1,int(max_decisions)); self.max_attestations=max(1,int(max_attestations)); self.max_snapshots=max(1,int(max_snapshots)); self.history_limit=max(100,int(history_limit)); self._lock=threading.RLock(); Path(self.db_path).parent.mkdir(parents=True,exist_ok=True); self._init_db()
    def _connect(self):
        class _ClosingConnection(sqlite3.Connection):
            def __exit__(self,exc_type,exc,tb):
                try:return super().__exit__(exc_type,exc,tb)
                finally:self.close()
        db=sqlite3.connect(self.db_path,timeout=30,check_same_thread=False,factory=_ClosingConnection); db.row_factory=sqlite3.Row; db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA foreign_keys=ON"); return db
    def _init_db(self):
        with self._connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS irgf_institutions(id TEXT PRIMARY KEY,title TEXT NOT NULL,jurisdiction TEXT NOT NULL,state TEXT NOT NULL,canonical_ref TEXT NOT NULL,policies_json TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_bodies(id TEXT PRIMARY KEY,institution_id TEXT NOT NULL,body_type TEXT NOT NULL,title TEXT NOT NULL,mandate TEXT NOT NULL,state TEXT NOT NULL,policy_refs_json TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_links(id TEXT PRIMARY KEY,from_institution_id TEXT NOT NULL,to_institution_id TEXT NOT NULL,relationship_type TEXT NOT NULL,state TEXT NOT NULL,scope TEXT NOT NULL,evidence_ref TEXT NOT NULL,human_authorization INTEGER NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_cases(id TEXT PRIMARY KEY,institution_id TEXT NOT NULL,body_id TEXT NOT NULL,case_type TEXT NOT NULL,title TEXT NOT NULL,scope TEXT NOT NULL,program_id TEXT NOT NULL,project_id TEXT NOT NULL,source_refs_json TEXT NOT NULL,state TEXT NOT NULL,resolution_note TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_assignments(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,reviewer_id TEXT NOT NULL,affiliation_institution_id TEXT NOT NULL,role TEXT NOT NULL,state TEXT NOT NULL,independence_declaration TEXT NOT NULL,independence_evidence_ref TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_decisions(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,assignment_id TEXT NOT NULL,outcome TEXT NOT NULL,statement TEXT NOT NULL,evidence_refs_json TEXT NOT NULL,human_authorization INTEGER NOT NULL,created_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_attestations(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,attestation_type TEXT NOT NULL,statement TEXT NOT NULL,evidence_ref TEXT NOT NULL,human_authorization INTEGER NOT NULL,created_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_snapshots(id TEXT PRIMARY KEY,institution_id TEXT NOT NULL,snapshot_json TEXT NOT NULL,digest TEXT NOT NULL,created_at TEXT NOT NULL,actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS irgf_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,institution_id TEXT NOT NULL,kind TEXT NOT NULL,object_id TEXT NOT NULL,payload_json TEXT NOT NULL,created_at TEXT NOT NULL,actor TEXT NOT NULL);
            ''')
    @staticmethod
    def _count(db,table): return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    def _event(self,db,institution_id,kind,object_id,payload,actor): db.execute("INSERT INTO irgf_events(institution_id,kind,object_id,payload_json,created_at,actor) VALUES(?,?,?,?,?,?)",(institution_id,kind,object_id,json.dumps(payload,sort_keys=True),_now(),actor or "human"))
    def health(self):
        return {"ok":True,"version":VERSION,"institutionRegistry":True,"governanceBodyRegistry":True,"federatedReviewRelationships":True,"externalReviewerAssignments":True,"explicitIndependenceDeclarations":True,"humanRecordedDecisions":True,"dissentPreservation":True,"institutionalSignoffBoundaries":True,"policyAttestations":True,"federatedGovernanceCommandCenter":True,"immutableSnapshots":True,"manifestDigestVerification":True,"automaticReviewerSelection":False,"automaticIndependenceInference":False,"automaticEthicsApproval":False,"automaticCaseApproval":False,"automaticDissentResolution":False,"automaticScientificValidity":False,"automaticResourceAllocation":False,"automaticFundingAllocation":False,"automaticExecution":False,"automaticPublication":False,"crossInstitutionCredentialSharing":False,"directRemoteCallbacks":False,"persistentDiskMounted":self.persistent_disk_mounted,"boundary":BOUNDARY}
    def policies(self):
        h=self.health(); return {"ok":True,"version":VERSION,"explicitInstitutionsOnly":True,"explicitGovernanceBodiesOnly":True,"explicitFederationLinksOnly":True,"explicitReviewerAssignmentsOnly":True,"explicitIndependenceDeclarationsOnly":True,"humanDecisionsRequired":True,"dissentIsPreserved":True,"humanCaseTransitionsRequired":True,**{k:v for k,v in h.items() if k.startswith('automatic') or k in {'crossInstitutionCredentialSharing','directRemoteCallbacks','boundary'}}}
    def _institution(self,db,institution_id):
        row=db.execute("SELECT * FROM irgf_institutions WHERE id=?",(_id(institution_id,"institution id"),)).fetchone()
        if not row: raise InstitutionalGovernanceError("Institution not found.",404)
        return self._institution_row(row)
    def _institution_row(self,row): return {"schema":INSTITUTION_SCHEMA,"id":row['id'],"title":row['title'],"jurisdiction":row['jurisdiction'],"state":row['state'],"canonicalRef":row['canonical_ref'],"policies":json.loads(row['policies_json']),"createdAt":row['created_at'],"updatedAt":row['updated_at'],"actor":row['actor']}
    def create_institution(self,payload,actor="human"):
        iid=_id(payload.get('institutionId') or f"institution:{uuid.uuid4().hex}","institution id"); title=_text(payload.get('title'),'title',500,True); jurisdiction=_text(payload.get('jurisdiction'),'jurisdiction',500,True); state=str(payload.get('state') or 'active')
        if state not in INSTITUTION_STATES: raise InstitutionalGovernanceError("Invalid institution state.")
        policies=_json(payload.get('policies') or [],'policies'); canonical=_text(payload.get('canonicalRef'),'canonicalRef',1000); now=_now()
        with self._lock,self._connect() as db:
            if self._count(db,'irgf_institutions')>=self.max_institutions: raise InstitutionalGovernanceError('Institution limit reached.',409)
            try: db.execute("INSERT INTO irgf_institutions VALUES(?,?,?,?,?,?,?,?,?)",(iid,title,jurisdiction,state,canonical,json.dumps(policies,sort_keys=True),now,now,actor))
            except sqlite3.IntegrityError as exc: raise InstitutionalGovernanceError('Institution already exists.',409) from exc
            self._event(db,iid,'institution.created',iid,{"state":state},actor); out=self._institution(db,iid)
        return {"ok":True,"institution":out}
    def list_institutions(self,limit=1000):
        with self._connect() as db: rows=db.execute("SELECT * FROM irgf_institutions ORDER BY created_at DESC LIMIT ?",(max(1,min(int(limit),5000)),)).fetchall()
        return {"ok":True,"institutions":[self._institution_row(r) for r in rows],"count":len(rows)}
    def set_institution_state(self,institution_id,payload,actor="human"):
        state=str(payload.get('state') or '')
        if state not in INSTITUTION_STATES: raise InstitutionalGovernanceError('Invalid institution state.')
        if not bool(payload.get('humanAuthorization')): raise InstitutionalGovernanceError('Institution state changes require explicit human authorization.',409)
        with self._lock,self._connect() as db:
            self._institution(db,institution_id); now=_now(); db.execute("UPDATE irgf_institutions SET state=?,updated_at=?,actor=? WHERE id=?",(state,now,actor,institution_id)); self._event(db,institution_id,'institution.state',institution_id,{"state":state},actor); out=self._institution(db,institution_id)
        return {"ok":True,"institution":out}
    def _body_row(self,row): return {"schema":BODY_SCHEMA,"id":row['id'],"institutionId":row['institution_id'],"bodyType":row['body_type'],"title":row['title'],"mandate":row['mandate'],"state":row['state'],"policyRefs":json.loads(row['policy_refs_json']),"createdAt":row['created_at'],"updatedAt":row['updated_at'],"actor":row['actor']}
    def create_body(self,institution_id,payload,actor="human"):
        institution_id=_id(institution_id,'institution id'); bid=_id(payload.get('bodyId') or f"review-body:{uuid.uuid4().hex}",'body id'); typ=str(payload.get('bodyType') or 'scientific-review-board'); state=str(payload.get('state') or 'active')
        if typ not in BODY_TYPES or state not in BODY_STATES: raise InstitutionalGovernanceError('Invalid review body type or state.')
        title=_text(payload.get('title'),'title',500,True); mandate=_text(payload.get('mandate'),'mandate',16000,True); refs=_json(payload.get('policyRefs') or [],'policyRefs'); now=_now()
        with self._lock,self._connect() as db:
            self._institution(db,institution_id)
            if self._count(db,'irgf_bodies')>=self.max_bodies: raise InstitutionalGovernanceError('Governance body limit reached.',409)
            try: db.execute("INSERT INTO irgf_bodies VALUES(?,?,?,?,?,?,?,?,?,?)",(bid,institution_id,typ,title,mandate,state,json.dumps(refs,sort_keys=True),now,now,actor))
            except sqlite3.IntegrityError as exc: raise InstitutionalGovernanceError('Governance body already exists.',409) from exc
            self._event(db,institution_id,'body.created',bid,{"bodyType":typ},actor); row=db.execute("SELECT * FROM irgf_bodies WHERE id=?",(bid,)).fetchone()
        return {"ok":True,"body":self._body_row(row)}
    def list_bodies(self,institution_id,limit=1000):
        institution_id=_id(institution_id,'institution id')
        with self._connect() as db: self._institution(db,institution_id); rows=db.execute("SELECT * FROM irgf_bodies WHERE institution_id=? ORDER BY created_at DESC LIMIT ?",(institution_id,max(1,min(int(limit),5000)))).fetchall()
        return {"ok":True,"bodies":[self._body_row(r) for r in rows],"count":len(rows)}
    def _link_row(self,row): return {"schema":FEDERATION_SCHEMA,"id":row['id'],"fromInstitutionId":row['from_institution_id'],"toInstitutionId":row['to_institution_id'],"relationshipType":row['relationship_type'],"state":row['state'],"scope":row['scope'],"evidenceRef":row['evidence_ref'],"humanAuthorization":bool(row['human_authorization']),"createdAt":row['created_at'],"updatedAt":row['updated_at'],"actor":row['actor']}
    def create_federation_link(self,payload,actor="human"):
        a=_id(payload.get('fromInstitutionId'),'from institution id'); b=_id(payload.get('toInstitutionId'),'to institution id')
        if a==b: raise InstitutionalGovernanceError('Federation link requires two distinct institutions.')
        typ=str(payload.get('relationshipType') or 'external-review'); state=str(payload.get('state') or 'proposed')
        if typ not in FEDERATION_TYPES or state not in FEDERATION_STATES: raise InstitutionalGovernanceError('Invalid federation link type or state.')
        if state=='active' and not bool(payload.get('humanAuthorization')): raise InstitutionalGovernanceError('Activating a federation link requires explicit human authorization.',409)
        lid=_id(payload.get('linkId') or f"federation-link:{uuid.uuid4().hex}",'link id'); scope=_text(payload.get('scope'),'scope',16000,True); evidence=_text(payload.get('evidenceRef'),'evidenceRef',1000); now=_now(); auth=bool(payload.get('humanAuthorization'))
        with self._lock,self._connect() as db:
            self._institution(db,a); self._institution(db,b)
            if self._count(db,'irgf_links')>=self.max_links: raise InstitutionalGovernanceError('Federation link limit reached.',409)
            db.execute("INSERT INTO irgf_links VALUES(?,?,?,?,?,?,?,?,?,?,?)",(lid,a,b,typ,state,scope,evidence,int(auth),now,now,actor)); self._event(db,a,'federation.link.created',lid,{"peerInstitutionId":b,"state":state},actor); row=db.execute("SELECT * FROM irgf_links WHERE id=?",(lid,)).fetchone()
        return {"ok":True,"link":self._link_row(row)}
    def list_federation_links(self,institution_id,limit=1000):
        institution_id=_id(institution_id,'institution id')
        with self._connect() as db: self._institution(db,institution_id); rows=db.execute("SELECT * FROM irgf_links WHERE from_institution_id=? OR to_institution_id=? ORDER BY created_at DESC LIMIT ?",(institution_id,institution_id,max(1,min(int(limit),5000)))).fetchall()
        return {"ok":True,"links":[self._link_row(r) for r in rows],"count":len(rows)}
    def _case_row(self,row): return {"schema":CASE_SCHEMA,"id":row['id'],"institutionId":row['institution_id'],"bodyId":row['body_id'],"caseType":row['case_type'],"title":row['title'],"scope":row['scope'],"programId":row['program_id'],"projectId":row['project_id'],"sourceRefs":json.loads(row['source_refs_json']),"state":row['state'],"resolutionNote":row['resolution_note'],"createdAt":row['created_at'],"updatedAt":row['updated_at'],"actor":row['actor']}
    def create_case(self,institution_id,payload,actor="human"):
        institution_id=_id(institution_id,'institution id'); body_id=_id(payload.get('bodyId'),'body id'); typ=str(payload.get('caseType') or 'scientific')
        if typ not in CASE_TYPES: raise InstitutionalGovernanceError('Invalid review case type.')
        cid=_id(payload.get('caseId') or f"review-case:{uuid.uuid4().hex}",'case id'); title=_text(payload.get('title'),'title',500,True); scope=_text(payload.get('scope'),'scope',16000,True); program=_text(payload.get('programId'),'programId',180); project=_text(payload.get('projectId'),'projectId',180); refs=_json(payload.get('sourceRefs') or [],'sourceRefs'); now=_now()
        with self._lock,self._connect() as db:
            self._institution(db,institution_id); body=db.execute("SELECT * FROM irgf_bodies WHERE id=? AND institution_id=?",(body_id,institution_id)).fetchone()
            if not body: raise InstitutionalGovernanceError('Governance body not found for institution.',404)
            if program and self.program_portfolio is not None:
                try:self.program_portfolio.get_program(program)
                except Exception as exc: raise InstitutionalGovernanceError('Referenced research program not found.',404) from exc
            if self._count(db,'irgf_cases')>=self.max_cases: raise InstitutionalGovernanceError('Review case limit reached.',409)
            db.execute("INSERT INTO irgf_cases VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cid,institution_id,body_id,typ,title,scope,program,project,json.dumps(refs,sort_keys=True),'draft','',now,now,actor)); self._event(db,institution_id,'case.created',cid,{"caseType":typ},actor); row=db.execute("SELECT * FROM irgf_cases WHERE id=?",(cid,)).fetchone()
        return {"ok":True,"case":self._case_row(row)}
    def get_case(self,case_id):
        case_id=_id(case_id,'case id')
        with self._connect() as db:
            row=db.execute("SELECT * FROM irgf_cases WHERE id=?",(case_id,)).fetchone()
            if not row: raise InstitutionalGovernanceError('Review case not found.',404)
            case=self._case_row(row); assignments=[self._assignment_row(r) for r in db.execute("SELECT * FROM irgf_assignments WHERE case_id=? ORDER BY created_at",(case_id,)).fetchall()]; decisions=[self._decision_row(r) for r in db.execute("SELECT * FROM irgf_decisions WHERE case_id=? ORDER BY created_at",(case_id,)).fetchall()]; attest=[self._attestation_row(r) for r in db.execute("SELECT * FROM irgf_attestations WHERE case_id=? ORDER BY created_at",(case_id,)).fetchall()]
        case.update({"assignments":assignments,"decisions":decisions,"attestations":attest}); return case
    def list_cases(self,institution_id,limit=1000):
        institution_id=_id(institution_id,'institution id')
        with self._connect() as db: self._institution(db,institution_id); rows=db.execute("SELECT * FROM irgf_cases WHERE institution_id=? ORDER BY created_at DESC LIMIT ?",(institution_id,max(1,min(int(limit),5000)))).fetchall()
        return {"ok":True,"cases":[self._case_row(r) for r in rows],"count":len(rows)}
    def _assignment_row(self,row): return {"schema":ASSIGNMENT_SCHEMA,"id":row['id'],"caseId":row['case_id'],"reviewerId":row['reviewer_id'],"affiliationInstitutionId":row['affiliation_institution_id'],"role":row['role'],"state":row['state'],"independenceDeclaration":row['independence_declaration'],"independenceEvidenceRef":row['independence_evidence_ref'],"createdAt":row['created_at'],"updatedAt":row['updated_at'],"actor":row['actor']}
    def assign_reviewer(self,case_id,payload,actor="human"):
        case_id=_id(case_id,'case id'); reviewer=_id(payload.get('reviewerId'),'reviewer id'); role=str(payload.get('role') or 'external')
        if role not in REVIEWER_ROLES: raise InstitutionalGovernanceError('Invalid reviewer role.')
        declaration=_text(payload.get('independenceDeclaration'),'independenceDeclaration',8000,True); affiliation=_text(payload.get('affiliationInstitutionId'),'affiliationInstitutionId',180); evidence=_text(payload.get('independenceEvidenceRef'),'independenceEvidenceRef',1000); aid=_id(payload.get('assignmentId') or f"review-assignment:{uuid.uuid4().hex}",'assignment id'); now=_now()
        with self._lock,self._connect() as db:
            case=db.execute("SELECT * FROM irgf_cases WHERE id=?",(case_id,)).fetchone()
            if not case: raise InstitutionalGovernanceError('Review case not found.',404)
            if case['state'] in {'approved','declined','closed'}: raise InstitutionalGovernanceError('Cannot assign a reviewer to a terminal case.',409)
            if affiliation:
                self._institution(db,affiliation)
            if self._count(db,'irgf_assignments')>=self.max_assignments: raise InstitutionalGovernanceError('Reviewer assignment limit reached.',409)
            db.execute("INSERT INTO irgf_assignments VALUES(?,?,?,?,?,?,?,?,?,?,?)",(aid,case_id,reviewer,affiliation,role,'assigned',declaration,evidence,now,now,actor)); self._event(db,case['institution_id'],'reviewer.assigned',aid,{"caseId":case_id,"role":role},actor); row=db.execute("SELECT * FROM irgf_assignments WHERE id=?",(aid,)).fetchone()
        return {"ok":True,"assignment":self._assignment_row(row),"independenceInferred":False}
    def set_assignment_state(self,assignment_id,payload,actor="human"):
        assignment_id=_id(assignment_id,'assignment id'); state=str(payload.get('state') or '')
        if state not in ASSIGNMENT_STATES: raise InstitutionalGovernanceError('Invalid assignment state.')
        if not bool(payload.get('humanAuthorization')): raise InstitutionalGovernanceError('Assignment state changes require explicit human authorization.',409)
        with self._lock,self._connect() as db:
            row=db.execute("SELECT a.*,c.institution_id FROM irgf_assignments a JOIN irgf_cases c ON c.id=a.case_id WHERE a.id=?",(assignment_id,)).fetchone()
            if not row: raise InstitutionalGovernanceError('Review assignment not found.',404)
            now=_now(); db.execute("UPDATE irgf_assignments SET state=?,updated_at=?,actor=? WHERE id=?",(state,now,actor,assignment_id)); self._event(db,row['institution_id'],'reviewer.assignment.state',assignment_id,{"state":state},actor); out=db.execute("SELECT * FROM irgf_assignments WHERE id=?",(assignment_id,)).fetchone()
        return {"ok":True,"assignment":self._assignment_row(out)}
    def _decision_row(self,row): return {"schema":DECISION_SCHEMA,"id":row['id'],"caseId":row['case_id'],"assignmentId":row['assignment_id'],"outcome":row['outcome'],"statement":row['statement'],"evidenceRefs":json.loads(row['evidence_refs_json']),"humanAuthorization":bool(row['human_authorization']),"createdAt":row['created_at'],"actor":row['actor']}
    def record_decision(self,case_id,payload,actor="human"):
        case_id=_id(case_id,'case id'); assignment_id=_id(payload.get('assignmentId'),'assignment id'); outcome=str(payload.get('outcome') or '')
        if outcome not in DECISION_OUTCOMES: raise InstitutionalGovernanceError('Invalid review decision outcome.')
        if not bool(payload.get('humanAuthorization')): raise InstitutionalGovernanceError('Review decisions require explicit human authorization.',409)
        statement=_text(payload.get('statement'),'statement',32000,True); refs=_json(payload.get('evidenceRefs') or [],'evidenceRefs'); did=_id(payload.get('decisionId') or f"review-decision:{uuid.uuid4().hex}",'decision id'); now=_now()
        with self._lock,self._connect() as db:
            case=db.execute("SELECT * FROM irgf_cases WHERE id=?",(case_id,)).fetchone(); assignment=db.execute("SELECT * FROM irgf_assignments WHERE id=? AND case_id=?",(assignment_id,case_id)).fetchone()
            if not case or not assignment: raise InstitutionalGovernanceError('Review case or assignment not found.',404)
            if assignment['state'] in {'recused','withdrawn'}: raise InstitutionalGovernanceError('Recused or withdrawn reviewers cannot record decisions.',409)
            if self._count(db,'irgf_decisions')>=self.max_decisions: raise InstitutionalGovernanceError('Decision limit reached.',409)
            db.execute("INSERT INTO irgf_decisions VALUES(?,?,?,?,?,?,?,?,?)",(did,case_id,assignment_id,outcome,statement,json.dumps(refs,sort_keys=True),1,now,actor)); db.execute("UPDATE irgf_assignments SET state='completed',updated_at=?,actor=? WHERE id=?",(now,actor,assignment_id)); self._event(db,case['institution_id'],'review.decision',did,{"caseId":case_id,"outcome":outcome},actor); row=db.execute("SELECT * FROM irgf_decisions WHERE id=?",(did,)).fetchone()
        return {"ok":True,"decision":self._decision_row(row),"caseStateChangedAutomatically":False,"dissentPreserved":outcome=='dissent'}
    def _attestation_row(self,row): return {"schema":ATTESTATION_SCHEMA,"id":row['id'],"caseId":row['case_id'],"attestationType":row['attestation_type'],"statement":row['statement'],"evidenceRef":row['evidence_ref'],"humanAuthorization":bool(row['human_authorization']),"createdAt":row['created_at'],"actor":row['actor']}
    def add_attestation(self,case_id,payload,actor="human"):
        case_id=_id(case_id,'case id'); typ=str(payload.get('attestationType') or 'other')
        if typ not in ATTESTATION_TYPES: raise InstitutionalGovernanceError('Invalid attestation type.')
        if not bool(payload.get('humanAuthorization')): raise InstitutionalGovernanceError('Governance attestations require explicit human authorization.',409)
        statement=_text(payload.get('statement'),'statement',32000,True); evidence=_text(payload.get('evidenceRef'),'evidenceRef',1000); aid=_id(payload.get('attestationId') or f"governance-attestation:{uuid.uuid4().hex}",'attestation id'); now=_now()
        with self._lock,self._connect() as db:
            case=db.execute("SELECT * FROM irgf_cases WHERE id=?",(case_id,)).fetchone()
            if not case: raise InstitutionalGovernanceError('Review case not found.',404)
            db.execute("INSERT INTO irgf_attestations VALUES(?,?,?,?,?,?,?,?)",(aid,case_id,typ,statement,evidence,1,now,actor)); self._event(db,case['institution_id'],'governance.attestation',aid,{"caseId":case_id,"attestationType":typ},actor); row=db.execute("SELECT * FROM irgf_attestations WHERE id=?",(aid,)).fetchone()
        return {"ok":True,"attestation":self._attestation_row(row)}
    def transition_case(self,case_id,payload,actor="human"):
        case_id=_id(case_id,'case id'); target=str(payload.get('targetState') or ''); reason=_text(payload.get('reason'),'reason',16000,True); resolution=_text(payload.get('resolutionNote'),'resolutionNote',32000); auth=bool(payload.get('humanAuthorization'))
        if target not in CASE_STATES: raise InstitutionalGovernanceError('Invalid review case state.')
        if not auth: raise InstitutionalGovernanceError('Case transitions require explicit human authorization.',409)
        allowed={'draft':{'submitted','closed'},'submitted':{'under-review','closed'},'under-review':{'revisions-required','approved','declined','closed'},'revisions-required':{'under-review','closed'},'approved':{'closed'},'declined':{'closed'},'closed':set()}
        with self._lock,self._connect() as db:
            row=db.execute("SELECT * FROM irgf_cases WHERE id=?",(case_id,)).fetchone()
            if not row: raise InstitutionalGovernanceError('Review case not found.',404)
            if target not in allowed[row['state']]: raise InstitutionalGovernanceError(f"Invalid case transition {row['state']} -> {target}.",409)
            if target in {'approved','declined'}:
                n=int(db.execute("SELECT COUNT(*) FROM irgf_decisions WHERE case_id=?",(case_id,)).fetchone()[0])
                if n<1: raise InstitutionalGovernanceError('Terminal review outcomes require at least one explicit human reviewer decision.',409)
            now=_now(); db.execute("UPDATE irgf_cases SET state=?,resolution_note=?,updated_at=?,actor=? WHERE id=?",(target,resolution,now,actor,case_id)); self._event(db,row['institution_id'],'case.transition',case_id,{"fromState":row['state'],"toState":target,"reason":reason,"resolutionNote":resolution},actor); out=db.execute("SELECT * FROM irgf_cases WHERE id=?",(case_id,)).fetchone()
        return {"ok":True,"case":self._case_row(out),"automaticApproval":False,"scientificValidityInferred":False}
    def command_center(self,institution_id):
        institution_id=_id(institution_id,'institution id')
        with self._connect() as db:
            inst=self._institution(db,institution_id); bodies=int(db.execute("SELECT COUNT(*) FROM irgf_bodies WHERE institution_id=?",(institution_id,)).fetchone()[0]); links=int(db.execute("SELECT COUNT(*) FROM irgf_links WHERE from_institution_id=? OR to_institution_id=?",(institution_id,institution_id)).fetchone()[0]); cases=[self._case_row(r) for r in db.execute("SELECT * FROM irgf_cases WHERE institution_id=? ORDER BY updated_at DESC LIMIT 500",(institution_id,)).fetchall()]; open_case_ids=[x['id'] for x in cases if x['state'] not in {'approved','declined','closed'}]; outstanding=0; dissent=0
            if open_case_ids:
                qs=','.join('?' for _ in open_case_ids); outstanding=int(db.execute(f"SELECT COUNT(*) FROM irgf_assignments WHERE case_id IN ({qs}) AND state IN ('assigned','accepted')",open_case_ids).fetchone()[0]); dissent=int(db.execute(f"SELECT COUNT(*) FROM irgf_decisions WHERE case_id IN ({qs}) AND outcome='dissent'",open_case_ids).fetchone()[0])
        return {"ok":True,"version":VERSION,"institution":inst,"governanceBodyCount":bodies,"federationLinkCount":links,"reviewCaseCount":len(cases),"openReviewCaseCount":len(open_case_ids),"outstandingReviewerAssignmentCount":outstanding,"openDissentCount":dissent,"cases":cases,"descriptiveOnly":True,"automaticReviewerSelection":False,"automaticCaseApproval":False,"automaticScientificValidity":False,"boundary":BOUNDARY}
    def manifest(self,institution_id):
        institution_id=_id(institution_id,'institution id')
        with self._connect() as db:
            inst=self._institution(db,institution_id); bodies=[self._body_row(r) for r in db.execute("SELECT * FROM irgf_bodies WHERE institution_id=? ORDER BY id",(institution_id,)).fetchall()]; links=[self._link_row(r) for r in db.execute("SELECT * FROM irgf_links WHERE from_institution_id=? OR to_institution_id=? ORDER BY id",(institution_id,institution_id)).fetchall()]; cases=[self._case_row(r) for r in db.execute("SELECT * FROM irgf_cases WHERE institution_id=? ORDER BY id",(institution_id,)).fetchall()]; case_ids=[x['id'] for x in cases]; assignments=[]; decisions=[]; attest=[]
            for cid in case_ids:
                assignments += [self._assignment_row(r) for r in db.execute("SELECT * FROM irgf_assignments WHERE case_id=? ORDER BY id",(cid,)).fetchall()]; decisions += [self._decision_row(r) for r in db.execute("SELECT * FROM irgf_decisions WHERE case_id=? ORDER BY id",(cid,)).fetchall()]; attest += [self._attestation_row(r) for r in db.execute("SELECT * FROM irgf_attestations WHERE case_id=? ORDER BY id",(cid,)).fetchall()]
        body={"schema":MANIFEST_SCHEMA,"version":VERSION,"institution":inst,"governanceBodies":bodies,"federationLinks":links,"reviewCases":cases,"reviewerAssignments":assignments,"reviewDecisions":decisions,"attestations":attest,"boundary":BOUNDARY}; return {"ok":True,"manifest":body,"digest":_sha(body)}
    def verify_manifest(self,payload):
        manifest=payload.get('manifest') if isinstance(payload,dict) else None; digest=str(payload.get('digest') or '') if isinstance(payload,dict) else ''
        if not isinstance(manifest,dict): raise InstitutionalGovernanceError('manifest is required.')
        actual=_sha(manifest); return {"ok":True,"valid":bool(digest) and actual==digest,"expectedDigest":digest,"actualDigest":actual}
    def snapshot(self,institution_id,payload,actor="human"):
        if not bool(payload.get('humanAuthorization')): raise InstitutionalGovernanceError('Institutional governance snapshots require explicit human authorization.',409)
        m=self.manifest(institution_id); sid=_id(payload.get('snapshotId') or f"governance-snapshot:{uuid.uuid4().hex}",'snapshot id'); now=_now(); body={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"manifest":m['manifest'],"manifestDigest":m['digest'],"note":_text(payload.get('note'),'note',16000)}; digest=_sha(body)
        with self._lock,self._connect() as db:
            if self._count(db,'irgf_snapshots')>=self.max_snapshots: raise InstitutionalGovernanceError('Snapshot limit reached.',409)
            db.execute("INSERT INTO irgf_snapshots VALUES(?,?,?,?,?,?)",(sid,institution_id,json.dumps(body,sort_keys=True),digest,now,actor)); self._event(db,institution_id,'snapshot.created',sid,{"digest":digest},actor)
        return {"ok":True,"snapshot":{"id":sid,"institutionId":institution_id,"body":body,"digest":digest,"createdAt":now,"actor":actor}}
    def get_snapshot(self,snapshot_id):
        snapshot_id=_id(snapshot_id,'snapshot id')
        with self._connect() as db: row=db.execute("SELECT * FROM irgf_snapshots WHERE id=?",(snapshot_id,)).fetchone()
        if not row: raise InstitutionalGovernanceError('Snapshot not found.',404)
        return {"ok":True,"snapshot":{"id":row['id'],"institutionId":row['institution_id'],"body":json.loads(row['snapshot_json']),"digest":row['digest'],"createdAt":row['created_at'],"actor":row['actor']}}
    def timeline(self,institution_id,limit=500):
        institution_id=_id(institution_id,'institution id')
        with self._connect() as db: self._institution(db,institution_id); rows=db.execute("SELECT * FROM irgf_events WHERE institution_id=? ORDER BY seq DESC LIMIT ?",(institution_id,max(1,min(int(limit),5000)))).fetchall()
        events=[{"seq":r['seq'],"kind":r['kind'],"objectId":r['object_id'],"payload":json.loads(r['payload_json']),"createdAt":r['created_at'],"actor":r['actor']} for r in rows]
        return {"ok":True,"institutionId":institution_id,"events":events,"count":len(events)}
