from __future__ import annotations

import hmac
import json
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.institutional_node_federation import InstitutionalNodeFederation
from app.offline_edge_sync import EdgeSyncError, OfflineEdgeSyncManager, policies
from app.registry import resolve
from app.team_workspaces import TeamWorkspaceManager


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return sha256(stable(value).encode()).hexdigest()


def setup_manager(tmp_path: Path):
    workspaces = TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 10000)
    workspaces.create({"id": "field-team", "title": "Field Team"}, "alice", "Alice")
    for actor, role in (("bob", "reviewer"), ("carol", "contributor"), ("dana", "editor")):
        invite = workspaces.invite("field-team", {"inviteeActorId": actor, "role": role}, "alice")
        workspaces.accept_invitation({"token": invite["invitation"]["token"]}, actor, actor.title())
    nodes = InstitutionalNodeFederation(str(tmp_path / "nodes.sqlite3"), workspaces, resolve, "coordinator-secret", 20, 100, 1000, 10000)
    nodes.register_node("field-team", {"id": "field-hub", "title": "Field Hub", "institution": "Research Institute", "allowedMethods": ["statistics.descriptive"]}, "alice")
    manager = OfflineEdgeSyncManager(str(tmp_path / "edge.sqlite3"), workspaces, nodes, 20, 100, 1000, 50, 10000)
    dev1 = manager.enroll_device("field-team", {"id": "tablet-1", "title": "Field Tablet 1", "nodeId": "field-hub", "platform": "ios", "appVersion": "1.0", "capabilities": {"camera": True, "offlineForms": True}}, "dana")["device"]
    dev2 = manager.enroll_device("field-team", {"id": "tablet-2", "title": "Field Tablet 2", "nodeId": "field-hub", "platform": "android"}, "dana")["device"]
    package = manager.create_package("field-team", {"id": "wetland-survey", "title": "Wetland Survey", "nodeId": "field-hub", "definition": {"methods": ["statistics.descriptive"], "forms": [{"id": "observation", "fields": ["species", "count"]}], "dataAssetRefs": ["local-wetland-index"], "artifactRefs": [], "constraints": {"rawRestrictedDataExport": False}, "metadata": {"study": "wetlands"}}}, "dana")["package"]
    manager.seal_package("field-team", "wetland-survey", "dana")
    manager.assign_package("field-team", "wetland-survey", "tablet-1", "dana")
    manager.assign_package("field-team", "wetland-survey", "tablet-2", "dana")
    return workspaces, nodes, manager, dev1, dev2, package


def signed_batch(secret: str, session_id: str, device_id: str, changes: list[dict]):
    signed = {"sessionId": session_id, "deviceId": device_id, "changes": changes}
    return {"changes": changes, "signature": hmac.new(secret.encode(), digest(signed).encode(), sha256).hexdigest()}


def test_policy_contract():
    body = policies(10, 20, 30, 40)
    assert body["version"] == "0.36.2"
    assert body["capabilities"]["offlineWorkPackages"] is True
    assert body["capabilities"]["restrictedDataBytesInPackage"] is False
    assert body["limits"]["batchChanges"] == 40


def test_device_secret_returned_once_and_role_boundary(tmp_path: Path):
    _, _, manager, dev1, _, _ = setup_manager(tmp_path)
    assert dev1["deviceSecret"]
    listed = manager.list_devices("field-team", "bob")["devices"]
    assert "deviceSecret" not in listed[0]
    with pytest.raises(EdgeSyncError) as exc:
        manager.enroll_device("field-team", {"id": "viewer-device"}, "bob")
    assert exc.value.status_code == 403


def test_offline_package_is_sealed_assigned_and_contains_no_data_bytes(tmp_path: Path):
    _, _, manager, dev1, _, _ = setup_manager(tmp_path)
    pulled = manager.pull_package("tablet-1", "wetland-survey", dev1["deviceSecret"])
    assert pulled["package"]["status"] == "sealed"
    assert len(pulled["package"]["packageHash"]) == 64
    assert pulled["constraints"]["containsRestrictedDataBytes"] is False


def test_nested_executable_fields_are_rejected(tmp_path: Path):
    _, _, manager, _, _, _ = setup_manager(tmp_path)
    with pytest.raises(EdgeSyncError) as exc:
        manager.create_package("field-team", {"id": "unsafe", "definition": {"forms": [{"id": "x", "callbackUrl": "https://bad.example"}]}}, "dana")
    assert exc.value.status_code == 422


def test_signed_resumable_push_dedup_and_completion(tmp_path: Path):
    _, _, manager, dev1, _, _ = setup_manager(tmp_path)
    session = manager.begin_sync("tablet-1", "wetland-survey", {"direction": "bidirectional", "baseCursor": 0}, dev1["deviceSecret"])["session"]
    changes = [{"changeId": "obs-1", "entityType": "observation", "entityId": "plot-1", "operation": "upsert", "payload": {"species": "Carex", "count": 12}, "createdAt": "2026-07-17T20:00:00Z"}]
    first = manager.push_changes("tablet-1", session["id"], signed_batch(dev1["deviceSecret"], session["id"], "tablet-1", changes), dev1["deviceSecret"], session["resumeToken"])
    assert first["summary"]["accepted"] == 1
    again = manager.push_changes("tablet-1", session["id"], signed_batch(dev1["deviceSecret"], session["id"], "tablet-1", changes), dev1["deviceSecret"], session["resumeToken"])
    assert again["summary"]["duplicates"] == 1
    completed = manager.complete_sync("tablet-1", session["id"], {"finalCursor": first["session"]["serverCursor"]}, dev1["deviceSecret"], session["resumeToken"])
    assert completed["session"]["status"] == "completed"


def test_bad_secret_signature_and_resume_token_are_rejected(tmp_path: Path):
    _, _, manager, dev1, _, _ = setup_manager(tmp_path)
    with pytest.raises(EdgeSyncError) as exc:
        manager.pull_package("tablet-1", "wetland-survey", "wrong")
    assert exc.value.status_code == 401
    session = manager.begin_sync("tablet-1", "wetland-survey", {}, dev1["deviceSecret"])["session"]
    with pytest.raises(EdgeSyncError) as exc:
        manager.push_changes("tablet-1", session["id"], {"changes": [], "signature": "0" * 64}, dev1["deviceSecret"], session["resumeToken"])
    assert exc.value.status_code == 401
    with pytest.raises(EdgeSyncError) as exc:
        manager.pull_changes("tablet-1", session["id"], 0, dev1["deviceSecret"], "wrong")
    assert exc.value.status_code == 401


def test_delta_pull_and_cursor_provenance(tmp_path: Path):
    _, _, manager, dev1, _, _ = setup_manager(tmp_path)
    session = manager.begin_sync("tablet-1", "wetland-survey", {}, dev1["deviceSecret"])["session"]
    changes = [
        {"changeId": "obs-a", "entityType": "observation", "entityId": "plot-a", "operation": "append", "payload": {"value": 1}},
        {"changeId": "obs-b", "entityType": "observation", "entityId": "plot-b", "operation": "append", "payload": {"value": 2}},
    ]
    manager.push_changes("tablet-1", session["id"], signed_batch(dev1["deviceSecret"], session["id"], "tablet-1", changes), dev1["deviceSecret"], session["resumeToken"])
    pulled = manager.pull_changes("tablet-1", session["id"], 0, dev1["deviceSecret"], session["resumeToken"], 1)
    assert len(pulled["changes"]) == 1 and pulled["hasMore"] is True
    pulled2 = manager.pull_changes("tablet-1", session["id"], pulled["cursor"], dev1["deviceSecret"], session["resumeToken"], 10)
    assert len(pulled2["changes"]) == 1 and pulled2["cursor"] > pulled["cursor"]


def test_conflicting_device_changes_create_and_resolve_conflict(tmp_path: Path):
    _, _, manager, dev1, dev2, _ = setup_manager(tmp_path)
    s1 = manager.begin_sync("tablet-1", "wetland-survey", {}, dev1["deviceSecret"])["session"]
    c1 = [{"changeId": "plot-1-a", "entityType": "observation", "entityId": "plot-1", "operation": "upsert", "payload": {"count": 12}}]
    accepted = manager.push_changes("tablet-1", s1["id"], signed_batch(dev1["deviceSecret"], s1["id"], "tablet-1", c1), dev1["deviceSecret"], s1["resumeToken"])
    assert accepted["summary"]["accepted"] == 1
    s2 = manager.begin_sync("tablet-2", "wetland-survey", {"baseCursor": 0}, dev2["deviceSecret"])["session"]
    c2 = [{"changeId": "plot-1-b", "entityType": "observation", "entityId": "plot-1", "operation": "upsert", "payload": {"count": 18}}]
    result = manager.push_changes("tablet-2", s2["id"], signed_batch(dev2["deviceSecret"], s2["id"], "tablet-2", c2), dev2["deviceSecret"], s2["resumeToken"])
    assert result["summary"]["conflicts"] == 1
    conflict = manager.list_conflicts("field-team", "bob")["conflicts"][0]
    resolved = manager.resolve_conflict("field-team", conflict["id"], {"resolution": "retain-both"}, "dana")
    assert resolved["conflict"]["status"] == "resolved"


def test_health_sessions_and_hashed_timeline(tmp_path: Path):
    _, _, manager, dev1, _, _ = setup_manager(tmp_path)
    manager.begin_sync("tablet-1", "wetland-survey", {}, dev1["deviceSecret"])
    health = manager.health()
    assert health["database"]["schemaVersion"] == 1
    assert health["database"]["integrity"] == "ok"
    assert health["counts"]["devices"] == 2
    assert len(manager.list_sessions("field-team", "bob")["sessions"]) == 1
    events = manager.timeline("field-team", "bob")["events"]
    assert events and all(len(event["eventHash"]) == 64 for event in events)


def test_fastapi_edge_routes_use_workspace_actor(tmp_path: Path, monkeypatch):
    from app import main
    workspaces, nodes, manager, dev1, _, _ = setup_manager(tmp_path)
    monkeypatch.setattr(main, "team_workspaces", workspaces)
    monkeypatch.setattr(main, "institutional_nodes", nodes)
    monkeypatch.setattr(main, "edge_sync", manager)
    headers = {"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}
    with TestClient(main.app) as client:
        health = client.get("/v1/edge-sync/health", headers=headers)
        assert health.status_code == 200
        assert health.json()["serviceVersion"] == "0.37.2"
        devices = client.get("/v1/team-workspaces/field-team/edge-devices", headers=headers)
        assert devices.status_code == 200 and len(devices.json()["devices"]) == 2
        package = client.get("/v1/edge-devices/tablet-1/offline-packages/wetland-survey", headers={**headers, "X-SC-Lab-Edge-Secret": dev1["deviceSecret"]})
        assert package.status_code == 200 and package.json()["package"]["id"] == "wetland-survey"
