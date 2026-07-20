from pathlib import Path
import importlib
import json

import pytest
from fastapi.testclient import TestClient

from app.institutional_governance import (
    InstitutionalGovernanceError,
    InstitutionalGovernanceManager,
    policies,
)
from app.team_workspaces import TeamWorkspaceManager


def setup(tmp_path: Path):
    workspaces = TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 10000)
    workspaces.create({"id": "research-team", "title": "Research Team"}, "alice", "Alice")
    for actor, role in (("bob", "contributor"), ("carol", "reviewer"), ("eve", "viewer")):
        invite = workspaces.invite("research-team", {"inviteeActorId": actor, "role": role}, "alice")
        workspaces.accept_invitation({"token": invite["invitation"]["token"]}, actor, actor.title())
    manager = InstitutionalGovernanceManager(str(tmp_path / "governance.sqlite3"), workspaces)
    manager.create_institution({"id": "catalyst-institute", "name": "Catalyst Institute", "domains": ["example.org"]}, "alice")
    manager.create_unit("catalyst-institute", {"id": "climate-lab", "title": "Climate Lab", "code": "CLIM"}, "alice")
    for principal in (
        {"id": "bob", "principalType": "human", "displayName": "Bob Researcher", "email": "bob@example.org"},
        {"id": "carol", "principalType": "human", "displayName": "Carol Approver", "email": "carol@example.org"},
        {"id": "compute-agent", "principalType": "service", "displayName": "Compute Agent", "externalSubject": "service:compute-agent"},
    ):
        manager.register_principal("catalyst-institute", principal, "alice")
    manager.grant_role("catalyst-institute", {"principalId": "bob", "role": "steward", "workspaceId": "research-team", "unitId": "climate-lab"}, "alice")
    manager.grant_role("catalyst-institute", {"principalId": "carol", "role": "approver", "workspaceId": "research-team", "unitId": "climate-lab"}, "alice")
    manager.grant_role("catalyst-institute", {"principalId": "compute-agent", "role": "researcher", "workspaceId": "research-team"}, "alice")
    retention = manager.create_retention_policy("catalyst-institute", {"id": "research-ten-years", "title": "Research Ten Years", "retentionDays": 3650, "reviewIntervalDays": 365, "disposition": "review"}, "alice")
    manager.govern_workspace("research-team", {"institutionId": "catalyst-institute", "unitId": "climate-lab", "classification": "confidential", "retentionPolicyId": retention["retentionPolicy"]["id"], "approvalActions": ["research.publish", "research.share"], "approvalQuorum": 1, "externalSharing": True}, "alice")
    return workspaces, manager


def test_policy_boundary():
    body = policies()
    assert body["version"] == "0.39.0"
    assert body["capabilities"]["credentialFreeServicePrincipals"] is True
    assert body["capabilities"]["secretStorage"] is False
    assert body["capabilities"]["singleSignOn"] is False


def test_institution_bootstrap_and_directory(tmp_path):
    _, manager = setup(tmp_path)
    institution = manager.get_institution("catalyst-institute", "alice")["institution"]
    assert institution["currentRoles"] == ["institution-owner"]
    principals = manager.list_principals("catalyst-institute", "alice")["principals"]
    service = next(item for item in principals if item["id"] == "compute-agent")
    assert service["principalType"] == "service" and service["credentialsStored"] is False
    assert manager.list_units("catalyst-institute", "alice")["units"][0]["id"] == "climate-lab"


def test_final_owner_binding_cannot_be_revoked(tmp_path):
    _, manager = setup(tmp_path)
    owner = next(item for item in manager.list_bindings("catalyst-institute", "alice")["bindings"] if item["role"] == "institution-owner")
    with pytest.raises(InstitutionalGovernanceError) as exc:
        manager.revoke_role("catalyst-institute", owner["id"], "alice")
    assert exc.value.status_code == 409


def test_workspace_governance_and_policy_evaluation(tmp_path):
    _, manager = setup(tmp_path)
    governed = manager.get_workspace_governance("research-team", "bob")["workspaceGovernance"]
    assert governed["classification"] == "confidential"
    share = manager.evaluate("research-team", {"action": "research.share", "resourceType": "dataset", "resourceId": "dataset-1"}, "bob")["decision"]
    assert share["allowed"] is True and share["requiresApproval"] is True and share["approvalQuorum"] == 1
    denied = manager.evaluate("research-team", {"action": "governance.administer", "resourceType": "dataset", "resourceId": "dataset-1"}, "bob")["decision"]
    assert denied["allowed"] is False


def test_approval_workflow(tmp_path):
    _, manager = setup(tmp_path)
    created = manager.create_approval("research-team", {"id": "approval-1", "action": "research.share", "resourceType": "dataset", "resourceId": "dataset-1", "request": {"summary": "Share aggregate climate indicators"}}, "bob")
    assert created["approvalRequest"]["status"] == "pending"
    decided = manager.decide_approval("research-team", "approval-1", {"decision": "approve", "rationale": "Aggregate data only"}, "carol")
    assert decided["approvalRequest"]["status"] == "approved"
    assert decided["approvalRequest"]["decisions"][0]["actorId"] == "carol"


def test_restricted_export_requires_owner(tmp_path):
    _, manager = setup(tmp_path)
    manager.govern_workspace("research-team", {"institutionId": "catalyst-institute", "unitId": "climate-lab", "classification": "restricted", "approvalActions": ["research.export"], "approvalQuorum": 1, "externalSharing": False}, "alice")
    result = manager.evaluate("research-team", {"action": "research.export", "resourceType": "dataset", "resourceId": "restricted-1"}, "bob")["decision"]
    assert result["allowed"] is False
    assert any("institution owner" in reason.lower() for reason in result["reasons"])


def test_dashboard_and_hash_chained_timeline(tmp_path):
    _, manager = setup(tmp_path)
    dashboard = manager.dashboard("catalyst-institute", "alice")
    assert dashboard["counts"]["governedWorkspaces"] == 1
    timeline = manager.timeline("catalyst-institute", "alice", 100)["events"]
    assert len(timeline) >= 10
    chronological = list(reversed(timeline))
    for previous, current in zip(chronological, chronological[1:]):
        assert current["previousHash"] == previous["eventHash"]


def test_contract_instances(tmp_path):
    import jsonschema

    _, manager = setup(tmp_path)
    root = Path(__file__).resolve().parents[1] / "contracts"
    records = [
        ("institution-v0390.schema.json", manager.get_institution("catalyst-institute", "alice")["institution"]),
        ("organizational-unit-v0390.schema.json", manager.list_units("catalyst-institute", "alice")["units"][0]),
        ("institutional-principal-v0390.schema.json", manager.list_principals("catalyst-institute", "alice")["principals"][0]),
        ("institutional-role-binding-v0390.schema.json", manager.list_bindings("catalyst-institute", "alice")["bindings"][0]),
        ("retention-policy-v0390.schema.json", manager.list_retention_policies("catalyst-institute", "alice")["retentionPolicies"][0]),
        ("workspace-governance-v0390.schema.json", manager.get_workspace_governance("research-team", "alice")["workspaceGovernance"]),
        ("governance-decision-v0390.schema.json", manager.evaluate("research-team", {"action": "research.read", "resourceType": "dataset", "resourceId": "d1"}, "bob")["decision"]),
        ("institutional-governance-event-v0390.schema.json", manager.timeline("catalyst-institute", "alice", 1)["events"][0]),
    ]
    for name, value in records:
        jsonschema.Draft202012Validator(json.loads((root / name).read_text())).validate(value)


def test_fastapi_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("SC_LAB_TEAM_WORKSPACE_DB_PATH", str(tmp_path / "route-workspaces.sqlite3"))
    monkeypatch.setenv("SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH", str(tmp_path / "route-governance.sqlite3"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "route-key")
    import app.config as config_module
    import app.main as main_module
    importlib.reload(config_module)
    importlib.reload(main_module)
    client = TestClient(main_module.app)
    headers = {"X-SC-Lab-Key": "route-key", "X-SC-Lab-Actor": "alice"}
    assert client.get("/v1/institutional-governance/health", headers=headers).json()["serviceVersion"] == "0.39.2"
    assert client.post("/v1/team-workspaces", headers=headers, json={"id": "route-team", "title": "Route Team"}).status_code == 200
    created = client.post("/v1/institutions", headers=headers, json={"id": "route-institution", "name": "Route Institution"})
    assert created.status_code == 200
    assert client.post("/v1/institutions/route-institution/principals", headers=headers, json={"id": "route-service", "principalType": "service", "displayName": "Route Service"}).status_code == 200
    assert client.post("/v1/team-workspaces/route-team/institutional-governance", headers=headers, json={"institutionId": "route-institution", "classification": "internal"}).status_code == 200
    assert client.get("/v1/institutions/route-institution/governance-dashboard", headers=headers).status_code == 200
