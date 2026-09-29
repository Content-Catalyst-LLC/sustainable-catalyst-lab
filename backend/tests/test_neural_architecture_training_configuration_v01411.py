from app import neural_architecture_training_configuration_v01411 as m

PAYLOAD={
 "experimentId":"exp-1411",
 "architecture":{"title":"Tiny classifier","family":"mlp","inputSignature":{"shape":[32]},"outputSignature":{"shape":[3]},"layers":[{"id":"input","type":"input"},{"id":"dense1","type":"dense","parameters":{"units":64},"activation":"relu"},{"id":"out","type":"dense","parameters":{"units":3}}],"edges":[{"source":"input","target":"dense1"},{"source":"dense1","target":"out"}],"declaredParameterCount":2307},
 "trainingConfiguration":{"epochs":10,"batchSize":32,"seed":42,"optimizer":{"name":"adamw","learningRate":0.001},"loss":{"name":"cross-entropy"},"scheduler":{"name":"cosine"},"precision":"fp32","computeTarget":"cpu","checkpointPolicy":{"everyEpochs":1}},
 "datasets":[{"datasetRef":"dataset-1","version":"1","sourceHash":"abc"}],
 "evaluationPlan":{"metrics":["accuracy"]}
}

def test_health_and_contract():
    h=m.health(); assert h["ok"] and h["version"]=="0.141.1" and h["api_route_count"]==33
    assert h["machineLearningExperimentWorkspaceVersion"]=="0.141.0" and h["manifestIntegrityBaseline"]=="0.140.0.1"
    assert m.contract()["workspaceHandoffSchema"]=="sc-workspace-neural-training-request/1.0"

def test_architecture_and_training_normalization():
    a=m.normalize_architecture(PAYLOAD)["architecture"]; c=m.normalize_training_configuration(PAYLOAD)["trainingConfiguration"]
    assert a["family"]=="mlp" and len(a["layers"])==3 and a["automaticArchitectureApproval"] is False
    assert c["seed"]==42 and c["optimizer"]["name"]=="adamw" and c["labExecutesTraining"] is False
    assert m.validate_architecture(PAYLOAD)["ok"] is True
    assert m.validate_training_configuration(PAYLOAD)["ok"] is True

def test_handoffs_preserve_authority_boundaries():
    w=m.workspace_handoff(PAYLOAD)["handoff"]; core=m.core_handoff(PAYLOAD)["handoff"]
    assert w["executionAuthority"]=="workspace" and w["automaticExecution"] is False
    assert core["canonicalAuthority"]=="platform-core" and core["labMayOverrideCoreObjectSemantics"] is False

def test_fingerprints_and_snapshots_are_deterministic():
    f1=m.configuration_fingerprint(PAYLOAD)["fingerprint"]; f2=m.configuration_fingerprint(PAYLOAD)["fingerprint"]
    assert f1==f2
    s1=m.snapshot(PAYLOAD)["snapshot"]; s2=m.snapshot(PAYLOAD)["snapshot"]
    assert s1["fingerprint"]==s2["fingerprint"] and s1["snapshotId"]==s2["snapshotId"]

def test_comparisons_do_not_rank_or_choose():
    a=m.compare_architectures({"architectures":[PAYLOAD["architecture"],{"title":"other","family":"cnn"}]})
    c=m.compare_training_configurations({"configurations":[PAYLOAD["trainingConfiguration"],{"epochs":5,"batchSize":16}]})
    assert a["winnerSelected"] is False and a["rankingProduced"] is False
    assert c["winnerSelected"] is False and c["automaticTuning"] is False

def test_reproducibility_is_not_certification():
    r=m.reproducibility_packet(PAYLOAD)
    assert r["ok"] and r["reproducibilityCertified"] is False
    assert m.policy()["predictionIsEvidence"] is False
