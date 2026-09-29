from app import scientific_research_operating_system_v01400 as m


def payload():
    return {
        "projectId":"project-1","studyId":"study-1","title":"Research OS Study","phase":"analysis",
        "question":{"text":"Does X affect Y?"},"methods":[{"id":"method-1"}],"datasets":[{"id":"data-1"}],
        "executions":[{"id":"run-1"}],"analyses":[{"id":"analysis-1"}],"evidence":[{"id":"evidence-1"}],
        "claims":[{"id":"claim-1"}],"findings":[{"id":"finding-1"}],"limitations":[{"id":"limit-1"}],
        "reviews":[{"id":"review-1"}],"reproductionPackages":[{"id":"repro-1"}],"manuscripts":[{"id":"ms-1"}],
        "provenance":{"rootRef":"project-1"},"nodes":[{"id":"data-1"},{"id":"finding-1"}],"edges":[{"from":"data-1","to":"finding-1"}],
        "program":{"programId":"program-1","studies":[{"studyId":"study-1"}]},
    }


def test_normalization_is_deterministic_and_non_adjudicative():
    a=m.normalize(payload()); b=m.normalize(payload())
    assert a["ok"] and a["record"]["fingerprint"]==b["record"]["fingerprint"]
    assert a["record"]["automaticScientificValidity"] is False
    assert a["record"]["automaticPhaseAdvance"] is False


def test_lifecycle_reports_presence_without_advancing_phase():
    result=m.lifecycle(payload())
    assert result["declaredCurrentPhase"]=="analysis"
    assert result["automaticPhaseAdvance"] is False
    assert any(x["phase"]=="analysis" and x["declaredArtifactsPresent"] for x in result["phases"])


def test_capability_matrix_preserves_authority():
    result=m.capability_matrix({})
    assert result["count"]>=9
    assert result["orchestrationDoesNotReplaceSubsystemAuthority"] is True


def test_readiness_does_not_certify_science():
    result=m.readiness(payload())
    assert result["administrativelyComplete"] is True
    assert result["scientificValidityCertified"] is False
    assert result["reproducibilityCertified"] is False
    assert result["publicationAccepted"] is False


def test_continuity_retains_previous_three_releases():
    result=m.continuity(payload())
    versions={x["version"] for x in result["bridges"]}
    assert versions=={"0.137.0","0.138.0","0.139.0"}


def test_snapshot_and_handoff_are_deterministic_contracts():
    s1=m.snapshot(payload())["snapshot"]; s2=m.snapshot(payload())["snapshot"]
    assert s1["fingerprint"]==s2["fingerprint"]
    h=m.handoff({**payload(),"target":"workspace"})
    assert h["ok"] and h["handoff"]["automaticImport"] is False


def test_acceptance_and_release_gates():
    a=m.acceptance_report(); g=m.release_gates(); h=m.health()
    assert a["scientificResearchOperatingSystem"] is True
    assert a["backwardCompatibleV01390"] is True
    assert a["automaticScientificValidity"] is False
    assert g["requiredRouteCount"]==25
    assert h["version"]=="0.140.0"
