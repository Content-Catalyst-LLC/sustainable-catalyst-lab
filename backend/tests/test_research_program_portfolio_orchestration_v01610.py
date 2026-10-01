from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.research_program_portfolio_orchestration_v01610 import (
    ResearchProgramPortfolioError,
    ResearchProgramPortfolioOrchestrationManager,
)


class FakeResearchOS:
    def __init__(self):
        self.projects = {
            "research:p1": {"id": "research:p1", "title": "Project One", "stage": "workflow", "updatedAt": "2026-10-01T00:00:00+00:00"},
            "research:p2": {"id": "research:p2", "title": "Project Two", "stage": "review", "updatedAt": "2026-10-01T00:00:00+00:00"},
            "research:p3": {"id": "research:p3", "title": "Project Three", "stage": "publication-package", "updatedAt": "2026-10-01T00:00:00+00:00"},
        }

    def get_project(self, project_id):
        if project_id not in self.projects:
            raise ValueError("missing project")
        return dict(self.projects[project_id])


def manager(tmp_path: Path):
    return ResearchProgramPortfolioOrchestrationManager(str(tmp_path / "rppo.sqlite3"), FakeResearchOS())


def seed_program(mgr):
    mgr.create_program({"programId": "program:test", "title": "Program Test", "purpose": "Coordinate related research."})
    mgr.add_project("program:test", {"projectId": "research:p1", "role": "primary", "workstream": "methods", "contribution": "Primary computational study."})
    mgr.create_objective("program:test", {"objectiveId": "objective:o1", "title": "Objective One", "description": "Complete the first objective."})
    return mgr.get_program("program:test")


def test_health_and_policies_preserve_human_control(tmp_path):
    mgr = manager(tmp_path)
    h = mgr.health()
    p = mgr.policies()
    assert h["version"] == "0.161.0"
    assert h["researchProgramPortfolioOrchestration"] is True
    assert h["descriptiveAggregationOnly"] is True
    assert h["automaticProjectRanking"] is False
    assert h["automaticFundingAllocation"] is False
    assert h["automaticResourceAllocation"] is False
    assert h["automaticScientificValidity"] is False
    assert p["researchOSProjectLifecycleAuthority"] is True
    assert p["workspaceExecutionAuthority"] is True
    assert p["humanAuthorizationRequired"] is True


def test_program_create_list_and_membership_resolves_research_os(tmp_path):
    mgr = manager(tmp_path)
    mgr.create_program({"programId": "program:a", "title": "A", "purpose": "Purpose"})
    out = mgr.add_project("program:a", {"projectId": "research:p1", "role": "supporting", "workstream": "analysis"})
    assert out["program"]["projects"][0]["projectId"] == "research:p1"
    assert out["program"]["projects"][0]["role"] == "supporting"
    listed = mgr.list_programs()
    assert listed["count"] == 1
    assert listed["programs"][0]["state"] == "draft"
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.add_project("program:a", {"projectId": "research:missing", "role": "primary"})


def test_duplicate_membership_rejected_and_status_is_explicit(tmp_path):
    mgr = manager(tmp_path)
    p = seed_program(mgr)
    membership_id = p["projects"][0]["id"]
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.add_project("program:test", {"projectId": "research:p1", "role": "primary"})
    out = mgr.set_project_membership_status("program:test", membership_id, {"status": "withdrawn"})
    assert out["program"]["projects"][0]["status"] == "withdrawn"


def test_objective_allocation_requires_active_program_membership(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    out = mgr.allocate_objective_project("program:test", "objective:o1", {"projectId": "research:p1", "contribution": "Provides primary evidence."})
    assert out["program"]["objectiveProjectAllocations"][0]["projectId"] == "research:p1"
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.allocate_objective_project("program:test", "objective:o1", {"projectId": "research:p2", "contribution": "Not a member."})


def test_objective_and_milestone_statuses_are_human_authored_records(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    obj = mgr.set_objective_status("program:test", "objective:o1", {"status": "active"})
    assert obj["objective"]["status"] == "active"
    milestone = mgr.create_milestone("program:test", {"milestoneId": "milestone:m1", "title": "First milestone", "targetDate": "2026-12-01"})
    assert milestone["milestone"]["status"] == "planned"
    done = mgr.set_milestone_status("program:test", "milestone:m1", {"status": "complete", "evidenceRef": "package:abc"})
    assert done["milestone"]["status"] == "complete"
    assert done["milestone"]["evidenceRef"] == "package:abc"


def test_program_transition_requires_authorization_and_prerequisites(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.transition_program("program:test", {"targetState": "active", "reason": "Begin."})
    active = mgr.transition_program("program:test", {"targetState": "active", "reason": "Human approval.", "humanAuthorization": True})
    assert active["program"]["state"] == "active"
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.transition_program("program:test", {"targetState": "review", "reason": "Review now.", "humanAuthorization": True})
    mgr.set_objective_status("program:test", "objective:o1", {"status": "complete"})
    reviewed = mgr.transition_program("program:test", {"targetState": "review", "reason": "Objective completed.", "humanAuthorization": True})
    assert reviewed["program"]["state"] == "review"


def test_program_completion_is_procedural_not_scientific_validity(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    mgr.create_milestone("program:test", {"milestoneId": "milestone:m1", "title": "Milestone"})
    mgr.transition_program("program:test", {"targetState": "active", "reason": "Start.", "humanAuthorization": True})
    mgr.set_objective_status("program:test", "objective:o1", {"status": "complete"})
    mgr.transition_program("program:test", {"targetState": "review", "reason": "Review.", "humanAuthorization": True})
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.transition_program("program:test", {"targetState": "completed", "reason": "Finish.", "humanAuthorization": True})
    mgr.set_milestone_status("program:test", "milestone:m1", {"status": "complete"})
    out = mgr.transition_program("program:test", {"targetState": "completed", "reason": "Procedural closure.", "humanAuthorization": True})
    assert out["program"]["state"] == "completed"
    evaluation = mgr.evaluate_program("program:test", "completed")
    assert evaluation["proceduralReady"] is True
    assert evaluation["automaticScientificValidity"] is False
    assert evaluation["automaticProjectRanking"] is False


def test_program_command_center_aggregates_without_ranking(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    mgr.add_project("program:test", {"projectId": "research:p2", "role": "validation", "workstream": "review"})
    cc = mgr.program_command_center("program:test")
    assert cc["projectStageCounts"]["workflow"] == 1
    assert cc["projectStageCounts"]["review"] == 1
    assert cc["automaticPrioritization"] is False
    assert cc["automaticFundingAllocation"] is False
    assert cc["automaticResourceAllocation"] is False
    assert "score" not in cc and "ranking" not in cc


def test_program_manifest_snapshot_and_verification_are_digest_bound(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    manifest = mgr.manifest("program", "program:test")
    assert mgr.verify_manifest(manifest)["verified"] is True
    altered = dict(manifest["manifest"])
    altered["entityType"] = "portfolio"
    assert mgr.verify_manifest({"manifest": altered, "digest": manifest["digest"]})["verified"] is False
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.snapshot("program", "program:test", {})
    snap = mgr.snapshot("program", "program:test", {"humanAuthorization": True})
    fetched = mgr.get_snapshot(snap["snapshotId"])
    assert fetched["digest"] == snap["digest"]
    assert fetched["snapshot"]["immutable"] is True


def test_portfolio_membership_and_descriptive_command_center(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    mgr.create_portfolio({"portfolioId": "portfolio:p", "title": "Portfolio", "purpose": "Coordinate programs."})
    out = mgr.add_program_to_portfolio("portfolio:p", {"programId": "program:test", "role": "primary"})
    assert out["portfolio"]["programs"][0]["programId"] == "program:test"
    cc = mgr.portfolio_command_center("portfolio:p")
    assert cc["programStateCounts"]["draft"] == 1
    assert cc["uniqueProjectCount"] == 1
    assert cc["projectStageCounts"]["workflow"] == 1
    assert cc["automaticPrioritization"] is False
    assert cc["automaticFundingAllocation"] is False


def test_portfolio_transition_requires_human_authorization_and_program_state(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    mgr.create_portfolio({"portfolioId": "portfolio:p", "title": "Portfolio", "purpose": "Coordinate programs."})
    mgr.add_program_to_portfolio("portfolio:p", {"programId": "program:test"})
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.transition_portfolio("portfolio:p", {"targetState": "active", "reason": "Start"})
    out = mgr.transition_portfolio("portfolio:p", {"targetState": "active", "reason": "Human start", "humanAuthorization": True})
    assert out["portfolio"]["state"] == "active"
    with pytest.raises(ResearchProgramPortfolioError):
        mgr.transition_portfolio("portfolio:p", {"targetState": "review", "reason": "Review", "humanAuthorization": True})
    mgr.transition_program("program:test", {"targetState": "active", "reason": "Start program", "humanAuthorization": True})
    mgr.set_objective_status("program:test", "objective:o1", {"status": "complete"})
    mgr.transition_program("program:test", {"targetState": "review", "reason": "Review program", "humanAuthorization": True})
    reviewed = mgr.transition_portfolio("portfolio:p", {"targetState": "review", "reason": "Portfolio review", "humanAuthorization": True})
    assert reviewed["portfolio"]["state"] == "review"


def test_portfolio_manifest_and_snapshot_are_supported(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    mgr.create_portfolio({"portfolioId": "portfolio:p", "title": "Portfolio", "purpose": "Coordinate programs."})
    mgr.add_program_to_portfolio("portfolio:p", {"programId": "program:test"})
    manifest = mgr.manifest("portfolio", "portfolio:p")
    assert manifest["manifest"]["entityType"] == "portfolio"
    assert mgr.verify_manifest(manifest)["verified"] is True
    snap = mgr.snapshot("portfolio", "portfolio:p", {"humanAuthorization": True})
    assert snap["snapshot"]["entityType"] == "portfolio"


def test_timeline_preserves_append_only_program_events(tmp_path):
    mgr = manager(tmp_path)
    seed_program(mgr)
    events = mgr.timeline("program", "program:test")["events"]
    kinds = {x["kind"] for x in events}
    assert "program.created" in kinds
    assert "project.membership.added" in kinds
    assert "objective.created" in kinds


def test_sqlite_connection_context_closes_under_repetition(tmp_path):
    mgr = manager(tmp_path)
    for _ in range(200):
        with mgr._connect() as db:
            assert db.execute("SELECT 1").fetchone()[0] == 1
        with pytest.raises(sqlite3.ProgrammingError):
            db.execute("SELECT 1")
