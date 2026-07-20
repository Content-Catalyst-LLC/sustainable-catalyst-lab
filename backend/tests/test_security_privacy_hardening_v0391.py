from __future__ import annotations

import base64
import importlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.security_privacy_hardening import SecurityHardeningError, SecurityPrivacyManager, policies, privacy_redact, privacy_scan


def key(seed: bytes = b"k") -> str:
    return base64.urlsafe_b64encode((seed * 32)[:32]).decode().rstrip("=")


def manager(tmp_path: Path) -> SecurityPrivacyManager:
    return SecurityPrivacyManager(str(tmp_path / "security.sqlite3"), key(), "", "audit-secret", True, 100, 100, 1000, 30)


def test_policy_and_locked_vault(tmp_path):
    locked = SecurityPrivacyManager(str(tmp_path / "locked.sqlite3"))
    assert locked.health()["vaultLocked"] is True
    assert policies(True, True)["capabilities"]["aes256GcmSecretVault"] is True
    with pytest.raises(SecurityHardeningError) as exc:
        locked.put_secret("institution-one", {"name": "api-key", "value": "secret"}, "alice")
    assert exc.value.status_code == 503


def test_secret_encryption_rotation_and_no_plaintext_storage(tmp_path):
    store = manager(tmp_path)
    first = store.put_secret("institution-one", {"name": "provider-key", "value": "alpha-secret"}, "alice")
    second = store.put_secret("institution-one", {"name": "provider-key", "value": "beta-secret"}, "alice")
    assert first["secret"]["version"] == 1 and second["secret"]["version"] == 2
    assert store.resolve_secret("institution-one", "provider-key") == "beta-secret"
    listing = store.list_secrets("institution-one", "alice", "provider-key")
    assert listing["valuesDisclosed"] is False
    raw = (tmp_path / "security.sqlite3").read_bytes()
    assert b"alpha-secret" not in raw and b"beta-secret" not in raw
    assert store.verify_secret("institution-one", "provider-key", "beta-secret", "alice")["valid"] is True


def test_previous_key_can_decrypt_old_secret(tmp_path):
    first = SecurityPrivacyManager(str(tmp_path / "rotation.sqlite3"), key(b"a"))
    first.put_secret("institution-one", {"name": "rotating", "value": "old-value"}, "alice")
    old_raw = base64.urlsafe_b64decode(key(b"a") + "==")
    old_id = __import__("hashlib").sha256(old_raw).hexdigest()[:16]
    second = SecurityPrivacyManager(str(tmp_path / "rotation.sqlite3"), key(b"b"), json.dumps({old_id: key(b"a")}))
    assert second.resolve_secret("institution-one", "rotating") == "old-value"
    second.put_secret("institution-one", {"name": "rotating", "value": "new-value"}, "alice")
    assert second.resolve_secret("institution-one", "rotating") == "new-value"


def test_service_credentials_are_one_time_and_hashed(tmp_path):
    store = manager(tmp_path)
    issued = store.issue_credential("institution-one", "compute-agent", {"label": "Compute", "scopes": ["research:read", "research:write"], "ttlDays": 30}, "alice")
    token = issued["token"]
    assert issued["tokenDisclosure"] == "one-time"
    assert store.verify_credential(token, "research:write")["valid"] is True
    assert store.verify_credential(token, "admin:write")["valid"] is False
    listing = store.list_credentials("institution-one", "alice")
    assert listing["tokensDisclosed"] is False
    raw = (tmp_path / "security.sqlite3").read_bytes()
    assert token.encode() not in raw
    store.revoke_credential("institution-one", issued["credential"]["id"], "alice")
    assert store.verify_credential(token)["valid"] is False


def test_privacy_scan_and_redaction_never_echo_secrets():
    payload = {"email": "person@example.org", "phone": "312-555-0100", "api_key": "do-not-return", "nested": {"refreshToken": "also-secret"}}
    scan = privacy_scan(payload)
    assert scan["containsSensitiveData"] is True and scan["findingCount"] >= 4
    redacted = privacy_redact(payload)
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["email"] == "[EMAIL]" and redacted["phone"] == "[PHONE]"
    assert "do-not-return" not in json.dumps(redacted)


def test_privacy_request_workflow(tmp_path):
    store = manager(tmp_path)
    created = store.create_privacy_request("institution-one", {"id": "privacy-one", "requestType": "access", "subjectReference": "researcher-42"}, "alice")
    assert created["privacyRequest"]["status"] == "open"
    resolved = store.resolve_privacy_request("institution-one", "privacy-one", {"status": "completed", "resolution": "Export delivered securely."}, "privacy-officer")
    assert resolved["status"] == "completed"
    assert store.list_privacy_requests("institution-one", "alice", "completed")["privacyRequests"][0]["id"] == "privacy-one"


def test_audit_chain_is_signed_and_tamper_evident(tmp_path):
    store = manager(tmp_path)
    store.put_secret("institution-one", {"name": "provider-key", "value": "secret-value"}, "alice")
    store.issue_credential("institution-one", "compute-agent", {"label": "Agent"}, "alice")
    verified = store.verify_audit_chain("institution-one", "auditor")
    assert verified["valid"] is True and verified["signed"] is True
    timeline = store.audit_timeline("institution-one", "auditor")["events"]
    assert all(event["signature"] for event in timeline)
    assert "secret-value" not in json.dumps(timeline)
    import sqlite3
    with sqlite3.connect(tmp_path / "security.sqlite3") as db:
        db.execute("UPDATE security_audit_events SET detail_json='{}' WHERE sequence=(SELECT MIN(sequence) FROM security_audit_events)")
    assert store.verify_audit_chain("institution-one", "auditor")["valid"] is False


def test_contract_instances(tmp_path):
    import jsonschema
    store = manager(tmp_path)
    secret = store.put_secret("institution-one", {"name": "provider-key", "value": "secret-value"}, "alice")["secret"]
    credential = store.issue_credential("institution-one", "compute-agent", {"label": "Agent"}, "alice")["credential"]
    privacy = store.create_privacy_request("institution-one", {"id": "privacy-contract", "requestType": "access", "subjectReference": "subject-1"}, "alice")["privacyRequest"]
    event = store.audit_timeline("institution-one", "auditor", 1)["events"][0]
    contracts = Path(__file__).resolve().parents[1] / "contracts"
    for name, value in (("secret-record-v0391.schema.json", secret), ("service-credential-v0391.schema.json", credential), ("privacy-request-v0391.schema.json", privacy), ("security-audit-event-v0391.schema.json", event)):
        jsonschema.Draft202012Validator(json.loads((contracts / name).read_text())).validate(value)


def test_fastapi_routes_and_security_headers(tmp_path, monkeypatch):
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "route-key")
    monkeypatch.setenv("SC_LAB_SECURITY_PRIVACY_DB_PATH", str(tmp_path / "route-security.sqlite3"))
    monkeypatch.setenv("SC_LAB_SECURITY_REPLAY_DB_PATH", str(tmp_path / "route-replay.sqlite3"))
    monkeypatch.setenv("SC_LAB_SECRET_MASTER_KEY", key())
    monkeypatch.setenv("SC_LAB_AUDIT_SIGNING_SECRET", "audit-route")
    import app.config as config_module
    import app.main as main_module
    importlib.reload(config_module)
    importlib.reload(main_module)
    client = TestClient(main_module.app)
    headers = {"X-SC-Lab-Key": "route-key", "X-SC-Lab-Actor": "alice"}
    health = client.get("/v1/security-privacy/health", headers=headers)
    assert health.status_code == 200 and health.json()["serviceVersion"] == "0.40.0"
    assert health.headers["x-content-type-options"] == "nosniff"
    created = client.post("/v1/institutions/institution-one/secrets", headers=headers, json={"name": "provider-key", "value": "route-secret"})
    assert created.status_code == 200 and "route-secret" not in created.text
    scan = client.post("/v1/security-privacy/privacy-scan", headers=headers, json={"email": "person@example.org"})
    assert scan.json()["containsSensitiveData"] is True


def test_hmac_nonce_replay_is_rejected(tmp_path, monkeypatch):
    import time
    monkeypatch.setenv("SC_LAB_COMPUTE_SIGNING_SECRET", "signed-route-secret")
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "")
    monkeypatch.setenv("SC_LAB_REQUIRE_REQUEST_NONCE", "1")
    monkeypatch.setenv("SC_LAB_SECURITY_PRIVACY_DB_PATH", str(tmp_path / "signed-security.sqlite3"))
    monkeypatch.setenv("SC_LAB_SECURITY_REPLAY_DB_PATH", str(tmp_path / "signed-replay.sqlite3"))
    import app.config as config_module
    import app.main as main_module
    import app.security as security_module
    importlib.reload(config_module)
    importlib.reload(security_module)
    importlib.reload(main_module)
    client = TestClient(main_module.app)
    timestamp = str(int(time.time()))
    path = "/v1/security-privacy/health"
    signature = security_module.make_signature("signed-route-secret", timestamp, "GET", path, b"")
    headers = {"X-SC-Lab-Timestamp": timestamp, "X-SC-Lab-Signature": signature, "X-SC-Lab-Nonce": "unique_nonce_value_123456", "X-SC-Lab-Actor": "alice"}
    assert client.get(path, headers=headers).status_code == 200
    replay = client.get(path, headers=headers)
    assert replay.status_code == 409
    assert "replayed" in replay.json()["detail"].lower()
