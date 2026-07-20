import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.research_interoperability import InteroperabilityError, ResearchInteroperabilityLayer, policies
from app.team_workspaces import TeamWorkspaceManager


def setup(tmp_path: Path):
    ws = TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 10000)
    ws.create({"id": "research-team", "title": "Research Team"}, "alice", "Alice")
    for actor, role in [("bob", "reviewer"), ("dana", "editor"), ("cory", "contributor"), ("eve", "viewer")]:
        invitation = ws.invite("research-team", {"inviteeActorId": actor, "role": role}, "alice")
        ws.accept_invitation({"token": invitation["invitation"]["token"]}, actor, actor.title())
    layer = ResearchInteroperabilityLayer(str(tmp_path / "interoperability.sqlite3"), ws, "receipt-secret", 100, 1000, 10000)
    return ws, layer


def register_profiles(layer):
    lab = layer.register_profile("research-team", {
        "id": "lab-profile", "productId": "sustainable-catalyst-lab", "displayName": "Sustainable Catalyst Lab",
        "supportedContracts": ["sc-research-dataset/1.0", "sc-research-workflow/1.0"],
        "capabilities": ["sha256-resources", "provenance", "workspace-governance"],
    }, "dana")["profile"]
    decision = layer.register_profile("research-team", {
        "id": "decision-profile", "productId": "decision-studio", "displayName": "Decision Studio",
        "supportedContracts": ["sc-research-dataset/1.0", "sc-decision-packet/1.0"],
        "capabilities": ["sha256-resources", "provenance", "decision-packets"],
    }, "dana")["profile"]
    return lab, decision


def handoff_payload():
    return {
        "id": "wetland-dataset-handoff", "sourceProduct": "sustainable-catalyst-lab", "targetProduct": "decision-studio",
        "entityType": "dataset", "contractVersion": "sc-research-dataset/1.0",
        "resource": {"id": "wetland-dataset-v1", "title": "Wetland dataset", "sha256": "1" * 64, "mediaType": "text/csv", "metadata": {"rows": 42}},
        "provenance": {"runIds": ["run-1"], "workspaceSnapshot": "2" * 64},
        "requiredCapabilities": ["sha256-resources", "provenance"],
    }


def test_policy_contract():
    body = policies(10, 20)
    assert body["version"] == "0.38.0"
    assert body["capabilities"]["typedCrossProductHandoffs"] is True
    assert body["capabilities"]["directRemoteCallbacks"] is False


def test_profile_registration_requires_editor(tmp_path):
    _, layer = setup(tmp_path)
    with pytest.raises(InteroperabilityError) as exc:
        layer.register_profile("research-team", {"id": "bad", "productId": "decision-studio", "supportedContracts": ["sc-research-dataset/1.0"]}, "eve")
    assert exc.value.status_code == 403
    profile = layer.register_profile("research-team", {"id": "lab", "productId": "sustainable-catalyst-lab", "supportedContracts": ["sc-research-dataset/1.0"], "capabilities": ["provenance"]}, "dana")["profile"]
    assert len(profile["profileHash"]) == 64


def test_contract_and_capability_negotiation(tmp_path):
    _, layer = setup(tmp_path); register_profiles(layer)
    result = layer.negotiate("research-team", {"sourceProfileId": "lab-profile", "targetProfileId": "decision-profile", "requestedContracts": ["sc-research-dataset/1.0"], "requiredCapabilities": ["provenance"]}, "eve")["negotiation"]
    assert result["compatible"] is True and result["selectedContract"] == "sc-research-dataset/1.0"
    blocked = layer.negotiate("research-team", {"sourceProfileId": "lab-profile", "targetProfileId": "decision-profile", "requestedContracts": ["sc-research-workflow/1.0"]}, "eve")["negotiation"]
    assert blocked["compatible"] is False


def test_handoff_sealing_and_export_bundle(tmp_path):
    _, layer = setup(tmp_path); register_profiles(layer)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    assert created["status"] == "draft" and len(created["envelopeHash"]) == 64
    sealed = layer.seal_handoff("research-team", created["id"], {"sourceProfileId": "lab-profile", "targetProfileId": "decision-profile"}, "dana")["handoff"]
    assert sealed["status"] == "sealed" and sealed["compatibility"]["compatible"] is True
    bundle = layer.export_bundle("research-team", created["id"], "eve")["bundle"]
    assert len(bundle["bundleHash"]) == 64 and bundle["envelopeHash"] == created["envelopeHash"]


def test_tampered_envelope_rejected_on_seal(tmp_path):
    _, layer = setup(tmp_path)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    with layer._connect() as con:
        envelope = json.loads(con.execute("SELECT envelope_json FROM interoperability_handoffs WHERE id=?", (created["id"],)).fetchone()[0])
        envelope["resource"]["title"] = "Tampered"
        con.execute("UPDATE interoperability_handoffs SET envelope_json=? WHERE id=?", (json.dumps(envelope), created["id"]))
    with pytest.raises(InteroperabilityError) as exc:
        layer.seal_handoff("research-team", created["id"], {}, "dana")
    assert exc.value.status_code == 409


def test_import_is_idempotent_and_hash_verified(tmp_path):
    _, layer = setup(tmp_path)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    layer.seal_handoff("research-team", created["id"], {}, "dana")
    bundle = layer.export_bundle("research-team", created["id"], "eve")["bundle"]
    first = layer.import_envelope("research-team", {"importId": "incoming-wetland", "envelope": bundle["envelope"], "envelopeHash": bundle["envelopeHash"]}, "cory")
    second = layer.import_envelope("research-team", {"importId": "incoming-wetland-2", "envelope": bundle["envelope"], "envelopeHash": bundle["envelopeHash"]}, "cory")
    assert first["idempotent"] is False and second["idempotent"] is True
    bad = dict(bundle); bad["envelopeHash"] = "f" * 64
    with pytest.raises(InteroperabilityError): layer.import_envelope("research-team", bad, "cory")


def test_signed_receipt_and_verification(tmp_path):
    _, layer = setup(tmp_path)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    layer.seal_handoff("research-team", created["id"], {}, "dana")
    receipt = layer.record_receipt("research-team", created["id"], {"id": "receipt-1", "decision": "accepted", "details": {"importedResourceId": "decision-dataset-1"}}, "bob")["receipt"]
    assert len(receipt["receiptHash"]) == 64 and len(receipt["signature"]) == 64
    verified = layer.verify_receipt("research-team", receipt["receiptHash"], "eve")
    assert verified["ok"] is True and verified["integrity"]["signatureValid"] is True


def test_unsafe_fields_and_unknown_entity_rejected(tmp_path):
    _, layer = setup(tmp_path)
    bad = handoff_payload(); bad["resource"]["callbackUrl"] = "https://example.invalid"
    with pytest.raises(InteroperabilityError) as exc: layer.create_handoff("research-team", bad, "cory")
    assert exc.value.status_code == 422
    bad2 = handoff_payload(); bad2["entityType"] = "arbitrary-object"
    with pytest.raises(InteroperabilityError): layer.create_handoff("research-team", bad2, "cory")


def test_withdrawal_preserves_history_and_accepted_handoff_is_immutable(tmp_path):
    _, layer = setup(tmp_path)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    withdrawn = layer.withdraw("research-team", created["id"], {"reason": "Superseded by corrected metadata."}, "dana")["handoff"]
    assert withdrawn["status"] == "withdrawn" and "Superseded" in withdrawn["withdrawalReason"]
    created2 = layer.create_handoff("research-team", {**handoff_payload(), "id": "accepted-handoff", "resource": {**handoff_payload()["resource"], "id": "accepted-resource", "sha256": "3" * 64}}, "cory")["handoff"]
    layer.seal_handoff("research-team", created2["id"], {}, "dana")
    layer.record_receipt("research-team", created2["id"], {"decision": "accepted"}, "bob")
    with pytest.raises(InteroperabilityError) as exc: layer.withdraw("research-team", created2["id"], {"reason": "No"}, "dana")
    assert exc.value.status_code == 409



def test_profile_ids_cannot_cross_workspace_boundaries(tmp_path):
    ws, layer = setup(tmp_path)
    ws.create({"id": "second-team", "title": "Second Team"}, "zoe", "Zoe")
    layer.register_profile("research-team", {"id": "shared-profile", "productId": "sustainable-catalyst-lab", "supportedContracts": ["sc-research-dataset/1.0"]}, "dana")
    with pytest.raises(InteroperabilityError) as exc:
        layer.register_profile("second-team", {"id": "shared-profile", "productId": "decision-studio", "supportedContracts": ["sc-research-dataset/1.0"]}, "zoe")
    assert exc.value.status_code == 409


def test_seal_rejects_profile_product_mismatch(tmp_path):
    _, layer = setup(tmp_path); register_profiles(layer)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    with pytest.raises(InteroperabilityError) as exc:
        layer.seal_handoff("research-team", created["id"], {"sourceProfileId": "decision-profile", "targetProfileId": "lab-profile"}, "dana")
    assert exc.value.status_code == 409


def test_draft_handoff_cannot_receive_receipt(tmp_path):
    _, layer = setup(tmp_path)
    created = layer.create_handoff("research-team", handoff_payload(), "cory")["handoff"]
    with pytest.raises(InteroperabilityError) as exc:
        layer.record_receipt("research-team", created["id"], {"decision": "accepted"}, "bob")
    assert exc.value.status_code == 409


def test_health_timeline_and_fastapi_routes(tmp_path, monkeypatch):
    db = tmp_path / "route-interoperability.sqlite3"; wsdb = tmp_path / "route-workspaces.sqlite3"
    monkeypatch.setenv("SC_LAB_TEAM_WORKSPACE_DB_PATH", str(wsdb)); monkeypatch.setenv("SC_LAB_INTEROPERABILITY_DB_PATH", str(db)); monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "test-key")
    import importlib
    import app.config as config_module; import app.main as main_module
    importlib.reload(config_module); importlib.reload(main_module)
    client = TestClient(main_module.app); headers = {"X-SC-Lab-Key": "test-key", "X-SC-Lab-Actor": "alice"}
    created_ws = client.post("/v1/team-workspaces", headers=headers, json={"id": "route-team", "title": "Route Team"})
    assert created_ws.status_code == 200
    profile = client.post("/v1/team-workspaces/route-team/interoperability-profiles", headers=headers, json={"id": "route-lab", "productId": "sustainable-catalyst-lab", "supportedContracts": ["sc-research-dataset/1.0"], "capabilities": ["provenance"]})
    assert profile.status_code == 200
    health = client.get("/v1/research-interoperability/health", headers=headers)
    assert health.status_code == 200 and health.json()["serviceVersion"] == "0.39.3"
    timeline = client.get("/v1/team-workspaces/route-team/interoperability-timeline", headers=headers)
    assert timeline.status_code == 200 and timeline.json()["count"] >= 1
