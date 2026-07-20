from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.40.2"
CURRENT_RELEASE = "0.40.2"
SUPPORTED_BASELINES = ("0.31.0", "0.31.1", "0.38.0", "0.38.1", "0.38.2", "0.39.0", "0.39.1", "0.39.2", "0.39.3", "0.40.0", "0.40.1")
REQUIRED_CLEAN_INSTALL_CHECKS = (
    "source-integrity", "database-bootstrap", "api-health", "wordpress-activation",
    "sdk-discovery", "offline-shell-opt-in", "security-headers", "documentation",
)
REQUIRED_RELEASE_EVIDENCE = (
    "migration", "compatibility", "cleanInstall", "rollback", "security",
    "licensing", "documentation", "archives", "tests",
)


class PublicReleaseHardeningError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _clean_id(value: Any, label: str) -> str:
    text=str(value or "").strip().lower(); allowed="abcdefghijklmnopqrstuvwxyz0123456789-_.:"
    if not text or len(text)>180 or any(ch not in allowed for ch in text):
        raise PublicReleaseHardeningError(f"Invalid {label}.")
    return text


def _clean_text(value: Any, label: str, maximum: int=8000, required: bool=True) -> str:
    text=str(value or "").strip()
    if required and not text: raise PublicReleaseHardeningError(f"{label} is required.")
    if len(text)>maximum: raise PublicReleaseHardeningError(f"{label} exceeds {maximum} characters.")
    return text


def _reject_sensitive(value: Any, path: str="payload", depth: int=0) -> None:
    if depth>20: raise PublicReleaseHardeningError("Payload nesting exceeds the release-hardening boundary.")
    if isinstance(value,dict):
        for key,child in value.items():
            normalized=re.sub(r"(?<!^)(?=[A-Z])", "_", str(key)).lower().replace("-","_")
            if any(part in normalized for part in ("password","secret","credential","private_key","access_token","refresh_token","authorization","cookie","raw_data","dataset_bytes","executable","callback","script")):
                raise PublicReleaseHardeningError(f"Sensitive or executable field is not permitted: {path}.{key}")
            _reject_sensitive(child,f"{path}.{key}",depth+1)
    elif isinstance(value,list):
        if len(value)>10000: raise PublicReleaseHardeningError("Payload contains too many list items.")
        for i,child in enumerate(value): _reject_sensitive(child,f"{path}[{i}]",depth+1)
    elif isinstance(value,str):
        lowered=value.lower()
        if "-----begin private key-----" in lowered or "<script" in lowered or "javascript:" in lowered:
            raise PublicReleaseHardeningError("Executable or private-key material is not permitted.")
        if len(value)>250000: raise PublicReleaseHardeningError("Payload text exceeds the release-hardening boundary.")


def policies(persistent_disk_mounted: bool, allow_execution: bool=False) -> dict[str,Any]:
    return {
        "ok": True, "version": VERSION, "releaseStage": "public-release-hardening",
        "persistentDiskMounted": bool(persistent_disk_mounted),
        "migrationExecutionEnabled": bool(allow_execution),
        "migrationDefaultMode": "dry-run", "forcePushPermitted": False,
        "productionFilesMayBeOverwrittenByApi": False,
        "supportedBaselines": list(SUPPORTED_BASELINES),
        "requiredCleanInstallChecks": list(REQUIRED_CLEAN_INSTALL_CHECKS),
        "requiredReleaseEvidence": list(REQUIRED_RELEASE_EVIDENCE),
        "capabilities": {
            "upgradeAssessment": True, "compatibilityMatrices": True,
            "deprecationRegistry": True, "cleanInstallCertification": True,
            "rollbackEvidence": True, "releaseCandidateGate": True,
            "documentationGate": True, "securityLicensingGate": True,
        },
    }


class PublicReleaseHardeningManager:
    def __init__(self, db_path: str, persistent_disk_mounted: bool, allow_execution: bool=False, history_limit: int=250000) -> None:
        self.db_path=str(db_path); self.persistent_disk_mounted=bool(persistent_disk_mounted)
        self.allow_execution=bool(allow_execution); self.history_limit=max(100,int(history_limit)); self._lock=threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True,exist_ok=True); self._init_db()

    def _connect(self):
        db=sqlite3.connect(self.db_path,timeout=30,check_same_thread=False); db.row_factory=sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA foreign_keys=ON"); return db

    def _init_db(self):
        with self._connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS compatibility_matrices(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS migration_assessments(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, baseline TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS deprecations(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS clean_install_reports(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS rollback_plans(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS release_candidate_reports(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, record_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS release_hardening_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,actor TEXT NOT NULL,subject_type TEXT NOT NULL,subject_id TEXT NOT NULL,occurred_at TEXT NOT NULL,payload_json TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL);
            ''')

    def _event(self,db,event_type,actor,subject_type,subject_id,payload):
        row=db.execute("SELECT event_hash FROM release_hardening_events ORDER BY seq DESC LIMIT 1").fetchone(); previous=str(row['event_hash']) if row else ''
        occurred=_now(); envelope={"eventType":event_type,"actor":actor,"subjectType":subject_type,"subjectId":subject_id,"occurredAt":occurred,"payload":payload,"previousHash":previous}; event_hash=_sha(envelope)
        db.execute("INSERT INTO release_hardening_events(event_type,actor,subject_type,subject_id,occurred_at,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",(event_type,actor,subject_type,subject_id,occurred,json.dumps(payload,sort_keys=True),previous,event_hash))
        db.execute("DELETE FROM release_hardening_events WHERE seq NOT IN (SELECT seq FROM release_hardening_events ORDER BY seq DESC LIMIT ?)",(self.history_limit,))

    def _store(self,table,payload,actor,status,extra=()):
        record=dict(payload); record_hash=_sha(record); values=(record['id'],record['createdAt'],actor,*extra,status,json.dumps(record,sort_keys=True),record_hash)
        cols={
          'compatibility_matrices':'id,created_at,actor,status,payload_json,record_hash',
          'migration_assessments':'id,created_at,actor,baseline,status,payload_json,record_hash',
          'deprecations':'id,created_at,actor,status,payload_json,record_hash',
          'clean_install_reports':'id,created_at,actor,status,payload_json,record_hash',
          'rollback_plans':'id,created_at,actor,status,payload_json,record_hash',
          'release_candidate_reports':'id,created_at,actor,status,payload_json,record_hash',
        }[table]
        q=','.join('?' for _ in values)
        with self._lock,self._connect() as db:
            db.execute(f"INSERT OR REPLACE INTO {table}({cols}) VALUES({q})",values)
            self._event(db,f"{table}.recorded",actor,table,record['id'],{"status":status,"recordHash":record_hash})
        record['recordHash']=record_hash; return record

    def health(self):
        d=self.dashboard(); return {"ok":True,"status":"ready","version":VERSION,"storage":"persistent" if self.persistent_disk_mounted else "instance-local","releaseCandidateReports":d['counts']['releaseCandidates'],"forcePushPermitted":False,"productionFilesMayBeOverwrittenByApi":False}

    def catalog(self):
        return {"ok":True,"version":VERSION,"supportedBaselines":list(SUPPORTED_BASELINES),"compatibilityDimensions":["wordpress","php","python","browser","database","sdk","render"],"cleanInstallChecks":list(REQUIRED_CLEAN_INSTALL_CHECKS),"releaseEvidence":list(REQUIRED_RELEASE_EVIDENCE),"deprecationStates":["announced","active","removed"],"candidateStates":["blocked","release-candidate-ready"]}

    def create_compatibility_matrix(self,payload,actor):
        _reject_sensitive(payload); matrix_id=_clean_id(payload.get('id') or f"compat-{uuid.uuid4().hex[:12]}",'compatibility matrix id')
        dimensions=payload.get('dimensions') or {}; 
        if not isinstance(dimensions,dict) or not dimensions: raise PublicReleaseHardeningError('dimensions must be a non-empty object.')
        normalized={}; blockers=[]
        for name,value in dimensions.items():
            key=_clean_id(name,'compatibility dimension'); item=value if isinstance(value,dict) else {"status":value}
            status=str(item.get('status','unknown')).strip().lower()
            if status not in {'supported','conditional','unsupported','unknown'}: raise PublicReleaseHardeningError(f'Invalid compatibility status for {key}.')
            normalized[key]={"status":status,"minimum":str(item.get('minimum','')).strip(),"maximum":str(item.get('maximum','')).strip(),"notes":str(item.get('notes','')).strip()[:2000]}
            if status in {'unsupported','unknown'}: blockers.append(key)
        record={"id":matrix_id,"schema":"sc-lab-compatibility-matrix/0.40.2","createdAt":_now(),"releaseVersion":CURRENT_RELEASE,"dimensions":normalized,"blockers":sorted(blockers)}
        status='supported' if not blockers else 'blocked'; record['status']=status
        return {"ok":True,"matrix":self._store('compatibility_matrices',record,actor,status)}

    def assess_migration(self,payload,actor):
        _reject_sensitive(payload); assessment_id=_clean_id(payload.get('id') or f"migration-{uuid.uuid4().hex[:12]}",'migration assessment id')
        baseline=str(payload.get('baselineVersion','')).strip(); target=str(payload.get('targetVersion',CURRENT_RELEASE)).strip()
        blockers=[]
        if baseline not in SUPPORTED_BASELINES: blockers.append('unsupported-baseline')
        if target!=CURRENT_RELEASE: blockers.append('target-version-mismatch')
        backup_verified=bool(payload.get('backupVerified',False)); rollback_tested=bool(payload.get('rollbackTested',False))
        if not backup_verified: blockers.append('verified-backup-required')
        if not rollback_tested: blockers.append('rollback-proof-required')
        steps=payload.get('steps') or ["verify-source","backup","apply-schema-migrations","validate-contracts","smoke-test","activate"]
        if not isinstance(steps,list) or not steps: raise PublicReleaseHardeningError('steps must be a non-empty list.')
        record={"id":assessment_id,"schema":"sc-lab-migration-assessment/0.40.2","createdAt":_now(),"baselineVersion":baseline,"targetVersion":target,"mode":"dry-run","executionPermitted":False,"backupVerified":backup_verified,"rollbackTested":rollback_tested,"steps":[str(x)[:180] for x in steps],"blockers":sorted(set(blockers))}
        status='ready' if not blockers else 'blocked'; record['status']=status
        return {"ok":True,"assessment":self._store('migration_assessments',record,actor,status,(baseline,))}

    def register_deprecation(self,payload,actor):
        _reject_sensitive(payload); record_id=_clean_id(payload.get('id') or f"deprecation-{uuid.uuid4().hex[:12]}",'deprecation id')
        state=str(payload.get('status','announced')).strip().lower()
        if state not in {'announced','active','removed'}: raise PublicReleaseHardeningError('Invalid deprecation status.')
        replacement=_clean_text(payload.get('replacement'),'replacement',500,False)
        removal=str(payload.get('removalVersion','')).strip()
        record={"id":record_id,"schema":"sc-lab-deprecation-record/0.40.2","createdAt":_now(),"subject":_clean_text(payload.get('subject'),'subject',500),"status":state,"replacement":replacement,"removalVersion":removal,"migrationGuidance":_clean_text(payload.get('migrationGuidance'),'migrationGuidance',6000,False)}
        return {"ok":True,"deprecation":self._store('deprecations',record,actor,state)}

    def create_clean_install_report(self,payload,actor):
        _reject_sensitive(payload); report_id=_clean_id(payload.get('id') or f"clean-install-{uuid.uuid4().hex[:12]}",'clean install report id')
        checks=payload.get('checks') or []
        if not isinstance(checks,list): raise PublicReleaseHardeningError('checks must be a list.')
        seen={};
        for item in checks:
            if not isinstance(item,dict): continue
            cid=_clean_id(item.get('id'),'clean install check id'); state=str(item.get('status','')).strip().lower(); seen[cid]=state
        missing=[x for x in REQUIRED_CLEAN_INSTALL_CHECKS if x not in seen]; failed=[k for k,v in seen.items() if v!='pass']; blockers=sorted(set(missing+failed))
        record={"id":report_id,"schema":"sc-lab-clean-install-report/0.40.2","createdAt":_now(),"releaseVersion":CURRENT_RELEASE,"checks":[{"id":k,"status":v} for k,v in sorted(seen.items())],"missingChecks":missing,"failedChecks":failed,"blockers":blockers}
        status='passed' if not blockers else 'blocked'; record['status']=status
        return {"ok":True,"report":self._store('clean_install_reports',record,actor,status)}

    def create_rollback_plan(self,payload,actor):
        _reject_sensitive(payload); plan_id=_clean_id(payload.get('id') or f"rollback-{uuid.uuid4().hex[:12]}",'rollback plan id')
        backup_id=_clean_id(payload.get('backupId'),'backup id'); tested=bool(payload.get('tested',False)); restore_verified=bool(payload.get('restoreVerified',False))
        blockers=[]
        if not tested: blockers.append('rollback-not-tested')
        if not restore_verified: blockers.append('restore-not-verified')
        record={"id":plan_id,"schema":"sc-lab-rollback-plan/0.40.2","createdAt":_now(),"releaseVersion":CURRENT_RELEASE,"backupId":backup_id,"tested":tested,"restoreVerified":restore_verified,"activationProcedure":_clean_text(payload.get('activationProcedure'),'activationProcedure',6000),"productionOverwriteByApi":False,"blockers":blockers}
        status='verified' if not blockers else 'blocked'; record['status']=status
        return {"ok":True,"plan":self._store('rollback_plans',record,actor,status)}

    def create_release_candidate(self,payload,actor):
        _reject_sensitive(payload); report_id=_clean_id(payload.get('id') or f"rc-{uuid.uuid4().hex[:12]}",'release candidate id')
        evidence=payload.get('evidence') or {}
        if not isinstance(evidence,dict): raise PublicReleaseHardeningError('evidence must be an object.')
        normalized={}; blockers=[]
        for key in REQUIRED_RELEASE_EVIDENCE:
            value=evidence.get(key); state='missing'
            if isinstance(value,dict): state=str(value.get('status','missing')).strip().lower()
            elif isinstance(value,bool): state='pass' if value else 'fail'
            elif value is not None: state=str(value).strip().lower()
            if state not in {'pass','passed','ready','verified','complete'}: blockers.append(key)
            normalized[key]={"status":state}
        critical=list(payload.get('criticalDefects') or []); high=list(payload.get('highDefects') or [])
        if critical: blockers.append('critical-defects')
        if high: blockers.append('high-defects')
        record={"id":report_id,"schema":"sc-lab-release-candidate-report/0.40.2","createdAt":_now(),"releaseVersion":CURRENT_RELEASE,"evidence":normalized,"criticalDefects":[str(x)[:500] for x in critical],"highDefects":[str(x)[:500] for x in high],"blockers":sorted(set(blockers)),"generalAvailabilityClaim":False}
        status='release-candidate-ready' if not blockers else 'blocked'; record['status']=status
        return {"ok":True,"report":self._store('release_candidate_reports',record,actor,status)}

    def _list(self,table,limit=200):
        limit=max(1,min(int(limit),5000))
        with self._connect() as db: rows=db.execute(f"SELECT payload_json,record_hash FROM {table} ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
        values=[]
        for row in rows:
            value=json.loads(row['payload_json']); value['recordHash']=row['record_hash']; values.append(value)
        return values

    def list_records(self,kind,limit=200):
        table={'compatibility':'compatibility_matrices','migrations':'migration_assessments','deprecations':'deprecations','clean-installs':'clean_install_reports','rollbacks':'rollback_plans','release-candidates':'release_candidate_reports'}.get(kind)
        if not table: raise PublicReleaseHardeningError('Unknown record kind.')
        return {"ok":True,"version":VERSION,"kind":kind,"records":self._list(table,limit)}

    def verify_timeline(self):
        with self._connect() as db: rows=db.execute("SELECT * FROM release_hardening_events ORDER BY seq").fetchall()
        previous=''
        for row in rows:
            payload=json.loads(row['payload_json']); envelope={"eventType":row['event_type'],"actor":row['actor'],"subjectType":row['subject_type'],"subjectId":row['subject_id'],"occurredAt":row['occurred_at'],"payload":payload,"previousHash":row['previous_hash']}
            if row['previous_hash']!=previous or row['event_hash']!=_sha(envelope): return {"ok":True,"valid":False,"failedSequence":row['seq']}
            previous=row['event_hash']
        return {"ok":True,"valid":True,"eventCount":len(rows),"headHash":previous}

    def dashboard(self):
        counts={}
        with self._connect() as db:
            for key,table in [('compatibilityMatrices','compatibility_matrices'),('migrationAssessments','migration_assessments'),('deprecations','deprecations'),('cleanInstalls','clean_install_reports'),('rollbackPlans','rollback_plans'),('releaseCandidates','release_candidate_reports')]: counts[key]=db.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()['c']
            counts['readyCandidates']=db.execute("SELECT COUNT(*) c FROM release_candidate_reports WHERE status='release-candidate-ready'").fetchone()['c']
        return {"ok":True,"version":VERSION,"counts":counts,"timeline":self.verify_timeline(),"forcePushPermitted":False,"productionFilesMayBeOverwrittenByApi":False}
