from app import integrated_neural_research_workspace_v01420 as m

O=[
 {"objectId":"exp","kind":"experiment","panel":"experiment","ref":"exp:1","sourceVersion":"0.141.0","provenanceRef":"p:exp"},
 {"objectId":"model","kind":"model","panel":"architecture","ref":"model:1","sourceVersion":"0.141.1","experimentRef":"exp:1","provenanceRef":"p:model","dependsOn":["exp"]},
 {"objectId":"run","kind":"run","panel":"telemetry","ref":"run:1","sourceVersion":"0.141.2","experimentRef":"exp:1","modelRef":"model:1","provenanceRef":"p:run","dependsOn":["model"]},
 {"objectId":"cmp","kind":"comparison","panel":"comparison","ref":"cmp:1","sourceVersion":"0.141.3","experimentRef":"exp:1","provenanceRef":"p:cmp","dependsOn":["run"]},
 {"objectId":"search","kind":"search-study","panel":"search","ref":"search:1","sourceVersion":"0.141.4","experimentRef":"exp:1","provenanceRef":"p:search"},
 {"objectId":"abl","kind":"ablation-study","panel":"ablation","ref":"abl:1","sourceVersion":"0.141.5","modelRef":"model:1","provenanceRef":"p:abl"},
 {"objectId":"xai","kind":"explanation","panel":"explainability","ref":"xai:1","sourceVersion":"0.141.6","modelRef":"model:1","provenanceRef":"p:xai"},
 {"objectId":"emb","kind":"embedding","panel":"embeddings","ref":"emb:1","sourceVersion":"0.141.7","modelRef":"model:1","provenanceRef":"p:emb"},
 {"objectId":"pkg","kind":"package","panel":"reproducibility","ref":"pkg:1","sourceVersion":"0.141.8","experimentRef":"exp:1","provenanceRef":"p:pkg","dependsOn":["run"]},
]
P={"sessionId":"s1","projectRef":"project:1","studyRef":"study:1","experimentRef":"exp:1","state":"active","activePanel":"telemetry","focusedObjectId":"run","pinnedObjectIds":["model"],"objects":O,"limitations":["single dataset"],"review":{"status":"in-review"}}

def test_health_policy_catalog():
    h=m.health(); assert h["version"]=="0.142.0" and h["api_route_count"]==39 and h["panelCount"]==9
    p=m.policy(); assert p["workspaceExecutionAuthority"] is True and p["labExecutesTraining"] is False and p["automaticScientificValidity"] is False
    assert m.module_catalog()["panelCount"]==9

def test_session_and_panel_state():
    s=m.normalize_session(P); assert s["activePanel"]=="telemetry" and len(s["objects"])==9
    x=m.panel_state({**P,"panel":"embeddings"}); assert x["objectCount"]==1 and x["objects"][0]["objectId"]=="emb"

def test_lineage_and_links():
    g=m.lineage_graph(P); assert g["complete"] is True and len(g["edges"])>=4 and g["lineageGraphIsCausalGraph"] is False
    f=m.focus_context(P); assert f["focusedObject"]["objectId"]=="run" and any(x["objectId"]=="model" for x in f["linkedObjects"])

def test_readiness_provenance_review():
    r=m.readiness_report(P); assert r["minimumWorkspaceReady"] is True and r["readinessIsScientificValidity"] is False
    p=m.provenance_summary(P); assert p["allObjectsHaveProvenance"] is True and p["provenanceCompletenessIsScientificValidity"] is False
    rv=m.review_state(P); assert rv["review"]["status"]=="in-review" and rv["reviewCompletionIsPublicationAcceptance"] is False

def test_handoff_boundaries():
    w=m.workspace_execution_handoff({**P,"requestedOperation":"train"})["handoff"]; assert w["executionAuthority"]=="workspace" and w["automaticExecution"] is False
    c=m.core_handoff(P)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["automaticCanonicalization"] is False
    ro=m.research_os_handoff(P)["handoff"]; assert ro["automaticPhaseAdvance"] is False
    pk=m.package_handoff(P)["handoff"]; assert pk["reproductionCertified"] is False and pk["replicationCertified"] is False

def test_visual_and_boundaries():
    v=m.visual_workspace_spec(P)["visualSpec"]; assert v["layout"]=="linked-nine-panel-workspace" and v["automaticRanking"] is False
    b=m.interpretation_boundary()["boundaries"]; assert b["embeddingProximityIsRelationship"] is False and b["explanationIsCausalProof"] is False and b["ablationDeltaIsCausalEffect"] is False

def test_snapshot_determinism_and_diff():
    a=m.workspace_snapshot(P)["snapshot"]; b=m.workspace_snapshot(P)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    c=m.compare_snapshots({"left":P,"right":P}); assert c["sameWorkspaceState"] is True
    d=m.workspace_diff({"left":P,"right":P}); assert d["sameWorkspaceContent"] is True

def test_export_repro_not_certification():
    e=m.export_bundle(P); assert e["scientificValidityCertified"] is False
    r=m.reproducibility_summary(P)["summary"]; assert r["reproductionCertified"] is False and r["replicationCertified"] is False
