import os, tempfile
import pytest
import sqlite3
from app.cross_project_dependency_research_resource_planning_v01620 import CrossProjectDependencyResearchResourcePlanningManager, CrossProjectResourcePlanningError

class Programs:
    def __init__(self):
        self.program={"id":"program:test","title":"Test program","state":"active","projects":[
            {"projectId":"research:a","status":"active"},{"projectId":"research:b","status":"active"},{"projectId":"research:c","status":"active"}]}
    def get_program(self, program_id):
        if program_id != self.program["id"]: raise ValueError("missing")
        return dict(self.program)

def manager(td): return CrossProjectDependencyResearchResourcePlanningManager(os.path.join(td,"planning.sqlite3"),Programs())

def seed(m):
    r=m.create_resource("program:test",{"resourceId":"resource:gpu","resourceType":"compute-profile","title":"GPU hours","unit":"gpu-hour","capacity":10})["resource"]
    d=m.create_dependency("program:test",{"fromProjectId":"research:a","toProjectId":"research:b","dependencyType":"data","description":"Project B consumes Project A data."})["dependency"]
    q=m.create_requirement("program:test",{"projectId":"research:a","resourceId":r["id"],"quantity":4,"purpose":"Training"})["requirement"]
    return r,d,q

def test_health_and_policy_boundaries():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);h=m.health();p=m.policies();assert h["version"]=="0.162.0";assert h["automaticResourceAllocation"] is False;assert p["automaticScheduling"] is False;assert p["explicitDependenciesOnly"] is True

def test_dependency_requires_two_program_projects():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td)
        with pytest.raises(CrossProjectResourcePlanningError): m.create_dependency("program:test",{"fromProjectId":"research:a","toProjectId":"research:a","description":"bad"})
        with pytest.raises(CrossProjectResourcePlanningError): m.create_dependency("program:test",{"fromProjectId":"research:a","toProjectId":"research:missing","description":"bad"})

def test_dependency_create_and_status():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);d=m.create_dependency("program:test",{"fromProjectId":"research:a","toProjectId":"research:b","dependencyType":"model","description":"Uses model"})["dependency"];assert d["status"]=="planned";d=m.set_dependency_status("program:test",d["id"],{"status":"satisfied"})["dependency"];assert d["status"]=="satisfied"

def test_resource_registry_and_state():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);r=m.create_resource("program:test",{"resourceId":"resource:lab","resourceType":"facility","title":"Lab bay","capacity":2,"unit":"bay"})["resource"];assert r["capacity"]==2;r=m.set_resource_state("program:test",r["id"],{"state":"limited"})["resource"];assert r["state"]=="limited"

def test_requirement_requires_registered_resource_and_member_project():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td)
        with pytest.raises(CrossProjectResourcePlanningError): m.create_requirement("program:test",{"projectId":"research:a","resourceId":"resource:none","purpose":"x"})
        m.create_resource("program:test",{"resourceId":"resource:x","resourceType":"dataset","title":"X","capacity":1})
        with pytest.raises(CrossProjectResourcePlanningError): m.create_requirement("program:test",{"projectId":"research:nope","resourceId":"resource:x","purpose":"x"})

def test_requirement_status_lifecycle_is_explicit():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);r=m.create_resource("program:test",{"resourceId":"resource:x","resourceType":"dataset","title":"X","capacity":1})["resource"];q=m.create_requirement("program:test",{"projectId":"research:a","resourceId":r["id"],"purpose":"Input"})["requirement"];q=m.set_requirement_status("program:test",q["id"],{"status":"acknowledged"})["requirement"];assert q["status"]=="acknowledged"

def test_analysis_detects_declared_capacity_conflict_without_allocating():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);r=m.create_resource("program:test",{"resourceId":"resource:gpu","resourceType":"compute-profile","title":"GPU","capacity":5,"unit":"gpu-hour"})["resource"]
        m.create_requirement("program:test",{"projectId":"research:a","resourceId":r["id"],"quantity":4,"purpose":"A"});m.create_requirement("program:test",{"projectId":"research:b","resourceId":r["id"],"quantity":4,"purpose":"B"})
        a=m.analyze_program("program:test")["analysis"];assert a["capacityConflictCount"]==1;assert a["capacityConflicts"][0]["requestedQuantity"]==8;assert a["automaticResourceAllocation"] is False

def test_analysis_dependency_graph_is_explicit_and_descriptive():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);seed(m);a=m.analyze_program("program:test")["analysis"];assert a["dependencyCount"]==1;assert len(a["dependencyGraph"]["nodes"])==3;assert a["descriptiveOnly"] is True

def test_plan_approval_requires_human_authorization():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);p=m.create_plan("program:test",{"title":"Plan"})["plan"];p=m.transition_plan(p["id"],{"targetState":"review","reason":"Review","humanAuthorization":True})["plan"]
        with pytest.raises(CrossProjectResourcePlanningError):m.transition_plan(p["id"],{"targetState":"approved","reason":"Approve","humanAuthorization":False})

def test_plan_approval_blocks_on_capacity_conflicts():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);r=m.create_resource("program:test",{"resourceId":"resource:gpu","resourceType":"compute-profile","title":"GPU","capacity":1})["resource"];m.create_requirement("program:test",{"projectId":"research:a","resourceId":r["id"],"quantity":2,"purpose":"A"});p=m.create_plan("program:test",{"title":"Plan"})["plan"];m.transition_plan(p["id"],{"targetState":"review","reason":"Review","humanAuthorization":True})
        with pytest.raises(CrossProjectResourcePlanningError):m.transition_plan(p["id"],{"targetState":"approved","reason":"Approve","humanAuthorization":True})

def test_plan_can_be_human_approved_when_procedurally_clear():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);p=m.create_plan("program:test",{"title":"Plan"})["plan"];p=m.transition_plan(p["id"],{"targetState":"review","reason":"Review","humanAuthorization":True})["plan"];p=m.transition_plan(p["id"],{"targetState":"approved","reason":"Approve","humanAuthorization":True})["plan"];assert p["state"]=="approved";assert p["humanAuthorization"] is True

def test_manifest_digest_verification():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);seed(m);x=m.manifest("program:test");assert m.verify_manifest(x)["valid"] is True;x["manifest"]["program"]["state"]="tampered";assert m.verify_manifest(x)["valid"] is False

def test_snapshot_requires_human_authorization_and_is_immutable():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);seed(m)
        with pytest.raises(CrossProjectResourcePlanningError):m.snapshot("program:test",{})
        s=m.snapshot("program:test",{"humanAuthorization":True})["snapshot"];loaded=m.get_snapshot(s["id"])["snapshot"];assert loaded["digest"]==s["digest"];assert loaded["body"]["program"]["id"]=="program:test"

def test_command_center_and_timeline_surface_program_planning():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);seed(m);c=m.command_center("program:test");assert c["program"]["id"]=="program:test";t=m.timeline("program:test");assert t["count"]>=3

def test_connection_context_closes_file_descriptor():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td);db=m._connect();assert db.execute("select 1").fetchone()[0]==1
        with db: pass
        with pytest.raises(sqlite3.ProgrammingError): db.execute("select 1")
