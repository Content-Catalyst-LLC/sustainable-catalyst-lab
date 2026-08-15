from copy import deepcopy
import pytest

from app.scientific_study_lifecycle_v0610 import (
    ScientificStudyLifecycleError, build_study_packet, evaluate_lifecycle, health,
    normalize_study, policies, record_stage_review, templates, verify_study_packet,
)


def _study(study_type="observational"):
    return {
        "id": "wetland-resilience",
        "title": "Wetland resilience study",
        "studyType": study_type,
        "status": "active",
        "researchQuestion": "How is drought frequency associated with wetland resilience?",
        "hypotheses": ["Higher drought frequency is associated with lower resilience."],
        "methodsSummary": "Use governed observations, declared inclusion criteria, and registered transformations.",
        "analysisPlan": "Fit declared statistical models, validate out of sample, and inspect diagnostics.",
        "uncertaintyPlan": "Quantify interval uncertainty and sensitivity to model assumptions.",
        "conclusionSummary": "Current evidence supports a bounded association under the declared study design.",
        "limitations": "Observational design does not establish causality; measurement and sampling limitations remain.",
    }


def _project(audit="audit-ready", experiments=0):
    return {
        "id": "project-one", "title": "Project one",
        "counts": {"datasets": 1, "models": 1, "analysisPackets": 8, "visualizations": 1, "experiments": experiments,
                   "reports": 1, "scientificWorkflowsV0570": 1, "scientificWorkflowRunsV0570": 1, "reproduciblePackages": 1},
        "analysisRecordTypes": ["advanced-statistical-model-v0510", "cross-validation", "probabilistic-analysis-v0480"],
        "workflowRunHashes": ["a"*64], "packageHashes": ["b"*64], "figureHashes": ["c"*64],
        "audit": {"gate": audit, "auditHash": "d"*64, "humanReviewRequired": True},
    }


def _accept_all(study, project):
    current = normalize_study(study)
    first = evaluate_lifecycle({"study": current, "project": project})
    for stage in first["requiredStageIds"]:
        current = record_stage_review({"study": current, "review": {"stageId": stage, "decision": "accept", "rationale": "Evidence reviewed and accepted for this lifecycle stage.", "reviewedAt": f"2026-08-15T12:{len(current['stageReviews']):02d}:00-05:00"}})["study"]
    return current


def test_health_and_policy_define_human_governed_study_lifecycle():
    assert health()["stageCount"] == 11
    p = policies()
    assert p["endToEndStudyLifecycle"] is True
    assert p["humanStageReviewRequired"] is True
    assert p["automaticScientificCertificationAuthorized"] is False
    assert p["automaticCausalClaimAuthorized"] is False


def test_template_catalog_has_four_bounded_study_types():
    t = templates()
    assert len(t["templates"]) == 4
    assert {x["studyType"] for x in t["templates"]} == {"observational", "experimental", "computational", "mixed"}
    assert len(t["templateHash"]) == 64


def test_study_normalization_is_deterministic_and_hashed():
    a = normalize_study(_study())
    b = normalize_study(_study())
    assert a["studyHash"] == b["studyHash"]
    assert a["schema"] == "sc-lab-scientific-study/0.61.0"
    assert a["studyType"] == "observational"


def test_study_rejects_raw_data_credentials_and_arbitrary_inputs():
    with pytest.raises(ScientificStudyLifecycleError):
        normalize_study({**_study(), "dataset": {"rows": [{"x": 1}]}})
    with pytest.raises(ScientificStudyLifecycleError):
        normalize_study({**_study(), "credentials": {"token": "never"}})
    with pytest.raises(ScientificStudyLifecycleError):
        normalize_study({**_study(), "inputs": {"callback": "x"}})


def test_complete_evidence_requires_explicit_human_stage_review():
    result = evaluate_lifecycle({"study": _study(), "project": _project()})
    assert result["gate"] == "needs-review"
    assert not result["missingEvidence"]
    assert "question" in result["pendingHumanReview"]
    assert result["scientificCertificationClaim"] is False


def test_experimental_study_requires_experimental_evidence():
    result = evaluate_lifecycle({"study": _study("experimental"), "project": _project(experiments=0)})
    assert result["gate"] == "needs-evidence"
    assert "experiment" in result["missingEvidence"]


def test_observational_study_marks_experiment_not_applicable():
    result = evaluate_lifecycle({"study": _study("observational"), "project": _project()})
    experiment = next(row for row in result["stages"] if row["id"] == "experiment")
    assert experiment["status"] == "not-applicable"
    assert experiment["required"] is False


def test_stage_review_requires_rationale_and_is_tamper_evident():
    with pytest.raises(ScientificStudyLifecycleError):
        record_stage_review({"study": _study(), "review": {"stageId": "question", "decision": "accept", "rationale": ""}})
    out = record_stage_review({"study": _study(), "review": {"stageId": "question", "decision": "accept", "rationale": "Research question reviewed against the study purpose.", "reviewedAt": "2026-08-15T12:00:00-05:00"}})
    assert len(out["review"]["reviewHash"]) == 64
    assert out["study"]["stageReviews"][-1]["decision"] == "accept"


def test_blocked_stage_blocks_lifecycle_even_when_evidence_exists():
    reviewed = record_stage_review({"study": _study(), "review": {"stageId": "validation", "decision": "block", "rationale": "Validation evidence is not sufficient.", "reviewedAt": "2026-08-15T12:00:00-05:00"}})["study"]
    result = evaluate_lifecycle({"study": reviewed, "project": _project()})
    assert result["gate"] == "blocked"
    assert "validation" in result["blockedStages"]


def test_audit_block_propagates_to_study_lifecycle():
    result = evaluate_lifecycle({"study": _study(), "project": _project(audit="blocked")})
    assert result["gate"] == "blocked"
    assert "audit" in result["blockedStages"]


def test_all_required_stages_can_reach_study_complete_only_after_human_acceptance():
    reviewed = _accept_all(_study(), _project())
    result = evaluate_lifecycle({"study": reviewed, "project": _project()})
    assert result["gate"] == "study-complete"
    assert not result["pendingHumanReview"]
    assert all(row["status"] in {"accepted", "not-applicable", "evidence-ready"} for row in result["stages"])


def test_study_packet_is_deterministic_metadata_only_and_tamper_evident():
    reviewed = _accept_all(_study(), _project())
    first = build_study_packet({"study": reviewed, "project": _project()})["packet"]
    second = build_study_packet({"study": reviewed, "project": _project()})["packet"]
    assert first["packetHash"] == second["packetHash"]
    assert first["boundaries"]["rawScientificDataIncluded"] is False
    assert first["boundaries"]["automaticCausalClaim"] is False
    assert verify_study_packet({"packet": first})["ok"] is True
    broken = deepcopy(first); broken["gate"] = "blocked"
    assert verify_study_packet({"packet": broken})["ok"] is False
