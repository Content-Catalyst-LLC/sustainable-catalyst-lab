from __future__ import annotations

from hashlib import sha256
import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fastapi.testclient import TestClient

from app.artifact_transport import ArtifactStore, ArtifactTransportError
from app.persistent_dispatch_queue import PersistentDistributedDispatcher
from app.worker_agent_runtime import externalize_receipt_result, materialize_artifact_inputs


def test_resumable_upload_hash_verification_deduplication_and_range_reads():
    with TemporaryDirectory() as td:
        store = ArtifactStore(str(Path(td) / "artifacts"), chunk_bytes=65536)
        data = (b"scientific-result," * 10000) + b"done"
        digest = sha256(data).hexdigest()
        created = store.create_upload({"kind": "result", "projectId": "p1", "filename": "result.csv", "mediaType": "text/csv", "sha256": digest, "sizeBytes": len(data)})
        midpoint = 65536
        first = store.append_chunk(created["sessionId"], 0, data[:midpoint], chunk_sha256=sha256(data[:midpoint]).hexdigest())
        assert first["nextOffset"] == midpoint
        with pytest.raises(ArtifactTransportError):
            store.append_chunk(created["sessionId"], 0, b"wrong offset")
        offset = midpoint
        while offset < len(data):
            chunk = data[offset: offset + 65536]
            store.append_chunk(created["sessionId"], offset, chunk, chunk_sha256=sha256(chunk).hexdigest())
            offset += len(chunk)
        finalized = store.finalize(created["sessionId"])
        artifact = finalized["artifact"]
        metadata, partial = store.read(artifact["id"], 25, 200)
        assert partial == data[25:225]
        assert metadata["sha256"] == digest

        duplicate = store.create_upload({"kind": "result", "projectId": "p1", "filename": "again.csv", "sha256": digest, "sizeBytes": len(data)})
        offset = 0
        while offset < len(data):
            chunk = data[offset: offset + 65536]
            store.append_chunk(duplicate["sessionId"], offset, chunk)
            offset += len(chunk)
        deduped = store.finalize(duplicate["sessionId"])
        assert deduped["deduplicated"] is True
        assert deduped["artifact"]["id"] == artifact["id"]


def test_hash_mismatch_quarantines_upload():
    with TemporaryDirectory() as td:
        store = ArtifactStore(str(Path(td) / "artifacts"))
        created = store.create_upload({"kind": "checkpoint", "filename": "state.bin", "sha256": "0" * 64, "sizeBytes": 4})
        store.append_chunk(created["sessionId"], 0, b"data")
        with pytest.raises(ArtifactTransportError) as error:
            store.finalize(created["sessionId"])
        assert error.value.status_code == 422
        assert store.sessions()["sessions"][0]["status"] == "quarantined"


def test_worker_lease_grants_artifact_access_only_while_active():
    with TemporaryDirectory() as td:
        dispatcher = PersistentDistributedDispatcher(str(Path(td) / "dispatcher.sqlite3"))
        dispatcher.register({"id": "worker-a", "name": "Worker A", "workerType": "local-python", "capabilities": {"methods": ["mechanics.kinetic_energy"], "packages": [], "memoryMb": 512, "maxConcurrentJobs": 1}, "tags": []})
        dispatcher.enqueue({"method": "mechanics.kinetic_energy", "projectId": "p1", "artifactInputs": [{"artifactId": "artifact-input-1", "inputKey": "mass", "format": "json"}], "request": {"inputs": {"velocity": 3}}})
        claim = dispatcher.claim({"workerId": "worker-a"}, "secret")
        assert claim["claimed"] and dispatcher.artifact_access_allowed("worker-a", "artifact-input-1")
        dispatcher.release(claim["contract"]["leaseId"], {"workerId": "worker-a", "requeue": True})
        assert dispatcher.artifact_access_allowed("worker-a", "artifact-input-1") is False


def test_materialize_inputs_and_externalize_large_result():
    payload = json.dumps({"mass": 2}).encode()
    digest = sha256(payload).hexdigest()
    contract = {"workload": {"artifactInputs": [{"artifactId": "a1", "inputKey": "massRecord", "format": "json", "sha256": digest}]}}
    values, records = materialize_artifact_inputs(contract, lambda artifact_id: (payload, {"id": artifact_id, "sha256": digest, "sizeBytes": len(payload)}))
    assert values["massRecord"] == {"mass": 2}
    assert records[0]["sha256"] == digest

    uploaded = []
    def uploader(data, descriptor):
        uploaded.append((data, descriptor))
        return {"id": "artifact-result-1", "sha256": sha256(data).hexdigest(), "sizeBytes": len(data), "mediaType": "application/json"}
    receipt = {"id": "r1", "contractId": "c1", "queueId": "q1", "method": "m", "resultHash": "h", "result": {"values": list(range(2000))}, "receiptHash": "old"}
    result = externalize_receipt_result(receipt, uploader, 1024)
    assert result["result"]["externalized"] is True
    assert result["resultArtifact"]["id"] == "artifact-result-1"
    assert uploaded


def test_fastapi_admin_and_worker_artifact_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_ENVIRONMENT", "development")
    monkeypatch.setenv("SC_LAB_WORKER_ENROLLMENT_TOKEN", "enroll-secret")
    monkeypatch.setenv("SC_LAB_DISPATCHER_CONTRACT_SECRET", "contract-secret")
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "admin-key")
    monkeypatch.setenv("SC_LAB_MAX_REQUEST_BYTES", "2097152")
    import app.config
    import app.main
    importlib.reload(app.config)
    module = importlib.reload(app.main)
    client = TestClient(module.app)
    admin = {"X-SC-Lab-Key": "admin-key"}
    data = b'{"mass":2}'
    digest = sha256(data).hexdigest()
    created = client.post("/v1/artifacts/uploads", json={"kind": "input", "projectId": "p1", "filename": "mass.json", "mediaType": "application/json", "sha256": digest, "sizeBytes": len(data)}, headers=admin)
    assert created.status_code == 200
    session = created.json()["sessionId"]
    chunk = client.post(f"/v1/artifacts/uploads/{session}/chunks?offset=0", content=data, headers={**admin, "Content-Type": "application/octet-stream", "X-SC-Lab-Chunk-SHA256": digest})
    assert chunk.status_code == 200
    finalized = client.post(f"/v1/artifacts/uploads/{session}/finalize", json={}, headers=admin)
    artifact_id = finalized.json()["artifact"]["id"]
    assert client.get(f"/v1/artifacts/{artifact_id}/content", headers=admin).content == data
    assert client.get("/v1/artifacts/health", headers=admin).json()["version"] == "0.31.3"

    worker = {"id": "agent-a", "name": "Agent A", "workerType": "local-python", "capabilities": {"methods": ["mechanics.kinetic_energy"], "packages": [], "memoryMb": 512, "maxConcurrentJobs": 1}, "tags": []}
    enrolled = client.post("/v1/worker-agent/enroll", json=worker, headers={"X-SC-Lab-Worker-Enrollment": "enroll-secret"}).json()
    scoped = {"X-SC-Lab-Worker-Credential": enrolled["credential"]}
    client.post("/v1/dispatcher/queue/enqueue", json={"method": "mechanics.kinetic_energy", "projectId": "p1", "artifactInputs": [{"artifactId": artifact_id, "inputKey": "mass", "format": "json", "sha256": digest}], "request": {"inputs": {"velocity": 3}}}, headers=admin)
    claim = client.post("/v1/worker-agent/agent-a/claim", json={"leaseSeconds": 120}, headers=scoped)
    assert claim.status_code == 200 and claim.json()["claimed"]
    download = client.get(f"/v1/worker-agent/agent-a/artifacts/{artifact_id}/content", headers=scoped)
    assert download.status_code == 200 and download.content == data
