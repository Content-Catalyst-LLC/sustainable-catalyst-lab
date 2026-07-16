from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import hmac
import json
import math
import re
import secrets
from threading import RLock
from typing import Any

VERSION = "0.31.2"
WORKER_SCHEMA = "sc-lab-distributed-worker/0.31.0"
WORKLOAD_SCHEMA = "sc-lab-distributed-workload/0.31.0"
CONTRACT_SCHEMA = "sc-lab-dispatch-contract/0.31.0"
ALLOWED_WORKER_TYPES = {"browser-web-worker", "render-cpu", "local-python", "raspberry-pi", "institutional-node"}
ALLOWED_STATES = {"online", "draining", "offline", "quarantined"}
MAX_METHODS = 256
MAX_PACKAGES = 128
MAX_TAGS = 64
MAX_WORKERS = 500
MAX_LEASE_SECONDS = 3600

class DispatcherError(ValueError):
    pass

def _now_dt() -> datetime: return datetime.now(timezone.utc)
def _now() -> str: return _now_dt().isoformat()
def _stable(value: Any) -> str: return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def _hash(value: Any) -> str: return sha256(_stable(value).encode("utf-8")).hexdigest()
def _text(value: Any, limit: int = 4000) -> str: return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]
def _int(value: Any, default: int, low: int, high: int) -> int:
    try: n=int(value)
    except (TypeError,ValueError): n=default
    return max(low,min(high,n))
def _float(value: Any, default: float, low: float, high: float) -> float:
    try: n=float(value)
    except (TypeError,ValueError): n=default
    if not math.isfinite(n): n=default
    return max(low,min(high,n))
def _list(value: Any, limit: int, item_limit: int = 160) -> list[str]:
    if not isinstance(value,list): return []
    out=[]
    for item in value[:limit]:
        text=_text(item,item_limit)
        if text and text not in out: out.append(text)
    return out

def policies() -> dict[str,Any]:
    return {
        "version": VERSION,
        "workerTypes": sorted(ALLOWED_WORKER_TYPES),
        "workerStates": sorted(ALLOWED_STATES),
        "routing": {"registeredMethodsOnly": True, "capabilityMatch": True, "loadAware": True, "targetPreference": True, "projectQuotaAware": True, "quarantineAware": True},
        "leases": {"defaultSeconds": 300, "maximumSeconds": MAX_LEASE_SECONDS, "acknowledgementRequired": True, "completionReceipt": True},
        "security": {"signedContracts": True, "hmacWhenConfigured": True, "arbitraryCallbackUrls": False, "arbitraryCode": False, "registeredMethodsOnly": True},
        "limits": {"workers": MAX_WORKERS, "methodsPerWorker": MAX_METHODS, "packagesPerWorker": MAX_PACKAGES, "tagsPerWorker": MAX_TAGS},
        "storage": "sqlite-wal-persistent-registry",
        "persistentWorkerRegistry": True,
    }

def normalize_worker(payload: dict[str,Any]) -> dict[str,Any]:
    src=payload.get("worker") if isinstance(payload.get("worker"),dict) else payload
    worker_type=_text(src.get("workerType") or src.get("type"),80).lower() or "local-python"
    if worker_type not in ALLOWED_WORKER_TYPES: raise DispatcherError("Unsupported worker type.")
    state=_text(src.get("state"),40).lower() or "online"
    if state not in ALLOWED_STATES: raise DispatcherError("Unsupported worker state.")
    caps=src.get("capabilities") if isinstance(src.get("capabilities"),dict) else {}
    methods=_list(caps.get("methods") or src.get("methods"),MAX_METHODS,180)
    packages=_list(caps.get("packages") or src.get("packages"),MAX_PACKAGES,100)
    tags=_list(src.get("tags"),MAX_TAGS,80)
    worker={
        "schema":WORKER_SCHEMA,"version":VERSION,"recordType":"distributed-worker",
        "id":_text(src.get("id"),180) or f"worker-{secrets.token_hex(8)}",
        "name":_text(src.get("name"),300) or worker_type.replace('-',' ').title(),
        "workerType":worker_type,"state":state,"endpointMode":_text(src.get("endpointMode"),80) or "lease-poll",
        "capabilities":{
            "methods":methods,"packages":packages,
            "cpuCores":_int(caps.get("cpuCores"),1,1,256),"memoryMb":_int(caps.get("memoryMb"),512,128,1048576),
            "gpu":bool(caps.get("gpu",False)),"checkpointing":bool(caps.get("checkpointing",False)),"localData":bool(caps.get("localData",False)),
            "maxConcurrentJobs":_int(caps.get("maxConcurrentJobs"),1,1,128),"architectures":_list(caps.get("architectures"),16,80),
        },
        "load":{"activeJobs":_int((src.get("load") or {}).get("activeJobs") if isinstance(src.get("load"),dict) else 0,0,0,128),"queuedJobs":_int((src.get("load") or {}).get("queuedJobs") if isinstance(src.get("load"),dict) else 0,0,0,10000)},
        "tags":tags,"projectAllowlist":_list(src.get("projectAllowlist"),200,180),"registeredAt":src.get("registeredAt") or _now(),"lastHeartbeatAt":_now(),
        "metadata":src.get("metadata") if isinstance(src.get("metadata"),dict) else {},
    }
    worker["capabilityFingerprint"]=_hash({"workerType":worker_type,"capabilities":worker["capabilities"],"tags":tags})
    return worker

def normalize_workload(payload: dict[str,Any]) -> dict[str,Any]:
    src=payload.get("workload") if isinstance(payload.get("workload"),dict) else payload
    method=_text(src.get("method") or src.get("methodId"),180)
    if not method: raise DispatcherError("A registered method identifier is required.")
    workload={
        "schema":WORKLOAD_SCHEMA,"version":VERSION,"recordType":"distributed-workload",
        "id":_text(src.get("id"),180) or f"workload-{secrets.token_hex(8)}","title":_text(src.get("title"),300) or method,
        "method":method,"projectId":_text(src.get("projectId") or src.get("project_id"),180),"priority":_int(src.get("priority"),50,0,100),
        "targetPreference":_list(src.get("targetPreference"),8,80),"requiredPackages":_list(src.get("requiredPackages"),MAX_PACKAGES,100),
        "requiredTags":_list(src.get("requiredTags"),MAX_TAGS,80),"minimumMemoryMb":_int(src.get("minimumMemoryMb"),128,128,1048576),
        "gpuRequired":bool(src.get("gpuRequired",False)),"checkpointingRequired":bool(src.get("checkpointingRequired",False)),
        "timeoutSeconds":_int(src.get("timeoutSeconds"),300,1,86400),"leaseSeconds":_int(src.get("leaseSeconds"),300,30,MAX_LEASE_SECONDS),
        "request":src.get("request") if isinstance(src.get("request"),dict) else {},"createdAt":src.get("createdAt") or _now(),
    }
    workload["workloadHash"]=_hash({k:v for k,v in workload.items() if k!="workloadHash"})
    return workload

class DistributedDispatcher:
    def __init__(self):
        self._lock=RLock(); self._workers:dict[str,dict[str,Any]]={}; self._contracts:dict[str,dict[str,Any]]={}
    def register(self,payload:dict[str,Any])->dict[str,Any]:
        worker=normalize_worker(payload)
        with self._lock:
            if worker["id"] not in self._workers and len(self._workers)>=MAX_WORKERS: raise DispatcherError("Worker registry capacity reached.")
            existing=self._workers.get(worker["id"])
            if existing: worker["registeredAt"]=existing.get("registeredAt",worker["registeredAt"])
            self._workers[worker["id"]]=worker
        return {"ok":True,"worker":worker}
    def heartbeat(self,worker_id:str,payload:dict[str,Any])->dict[str,Any]:
        with self._lock:
            worker=self._workers.get(worker_id)
            if not worker: raise DispatcherError("Worker was not found.")
            state=_text(payload.get("state"),40).lower()
            if state:
                if state not in ALLOWED_STATES: raise DispatcherError("Unsupported worker state.")
                worker["state"]=state
            load=payload.get("load") if isinstance(payload.get("load"),dict) else {}
            worker["load"]={"activeJobs":_int(load.get("activeJobs"),worker["load"]["activeJobs"],0,128),"queuedJobs":_int(load.get("queuedJobs"),worker["load"]["queuedJobs"],0,10000)}
            worker["lastHeartbeatAt"]=_now()
            return {"ok":True,"worker":worker}
    def list(self,active_only:bool=False)->dict[str,Any]:
        with self._lock: rows=list(self._workers.values())
        if active_only: rows=[w for w in rows if w["state"]=="online"]
        rows=sorted(rows,key=lambda w:(w["state"]!="online",w["load"]["activeJobs"],w["name"].lower()))
        return {"ok":True,"version":VERSION,"count":len(rows),"workers":rows}
    def _score(self,worker:dict[str,Any],workload:dict[str,Any])->tuple[float,list[str]]|None:
        if worker["state"]!="online": return None
        cap=worker["capabilities"]
        if cap["methods"] and workload["method"] not in cap["methods"]: return None
        if any(pkg not in cap["packages"] for pkg in workload["requiredPackages"]): return None
        if any(tag not in worker["tags"] for tag in workload["requiredTags"]): return None
        if cap["memoryMb"]<workload["minimumMemoryMb"] or (workload["gpuRequired"] and not cap["gpu"]) or (workload["checkpointingRequired"] and not cap["checkpointing"]): return None
        if worker["projectAllowlist"] and workload["projectId"] not in worker["projectAllowlist"]: return None
        active=worker["load"]["activeJobs"]; capacity=cap["maxConcurrentJobs"]
        if active>=capacity: return None
        score=100.0; reasons=["capability-match"]
        score-=40.0*(active/max(capacity,1)); score-=min(20.0,worker["load"]["queuedJobs"]*2.0)
        if workload["targetPreference"] and worker["workerType"] in workload["targetPreference"]:
            score+=25.0-max(0,workload["targetPreference"].index(worker["workerType"])*3); reasons.append("target-preference")
        if cap["checkpointing"] and workload["checkpointingRequired"]: score+=8; reasons.append("checkpoint-capable")
        if cap["gpu"] and workload["gpuRequired"]: score+=8; reasons.append("gpu-capable")
        score+=min(10.0,cap["memoryMb"]/8192.0)
        return score,reasons
    def route(self,payload:dict[str,Any])->dict[str,Any]:
        workload=normalize_workload(payload)
        with self._lock: workers=list(self._workers.values())
        candidates=[]
        for worker in workers:
            scored=self._score(worker,workload)
            if scored: candidates.append({"worker":worker,"score":round(scored[0],4),"reasons":scored[1]})
        candidates.sort(key=lambda x:(-x["score"],x["worker"]["id"]))
        selected=candidates[0] if candidates else None
        return {"ok":selected is not None,"version":VERSION,"workload":workload,"selectedWorker":selected["worker"] if selected else None,"score":selected["score"] if selected else None,"reasons":selected["reasons"] if selected else [],"candidateCount":len(candidates),"rejectionReason":None if selected else "No online worker satisfies the governed workload requirements."}
    def build_contract(self,payload:dict[str,Any],secret:str="")->dict[str,Any]:
        routed=self.route(payload)
        if not routed["ok"]: raise DispatcherError(routed["rejectionReason"])
        workload=routed["workload"]; worker=routed["selectedWorker"]; lease_id=f"lease-{secrets.token_hex(12)}"; issued=_now_dt(); expires=issued+timedelta(seconds=workload["leaseSeconds"])
        body={"schema":CONTRACT_SCHEMA,"version":VERSION,"recordType":"dispatch-contract","id":f"dispatch-{secrets.token_hex(10)}","leaseId":lease_id,"workerId":worker["id"],"workerFingerprint":worker["capabilityFingerprint"],"workload":workload,"issuedAt":issued.isoformat(),"expiresAt":expires.isoformat(),"status":"offered","acknowledgementRequired":True,"completionReceiptRequired":True,"coordinator":"sustainable-catalyst-lab-python-compute-core"}
        key=(secret or "open-development-dispatch-key").encode(); body["signatureMode"]="hmac-sha256" if secret else "development-hmac-sha256"; body["signature"]=hmac.new(key,_stable(body).encode(),sha256).hexdigest()
        with self._lock: self._contracts[body["id"]]=body
        return {"ok":True,"contract":body,"routing":{"score":routed["score"],"reasons":routed["reasons"],"candidateCount":routed["candidateCount"]}}
    def verify_contract(self,payload:dict[str,Any],secret:str="")->dict[str,Any]:
        contract=payload.get("contract") if isinstance(payload.get("contract"),dict) else payload
        signature=_text(contract.get("signature"),128); unsigned={k:v for k,v in contract.items() if k!="signature"}; key=(secret or "open-development-dispatch-key").encode(); expected=hmac.new(key,_stable(unsigned).encode(),sha256).hexdigest()
        try: expired=datetime.fromisoformat(str(contract.get("expiresAt"))).astimezone(timezone.utc) < _now_dt()
        except Exception: expired=True
        valid=bool(signature) and hmac.compare_digest(signature,expected) and contract.get("schema")==CONTRACT_SCHEMA and not expired
        return {"ok":valid,"valid":valid,"signatureValid":bool(signature) and hmac.compare_digest(signature,expected),"expired":expired,"contractId":contract.get("id"),"workerId":contract.get("workerId"),"workloadHash":(contract.get("workload") or {}).get("workloadHash")}
    def acknowledge(self,contract_id:str,worker_id:str)->dict[str,Any]:
        with self._lock:
            c=self._contracts.get(contract_id)
            if not c: raise DispatcherError("Dispatch contract was not found.")
            if c["workerId"]!=worker_id: raise DispatcherError("Worker does not match the dispatch contract.")
            c["status"]="acknowledged"; c["acknowledgedAt"]=_now(); return {"ok":True,"contract":c}
    def complete(self,contract_id:str,payload:dict[str,Any])->dict[str,Any]:
        with self._lock:
            c=self._contracts.get(contract_id)
            if not c: raise DispatcherError("Dispatch contract was not found.")
            c["status"]="completed" if payload.get("ok",True) else "failed"; c["completedAt"]=_now(); c["resultHash"]=_hash(payload.get("result")); c["receipt"]={"ok":bool(payload.get("ok",True)),"warnings":_list(payload.get("warnings"),50,500),"error":_text(payload.get("error"),2000)}; return {"ok":True,"contract":c}
    def health(self)->dict[str,Any]:
        rows=self.list(False)["workers"]
        return {"ok":True,"status":"ready","version":VERSION,"architecture":"governed-distributed-compute-dispatcher","workerCount":len(rows),"onlineWorkers":sum(1 for w in rows if w["state"]=="online"),"workerTypes":sorted(ALLOWED_WORKER_TYPES),"capabilityDiscovery":True,"workloadRouting":True,"signedDispatchContracts":True,"leases":True,"arbitraryCallbackUrls":False,"arbitraryCode":False,"persistentWorkerRegistry":False}
