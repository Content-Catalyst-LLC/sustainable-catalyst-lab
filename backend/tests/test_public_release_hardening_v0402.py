import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.public_release_hardening import PublicReleaseHardeningError, PublicReleaseHardeningManager, REQUIRED_CLEAN_INSTALL_CHECKS, REQUIRED_RELEASE_EVIDENCE

def manager(tmp_path): return PublicReleaseHardeningManager(str(tmp_path/'release.sqlite3'),True)

def test_compatibility_matrix_blocks_unknown(tmp_path):
    m=manager(tmp_path); r=m.create_compatibility_matrix({'id':'matrix','dimensions':{'python':{'status':'supported','minimum':'3.12'},'browser':{'status':'unknown'}}},'release')
    assert r['matrix']['status']=='blocked' and 'browser' in r['matrix']['blockers']

def test_migration_requires_supported_baseline_backup_and_rollback(tmp_path):
    m=manager(tmp_path); blocked=m.assess_migration({'id':'bad','baselineVersion':'0.1.0'},'release')['assessment']; assert blocked['status']=='blocked'
    ready=m.assess_migration({'id':'good','baselineVersion':'0.40.1','backupVerified':True,'rollbackTested':True},'release')['assessment']; assert ready['status']=='ready' and ready['mode']=='dry-run' and ready['executionPermitted'] is False

def test_deprecation_registry(tmp_path):
    m=manager(tmp_path); r=m.register_deprecation({'id':'old-route','subject':'/v0/old','replacement':'/v1/new','status':'announced','removalVersion':'1.1.0'},'release')['deprecation']; assert r['replacement']=='/v1/new'

def test_clean_install_requires_complete_checklist(tmp_path):
    m=manager(tmp_path); checks=[{'id':x,'status':'pass'} for x in REQUIRED_CLEAN_INSTALL_CHECKS]
    assert m.create_clean_install_report({'id':'clean','checks':checks},'release')['report']['status']=='passed'
    assert m.create_clean_install_report({'id':'partial','checks':checks[:-1]},'release')['report']['status']=='blocked'

def test_rollback_requires_test_and_restore(tmp_path):
    m=manager(tmp_path); blocked=m.create_rollback_plan({'id':'rb1','backupId':'backup-1','activationProcedure':'operator controlled'},'release')['plan']; assert blocked['status']=='blocked'
    ready=m.create_rollback_plan({'id':'rb2','backupId':'backup-2','tested':True,'restoreVerified':True,'activationProcedure':'operator controlled'},'release')['plan']; assert ready['status']=='verified' and ready['productionOverwriteByApi'] is False

def test_release_candidate_gate(tmp_path):
    m=manager(tmp_path); evidence={k:{'status':'pass'} for k in REQUIRED_RELEASE_EVIDENCE}
    ready=m.create_release_candidate({'id':'rc1','evidence':evidence,'criticalDefects':[],'highDefects':[]},'release')['report']; assert ready['status']=='release-candidate-ready' and ready['generalAvailabilityClaim'] is False
    blocked=m.create_release_candidate({'id':'rc2','evidence':{**evidence,'security':{'status':'fail'}}},'release')['report']; assert blocked['status']=='blocked' and 'security' in blocked['blockers']

def test_sensitive_fields_rejected(tmp_path):
    m=manager(tmp_path)
    with pytest.raises(PublicReleaseHardeningError): m.create_release_candidate({'id':'x','evidence':{},'accessToken':'secret'},'release')

def test_timeline_tamper_detection(tmp_path):
    m=manager(tmp_path); m.register_deprecation({'id':'d','subject':'old','replacement':'new'},'release'); assert m.verify_timeline()['valid'] is True
    with m._connect() as db: db.execute("UPDATE release_hardening_events SET event_hash='bad' WHERE seq=1")
    assert m.verify_timeline()['valid'] is False

def test_contracts_parse():
    root=Path(__file__).parents[2]
    for name in ('compatibility-matrix-v0402.schema.json','migration-assessment-v0402.schema.json','deprecation-record-v0402.schema.json','clean-install-report-v0402.schema.json','rollback-plan-v0402.schema.json','release-candidate-report-v0402.schema.json'):
        assert json.loads((root/'contracts'/name).read_text())['$schema'].startswith('https://json-schema.org')

def test_fastapi_routes(monkeypatch,tmp_path):
    monkeypatch.setenv('SC_LAB_PUBLIC_RELEASE_HARDENING_DB_PATH',str(tmp_path/'api.sqlite3')); monkeypatch.setenv('SC_LAB_COMPUTE_API_KEY','test-key')
    import importlib, app.config as config; importlib.reload(config); import app.main as main; importlib.reload(main)
    c=TestClient(main.app); h={'X-SC-Lab-Key':'test-key','X-SC-Lab-Actor':'release'}
    assert c.get('/v1/public-release-hardening/health',headers=h).status_code==200
    r=c.post('/v1/public-release-hardening/migration-assessments',headers=h,json={'id':'api','baselineVersion':'0.40.1','backupVerified':True,'rollbackTested':True})
    assert r.status_code==200 and r.json()['assessment']['status']=='ready'
