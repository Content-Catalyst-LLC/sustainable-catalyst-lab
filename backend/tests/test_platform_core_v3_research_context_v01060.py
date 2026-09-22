import pytest

from app.platform_core_v3_research_context_v01060 import (
    CORE_HANDOFF_BINDING_PATH,
    CORE_PRODUCT_BINDING_PATH,
    CORE_SESSION_PATH,
    MINIMUM_CORE_RELEASE,
    PlatformCoreV3ResearchContextError,
    build_contextual_handoff_binding,
    build_contextual_object_binding,
    build_core_product_context_binding,
    build_core_session_registration,
    check_context_continuity,
    health,
    manifest,
    normalize_research_context,
)


def base_context(**extra):
    value = {
        "project_ref": "project:carbon-study",
        "session_id": "42",
        "session_key": "carbon-study-2026",
        "title": "Carbon Study",
        "workflow_ref": "lab:workflow:w1",
        "project_state_ref": "core:project-state:9",
        "researcher_ref": "researcher:tariq",
        "agent_ref": "agent:lab-service",
        "contributor_refs": ["researcher:tariq", "agent:lab-service"],
        "visibility": "private",
        "metadata": {"course": "sustainable-development"},
        "provenance": {"source": "test"},
    }
    value.update(extra)
    return value


def test_health_and_manifest_define_context_boundary():
    h=health(); m=manifest()
    assert h["lab_release_version"] == "0.106.0"
    assert h["minimum_core_release"] == MINIMUM_CORE_RELEASE == "3.0.0"
    assert m["boundaries"]["core_owns_session_registry"] is True
    assert m["boundaries"]["lab_owns_scientific_workspace_state"] is True
    assert m["boundaries"]["automatic_core_submission"] is False
    assert m["boundaries"]["execution_lineage_deferred_to"] == "Lab v0.107.0"


def test_normalize_context_is_stable_and_private_maps_to_internal():
    a=normalize_research_context(base_context())["context"]
    b=normalize_research_context(base_context())["context"]
    assert a["context_ref"] == b["context_ref"]
    assert a["context_hash"] == b["context_hash"]
    assert a["project_ref"] == "project:carbon-study"
    assert a["lab_visibility"] == "private" and a["core_visibility"] == "internal"


def test_build_core_session_registration_matches_core_v3_contract():
    out=build_core_session_registration(base_context())
    assert out["target_path"] == CORE_SESSION_PATH
    assert out["automatic_submission"] is False
    assert out["request_body"] == {"data": out["data"]}
    assert out["data"]["project_ref"] == "project:carbon-study"
    assert out["data"]["workflow_ref"] == "lab:workflow:w1"
    assert out["data"]["project_state_ref"] == "core:project-state:9"
    assert out["data"]["metadata"]["context_ref"].startswith("lab:research-context:")


def test_product_binding_carries_same_context():
    out=build_core_product_context_binding(base_context())
    assert out["target_path"] == CORE_PRODUCT_BINDING_PATH
    assert out["data"]["session_id"] == "42"
    assert out["data"]["context_ref"] == out["context"]["context_ref"]
    assert out["data"]["metadata"]["project_ref"] == "project:carbon-study"
    assert out["automatic_submission"] is False


def test_contextual_object_binding_reuses_v01050_mapping_and_context():
    out=build_contextual_object_binding({
        "context": base_context(),
        "object": {"object_type":"dataset","id":"d1","content_hash":"a"*64,"metadata":{"title":"Study data"}},
    })
    mapped=out["core_mapping"]
    assert mapped["data"]["session_id"] == "42"
    assert mapped["data"]["object_ref"] == "lab:dataset:d1"
    meta=mapped["data"]["metadata"]["lab_metadata"]
    assert meta["project_ref"] == "project:carbon-study"
    assert meta["context_ref"] == out["context"]["context_ref"]
    assert out["automatic_submission"] is False and out["automatic_execution"] is False


def test_contextual_handoff_binding_preserves_project_session_context():
    out=build_contextual_handoff_binding({
        "context": base_context(),
        "handoff": {"id":"handoff-1","sourceProduct":"sustainable-catalyst-lab","targetProduct":"knowledge-library"},
    })
    assert out["target_path"] == CORE_HANDOFF_BINDING_PATH
    assert out["data"]["session_id"] == "42"
    assert out["data"]["context_ref"] == out["context"]["context_ref"]
    assert out["data"]["target_product_ref"] == "knowledge-library"
    assert out["automatic_submission"] is False
    assert out["automatic_execution"] is False
    assert out["automatic_core_mutation"] is False


def test_continuity_accepts_matching_entries_and_reports_conflicts():
    c=normalize_research_context(base_context())["context"]
    good=check_context_continuity({"context":c,"entries":[{"project_ref":c["project_ref"],"session_id":c["session_id"],"context_ref":c["context_ref"]}]})
    assert good["ok"] is True and good["mismatch_count"] == 0
    bad=check_context_continuity({"context":c,"entries":[{"project_ref":"project:other","session_id":c["session_id"]}]})
    assert bad["ok"] is False and bad["mismatches"][0]["field"] == "project_ref"


def test_required_fields_are_enforced():
    with pytest.raises(PlatformCoreV3ResearchContextError):
        normalize_research_context({})
    with pytest.raises(PlatformCoreV3ResearchContextError):
        build_core_session_registration({"project_ref":"p"})
    with pytest.raises(PlatformCoreV3ResearchContextError):
        build_core_product_context_binding({"project_ref":"p"})
