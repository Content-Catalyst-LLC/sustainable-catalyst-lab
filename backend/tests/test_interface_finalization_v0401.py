import hashlib
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.interface_finalization import InterfaceFinalizationError, InterfaceFinalizationManager, REQUIRED_CHECKS


def checks(status="pass"):
    return [{"id": item, "status": status, "count": 0} for item in REQUIRED_CHECKS]


def test_complete_accessibility_audit_is_ready(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    result=mgr.create_audit({"id":"phone-audit","profile":"phone","checks":checks()},"auditor")
    assert result["audit"]["status"]=="ready"
    assert result["audit"]["score"]==100.0


def test_failed_check_blocks_readiness(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    values=checks(); values[0]["status"]="fail"
    audit=mgr.create_audit({"id":"bad-audit","profile":"tablet","checks":values},"auditor")["audit"]
    assert audit["status"]=="needs-attention"
    assert "no-horizontal-overflow" in audit["failedChecks"]


def test_preferences_enforce_touch_minimum(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    profile=mgr.save_preferences("researcher",{"touchTargetMinimumPx":20,"reducedMotion":True},"researcher")["profile"]
    assert profile["touchTargetMinimumPx"]==44
    assert mgr.get_preferences("researcher")["profile"]["reducedMotion"] is True


def test_offline_snapshot_is_metadata_only_and_rejects_restricted(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    digest=hashlib.sha256(b"asset").hexdigest()
    snap=mgr.create_snapshot({"id":"snap","projectId":"p1","workspaceId":"w1","classification":"internal","assets":[{"id":"a1","url":"/artifact/a1","sha256":digest,"sizeBytes":5}]},"researcher")["snapshot"]
    assert snap["backendStoresRawPayload"] is False
    with pytest.raises(InterfaceFinalizationError):
        mgr.create_snapshot({"id":"restricted","projectId":"p1","workspaceId":"w1","classification":"restricted","assets":[]},"researcher")


def test_offline_queue_is_idempotent_and_conflict_safe(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    payload={"id":"op1","idempotencyKey":"same","workspaceId":"w1","projectId":"p1","operation":"save-draft","payload":{"title":"Draft"}}
    first=mgr.queue_operation(payload,"researcher")
    second=mgr.queue_operation(payload,"researcher")
    assert first["idempotent"] is False and second["idempotent"] is True
    with pytest.raises(InterfaceFinalizationError):
        mgr.queue_operation({**payload,"payload":{"title":"Different"}},"researcher")


def test_reconciliation_retains_conflicts(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    mgr.queue_operation({"id":"op1","workspaceId":"w1","projectId":"p1","operation":"update","payload":{"field":"value"}},"researcher")
    receipt=mgr.reconcile({"id":"receipt1","decisions":[{"operationId":"op1","status":"conflict","remoteVersion":"v2","resolution":"Manual review"}]},"sync-agent")["receipt"]
    assert receipt["conflictCount"]==1
    assert mgr.list_operations("conflict")["operations"][0]["status"]=="conflict"


def test_sensitive_or_executable_payloads_are_rejected(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    with pytest.raises(InterfaceFinalizationError):
        mgr.queue_operation({"id":"op","workspaceId":"w","projectId":"p","operation":"update","payload":{"accessToken":"secret"}},"actor")
    with pytest.raises(InterfaceFinalizationError):
        mgr.queue_operation({"id":"op2","workspaceId":"w","projectId":"p","operation":"update","payload":{"note":"<script>alert(1)</script>"}},"actor")


def test_timeline_verification(tmp_path):
    mgr=InterfaceFinalizationManager(str(tmp_path/'ui.sqlite3'), True)
    mgr.save_preferences("p",{},"actor")
    assert mgr.verify_timeline()["valid"] is True
    with mgr._connect() as db: db.execute("UPDATE interface_events SET event_hash='tampered' WHERE seq=1")
    assert mgr.verify_timeline()["valid"] is False


def test_contract_schemas_parse():
    root=Path(__file__).parents[2]
    for name in ("interface-finalization-audit-v0401.schema.json","accessibility-preferences-v0401.schema.json","offline-project-snapshot-v0401.schema.json","offline-operation-v0401.schema.json","offline-reconciliation-receipt-v0401.schema.json"):
        data=json.loads((root/'contracts'/name).read_text())
        assert data["$schema"].startswith("https://json-schema.org")


def test_fastapi_routes(monkeypatch,tmp_path):
    monkeypatch.setenv("SC_LAB_INTERFACE_FINALIZATION_DB_PATH",str(tmp_path/'api.sqlite3'))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY","test-key")
    import importlib
    import app.config as config
    importlib.reload(config)
    import app.main as main
    importlib.reload(main)
    client=TestClient(main.app)
    headers={"X-SC-Lab-Key":"test-key","X-SC-Lab-Actor":"tester"}
    assert client.get('/v1/interface-finalization/health',headers=headers).status_code==200
    response=client.post('/v1/interface-finalization/audits',headers=headers,json={"id":"api-audit","profile":"desktop","checks":checks()})
    assert response.status_code==200 and response.json()["audit"]["status"]=="ready"
    queued=client.post('/v1/interface-finalization/offline-operations',headers=headers,json={"id":"api-op","workspaceId":"w","projectId":"p","operation":"save-draft","payload":{"title":"Draft"}})
    assert queued.status_code==200
