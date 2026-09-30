from app import multimodal_scientific_experiment_workspace_v01480 as m

STUDY={"studyId":"mm-1","title":"multimodal test","taskType":"cross-modal-matching","samples":[{"sampleId":"s1","sources":[{"sourceId":"t1","modality":"text","contentHash":"abc","provenance":{"source":"paper"}},{"sourceId":"i1","modality":"image","contentHash":"def","provenance":{"source":"microscope"}}]}],"alignments":[{"alignmentId":"a1","alignmentType":"text-image","sourceRefs":["t1"],"targetRefs":["i1"],"confidence":0.9}],"model":{"modelId":"m1","modelFamily":"vision-language","fusionStrategy":"cross-attention"},"runs":[{"runId":"r1","modelRef":"m1","metrics":{"accuracy":0.8}}],"outputs":[{"outputId":"o1","taskType":"cross-modal-matching","sampleRef":"s1","score":0.91}]}

def test_health_policy_contract_catalog():
    h=m.health(); assert h["version"]=="0.148.0" and h["api_route_count"]==73 and h["labExecutesMultimodalTraining"] is False and h["predictionIsEvidence"] is False
    p=m.policy()["policy"]; assert p["originalSourcesPreserved"] is True and p["automaticSemanticEquivalence"] is False
    assert m.contract()["predecessorVersion"]=="0.147.0" and "microscopy" in m.catalog()["modalities"]

def test_normalization_preserves_sources_and_boundaries():
    s=m.normalize_study(STUDY); assert s["samples"][0]["sources"][0]["originalSourcePreserved"] is True
    assert s["alignments"][0]["semanticEquivalenceEstablished"] is False and s["outputs"][0]["predictionIsEvidence"] is False
    assert s["fingerprint"]==m.normalize_study(STUDY)["fingerprint"]

def test_provenance_missingness_and_alignment_audits():
    a=m.modality_provenance_audit(STUDY); assert len(a["rows"])==2 and a["provenanceCertifiedComplete"] is True
    assert m.missing_modality_audit({"study":STUDY})["silentTruthImputationAllowed"] is False
    assert m.temporal_alignment_audit({"pairs":[]})["temporalAlignmentCertified"] is False
    assert m.spatial_alignment_audit({"pairs":[]})["spatialAlignmentCertified"] is False

def test_leakage_fusion_similarity_boundaries():
    assert m.leakage_audit({})["leakageCertifiedAbsent"] is False
    assert m.fusion_audit({"fusionStrategy":"cross-attention"})["fusionInterpretationCertified"] is False
    c=m.cross_modal_similarity_audit({"similarities":[0.9]}); assert c["semanticEquivalenceEstablished"] is False and c["similarityIsEvidence"] is False

def test_result_objects_are_not_truth():
    assert m.normalize_retrieval_result({})["retrievalRankIsEvidence"] is False
    assert m.normalize_matching_result({})["matchEstablishesIdentity"] is False
    assert m.normalize_captioning_result({})["generatedCaptionIsSourceTruth"] is False
    assert m.normalize_anomaly_result({})["anomalyScoreIsProof"] is False
    assert m.normalize_embedding_result({})["embeddingProximityIsRelationship"] is False
    assert m.normalize_explanation({})["explanationIsCausalProof"] is False

def test_comparisons_and_ablation_do_not_rank_or_causalize():
    assert m.modality_ablation_matrix({"modalities":["text","image"],"rows":[]})["ablationDeltaIsCausalEffect"] is False
    assert m.fusion_comparison_matrix({"strategies":["early","late"]})["automaticWinnerSelection"] is False
    assert m.cross_modal_similarity_matrix({})["semanticEquivalenceEstablished"] is False
    assert m.model_comparison_matrix({})["automaticRanking"] is False

def test_visual_and_provenance_contracts():
    v=m.visual_specification({}); assert v["visual"]["alignmentUncertaintyVisible"] is True and v["visual"]["missingModalitiesVisible"] is True
    assert m.sample_inspector_spec({})["visual"]["derivedRepresentationsLabeled"] is True
    g=m.provenance_graph(STUDY); assert g["automaticSemanticEquivalence"] is False and len(g["nodes"])>=5

def test_handoffs_preserve_authorities():
    w=m.workspace_execution_handoff({"study":STUDY,"requestedOperation":"multimodal-train"})["handoff"]; assert w["executionAuthority"]=="workspace" and w["labExecutesMultimodalTraining"] is False
    assert m.workbench_handoff({"study":STUDY})["handoff"]["executionAuthority"]=="workbench"
    c=m.core_handoff(STUDY)["handoff"]; assert c["canonicalObjectAuthority"]=="platform-core" and c["automaticSemanticEquivalence"] is False
    assert m.research_os_handoff(STUDY)["handoff"]["automaticPhaseAdvance"] is False
    assert m.integrated_neural_handoff(STUDY)["handoff"]["automaticModelPromotion"] is False

def test_snapshot_export_reproducibility_publication():
    a=m.workspace_snapshot(STUDY)["snapshot"]; b=m.workspace_snapshot(STUDY)["snapshot"]; assert a["snapshotFingerprint"]==b["snapshotFingerprint"]
    assert m.compare_snapshots({"left":STUDY,"right":STUDY})["sameWorkspaceState"] is True
    assert m.export_bundle(STUDY)["scientificValidityCertified"] is False
    p=m.reproducibility_package(STUDY)["package"]; assert p["reproductionCertified"] is False and p["replicationCertified"] is False
    assert m.publication_handoff(STUDY)["handoff"]["publicationAccepted"] is False

def test_interpretation_boundaries_and_views():
    b=m.interpretation_boundary()["boundaries"]; assert b["crossModalSimilarityIsEvidence"] is False and b["alignmentIsSemanticEquivalence"] is False and b["generatedCaptionIsSourceTruth"] is False
    assert m.default_study_view()["view"]["missingModalitiesVisible"] is True
    assert m.default_analysis_view()["view"]["automaticWinnerSelection"] is False
    assert m.default_missingness_view()["view"]["silentTruthImputationAllowed"] is False
