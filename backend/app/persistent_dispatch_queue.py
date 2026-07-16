from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import hmac
import secrets
import sqlite3
from typing import Any

from .distributed_dispatcher import (
    CONTRACT_SCHEMA, VERSION, DispatcherError, DistributedDispatcher,
    _hash, _now, _now_dt, _stable, _text, normalize_worker, normalize_workload,
)

QUEUE_SCHEMA = "sc-lab-dispatch-queue-item/0.31.1"
LEASE_SCHEMA = "sc-lab-dispatch-lease/0.31.1"
EVENT_SCHEMA = "sc-lab-dispatch-event/0.31.1"
DB_SCHEMA_VERSION = 2
ACTIVE_QUEUE_STATES = {"queued", "leased", "running", "retrying"}
FINAL_QUEUE_STATES = {"completed", "failed", "cancelled"}

class PersistentDistributedDispatcher(DistributedDispatcher):
    def __init__(self, db_path: str, stale_seconds: int = 120, default_lease_seconds: int = 300,
                 max_workers: int = 500, max_queue_records: int = 5000,
                 max_attempts: int = 5, history_limit: int = 10000):
        super().__init__()
        self.db_path = str(db_path)
        self.stale_seconds = max(30, int(stale_seconds))
        self.default_lease_seconds = max(30, min(3600, int(default_lease_seconds)))
        self.max_workers = max(1, int(max_workers))
        self.max_queue_records = max(100, int(max_queue_records))
        self.max_attempts = max(1, int(max_attempts))
        self.history_limit = max(100, int(history_limit))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        return con

    def _migrate(self) -> None:
        with self._connect() as con:
            con.executescript('''
            CREATE TABLE IF NOT EXISTS dispatcher_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS dispatcher_workers(
              id TEXT PRIMARY KEY, state TEXT NOT NULL, worker_type TEXT NOT NULL,
              capability_fingerprint TEXT NOT NULL, payload_json TEXT NOT NULL,
              registered_at TEXT NOT NULL, last_heartbeat_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dispatcher_queue(
              id TEXT PRIMARY KEY, workload_hash TEXT NOT NULL, project_id TEXT NOT NULL,
              method TEXT NOT NULL, priority INTEGER NOT NULL, status TEXT NOT NULL,
              payload_json TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
              max_attempts INTEGER NOT NULL, available_at TEXT NOT NULL,
              lease_id TEXT, worker_id TEXT, lease_expires_at TEXT,
              result_json TEXT, error_text TEXT,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_dispatcher_queue_ready
              ON dispatcher_queue(status, priority DESC, available_at, created_at);
            CREATE INDEX IF NOT EXISTS idx_dispatcher_queue_hash
              ON dispatcher_queue(workload_hash, project_id, status);
            CREATE TABLE IF NOT EXISTS dispatcher_contracts(
              id TEXT PRIMARY KEY, lease_id TEXT UNIQUE NOT NULL, queue_id TEXT,
              worker_id TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL,
              expires_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dispatcher_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT, schema_name TEXT NOT NULL,
              entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, event_type TEXT NOT NULL,
              payload_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dispatcher_worker_credentials(
              worker_id TEXT PRIMARY KEY REFERENCES dispatcher_workers(id) ON DELETE CASCADE,
              credential_hash TEXT NOT NULL,
              issued_at TEXT NOT NULL,
              rotated_at TEXT,
              revoked_at TEXT,
              last_used_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_dispatcher_events_entity
              ON dispatcher_events(entity_type, entity_id, id DESC);
            ''')
            con.execute("INSERT INTO dispatcher_meta(key,value) VALUES('schema_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(DB_SCHEMA_VERSION),))

    @staticmethod
    def _loads(value: str | None) -> Any:
        return json.loads(value) if value else None

    def _event(self, con: sqlite3.Connection, entity_type: str, entity_id: str, event_type: str, payload: Any) -> None:
        con.execute("INSERT INTO dispatcher_events(schema_name,entity_type,entity_id,event_type,payload_json,created_at) VALUES(?,?,?,?,?,?)",
                    (EVENT_SCHEMA, entity_type, entity_id, event_type, _stable(payload if payload is not None else {}), _now()))
        con.execute("DELETE FROM dispatcher_events WHERE id NOT IN (SELECT id FROM dispatcher_events ORDER BY id DESC LIMIT ?)", (self.history_limit,))

    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        worker = normalize_worker(payload)
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute("SELECT payload_json,registered_at FROM dispatcher_workers WHERE id=?", (worker['id'],)).fetchone()
            count = con.execute("SELECT COUNT(*) FROM dispatcher_workers").fetchone()[0]
            if not existing and count >= self.max_workers:
                con.execute("ROLLBACK"); raise DispatcherError("Worker registry capacity reached.")
            if existing: worker['registeredAt'] = existing['registered_at']
            con.execute('''INSERT INTO dispatcher_workers(id,state,worker_type,capability_fingerprint,payload_json,registered_at,last_heartbeat_at,updated_at)
                           VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET state=excluded.state,worker_type=excluded.worker_type,
                           capability_fingerprint=excluded.capability_fingerprint,payload_json=excluded.payload_json,last_heartbeat_at=excluded.last_heartbeat_at,updated_at=excluded.updated_at''',
                        (worker['id'],worker['state'],worker['workerType'],worker['capabilityFingerprint'],_stable(worker),worker['registeredAt'],worker['lastHeartbeatAt'],now))
            self._event(con,'worker',worker['id'],'registered' if not existing else 'updated',worker)
            con.execute("COMMIT")
        return {'ok':True,'worker':worker,'persistent':True}

    @staticmethod
    def _credential_hash(value: str) -> str:
        return __import__("hashlib").sha256(value.encode("utf-8")).hexdigest()

    def enroll(self, payload: dict[str, Any]) -> dict[str, Any]:
        registered = self.register(payload)
        worker = registered["worker"]
        credential = secrets.token_urlsafe(36)
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute("SELECT worker_id FROM dispatcher_worker_credentials WHERE worker_id=?", (worker["id"],)).fetchone()
            con.execute(
                """INSERT INTO dispatcher_worker_credentials(worker_id,credential_hash,issued_at,rotated_at,revoked_at,last_used_at)
                   VALUES(?,?,?,?,NULL,NULL)
                   ON CONFLICT(worker_id) DO UPDATE SET credential_hash=excluded.credential_hash,
                   rotated_at=excluded.rotated_at,revoked_at=NULL,last_used_at=NULL""",
                (worker["id"], self._credential_hash(credential), now, now if existing else None),
            )
            self._event(con, "worker", worker["id"], "credential-enrolled" if not existing else "credential-rotated", {"credentialReturnedOnce": True})
            con.execute("COMMIT")
        return {
            "ok": True,
            "schema": "sc-lab-worker-enrollment/0.31.2",
            "version": VERSION,
            "worker": worker,
            "credential": credential,
            "credentialReturnedOnce": True,
        }

    def authenticate_worker(self, worker_id: str, credential: str) -> dict[str, Any]:
        worker_id = _text(worker_id, 180)
        credential = _text(credential, 512)
        if not worker_id or not credential:
            raise DispatcherError("Worker credential is required.")
        with self._connect() as con:
            row = con.execute(
                """SELECT c.credential_hash,c.revoked_at,w.state,w.payload_json
                   FROM dispatcher_worker_credentials c JOIN dispatcher_workers w ON w.id=c.worker_id
                   WHERE c.worker_id=?""",
                (worker_id,),
            ).fetchone()
            if not row or row["revoked_at"] or not hmac.compare_digest(row["credential_hash"], self._credential_hash(credential)):
                raise DispatcherError("Worker credential is invalid or revoked.")
            if row["state"] == "quarantined":
                raise DispatcherError("Worker is quarantined.")
            now = _now()
            con.execute("UPDATE dispatcher_worker_credentials SET last_used_at=? WHERE worker_id=?", (now, worker_id))
            worker = self._loads(row["payload_json"])
        return {"ok": True, "worker": worker, "authenticatedAt": now}

    def rotate_worker_credential(self, worker_id: str) -> dict[str, Any]:
        credential = secrets.token_urlsafe(36)
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT worker_id FROM dispatcher_worker_credentials WHERE worker_id=? AND revoked_at IS NULL", (worker_id,)).fetchone()
            if not row:
                con.execute("ROLLBACK")
                raise DispatcherError("Active worker credential was not found.")
            con.execute("UPDATE dispatcher_worker_credentials SET credential_hash=?,rotated_at=?,last_used_at=NULL WHERE worker_id=?", (self._credential_hash(credential), now, worker_id))
            self._event(con, "worker", worker_id, "credential-rotated", {"credentialReturnedOnce": True})
            con.execute("COMMIT")
        return {"ok": True, "workerId": worker_id, "credential": credential, "credentialReturnedOnce": True, "rotatedAt": now}

    def revoke_worker(self, worker_id: str, reason: str = "revoked by coordinator") -> dict[str, Any]:
        now = _now()
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT payload_json FROM dispatcher_workers WHERE id=?", (worker_id,)).fetchone()
            if not row:
                con.execute("ROLLBACK")
                raise DispatcherError("Worker was not found.")
            worker = self._loads(row["payload_json"])
            worker["state"] = "quarantined"
            worker["metadata"] = dict(worker.get("metadata") or {})
            worker["metadata"]["quarantineReason"] = _text(reason, 1000)
            worker["metadata"]["quarantinedAt"] = now
            con.execute("UPDATE dispatcher_workers SET state='quarantined',payload_json=?,updated_at=? WHERE id=?", (_stable(worker), now, worker_id))
            con.execute("UPDATE dispatcher_worker_credentials SET revoked_at=? WHERE worker_id=?", (now, worker_id))
            self._event(con, "worker", worker_id, "credential-revoked", {"reason": worker["metadata"]["quarantineReason"]})
            con.execute("COMMIT")
        return {"ok": True, "workerId": worker_id, "state": "quarantined", "revokedAt": now}

    def credential_status(self) -> dict[str, Any]:
        with self._connect() as con:
            total = con.execute("SELECT COUNT(*) FROM dispatcher_worker_credentials").fetchone()[0]
            active = con.execute("SELECT COUNT(*) FROM dispatcher_worker_credentials WHERE revoked_at IS NULL").fetchone()[0]
            revoked = total - active
            recently_used = con.execute("SELECT COUNT(*) FROM dispatcher_worker_credentials WHERE last_used_at IS NOT NULL").fetchone()[0]
        return {"ok": True, "version": VERSION, "total": total, "active": active, "revoked": revoked, "used": recently_used, "storedAsDigests": True}

    def heartbeat(self, worker_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row=con.execute("SELECT payload_json FROM dispatcher_workers WHERE id=?",(worker_id,)).fetchone()
            if not row: con.execute("ROLLBACK"); raise DispatcherError("Worker was not found.")
            worker=self._loads(row['payload_json'])
            state=_text(payload.get('state'),40).lower()
            if state:
                if state not in {'online','draining','offline','quarantined'}: con.execute("ROLLBACK"); raise DispatcherError("Unsupported worker state.")
                worker['state']=state
            load=payload.get('load') if isinstance(payload.get('load'),dict) else {}
            worker['load']={'activeJobs':max(0,min(128,int(load.get('activeJobs',worker['load']['activeJobs'])))), 'queuedJobs':max(0,min(10000,int(load.get('queuedJobs',worker['load']['queuedJobs']))))}
            worker['lastHeartbeatAt']=_now()
            con.execute("UPDATE dispatcher_workers SET state=?,payload_json=?,last_heartbeat_at=?,updated_at=? WHERE id=?",(worker['state'],_stable(worker),worker['lastHeartbeatAt'],worker['lastHeartbeatAt'],worker_id))
            self._event(con,'worker',worker_id,'heartbeat',{'state':worker['state'],'load':worker['load']})
            con.execute("COMMIT")
        return {'ok':True,'worker':worker,'persistent':True}

    def _worker_rows(self) -> list[dict[str,Any]]:
        cutoff=(_now_dt()-timedelta(seconds=self.stale_seconds)).isoformat()
        with self._connect() as con:
            rows=con.execute("SELECT payload_json,last_heartbeat_at FROM dispatcher_workers ORDER BY updated_at DESC").fetchall()
        out=[]
        for row in rows:
            w=self._loads(row['payload_json'])
            if w['state']=='online' and row['last_heartbeat_at'] < cutoff:
                w['state']='offline'; w['stale']=True
            out.append(w)
        return out

    def list(self, active_only: bool=False) -> dict[str,Any]:
        rows=self._worker_rows()
        if active_only: rows=[w for w in rows if w['state']=='online']
        rows.sort(key=lambda w:(w['state']!='online',w['load']['activeJobs'],w['name'].lower()))
        return {'ok':True,'version':VERSION,'count':len(rows),'workers':rows,'persistent':True}

    def route(self,payload:dict[str,Any])->dict[str,Any]:
        workload=normalize_workload(payload); candidates=[]
        for worker in self._worker_rows():
            scored=self._score(worker,workload)
            if scored: candidates.append({'worker':worker,'score':round(scored[0],4),'reasons':scored[1]})
        candidates.sort(key=lambda x:(-x['score'],x['worker']['id']))
        selected=candidates[0] if candidates else None
        return {'ok':selected is not None,'version':VERSION,'workload':workload,'selectedWorker':selected['worker'] if selected else None,'score':selected['score'] if selected else None,'reasons':selected['reasons'] if selected else [],'candidateCount':len(candidates),'rejectionReason':None if selected else 'No online worker satisfies the governed workload requirements.','persistent':True}

    def enqueue(self,payload:dict[str,Any])->dict[str,Any]:
        workload=normalize_workload(payload); workload['workloadHash']=_hash({k:v for k,v in workload.items() if k not in {'id','createdAt','workloadHash'}}); now=_now(); max_attempts=max(1,min(20,int(payload.get('maxAttempts',self.max_attempts))))
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing=con.execute("SELECT * FROM dispatcher_queue WHERE workload_hash=? AND project_id=? AND status IN ('queued','leased','running','retrying') ORDER BY created_at DESC LIMIT 1",(workload['workloadHash'],workload['projectId'])).fetchone()
            if existing:
                con.execute("COMMIT"); return {'ok':True,'deduplicated':True,'queueItem':self._queue_dict(existing)}
            total=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status NOT IN ('completed','failed','cancelled')").fetchone()[0]
            if total>=self.max_queue_records: con.execute("ROLLBACK"); raise DispatcherError("Persistent dispatch queue capacity reached.")
            qid=f"dispatch-job-{secrets.token_hex(10)}"
            con.execute('''INSERT INTO dispatcher_queue(id,workload_hash,project_id,method,priority,status,payload_json,attempts,max_attempts,available_at,created_at,updated_at)
                           VALUES(?,?,?,?,?,'queued',?,0,?,?,?,?)''',(qid,workload['workloadHash'],workload['projectId'],workload['method'],workload['priority'],_stable(workload),max_attempts,now,now,now))
            self._event(con,'queue-item',qid,'enqueued',{'workloadHash':workload['workloadHash'],'priority':workload['priority']})
            row=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(qid,)).fetchone(); con.execute("COMMIT")
        return {'ok':True,'deduplicated':False,'queueItem':self._queue_dict(row)}

    def _queue_dict(self,row:sqlite3.Row)->dict[str,Any]:
        return {'schema':QUEUE_SCHEMA,'version':VERSION,'id':row['id'],'recordType':'dispatch-queue-item','status':row['status'],'priority':row['priority'],'attempts':row['attempts'],'maxAttempts':row['max_attempts'],'availableAt':row['available_at'],'leaseId':row['lease_id'],'workerId':row['worker_id'],'leaseExpiresAt':row['lease_expires_at'],'createdAt':row['created_at'],'updatedAt':row['updated_at'],'completedAt':row['completed_at'],'workload':self._loads(row['payload_json']),'result':self._loads(row['result_json']),'error':row['error_text']}

    def _contract(self, queue_item:dict[str,Any], worker:dict[str,Any], lease_id:str, expires:str, secret:str)->dict[str,Any]:
        body={'schema':CONTRACT_SCHEMA,'version':VERSION,'recordType':'dispatch-contract','id':f"dispatch-{secrets.token_hex(10)}",'leaseId':lease_id,'queueId':queue_item['id'],'workerId':worker['id'],'workerFingerprint':worker['capabilityFingerprint'],'workload':queue_item['workload'],'issuedAt':_now(),'expiresAt':expires,'status':'offered','acknowledgementRequired':True,'completionReceiptRequired':True,'coordinator':'sustainable-catalyst-lab-python-compute-core'}
        import hmac
        from hashlib import sha256
        key=(secret or 'open-development-dispatch-key').encode(); body['signatureMode']='hmac-sha256' if secret else 'development-hmac-sha256'; body['signature']=hmac.new(key,_stable(body).encode(),sha256).hexdigest(); return body

    def claim(self,payload:dict[str,Any],secret:str='')->dict[str,Any]:
        worker_id=_text(payload.get('workerId'),180)
        if not worker_id: raise DispatcherError('Worker ID is required.')
        lease_seconds=max(30,min(3600,int(payload.get('leaseSeconds',self.default_lease_seconds))))
        self.recover()
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            wrow=con.execute("SELECT payload_json FROM dispatcher_workers WHERE id=?",(worker_id,)).fetchone()
            if not wrow: con.execute('ROLLBACK'); raise DispatcherError('Worker was not found.')
            worker=self._loads(wrow['payload_json'])
            if worker.get('state')!='online': con.execute('ROLLBACK'); raise DispatcherError('Worker is not online.')
            rows=con.execute("SELECT * FROM dispatcher_queue WHERE status IN ('queued','retrying') AND available_at<=? ORDER BY priority DESC,created_at ASC LIMIT 250",(_now(),)).fetchall()
            chosen=None
            for row in rows:
                if self._score(worker,self._loads(row['payload_json'])): chosen=row; break
            if not chosen: con.execute('COMMIT'); return {'ok':True,'claimed':False,'queueItem':None,'contract':None}
            lease_id=f"lease-{secrets.token_hex(12)}"; expires=(_now_dt()+timedelta(seconds=lease_seconds)).isoformat(); now=_now()
            updated=con.execute("UPDATE dispatcher_queue SET status='leased',attempts=attempts+1,lease_id=?,worker_id=?,lease_expires_at=?,updated_at=? WHERE id=? AND status IN ('queued','retrying')",(lease_id,worker_id,expires,now,chosen['id']))
            if updated.rowcount!=1: con.execute('ROLLBACK'); raise DispatcherError('Queue item was claimed by another coordinator.')
            qrow=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(chosen['id'],)).fetchone(); qitem=self._queue_dict(qrow)
            contract=self._contract(qitem,worker,lease_id,expires,secret)
            con.execute("INSERT INTO dispatcher_contracts(id,lease_id,queue_id,worker_id,status,payload_json,expires_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",(contract['id'],lease_id,qitem['id'],worker_id,'offered',_stable(contract),expires,now))
            self._event(con,'queue-item',qitem['id'],'leased',{'leaseId':lease_id,'workerId':worker_id,'expiresAt':expires})
            con.execute('COMMIT')
        return {'ok':True,'claimed':True,'queueItem':qitem,'contract':contract}

    def build_contract(self,payload:dict[str,Any],secret:str='')->dict[str,Any]:
        routed=self.route(payload)
        if not routed['ok']: raise DispatcherError(routed['rejectionReason'])
        queued=self.enqueue({'workload':routed['workload']})
        claimed=self.claim({'workerId':routed['selectedWorker']['id'],'leaseSeconds':routed['workload'].get('leaseSeconds',self.default_lease_seconds)},secret)
        if not claimed.get('claimed'): raise DispatcherError('The routed workload could not be leased.')
        return {'ok':True,'contract':claimed['contract'],'queueItem':claimed['queueItem'],'routing':{'score':routed['score'],'reasons':routed['reasons'],'candidateCount':routed['candidateCount']}}

    def acknowledge(self,contract_id:str,worker_id:str)->dict[str,Any]:
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_contracts WHERE id=?",(contract_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Dispatch contract was not found.')
            if row['worker_id']!=worker_id: con.execute('ROLLBACK'); raise DispatcherError('Worker does not match the dispatch contract.')
            contract=self._loads(row['payload_json']); contract['status']='acknowledged'; contract['acknowledgedAt']=_now()
            con.execute("UPDATE dispatcher_contracts SET status='acknowledged',payload_json=?,updated_at=? WHERE id=?",(_stable(contract),contract['acknowledgedAt'],contract_id))
            con.execute("UPDATE dispatcher_queue SET status='running',updated_at=? WHERE id=? AND lease_id=?",(contract['acknowledgedAt'],row['queue_id'],row['lease_id']))
            self._event(con,'contract',contract_id,'acknowledged',{'workerId':worker_id}); con.execute('COMMIT')
        return {'ok':True,'contract':contract}

    def renew(self,lease_id:str,payload:dict[str,Any])->dict[str,Any]:
        worker_id=_text(payload.get('workerId'),180); seconds=max(30,min(3600,int(payload.get('leaseSeconds',self.default_lease_seconds))))
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_queue WHERE lease_id=? AND status IN ('leased','running')",(lease_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Active lease was not found.')
            if row['worker_id']!=worker_id: con.execute('ROLLBACK'); raise DispatcherError('Worker does not own this lease.')
            expires=(_now_dt()+timedelta(seconds=seconds)).isoformat(); now=_now()
            con.execute("UPDATE dispatcher_queue SET lease_expires_at=?,updated_at=? WHERE id=?",(expires,now,row['id']))
            crow=con.execute("SELECT * FROM dispatcher_contracts WHERE lease_id=?",(lease_id,)).fetchone()
            if crow:
                c=self._loads(crow['payload_json']); c['expiresAt']=expires; c['renewedAt']=now
                con.execute("UPDATE dispatcher_contracts SET expires_at=?,payload_json=?,updated_at=? WHERE lease_id=?",(expires,_stable(c),now,lease_id))
            self._event(con,'lease',lease_id,'renewed',{'workerId':worker_id,'expiresAt':expires}); con.execute('COMMIT')
        return {'ok':True,'lease':{'schema':LEASE_SCHEMA,'leaseId':lease_id,'queueId':row['id'],'workerId':worker_id,'expiresAt':expires,'status':row['status']}}

    def release(self,lease_id:str,payload:dict[str,Any])->dict[str,Any]:
        worker_id=_text(payload.get('workerId'),180); reason=_text(payload.get('reason'),1000) or 'released'; requeue=bool(payload.get('requeue',True)); now=_now()
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_queue WHERE lease_id=? AND status IN ('leased','running')",(lease_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Active lease was not found.')
            if worker_id and row['worker_id']!=worker_id: con.execute('ROLLBACK'); raise DispatcherError('Worker does not own this lease.')
            status='queued' if requeue and row['attempts']<row['max_attempts'] else 'failed'
            con.execute("UPDATE dispatcher_queue SET status=?,lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,error_text=?,available_at=?,updated_at=?,completed_at=? WHERE id=?",(status,reason,now,now,now if status=='failed' else None,row['id']))
            con.execute("UPDATE dispatcher_contracts SET status='released',updated_at=? WHERE lease_id=?",(now,lease_id))
            self._event(con,'lease',lease_id,'released',{'reason':reason,'status':status}); q=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(row['id'],)).fetchone(); con.execute('COMMIT')
        return {'ok':True,'queueItem':self._queue_dict(q)}

    def complete(self,contract_id:str,payload:dict[str,Any],worker_id:str='')->dict[str,Any]:
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_contracts WHERE id=?",(contract_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Dispatch contract was not found.')
            if worker_id and row['worker_id'] != worker_id:
                con.execute('ROLLBACK'); raise DispatcherError('Worker does not own this dispatch contract.')
            contract=self._loads(row['payload_json']); ok=bool(payload.get('ok',True)); now=_now(); status='completed' if ok else 'failed'; result_hash=_hash(payload.get('result'))
            if row['status'] in ('completed','failed'):
                existing_hash=contract.get('resultHash')
                if existing_hash and existing_hash != result_hash:
                    con.execute('ROLLBACK'); raise DispatcherError('Completion receipt conflicts with the recorded terminal result.')
                con.execute('COMMIT'); return {'ok':True,'contract':contract,'idempotent':True}
            contract['status']=status; contract['completedAt']=now; contract['resultHash']=result_hash; contract['receipt']={'ok':ok,'warnings':payload.get('warnings') if isinstance(payload.get('warnings'),list) else [],'error':_text(payload.get('error'),2000),'workerId':worker_id or row['worker_id'],'receiptHash':_text(payload.get('receiptHash'),128)}
            con.execute("UPDATE dispatcher_contracts SET status=?,payload_json=?,updated_at=? WHERE id=?",(status,_stable(contract),now,contract_id))
            con.execute("UPDATE dispatcher_queue SET status=?,result_json=?,error_text=?,completed_at=?,updated_at=? WHERE id=?",(status,_stable(payload.get('result')) if payload.get('result') is not None else None,_text(payload.get('error'),2000) or None,now,now,row['queue_id']))
            self._event(con,'contract',contract_id,status,contract['receipt']); con.execute('COMMIT')
        return {'ok':True,'contract':contract,'idempotent':False}

    def recover(self)->dict[str,Any]:
        now=_now(); cutoff=(_now_dt()-timedelta(seconds=self.stale_seconds)).isoformat(); requeued=failed=stale=0
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            for row in con.execute("SELECT * FROM dispatcher_queue WHERE status IN ('leased','running') AND lease_expires_at IS NOT NULL AND lease_expires_at<?",(now,)).fetchall():
                status='queued' if row['attempts']<row['max_attempts'] else 'failed'
                con.execute("UPDATE dispatcher_queue SET status=?,lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,error_text='lease expired',available_at=?,updated_at=?,completed_at=? WHERE id=?",(status,now,now,now if status=='failed' else None,row['id']))
                con.execute("UPDATE dispatcher_contracts SET status='expired',updated_at=? WHERE lease_id=?",(now,row['lease_id']))
                self._event(con,'queue-item',row['id'],'lease-expired',{'nextStatus':status}); requeued += status=='queued'; failed += status=='failed'
            for row in con.execute("SELECT id,payload_json FROM dispatcher_workers WHERE state='online' AND last_heartbeat_at<?",(cutoff,)).fetchall():
                w=self._loads(row['payload_json']); w['state']='offline'; w['stale']=True
                con.execute("UPDATE dispatcher_workers SET state='offline',payload_json=?,updated_at=? WHERE id=?",(_stable(w),now,row['id'])); self._event(con,'worker',row['id'],'marked-stale',{}); stale+=1
            con.execute('COMMIT')
        return {'ok':True,'requeued':requeued,'failed':failed,'staleWorkers':stale,'recoveredAt':now}

    def status(self)->dict[str,Any]:
        with self._connect() as con:
            counts={r['status']:r['n'] for r in con.execute("SELECT status,COUNT(*) n FROM dispatcher_queue GROUP BY status")}
            active=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status IN ('leased','running')").fetchone()[0]
            workers=con.execute("SELECT COUNT(*) FROM dispatcher_workers").fetchone()[0]
            events=con.execute("SELECT COUNT(*) FROM dispatcher_events").fetchone()[0]
            page_count=con.execute("PRAGMA page_count").fetchone()[0]; page_size=con.execute("PRAGMA page_size").fetchone()[0]
        return {'ok':True,'version':VERSION,'storage':'sqlite-wal','persistent':True,'schemaVersion':DB_SCHEMA_VERSION,'credentials':self.credential_status(),'counts':counts,'activeLeases':active,'workerCount':workers,'eventCount':events,'databaseBytes':page_count*page_size,'restartRecovery':True,'horizontalCoordinatorSafeClaims':True}

    def leases(self,limit:int=100)->dict[str,Any]:
        with self._connect() as con: rows=con.execute("SELECT * FROM dispatcher_queue WHERE status IN ('leased','running') ORDER BY lease_expires_at ASC LIMIT ?",(max(1,min(500,limit)),)).fetchall()
        leases=[{'schema':LEASE_SCHEMA,'leaseId':r['lease_id'],'queueId':r['id'],'workerId':r['worker_id'],'status':r['status'],'expiresAt':r['lease_expires_at'],'attempts':r['attempts']} for r in rows]
        return {'ok':True,'count':len(leases),'leases':leases}

    def history(self,limit:int=100)->dict[str,Any]:
        with self._connect() as con: rows=con.execute("SELECT * FROM dispatcher_events ORDER BY id DESC LIMIT ?",(max(1,min(1000,limit)),)).fetchall()
        events=[{'schema':r['schema_name'],'id':r['id'],'entityType':r['entity_type'],'entityId':r['entity_id'],'eventType':r['event_type'],'payload':self._loads(r['payload_json']),'createdAt':r['created_at']} for r in rows]
        return {'ok':True,'count':len(events),'events':events}

    def health(self)->dict[str,Any]:
        st=self.status(); workers=self.list(False)['workers']
        return {'ok':True,'status':'ready','version':VERSION,'architecture':'persistent-distributed-compute-dispatcher','workerCount':len(workers),'onlineWorkers':sum(1 for w in workers if w['state']=='online'),'capabilityDiscovery':True,'workloadRouting':True,'signedDispatchContracts':True,'leases':True,'persistentWorkerRegistry':True,'persistentQueue':True,'restartRecovery':True,'horizontalCoordinatorSafeClaims':True,'storage':'sqlite-wal','schemaVersion':DB_SCHEMA_VERSION,'workerCredentials':st['credentials'],'queueCounts':st['counts'],'arbitraryCallbackUrls':False,'arbitraryCode':False}
