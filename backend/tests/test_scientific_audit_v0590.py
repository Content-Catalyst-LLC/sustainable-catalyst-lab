from __future__ import annotations

from copy import deepcopy

from app.reproducible_model_package import build_package
from app.scientific_audit_v0590 import (
    build_redacted_export, data_minimization_review, health, policies, reproducibility_audit,
    scan_surface, scientific_audit, verify_audit,
)


def _model():
    return {
        "id": "audit-model", "title": "Audit model", "family": "declarative-expression",
        "definition": {"equation": "y = a + b*x"},
        "variables": [{"symbol": "x", "role": "input"}, {"symbol": "y", "role": "response"}],
        "parameters": [{"symbol": "a", "value": 1}, {"symbol": "b", "value": 2}],
        "provenance": {"projectId": "audit-project"},
    }


def _package():
    return build_package({"model": _model(), "projectId": "audit-project", "modelVersion": "1.0.0", "dataset": {"mode": "snapshot", "datasetId": "d1", "rows": [{"x": 1, "y": 3}, {"x": 2, "y": 5}]}})["package"]


def test_health_and_policies_are_pre_beta_guardrails():
    assert health()["ok"] and health()["automaticCertification"] is False
    p = policies()
    assert p["capabilities"]["tamperEvidentAuditHash"] is True
    assert p["boundaries"]["automaticHighStakesDecisionAuthorized"] is False


def test_surface_scan_blocks_executable_and_secret_fields_without_echoing_values():
    result = scan_surface({"result": {"python": "print('never echo')", "api_key": "super-secret"}})
    assert result["ok"] is False and result["counts"]["block"] == 2
    rendered = str(result)
    assert "super-secret" not in rendered and "print('never echo')" not in rendered
    assert result["valuesDisclosed"] is False


def test_surface_scan_flags_identifiers_and_high_stakes_context_for_review():
    result = scan_surface({"email": "person@example.org", "clinical": {"diagnosis": "synthetic"}})
    cats = {row["category"] for row in result["findings"]}
    assert "direct-identifier" in cats or "email" in cats
    assert "high-stakes-context" in cats
    assert result["counts"]["review"] >= 2


def test_data_minimization_recommends_dropping_unneeded_identifiers():
    review = data_minimization_review({"purposeNote": "fit temperature response", "requiredColumns": ["temperature"], "rows": [{"email": "a@example.org", "temperature": 30.1}, {"email": "b@example.org", "temperature": 31.2}]})
    email = next(row for row in review["decisions"] if row["column"] == "email")
    temp = next(row for row in review["decisions"] if row["column"] == "temperature")
    assert email["recommendedAction"] == "drop-or-mask"
    assert temp["recommendedAction"] == "retain"
    assert review["rawValuesReturned"] is False


def test_required_identifier_is_retained_only_with_documented_controls():
    review = data_minimization_review({"purposeNote": "record linkage", "requiredColumns": ["employee_id"], "rows": [{"employee_id": "E-1", "signal": 2.0}]})
    row = next(x for x in review["decisions"] if x["column"] == "employee_id")
    assert row["required"] is True
    assert "documented-necessity" in row["recommendedAction"]


def test_redacted_export_removes_executable_fields_and_redacts_identifiers_deterministically():
    payload = {"email": "person@example.org", "api_key": "credential-value-never-return", "analysis": {"python": "bad()", "value": 4}}
    first = build_redacted_export(payload); second = build_redacted_export(payload)
    assert first["exportHash"] == second["exportHash"]
    assert first["payload"]["email"] == "[REDACTED]"
    assert first["payload"]["api_key"] == "[REDACTED]"
    assert "python" not in first["payload"]["analysis"]
    assert "credential-value-never-return" not in str(first["redactions"])


def test_reproducibility_audit_verifies_reproducible_model_package_and_detects_tamper():
    package = _package()
    assert reproducibility_audit({"package": package})["ok"] is True
    broken = deepcopy(package); broken["dataset"]["rows"][0]["y"] = 999
    checked = reproducibility_audit({"package": broken})
    assert checked["ok"] is False


def test_workflow_reproducibility_requires_semantic_and_stage_hashes():
    run = {"workflowHash": "a" * 64, "runHash": "b" * 64, "stages": [{"id": "fit", "outputHash": "c" * 64}, {"id": "cv", "outputHash": "d" * 64}]}
    assert reproducibility_audit({"workflowRun": run})["ok"] is True
    run["stages"][1].pop("outputHash")
    assert reproducibility_audit({"workflowRun": run})["ok"] is False


def test_scientific_audit_blocks_executable_payload_and_never_auto_certifies():
    report = scientific_audit({"target": {"script": "rm -rf never", "value": 1}, "sourceHash": "a" * 64, "modelHash": "b" * 64, "environmentHash": "c" * 64})
    assert report["gate"] == "blocked" and report["ok"] is False
    assert report["automaticCertificationAuthorized"] is False
    assert "rm -rf never" not in str(report)


def test_audit_hash_is_tamper_evident():
    report = scientific_audit({"target": {"x": 1}, "sourceHash": "a" * 64, "modelHash": "b" * 64, "environmentHash": "c" * 64})
    assert verify_audit(report)["ok"] is True
    report["gate"] = "audit-ready" if report["gate"] != "audit-ready" else "blocked"
    assert verify_audit(report)["ok"] is False
