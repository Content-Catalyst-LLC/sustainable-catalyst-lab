from app import scholarly_study_original_research_package_v01390 as m


def payload():
    return {
        "packageId": "pkg-1", "studyId": "study-1", "projectId": "project-1", "title": "Original Study",
        "researchQuestion": {"text": "Does X change Y?"},
        "methods": [{"id": "method-1", "title": "Declared method"}],
        "datasets": [{"id": "data-1", "title": "Dataset"}],
        "executions": [{"id": "run-1"}],
        "analyses": [{"id": "analysis-1"}],
        "evidence": [{"id": "evidence-1"}],
        "claims": [{"id": "claim-1"}],
        "findings": [{"id": "finding-1"}],
        "limitations": [{"id": "limit-1", "text": "Declared limitation"}],
        "reviews": [{"id": "review-1", "status": "closed"}],
        "reproductionPackages": [{"id": "repro-1"}],
        "manuscripts": [{"id": "manuscript-1"}],
        "contributors": [{"name": "Researcher"}],
        "provenance": {"rootRef": "project-1"},
        "nodes": [{"id": "data-1", "type": "dataset"}, {"id": "finding-1", "type": "finding"}],
        "edges": [{"from": "data-1", "to": "finding-1"}],
        "changeEvents": [],
    }


def test_normalization_and_manifest_are_deterministic():
    a = m.normalize_package(payload())
    b = m.normalize_package(payload())
    assert a["ok"] and a["record"]["fingerprint"] == b["record"]["fingerprint"]
    manifest = m.manifest(payload())
    assert manifest["ok"] and manifest["manifest"]["artifactCount"] >= 9


def test_readiness_is_descriptive_not_validity_certification():
    result = m.readiness(payload())
    assert result["packageAssemblyComplete"] is True
    assert result["readyForHumanReview"] is True
    assert result["scientificValidityCertified"] is False
    assert result["publicationAccepted"] is False


def test_provenance_and_reproduction_preserve_boundaries():
    p = m.provenance_lineage(payload())
    r = m.reproducibility_index(payload())
    assert p["aggregationDoesNotReplaceSourceProvenance"] is True
    assert r["reproducibleDoesNotEqualCorrect"] is True


def test_snapshot_and_compare():
    left = m.snapshot(payload())["snapshot"]
    changed = payload(); changed["figures"] = [{"id": "figure-1"}]
    right = m.snapshot(changed)["snapshot"]
    diff = m.compare_snapshots({"left": left, "right": right})
    assert diff["packageChanged"] is True
    assert "figure-1" in diff["addedArtifactRefs"]


def test_core_handoff_requires_explicit_submission():
    h = m.core_scholarly_handoff(payload())
    assert h["ok"] and h["automaticCoreSubmission"] is False and h["coreBecomesSourceAuthority"] is False


def test_policy_and_release_gates():
    p = m.policy(); g = m.release_gates(); h = m.health()
    assert p["automaticScientificValidity"] is False
    assert p["automaticPublicationAcceptance"] is False
    assert g["requiredRouteCount"] == 25
    assert h["version"] == "0.139.0"
