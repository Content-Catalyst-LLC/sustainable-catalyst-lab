import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.manuscript_assembly import ManuscriptAssemblyError, ManuscriptAssemblyStudio, policies
from app.publication_studio import ReproducibilityPublicationStudio
from app.team_workspaces import TeamWorkspaceManager


def setup(tmp_path: Path):
    ws = TeamWorkspaceManager(str(tmp_path / "workspaces.sqlite3"), 100, 1000, 10000)
    ws.create({"id": "research-team", "title": "Research Team"}, "alice", "Alice")
    for actor, role in [("bob", "reviewer"), ("dana", "editor"), ("cory", "contributor"), ("eve", "viewer")]:
        inv = ws.invite("research-team", {"inviteeActorId": actor, "role": role}, "alice")
        ws.accept_invitation({"token": inv["invitation"]["token"]}, actor, actor.title())
    pub = ReproducibilityPublicationStudio(str(tmp_path / "publications.sqlite3"), ws, 100, 100, 100, 10000)
    package = pub.create_package("research-team", {"id": "wetland-repro", "title": "Wetland Study"}, "dana")["package"]
    package = pub.update_package("research-team", package["id"], {
        "resources": [{"id": "dataset-1", "type": "dataset", "title": "Wetland observations", "sha256": "1" * 64, "mediaType": "text/csv"}],
        "methods": {"protocol": "We counted observations using a fixed transect protocol", "registeredMethods": ["statistics.descriptive"]},
        "environment": {"python": "3.12", "packages": {"numpy": "2.0"}},
        "citations": [{"formatted": "Ahmad, T. (2026). Wetland study."}],
        "provenance": {"runIds": ["run-1"]},
    }, "dana")["package"]
    package = pub.seal_package("research-team", package["id"], "dana")["package"]
    studio = ManuscriptAssemblyStudio(str(tmp_path / "assembly.sqlite3"), ws, pub, 100, 1000, 100, 10000)
    return ws, pub, studio, package


def test_policy_contract():
    p = policies(10, 20, 30)
    assert p["version"] == "0.37.1"
    assert p["capabilities"]["outputOnlyNotebooks"] is True
    assert p["capabilities"]["arbitraryCode"] is False


def test_section_library_roles_and_revisions(tmp_path):
    _, _, s, _ = setup(tmp_path)
    with pytest.raises(ManuscriptAssemblyError) as exc:
        s.create_section("research-team", {"id": "blocked", "body": "x"}, "eve")
    assert exc.value.status_code == 403
    sec = s.create_section("research-team", {"id": "intro", "title": "Introduction", "kind": "introduction", "content": {"body": "Original"}}, "cory")["section"]
    revised = s.update_section("research-team", sec["id"], {"content": {"body": "Revised"}}, "dana")["section"]
    assert revised["revision"] == 2 and revised["contentHash"] != sec["contentHash"]


def test_executable_and_secret_fields_rejected(tmp_path):
    _, _, s, _ = setup(tmp_path)
    with pytest.raises(ManuscriptAssemblyError) as exc:
        s.create_section("research-team", {"id": "unsafe", "content": {"sourceCode": "rm -rf /"}}, "cory")
    assert exc.value.status_code == 422


def test_library_section_is_snapshotted(tmp_path):
    _, _, s, package = setup(tmp_path)
    sec = s.create_section("research-team", {"id": "intro", "kind": "introduction", "content": {"body": "Original"}}, "cory")["section"]
    assembly = s.create_assembly("research-team", {"id": "paper", "title": "Wetlands", "packageId": package["id"], "sections": [{"librarySectionId": sec["id"]}]}, "cory")["assembly"]
    s.update_section("research-team", sec["id"], {"content": {"body": "Changed later"}}, "dana")
    assert assembly["sections"][0]["content"]["body"] == "Original"
    assert assembly["sections"][0]["libraryRevision"] == 1


def test_generated_methods_uses_reproducibility_package(tmp_path):
    _, _, s, package = setup(tmp_path)
    a = s.create_assembly("research-team", {"id": "methods-paper", "packageId": package["id"], "title": "Methods Paper", "sections": [{"id": "abstract", "kind": "abstract", "body": "Study summary"}]}, "cory")["assembly"]
    out = s.generate_methods("research-team", a["id"], "dana")
    body = out["section"]["content"]["body"]
    assert "statistics.descriptive" in body and "Python".lower() in body.lower()
    assert out["section"]["content"]["packageHash"] == package["packageHash"]


def test_notebook_validation_requires_output_safe_cells(tmp_path):
    _, _, s, _ = setup(tmp_path)
    a = s.create_assembly("research-team", {"id": "notebook", "documentType": "notebook", "template": "notebook-narrative", "title": "Notebook", "sections": [{"id": "intro", "kind": "introduction", "body": "Text"}]}, "cory")["assembly"]
    result = s.validate("research-team", a["id"], "eve")
    assert result["ok"] is False
    updated = s.update_assembly("research-team", a["id"], {"sections": [{"id": "cell-1", "kind": "notebook-markdown", "body": "Narrative"}, {"id": "cell-2", "kind": "notebook-output", "content": {"output": {"mean": 4.2}}}]}, "dana")["assembly"]
    assert s.validate("research-team", updated["id"], "eve")["ok"] is True


def test_cross_format_render_is_safe(tmp_path):
    _, _, s, package = setup(tmp_path)
    a = s.create_assembly("research-team", {"id": "rendered", "title": "Wetlands <script>", "packageId": package["id"], "metadata": {"authors": [{"name": "Tariq Ahmad"}], "citations": [{"key": "ahmad2026", "title": "Wetlands", "author": "Ahmad", "year": 2026}]}, "sections": [{"id": "abstract", "kind": "abstract", "title": "Abstract", "body": "Measured <carefully>."}]}, "cory")["assembly"]
    export = s.render("research-team", a["id"], "eve")["export"]
    assert {"manuscript.md", "report.html", "manuscript.xml", "notebook.ipynb", "methods.md", "references.bib"}.issubset(export["files"])
    assert "<script>" not in export["files"]["report.html"] and "&lt;script&gt;" in export["files"]["report.html"]
    notebook = json.loads(export["files"]["notebook.ipynb"])
    assert all(cell["cell_type"] != "code" for cell in notebook["cells"])


def test_seal_is_immutable_and_revision_preserves_lineage(tmp_path):
    _, _, s, package = setup(tmp_path)
    a = s.create_assembly("research-team", {"id": "sealed-paper", "title": "Paper", "packageId": package["id"], "sections": [{"id": "abstract", "kind": "abstract", "body": "Summary"}]}, "cory")["assembly"]
    sealed = s.seal("research-team", a["id"], "dana")["assembly"]
    assert sealed["status"] == "sealed" and len(sealed["assemblyHash"]) == 64
    with pytest.raises(ManuscriptAssemblyError) as exc:
        s.update_assembly("research-team", a["id"], {"title": "Changed"}, "dana")
    assert exc.value.status_code == 409
    revision = s.revise("research-team", a["id"], {"id": "sealed-paper-v2"}, "dana")["assembly"]
    assert revision["status"] == "draft" and revision["parentAssemblyHash"] == sealed["assemblyHash"]


def test_health_and_hashed_timeline(tmp_path):
    _, _, s, _ = setup(tmp_path)
    s.create_section("research-team", {"id": "intro", "body": "Text"}, "cory")
    h = s.health()
    assert h["database"]["integrity"] == "ok" and h["database"]["schemaVersion"] == 1
    events = s.timeline("research-team", "eve")["events"]
    assert events and all(len(event["eventHash"]) == 64 for event in events)


def test_fastapi_routes_use_workspace_actor(tmp_path, monkeypatch):
    from app import main
    ws, pub, studio, package = setup(tmp_path)
    monkeypatch.setattr(main, "team_workspaces", ws)
    monkeypatch.setattr(main, "publication_studio", pub)
    monkeypatch.setattr(main, "manuscript_assembly", studio)
    headers = {"X-SC-Lab-Actor": "cory", "X-SC-Lab-Actor-Name": "Cory"}
    with TestClient(main.app) as client:
        health = client.get("/v1/manuscript-assembly/health", headers=headers)
        assert health.status_code == 200 and health.json()["serviceVersion"] == "0.38.1"
        created = client.post("/v1/team-workspaces/research-team/research-assemblies", headers=headers, json={"id": "api-paper", "title": "API paper", "packageId": package["id"], "sections": [{"id": "abstract", "kind": "abstract", "body": "Summary"}]})
        assert created.status_code == 200
        rendered = client.post("/v1/team-workspaces/research-team/research-assemblies/api-paper/render", headers=headers)
        assert rendered.status_code == 200 and len(rendered.json()["export"]["exportHash"]) == 64
