from __future__ import annotations

import hmac
import json
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.institutional_node_federation import InstitutionalNodeError, InstitutionalNodeFederation, policies
from app.registry import resolve
from app.team_workspaces import TeamWorkspaceManager


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return sha256(stable(value).encode()).hexdigest()


def setup_manager(tmp_path: Path):
    workspaces = TeamWorkspaceManager(str(tmp_path / "workspace.sqlite3"), 100, 1000, 10000)
    workspaces.create({"id": "health-team", "title": "Health Team"}, "alice", "Alice")
    for actor, role in (("bob", "reviewer"), ("carol", "contributor"), ("dana", "editor")):
        invite = workspaces.invite("health-team", {"inviteeActorId": actor, "role": role}, "alice")
        workspaces.accept_invitation({"token": invite["invitation"]["token"]}, actor, actor.title())
    manager = InstitutionalNodeFederation(str(tmp_path / "nodes.sqlite3"), workspaces, resolve, "coordinator-secret", 20, 100, 1000, 10000)
    node = manager.register_node("health-team", {
        "id": "hospital-node", "title": "Hospital Node", "institution": "Example Hospital",
        "endpointUrl": "https://hospital.example/node", "allowedMethods": ["statistics.descriptive"],
        "classifications": ["public", "internal", "confidential", "restricted"],
    }, "alice")["node"]
    asset = manager.register_data_asset("health-team", "hospital-node", {
        "id": "local-cohort", "title": "Local Cohort", "classification": "restricted",
        "exportPolicy": "aggregate-only", "schemaHash": "a" * 64, "contentHash": "b" * 64,
        "rowCount": 2500, "metadata": {"fields": ["age", "outcome"]},
    }, "dana")["dataAsset"]
    return workspaces, manager, node, asset


def test_policy_contract():
    body = policies(10, 20, 30)
    assert body["version"] == "0.36.1"
    assert body["capabilities"]["localDataExecution"] is True
    assert body["capabilities"]["rawRestrictedDataExport"] is False
    assert body["limits"]["requests"] == 30


def test_node_registration_returns_secret_once(tmp_path: Path):
    _, manager, node, _ = setup_manager(tmp_path)
    assert node["nodeSecret"]
    listed = manager.list_nodes("health-team", "bob")["nodes"][0]
    assert "nodeSecret" not in listed
    assert len(listed["nodeHash"]) == 64


def test_local_data_registration_and_role_boundaries(tmp_path: Path):
    _, manager, _, asset = setup_manager(tmp_path)
    assert asset["classification"] == "restricted"
    assert len(asset["assetHash"]) == 64
    with pytest.raises(InstitutionalNodeError) as exc:
        manager.register_data_asset("health-team", "hospital-node", {"id": "viewer-data", "schemaHash": "c" * 64}, "bob")
    assert exc.value.status_code == 403


def test_restricted_data_blocks_artifact_export(tmp_path: Path):
    _, manager, _, _ = setup_manager(tmp_path)
    with pytest.raises(InstitutionalNodeError) as exc:
        manager.create_execution("health-team", {"nodeId": "hospital-node", "methodId": "statistics.descriptive", "dataAssetIds": ["local-cohort"], "outputPolicy": "artifact-allowed"}, "carol")
    assert exc.value.status_code == 422


def test_unregistered_and_disallowed_methods_are_rejected(tmp_path: Path):
    _, manager, _, _ = setup_manager(tmp_path)
    with pytest.raises(InstitutionalNodeError):
        manager.create_execution("health-team", {"nodeId": "hospital-node", "methodId": "unknown.method", "dataAssetIds": ["local-cohort"]}, "carol")
    with pytest.raises(InstitutionalNodeError) as exc:
        manager.create_execution("health-team", {"nodeId": "hospital-node", "methodId": "mechanics.kinetic_energy", "dataAssetIds": ["local-cohort"]}, "carol")
    assert exc.value.status_code == 403


def test_signed_envelope_claim_and_attested_completion(tmp_path: Path):
    _, manager, node, _ = setup_manager(tmp_path)
    request = manager.create_execution("health-team", {"id": "analysis-1", "nodeId": "hospital-node", "methodId": "statistics.descriptive", "dataAssetIds": ["local-cohort"], "parameters": {"column": "outcome"}, "outputPolicy": "aggregate-only"}, "carol")["request"]
    verified = manager.verify_envelope({"envelope": request["envelope"], "envelopeHash": request["envelopeHash"], "coordinatorSignature": request["coordinatorSignature"]})
    assert verified["ok"] is True
    claimed = manager.claim_execution("hospital-node", node["nodeSecret"])["request"]
    assert claimed["status"] == "claimed"
    attestation = {"requestId": "analysis-1", "nodeId": "hospital-node", "status": "completed", "resultHash": "c" * 64, "dataAccessDigest": "d" * 64, "environmentHash": "e" * 64, "artifactRefs": [], "resultSummary": {"count": 2500, "mean": 0.42}}
    signature = hmac.new(node["nodeSecret"].encode(), digest(attestation).encode(), sha256).hexdigest()
    completed = manager.complete_execution("hospital-node", "analysis-1", {**attestation, "attestationSignature": signature}, node["nodeSecret"])
    assert completed["receipt"]["status"] == "completed"
    assert len(completed["receipt"]["receiptHash"]) == 64
    again = manager.complete_execution("hospital-node", "analysis-1", {**attestation, "attestationSignature": signature}, node["nodeSecret"])
    assert again["idempotent"] is True


def test_bad_node_secret_and_attestation_are_rejected(tmp_path: Path):
    _, manager, node, _ = setup_manager(tmp_path)
    manager.create_execution("health-team", {"id": "analysis-2", "nodeId": "hospital-node", "methodId": "statistics.descriptive", "dataAssetIds": ["local-cohort"]}, "carol")
    with pytest.raises(InstitutionalNodeError) as exc:
        manager.claim_execution("hospital-node", "wrong")
    assert exc.value.status_code == 401
    manager.claim_execution("hospital-node", node["nodeSecret"])
    with pytest.raises(InstitutionalNodeError) as exc:
        manager.complete_execution("hospital-node", "analysis-2", {"status": "completed", "resultSummary": {}, "resultHash": "c" * 64, "dataAccessDigest": "d" * 64, "environmentHash": "e" * 64, "attestationSignature": "0" * 64}, node["nodeSecret"])
    assert exc.value.status_code == 401


def test_cancellation_status_and_timeline(tmp_path: Path):
    _, manager, _, _ = setup_manager(tmp_path)
    manager.create_execution("health-team", {"id": "analysis-3", "nodeId": "hospital-node", "methodId": "statistics.descriptive", "dataAssetIds": ["local-cohort"]}, "carol")
    cancelled = manager.cancel_execution("health-team", "analysis-3", "dana", "Protocol changed")["request"]
    assert cancelled["status"] == "cancelled"
    events = manager.timeline("health-team", "bob")["events"]
    assert any(e["eventType"] == "local-execution-cancelled" for e in events)
    assert all(len(e["eventHash"]) == 64 for e in events)


def test_health_counts_and_database_integrity(tmp_path: Path):
    _, manager, _, _ = setup_manager(tmp_path)
    health = manager.health()
    assert health["database"]["schemaVersion"] == 1
    assert health["database"]["integrity"] == "ok"
    assert health["counts"]["nodes"] == 1
    assert health["counts"]["dataAssets"] == 1


def test_fastapi_node_routes_use_workspace_actor(tmp_path: Path, monkeypatch):
    from app import main
    workspaces, manager, node, _ = setup_manager(tmp_path)
    monkeypatch.setattr(main, "team_workspaces", workspaces)
    monkeypatch.setattr(main, "institutional_nodes", manager)
    headers = {"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}
    with TestClient(main.app) as client:
        health = client.get("/v1/institutional-nodes/health", headers=headers)
        assert health.status_code == 200
        assert health.json()["serviceVersion"] == "0.40.1"
        nodes = client.get("/v1/team-workspaces/health-team/institutional-nodes", headers=headers)
        assert nodes.status_code == 200 and len(nodes.json()["nodes"]) == 1
        created = client.post("/v1/team-workspaces/health-team/local-executions", headers=headers, json={"id": "api-run", "nodeId": "hospital-node", "methodId": "statistics.descriptive", "dataAssetIds": ["local-cohort"]})
        assert created.status_code == 200, created.text
        claimed = client.post("/v1/institutional-nodes/hospital-node/executions/claim", headers={**headers, "X-SC-Lab-Node-Secret": node["nodeSecret"]})
        assert claimed.status_code == 200 and claimed.json()["request"]["id"] == "api-run"
