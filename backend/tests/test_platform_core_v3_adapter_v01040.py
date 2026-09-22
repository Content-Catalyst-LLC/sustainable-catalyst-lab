import pytest

from app.platform_core_v3_adapter_v01040 import (
    ADAPTER_REF,
    CORE_REQUIRED_RELEASE,
    CORE_RUNTIME_CONTRACT,
    CORE_UNIFIED_RUNTIME_CONTRACT,
    LAB_VERSION,
    PRODUCT_REF,
    RUNTIME_BINDING_REF,
    PlatformCoreV3AdapterError,
    build_contract_product_registration,
    build_session_product_binding,
    compatibility_report,
    health,
    manifest,
    normalize_runtime_context,
    validate_handoff,
)


def core_readiness():
    return {
        "release": "3.0.0",
        "contract": "sc.research.unified-research-scientific-investigation-runtime.v1",
        "reference_first_runtime_by_core": True,
        "unified_session_registry_by_core": True,
        "research_object_binding_by_core": True,
        "product_context_binding_by_core": True,
        "computation_execution_binding_by_core": True,
        "investigation_binding_by_core": True,
        "visual_reasoning_binding_by_core": True,
        "validation_challenge_binding_by_core": True,
        "research_package_binding_by_core": True,
        "cross_product_handoff_binding_by_core": True,
        "milestone_registry_by_core": True,
        "revision_history_by_core": True,
        "immutable_runtime_snapshots_by_core": True,
        "underlying_objects_remain_authoritative_in_specialist_layers": True,
        "execute_scientific_work_by_core": False,
        "execute_code_by_core": False,
        "run_investigation_by_core": False,
        "infer_findings_by_core": False,
        "infer_causality_by_core": False,
        "select_hypothesis_by_core": False,
        "rank_evidence_by_core": False,
        "render_visuals_by_core": False,
        "publish_research_by_core": False,
        "authorize_access_by_core": False,
        "certify_scientific_validity_by_core": False,
        "determine_truth_by_core": False,
    }


def test_manifest_and_health_are_core_v3_specific():
    m = manifest()
    h = health()
    assert m["lab_release_version"] == LAB_VERSION == "0.104.0"
    assert m["required_core_release"] == CORE_REQUIRED_RELEASE == "3.0.0"
    assert m["product_ref"] == PRODUCT_REF
    assert m["adapter_ref"] == ADAPTER_REF
    assert m["runtime_binding_ref"] == RUNTIME_BINDING_REF
    assert m["contracts"]["runtime_contract"] == CORE_RUNTIME_CONTRACT
    assert m["contracts"]["unified_runtime"] == CORE_UNIFIED_RUNTIME_CONTRACT
    assert m["boundaries"]["lab_is_scientific_execution_authority"] is True
    assert m["boundaries"]["lab_calls_core_automatically"] is False
    assert h["status"] == "platform-core-v3-adapter-ready"


def test_builds_core_contract_and_session_product_bindings_without_submitting():
    contract = build_contract_product_registration({"contract_id": "contract-1", "supported_object_types": ["dataset", "model"]})
    assert contract["target_path"] == "/v1/research/runtime-contract/product-bindings"
    assert contract["automatic_submission"] is False
    assert contract["data"]["product_ref"] == PRODUCT_REF
    assert contract["data"]["product_version"] == LAB_VERSION
    assert contract["data"]["adapter_ref"] == ADAPTER_REF
    assert contract["data"]["supported_object_types"] == ["dataset", "model"]

    session = build_session_product_binding({"session_id": "42", "context_ref": "context:abc"})
    assert session["target_path"] == "/v1/research/unified-runtime/product-bindings"
    assert session["automatic_submission"] is False
    assert session["data"]["session_id"] == "42"
    assert session["data"]["runtime_binding_ref"] == RUNTIME_BINDING_REF
    assert "scientific-compute" in session["data"]["declared_capabilities"]


def test_normalizes_core_session_context_reference_first():
    out = normalize_runtime_context({
        "id": 12,
        "project_ref": "project:grad-study",
        "workflow_ref": "workflow:causal-study",
        "project_state_ref": "project-state:7",
        "runtime_contract_ref": CORE_RUNTIME_CONTRACT,
        "visibility": "internal",
    })
    context = out["context"]
    assert context["session_id"] == "12"
    assert context["project_ref"] == "project:grad-study"
    assert context["lab_product_ref"] == PRODUCT_REF
    assert len(context["context_hash"]) == 64
    assert out["boundaries"]["core_executes_specialist_work"] is False


def test_rejects_wrong_runtime_contract_and_wrong_handoff_target():
    with pytest.raises(PlatformCoreV3AdapterError):
        normalize_runtime_context({"session_id": "1", "project_ref": "project:1", "runtime_contract_ref": "other-contract"})
    with pytest.raises(PlatformCoreV3AdapterError):
        validate_handoff({"session_id": "1", "handoff_ref": "handoff:1", "source_product_ref": "product:workspace", "target_product_ref": "product:other"})


def test_accepts_core_v3_handoff_without_auto_execution():
    result = validate_handoff({
        "session_id": "9",
        "handoff_ref": "handoff:core-to-lab:9",
        "source_product_ref": "product:sustainable-catalyst-workspace",
        "target_product_ref": PRODUCT_REF,
        "context_ref": "context:9",
        "status": "declared",
    })
    assert result["ok"] is True
    assert result["automatic_execution"] is False
    assert result["automatic_core_mutation"] is False
    assert result["handoff"]["target_product_ref"] == PRODUCT_REF
    assert len(result["handoff"]["handoff_hash"]) == 64


def test_core_v3_readiness_compatibility_and_boundary_failure():
    good = compatibility_report(core_readiness())
    assert good["ok"] is True
    assert good["status"] == "compatible"
    assert good["failed_checks"] == []

    bad_payload = core_readiness()
    bad_payload["execute_scientific_work_by_core"] = True
    bad = compatibility_report(bad_payload)
    assert bad["ok"] is False
    assert "execute_scientific_work_by_core" in bad["failed_checks"]
