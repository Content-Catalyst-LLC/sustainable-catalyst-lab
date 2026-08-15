from __future__ import annotations
from copy import deepcopy
import pytest

from app.integrated_research_beta_v0600 import (
    IntegratedResearchBetaError, beta_readiness, build_beta_packet, capability_matrix,
    health, normalize_project_summary, policies, research_journey, verify_beta_packet,
)


def _summary():
    return {
        "id": "beta-project", "title": "Integrated beta project", "schemaVersion": "0.28.0",
        "counts": {"datasets": 1, "models": 1, "analysisPackets": 8, "visualizations": 2,
                   "experiments": 1, "scientificWorkflowsV0570": 1, "scientificWorkflowRunsV0570": 1,
                   "reproduciblePackages": 1},
        "analysisRecordTypes": ["data-transformation-v0550", "advanced-statistical-model-v0510", "cross-validation-v0510", "correlated-uncertainty-v0530", "advanced-experimental-design-v0560", "reproducible-model-package-v0500"],
        "workflowRunHashes": ["a" * 64], "packageHashes": ["b" * 64], "figureHashes": ["c" * 64],
        "audit": {"gate": "audit-ready", "auditHash": "d" * 64, "humanReviewRequired": True},
    }


def test_health_and_policy_define_beta_not_auto_certification():
    assert health()["ok"] is True
    p = policies()
    assert p["betaMilestone"] is True
    assert p["automaticScientificCertificationAuthorized"] is False
    assert p["rawSensitiveDataInBetaPacket"] is False


def test_capability_matrix_integrates_major_release_line():
    matrix = capability_matrix()
    ids = {row["id"] for row in matrix["capabilities"]}
    assert {"reproducibility", "statistics", "bayesian", "dependency", "transformations", "experiments", "workflow", "compute", "audit"} <= ids
    assert len(matrix["capabilityHash"]) == 64


def test_project_summary_rejects_raw_dataset_inputs_and_credentials():
    with pytest.raises(IntegratedResearchBetaError):
        normalize_project_summary({"rows": [{"x": 1}]})
    with pytest.raises(IntegratedResearchBetaError):
        normalize_project_summary({"credentials": {"token": "never"}})


def test_empty_project_journey_marks_required_evidence_missing():
    journey = research_journey({"project": {"id": "empty", "counts": {}}})
    assert set(["data", "model", "validation", "workflow", "reproducibility", "audit"]) <= set(journey["missingRequired"])
    assert journey["humanReviewRequired"] is True


def test_complete_project_journey_covers_required_research_path():
    journey = research_journey({"project": _summary()})
    assert journey["missingRequired"] == []
    assert journey["requiredComplete"] == journey["requiredTotal"]
    assert any(step["id"] == "figure" and step["complete"] for step in journey["steps"])


def test_blocked_audit_blocks_beta_readiness():
    summary = _summary(); summary["audit"]["gate"] = "blocked"
    result = beta_readiness({"project": summary})
    assert result["gate"] == "blocked" and result["readyForBetaUse"] is False


def test_complete_evidence_is_beta_review_ready_but_human_review_remains_required():
    result = beta_readiness({"project": _summary()})
    assert result["gate"] == "beta-review-ready" and result["readyForBetaUse"] is True
    assert result["humanReviewRequired"] is True
    assert result["automaticScientificCertificationAuthorized"] is False


def test_beta_packet_is_deterministic_and_metadata_only():
    first = build_beta_packet({"project": _summary()})["packet"]
    second = build_beta_packet({"project": _summary()})["packet"]
    assert first["packetHash"] == second["packetHash"]
    assert first["boundaries"]["rawSensitiveDataIncluded"] is False
    assert "counts" not in first and "analysisRecordTypes" not in first


def test_beta_packet_changes_when_evidence_changes():
    first = build_beta_packet({"project": _summary()})["packet"]
    changed = _summary(); changed["packageHashes"] = ["e" * 64]
    second = build_beta_packet({"project": changed})["packet"]
    assert first["packetHash"] != second["packetHash"]


def test_beta_packet_verification_detects_tampering():
    packet = build_beta_packet({"project": _summary()})["packet"]
    assert verify_beta_packet({"packet": packet})["ok"] is True
    broken = deepcopy(packet); broken["gate"] = "blocked"
    assert verify_beta_packet({"packet": broken})["ok"] is False
