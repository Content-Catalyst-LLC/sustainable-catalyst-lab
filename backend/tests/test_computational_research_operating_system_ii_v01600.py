import tempfile
from pathlib import Path

import pytest

from app.computational_research_operating_system_ii_v01600 import (
    ComputationalResearchOperatingSystemIIManager,
    ResearchOSError,
)


class DummyBatch:
    def get(self, ref, *args, **kwargs):
        if ref == "campaign:missing":
            raise ValueError("missing")
        return {"id": ref, "status": "planned"}


class DummyCross:
    def get_workspace(self, ref):
        if ref == "workspace:missing":
            raise ValueError("missing")
        return {"id": ref, "status": "frozen"}


class DummyNetwork:
    def get_network(self, ref):
        if ref == "network:missing":
            raise ValueError("missing")
        return {"id": ref, "status": "frozen"}


class DummyReview:
    def get_dossier(self, ref):
        if ref == "review:blocked":
            return {"id": ref, "status": "under-review"}
        if ref == "review:missing":
            raise ValueError("missing")
        return {"id": ref, "status": "publication-ready"}

    def publication_packet(self, ref):
        dossier = self.get_dossier(ref)
        if dossier["status"] != "publication-ready":
            raise ValueError("not ready")
        return {"ok": True, "packet": {"dossierId": ref, "automaticPublication": False}}


def manager(tmpdir):
    return ComputationalResearchOperatingSystemIIManager(
        str(Path(tmpdir) / "research-os.sqlite3"),
        DummyBatch(),
        DummyCross(),
        DummyNetwork(),
        DummyReview(),
        True,
    )


def make_project(m, pid="research:test"):
    return m.create_project({"projectId": pid, "title": "Test research", "question": "What changes?", "objective": "Reproducible answer."})["project"]


def link(m, pid, kind, ref, **extra):
    payload = {"objectType": kind, "objectRef": ref, "sourceLayer": "test", "role": "primary"}
    payload.update(extra)
    return m.link_object(pid, payload)["object"]


def advance(m, pid, target):
    return m.transition(pid, {"targetStage": target, "reason": f"Advance to {target}", "humanAuthorization": True})


def test_health_and_policies_are_human_controlled():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t)
        h = m.health()
        p = m.policies()
        assert h["version"] == "0.160.0"
        assert h["computationalResearchOperatingSystemII"] is True
        assert h["automaticStageAdvancement"] is False
        assert h["automaticExecution"] is False
        assert h["automaticScientificValidity"] is False
        assert p["workspaceExecutionAuthority"] is True
        assert p["platformCoreCanonicalAuthority"] is True
        assert p["humanAuthorizationRequired"] is True


def test_project_starts_at_question_and_lists():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t)
        p = make_project(m)
        assert p["stage"] == "question"
        listed = m.list_projects()
        assert listed["count"] == 1
        assert listed["projects"][0]["id"] == p["id"]


def test_transition_requires_human_authorization():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m); link(m, "research:test", "protocol", "protocol:r1")
        with pytest.raises(ResearchOSError, match="humanAuthorization"):
            m.transition("research:test", {"targetStage": "protocol", "reason": "No auth"})


def test_stage_prerequisites_block_missing_objects():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m)
        v = m.validate_project("research:test", "protocol")
        assert v["proceduralReady"] is False
        assert v["blockingReasons"][0]["type"] == "missing-object"
        with pytest.raises(ResearchOSError, match="prerequisites"):
            advance(m, "research:test", "protocol")


def test_reference_resolution_for_governed_upstream_objects():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m)
        with pytest.raises(ResearchOSError, match="could not be resolved"):
            link(m, "research:test", "replication-network", "network:missing")
        assert link(m, "research:test", "cross-study-workspace", "workspace:ok")["status"] == "active"
        assert link(m, "research:test", "replication-network", "network:ok")["status"] == "active"
        assert link(m, "research:test", "review-dossier", "review:ready")["status"] == "active"


def test_digest_mismatch_marks_stale_and_blocks_validation():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m)
        obj = link(m, "research:test", "protocol", "protocol:r1", expectedDigest="aaa", observedDigest="bbb")
        assert obj["status"] == "stale"
        v = m.validate_project("research:test", "protocol")
        assert any(x["type"] == "stale-object" for x in v["blockingReasons"])
        updated = m.observe_object("research:test", obj["id"], {"observedDigest": "aaa"})["object"]
        assert updated["status"] == "active"
        assert m.validate_project("research:test", "protocol")["proceduralReady"] is True


def test_duplicate_link_is_rejected():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m)
        link(m, "research:test", "protocol", "protocol:r1")
        with pytest.raises(ResearchOSError, match="already linked"):
            link(m, "research:test", "protocol", "protocol:r1")


def test_lifecycle_cannot_skip_stages():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m); link(m, "research:test", "protocol", "protocol:r1")
        with pytest.raises(ResearchOSError, match="one stage at a time"):
            m.transition("research:test", {"targetStage": "workflow", "reason": "skip", "humanAuthorization": True})


def build_publication_ready_project(m, pid="research:test"):
    make_project(m, pid)
    link(m, pid, "protocol", "protocol:r1"); advance(m, pid, "protocol")
    link(m, pid, "notebook", "notebook:r1"); advance(m, pid, "notebook")
    link(m, pid, "workflow", "workflow:r1"); advance(m, pid, "workflow")
    link(m, pid, "campaign", "campaign:r1"); advance(m, pid, "campaign")
    advance(m, pid, "compute")
    link(m, pid, "result", "result:r1"); advance(m, pid, "results")
    link(m, pid, "cross-study-workspace", "workspace:r1"); advance(m, pid, "synthesis")
    link(m, pid, "replication-network", "network:r1"); advance(m, pid, "replication")
    link(m, pid, "review-dossier", "review:ready"); advance(m, pid, "review")
    advance(m, pid, "publication-package")
    return m.get_project(pid)


def test_full_lifecycle_reaches_publication_package_without_auto_execution():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t)
        p = build_publication_ready_project(m)
        assert p["stage"] == "publication-package"
        c = m.command_center(p["id"])
        assert c["automaticActionsTaken"] == 0
        assert c["humanControl"] is True


def test_publication_package_requires_review_gate_ready():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m)
        link(m, "research:test", "review-dossier", "review:blocked")
        v = m.validate_project("research:test", "publication-package")
        assert any(x["type"] == "review-gate" for x in v["blockingReasons"])
        assert v["reviewDossierStatus"] == "under-review"


def test_package_and_handoff_are_explicit_and_non_executing():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); build_publication_ready_project(m)
        with pytest.raises(ResearchOSError, match="humanAuthorization"):
            m.compose_package("research:test", {})
        pkg = m.compose_package("research:test", {"humanAuthorization": True})
        assert pkg["package"]["automaticPublication"] is False
        assert pkg["package"]["embeddedRestrictedData"] is False
        with pytest.raises(ResearchOSError, match="humanAuthorization"):
            m.prepare_handoff(pkg["packageId"], {"targetProduct": "publisher"})
        h = m.prepare_handoff(pkg["packageId"], {"targetProduct": "publisher", "humanAuthorization": True})["handoff"]
        assert h["executionRequested"] is False
        assert h["publicationRequested"] is False
        assert h["requiresExplicitUserAction"] is True


def test_manifest_digest_verification_and_timeline():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); build_publication_ready_project(m)
        pkg = m.compose_package("research:test", {"humanAuthorization": True})
        got = m.get_package(pkg["packageId"])
        assert got["digest"] == pkg["digest"]
        manifest = m.manifest("research:test")
        assert m.verify_manifest(manifest)["verified"] is True
        tampered = dict(manifest["manifest"]); tampered["version"] = "tampered"
        assert m.verify_manifest({"manifest": tampered, "digest": manifest["digest"]})["verified"] is False
        assert len(m.timeline("research:test")["events"]) > 5


def test_archive_is_explicit_terminal_state():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t); make_project(m)
        out = m.archive("research:test", reason="Study closed.")
        assert out["project"]["stage"] == "archived"
        with pytest.raises(ResearchOSError, match="Archived"):
            link(m, "research:test", "protocol", "protocol:r1")


def test_sqlite_context_connection_closes():
    with tempfile.TemporaryDirectory() as t:
        m = manager(t)
        db = m._connect()
        with db:
            db.execute("SELECT 1")
        with pytest.raises(Exception):
            db.execute("SELECT 1")
