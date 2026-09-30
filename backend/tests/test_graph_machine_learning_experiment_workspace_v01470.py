from app import graph_machine_learning_experiment_workspace_v01470 as m
STUDY={"studyId":"gml1","projectRef":"p1","title":"Graph ML study","question":"Can candidate links be predicted?","graphStudyRef":"gs1","task":{"taskId":"t1","taskType":"link-prediction"},"dataset":{"datasetId":"d1","graphRef":"g1","nodeFeatureSchema":{"x":"float"},"edgeFeatureSchema":{"w":"float"},"labelProvenance":{"sourceRef":"labels:1"},"featureProvenance":{"sourceRef":"features:1"}},"split":{"splitId":"s1","strategy":"temporal","trainRefs":["e1","e2"],"validationRefs":["e3"],"testRefs":["e4"],"negativeSampling":{"method":"temporal"}},"model":{"modelId":"m1","modelFamily":"graphsage"},"runs":[{"runId":"r1","taskRef":"t1","datasetRef":"d1","splitRef":"s1","modelRef":"m1","metrics":{"mrr":.5}}],"review":{"status":"in-review"},"limitations":["candidate relationships only"]}

def test_health_contract_catalog():
    h=m.health(); assert h["version"]=="0.147.0" and h["api_route_count"]==65 and h["labExecutesGraphMLTraining"] is False and h["predictionIsEvidence"] is False
    c=m.contract(); assert c["predecessorVersion"]=="0.146.0" and "link-prediction" in c["taskTypes"] and "graphsage" in c["modelFamilies"]
    assert m.catalog()["automaticRelationshipEstablishment"] is False

def test_study_normalization_and_candidate_boundary():
    s=m.normalize_study(STUDY); assert s["task"]["taskType"]=="link-prediction" and s["dataset"]["relationshipSemanticsPreserved"] is True
    p=m.normalize_prediction({"taskType":"link-prediction","sourceNodeRef":"a","targetNodeRef":"b","score":.91}); assert p["candidateOnly"] is True and p["relationshipEstablished"] is False and p["evidenceEdgeCreated"] is False

def test_graph_specific_leakage_audits():
    assert m.split_leakage_audit(STUDY["split"])["possibleLeakage"] is False
    leak=m.split_leakage_audit({"trainRefs":["x"],"testRefs":["x"]}); assert leak["possibleLeakage"] is True and leak["leakageCertifiedAbsent"] is False
    neg=m.negative_sampling_audit({"method":"hard-negative","knownPositiveExclusion":True}); assert neg["absenceIsNegativeLabel"] is False and neg["samplingAdequacyCertified"] is False
    assert m.temporal_leakage_audit({"futureInformationRefs":["future:1"]})["possibleTemporalLeakage"] is True

def test_prediction_result_types_keep_epistemic_boundaries():
    lp=m.normalize_link_prediction_result({"candidates":[{"sourceNodeRef":"a","targetNodeRef":"b","score":.8}]}); assert lp["relationshipsEstablished"] is False and lp["candidates"][0]["candidateOnly"] is True
    assert m.normalize_node_classification_result({"rows":[]})["predictionIsEvidence"] is False
    assert m.normalize_anomaly_result({"rows":[]})["predictionIsEvidence"] is False
    assert m.normalize_embedding_result({"rows":[]})["embeddingProximityIsRelationship"] is False

def test_metrics_calibration_and_comparison_no_winner():
    assert m.threshold_sweep({"rows":[]})["automaticThresholdSelection"] is False
    assert m.calibration_summary({"ece":.03})["calibrationCertified"] is False
    assert m.model_comparison_matrix({"modelRefs":["m1","m2"],"rows":[]})["automaticWinnerSelection"] is False
    assert m.ranking_metrics({"mrr":.5})["rankingMetricIsEvidence"] is False

def test_explainability_and_fairness_boundaries():
    x=m.normalize_gnn_explanation({"method":"gnnexplainer","targetRef":"n1"}); assert x["explanationIsCausalProof"] is False and x["explanationFaithfulnessCertified"] is False
    assert m.fairness_audit({"groups":["a","b"]})["automaticPolicyConclusion"] is False
    assert m.out_of_distribution_audit({"shiftTests":[]})["generalizationCertified"] is False

def test_authority_handoffs():
    w=m.workspace_execution_handoff({"study":STUDY,"requestedOperation":"link-prediction-train"})["handoff"]; assert w["executionAuthority"]=="workspace" and w["labExecutesGraphMLTraining"] is False
    wb=m.workbench_handoff({"study":STUDY,"requestedPrototype":"gnn-prototype"})["handoff"]; assert wb["executionAuthority"]=="workbench"
    c=m.core_handoff(STUDY)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["candidatePredictionsRemainCandidates"] is True and c["automaticRelationshipEstablishment"] is False
    assert m.research_os_handoff(STUDY)["handoff"]["automaticPhaseAdvance"] is False

def test_snapshot_reproducibility_publication():
    a=m.workspace_snapshot(STUDY)["snapshot"]; b=m.workspace_snapshot(STUDY)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    assert m.compare_snapshots({"left":STUDY,"right":STUDY})["sameWorkspaceState"] is True
    assert m.export_bundle(STUDY)["scientificValidityCertified"] is False
    p=m.reproducibility_package(STUDY)["package"]; assert p["reproductionCertified"] is False and p["replicationCertified"] is False
    assert m.publication_handoff(STUDY)["handoff"]["publicationAccepted"] is False

def test_interpretation_boundaries():
    b=m.interpretation_boundary()["boundaries"]
    assert b["predictionIsEvidence"] is False and b["candidateLinkIsEstablishedRelationship"] is False and b["embeddingProximityIsRelationship"] is False and b["performanceIsScientificValidity"] is False
