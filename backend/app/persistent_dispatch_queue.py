from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import hmac
import secrets
import sqlite3
from typing import Any

from .dispatcher_operations import DEAD_LETTER_SCHEMA, FAILURE_SCHEMA, classify_failure, policies as operations_policies, retry_delay_seconds
from .distributed_dispatcher import (
    CONTRACT_SCHEMA, VERSION, DispatcherError, DistributedDispatcher,
    _hash, _now, _now_dt, _stable, _text, normalize_worker, normalize_workload,
)

QUEUE_SCHEMA = "sc-lab-dispatch-queue-item/0.31.1"
LEASE_SCHEMA = "sc-lab-dispatch-lease/0.31.1"
EVENT_SCHEMA = "sc-lab-dispatch-event/0.31.1"
DB_SCHEMA_VERSION = 3
ACTIVE_QUEUE_STATES = {"queued", "leased", "running", "retrying"}
FINAL_QUEUE_STATES = {"completed", "failed", "cancelled", "dead-lettered"}

class PersistentDistributedDispatcher(DistributedDispatcher):
    def __init__(self, db_path: str, stale_seconds: int = 120, default_lease_seconds: int = 300,
                 max_workers: int = 500, max_queue_records: int = 5000,
                 max_attempts: int = 5, history_limit: int = 10000,
                 retry_base_delay_seconds: int = 15, retry_max_delay_seconds: int = 900):
        super().__init__()
        self.db_path = str(db_path)
        self.stale_seconds = max(30, int(stale_seconds))
        self.default_lease_seconds = max(30, min(3600, int(default_lease_seconds)))
        self.max_workers = max(1, int(max_workers))
        self.max_queue_records = max(100, int(max_queue_records))
        self.max_attempts = max(1, int(max_attempts))
        self.history_limit = max(100, int(history_limit))
        self.retry_base_delay_seconds = max(1, int(retry_base_delay_seconds))
        self.retry_max_delay_seconds = max(self.retry_base_delay_seconds, int(retry_max_delay_seconds))
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
            columns = {row["name"] for row in con.execute("PRAGMA table_info(dispatcher_queue)").fetchall()}
            for name, declaration in (
                ("failure_class", "TEXT"),
                ("failure_code", "TEXT"),
                ("retryable", "INTEGER"),
                ("dead_lettered_at", "TEXT"),
                ("operator_note", "TEXT"),
            ):
                if name not in columns:
                    con.execute(f"ALTER TABLE dispatcher_queue ADD COLUMN {name} {declaration}")
            con.executescript("""
            CREATE INDEX IF NOT EXISTS idx_dispatcher_queue_failure
              ON dispatcher_queue(status, failure_class, updated_at DESC);
            CREATE TABLE IF NOT EXISTS dispatcher_operator_actions(
              id INTEGER PRIMARY KEY AUTOINCREMENT, queue_id TEXT NOT NULL,
              action TEXT NOT NULL, operator_id TEXT NOT NULL, reason TEXT,
              payload_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_dispatcher_operator_queue
              ON dispatcher_operator_actions(queue_id, id DESC);
            """)
            con.execute("INSERT INTO dispatcher_meta(key,value) VALUES('schema_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(DB_SCHEMA_VERSION),))

    @staticmethod
    def _loads(value: str | None) -> Any:
        return json.loads(value) if value else None

    def _event(self, con: sqlite3.Connection, entity_type: str, entity_id: str, event_type: str, payload: Any) -> None:
        con.execute("INSERT INTO dispatcher_events(schema_name,entity_type,entity_id,event_type,payload_json,created_at) VALUES(?,?,?,?,?,?)",
                    (EVENT_SCHEMA, entity_type, entity_id, event_type, _stable(payload if payload is not None else {}), _now()))
        con.execute("DELETE FROM dispatcher_events WHERE id NOT IN (SELECT id FROM dispatcher_events ORDER BY id DESC LIMIT ?)", (self.history_limit,))

    def _operator_action(self, con: sqlite3.Connection, queue_id: str, action: str, operator_id: str, reason: str, payload: Any | None = None) -> None:
        con.execute(
            "INSERT INTO dispatcher_operator_actions(queue_id,action,operator_id,reason,payload_json,created_at) VALUES(?,?,?,?,?,?)",
            (_text(queue_id, 220), _text(action, 80), _text(operator_id, 180) or "operator", _text(reason, 1000), _stable(payload if payload is not None else {}), _now()),
        )

    def failure_policies(self) -> dict[str, Any]:
        return operations_policies(self.retry_base_delay_seconds, self.retry_max_delay_seconds)

    def _failure_transition(self, row: sqlite3.Row, payload: dict[str, Any] | None = None, fallback: str = "") -> tuple[str, dict[str, Any], str]:
        failure = classify_failure(payload, fallback)
        can_retry = bool(failure["retryable"]) and int(row["attempts"]) < int(row["max_attempts"])
        if can_retry:
            delay = retry_delay_seconds(int(row["attempts"]), self.retry_base_delay_seconds, self.retry_max_delay_seconds)
            available_at = (_now_dt() + timedelta(seconds=delay)).isoformat()
            failure["retryDelaySeconds"] = delay
            failure["nextAvailableAt"] = available_at
            return "retrying", failure, available_at
        failure["deadLetterReason"] = "non-retryable" if not failure["retryable"] else "attempt-limit-exhausted"
        return "dead-lettered", failure, _now()

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
            "schema": "sc-lab-worker-enrollment/0.31.3",
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
        keys=set(row.keys())
        created=row['created_at']; age=max(0,int((_now_dt()-datetime.fromisoformat(created)).total_seconds())) if created else 0
        failure_class=row['failure_class'] if 'failure_class' in keys else None
        failure={
            'schema':FAILURE_SCHEMA,'failureClass':failure_class,'failureCode':row['failure_code'] if 'failure_code' in keys else None,
            'retryable':bool(row['retryable']) if 'retryable' in keys and row['retryable'] is not None else None,
            'error':row['error_text'],
        } if failure_class else None
        return {'schema':QUEUE_SCHEMA,'version':VERSION,'id':row['id'],'recordType':'dispatch-queue-item','status':row['status'],'priority':row['priority'],'attempts':row['attempts'],'maxAttempts':row['max_attempts'],'availableAt':row['available_at'],'leaseId':row['lease_id'],'workerId':row['worker_id'],'leaseExpiresAt':row['lease_expires_at'],'createdAt':created,'updatedAt':row['updated_at'],'completedAt':row['completed_at'],'deadLetteredAt':row['dead_lettered_at'] if 'dead_lettered_at' in keys else None,'operatorNote':row['operator_note'] if 'operator_note' in keys else None,'ageSeconds':age,'workload':self._loads(row['payload_json']),'result':self._loads(row['result_json']),'error':row['error_text'],'failure':failure}

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
            if requeue:
                status,failure,available_at=self._failure_transition(row,payload,reason)
            else:
                status='cancelled'; failure=classify_failure({'failureClass':'operator-cancelled','retryable':False,'error':reason}); available_at=now
            completed_at=now if status in FINAL_QUEUE_STATES else None
            dead_lettered_at=now if status=='dead-lettered' else None
            con.execute("UPDATE dispatcher_queue SET status=?,lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,error_text=?,failure_class=?,failure_code=?,retryable=?,dead_lettered_at=?,available_at=?,updated_at=?,completed_at=? WHERE id=?",(status,failure['error'],failure['failureClass'],failure['failureCode'],1 if failure['retryable'] else 0,dead_lettered_at,available_at,now,completed_at,row['id']))
            con.execute("UPDATE dispatcher_contracts SET status='released',updated_at=? WHERE lease_id=?",(now,lease_id))
            self._event(con,'lease',lease_id,'released',{'reason':reason,'status':status,'failure':failure}); q=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(row['id'],)).fetchone(); con.execute('COMMIT')
        return {'ok':True,'queueItem':self._queue_dict(q),'failure':failure}

    def complete(self,contract_id:str,payload:dict[str,Any],worker_id:str='')->dict[str,Any]:
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_contracts WHERE id=?",(contract_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Dispatch contract was not found.')
            if worker_id and row['worker_id'] != worker_id:
                con.execute('ROLLBACK'); raise DispatcherError('Worker does not own this dispatch contract.')
            contract=self._loads(row['payload_json']); ok=bool(payload.get('ok',True)); now=_now(); result_hash=_hash(payload.get('result'))
            if row['status'] in ('completed','failed','dead-lettered'):
                existing_hash=contract.get('resultHash')
                if existing_hash and existing_hash != result_hash:
                    con.execute('ROLLBACK'); raise DispatcherError('Completion receipt conflicts with the recorded terminal result.')
                con.execute('COMMIT'); return {'ok':True,'contract':contract,'idempotent':True}
            qrow=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(row['queue_id'],)).fetchone()
            if not qrow: con.execute('ROLLBACK'); raise DispatcherError('Dispatch queue item was not found.')
            if ok:
                queue_status='completed'; contract_status='completed'; failure=None; available_at=qrow['available_at']; completed_at=now; dead_lettered_at=None
            else:
                queue_status,failure,available_at=self._failure_transition(qrow,payload,_text(payload.get('error'),2000))
                contract_status='failed'; completed_at=now if queue_status in FINAL_QUEUE_STATES else None; dead_lettered_at=now if queue_status=='dead-lettered' else None
            contract['status']=contract_status; contract['completedAt']=now; contract['resultHash']=result_hash; contract['receipt']={'ok':ok,'warnings':payload.get('warnings') if isinstance(payload.get('warnings'),list) else [],'error':_text(payload.get('error'),2000),'workerId':worker_id or row['worker_id'],'receiptHash':_text(payload.get('receiptHash'),128)}
            if failure: contract['failure']=failure
            con.execute("UPDATE dispatcher_contracts SET status=?,payload_json=?,updated_at=? WHERE id=?",(contract_status,_stable(contract),now,contract_id))
            con.execute("UPDATE dispatcher_queue SET status=?,result_json=?,error_text=?,failure_class=?,failure_code=?,retryable=?,dead_lettered_at=?,lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,available_at=?,completed_at=?,updated_at=? WHERE id=?",(queue_status,_stable(payload.get('result')) if payload.get('result') is not None else None,_text(payload.get('error'),2000) or None,failure['failureClass'] if failure else None,failure['failureCode'] if failure else None,(1 if failure['retryable'] else 0) if failure else None,dead_lettered_at,available_at,completed_at,now,row['queue_id']))
            event_payload=dict(contract['receipt'])
            if failure: event_payload['failure']=failure
            self._event(con,'contract',contract_id,queue_status,event_payload); con.execute('COMMIT')
        return {'ok':True,'contract':contract,'idempotent':False,'queueStatus':queue_status,'failure':failure}

    def recover(self)->dict[str,Any]:
        now=_now(); cutoff=(_now_dt()-timedelta(seconds=self.stale_seconds)).isoformat(); requeued=dead_lettered=stale=0
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            for row in con.execute("SELECT * FROM dispatcher_queue WHERE status IN ('leased','running') AND lease_expires_at IS NOT NULL AND lease_expires_at<?",(now,)).fetchall():
                status,failure,available_at=self._failure_transition(row,{'failureClass':'lease-timeout','failureCode':'lease_expired','error':'lease expired'})
                completed_at=now if status in FINAL_QUEUE_STATES else None; dl_at=now if status=='dead-lettered' else None
                con.execute("UPDATE dispatcher_queue SET status=?,lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,error_text=?,failure_class=?,failure_code=?,retryable=?,dead_lettered_at=?,available_at=?,updated_at=?,completed_at=? WHERE id=?",(status,failure['error'],failure['failureClass'],failure['failureCode'],1 if failure['retryable'] else 0,dl_at,available_at,now,completed_at,row['id']))
                con.execute("UPDATE dispatcher_contracts SET status='expired',updated_at=? WHERE lease_id=?",(now,row['lease_id']))
                self._event(con,'queue-item',row['id'],'lease-expired',{'nextStatus':status,'failure':failure}); requeued += status=='retrying'; dead_lettered += status=='dead-lettered'
            for row in con.execute("SELECT id,payload_json FROM dispatcher_workers WHERE state='online' AND last_heartbeat_at<?",(cutoff,)).fetchall():
                w=self._loads(row['payload_json']); w['state']='offline'; w['stale']=True
                con.execute("UPDATE dispatcher_workers SET state='offline',payload_json=?,updated_at=? WHERE id=?",(_stable(w),now,row['id'])); self._event(con,'worker',row['id'],'marked-stale',{}); stale+=1
            con.execute('COMMIT')
        return {'ok':True,'requeued':requeued,'failed':dead_lettered,'deadLettered':dead_lettered,'staleWorkers':stale,'recoveredAt':now}

    def status(self)->dict[str,Any]:
        with self._connect() as con:
            counts={r['status']:r['n'] for r in con.execute("SELECT status,COUNT(*) n FROM dispatcher_queue GROUP BY status")}
            for state in ('queued','retrying','leased','running','completed','failed','cancelled','dead-lettered'): counts.setdefault(state,0)
            active=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status IN ('leased','running')").fetchone()[0]
            workers=con.execute("SELECT COUNT(*) FROM dispatcher_workers").fetchone()[0]
            events=con.execute("SELECT COUNT(*) FROM dispatcher_events").fetchone()[0]
            page_count=con.execute("PRAGMA page_count").fetchone()[0]; page_size=con.execute("PRAGMA page_size").fetchone()[0]
        return {'ok':True,'version':VERSION,'storage':'sqlite-wal','persistent':True,'schemaVersion':DB_SCHEMA_VERSION,'credentials':self.credential_status(),'counts':counts,'activeLeases':active,'workerCount':workers,'eventCount':events,'databaseBytes':page_count*page_size,'restartRecovery':True,'horizontalCoordinatorSafeClaims':True,'deadLetterQueue':True,'failureClassification':True,'operatorReplay':True}

    def leases(self,limit:int=100)->dict[str,Any]:
        with self._connect() as con: rows=con.execute("SELECT * FROM dispatcher_queue WHERE status IN ('leased','running') ORDER BY lease_expires_at ASC LIMIT ?",(max(1,min(500,limit)),)).fetchall()
        leases=[{'schema':LEASE_SCHEMA,'leaseId':r['lease_id'],'queueId':r['id'],'workerId':r['worker_id'],'status':r['status'],'expiresAt':r['lease_expires_at'],'attempts':r['attempts']} for r in rows]
        return {'ok':True,'count':len(leases),'leases':leases}

    def history(self,limit:int=100)->dict[str,Any]:
        with self._connect() as con: rows=con.execute("SELECT * FROM dispatcher_events ORDER BY id DESC LIMIT ?",(max(1,min(1000,limit)),)).fetchall()
        events=[{'schema':r['schema_name'],'id':r['id'],'entityType':r['entity_type'],'entityId':r['entity_id'],'eventType':r['event_type'],'payload':self._loads(r['payload_json']),'createdAt':r['created_at']} for r in rows]
        return {'ok':True,'count':len(events),'events':events}

    def queue_item(self, queue_id: str) -> dict[str, Any]:
        with self._connect() as con:
            row=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(_text(queue_id,220),)).fetchone()
        if not row: raise DispatcherError('Dispatch queue item was not found.')
        return {'ok':True,'queueItem':self._queue_dict(row)}

    def timeline(self, queue_id: str, limit: int = 250) -> dict[str, Any]:
        queue_id=_text(queue_id,220); limit=max(1,min(1000,int(limit)))
        with self._connect() as con:
            q=con.execute("SELECT id FROM dispatcher_queue WHERE id=?",(queue_id,)).fetchone()
            if not q: raise DispatcherError('Dispatch queue item was not found.')
            events=con.execute("SELECT * FROM dispatcher_events WHERE (entity_type='queue-item' AND entity_id=?) OR (entity_type='contract' AND entity_id IN (SELECT id FROM dispatcher_contracts WHERE queue_id=?)) OR (entity_type='lease' AND entity_id IN (SELECT lease_id FROM dispatcher_contracts WHERE queue_id=?)) ORDER BY id DESC LIMIT ?",(queue_id,queue_id,queue_id,limit)).fetchall()
            actions=con.execute("SELECT * FROM dispatcher_operator_actions WHERE queue_id=? ORDER BY id DESC LIMIT ?",(queue_id,limit)).fetchall()
        records=[{'kind':'event','id':r['id'],'entityType':r['entity_type'],'entityId':r['entity_id'],'eventType':r['event_type'],'payload':self._loads(r['payload_json']),'createdAt':r['created_at']} for r in events]
        records += [{'kind':'operator-action','id':r['id'],'entityType':'queue-item','entityId':queue_id,'eventType':r['action'],'operatorId':r['operator_id'],'reason':r['reason'],'payload':self._loads(r['payload_json']),'createdAt':r['created_at']} for r in actions]
        records.sort(key=lambda item:item['createdAt'],reverse=True)
        return {'ok':True,'queueId':queue_id,'count':len(records[:limit]),'timeline':records[:limit]}

    def dead_letters(self, limit: int = 100, failure_class: str = '') -> dict[str, Any]:
        limit=max(1,min(1000,int(limit))); params=[]; where="status='dead-lettered'"
        if failure_class:
            where += " AND failure_class=?"; params.append(_text(failure_class,80))
        params.append(limit)
        with self._connect() as con:
            rows=con.execute(f"SELECT * FROM dispatcher_queue WHERE {where} ORDER BY dead_lettered_at DESC,updated_at DESC LIMIT ?",params).fetchall()
        return {'ok':True,'schema':DEAD_LETTER_SCHEMA,'count':len(rows),'deadLetters':[self._queue_dict(row) for row in rows]}

    def replay(self, queue_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload=payload if isinstance(payload,dict) else {}; queue_id=_text(queue_id,220); operator=_text(payload.get('operatorId'),180) or 'operator'; reason=_text(payload.get('reason'),1000) or 'operator replay'; reset_attempts=bool(payload.get('resetAttempts',True)); now=_now()
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(queue_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Dispatch queue item was not found.')
            if row['status'] not in ('dead-lettered','failed','cancelled'):
                con.execute('ROLLBACK'); raise DispatcherError('Only terminal queue items can be replayed.')
            attempts=0 if reset_attempts else min(int(row['attempts']),max(0,int(row['max_attempts'])-1))
            con.execute("UPDATE dispatcher_queue SET status='queued',attempts=?,available_at=?,lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,result_json=NULL,error_text=NULL,failure_class=NULL,failure_code=NULL,retryable=NULL,dead_lettered_at=NULL,operator_note=?,completed_at=NULL,updated_at=? WHERE id=?",(attempts,now,reason,now,queue_id))
            self._operator_action(con,queue_id,'replayed',operator,reason,{'resetAttempts':reset_attempts,'previousStatus':row['status']})
            self._event(con,'queue-item',queue_id,'operator-replayed',{'operatorId':operator,'reason':reason,'resetAttempts':reset_attempts})
            updated=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(queue_id,)).fetchone(); con.execute('COMMIT')
        return {'ok':True,'replayed':True,'queueItem':self._queue_dict(updated)}

    def replay_many(self, payload: dict[str, Any]) -> dict[str, Any]:
        ids=payload.get('queueIds') if isinstance(payload.get('queueIds'),list) else []
        if not ids: raise DispatcherError('At least one queue ID is required.')
        results=[]; errors=[]
        for queue_id in ids[:250]:
            try: results.append(self.replay(str(queue_id),payload)['queueItem'])
            except DispatcherError as exc: errors.append({'queueId':str(queue_id),'error':str(exc)})
        return {'ok':not errors,'replayed':len(results),'failed':len(errors),'queueItems':results,'errors':errors}

    def cancel_queue_item(self, queue_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload=payload if isinstance(payload,dict) else {}; queue_id=_text(queue_id,220); operator=_text(payload.get('operatorId'),180) or 'operator'; reason=_text(payload.get('reason'),1000) or 'operator cancellation'; now=_now()
        failure=classify_failure({'failureClass':'operator-cancelled','retryable':False,'error':reason})
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE'); row=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(queue_id,)).fetchone()
            if not row: con.execute('ROLLBACK'); raise DispatcherError('Dispatch queue item was not found.')
            if row['status']=='completed': con.execute('ROLLBACK'); raise DispatcherError('Completed queue items cannot be cancelled.')
            con.execute("UPDATE dispatcher_queue SET status='cancelled',lease_id=NULL,worker_id=NULL,lease_expires_at=NULL,error_text=?,failure_class=?,failure_code=?,retryable=0,operator_note=?,completed_at=?,updated_at=? WHERE id=?",(reason,failure['failureClass'],failure['failureCode'],reason,now,now,queue_id))
            con.execute("UPDATE dispatcher_contracts SET status='cancelled',updated_at=? WHERE queue_id=? AND status NOT IN ('completed','failed','cancelled')",(now,queue_id))
            self._operator_action(con,queue_id,'cancelled',operator,reason,{})
            self._event(con,'queue-item',queue_id,'operator-cancelled',{'operatorId':operator,'reason':reason})
            updated=con.execute("SELECT * FROM dispatcher_queue WHERE id=?",(queue_id,)).fetchone(); con.execute('COMMIT')
        return {'ok':True,'cancelled':True,'queueItem':self._queue_dict(updated)}

    def operations_metrics(self) -> dict[str, Any]:
        now=_now_dt(); hour=(now-timedelta(hours=1)).isoformat(); day=(now-timedelta(hours=24)).isoformat(); expiring=(now+timedelta(seconds=60)).isoformat()
        with self._connect() as con:
            counts={r['status']:r['n'] for r in con.execute("SELECT status,COUNT(*) n FROM dispatcher_queue GROUP BY status")}
            failures={r['failure_class'] or 'unclassified':r['n'] for r in con.execute("SELECT failure_class,COUNT(*) n FROM dispatcher_queue WHERE failure_class IS NOT NULL GROUP BY failure_class")}
            oldest=con.execute("SELECT created_at FROM dispatcher_queue WHERE status IN ('queued','retrying') ORDER BY created_at ASC LIMIT 1").fetchone()
            expiring_leases=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status IN ('leased','running') AND lease_expires_at<=?",(expiring,)).fetchone()[0]
            completed_hour=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status='completed' AND completed_at>=?",(hour,)).fetchone()[0]
            completed_day=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status='completed' AND completed_at>=?",(day,)).fetchone()[0]
            failed_hour=con.execute("SELECT COUNT(*) FROM dispatcher_queue WHERE status='dead-lettered' AND dead_lettered_at>=?",(hour,)).fetchone()[0]
            action_count=con.execute("SELECT COUNT(*) FROM dispatcher_operator_actions").fetchone()[0]
        oldest_age=0
        if oldest and oldest['created_at']:
            oldest_age=max(0,int((now-datetime.fromisoformat(oldest['created_at'])).total_seconds()))
        for state in ('queued','retrying','leased','running','completed','failed','cancelled','dead-lettered'): counts.setdefault(state,0)
        return {'ok':True,'version':VERSION,'capturedAt':now.isoformat(),'counts':counts,'failureClasses':failures,'queueDepth':counts['queued']+counts['retrying'],'oldestReadyAgeSeconds':oldest_age,'activeLeases':counts['leased']+counts['running'],'leasesExpiringWithin60Seconds':expiring_leases,'throughput':{'completedLastHour':completed_hour,'completedLast24Hours':completed_day,'deadLetteredLastHour':failed_hour},'operatorActionCount':action_count}

    def diagnostics(self) -> dict[str, Any]:
        path=Path(self.db_path); wal=Path(self.db_path+'-wal'); shm=Path(self.db_path+'-shm')
        with self._connect() as con:
            integrity=con.execute("PRAGMA integrity_check").fetchone()[0]
            journal=con.execute("PRAGMA journal_mode").fetchone()[0]
            foreign=con.execute("PRAGMA foreign_key_check").fetchall()
            page_count=con.execute("PRAGMA page_count").fetchone()[0]; page_size=con.execute("PRAGMA page_size").fetchone()[0]
        return {'ok':integrity=='ok' and not foreign,'version':VERSION,'databasePath':str(path),'databaseExists':path.exists(),'databaseBytes':path.stat().st_size if path.exists() else page_count*page_size,'walBytes':wal.stat().st_size if wal.exists() else 0,'sharedMemoryBytes':shm.stat().st_size if shm.exists() else 0,'journalMode':journal,'integrityCheck':integrity,'foreignKeyViolations':len(foreign),'schemaVersion':DB_SCHEMA_VERSION,'instanceLocalPath':not str(path).startswith('/app/data/')}

    def operations_health(self) -> dict[str, Any]:
        metrics=self.operations_metrics(); diagnostics=self.diagnostics()
        return {'ok':bool(diagnostics['ok']),'status':'ready' if diagnostics['ok'] else 'degraded','version':VERSION,'architecture':'dispatcher-operations-dead-letter-observability','failureClassification':True,'boundedRetries':True,'deadLetterRecovery':True,'operatorReplay':True,'queueMetrics':True,'eventTimelines':True,'databaseDiagnostics':True,'metrics':metrics,'diagnostics':diagnostics}

    def artifact_access_allowed(self, worker_id: str, artifact_id: str) -> bool:
        worker_id = _text(worker_id, 180)
        artifact_id = _text(artifact_id, 220)
        if not worker_id or not artifact_id:
            return False
        with self._connect() as con:
            rows = con.execute(
                "SELECT payload_json FROM dispatcher_queue WHERE worker_id=? AND status IN ('leased','running')",
                (worker_id,),
            ).fetchall()
        for row in rows:
            workload = self._loads(row['payload_json'])
            references = workload.get('artifactInputs') if isinstance(workload.get('artifactInputs'), list) else []
            for reference in references:
                if isinstance(reference, dict) and _text(reference.get('artifactId'), 220) == artifact_id:
                    return True
        return False

    def health(self)->dict[str,Any]:
        st=self.status(); workers=self.list(False)['workers']; ops=self.operations_health()
        return {'ok':ops['ok'],'status':ops['status'],'version':VERSION,'architecture':'persistent-distributed-compute-dispatcher','workerCount':len(workers),'onlineWorkers':sum(1 for w in workers if w['state']=='online'),'capabilityDiscovery':True,'workloadRouting':True,'signedDispatchContracts':True,'leases':True,'persistentWorkerRegistry':True,'persistentQueue':True,'restartRecovery':True,'horizontalCoordinatorSafeClaims':True,'storage':'sqlite-wal','schemaVersion':DB_SCHEMA_VERSION,'workerCredentials':st['credentials'],'queueCounts':st['counts'],'deadLetterRecovery':True,'failureClassification':True,'operatorReplay':True,'operationsStatus':ops['status'],'arbitraryCallbackUrls':False,'arbitraryCode':False}
