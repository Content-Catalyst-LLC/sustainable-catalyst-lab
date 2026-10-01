from pathlib import Path

from app.computational_research_workspace_v01530 import ComputationalResearchWorkspaceManager


def sample_scene(name="scene-a", w=0.25):
    state = {"model": "logistic-growth", "w": w, "linked": {"history": [{"id": "sel:1"}], "pins": []}, "surface": {"xValues": [1, 2], "yValues": [3, 4]}}
    return {
        "id": name,
        "sceneState": state,
        "provenance": {"integrity": {"sceneStateDigest": f"digest-{name}-{w}"}},
    }


def manager(tmp_path: Path):
    return ComputationalResearchWorkspaceManager(str(tmp_path / "workspace.sqlite3"), True, 20, 1000)


def test_health_and_policies(tmp_path):
    m = manager(tmp_path)
    h = m.health()
    assert h["ok"] is True
    assert h["version"] == "0.153.0"
    assert h["serverBackedProjectAssets"] is True
    assert m.policies()["revisionsImmutable"] is True


def test_create_revision_fork_compare_lineage_archive(tmp_path):
    m = manager(tmp_path)
    a = m.create_asset("project:test", {"title": "Baseline scene", "scene": sample_scene(), "provenance": sample_scene()["provenance"], "computeRefs": [{"ref": "run:123", "method": "simulation.parameter_sweep"}]}, "actor:test")
    aid = a["asset"]["id"]
    assert a["asset"]["projectId"] == "project:test"
    assert a["revisions"][0]["revision"] == 1
    b = m.add_revision(aid, {"scene": sample_scene("scene-b", 0.5), "provenance": sample_scene("scene-b", 0.5)["provenance"]}, "actor:test")
    assert b["revisions"][0]["revision"] == 2
    fork = m.fork_asset(aid, {"title": "Forked scene"}, "actor:test")
    fid = fork["asset"]["id"]
    assert fork["asset"]["parentAssetId"] == aid
    cmp = m.compare(aid, fid)
    assert cmp["ok"] is True
    assert cmp["descriptiveOnly"] is True
    lineage = m.lineage(fid)
    assert [x["id"] for x in lineage["ancestorChain"]][:2] == [fid, aid]
    listing = m.list_assets("project:test")
    assert listing["count"] == 2
    archived = m.archive(fid, "actor:test")
    assert archived["asset"]["status"] == "archived"
    assert m.list_assets("project:test")["count"] == 1
