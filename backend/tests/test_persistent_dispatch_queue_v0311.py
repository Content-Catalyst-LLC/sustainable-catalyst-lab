from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient

from app.persistent_dispatch_queue import PersistentDistributedDispatcher

def worker():
 return {'id':'worker-a','name':'Worker A','workerType':'local-python','capabilities':{'methods':['simulation.parameter_sweep'],'packages':['numpy'],'memoryMb':2048,'checkpointing':True,'maxConcurrentJobs':2},'tags':['local']}
def workload():
 return {'method':'simulation.parameter_sweep','projectId':'project-1','priority':80,'requiredPackages':['numpy'],'requiredTags':['local'],'minimumMemoryMb':512,'checkpointingRequired':True,'request':{'inputs':{'values':[1,2,3]}}}

def test_registry_survives_restart():
 with TemporaryDirectory() as td:
  path=str(Path(td)/'dispatcher.sqlite3'); a=PersistentDistributedDispatcher(path); a.register(worker()); b=PersistentDistributedDispatcher(path); assert b.list()['count']==1

def test_enqueue_deduplicates_active_workload():
 with TemporaryDirectory() as td:
  d=PersistentDistributedDispatcher(str(Path(td)/'d.sqlite3')); first=d.enqueue(workload()); second=d.enqueue(workload()); assert first['deduplicated'] is False and second['deduplicated'] is True and first['queueItem']['id']==second['queueItem']['id']

def test_claim_ack_complete_and_history():
 with TemporaryDirectory() as td:
  d=PersistentDistributedDispatcher(str(Path(td)/'d.sqlite3')); d.register(worker()); d.enqueue(workload()); claim=d.claim({'workerId':'worker-a','leaseSeconds':60},'secret'); assert claim['claimed']; c=claim['contract']; assert d.verify_contract(c,'secret')['valid']; d.acknowledge(c['id'],'worker-a'); out=d.complete(c['id'],{'ok':True,'result':{'value':4}}); assert out['contract']['status']=='completed'; assert d.status()['counts']['completed']==1; assert d.history()['count']>=4

def test_expired_lease_is_requeued():
 with TemporaryDirectory() as td:
  d=PersistentDistributedDispatcher(str(Path(td)/'d.sqlite3'),max_attempts=2); d.register(worker()); d.enqueue(workload()); c=d.claim({'workerId':'worker-a','leaseSeconds':30},'secret');
  with d._connect() as con: con.execute("UPDATE dispatcher_queue SET lease_expires_at='2000-01-01T00:00:00+00:00' WHERE lease_id=?",(c['contract']['leaseId'],))
  r=d.recover(); assert r['requeued']==1 and d.status()['counts']['queued']==1

def test_atomic_claim_prevents_double_lease():
 with TemporaryDirectory() as td:
  path=str(Path(td)/'d.sqlite3'); a=PersistentDistributedDispatcher(path); b=PersistentDistributedDispatcher(path); a.register(worker()); a.enqueue(workload()); one=a.claim({'workerId':'worker-a'},'secret'); two=b.claim({'workerId':'worker-a'},'secret'); assert one['claimed'] and not two['claimed']

def test_fastapi_persistent_queue_routes(monkeypatch,tmp_path):
 monkeypatch.setenv('SC_LAB_DISPATCHER_DB_PATH',str(tmp_path/'api.sqlite3'))
 import importlib,app.config,app.main
 importlib.reload(app.config); m=importlib.reload(app.main); client=TestClient(m.app)
 headers={'X-SC-Lab-API-Key':m.settings.api_key} if m.settings.api_key else {}
 assert client.get('/v1/dispatcher/queue/status',headers=headers).status_code==200
