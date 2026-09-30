from app import cross_workspace_research_dependency_graph_v01520 as m


def sample():
    return {"nodes":[
      {"nodeId":"source","nodeType":"source","workspaceId":"library","provenance":{"source":"library"}},
      {"nodeId":"data","nodeType":"dataset","workspaceId":"statistics-econometrics","provenance":{"source":"source"}},
      {"nodeId":"model","nodeType":"ml-model","workspaceId":"neural","provenance":{"source":"data"}},
      {"nodeId":"validation","nodeType":"validation-record","workspaceId":"validation","provenance":{"source":"model"}},
      {"nodeId":"finding","nodeType":"finding","workspaceId":"integrated-lab","provenance":{"source":"validation"}},
      {"nodeId":"figure","nodeType":"figure","workspaceId":"integrated-lab","provenance":{"source":"finding"}},
      {"nodeId":"publication","nodeType":"publication","workspaceId":"publication","provenance":{"source":"figure"}}
    ],"edges":[
      {"edgeId":"e1","sourceRef":"source","targetRef":"data","edgeType":"produces","dependencyClass":"data-lineage","provenance":{"source":"ingest"}},
      {"edgeId":"e2","sourceRef":"data","targetRef":"model","edgeType":"consumes","dependencyClass":"computational","provenance":{"source":"run"}},
      {"edgeId":"e3","sourceRef":"model","targetRef":"validation","edgeType":"validates","dependencyClass":"validation","provenance":{"source":"benchmark"}},
      {"edgeId":"e4","sourceRef":"validation","targetRef":"finding","edgeType":"derives-from","dependencyClass":"methodological","provenance":{"source":"analysis"}},
      {"edgeId":"e5","sourceRef":"finding","targetRef":"figure","edgeType":"visualizes","dependencyClass":"visualization","provenance":{"source":"figure"}},
      {"edgeId":"e6","sourceRef":"figure","targetRef":"publication","edgeType":"publishes","dependencyClass":"publication","provenance":{"source":"pub"}}
    ]}

def test_health_contract_and_policy():
    h=m.health(); assert h["version"]=="0.152.0" and h["crossWorkspaceResearchDependencyGraph"] and h["api_route_count"]==120
    p=m.policy(); assert p["automaticGraphMutation"] is False and p["dependencyEdgeIsCausalProof"] is False and p["humanScientificReviewRequired"] is True

def test_normalized_objects_are_deterministic_and_guarded():
    n=m.normalize_node({"title":"Dataset","nodeType":"dataset"}); assert n["fingerprint"]==m.normalize_node({"title":"Dataset","nodeType":"dataset"})["fingerprint"]
    e=m.normalize_edge({"sourceRef":"a","targetRef":"b","edgeType":"depends-on","dependencyClass":"computational"}); assert e["dependencyEdgeIsCausalProof"] is False and e["dependencyEdgeIsEvidence"] is False

def test_reference_and_provenance_audits():
    p=sample(); assert m.reference_integrity_audit(p)["clean"] is True and m.provenance_audit(p)["complete"] is True
    q=sample(); q["edges"].append({"edgeId":"bad","sourceRef":"missing","targetRef":"model","edgeType":"depends-on","dependencyClass":"computational"}); assert m.reference_integrity_audit(q)["clean"] is False

def test_dependency_traversal_and_paths():
    p=sample(); assert m.direct_dependents({**p,"nodeRef":"data"})["nodeRefs"]==["model"]
    d=m.downstream_closure({**p,"nodeRef":"data"}); assert "publication" in d["nodeRefs"] and d["automaticInvalidation"] is False
    path=m.shortest_dependency_path({**p,"sourceRef":"source","targetRef":"publication"}); assert path["path"][0]=="source" and path["path"][-1]=="publication" and path["shortestPathIsMechanism"] is False

def test_cycle_detection_only_for_computational_dependencies():
    p=sample(); p["edges"].append({"edgeId":"loop","sourceRef":"model","targetRef":"data","edgeType":"depends-on","dependencyClass":"computational"}); x=m.computational_cycle_audit(p); assert x["acyclic"] is False and {"data","model"}.issubset(set(x["cycleCandidateRefs"]))

def test_cross_workspace_and_type_summaries():
    p=sample(); x=m.cross_workspace_edge_summary(p); assert x["count"]>=4 and x["crossWorkspaceEdgeIsScientificIntegrationProof"] is False
    assert m.object_type_summary(p)["counts"]["publication"]==1

def test_change_impact_and_staleness_are_candidates():
    p=sample(); x=m.change_impact({**p,"changedRefs":["data"]}); assert "publication" in x["impactedRefs"] and x["automaticInvalidation"] is False
    s=m.stale_candidate_report({**p,"changedRefs":["data"]}); assert s["records"] and all(r["automaticInvalidation"] is False for r in s["records"])

def test_typed_impact_and_plans_do_not_auto_act():
    p=sample(); assert m.affected_publications({**p,"changedRefs":["data"]})["impactedRefs"]==["publication"]
    assert m.revalidation_plan({**p,"changedRefs":["model"]})["automaticRevalidation"] is False
    assert m.recompute_plan({**p,"changedRefs":["data"]})["automaticRecompute"] is False
    assert m.publication_impact_plan({**p,"changedRefs":["data"]})["automaticRetraction"] is False

def test_snapshot_diff_and_reproducibility():
    p=sample(); a=m.snapshot(p)["snapshot"]; b=m.snapshot(p)["snapshot"]; assert a["fingerprint"]==b["fingerprint"]
    q=sample(); q["nodes"].append({"nodeId":"extra","nodeType":"artifact","workspaceId":"other"}); d=m.dependency_diff({"a":p,"b":q}); assert d["addedNodes"]==["extra"] and d["changeIsScientificInvalidation"] is False
    rp=m.reproducibility_package(p)["package"]; assert rp["reproductionCertified"] is False and rp["scientificValidityCertified"] is False

def test_handoffs_preserve_authorities_and_boundaries():
    for fn in (m.graph_studio_handoff,m.workflow_orchestration_handoff,m.integrated_lab_handoff,m.workspace_execution_handoff,m.workbench_handoff,m.core_handoff,m.library_handoff,m.validation_handoff,m.research_os_handoff,m.publication_handoff):
        h=fn({"graphRef":"g"})["handoff"]; assert h["scientificValidityCertified"] is False and h["automaticMutation"] is False

def test_subgraphs_query_and_explanation():
    p=sample(); q=m.workspace_subgraph({**p,"workspaceId":"validation"}); assert [n["nodeId"] for n in q["nodes"]]==["validation"]
    e=m.explain_dependency({**p,"sourceRef":"data","targetRef":"finding"}); assert e["causalProof"] is False and e["evidenceProof"] is False

def test_release_gates_acceptance_and_boundary():
    assert all(m.release_gates()["gates"].values())
    a=m.acceptance_report(); assert a["accepted"]["crossWorkspaceDependencyGraph"] is True and a["scientificValidityCertified"] is False
    b=m.interpretation_boundary(); assert b["dependencyEdgeIsCausalProof"] is False and b["impactCandidateIsScientificInvalidation"] is False and b["publicationImpactIsRetractionDecision"] is False
