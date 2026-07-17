from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.team_workspaces import TeamWorkspaceError, TeamWorkspaceManager, policies


def manager(tmp_path: Path) -> TeamWorkspaceManager:
    return TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 1000)


def create_workspace(m: TeamWorkspaceManager, actor: str = "alice") -> dict:
    return m.create({"id": "climate-research", "title": "Climate Research", "primaryProjectId": "project-climate"}, actor, actor.title())


def add_member(m: TeamWorkspaceManager, role: str, actor: str) -> None:
    invite = m.invite("climate-research", {"inviteeActorId": actor, "role": role}, "alice")
    m.accept_invitation({"token": invite["invitation"]["token"]}, actor, actor.title())


def test_workspace_creation_owner_and_listing(tmp_path: Path):
    m = manager(tmp_path)
    created = create_workspace(m)
    workspace = created["workspace"]
    assert workspace["ownerId"] == "alice"
    assert workspace["currentMembership"]["role"] == "owner"
    assert len(workspace["members"]) == 1
    assert m.list("alice")["workspaces"][0]["id"] == "climate-research"
    with pytest.raises(TeamWorkspaceError) as exc:
        m.get("climate-research", "outsider")
    assert exc.value.status_code == 403


def test_single_use_targeted_invitation(tmp_path: Path):
    m = manager(tmp_path); create_workspace(m)
    invite = m.invite("climate-research", {"inviteeActorId": "bob", "inviteeLabel": "Bob", "role": "editor"}, "alice")
    token = invite["invitation"]["token"]
    assert "token" in invite["invitation"]
    with pytest.raises(TeamWorkspaceError) as exc:
        m.accept_invitation({"token": token}, "carol")
    assert exc.value.status_code == 403
    accepted = m.accept_invitation({"token": token}, "bob", "Bob")
    assert accepted["workspace"]["currentMembership"]["role"] == "editor"
    with pytest.raises(TeamWorkspaceError) as exc:
        m.accept_invitation({"token": token}, "bob")
    assert exc.value.status_code == 409


def test_role_enforcement_and_member_governance(tmp_path: Path):
    m = manager(tmp_path); create_workspace(m); add_member(m, "contributor", "bob"); add_member(m, "administrator", "carol")
    with pytest.raises(TeamWorkspaceError) as exc:
        m.update("climate-research", {"title": "No"}, "bob")
    assert exc.value.status_code == 403
    updated = m.update("climate-research", {"title": "Climate Team Workspace"}, "carol")
    assert updated["workspace"]["title"] == "Climate Team Workspace"
    with pytest.raises(TeamWorkspaceError):
        m.set_member_role("climate-research", "bob", {"role": "administrator"}, "carol")
    changed = m.set_member_role("climate-research", "bob", {"role": "editor"}, "alice")
    assert changed["membership"]["role"] == "editor"


def test_resource_links_respect_minimum_roles(tmp_path: Path):
    m = manager(tmp_path); create_workspace(m); add_member(m, "contributor", "bob"); add_member(m, "viewer", "carol")
    link = m.link_resource("climate-research", {"resourceType": "dataset", "resourceId": "dataset-2026", "minimumRole": "contributor"}, "bob")
    assert link["resource"]["minimumRole"] == "contributor"
    bob = m.get("climate-research", "bob")["workspace"]
    carol = m.get("climate-research", "carol")["workspace"]
    assert len(bob["resources"]) == 1
    assert carol["resources"] == []
    decision = m.authorize("climate-research", {"action": "resources.read", "resourceLinkId": link["resource"]["id"]}, "carol")
    assert decision["decision"]["allowed"] is False


def test_ownership_transfer_preserves_previous_owner(tmp_path: Path):
    m = manager(tmp_path); create_workspace(m); add_member(m, "editor", "bob")
    transferred = m.transfer_ownership("climate-research", {"newOwnerId": "bob", "reason": "Principal investigator changed."}, "alice")
    members = {row["actorId"]: row["role"] for row in transferred["workspace"]["members"]}
    assert transferred["workspace"]["ownerId"] == "bob"
    assert members == {"alice": "administrator", "bob": "owner"}
    with pytest.raises(TeamWorkspaceError):
        m.transfer_ownership("climate-research", {"newOwnerId": "alice", "reason": "no"}, "alice")


def test_archive_is_read_only_and_revokes_invitations(tmp_path: Path):
    m = manager(tmp_path); create_workspace(m)
    invite = m.invite("climate-research", {"inviteeActorId": "bob", "role": "viewer"}, "alice")
    archived = m.archive("climate-research", "alice", "Research program completed.")
    assert archived["workspace"]["status"] == "archived"
    with pytest.raises(TeamWorkspaceError) as exc:
        m.accept_invitation({"token": invite["invitation"]["token"]}, "bob")
    assert exc.value.status_code == 409
    with pytest.raises(TeamWorkspaceError):
        m.link_resource("climate-research", {"resourceType": "report", "resourceId": "r1"}, "alice")
    assert m.get("climate-research", "alice")["workspace"]["status"] == "archived"


def test_timeline_and_access_decisions_are_hashed(tmp_path: Path):
    m = manager(tmp_path); create_workspace(m); add_member(m, "reviewer", "bob")
    decision = m.authorize("climate-research", {"action": "resource.review"}, "bob")["decision"]
    assert decision["allowed"] is True
    assert len(decision["decisionHash"]) == 64
    events = m.timeline("climate-research", "bob")["events"]
    assert events[-1]["eventType"] == "access-decision"
    assert all(len(event["eventHash"]) == 64 for event in events)


def test_persistence_and_health(tmp_path: Path):
    db = tmp_path / "workspace.sqlite3"
    first = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    create_workspace(first)
    second = TeamWorkspaceManager(str(db), 100, 1000, 1000)
    assert second.get("climate-research", "alice")["workspace"]["workspaceHash"]
    health = second.health()
    assert health["ok"] is True
    assert health["database"]["schemaVersion"] == 1
    assert health["counts"]["workspaces"] == 1


def test_policy_excludes_review_comments_and_code_execution():
    body = policies()
    assert body["capabilities"]["roleBasedAccess"] is True
    assert body["capabilities"]["reviewComments"] is False
    assert body["capabilities"]["scientificApprovals"] is False
    assert body["capabilities"]["arbitraryCode"] is False


def test_fastapi_routes_use_actor_headers(tmp_path: Path, monkeypatch):
    from app import main
    test_manager = TeamWorkspaceManager(str(tmp_path / "api.sqlite3"), 100, 1000, 1000)
    monkeypatch.setattr(main, "team_workspaces", test_manager)
    with TestClient(main.app) as client:
        created = client.post("/v1/team-workspaces", headers={"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}, json={"id": "api-workspace", "title": "API Workspace"})
        assert created.status_code == 200
        invite = client.post("/v1/team-workspaces/api-workspace/invitations", headers={"X-SC-Lab-Actor": "alice"}, json={"inviteeActorId": "bob", "role": "viewer"})
        assert invite.status_code == 200
        token = invite.json()["invitation"]["token"]
        accepted = client.post("/v1/team-workspaces/invitations/accept", headers={"X-SC-Lab-Actor": "bob", "X-SC-Lab-Actor-Name": "Bob"}, json={"token": token})
        assert accepted.status_code == 200
        listing = client.get("/v1/team-workspaces", headers={"X-SC-Lab-Actor": "bob"})
        assert listing.status_code == 200
        assert listing.json()["workspaces"][0]["currentMembership"]["role"] == "viewer"
