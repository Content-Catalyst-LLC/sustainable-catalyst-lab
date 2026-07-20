from __future__ import annotations
import importlib, json
from pathlib import Path
from fastapi.testclient import TestClient
from app.performance_chaos_validation import PerformanceChaosManager, policies


def manager(tmp_path: Path) -> PerformanceChaosManager:
    return PerformanceChaosManager(str(tmp_path/'performance.sqlite3'), True, 8, 500, 1000, 5000, .1)


def test_catalog_policy_and_health(tmp_path):
    store=manager(tmp_path)
    assert store.health()['serviceVersion']=='0.39.3'
    assert len(store.catalog()['workloads'])==5
    assert policies(True)['capabilities']['productionChaos'] is False


def test_load_profile_metrics_and_budget(tmp_path):
    run=manager(tmp_path).run_load({'id':'api-read-baseline','profile':'api-read','iterations':60,'concurrency':4,'budget':{'p95Ms':5000,'maxErrorRate':0,'minThroughputPerSecond':1}},'tester')['run']
    assert run['status']=='passed' and run['metrics']['iterations']==60
    assert run['metrics']['latencyMs']['p95'] >= 0
    assert run['productionResourcesMutated'] is False


def test_sqlite_write_load_is_isolated(tmp_path):
    run=manager(tmp_path).run_load({'id':'write-baseline','profile':'api-write','iterations':24,'concurrency':2,'budget':{'p95Ms':10000,'maxErrorRate':0.2}},'tester')['run']
    assert run['metrics']['errors'] <= 4
    assert not list(tmp_path.glob('load.sqlite3'))


def test_all_chaos_scenarios_are_safe_and_recover(tmp_path):
    store=manager(tmp_path)
    for scenario in ('database-lock','storage-latency','worker-termination','network-timeout','partial-write'):
        run=store.run_chaos({'id':'chaos-'+scenario,'scenario':scenario},'tester')['run']
        assert run['status']=='passed'
        assert run['productionResourcesMutated'] is False
        assert run['externalTrafficGenerated'] is False


def test_capacity_report_is_evidence_bounded(tmp_path):
    store=manager(tmp_path)
    store.run_load({'id':'capacity-source','profile':'api-read','iterations':20,'concurrency':2,'budget':{'p95Ms':5000,'maxErrorRate':0}},'tester')
    report=store.capacity_report({'id':'capacity-report'},'tester')['report']
    assert report['runCount']==1 and report['productionSizingClaim'] is False
    assert report['profiles']['api-read']['maxValidatedConcurrency']==2


def test_contract_instances(tmp_path):
    import jsonschema
    store=manager(tmp_path)
    load=store.run_load({'id':'contract-load','profile':'api-read','iterations':10,'concurrency':2,'budget':{'p95Ms':5000}},'tester')['run']
    chaos=store.run_chaos({'id':'contract-chaos','scenario':'network-timeout'},'tester')['run']
    report=store.capacity_report({'id':'contract-capacity'},'tester')['report']
    contracts=Path(__file__).resolve().parents[1]/'contracts'
    for name,value in (('performance-validation-run-v0393.schema.json',load),('chaos-validation-run-v0393.schema.json',chaos),('capacity-report-v0393.schema.json',report)):
        jsonschema.Draft202012Validator(json.loads((contracts/name).read_text())).validate(value)


def test_fastapi_routes(tmp_path, monkeypatch):
    monkeypatch.setenv('SC_LAB_COMPUTE_API_KEY','perf-key')
    monkeypatch.setenv('SC_LAB_PERFORMANCE_VALIDATION_DB_PATH',str(tmp_path/'route-performance.sqlite3'))
    import app.config as config_module, app.main as main_module
    importlib.reload(config_module); importlib.reload(main_module)
    client=TestClient(main_module.app); headers={'X-SC-Lab-Key':'perf-key','X-SC-Lab-Actor':'performance-admin'}
    health=client.get('/v1/performance-validation/health',headers=headers)
    assert health.status_code==200 and health.json()['serviceVersion']=='0.39.3'
    load=client.post('/v1/performance-validation/load-runs',headers=headers,json={'id':'route-load','profile':'api-read','iterations':12,'concurrency':2,'budget':{'p95Ms':5000}})
    assert load.status_code==200 and load.json()['run']['kind']=='load'
    chaos=client.post('/v1/performance-validation/chaos-runs',headers=headers,json={'id':'route-chaos','scenario':'partial-write'})
    assert chaos.status_code==200 and chaos.json()['run']['status']=='passed'
