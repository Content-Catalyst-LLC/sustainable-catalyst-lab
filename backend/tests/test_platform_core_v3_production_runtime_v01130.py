import pytest
from app.platform_core_v3_production_runtime_v01130 import *

CTX={"project_ref":"project:p1","session_id":"12","session_key":"s12","title":"Production","workflow_ref":"lab:workflow:w1","project_state_ref":"core:state:12","researcher_ref":"researcher:r1"}

COMPONENT_HEALTH={name:{"ok":True,"lab_release_version":spec["version"]} for name,spec in COMPONENTS.items()}


def test_catalog_and_manifest_boundaries():
    c=catalog(); m=manifest(); h=health()
    assert c["component_count"]==9 and c["operation_type_count"]==14
    assert h["lab_release_version"]=="0.113.0" and h["minimum_core_release"]=="3.0.0"
    assert m["boundaries"]["automatic_retry"] is False and m["boundaries"]["automatic_truth_determination"] is False


def test_normalize_object_operation_is_deterministic_and_non_submitting():
    p={"context":CTX,"operation_type":"object-binding","payload":{"object":{"object_type":"dataset","id":"d1","content_hash":"a"*64}}}
    a=normalize_operation(p); b=normalize_operation(p)
    assert a["operation"]["request_hash"]==b["operation"]["request_hash"]
    assert a["operation"]["idempotency_key"]==b["operation"]["idempotency_key"]
    assert a["operation"]["automatic_submission"] is False
    assert a["operation"]["target_endpoint"].endswith("/object-bindings")


def test_submission_plan_has_explicit_idempotency_headers_only():
    p=build_submission_plan({"context":CTX,"operation_type":"execution-binding","payload":{"execution":{"id":"r1","runtime":"python","environment_ref":"lab:env:e1","method_ref":"lab:method:m1","inputs":[],"outputs":[]}}})
    assert p["request"]["headers"]["Idempotency-Key"].startswith("sc-lab-v01130:")
    assert p["automatic_submission"] is False and p["authorization_material_included"] is False


def test_idempotency_new_replay_safe_and_conflict():
    base={"context":CTX,"operation_type":"object-binding","payload":{"object":{"object_type":"dataset","id":"d1","content_hash":"a"*64}}}
    op=normalize_operation(base)["operation"]
    assert check_idempotency(base)["state"]=="new"
    safe={**base,"prior_records":[{"idempotency_key":op["idempotency_key"],"request_hash":op["request_hash"]}]}
    assert check_idempotency(safe)["state"]=="replay-safe"
    conflict={**base,"prior_records":[{"idempotency_key":op["idempotency_key"],"request_hash":"b"*64}]}
    assert check_idempotency(conflict)["state"]=="conflict"


def test_receipt_never_infers_success_from_http_status():
    op=normalize_operation({"context":CTX,"operation_type":"object-binding","payload":{"object":{"object_type":"dataset","id":"d1","content_hash":"a"*64}}})["operation"]
    r=build_receipt({"operation":op,"declared_outcome":"uncertain","status_code":200,"response":{"ok":True}})["receipt"]
    assert r["declared_outcome"]=="uncertain" and r["success_inferred_from_status_code"] is False


def test_retry_plan_is_advisory_and_never_automatic():
    r={"operation_ref":"op:1","operation_type":"object-binding","idempotency_key":"k","request_hash":"a"*64,"correlation_ref":"c","attempt":1,"declared_outcome":"failed","status_code":503,"error_code":None}
    p=build_retry_plan({"receipt":r,"max_attempts":4})
    assert p["eligible_for_explicit_retry"] is True and p["next_attempt"]==2
    assert p["automatic_retry"] is False and p["automatic_submission"] is False


def test_recovery_checkpoint_and_continuity():
    op={"operation_ref":"op:1","context_ref":"ctx:1","project_ref":"project:p1","session_id":"12"}
    recovery=build_recovery_plan({"receipts":[{"operation_ref":"op:1","declared_outcome":"failed"},{"operation_ref":"op:2","declared_outcome":"conflict"}]})
    assert recovery["recovery_required"] is True and recovery["automatic_recovery"] is False
    ctx={**CTX,"context_ref":"ctx:1"}
    cp=build_checkpoint({"context":ctx,"operations":[op],"receipts":[]})
    assert cp["checkpoint"]["operation_count"]==1 and cp["automatic_persistence"] is False
    continuity=check_continuity({"context":ctx,"operations":[op]})
    assert continuity["continuous"] is True


def test_diagnostics_and_readiness_use_declared_health_only():
    d=assess_diagnostics({"components":COMPONENT_HEALTH})
    assert d["ready"] is True and d["live_calls_performed"] is False
    ready=check_readiness({"core_health":{"ok":True,"version":"3.1.0"},"components":COMPONENT_HEALTH,"certification":{"declared_conformance":True}})
    assert ready["production_ready"] is True and ready["scientific_validity_certified"] is False
    bad=check_readiness({"core_health":{"ok":True,"version":"2.99.0"},"components":COMPONENT_HEALTH,"certification":{"declared_conformance":True}})
    assert bad["production_ready"] is False


def test_roundtrip_plan_and_assessment_are_explicit():
    p=build_roundtrip_plan({"context":CTX,"operations":[{"operation_type":"object-binding","payload":{"object":{"object_type":"dataset","id":"d1","content_hash":"a"*64}}}]})
    assert len(p["stages"])==7 and len(p["operations"])==1 and p["automatic_retry"] is False
    a=assess_roundtrip({"receipts":[{"declared_outcome":"succeeded"},{"declared_outcome":"duplicate"}]})
    assert a["declared_roundtrip_complete"] is True and a["scientific_validity_certified"] is False
    b=assess_roundtrip({"receipts":[{"declared_outcome":"uncertain"}]})
    assert b["declared_roundtrip_complete"] is False


def test_forbidden_auto_authority_is_rejected():
    with pytest.raises(PlatformCoreV3ProductionRuntimeError):
        normalize_operation({"context":CTX,"operation_type":"object-binding","automatic_retry":True,"payload":{"object":{"object_type":"dataset","id":"d1"}}})
