from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.research_interoperability import InteroperabilityError, ResearchInteroperabilityLayer
from app.team_workspaces import TeamWorkspaceManager
from app.typed_cross_product_handoffs import ADAPTERS, TypedCrossProductHandoffs, policies


def setup(tmp_path: Path):
    ws = TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 10000)
    ws.create({"id": "research-team", "title": "Research Team"}, "alice", "Alice")
    for actor, role in [("dana", "editor"), ("cory", "contributor"), ("eve", "viewer")]:
        invitation = ws.invite("research-team", {"inviteeActorId": actor, "role": role}, "alice")
        ws.accept_invitation({"token": invitation["invitation"]["token"]}, actor, actor.title())
    interop = ResearchInteroperabilityLayer(str(tmp_path / "interop.sqlite3"), ws, "secret", 100, 1000, 10000)
    return ws, interop, TypedCrossProductHandoffs(interop)


def payload(target="decision-studio", entity="dataset"):
    return {
        "id": f"wetland-{target}-{entity}", "sourceProduct": "sustainable-catalyst-lab", "targetProduct": target,
        "entityType": entity,
        "resource": {"id": "wetland-v1", "title": "Wetland observations", "sha256": "1" * 64, "mediaType": "text/csv", "metadata": {"rows": 42}},
        "provenance": {"runIds": ["run-1"]},
    }


def test_policy_and_adapter_catalog(tmp_path):
    _, _, typed = setup(tmp_path)
    assert policies()["version"] == "0.38.1"
    catalog = typed.catalog()
    assert catalog["count"] == 13 and len(catalog["catalogHash"]) == 64
    assert "catalyst-analytics-r" in ADAPTERS


def test_lab_decision_studio_dataset_plan(tmp_path):
    _, _, typed = setup(tmp_path)
    plan = typed.plan("research-team", payload(), "eve")["plan"]
    assert plan["valid"] is True
    assert plan["route"]["targetBinding"] == "decision-evidence-input"
    assert plan["handoff"]["contractVersion"] == "sc-research-dataset/1.0"
    assert plan["handoff"]["resource"]["metadata"]["typedRouteHash"] == plan["route"]["routeHash"]


def test_alias_and_analytics_route(tmp_path):
    _, _, typed = setup(tmp_path)
    body = payload("analyticsr", "model")
    plan = typed.plan("research-team", body, "eve")["plan"]
    assert plan["valid"] is True and plan["route"]["targetProduct"] == "catalyst-analytics-r"
    assert plan["route"]["targetBinding"] == "analysis-input"


def test_knowledge_library_publication_route(tmp_path):
    _, _, typed = setup(tmp_path)
    plan = typed.plan("research-team", payload("knowledge-library", "publication"), "eve")["plan"]
    assert plan["valid"] is True and plan["route"]["contractVersion"] == "sc-research-publication/1.0"


def test_unsupported_product_pair_is_reported(tmp_path):
    _, _, typed = setup(tmp_path)
    plan = typed.plan("research-team", payload("research-librarian", "model"), "eve")["plan"]
    assert plan["valid"] is False and any("does not accept" in item for item in plan["errors"])


def test_contract_override_must_match_route(tmp_path):
    _, _, typed = setup(tmp_path)
    body = payload(); body["contractVersion"] = "sc-research-workflow/1.0"
    plan = typed.plan("research-team", body, "eve")["plan"]
    assert plan["valid"] is False and "requires contract" in plan["errors"][0]


def test_create_persists_governed_handoff(tmp_path):
    _, interop, typed = setup(tmp_path)
    result = typed.create("research-team", payload(), "cory")
    assert result["handoff"]["status"] == "draft" and result["sealed"] is False
    stored = interop.get_handoff("research-team", result["handoff"]["id"], "eve")["handoff"]
    assert stored["resource"]["metadata"]["targetBinding"] == "decision-evidence-input"


def test_profile_aware_create_and_seal(tmp_path):
    _, interop, typed = setup(tmp_path)
    interop.register_profile("research-team", {"id":"lab-profile","productId":"sustainable-catalyst-lab","supportedContracts":["sc-research-dataset/1.0"],"capabilities":["sha256-resources","provenance","workspace-governance","typed-route-plan"]}, "dana")
    interop.register_profile("research-team", {"id":"decision-profile","productId":"decision-studio","supportedContracts":["sc-research-dataset/1.0"],"capabilities":["sha256-resources","provenance","workspace-governance","typed-route-plan"]}, "dana")
    body = payload(); body.update({"sourceProfileId":"lab-profile","targetProfileId":"decision-profile"})
    result = typed.create("research-team", body, "dana")
    assert result["sealed"] is True and result["handoff"]["status"] == "sealed"


def test_governed_layer_rejects_unsafe_resource_fields(tmp_path):
    _, _, typed = setup(tmp_path)
    body = payload(); body["resource"]["callbackUrl"] = "https://example.invalid"
    with pytest.raises(InteroperabilityError) as exc:
        typed.create("research-team", body, "cory")
    assert exc.value.status_code == 422


def test_route_catalog_filters(tmp_path):
    _, _, typed = setup(tmp_path)
    routes = typed.route_catalog("sustainable-catalyst-lab", "site-intelligence", "observation-set")
    assert routes["count"] == 1 and routes["routes"][0]["targetBinding"] == "intelligence-source"


def test_health_and_fastapi_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("SC_LAB_TEAM_WORKSPACE_DB_PATH", str(tmp_path / "route-ws.sqlite3"))
    monkeypatch.setenv("SC_LAB_INTEROPERABILITY_DB_PATH", str(tmp_path / "route-interop.sqlite3"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "test-key")
    import importlib
    import app.config as config_module
    import app.main as main_module
    importlib.reload(config_module); importlib.reload(main_module)
    client = TestClient(main_module.app)
    headers = {"X-SC-Lab-Key": "test-key", "X-SC-Lab-Actor": "alice"}
    assert client.post("/v1/team-workspaces", headers=headers, json={"id":"route-team","title":"Route Team"}).status_code == 200
    health = client.get("/v1/typed-cross-product-handoffs/health", headers=headers)
    assert health.status_code == 200 and health.json()["serviceVersion"] == "0.38.1"
    catalog = client.get("/v1/typed-cross-product-handoffs/adapters", headers=headers)
    assert catalog.status_code == 200 and catalog.json()["count"] == 13
    plan = client.post("/v1/team-workspaces/route-team/typed-research-handoffs/plan", headers=headers, json=payload())
    assert plan.status_code == 200 and plan.json()["plan"]["valid"] is True
