from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import importlib

import pytest
from fastapi.testclient import TestClient

from app.persistent_dispatch_queue import PersistentDistributedDispatcher
from app.worker_agent_runtime import WorkerAgentError, compute_request_from_contract, execute_contract, verify_contract
from worker_agent.client import CredentialStore
from worker_agent.config import AgentConfig


def worker(worker_id: str = "agent-a") -> dict:
    return {
        "id": worker_id,
        "name": "Secure Agent A",
        "workerType": "local-python",
        "capabilities": {
            "methods": ["mechanics.kinetic_energy"],
            "packages": ["numpy"],
            "memoryMb": 2048,
            "cpuCores": 2,
            "checkpointing": True,
            "maxConcurrentJobs": 1,
        },
        "tags": ["trusted", "local"],
    }


def workload() -> dict:
    return {
        "method": "mechanics.kinetic_energy",
        "projectId": "project-agent",
        "priority": 90,
        "requiredPackages": ["numpy"],
        "requiredTags": ["trusted"],
        "request": {"inputs": {"mass": 2.0, "velocity": 3.0}},
    }


def test_worker_enrollment_credential_rotation_and_revocation():
    with TemporaryDirectory() as td:
        dispatcher = PersistentDistributedDispatcher(str(Path(td) / "dispatcher.sqlite3"))
        enrolled = dispatcher.enroll(worker())
        assert enrolled["credentialReturnedOnce"] is True
        credential = enrolled["credential"]
        assert dispatcher.authenticate_worker("agent-a", credential)["ok"]
        rotated = dispatcher.rotate_worker_credential("agent-a")
        with pytest.raises(Exception):
            dispatcher.authenticate_worker("agent-a", credential)
        assert dispatcher.authenticate_worker("agent-a", rotated["credential"])["ok"]
        dispatcher.revoke_worker("agent-a", "operator test")
        with pytest.raises(Exception):
            dispatcher.authenticate_worker("agent-a", rotated["credential"])
        status = dispatcher.credential_status()
        assert status["total"] == 1 and status["revoked"] == 1 and status["storedAsDigests"]


def test_signed_contract_executes_registered_method_and_completion_is_idempotent():
    with TemporaryDirectory() as td:
        dispatcher = PersistentDistributedDispatcher(str(Path(td) / "dispatcher.sqlite3"))
        enrolled = dispatcher.enroll(worker())
        dispatcher.enqueue(workload())
        claimed = dispatcher.claim({"workerId": "agent-a", "leaseSeconds": 120}, "contract-secret")
        contract = claimed["contract"]
        verified = verify_contract(contract, "agent-a", "contract-secret")
        assert verified["signatureValid"] is True
        dispatcher.acknowledge(contract["id"], "agent-a")
        receipt = execute_contract(contract, "agent-a", "contract-secret", {"mode": "worker-agent", "client": "agent-a"})
        assert receipt["schema"] == "sc-lab-worker-execution-receipt/0.31.3"
        assert receipt["result"]["outputs"]["kineticEnergyJ"] == 9.0
        first = dispatcher.complete(contract["id"], {"ok": True, "result": receipt, "receiptHash": receipt["receiptHash"]}, "agent-a")
        second = dispatcher.complete(contract["id"], {"ok": True, "result": receipt, "receiptHash": receipt["receiptHash"]}, "agent-a")
        assert first["idempotent"] is False and second["idempotent"] is True
        assert dispatcher.authenticate_worker("agent-a", enrolled["credential"])["ok"]


def test_contract_rejects_wrong_worker_and_unsafe_fields():
    with TemporaryDirectory() as td:
        dispatcher = PersistentDistributedDispatcher(str(Path(td) / "dispatcher.sqlite3"))
        dispatcher.register(worker())
        contract = dispatcher.build_contract(workload(), "contract-secret")["contract"]
        with pytest.raises(WorkerAgentError):
            verify_contract(contract, "other-worker", "contract-secret")
        unsafe = dict(contract)
        unsafe["workload"] = dict(contract["workload"])
        unsafe["workload"]["request"] = {"code": "print('unsafe')"}
        # Re-sign so this test reaches governed request validation.
        from app.distributed_dispatcher import _stable
        from hashlib import sha256
        import hmac
        unsigned = {key: value for key, value in unsafe.items() if key != "signature"}
        unsafe["signature"] = hmac.new(b"contract-secret", _stable(unsigned).encode(), sha256).hexdigest()
        with pytest.raises(WorkerAgentError):
            compute_request_from_contract(unsafe, "agent-a", "contract-secret")


def test_credential_store_uses_private_permissions(tmp_path: Path):
    path = tmp_path / "credential.json"
    store = CredentialStore(path)
    store.save("agent-a", "secret-value")
    assert store.load("agent-a") == "secret-value"
    assert path.stat().st_mode & 0o777 == 0o600


def test_agent_config_requires_contract_verification_secret(tmp_path: Path):
    with pytest.raises(ValueError):
        AgentConfig(
            coordinator_url="https://compute.example.com",
            worker_id="agent-a",
            name="Agent A",
            contract_secret="",
            credential_file=tmp_path / "credential.json",
        )
    config = AgentConfig(
        coordinator_url="https://compute.example.com",
        worker_id="agent-a",
        name="Agent A",
        contract_secret="contract-secret",
        credential_file=tmp_path / "credential.json",
        methods=["mechanics.kinetic_energy"],
    )
    assert config.worker_payload()["endpointMode"] == "secure-credential-pull-artifact-transport"


def test_fastapi_worker_agent_enrollment_and_scoped_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_ENVIRONMENT", "development")
    monkeypatch.setenv("SC_LAB_WORKER_ENROLLMENT_TOKEN", "enroll-secret")
    monkeypatch.setenv("SC_LAB_DISPATCHER_CONTRACT_SECRET", "contract-secret")
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "admin-key")
    monkeypatch.setenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")
    import app.config
    import app.main
    importlib.reload(app.config)
    module = importlib.reload(app.main)
    client = TestClient(module.app)
    admin = {"X-SC-Lab-Key": "admin-key"}
    bad = client.post("/v1/worker-agent/enroll", json=worker(), headers={"X-SC-Lab-Worker-Enrollment": "wrong"})
    assert bad.status_code == 401
    enrolled = client.post("/v1/worker-agent/enroll", json=worker(), headers={"X-SC-Lab-Worker-Enrollment": "enroll-secret"})
    assert enrolled.status_code == 200
    credential = enrolled.json()["credential"]
    scoped = {"X-SC-Lab-Worker-Credential": credential}
    assert client.post("/v1/worker-agent/agent-a/heartbeat", json={"state": "online"}, headers=scoped).status_code == 200
    assert client.get("/v1/worker-agent/health", headers=admin).json()["contractSecretConfigured"] is True
    assert client.post("/v1/dispatcher/queue/enqueue", json=workload(), headers=admin).status_code == 200
    claim = client.post("/v1/worker-agent/agent-a/claim", json={"leaseSeconds": 120}, headers=scoped)
    assert claim.status_code == 200 and claim.json()["claimed"] is True
    contract = claim.json()["contract"]
    assert client.post(f"/v1/worker-agent/agent-a/contracts/{contract['id']}/acknowledge", json={}, headers=scoped).status_code == 200
    receipt = execute_contract(contract, "agent-a", "contract-secret", {"mode": "worker-agent", "client": "agent-a"})
    complete = client.post(
        f"/v1/worker-agent/agent-a/contracts/{contract['id']}/complete",
        json={"ok": True, "result": receipt, "receiptHash": receipt["receiptHash"]},
        headers=scoped,
    )
    assert complete.status_code == 200 and complete.json()["contract"]["status"] == "completed"
