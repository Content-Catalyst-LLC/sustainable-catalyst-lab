from app import graph_network_science_research_workspace_v01460 as m
GRAPH={"graphId":"g1","title":"Research network","networkType":"directed","directed":True,"nodes":[{"nodeId":"a","label":"A","sourceRef":"src:a"},{"nodeId":"b","label":"B","sourceRef":"src:b"},{"nodeId":"c","label":"C","sourceRef":"src:c"}],"edges":[{"edgeId":"e1","source":"a","target":"b","semantics":"citation","sourceRef":"src:e1"},{"edgeId":"e2","source":"b","target":"c","semantics":"candidate","sourceRef":"src:e2"}],"limitations":["sample network"]}
STUDY={"studyId":"s1","projectRef":"p1","title":"Network study","question":"How is the network structured?","state":"analysis","analysisFamily":"structure","graph":GRAPH,"review":{"status":"in-review"},"limitations":["observational structure only"]}

def test_health_contract_catalog():
    h=m.health(); assert h["version"]=="0.146.0" and h["api_route_count"]==61 and h["labExecutesLargeGraphAlgorithms"] is False and h["graphMetricIsEvidence"] is False
    c=m.contract(); assert c["predecessorVersion"]=="0.145.0" and "temporal" in c["networkTypes"] and "candidate" in c["edgeSemantics"]
    assert m.network_catalog()["automaticRelationshipInference"] is False

def test_objects_preserve_relationship_semantics():
    g=m.normalize_graph(GRAPH); assert g["nodeCount"]==3 and g["edgeCount"]==2 and g["scientificValidityCertified"] is False
    cand=[e for e in g["edges"] if e["edgeId"]=="e2"][0]; assert cand["candidateOnly"] is True and cand["relationshipEstablished"] is False
    obs=[e for e in g["edges"] if e["edgeId"]=="e1"][0]; assert obs["semantics"]=="citation"

def test_schema_provenance_and_semantics_audits():
    assert m.schema_audit(GRAPH)["clean"] is True
    assert m.provenance_audit(GRAPH)["complete"] is True
    a=m.relationship_semantics_audit(GRAPH); assert a["semanticsCounts"]["candidate"]==1 and a["similarityIsRelationship"] is False

def test_structural_summaries_do_not_infer_importance_or_causality():
    d=m.degree_summary(GRAPH); assert len(d["rows"])==3 and d["automaticImportanceInference"] is False
    den=m.density_summary(GRAPH); assert den["density"]==2/6 and den["densityIsEvidence"] is False
    con=m.connectivity_summary(GRAPH); assert con["componentCount"]==1 and con["connectivityIsCausalEvidence"] is False

def test_community_and_centrality_boundaries():
    c=m.centrality_summary({"method":"pagerank","rows":[{"nodeRef":"a","value":.4},{"nodeRef":"b","value":.6}]}); assert c["automaticImportanceRanking"] is False and c["centralityIsSubstantiveImportance"] is False
    q=m.community_summary({"method":"leiden","assignments":{"a":1,"b":1,"c":2},"modularity":.3}); assert q["communityCount"]==2 and q["communityIsGroundTruthGroup"] is False

def test_temporal_multilayer_and_null_model_boundaries():
    t=m.temporal_network_summary({"slices":[{"id":"t1"}],"turnover":{"edge":.2}}); assert t["temporalOrderIsCausality"] is False
    ml=m.multilayer_summary({"layers":[{"id":"l1"},{"id":"l2"}]}); assert ml["crossLayerEquivalenceInferred"] is False
    n=m.null_model_audit({"nullModel":"configuration","preservedProperties":["degree"],"randomizationCount":1000}); assert n["nullModelAdequacyCertified"] is False and n["pValueIsMechanism"] is False

def test_network_comparison_no_auto_winner():
    c=m.network_comparison({"leftRef":"g1","rightRef":"g2","metrics":{"density":[.1,.2]}}); assert c["automaticWinnerSelection"] is False
    mm=m.metric_matrix({"networkRefs":["g1","g2"],"metricKeys":["density"],"rows":[]}); assert mm["automaticRanking"] is False

def test_authority_handoffs():
    w=m.workspace_execution_handoff({"study":STUDY,"requestedOperation":"community-detection"})["handoff"]; assert w["executionAuthority"]=="workspace" and w["automaticExecution"] is False and w["labExecutesLargeGraphAlgorithms"] is False
    wb=m.workbench_handoff({"study":STUDY,"requestedPrototype":"layout-prototype"})["handoff"]; assert wb["executionAuthority"]=="workbench"
    c=m.core_handoff(STUDY)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["automaticCanonicalization"] is False
    r=m.research_os_handoff(STUDY)["handoff"]; assert r["automaticPhaseAdvance"] is False

def test_snapshot_reproducibility_publication():
    a=m.workspace_snapshot(STUDY)["snapshot"]; b=m.workspace_snapshot(STUDY)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    assert m.compare_snapshots({"left":STUDY,"right":STUDY})["sameWorkspaceState"] is True
    assert m.export_bundle(STUDY)["scientificValidityCertified"] is False
    p=m.reproducibility_package(STUDY)["package"]; assert p["reproductionCertified"] is False and p["replicationCertified"] is False
    ph=m.publication_handoff(STUDY)["handoff"]; assert ph["publicationAccepted"] is False

def test_interpretation_boundaries():
    b=m.interpretation_boundary()["boundaries"]
    assert b["connectivityIsCausality"] is False and b["communityIsGroundTruthGroup"] is False and b["similarityIsEstablishedRelationship"] is False and b["graphMetricIsEvidence"] is False
