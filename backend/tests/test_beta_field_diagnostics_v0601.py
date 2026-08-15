from __future__ import annotations
from copy import deepcopy
import pytest

from app.beta_field_diagnostics_v0601 import (
    BetaFieldDiagnosticsError, analyze_soak, build_diagnostic_packet, health,
    integration_probe, normalize_runtime_snapshot, policies, scenarios,
    verify_diagnostic_packet,
)


def _runtime(release="0.60.1", integrity="verified"):
    return {
        "release": release,
        "platformVersion": "1.0.0",
        "activeModule": "workflow-orchestration",
        "visibility": "visible",
        "online": True,
        "connectivity": {"wordpressRest": True, "computeBackend": True},
        "storage": {"projectStore": True, "localStorage": True, "sessionStorage": True},
        "integrity": {"state": integrity, "partialInstallRisk": False},
        "dom": {"primaryRailCount": 6, "applicationCardCount": 3, "graphStudioPresent": True, "workflowWorkspacePresent": True},
        "errorCategories": [],
    }


def _observations(fail_first=False):
    endpoints = ["diagnostics", "integrated-beta", "scientific-audit", "compute-hardening", "workflow-composer"]
    rows = []
    for cycle in range(1, 5):
        for i, endpoint in enumerate(endpoints):
            ok = not (fail_first and cycle == 1 and endpoint == "compute-hardening")
            rows.append({"cycle": cycle, "endpoint": endpoint, "ok": ok, "status": 200 if ok else 503, "latencyMs": 40 + cycle * 5 + i, "errorCategory": "" if ok else "http"})
    return rows


def test_health_and_policy_define_stabilization_without_automatic_repair():
    assert health()["ok"] is True
    p = policies()
    assert p["betaStabilizationRelease"] is True
    assert p["automaticRepairAuthorized"] is False
    assert p["externalTelemetryAuthorized"] is False
    assert p["rawScientificDataAccepted"] is False


def test_runtime_snapshot_is_metadata_only_and_deterministic():
    first = normalize_runtime_snapshot(_runtime())
    second = normalize_runtime_snapshot(_runtime())
    assert first["schema"] == "sc-lab-beta-runtime-snapshot/0.60.1"
    assert first["snapshotHash"] == second["snapshotHash"]
    assert first["dom"]["primaryRailCount"] == 6


def test_runtime_snapshot_rejects_raw_data_and_credentials_even_when_nested():
    with pytest.raises(BetaFieldDiagnosticsError):
        normalize_runtime_snapshot({"runtime": {"dataset": {"rows": [{"x": 1}]}}})
    with pytest.raises(BetaFieldDiagnosticsError):
        normalize_runtime_snapshot({"runtime": {"auth": {"token": "never"}}})


def test_integration_probe_passes_complete_runtime_contract():
    result = integration_probe({"runtime": _runtime()})
    assert result["status"] == "pass"
    assert result["failureDomains"] == []
    assert len(result["probeHash"]) == 64
    assert result["automaticRepairAuthorized"] is False


def test_integration_probe_localizes_release_and_integrity_failure():
    runtime = _runtime(release="0.60.0", integrity="degraded")
    result = integration_probe({"runtime": runtime})
    assert result["status"] == "fail"
    assert "release-line" in result["failureDomains"]
    assert "integrity" in result["failureDomains"]
    assert result["repairHints"]


def test_scenario_catalog_has_eight_bounded_runtime_scenarios():
    result = scenarios()
    assert len(result["scenarios"]) == 8
    assert {row["id"] for row in result["scenarios"]} >= {"cross-studio-cycle", "transient-recovery", "sustained-stability"}
    assert len(result["scenarioHash"]) == 64


def test_all_green_bounded_soak_passes_and_is_deterministic():
    first = analyze_soak({"observations": _observations()})
    second = analyze_soak({"observations": _observations()})
    assert first["status"] == "pass"
    assert first["completeCycles"] == 4 and first["fullyGreenCycles"] == 4
    assert first["soakHash"] == second["soakHash"]


def test_transient_failure_recovers_but_remains_review_warning():
    result = analyze_soak({"observations": _observations(fail_first=True)})
    assert result["status"] == "warn"
    recovery = next(row for row in result["scenarios"] if row["id"] == "transient-recovery")
    assert recovery["status"] == "pass"


def test_soak_rejects_unsupported_or_unbounded_observations():
    with pytest.raises(BetaFieldDiagnosticsError):
        analyze_soak({"observations": [{"cycle": 1, "endpoint": "arbitrary-url", "ok": True}]})
    with pytest.raises(BetaFieldDiagnosticsError):
        analyze_soak({"observations": _observations() * 5})


def test_diagnostic_packet_is_metadata_only_deterministic_and_tamper_evident():
    soak = analyze_soak({"observations": _observations()})
    first = build_diagnostic_packet({"runtime": _runtime(), "soakResult": soak})["packet"]
    second = build_diagnostic_packet({"runtime": _runtime(), "soakResult": soak})["packet"]
    assert first["packetHash"] == second["packetHash"]
    assert first["boundaries"]["rawScientificDataIncluded"] is False
    assert first["boundaries"]["externalTelemetry"] is False
    assert verify_diagnostic_packet({"packet": first})["ok"] is True
    broken = deepcopy(first); broken["soakStatus"] = "fail"
    assert verify_diagnostic_packet({"packet": broken})["ok"] is False
