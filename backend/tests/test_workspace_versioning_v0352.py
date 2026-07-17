from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.team_workspaces import TeamWorkspaceManager
from app.workspace_reviews import WorkspaceReviewManager
from app.workspace_versioning import WorkspaceVersionError, WorkspaceVersionManager, policies


def managers(tmp_path: Path):
    db = tmp_path / "workspace-versioning.sqlite3"
    workspaces = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    reviews = WorkspaceReviewManager(str(db), 1000)
    versions = WorkspaceVersionManager(str(db), 1000)
    workspaces.create({"id": "climate-team", "title": "Climate Team"}, "alice", "Alice")
    for actor, role in (("bob", "reviewer"), ("carol", "editor"), ("dana", "contributor"), ("erin", "viewer")):
        invite = workspaces.invite("climate-team", {"inviteeActorId": actor, "role": role}, "alice")
        workspaces.accept_invitation({"token": invite["invitation"]["token"]}, actor, actor.title())
    resource = workspaces.link_resource("climate-team", {"resourceType": "report", "resourceId": "climate-report", "title": "Climate report", "minimumRole": "reviewer"}, "alice")["resource"]
    versions.bootstrap("climate-team", "alice")
    first = versions.create_snapshot("climate-team", "main", {"id": "snapshot-base", "expectedHeadSnapshotId": None, "message": "Initial governed research state", "tree": {"reports/climate.json": {"version": 1, "status": "draft"}, "datasets/source.json": {"id": "dataset-1"}}}, "alice")["snapshot"]
    return workspaces, reviews, versions, resource, first


def unprotect_main(versions: WorkspaceVersionManager) -> None:
    main = versions.list_branches("climate-team", "alice")["branches"][0]
    versions.set_branch("climate-team", "main", {"expectedRevision": main["revision"], "protected": False}, "alice")


def test_policies_exclude_history_rewrite_and_code_execution():
    body = policies()
    assert body["capabilities"]["immutableSnapshots"] is True
    assert body["capabilities"]["threeWayMerge"] is True
    assert body["capabilities"]["historyRewrite"] is False
    assert body["capabilities"]["arbitraryCode"] is False


def test_snapshot_history_and_stale_head_conflict(tmp_path: Path):
    _, _, versions, _, first = managers(tmp_path)
    branch = versions.create_branch("climate-team", {"id": "branch-methods", "name": "methods", "sourceBranch": "main"}, "carol")["branch"]
    second = versions.create_snapshot("climate-team", branch["id"], {"expectedHeadSnapshotId": first["id"], "message": "Document uncertainty method", "changes": [{"operation": "set", "path": "methods/uncertainty.json", "value": {"method": "bootstrap", "replicates": 1000}}]}, "dana")["snapshot"]
    assert second["parentSnapshotId"] == first["id"]
    assert len(second["treeHash"]) == 64
    with pytest.raises(WorkspaceVersionError) as exc:
        versions.create_snapshot("climate-team", branch["id"], {"expectedHeadSnapshotId": first["id"], "message": "Stale edit", "tree": {"x": 1}}, "dana")
    assert exc.value.status_code == 409
    assert versions.get_snapshot("climate-team", first["id"], "erin")["snapshot"]["tree"]["reports/climate.json"]["version"] == 1


def test_compare_and_restore_create_new_history(tmp_path: Path):
    _, _, versions, _, first = managers(tmp_path)
    main = versions.list_branches("climate-team", "alice")["branches"][0]
    changed = versions.create_snapshot("climate-team", "main", {"expectedHeadSnapshotId": first["id"], "message": "Publish draft two", "changes": [{"operation": "set", "path": "reports/climate.json", "value": {"version": 2, "status": "review"}}, {"operation": "set", "path": "evidence/table.json", "value": {"rows": 24}}]}, "dana")["snapshot"]
    comparison = versions.compare("climate-team", first["id"], changed["id"], "erin")["comparison"]
    assert comparison["differenceCount"] == 2
    assert comparison["added"][0]["path"] == "evidence/table.json"
    restored = versions.restore_snapshot("climate-team", "main", first["id"], {"expectedHeadSnapshotId": changed["id"], "message": "Restore the approved baseline"}, "alice")["snapshot"]
    assert restored["id"] != first["id"]
    assert restored["parentSnapshotId"] == changed["id"]
    assert restored["metadata"]["restoredFromSnapshotId"] == first["id"]


def test_clean_three_way_merge(tmp_path: Path):
    _, _, versions, _, first = managers(tmp_path)
    unprotect_main(versions)
    branch = versions.create_branch("climate-team", {"id": "branch-evidence", "name": "evidence", "sourceBranch": "main"}, "carol")["branch"]
    source = versions.create_snapshot("climate-team", branch["id"], {"expectedHeadSnapshotId": first["id"], "message": "Add evidence", "changes": [{"operation": "set", "path": "evidence/claim-1.json", "value": {"claim": "warming", "confidence": 0.95}}]}, "dana")["snapshot"]
    merge = versions.create_merge_request("climate-team", {"id": "merge-evidence", "sourceBranch": branch["id"], "targetBranch": "main"}, "dana")["mergeRequest"]
    assert merge["status"] == "ready"
    result = versions.finalize_merge("climate-team", merge["id"], {"expectedRevision": merge["revision"], "message": "Merge reviewed evidence"}, "carol")
    assert result["mergeRequest"]["status"] == "merged"
    assert result["snapshot"]["mergeParentSnapshotId"] == source["id"]
    assert result["snapshot"]["tree"]["evidence/claim-1.json"]["confidence"] == 0.95


def test_conflict_resolution_is_path_level_and_revision_safe(tmp_path: Path):
    _, _, versions, _, first = managers(tmp_path)
    unprotect_main(versions)
    branch = versions.create_branch("climate-team", {"name": "alternative-model", "sourceBranch": "main"}, "carol")["branch"]
    source = versions.create_snapshot("climate-team", branch["id"], {"expectedHeadSnapshotId": first["id"], "message": "Alternative model", "changes": [{"operation": "set", "path": "reports/climate.json", "value": {"version": 2, "model": "B"}}]}, "dana")["snapshot"]
    target = versions.create_snapshot("climate-team", "main", {"expectedHeadSnapshotId": first["id"], "message": "Primary model", "changes": [{"operation": "set", "path": "reports/climate.json", "value": {"version": 2, "model": "A"}}]}, "alice")["snapshot"]
    merge = versions.create_merge_request("climate-team", {"sourceBranch": branch["id"], "targetBranch": "main"}, "dana")["mergeRequest"]
    assert merge["status"] == "conflicted"
    conflict = merge["conflicts"][0]
    resolved = versions.resolve_conflict("climate-team", merge["id"], conflict["id"], {"expectedRevision": merge["revision"], "resolution": "custom", "value": {"version": 2, "model": "A+B", "rationale": "reviewed ensemble"}}, "bob")["mergeRequest"]
    assert resolved["status"] == "ready"
    with pytest.raises(WorkspaceVersionError) as exc:
        versions.finalize_merge("climate-team", merge["id"], {"expectedRevision": merge["revision"]}, "carol")
    assert exc.value.status_code == 409
    finalized = versions.finalize_merge("climate-team", merge["id"], {"expectedRevision": resolved["revision"]}, "carol")["snapshot"]
    assert finalized["tree"]["reports/climate.json"]["model"] == "A+B"
    assert finalized["parentSnapshotId"] == target["id"]
    assert finalized["mergeParentSnapshotId"] == source["id"]


def test_protected_branch_requires_signed_scientific_approval(tmp_path: Path):
    _, reviews, versions, resource, first = managers(tmp_path)
    branch = versions.create_branch("climate-team", {"name": "publication", "sourceBranch": "main"}, "carol")["branch"]
    versions.create_snapshot("climate-team", branch["id"], {"expectedHeadSnapshotId": first["id"], "message": "Publication candidate", "changes": [{"operation": "set", "path": "reports/climate.json", "value": {"version": 2, "status": "publication-candidate"}}]}, "dana")
    merge = versions.create_merge_request("climate-team", {"sourceBranch": branch["id"], "targetBranch": "main"}, "dana")["mergeRequest"]
    with pytest.raises(WorkspaceVersionError) as exc:
        versions.finalize_merge("climate-team", merge["id"], {"expectedRevision": merge["revision"]}, "carol")
    assert "signed scientific approval" in exc.value.detail
    reviews.create_assignment("climate-team", {"resourceLinkId": resource["id"], "reviewerId": "bob"}, "carol")
    approval = reviews.create_approval("climate-team", {"id": "approval-version", "resourceLinkId": resource["id"], "requiredApprovals": 1, "requireNoOpenThreads": False, "requireAssignmentsComplete": False}, "carol")["approval"]
    approved = reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "approve", "rationale": "The candidate snapshot is scientifically sound."}, "bob")["approval"]
    signed = reviews.signoff("climate-team", approval["id"], {"expectedRevision": approved["revision"], "statement": "Approved for the protected main branch."}, "alice")["approval"]
    assert signed["status"] == "signed"
    attached = versions.attach_approval("climate-team", merge["id"], {"expectedRevision": merge["revision"], "approvalRequestId": approval["id"]}, "carol")["mergeRequest"]
    result = versions.finalize_merge("climate-team", merge["id"], {"expectedRevision": attached["revision"]}, "alice")
    assert result["mergeRequest"]["approvalRequestId"] == approval["id"]
    assert result["mergeRequest"]["status"] == "merged"


def test_role_boundaries_and_branch_protection(tmp_path: Path):
    _, _, versions, _, first = managers(tmp_path)
    with pytest.raises(WorkspaceVersionError) as exc:
        versions.create_branch("climate-team", {"name": "viewer-branch", "sourceBranch": "main"}, "erin")
    assert exc.value.status_code == 403
    with pytest.raises(WorkspaceVersionError) as exc:
        versions.create_branch("climate-team", {"name": "protected-review", "sourceBranch": "main", "protected": True}, "carol")
    assert exc.value.status_code == 403
    protected = versions.create_branch("climate-team", {"name": "protected-review", "sourceBranch": "main", "protected": True}, "alice")["branch"]
    assert protected["protected"] is True
    assert protected["headSnapshotId"] == first["id"]


def test_schema_migration_health_and_hashed_timeline(tmp_path: Path):
    db = tmp_path / "migration.sqlite3"
    workspaces = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    workspaces.create({"id": "migrate", "title": "Migration"}, "alice", "Alice")
    reviews = WorkspaceReviewManager(str(db), 1000)
    assert reviews.health()["database"]["schemaVersion"] == 2
    versions = WorkspaceVersionManager(str(db), 1000)
    versions.bootstrap("migrate", "alice")
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0] == "3"
    health = versions.health()
    assert health["database"]["schemaVersion"] == 3
    events = versions.timeline("migrate", "alice")["events"]
    assert all(len(event["eventHash"]) == 64 for event in events)


def test_fastapi_version_routes_use_workspace_actor(tmp_path: Path, monkeypatch):
    from app import main
    db = tmp_path / "api.sqlite3"
    workspaces = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    reviews = WorkspaceReviewManager(str(db), 1000)
    versions = WorkspaceVersionManager(str(db), 1000)
    monkeypatch.setattr(main, "team_workspaces", workspaces)
    monkeypatch.setattr(main, "workspace_reviews", reviews)
    monkeypatch.setattr(main, "workspace_versions", versions)
    headers = {"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}
    with TestClient(main.app) as client:
        assert client.post("/v1/team-workspaces", headers=headers, json={"id": "api-team", "title": "API Team"}).status_code == 200
        assert client.post("/v1/team-workspaces/api-team/versions/bootstrap", headers=headers).status_code == 200
        created = client.post("/v1/team-workspaces/api-team/branches/main/snapshots", headers=headers, json={"id": "api-base", "expectedHeadSnapshotId": None, "message": "API baseline", "tree": {"report.json": {"version": 1}}})
        assert created.status_code == 200, created.text
        listing = client.get("/v1/team-workspaces/api-team/branches", headers=headers)
        assert listing.status_code == 200
        health = client.get("/v1/workspace-versions/health", headers=headers)
        assert health.status_code == 200
        assert health.json()["serviceVersion"] == "0.36.1"
