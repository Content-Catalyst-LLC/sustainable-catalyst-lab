from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.connected_platform_beta import BetaPlatformError, ConnectedPlatformBetaManager, policies


def manager(tmp_path: Path, telemetry: bool = True) -> ConnectedPlatformBetaManager:
    return ConnectedPlatformBetaManager(str(tmp_path / "beta.sqlite3"), True, telemetry, 10000, 10000)


def ready_components():
    return {key: {"ok": True, "status": "ready", "serviceVersion": "0.40.0"} for key in ("interoperability", "typedHandoffs", "publicIntegrations", "governance", "securityPrivacy", "recovery", "performanceValidation")}


def test_health_policy_and_catalog(tmp_path):
    store = manager(tmp_path)
    assert store.health()["serviceVersion"] == "0.40.0"
    assert store.health()["releaseStage"] == "beta"
    assert policies(True, True)["generalAvailabilityClaim"] is False
    assert len(store.catalog()["projectTemplates"]) == 3


def test_cohort_and_sequential_onboarding(tmp_path):
    store = manager(tmp_path)
    cohort = store.create_cohort({"id":"cohort-one","name":"Institutional Beta One","institutionId":"inst-one","status":"active","goals":["validate workflow"]}, "alice")["cohort"]
    assert cohort["status"] == "active"
    onboarding = store.start_onboarding({"id":"onboard-one","cohortId":"cohort-one","institutionId":"inst-one","principalId":"alice","workspaceId":"research-one"}, "alice")["onboarding"]
    assert onboarding["stage"] == "institution"
    advanced = store.advance_onboarding("onboard-one", {"stage":"identity","completedItems":["institution profile"]}, "alice")["onboarding"]
    assert advanced["stage"] == "identity"
    with pytest.raises(BetaPlatformError):
        store.advance_onboarding("onboard-one", {"stage":"data"}, "alice")


def test_guided_project_advances_and_preserves_handoff_refs(tmp_path):
    store = manager(tmp_path)
    project = store.create_project({"id":"project-one","templateId":"scenario-to-decision","title":"Wetland scenario","workspaceId":"research-one","researchQuestion":"What changes under drought?"}, "alice")["project"]
    assert project["stage"] == "define"
    result = store.advance_project("project-one", {"stage":"source","outputs":{"evidence":"sha256:abc"},"handoffs":[{"product":"decision-studio","resourceId":"packet-one"}]}, "alice")["project"]
    assert result["stage"] == "source"
    assert result["handoffs"][0]["product"] == "decision-studio"
    with pytest.raises(BetaPlatformError):
        store.advance_project("project-one", {"stage":"execute"}, "alice")


def test_telemetry_requires_opt_in_and_hashes_identifiers(tmp_path):
    store = manager(tmp_path, True)
    with pytest.raises(BetaPlatformError):
        store.record_telemetry({"eventType":"module.opened","workspaceId":"secret-workspace"}, "alice")
    event = store.record_telemetry({"id":"event-one","eventType":"module.opened","workspaceId":"secret-workspace","optIn":True,"properties":{"module":"experiment-framework"}}, "alice")["telemetryEvent"]
    assert event["actorHash"] != "alice"
    assert event["workspaceHash"] != "secret-workspace"
    assert event["rawIdentifiersStored"] is False
    assert store.telemetry_summary()["total"] == 1


def test_sensitive_beta_payloads_are_rejected(tmp_path):
    store = manager(tmp_path)
    with pytest.raises(BetaPlatformError):
        store.create_feedback({"title":"Bad payload","description":"contains secret","severity":"low","secret":"do-not-store"}, "alice")
    with pytest.raises(BetaPlatformError):
        store.create_project({"templateId":"evidence-to-experiment","title":"Bad","workspaceId":"one","callback":"https://example.org"}, "alice")


def test_feedback_limitations_support_and_readiness_blockers(tmp_path):
    store = manager(tmp_path)
    feedback = store.create_feedback({"id":"feedback-one","category":"bug","severity":"critical","title":"Critical beta bug","description":"The guided stage cannot advance"}, "alice")["feedback"]
    assert feedback["severity"] == "critical"
    store.create_limitation({"id":"limit-one","severity":"medium","title":"Offline package size","description":"Large packages require testing","workaround":"Split the package"}, "alice")
    store.create_support_case({"id":"support-one","severity":"high","title":"Institution setup","summary":"Need onboarding assistance"}, "alice")
    report = store.evaluate_readiness({"id":"readiness-one"}, "release-manager", ready_components())["report"]
    assert report["status"] == "blocked"
    store.update_feedback("feedback-one", {"status":"resolved","resolution":"Fixed and verified"}, "alice")
    report2 = store.evaluate_readiness({"id":"readiness-two"}, "release-manager", ready_components())["report"]
    assert report2["status"] == "ready"
    assert report2["generalAvailabilityClaim"] is False


def test_component_failure_blocks_beta_expansion(tmp_path):
    store = manager(tmp_path)
    components = ready_components(); components["securityPrivacy"] = {"ok":False,"status":"degraded"}
    report = store.evaluate_readiness({"id":"readiness-components"}, "release-manager", components)["report"]
    assert report["status"] == "blocked"
    assert any(item.get("id") == "securityPrivacy" for item in report["blockers"])


def test_timeline_is_hash_chained_and_detects_tampering(tmp_path):
    store = manager(tmp_path)
    store.create_cohort({"id":"cohort-one","name":"One","institutionId":"inst-one"}, "alice")
    store.create_feedback({"id":"feedback-one","category":"usability","severity":"low","title":"Label","description":"Improve label"}, "bob")
    assert store.verify_timeline()["valid"] is True
    with store._connect() as db:
        db.execute("UPDATE beta_events SET payload_json='{}' WHERE seq=1")
    assert store.verify_timeline()["valid"] is False


def test_json_contracts_validate(tmp_path):
    import jsonschema
    root = Path(__file__).resolve().parents[2]
    for name in ("beta-cohort-v0400.schema.json","beta-onboarding-v0400.schema.json","guided-research-project-v0400.schema.json","beta-telemetry-event-v0400.schema.json","beta-feedback-v0400.schema.json","beta-readiness-report-v0400.schema.json"):
        schema = json.loads((root / "contracts" / name).read_text())
        jsonschema.validators.validator_for(schema).check_schema(schema)


def test_fastapi_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "beta-test-key")
    monkeypatch.setenv("SC_LAB_PLATFORM_BETA_DB_PATH", str(tmp_path / "routes.sqlite3"))
    monkeypatch.setenv("SC_LAB_PLATFORM_BETA_TELEMETRY_ENABLED", "1")
    from app import config
    config.Settings.version = "0.40.0"
    import importlib
    import app.main as main
    importlib.reload(main)
    client = TestClient(main.app)
    headers={"X-SC-Lab-Key":"beta-test-key"}
    health=client.get("/v1/platform-beta/health",headers=headers)
    assert health.status_code==200 and health.json()["serviceVersion"]=="0.40.0"
    cohort=client.post("/v1/platform-beta/cohorts",headers=headers,json={"id":"route-cohort","name":"Route Cohort","institutionId":"inst-route"})
    assert cohort.status_code==200
    templates=client.get("/v1/platform-beta/project-templates",headers=headers)
    assert templates.status_code==200 and len(templates.json()["projectTemplates"])==3
