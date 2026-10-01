import json
import tempfile
from pathlib import Path
import pytest
from app.scientific_reproduction_independent_replication_network_v01580 import ScientificReproductionIndependentReplicationNetworkManager, ReplicationNetworkError

class CrossStub:
    def __init__(self): self.studies={"study:anchor":{"study":{"id":"study:anchor","projectId":"project:test"}},"study:rep":{"study":{"id":"study:rep","projectId":"project:test"}}}; self.workspaces={"workspace:meta":{"workspace":{"id":"workspace:meta","projectId":"project:test"}}}
    def get_study(self,i,*a):
        if i not in self.studies: raise ValueError("missing")
        return self.studies[i]
    def get_workspace(self,i,*a):
        if i not in self.workspaces: raise ValueError("missing")
        return self.workspaces[i]

def mgr(tmp): return ScientificReproductionIndependentReplicationNetworkManager(str(Path(tmp)/"rn.sqlite3"),CrossStub(),None,None,True)

def node_payload(name="Independent Lab"):
    return {"name":name,"nodeType":"laboratory","independenceDeclared":True,"independenceEvidence":"Separate team, analysis and funding disclosure.","capabilityRefs":["workspace:python"]}

def network_payload():
    return {"title":"Independent replication network","researchQuestion":"Can the anchor result be independently reproduced?","anchorStudyId":"study:anchor","metaExperimentId":"workspace:meta","protocolRef":"protocol:anchor"}

def plan_payload(node):
    return {"title":"Direct replication plan","sourceStudyId":"study:anchor","nodeId":node,"protocolRef":"protocol:anchor:r1","preregistrationRef":"registry:pre-001","plannedMetrics":["primary"],"samplePlan":"Match declared sample design.","deviationPolicy":"Record all deviations before interpretation."}

def test_health_and_boundaries():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); h=m.health(); assert h["version"]=="0.158.0"; assert h["scientificReproductionIndependentReplicationNetwork"] is True; assert h["independenceInferred"] is False; assert h["automaticReplicationJudgment"] is False; assert h["credentialsStored"] is False

def test_independence_evidence_required():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t)
        with pytest.raises(ReplicationNetworkError): m.create_node("project:test",{"name":"Lab","independenceDeclared":True})

def test_network_membership_and_freeze():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]
        m.add_node(net["id"],{"nodeId":n["id"],"role":"replication-site"}); frozen=m.freeze_network(net["id"])["network"]; assert frozen["status"]=="frozen"; assert frozen["members"][0]["nodeId"]==n["id"]

def test_plan_is_immutable_spec_and_handoff_is_explicit():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]; m.add_node(net["id"],{"nodeId":n["id"]}); p=m.create_plan(net["id"],plan_payload(n["id"]))["plan"]
        assert p["immutable"] is True; hand=m.execution_handoff(p["id"])["handoff"]; assert hand["automaticDispatch"] is False; assert hand["requiresExplicitUserAction"] is True; assert hand["targetProduct"]=="sustainable-catalyst-workspace"

def test_result_links_cross_study_record_without_auto_judgment():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]; m.add_node(net["id"],{"nodeId":n["id"]}); p=m.create_plan(net["id"],plan_payload(n["id"]))["plan"]
        r=m.record_result(p["id"],{"replicationStudyId":"study:rep","state":"completed","resultRefs":["artifact:1"],"deviations":"None declared."})["result"]; assert r["automaticReplicationJudgment"] is False; assert m.get_plan(p["id"])["status"]=="completed"

def test_human_review_states_are_explicit():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]; m.add_node(net["id"],{"nodeId":n["id"]}); p=m.create_plan(net["id"],plan_payload(n["id"]))["plan"]
        review=m.record_review(net["id"],{"planId":p["id"],"state":"mixed","rationale":"Direction agrees; magnitude differs.","reviewerRef":"person:reviewer"})["review"]; assert review["humanAuthored"] is True; assert review["state"]=="mixed"

def test_coverage_is_descriptive_and_reports_independence_declarations():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]; m.add_node(net["id"],{"nodeId":n["id"]}); p=m.create_plan(net["id"],plan_payload(n["id"]))["plan"]; m.record_result(p["id"],{"replicationStudyId":"study:rep","state":"completed"}); c=m.coverage(net["id"]); assert c["completionFraction"]==1.0; assert c["independenceCoverageFraction"]==1.0; assert c["interpretation"]=="descriptive-only"

def test_manifest_digest_detects_tampering():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]; m.add_node(net["id"],{"nodeId":n["id"]}); p=m.create_plan(net["id"],plan_payload(n["id"]))["plan"]
        bundle=m.manifest(net["id"]); assert m.verify_manifest(bundle)["verified"] is True; bad=json.loads(json.dumps(bundle)); bad["manifest"]["network"]["title"]="tampered"; assert m.verify_manifest(bad)["verified"] is False

def test_archived_network_retains_records():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:test",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]; m.add_node(net["id"],{"nodeId":n["id"]}); m.archive_network(net["id"]); assert m.get_network(net["id"])["status"]=="archived"

def test_cross_project_node_link_is_rejected():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); n=m.create_node("project:other",node_payload())["node"]; net=m.create_network("project:test",network_payload())["network"]
        with pytest.raises(ReplicationNetworkError): m.add_node(net["id"],{"nodeId":n["id"]})
