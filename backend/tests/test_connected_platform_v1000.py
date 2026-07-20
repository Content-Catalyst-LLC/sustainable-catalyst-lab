import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.connected_platform import (
    ConnectedPlatformError,
    ConnectedScientificPlatform,
    REQUIRED_GA_EVIDENCE,
    REQUIRED_INCIDENT_CHECKS,
)


def manager(tmp_path):
    return ConnectedScientificPlatform(str(tmp_path / "stable.sqlite3"), True)


def test_contract_registry_and_semver(tmp_path):
    result = manager(tmp_path).register_contract(
        {"id": "research-api", "name": "Research API", "versions": ["v1"], "compatibilityPolicy": "semantic-versioning"},
        "release",
    )["contract"]
    assert result["status"] == "stable"
    assert result["breakingChangesRequireMajorVersion"] is True
    assert result["releaseVersion"] == "1.0.0"


def test_support_lifecycle(tmp_path):
    result = manager(tmp_path).declare_support_lifecycle(
        {
            "id": "v1",
            "releaseVersion": "1.0.0",
            "supportStart": "2026-07-20",
            "maintenanceEnd": "2027-07-20",
            "securityEnd": "2028-07-20",
        },
        "release",
    )["lifecycle"]
    assert result["status"] == "supported"


def test_upgrade_certification_requires_all_proofs(tmp_path):
    platform = manager(tmp_path)
    assert platform.certify_upgrade({"id": "bad", "baselineVersion": "0.40.2"}, "release")["certification"]["status"] == "blocked"
    ready = platform.certify_upgrade(
        {
            "id": "good",
            "baselineVersion": "0.40.2",
            "backupVerified": True,
            "rollbackVerified": True,
            "migrationPassed": True,
            "packageParityVerified": True,
        },
        "release",
    )["certification"]
    assert ready["status"] == "certified"
    assert ready["forcePushRequired"] is False


def test_production_attestation(tmp_path):
    components = {item: {"status": "pass"} for item in ("api", "compute", "wordpress", "governance", "security", "recovery", "monitoring")}
    ready = manager(tmp_path).attest_production_readiness(
        {"id": "prod", "components": components, "monitoringEnabled": True, "persistentStorageVerified": True},
        "release",
    )["attestation"]
    assert ready["status"] == "production-ready"


def test_incident_readiness(tmp_path):
    checks = [{"id": item, "status": "pass"} for item in REQUIRED_INCIDENT_CHECKS]
    assert manager(tmp_path).attest_incident_readiness({"id": "incident", "checks": checks}, "release")["attestation"]["status"] == "ready"


def test_general_availability_gate(tmp_path):
    platform = manager(tmp_path)
    evidence = {key: {"status": "pass"} for key in REQUIRED_GA_EVIDENCE}
    ready = platform.certify_general_availability(
        {"id": "v1-ga", "evidence": evidence, "criticalDefects": [], "highDefects": []},
        "release",
    )["certification"]
    assert ready["status"] == "general-availability-certified"
    assert ready["generalAvailabilityClaim"] is True
    blocked = platform.certify_general_availability(
        {"id": "v1-blocked", "evidence": {**evidence, "securityPrivacy": {"status": "fail"}}},
        "release",
    )["certification"]
    assert blocked["status"] == "blocked"
    assert blocked["generalAvailabilityClaim"] is False


def test_sensitive_payloads_rejected(tmp_path):
    with pytest.raises(ConnectedPlatformError):
        manager(tmp_path).certify_general_availability({"id": "x", "evidence": {}, "accessToken": "secret"}, "release")


def test_timeline_tamper_detection(tmp_path):
    platform = manager(tmp_path)
    platform.register_contract({"id": "c", "name": "Contract", "versions": ["v1"]}, "release")
    assert platform.verify_timeline()["valid"] is True
    with platform._connect() as db:
        db.execute("UPDATE stable_platform_events SET event_hash='bad' WHERE seq=1")
    assert platform.verify_timeline()["valid"] is False


def test_contracts_parse():
    root = Path(__file__).parents[2]
    for name in (
        "stable-contract-v1000.schema.json",
        "support-lifecycle-v1000.schema.json",
        "upgrade-certification-v1000.schema.json",
        "production-readiness-attestation-v1000.schema.json",
        "incident-readiness-v1000.schema.json",
        "general-availability-certification-v1000.schema.json",
    ):
        assert json.loads((root / "contracts" / name).read_text())["$schema"].startswith("https://json-schema.org")


def test_fastapi_routes(monkeypatch, tmp_path):
    monkeypatch.setenv("SC_LAB_STABLE_PLATFORM_DB_PATH", str(tmp_path / "api.sqlite3"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "test-key")
    import importlib
    import app.config as config
    import app.main as main

    importlib.reload(config)
    importlib.reload(main)
    client = TestClient(main.app)
    headers = {"X-SC-Lab-Key": "test-key", "X-SC-Lab-Actor": "release"}
    health = client.get("/v1/connected-platform/health", headers=headers)
    assert health.status_code == 200
    assert health.json()["serviceVersion"] == "1.0.0"
    result = client.post(
        "/v1/connected-platform/upgrade-certifications",
        headers=headers,
        json={
            "id": "api",
            "baselineVersion": "0.40.2",
            "backupVerified": True,
            "rollbackVerified": True,
            "migrationPassed": True,
            "packageParityVerified": True,
        },
    )
    assert result.status_code == 200
    assert result.json()["certification"]["status"] == "certified"
