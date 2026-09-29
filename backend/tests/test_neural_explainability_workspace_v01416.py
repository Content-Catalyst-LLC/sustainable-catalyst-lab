from app import neural_explainability_workspace_v01416 as m
P={"studyId":"xai-1","modelRef":"model-a","checkpointRef":"ckpt-10","datasetRef":"ds-a","splitRef":"test-a","targetRef":"class-1","environmentRef":"env-a",
   "methods":[{"methodId":"ig","family":"integrated-gradients","version":"1","scope":"feature","baselinePolicy":{"type":"zero"}},
              {"methodId":"sal","family":"saliency","version":"1","scope":"feature"}],
   "explanations":[
      {"explanationId":"ig-a","method":{"methodId":"ig","family":"integrated-gradients","baselinePolicy":{"type":"zero"}},"inputRef":"row-1","attributions":{"f1":0.3,"f2":-0.2,"f3":0.1},"environmentRef":"env-a","provenanceRef":"prov-1"},
      {"explanationId":"sal-a","method":{"methodId":"sal","family":"saliency"},"inputRef":"row-1","attributions":{"f1":0.2,"f2":-0.1,"f3":0.4},"environmentRef":"env-a","provenanceRef":"prov-2"},
      {"explanationId":"ig-b","method":{"methodId":"ig","family":"integrated-gradients","baselinePolicy":{"type":"zero"}},"inputRef":"row-2","attributions":{"f1":0.28,"f2":-0.18,"f3":0.12},"environmentRef":"env-a","provenanceRef":"prov-3"},
   ]}

def test_health_policy():
    h=m.health(); assert h["version"]=="0.141.6" and h["api_route_count"]==31 and h["labExecutesExplanationCompute"] is False
    p=m.policy(); assert p["causalMechanismInferred"] is False and p["explanationFaithfulnessCertified"] is False and p["automaticModelEndorsement"] is False

def test_study_and_workspace_handoff():
    s=m.study_spec(P); assert s["readyForWorkspaceHandoff"] is True and len(s["study"]["methods"])==2
    h=m.workspace_handoff(P); assert h["handoff"]["executionAuthority"]=="workspace" and h["handoff"]["labExecutesExplanationCompute"] is False

def test_normalization_and_registry():
    r=m.normalize_results(P); assert len(r["results"]["explanations"])==3 and r["results"]["explanationIsEvidence"] is False
    g=m.explanation_registry(P); assert g["count"]==3 and g["automaticRanking"] is False

def test_reference_and_provenance_audits():
    a=m.baseline_reference_audit(P); assert a["allRequiredReferencesDeclared"] is True
    p=m.provenance_audit(P); assert p["allComplete"] is True
    q={**P,"explanations":[{**P["explanations"][0],"environmentRef":""}]}; assert m.provenance_audit(q)["allComplete"] is True  # inherited from study environment

def test_feature_matrix_and_summary():
    x=m.feature_attribution_matrix(P); assert x["matrix"]["features"]==["f1","f2","f3"] and x["matrix"]["automaticImportanceRanking"] is False
    s=m.attribution_summary(P); assert s["descriptiveOnly"] is True and len(s["rows"])==3

def test_method_agreement_is_not_certification():
    x=m.method_agreement(P); assert len(x["rows"])==3 and x["explanationFaithfulnessCertified"] is False
    assert all(r["agreementIsReliabilityCertification"] is False for r in x["rows"])

def test_stability_does_not_certify():
    x=m.stability_audit(P); assert x["stabilityCertified"] is False and any(r["group"]=="ig" for r in x["rows"])

def test_local_comparison_has_no_consensus():
    x=m.local_explanation_comparison({**P,"inputRef":"row-1"}); assert len(x["explanations"])==2 and x["automaticConsensus"] is False

def test_visual_and_core_handoff_boundaries():
    v=m.visual_spec({**P,"view":"method-comparison"})["visualSpec"]; assert v["rawValuesPreserved"] is True and v["causalMechanismInferred"] is False
    h=m.core_visual_handoff(P)["handoff"]; assert h["canonicalVisualObjectAuthority"]=="platform-core" and h["explanationIsEvidence"] is False

def test_snapshot_is_deterministic_and_repro_not_certified():
    a=m.snapshot(P)["snapshot"]; b=m.snapshot(P)["snapshot"]; assert a["fingerprint"]==b["fingerprint"] and a["snapshotId"]==b["snapshotId"]
    r=m.reproducibility_packet(P); assert r["reproducibilityCertified"] is False and r["reproducibilityPacket"]["explanationFaithfulnessCertified"] is False
