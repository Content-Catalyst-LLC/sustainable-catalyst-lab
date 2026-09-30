from app import integrated_computational_research_laboratory_v01500 as m

def test_health_policy_and_registry():
    h=m.health(); assert h["version"]=="0.150.0" and h["integratedComputationalResearchLaboratory"] and h["api_route_count"]==86 and h["workspaceCount"]==8
    p=m.policy(); assert p["labExecutesHeavyCompute"] is False and p["automaticScientificValidity"] is False and p["humanScientificReviewRequired"] is True

def test_session_and_project_determinism():
    p={"title":"x","projectRef":"p1","activeWorkspace":"simulation"}; a=m.normalize_session(p); b=m.normalize_session(p); assert a["fingerprint"]==b["fingerprint"] and a["automaticWorkflowAdvance"] is False
    q=m.normalize_project({"title":"project","researchQuestion":"rq"}); assert q["scientificValidityCertified"] is False

def test_workspace_registry_versions():
    r=m.workspace_registry(); assert [x["version"] for x in r["workspaces"]]==["0.142.0","0.143.0","0.144.0","0.145.0","0.146.0","0.147.0","0.148.0","0.149.0"]

def test_object_index_and_lineage_boundaries():
    idx=m.object_index({"objects":[{"ref":"a","kind":"result","workspaceId":"simulation","derived":True},{"ref":"b","kind":"source","workspaceId":"linguistics"}]}); assert idx["count"]==2 and idx["byWorkspace"]["simulation"]==1
    g=m.lineage_graph({"nodes":[{"id":"a"}],"edges":[{"source":"a","target":"b"}]}); assert g["lineageIsCausalProof"] is False

def test_cross_workspace_link_and_navigation_boundaries():
    x=m.cross_workspace_links({"links":[{"from":"a","to":"b","type":"derived-from"}]}); assert x["crossWorkspaceLinkIsEvidence"] is False and x["semanticEquivalenceInferred"] is False
    n=m.navigation_plan({"currentWorkspace":"neural","nextWorkspace":"validation"}); assert n["automaticWorkflowAdvance"] is False and n["humanChoiceRequired"] is True

def test_readiness_missingness_and_provenance():
    r=m.readiness_report({"requirements":[{"name":"data","satisfied":True},{"name":"review","satisfied":False}]}); assert r["ready"] is False and len(r["missing"])==1
    p=m.provenance_summary({"items":[{"provenance":{"source":"x"}},{}]}); assert p["missingProvenance"]==1 and p["provenanceCompletenessIsValidity"] is False

def test_evidence_and_scientific_boundary_audits():
    a=m.evidence_boundary_audit({"items":[{"ref":"model-output","derived":True,"evidenceStatus":"fact"}]}); assert a["clean"] is False and a["derivedOutputAutomaticallyBecomesEvidence"] is False
    b=m.scientific_boundary_audit({}); assert all(v is False for v in b["boundaries"].values())

def test_handoffs_do_not_certify_validity():
    fns=(m.workspace_execution_handoff,m.workbench_handoff,m.core_handoff,m.library_handoff,m.research_os_handoff,m.neural_handoff,m.linguistics_handoff,m.statistics_handoff,m.simulation_handoff,m.graph_handoff,m.graph_ml_handoff,m.multimodal_handoff,m.validation_handoff)
    for fn in fns:
        h=fn({"sessionRef":"s1","objectRefs":["o1"]})["handoff"]; assert h["scientificValidityCertified"] is False and h["deploymentReadinessCertified"] is False and h["publicationAccepted"] is False

def test_snapshot_diff_and_reproducibility():
    p={"session":{"title":"s"},"project":{"title":"p"}}; a=m.workspace_snapshot(p)["snapshot"]; b=m.workspace_snapshot(p)["snapshot"]; assert a["fingerprint"]==b["fingerprint"]
    d=m.workspace_diff({"a":{"x":1},"b":{"x":2}}); assert d["changeCount"]==1
    rp=m.reproducibility_package({"sessionRef":"s1"})["package"]; assert rp["reproductionCertified"] is False and rp["scientificValidityCertified"] is False

def test_panel_views_preserve_specialized_workspace_versions():
    assert m.panel_view("graph-ml")["workspaceVersion"]=="0.147.0" and m.panel_view("validation")["workspaceVersion"]=="0.149.0"

def test_release_gates_and_acceptance():
    assert all(m.release_gates()["gates"].values()); a=m.acceptance_report(); assert a["accepted"]["integratedLaboratoryShell"] is True and a["scientificValidityCertified"] is False and a["publicationAccepted"] is False
