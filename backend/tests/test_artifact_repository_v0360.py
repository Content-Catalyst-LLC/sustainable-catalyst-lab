from __future__ import annotations

import copy
import json
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.artifact_repository import ArtifactRepositoryError, MANIFEST_SCHEMA, ScientificArtifactRepository, policies
from app.team_workspaces import TeamWorkspaceManager


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def manifest_hash(value):
    clone = copy.deepcopy(value)
    clone.pop("manifestHash", None)
    return sha256(stable(clone).encode()).hexdigest()


def setup_managers(tmp_path: Path):
    workspace_db = tmp_path / "workspace.sqlite3"
    repo_db = tmp_path / "repository.sqlite3"
    workspaces = TeamWorkspaceManager(str(workspace_db), 100, 1000, 10000)
    workspaces.create({"id": "climate-team", "title": "Climate Team"}, "alice", "Alice")
    for actor, role in (("bob", "reviewer"), ("carol", "contributor"), ("dana", "editor"), ("erin", "viewer")):
        invitation = workspaces.invite("climate-team", {"inviteeActorId": actor, "role": role, "expiresInHours": 24}, "alice")
        workspaces.accept_invitation({"token": invitation["invitation"]["token"]}, actor, actor.title())
    transport = {
        "artifact-local": {
            "id": "artifact-local", "sha256": "a" * 64, "sizeBytes": 12,
            "filename": "local.json", "mediaType": "application/json",
        }
    }
    repo = ScientificArtifactRepository(str(repo_db), workspaces, lambda artifact_id: {"artifact": transport[artifact_id]}, 100, 1000, 100, 10000)
    collection = repo.create_collection("climate-team", {"id": "climate-artifacts", "title": "Climate Artifacts"}, "carol")["collection"]
    return workspaces, repo, collection


def remote_manifest(node_id="node-west", digest="b" * 64, status="active", modified="2026-07-17T12:00:00Z"):
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "version": "0.36.0",
        "nodeId": node_id,
        "generatedAt": "2026-07-17T12:00:00Z",
        "cursor": "1",
        "collection": {"id": "remote-climate", "title": "Remote Climate"},
        "artifacts": [{
            "remoteId": "remote-dataset",
            "artifactVersion": "1.0.0",
            "title": "Regional climate observations",
            "artifactType": "dataset",
            "mediaType": "application/json",
            "sha256": digest,
            "sizeBytes": 200,
            "canonicalUri": "https://example.org/artifacts/climate-observations",
            "modifiedAt": modified,
            "status": status,
            "provenance": {"institution": "Example Observatory"},
            "metadata": {"license": "CC-BY-4.0"},
        }],
    }
    manifest["manifestHash"] = manifest_hash(manifest)
    return manifest


def test_policy_contract():
    body = policies(10, 20, 30)
    assert body["version"] == "0.36.0"
    assert body["capabilities"]["manifestFederation"] is True
    assert body["capabilities"]["automaticRemoteCallbacks"] is False
    assert body["limits"]["manifestRecords"] == 30


def test_collection_local_artifact_and_integrity(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    result = repo.register_artifact("climate-team", collection["id"], {
        "id": "repo-local", "transportArtifactId": "artifact-local", "title": "Local result",
        "artifactType": "result", "artifactVersion": "1.0.0", "sha256": "a" * 64,
        "sizeBytes": 12, "canonicalUri": "urn:climate:local-result",
    }, "carol")
    assert result["artifact"]["integrityState"] == "transport-verified"
    verification = repo.verify_artifact("climate-team", "repo-local", "bob")["verification"]
    assert verification["verified"] is True
    assert len(verification["verificationHash"]) == 64


def test_artifact_registration_is_idempotent(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    payload = {"title": "Dataset", "artifactType": "dataset", "artifactVersion": "2.0.0", "sha256": "c" * 64, "sizeBytes": 40, "canonicalUri": "urn:data:2"}
    first = repo.register_artifact("climate-team", collection["id"], payload, "carol")
    second = repo.register_artifact("climate-team", collection["id"], payload, "carol")
    assert first["idempotent"] is False
    assert second["idempotent"] is True
    assert second["artifact"]["id"] == first["artifact"]["id"]


def test_collection_manifest_is_stable_and_self_verifying(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    repo.register_artifact("climate-team", collection["id"], {"title": "Figure", "artifactType": "figure", "artifactVersion": "1.0.0", "sha256": "d" * 64, "sizeBytes": 80, "canonicalUri": "urn:figure:1"}, "carol")
    manifest = repo.export_manifest("climate-team", collection["id"], "bob", "node-central")["manifest"]
    assert manifest["schema"] == MANIFEST_SCHEMA
    assert manifest["nodeId"] == "node-central"
    assert manifest_hash(manifest) == manifest["manifestHash"]


def test_strict_federation_rejects_bad_manifest_hash(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    repo.register_source("climate-team", {"id": "west", "title": "West Node", "nodeId": "node-west", "trustMode": "strict"}, "alice")
    manifest = remote_manifest()
    manifest["manifestHash"] = "0" * 64
    with pytest.raises(ArtifactRepositoryError) as exc:
        repo.sync_manifest("climate-team", "west", collection["id"], manifest, "carol")
    assert exc.value.status_code == 422


def test_federated_sync_is_idempotent_and_supports_tombstones(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    repo.register_source("climate-team", {"id": "west", "title": "West Node", "nodeId": "node-west", "trustMode": "strict"}, "alice")
    first = repo.sync_manifest("climate-team", "west", collection["id"], remote_manifest(), "carol")["sync"]
    second = repo.sync_manifest("climate-team", "west", collection["id"], remote_manifest(), "carol")["sync"]
    tombstone = remote_manifest(status="tombstoned")
    third = repo.sync_manifest("climate-team", "west", collection["id"], tombstone, "carol")["sync"]
    assert first["imported"] == 1
    assert second["unchanged"] == 1
    assert third["tombstoned"] == 1
    records = repo.get_collection("climate-team", collection["id"], "bob")["artifacts"]
    assert records[0]["status"] == "tombstoned"


def test_conflict_record_and_governed_resolution(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    repo.register_source("climate-team", {"id": "west", "title": "West Node", "nodeId": "node-west", "trustMode": "strict", "conflictPolicy": "reject"}, "alice")
    repo.sync_manifest("climate-team", "west", collection["id"], remote_manifest(), "carol")
    changed = remote_manifest(digest="e" * 64, modified="2026-07-18T12:00:00Z")
    sync = repo.sync_manifest("climate-team", "west", collection["id"], changed, "carol")["sync"]
    assert sync["conflicts"] == 1
    conflict = repo.list_conflicts("climate-team", "bob")["conflicts"][0]
    resolved = repo.resolve_conflict("climate-team", conflict["id"], {"resolution": "retain-both"}, "dana")
    assert resolved["status"] == "resolved"
    assert repo.list_conflicts("climate-team", "bob")["conflicts"] == []


def test_role_boundaries_and_archive(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    with pytest.raises(ArtifactRepositoryError) as exc:
        repo.create_collection("climate-team", {"title": "Viewer collection"}, "erin")
    assert exc.value.status_code == 403
    archived = repo.archive_collection("climate-team", collection["id"], {"reason": "superseded project"}, "dana")["collection"]
    assert archived["status"] == "archived"
    with pytest.raises(ArtifactRepositoryError) as exc:
        repo.register_artifact("climate-team", collection["id"], {"artifactType": "dataset", "sha256": "f" * 64, "sizeBytes": 1}, "carol")
    assert exc.value.status_code == 409


def test_health_sync_history_and_hashed_timeline(tmp_path: Path):
    _, repo, collection = setup_managers(tmp_path)
    repo.register_source("climate-team", {"id": "west", "title": "West Node", "nodeId": "node-west"}, "alice")
    repo.sync_manifest("climate-team", "west", collection["id"], remote_manifest(), "carol")
    health = repo.health()
    assert health["database"]["schemaVersion"] == 1
    assert health["counts"]["syncRuns"] == 1
    history = repo.sync_history("climate-team", "bob", "west")["syncRuns"]
    assert len(history) == 1 and len(history[0]["runHash"]) == 64
    events = repo.timeline("climate-team", "bob")["events"]
    assert events and all(len(event["eventHash"]) == 64 for event in events)


def test_fastapi_repository_routes_use_workspace_actor(tmp_path: Path, monkeypatch):
    from app import main
    workspaces, repo, _ = setup_managers(tmp_path)
    monkeypatch.setattr(main, "team_workspaces", workspaces)
    monkeypatch.setattr(main, "artifact_repository", repo)
    headers = {"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}
    with TestClient(main.app) as client:
        health = client.get("/v1/artifact-repository/health", headers=headers)
        assert health.status_code == 200
        assert health.json()["serviceVersion"] == "0.38.1"
        created = client.post("/v1/team-workspaces/climate-team/artifact-collections", headers=headers, json={"id": "api-artifacts", "title": "API Artifacts"})
        assert created.status_code == 200, created.text
        registered = client.post("/v1/team-workspaces/climate-team/artifact-collections/api-artifacts/artifacts", headers=headers, json={"id": "api-record", "title": "API Dataset", "artifactType": "dataset", "artifactVersion": "1.0.0", "sha256": "9" * 64, "sizeBytes": 5, "canonicalUri": "urn:api:dataset"})
        assert registered.status_code == 200, registered.text
        listing = client.get("/v1/team-workspaces/climate-team/artifact-collections/api-artifacts", headers=headers)
        assert listing.status_code == 200
        assert len(listing.json()["artifacts"]) == 1
