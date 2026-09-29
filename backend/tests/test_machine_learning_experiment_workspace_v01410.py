from app import machine_learning_experiment_workspace_v01410 as m


def payload():
    return {
        "projectId":"project-ml-1","studyId":"study-ml-1","experimentId":"exp-1","title":"Classifier study",
        "state":"designed","taskType":"classification","objective":{"text":"Compare declared model configurations"},
        "datasets":[{"id":"dataset-1","version":"v1","role":"train","sha256":"abc"}],
        "features":[{"id":"feature-set-1"}],"transformations":[{"id":"transform-1"}],
        "modelSpecification":{"modelId":"model-1","framework":"pytorch","architecture":"mlp"},
        "trainingConfiguration":{"epochs":5,"seed":42,"optimizer":"adam"},
        "evaluationPlan":{"metrics":["accuracy","log_loss"]},"computeTarget":"mps",
        "runtime":{"runtime":"pytorch"},
        "runs":[{"id":"run-1","state":"completed"}],
        "checkpoints":[{"id":"ckpt-1","runId":"run-1","epoch":5,"sha256":"def"}],
        "metrics":[{"name":"accuracy","value":0.8,"split":"validation","epoch":5}],
        "predictions":[{"id":"pred-1","runId":"run-1","value":"A","probability":0.8}],
        "interpretations":[{"id":"interp-1"}],"artifacts":[{"id":"artifact-1"}],
        "provenance":{"codeRef":"commit-1"},"limitations":[{"text":"small sample"}],
    }


def test_normalize_is_deterministic_and_preserves_boundaries():
    a=m.normalize(payload()); b=m.normalize(payload())
    assert a["ok"] and a["record"]["fingerprint"]==b["record"]["fingerprint"]
    assert a["record"]["labExecutesTraining"] is False
    assert a["record"]["predictionIsEvidence"] is False
    assert a["record"]["automaticBestModelSelection"] is False


def test_validation_and_lifecycle_are_descriptive():
    v=m.validate(payload()); life=m.lifecycle(payload())
    assert v["ok"] and not v["errors"]
    assert life["automaticStateAdvance"] is False
    assert any(x["stage"]=="execution" and x["declaredArtifactsPresent"] for x in life["stages"])


def test_workspace_handoff_does_not_execute():
    h=m.workspace_handoff(payload())
    assert h["ok"] and h["handoff"]["computeTarget"]=="mps"
    assert h["handoff"]["automaticExecution"] is False
    assert h["executionAuthority"]=="workspace"


def test_workspace_result_ingest_does_not_certify_science():
    p=payload(); p["workspaceResult"]={"experimentId":"exp-1","runId":"run-2","state":"completed","metrics":[{"name":"accuracy","value":0.9}]}
    r=m.ingest_workspace_result(p)
    assert r["ok"] and r["accepted"]
    assert r["result"]["predictionIsEvidence"] is False
    assert r["scientificValidityCertified"] is False


def test_comparison_never_selects_automatic_winner():
    a=payload(); b=payload(); b["experimentId"]="exp-2"; b["trainingConfiguration"]={"epochs":10,"seed":42}
    matrix=m.comparison_matrix({"experiments":[a,b]})
    comp=m.experiment_compare({"left":a,"right":b})
    assert matrix["automaticWinner"] is None
    assert comp["preferredExperiment"] is None
    assert "trainingConfiguration" in comp["changedFields"]


def test_predictions_remain_predictions():
    r=m.prediction_registry(payload())
    assert r["predictionIsEvidence"] is False
    assert r["predictions"][0]["evidenceStatus"]=="prediction-not-evidence"


def test_reproducibility_and_snapshots_are_deterministic():
    p1=m.reproducibility_packet(payload())["packet"]; p2=m.reproducibility_packet(payload())["packet"]
    s1=m.snapshot(payload())["snapshot"]; s2=m.snapshot(payload())["snapshot"]
    assert p1["fingerprint"]==p2["fingerprint"]
    assert s1["fingerprint"]==s2["fingerprint"]
    assert p1["scientificValidityCertified"] is False


def test_research_os_bridge_preserves_human_phase_control():
    r=m.research_os_handoff(payload())
    assert r["ok"] and r["sourceVersion"]=="0.140.0"
    assert r["automaticPhaseAdvance"] is False


def test_acceptance_health_and_gates():
    a=m.acceptance_report(); h=m.health(); g=m.release_gates()
    assert a["machineLearningExperimentWorkspace"] is True
    assert a["backwardCompatibleV01400"] is True
    assert a["manifestScopeRepairRetainedV013901"] is True
    assert h["version"]=="0.141.0"
    assert g["requiredRouteCount"]==27
