from fastapi.testclient import TestClient
from app.main import app
from app.distributed_dispatcher import DistributedDispatcher, normalize_worker, normalize_workload


def worker(worker_id="local-1", worker_type="local-python", active=0):
    return {"id":worker_id,"name":worker_id,"workerType":worker_type,"state":"online","capabilities":{"methods":["numerical.root.bracketed_polynomial","simulation.parameter_sweep"],"packages":["numpy","scipy"],"cpuCores":4,"memoryMb":4096,"checkpointing":True,"maxConcurrentJobs":2},"load":{"activeJobs":active,"queuedJobs":0},"tags":["trusted","cpu"]}

def workload():
    return {"method":"simulation.parameter_sweep","projectId":"project-1","targetPreference":["local-python","raspberry-pi"],"requiredPackages":["numpy"],"requiredTags":["trusted"],"minimumMemoryMb":512,"checkpointingRequired":True,"priority":70,"request":{"inputs":{"values":[1,2,3]}}}

def test_worker_and_workload_normalization():
    w=normalize_worker(worker()); q=normalize_workload(workload())
    assert w["version"]=="0.31.0" and w["capabilityFingerprint"]
    assert q["method"]=="simulation.parameter_sweep" and q["workloadHash"]

def test_capability_and_load_aware_routing():
    d=DistributedDispatcher(); d.register(worker("busy","local-python",1)); d.register(worker("free","raspberry-pi",0))
    out=d.route(workload()); assert out["ok"] and out["selectedWorker"]["id"] in {"busy","free"}
    assert out["candidateCount"]==2

def test_incompatible_worker_rejected():
    d=DistributedDispatcher(); d.register({**worker(),"capabilities":{"methods":["other.method"],"packages":["numpy"],"memoryMb":4096,"maxConcurrentJobs":1}})
    out=d.route(workload()); assert not out["ok"] and out["candidateCount"]==0

def test_contract_signature_acknowledgement_and_completion():
    d=DistributedDispatcher(); d.register(worker())
    built=d.build_contract(workload(),"secret"); c=built["contract"]
    assert d.verify_contract(c,"secret")["valid"]
    assert not d.verify_contract(c,"wrong")["valid"]
    assert d.acknowledge(c["id"],c["workerId"])["contract"]["status"]=="acknowledged"
    done=d.complete(c["id"],{"ok":True,"result":{"value":42}}); assert done["contract"]["status"]=="completed" and done["contract"]["resultHash"]

def test_heartbeat_updates_worker_load():
    d=DistributedDispatcher(); d.register(worker()); out=d.heartbeat("local-1",{"load":{"activeJobs":1,"queuedJobs":3}})
    assert out["worker"]["load"]=={"activeJobs":1,"queuedJobs":3}

def test_fastapi_dispatcher_routes():
    with TestClient(app) as client:
        assert client.get('/v1/dispatcher/health').json()["version"]=="0.31.0"
        reg=client.post('/v1/dispatcher/workers/register',json=worker("api-worker")); assert reg.status_code==200
        route=client.post('/v1/dispatcher/route',json=workload()); assert route.status_code==200 and route.json()["ok"]
        contract=client.post('/v1/dispatcher/contracts/build',json=workload()); assert contract.status_code==200
        verify=client.post('/v1/dispatcher/contracts/verify',json=contract.json()["contract"]); assert verify.status_code==200 and verify.json()["valid"]
