from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.team_workspaces import TeamWorkspaceManager
from app.workspace_reviews import WorkspaceReviewError, WorkspaceReviewManager, policies


def managers(tmp_path: Path):
    db = tmp_path / "workspace-review.sqlite3"
    workspaces = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    reviews = WorkspaceReviewManager(str(db), 1000)
    workspaces.create({"id": "climate-team", "title": "Climate Team"}, "alice", "Alice")
    for actor, role in (("bob", "reviewer"), ("carol", "editor"), ("dana", "contributor"), ("erin", "viewer")):
        invite = workspaces.invite("climate-team", {"inviteeActorId": actor, "role": role}, "alice")
        workspaces.accept_invitation({"token": invite["invitation"]["token"]}, actor, actor.title())
    resource = workspaces.link_resource("climate-team", {"resourceType": "report", "resourceId": "climate-report", "title": "Climate report", "minimumRole": "reviewer"}, "alice")["resource"]
    return workspaces, reviews, resource


def test_append_only_nested_comments_and_withdrawal(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    thread = reviews.create_thread("climate-team", {"id": "methods-review", "title": "Methods review", "resourceLinkId": resource["id"]}, "dana")["thread"]
    first = reviews.add_comment("climate-team", thread["id"], {"id": "comment-1", "body": "Please document the uncertainty assumptions."}, "bob")["comment"]
    reply = reviews.add_comment("climate-team", thread["id"], {"id": "comment-2", "parentCommentId": first["id"], "body": "The assumptions are now in section 4."}, "dana")["comment"]
    assert reply["parentCommentId"] == "comment-1"
    withdrawn = reviews.withdraw_comment("climate-team", "comment-2", {"reason": "Superseded by a corrected explanation."}, "dana")["comment"]
    assert withdrawn["status"] == "withdrawn"
    assert len(withdrawn["commentHash"]) == 64


def test_role_rules_for_comments_and_review_management(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    thread = reviews.create_thread("climate-team", {"title": "Results review", "resourceLinkId": resource["id"]}, "bob")["thread"]
    with pytest.raises(WorkspaceReviewError) as exc:
        reviews.add_comment("climate-team", thread["id"], {"body": "Viewer comment"}, "erin")
    assert exc.value.status_code == 403
    with pytest.raises(WorkspaceReviewError):
        reviews.set_thread_status("climate-team", thread["id"], {"expectedRevision": thread["revision"], "resolution": "Done"}, "bob", "resolved")
    resolved = reviews.set_thread_status("climate-team", thread["id"], {"expectedRevision": thread["revision"], "resolution": "Methods corrected."}, "carol", "resolved")["thread"]
    assert resolved["status"] == "resolved"


def test_review_assignment_and_conflict_safe_revision(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    assignment = reviews.create_assignment("climate-team", {"id": "assignment-1", "resourceLinkId": resource["id"], "reviewerId": "bob", "instructions": "Review methods and evidence."}, "carol")["assignment"]
    started = reviews.update_assignment("climate-team", assignment["id"], {"expectedRevision": 1, "status": "in-review"}, "bob")["assignment"]
    assert started["revision"] == 2
    with pytest.raises(WorkspaceReviewError) as exc:
        reviews.update_assignment("climate-team", assignment["id"], {"expectedRevision": 1, "status": "approved"}, "bob")
    assert exc.value.status_code == 409


def test_approval_gates_open_threads_and_assignments(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    thread = reviews.create_thread("climate-team", {"title": "Open question", "resourceLinkId": resource["id"]}, "bob")["thread"]
    reviews.create_assignment("climate-team", {"resourceLinkId": resource["id"], "reviewerId": "bob"}, "carol")
    approval = reviews.create_approval("climate-team", {"id": "approval-1", "resourceLinkId": resource["id"], "requiredApprovals": 1}, "carol")["approval"]
    decided = reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "approve", "rationale": "Method and evidence are sufficient."}, "bob")["approval"]
    assert decided["status"] == "pending"
    assert decided["summary"]["openThreadCount"] == 1
    reviews.set_thread_status("climate-team", thread["id"], {"expectedRevision": thread["revision"], "resolution": "Question answered."}, "carol", "resolved")
    evaluated = reviews.evaluate_approval("climate-team", approval["id"], "alice")
    assert evaluated["status"] == "approved"
    assert evaluated["gates"]["readyForApproval"] is True


def test_decisions_are_immutable_and_require_assignment(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    approval = reviews.create_approval("climate-team", {"resourceLinkId": resource["id"], "requiredApprovals": 1, "requireNoOpenThreads": False, "requireAssignmentsComplete": False}, "carol")["approval"]
    with pytest.raises(WorkspaceReviewError) as exc:
        reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "approve", "rationale": "Looks good."}, "bob")
    assert exc.value.status_code == 403
    reviews.create_assignment("climate-team", {"resourceLinkId": resource["id"], "reviewerId": "bob"}, "carol")
    reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "approve", "rationale": "Looks good."}, "bob")
    with pytest.raises(WorkspaceReviewError) as exc:
        reviews.decide("climate-team", approval["id"], {"expectedRevision": 2, "decision": "reject", "rationale": "Changed mind."}, "bob")
    assert exc.value.status_code == 409


def test_rejection_and_changes_requested_states(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    reviews.create_assignment("climate-team", {"resourceLinkId": resource["id"], "reviewerId": "bob"}, "carol")
    approval = reviews.create_approval("climate-team", {"resourceLinkId": resource["id"], "requireNoOpenThreads": False, "requireAssignmentsComplete": False}, "carol")["approval"]
    result = reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "request-changes", "rationale": "Add the missing calibration evidence."}, "bob")
    assert result["approval"]["status"] == "changes-requested"
    assert result["approval"]["summary"]["changesRequestedCount"] == 1


def test_immutable_scientific_signoff_record(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    reviews.create_assignment("climate-team", {"resourceLinkId": resource["id"], "reviewerId": "bob"}, "carol")
    approval = reviews.create_approval("climate-team", {"id": "approval-sign", "resourceLinkId": resource["id"], "requiredApprovals": 1, "requireNoOpenThreads": False}, "carol")["approval"]
    approved = reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "approve", "rationale": "The report is scientifically sound.", "evidence": [{"type": "dataset", "id": "observations-2026"}]}, "bob")["approval"]
    assert approved["status"] == "approved"
    signed = reviews.signoff("climate-team", approval["id"], {"expectedRevision": approved["revision"], "statement": "I approve this report for scientific publication."}, "alice")
    assert signed["approval"]["status"] == "signed"
    assert len(signed["signoff"]["signoffHash"]) == 64
    with pytest.raises(WorkspaceReviewError):
        reviews.signoff("climate-team", approval["id"], {"expectedRevision": signed["approval"]["revision"], "statement": "Duplicate."}, "alice")


def test_signoff_requires_administrator_or_owner(tmp_path: Path):
    _, reviews, resource = managers(tmp_path)
    reviews.create_assignment("climate-team", {"resourceLinkId": resource["id"], "reviewerId": "bob"}, "carol")
    approval = reviews.create_approval("climate-team", {"resourceLinkId": resource["id"], "requiredApprovals": 1, "requireNoOpenThreads": False}, "carol")["approval"]
    approved = reviews.decide("climate-team", approval["id"], {"expectedRevision": 1, "decision": "approve", "rationale": "Approved."}, "bob")["approval"]
    with pytest.raises(WorkspaceReviewError) as exc:
        reviews.signoff("climate-team", approval["id"], {"expectedRevision": approved["revision"], "statement": "Editor sign-off."}, "carol")
    assert exc.value.status_code == 403


def test_schema_migration_health_and_policy(tmp_path: Path):
    db = tmp_path / "migration.sqlite3"
    workspaces = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    workspaces.create({"id": "migrate", "title": "Migration"}, "alice", "Alice")
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0] == "1"
    reviews = WorkspaceReviewManager(str(db), 1000)
    assert reviews.health()["database"]["schemaVersion"] == 2
    body = policies()
    assert body["capabilities"]["immutableScientificSignoff"] is True
    assert body["capabilities"]["arbitraryCode"] is False


def test_fastapi_review_routes_use_workspace_actor(tmp_path: Path, monkeypatch):
    from app import main
    db = tmp_path / "api.sqlite3"
    workspaces = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    reviews = WorkspaceReviewManager(str(db), 1000)
    monkeypatch.setattr(main, "team_workspaces", workspaces)
    monkeypatch.setattr(main, "workspace_reviews", reviews)
    with TestClient(main.app) as client:
        headers = {"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}
        assert client.post("/v1/team-workspaces", headers=headers, json={"id": "api-team", "title": "API Team"}).status_code == 200
        link = client.post("/v1/team-workspaces/api-team/resources", headers=headers, json={"resourceType": "report", "resourceId": "api-report", "minimumRole": "viewer"}).json()["resource"]
        thread = client.post("/v1/team-workspaces/api-team/review-threads", headers=headers, json={"title": "API review", "resourceLinkId": link["id"]})
        assert thread.status_code == 200
        approval = client.post("/v1/team-workspaces/api-team/approval-requests", headers=headers, json={"resourceLinkId": link["id"], "requireNoOpenThreads": False, "requireAssignmentsComplete": False})
        assert approval.status_code == 200
        health = client.get("/v1/workspace-reviews/health", headers=headers)
        assert health.status_code == 200
        assert health.json()["serviceVersion"] == "0.35.1"
