from app import embedding_explorer_v01417 as m

P={
 "studyId":"emb-1","modelRef":"model-a","checkpointRef":"ckpt-20","layerRef":"encoder.11",
 "datasetRef":"ds-a","splitRef":"test-a","environmentRef":"env-a","embeddingKind":"document","distanceMetric":"cosine",
 "embeddings":[
  {"embeddingId":"e1","sourceRef":"doc-1","label":"A","group":"g1","vector":[1,0,0],"provenanceRef":"p1"},
  {"embeddingId":"e2","sourceRef":"doc-2","label":"B","group":"g1","vector":[0.8,0.2,0],"provenanceRef":"p2"},
  {"embeddingId":"e3","sourceRef":"doc-3","label":"C","group":"g2","vector":[0,1,0],"provenanceRef":"p3"},
 ],
 "projections":[{"projectionId":"pca-1","method":"pca","dimensions":2,"points":[
   {"embeddingId":"e1","x":0.1,"y":0.2},{"embeddingId":"e2","x":0.2,"y":0.25},{"embeddingId":"e3","x":1.2,"y":1.1}
 ]}]
}

def test_health_policy():
    h=m.health(); assert h["version"]=="0.141.7" and h["api_route_count"]==33 and h["embeddingExplorer"] is True
    p=m.policy(); assert p["nearestNeighborIsRelationship"] is False and p["projectionFaithfulnessCertified"] is False and p["embeddingIsEvidence"] is False

def test_study_and_handoff():
    s=m.study_spec(P); assert s["readyForWorkspaceHandoff"] is True and s["study"]["distanceMetric"]=="cosine"
    h=m.workspace_handoff(P)["handoff"]; assert h["executionAuthority"]=="workspace" and h["labExecutesEmbeddingExtraction"] is False

def test_normalization_registry_and_provenance():
    r=m.normalize_results(P); assert len(r["results"]["embeddings"])==3 and r["results"]["embeddingIsEvidence"] is False
    g=m.vector_registry(P); assert g["count"]==3 and g["automaticSemanticInterpretation"] is False
    a=m.provenance_audit(P); assert a["allComplete"] is True

def test_dimension_audit_and_distance_matrix():
    a=m.dimensionality_audit(P); assert a["consistent"] is True and a["dimensions"]==[3]
    d=m.distance_matrix(P); assert d["comparable"] is True and len(d["rows"])==3 and d["distanceIsEvidence"] is False

def test_neighborhood_is_not_relationship():
    q=m.neighborhood_query({**P,"targetEmbeddingId":"e1","k":2}); assert len(q["neighbors"])==2
    assert q["nearestNeighborIsRelationship"] is False and q["semanticRelationshipInferred"] is False

def test_projection_registry_audit():
    r=m.projection_registry(P); assert r["count"]==1 and r["projections"][0]["derivedRepresentation"] is True
    a=m.projection_audit(P); assert a["allComplete"] is True and a["projectionFaithfulnessCertified"] is False

def test_cluster_overlay_no_meaning():
    x=m.cluster_overlay({**P,"clusterAssignments":{"e1":"c1","e2":"c1","e3":"c2"}})
    assert len(x["rows"])==3 and x["clusterMeaningInferred"] is False and x["clusterMembershipIsEvidence"] is False

def test_drift_and_space_comparison_are_descriptive():
    before=P["embeddings"]; after=[{**x,"vector":[v+0.01 for v in x["vector"]]} for x in before]
    d=m.drift_comparison({"beforeEmbeddings":before,"afterEmbeddings":after,"distanceMetric":"euclidean"}); assert d["driftCauseInferred"] is False
    c=m.embedding_space_comparison({"left":P,"right":P}); assert c["directlyComparable"] is True and c["automaticSuperiorityJudgment"] is False

def test_visual_and_core_handoff_boundaries():
    v=m.visual_spec({**P,"view":"projection"})["visualSpec"]; assert v["derivedProjection"] is True and v["embeddingIsEvidence"] is False
    h=m.core_visual_handoff(P)["handoff"]; assert h["canonicalVisualObjectAuthority"]=="platform-core" and h["semanticRelationshipInferred"] is False

def test_snapshot_determinism_and_repro_not_certified():
    a=m.snapshot(P)["snapshot"]; b=m.snapshot(P)["snapshot"]; assert a["fingerprint"]==b["fingerprint"] and a["snapshotId"]==b["snapshotId"]
    r=m.reproducibility_packet(P); assert r["reproducibilityCertified"] is False and r["reproducibilityPacket"]["projectionFaithfulnessCertified"] is False
