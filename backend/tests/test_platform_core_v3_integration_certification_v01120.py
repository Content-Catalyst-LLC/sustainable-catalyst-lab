import pytest
from app.platform_core_v3_integration_certification_v01120 import *

CTX={"project_ref":"project:p1","session_id":"12","session_key":"s12","title":"Certification","workflow_ref":"lab:workflow:w1","project_state_ref":"core:state:12","researcher_ref":"researcher:r1"}

def test_catalog_and_manifest_boundaries():
    c=catalog(); m=manifest(); h=health()
    assert c["layer_count"]==8 and c["case_count"]==18
    assert h["lab_release_version"]=="0.112.0" and h["minimum_core_release"]=="3.0.0"
    assert m["boundaries"]["automatic_core_submission"] is False and m["boundaries"]["core_determines_truth"] is False

def test_suite_product_cases_and_run_plans_are_non_submitting():
    s=build_suite_plan({"context":CTX}); p=build_product_plan({"suite_id":"suite:1"}); cases=build_case_plans({"suite_id":"suite:1"}); r=build_run_plan({"suite_id":"suite:1","product_id":"product-row:1"})
    assert s["endpoint"].endswith("/suites") and s["automatic_submission"] is False
    assert p["data"]["product_ref"]==PRODUCT_REF and "scientific-investigation" in p["data"]["metadata"]["integration_layers"]
    assert cases["count"]==18 and all(x["endpoint"].endswith("/cases") for x in cases["cases"])
    assert r["automatic_product_invocation"] is False

def test_case_result_and_checks_preserve_declared_status_only():
    x=build_case_result_plan({"run_id":"r1","case_id":"c1","status":"pass","evidence_refs":["e1"]})
    e=build_exchange_check_plan({"run_id":"r1","source_product_ref":"product:core","target_product_ref":PRODUCT_REF,"exchange_ref":"x1","status":"pass"})
    t=build_trace_check_plan({"run_id":"r1","object_ref":"lab:dataset:d1","status":"pass"})
    q=build_reproduction_check_plan({"run_id":"r1","project_ref":"project:p1","status":"pass"})
    assert x["scientific_validity_assessed"] is False
    assert e["automatic_submission"] is t["automatic_submission"] is q["automatic_submission"] is False

def test_evidence_and_finding_are_certification_records_not_science_truth():
    e=build_evidence_plan({"evidence_key":"http","run_id":"r1","evidence_type":"trace","evidence_ref":"artifact:a1"})
    f=build_finding_plan({"finding_key":"f1","run_id":"r1","category":"contract","statement":"Round trip preserved object ref"})
    assert e["scientific_validity_assessed"] is False and f["scientific_validity_assessed"] is False

def test_roundtrip_assessment_requires_all_cases_and_does_not_certify_science():
    results=[{"case_key":x[0],"status":"pass"} for x in CASE_CATALOG]
    a=assess_roundtrip({"results":results})
    assert a["declared_conformance"] is True and a["scientific_validity_certified"] is False and a["truth_determined"] is False
    b=assess_roundtrip({"results":results[:-1]})
    assert b["declared_conformance"] is False and b["missing_required_cases"]

def test_compatibility_report_matches_core_v297_boundaries_and_core_v3_plus():
    ready={"release":"3.1.0","contract":CORE_CERTIFICATION_CONTRACT}
    for k in ["certification_suite_registry_by_core","certification_product_registry_by_core","conformance_case_registry_by_core","conformance_run_registry_by_core","conformance_result_registry_by_core","exchange_check_registry_by_core","trace_check_registry_by_core","reproduction_check_registry_by_core","certification_evidence_registry_by_core","certification_finding_registry_by_core","revision_history_by_core","immutable_certification_snapshots_by_core"]: ready[k]=True
    for k in ["invoke_product_by_core","execute_conformance_case_by_core","certify_scientific_validity_by_core","certify_product_quality_by_core","authorize_product_by_certification_by_core","rank_products_by_core","infer_missing_evidence_by_core","infer_reproducibility_by_core","resolve_failed_case_by_core","determine_truth_by_core"]: ready[k]=False
    r=compatibility_report(ready); assert r["status"]=="compatible" and r["compatible"] is True
    ready["determine_truth_by_core"]=True; assert compatibility_report(ready)["compatible"] is False

def test_full_submission_plan_is_explicit_and_non_automatic():
    p=build_full_submission_plan({"context":CTX})
    assert len(p["steps"])==7 and p["automatic_submission"] is False and p["automatic_case_execution"] is False and p["automatic_truth_determination"] is False

def test_forbidden_authority_is_rejected():
    with pytest.raises(PlatformCoreV3IntegrationCertificationError): build_suite_plan({"context":CTX,"certify_scientific_validity_by_core":True})
