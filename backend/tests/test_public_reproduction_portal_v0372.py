import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.manuscript_assembly import ManuscriptAssemblyStudio
from app.public_reproduction_portal import PublicReproductionError, PublicReproductionPortal, policies
from app.publication_studio import ReproducibilityPublicationStudio
from app.team_workspaces import TeamWorkspaceManager


def setup(tmp_path: Path):
    ws = TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 10000)
    ws.create({"id": "research-team", "title": "Research Team"}, "alice", "Alice")
    for actor, role in [("bob", "reviewer"), ("dana", "editor"), ("cory", "contributor"), ("eve", "viewer")]:
        inv = ws.invite("research-team", {"inviteeActorId": actor, "role": role}, "alice")
        ws.accept_invitation({"token": inv["invitation"]["token"]}, actor, actor.title())
    pub = ReproducibilityPublicationStudio(str(tmp_path / "publications.sqlite3"), ws, 100, 100, 100, 10000)
    package = pub.create_package("research-team", {"id": "wetland-repro", "title": "Wetland Reproducibility Package"}, "dana")["package"]
    package = pub.update_package("research-team", package["id"], {
        "resources": [
            {"id": "dataset-1", "type": "dataset", "title": "Wetland observations", "sha256": "1" * 64, "mediaType": "text/csv"},
            {"id": "workflow-1", "type": "workflow", "title": "Descriptive analysis", "sha256": "2" * 64, "mediaType": "application/json"},
        ],
        "methods": {"protocol": "Count observations using fixed transects", "registeredMethods": ["statistics.descriptive"]},
        "environment": {"python": "3.12", "packages": {"numpy": "2.0"}},
        "citations": [{"formatted": "Ahmad, T. (2026). Wetland study."}],
        "provenance": {"runIds": ["run-1"]},
    }, "dana")["package"]
    package = pub.seal_package("research-team", package["id"], "dana")["package"]
    pub.verify_package("research-team", package["id"], "bob")
    publication = pub.create_publication("research-team", {
        "id": "wetland-paper", "packageId": package["id"], "title": "Wetland Monitoring Study",
        "abstract": "A reproducible field monitoring study.", "authors": [{"name": "Tariq Ahmad"}],
        "sections": [{"title": "Results", "body": "The verified aggregate count was 42."}], "visibility": "public",
    }, "dana")["publication"]
    pub.render_publication("research-team", publication["id"], "dana")
    pub.mark_ready("research-team", publication["id"], "bob")
    publication = pub.publish("research-team", publication["id"], {"scientificSignoff": {"id": "signoff-1", "signoffHash": "a" * 64}}, "alice")["publication"]
    assembly = ManuscriptAssemblyStudio(str(tmp_path / "assembly.sqlite3"), ws, pub, 100, 1000, 100, 10000)
    assembled = assembly.create_assembly("research-team", {
        "id": "wetland-manuscript", "title": "Wetland Monitoring Study", "packageId": package["id"],
        "publicationId": publication["id"], "sections": [{"id": "abstract", "kind": "abstract", "body": "Summary"}],
    }, "cory")["assembly"]
    assembled = assembly.seal("research-team", assembled["id"], "dana")["assembly"]
    portal = PublicReproductionPortal(str(tmp_path / "public-reproduction.sqlite3"), ws, pub, assembly, "receipt-secret", 100, 1000, 3600, 10000)
    return ws, pub, assembly, portal, package, publication, assembled


def create_and_publish(portal, publication, assembly):
    record = portal.create_record("research-team", {
        "id": "wetland-verification", "slug": "wetland-verification", "publicationId": publication["id"],
        "assemblyId": assembly["id"], "title": "Wetland Study Verification", "summary": "Public reproduction record.",
        "publicMetadata": {"field": "ecology", "studyYear": 2026},
    }, "dana")["record"]
    return portal.publish_record("research-team", record["id"], "alice")["record"]


def evidence(challenge):
    expected = challenge["expected"]
    return {
        "nonce": challenge["nonce"], "recordHash": expected["recordHash"], "snapshotHash": expected["snapshotHash"],
        "manifestHash": expected["manifestHash"], "publicationHash": expected["publicationHash"],
        "packageHash": expected["packageHash"], "assemblyHash": expected["assemblyHash"],
        "resourceHashes": expected["resourceHashes"], "environment": {"python": "3.12", "platform": "independent-node"},
        "resultHashes": {"summary": "3" * 64},
    }


def test_policy_contract():
    p = policies(10, 20, 3600)
    assert p["version"] == "0.37.2"
    assert p["capabilities"]["signedReceipts"] is True
    assert p["capabilities"]["publicCodeExecution"] is False


def test_record_requires_published_publication_and_editor_role(tmp_path):
    ws, pub, assembly, portal, package, publication, assembled = setup(tmp_path)
    with pytest.raises(PublicReproductionError) as exc:
        portal.create_record("research-team", {"id": "blocked", "slug": "blocked-record", "publicationId": publication["id"]}, "eve")
    assert exc.value.status_code == 403
    with pub._connect() as con:
        con.execute("UPDATE publications SET status='ready' WHERE id=?", (publication["id"],))
    with pytest.raises(PublicReproductionError) as exc:
        portal.create_record("research-team", {"id": "not-published", "slug": "not-published", "publicationId": publication["id"]}, "dana")
    assert exc.value.status_code == 409


def test_public_snapshot_is_safe_and_hides_workspace_actor_ids(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = create_and_publish(portal, publication, assembled)
    public = portal.public_record(record["slug"])["record"]
    assert public["status"] == "published" and "workspaceId" not in public and "createdBy" not in public
    assert public["snapshot"]["package"]["resources"][0]["sha256"] == "1" * 64
    assert len(public["snapshot"]["snapshotHash"]) == 64


def test_nonce_challenge_and_signed_verification_receipt(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = create_and_publish(portal, publication, assembled)
    challenge = portal.issue_challenge(record["slug"], {"submitterLabel": "Independent verifier"})["challenge"]
    result = portal.submit_challenge(challenge["id"], evidence(challenge))
    assert result["verified"] is True
    receipt = result["receipt"]
    assert len(receipt["receiptHash"]) == 64 and len(receipt["signature"]) == 64
    public = portal.public_receipt(receipt["receiptHash"])
    assert public["ok"] is True and public["integrity"]["signatureValid"] is True


def test_mismatch_creates_failed_receipt_without_mutating_record(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = create_and_publish(portal, publication, assembled)
    challenge = portal.issue_challenge(record["slug"])["challenge"]
    bad = evidence(challenge); bad["resourceHashes"]["dataset-1"] = "f" * 64
    result = portal.submit_challenge(challenge["id"], bad)
    assert result["verified"] is False
    assert any(item["field"] == "resourceHashes.dataset-1" for item in result["receipt"]["mismatches"])
    assert portal.public_record(record["slug"])["record"]["recordHash"] == record["recordHash"]


def test_expired_challenge_is_rejected(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = create_and_publish(portal, publication, assembled)
    challenge = portal.issue_challenge(record["slug"])["challenge"]
    expired = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
    with portal._connect() as con:
        con.execute("UPDATE reproduction_challenges SET expires_at=? WHERE id=?", (expired, challenge["id"]))
    with pytest.raises(PublicReproductionError) as exc:
        portal.submit_challenge(challenge["id"], evidence(challenge))
    assert exc.value.status_code == 410


def test_withdrawal_preserves_public_tombstone_and_blocks_new_challenges(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = create_and_publish(portal, publication, assembled)
    withdrawn = portal.withdraw_record("research-team", record["id"], {"reason": "Superseded by a corrected release."}, "alice")["record"]
    assert withdrawn["status"] == "withdrawn"
    public = portal.public_record(record["slug"])["record"]
    assert public["publicStatus"] == "withdrawn" and "Superseded" in public["withdrawalReason"]
    with pytest.raises(PublicReproductionError) as exc:
        portal.issue_challenge(record["slug"])
    assert exc.value.status_code == 409


def test_snapshot_tampering_blocks_publication(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = portal.create_record("research-team", {"id": "tampered-record", "slug": "tampered-record", "publicationId": publication["id"], "assemblyId": assembled["id"]}, "dana")["record"]
    with portal._connect() as con:
        snapshot = json.loads(con.execute("SELECT snapshot_json FROM public_reproduction_records WHERE id=?", (record["id"],)).fetchone()[0])
        snapshot["publication"]["title"] = "Tampered"
        con.execute("UPDATE public_reproduction_records SET snapshot_json=? WHERE id=?", (json.dumps(snapshot), record["id"]))
    with pytest.raises(PublicReproductionError) as exc:
        portal.publish_record("research-team", record["id"], "alice")
    assert exc.value.status_code == 409


def test_executable_secret_and_embedded_data_fields_rejected(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    with pytest.raises(PublicReproductionError) as exc:
        portal.create_record("research-team", {"id": "unsafe-record", "slug": "unsafe-record", "publicationId": publication["id"], "assemblyId": assembled["id"], "publicMetadata": {"callbackUrl": "https://bad.example"}}, "dana")
    assert exc.value.status_code == 422


def test_health_timeline_and_challenge_listing(tmp_path):
    _, _, _, portal, _, publication, assembled = setup(tmp_path)
    record = create_and_publish(portal, publication, assembled)
    portal.issue_challenge(record["slug"])
    health = portal.health()
    assert health["database"]["integrity"] == "ok" and health["database"]["schemaVersion"] == 1
    events = portal.timeline("research-team", "eve")["events"]
    challenges = portal.list_challenges("research-team", record["id"], "bob")["challenges"]
    assert events and all(len(item["eventHash"]) == 64 for item in events)
    assert len(challenges) == 1


def test_fastapi_workspace_and_public_routes(tmp_path, monkeypatch):
    from app import main
    ws, pub, assembly, portal, package, publication, assembled = setup(tmp_path)
    monkeypatch.setattr(main, "team_workspaces", ws)
    monkeypatch.setattr(main, "publication_studio", pub)
    monkeypatch.setattr(main, "manuscript_assembly", assembly)
    monkeypatch.setattr(main, "public_reproduction", portal)
    headers = {"X-SC-Lab-Actor": "dana", "X-SC-Lab-Actor-Name": "Dana"}
    admin = {"X-SC-Lab-Actor": "alice", "X-SC-Lab-Actor-Name": "Alice"}
    with TestClient(main.app) as client:
        health = client.get("/v1/public-reproduction/health", headers=headers)
        assert health.status_code == 200 and health.json()["serviceVersion"] == "0.38.1"
        created = client.post("/v1/team-workspaces/research-team/public-reproduction-records", headers=headers, json={"id": "api-record", "slug": "api-verification-record", "publicationId": publication["id"], "assemblyId": assembled["id"]})
        assert created.status_code == 200
        published = client.post("/v1/team-workspaces/research-team/public-reproduction-records/api-record/publish", headers=admin)
        assert published.status_code == 200
        public = client.get("/v1/public/reproduction/api-verification-record")
        assert public.status_code == 200 and public.json()["record"]["recordHash"]
        challenge = client.post("/v1/public/reproduction/api-verification-record/challenges", json={"submitterLabel": "API verifier"})
        assert challenge.status_code == 200
        c = challenge.json()["challenge"]
        submitted = client.post(f"/v1/public/reproduction/challenges/{c['id']}/submit", json=evidence(c))
        assert submitted.status_code == 200 and submitted.json()["verified"] is True
