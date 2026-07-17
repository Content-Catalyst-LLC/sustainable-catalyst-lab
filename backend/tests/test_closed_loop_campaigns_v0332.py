from __future__ import annotations

import copy
import importlib
from pathlib import Path

import pytest

from app.closed_loop_campaigns import (
    ClosedLoopCampaignManager,
    ClosedLoopError,
    normalize_loop,
    sign_measurement,
)


class StubCampaigns:
    def __init__(self):
        self.campaigns = {
            "adaptive-calibration": {
                "id": "adaptive-calibration",
                "status": "draft",
                "trials": [],
            }
        }
        self.preview_parameters = {"temperature": 40.0, "flow": 2.0}
        self.counter = 0

    def get(self, campaign_id):
        if campaign_id not in self.campaigns:
            raise Exception("campaign missing")
        return {"ok": True, "campaign": copy.deepcopy(self.campaigns[campaign_id])}

    def start_campaign(self, campaign_id):
        campaign = self.campaigns[campaign_id]
        campaign["status"] = "running"
        return self.advance(campaign_id, 1, False)

    def advance(self, campaign_id, count=1, reconcile_first=True):
        del reconcile_first
        campaign = self.campaigns[campaign_id]
        for _ in range(count or 1):
            self.counter += 1
            campaign["trials"].append({
                "id": f"trial-{self.counter}",
                "status": "running",
                "workflowRunId": f"run-{self.counter}",
                "parameters": {"temperature": 30.0 + self.counter, "flow": 1.0},
                "objectiveValue": None,
                "createdAt": "2026-07-17T00:00:00+00:00",
            })
        return {"ok": True, "launchedCount": count or 1, "campaign": copy.deepcopy(campaign)}

    def complete_latest(self, objective=1.0):
        trial = self.campaigns["adaptive-calibration"]["trials"][-1]
        trial["status"] = "completed"
        trial["objectiveValue"] = objective
        trial["completedAt"] = "2026-07-17T00:01:00+00:00"

    def reconcile(self, campaign_id, auto_advance=False):
        del auto_advance
        return {"ok": True, "campaign": copy.deepcopy(self.campaigns[campaign_id])}

    def preview_proposal(self, campaign_id):
        self.get(campaign_id)
        return {"ok": True, "parameters": copy.deepcopy(self.preview_parameters), "proposal": {"source": "surrogate"}}

    def observe(self, campaign_id, payload):
        campaign = self.campaigns[campaign_id]
        self.counter += 1
        trial = {
            "id": f"observed-{self.counter}",
            "status": "completed",
            "workflowRunId": None,
            "parameters": copy.deepcopy(payload["parameters"]),
            "objectiveValue": float(payload["objectiveValue"]),
            "result": copy.deepcopy(payload.get("result", {})),
        }
        campaign["trials"].append(trial)
        return {"ok": True, "campaign": copy.deepcopy(campaign), "trial": copy.deepcopy(trial)}


def loop_payload(**changes):
    payload = {
        "id": "reactor-loop",
        "title": "Bench reactor closed loop",
        "projectId": "test",
        "campaignId": "adaptive-calibration",
        "mode": "instrument",
        "adapter": {"gatewayId": "bench-gateway", "protocol": "signed-envelope-v1", "capabilities": ["temperature", "flow"]},
        "safety": {
            "signalLimits": {"temperature": {"min": 10, "max": 90}},
            "parameterLimits": {
                "temperature": {"min": 20, "max": 80, "maxStepDelta": 20},
                "flow": {"min": 0.5, "max": 5},
            },
            "emergencyStopSignals": ["emergencyStop"],
            "requireCommandApproval": True,
            "maxConsecutiveFailures": 2,
        },
        "observation": {"objectivePath": "objectiveValue", "parameterPath": "parameters", "signalsPath": "signals", "requireSignature": False},
        "control": {"autoAdvance": True, "maxCycles": 5, "stopOnCampaignCompletion": True},
    }
    payload.update(changes)
    return payload


def test_normalize_loop_contract_and_rejections():
    record = normalize_loop(loop_payload())
    assert record["schema"].endswith("0.33.2")
    assert record["adapter"]["directNetworkCallbacks"] is False
    assert record["safety"]["requireCommandApproval"] is True
    with pytest.raises(ClosedLoopError):
        normalize_loop({**loop_payload(), "mode": "instrument", "adapter": {}})
    with pytest.raises(ClosedLoopError):
        normalize_loop({**loop_payload(), "safety": {"signalLimits": {"temperature": {"min": 90, "max": 10}}}})


def test_instrument_command_approval_dispatch_measurement_cycle(tmp_path: Path):
    campaigns = StubCampaigns()
    manager = ClosedLoopCampaignManager(str(tmp_path / "closed.sqlite3"), campaigns)
    manager.save(loop_payload())
    started = manager.start_loop("reactor-loop")
    command = started["command"]["command"]
    assert command["status"] == "pending-approval"
    approved = manager.approve_command("reactor-loop", command["id"], "scientist", "safe bench setpoint")
    assert approved["command"]["status"] == "ready"
    dispatched = manager.dispatch_command("reactor-loop", command["id"])
    assert dispatched["command"]["status"] == "dispatched"
    assert dispatched["envelope"]["gatewayId"] == "bench-gateway"
    observed = manager.ingest_measurement("reactor-loop", {
        "id": "measurement-1",
        "gatewayId": "bench-gateway",
        "commandId": command["id"],
        "parameters": command["parameters"],
        "signals": {"temperature": 41.2, "emergencyStop": False},
        "objectiveValue": 0.42,
    })
    assert observed["measurement"]["objectiveValue"] == 0.42
    assert observed["loop"]["cycleCount"] == 1
    assert observed["loop"]["commands"][0]["status"] in {"pending-approval", "acknowledged"}
    assert campaigns.campaigns["adaptive-calibration"]["trials"][-1]["objectiveValue"] == 0.42


def test_measurement_deduplication_and_signature(tmp_path: Path):
    campaigns = StubCampaigns()
    secret = "measurement-secret"
    manager = ClosedLoopCampaignManager(str(tmp_path / "closed.sqlite3"), campaigns, measurement_secret=secret)
    manager.save(loop_payload(observation={"objectivePath": "objectiveValue", "parameterPath": "parameters", "signalsPath": "signals", "requireSignature": True}))
    command = manager.start_loop("reactor-loop")["command"]["command"]
    manager.approve_command("reactor-loop", command["id"])
    manager.dispatch_command("reactor-loop", command["id"])
    payload = {
        "gatewayId": "bench-gateway",
        "commandId": command["id"],
        "parameters": command["parameters"],
        "signals": {"temperature": 40.0},
        "objectiveValue": 0.5,
    }
    payload["signature"] = sign_measurement(secret, payload)
    first = manager.ingest_measurement("reactor-loop", payload)
    assert first["measurement"]["signatureValid"] is True
    second = manager.ingest_measurement("reactor-loop", payload)
    assert second["deduplicated"] is True


def test_safety_interlock_emergency_stops_loop(tmp_path: Path):
    campaigns = StubCampaigns()
    manager = ClosedLoopCampaignManager(str(tmp_path / "closed.sqlite3"), campaigns)
    manager.save(loop_payload())
    command = manager.start_loop("reactor-loop")["command"]["command"]
    with pytest.raises(ClosedLoopError) as caught:
        manager.ingest_measurement("reactor-loop", {
            "gatewayId": "bench-gateway",
            "commandId": command["id"],
            "parameters": command["parameters"],
            "signals": {"temperature": 120.0, "emergencyStop": True},
            "objectiveValue": 99,
        })
    assert caught.value.status_code == 409
    loop = manager.get("reactor-loop")["loop"]
    assert loop["status"] == "emergency-stopped"
    assert "interlock" in loop["stopReason"]


def test_simulation_trials_import_as_checkpointed_cycles(tmp_path: Path):
    campaigns = StubCampaigns()
    manager = ClosedLoopCampaignManager(str(tmp_path / "closed.sqlite3"), campaigns)
    manager.save(loop_payload(id="simulation-loop", mode="simulation", adapter={"protocol": "simulation-workflow-v1"}, safety={"requireCommandApproval": False}, control={"autoAdvance": False, "maxCycles": 3, "stopOnCampaignCompletion": False}))
    started = manager.start_loop("simulation-loop")
    assert started["campaign"]["campaign"]["trials"][0]["status"] == "running"
    campaigns.complete_latest(0.25)
    reconciled = manager.reconcile("simulation-loop")
    assert reconciled["importedSimulationCycles"] == 1
    assert reconciled["loop"]["cycles"][0]["source"] == "simulation"
    assert reconciled["loop"]["cycles"][0]["objectiveValue"] == 0.25


def test_persistence_pause_resume_and_timeline(tmp_path: Path):
    campaigns = StubCampaigns()
    db = str(tmp_path / "closed.sqlite3")
    manager = ClosedLoopCampaignManager(db, campaigns)
    manager.save(loop_payload())
    manager.start_loop("reactor-loop")
    assert manager.pause("reactor-loop", "inspect sensor")["loop"]["status"] == "paused"
    assert manager.resume("reactor-loop")["loop"]["status"] == "running"
    reopened = ClosedLoopCampaignManager(db, campaigns)
    assert reopened.get("reactor-loop")["loop"]["status"] == "running"
    events = reopened.timeline("reactor-loop")["events"]
    assert {item["eventType"] for item in events} >= {"loop-saved", "loop-started", "loop-paused", "loop-resumed"}


def test_fastapi_closed_loop_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", str(tmp_path / "schedules.sqlite3"))
    monkeypatch.setenv("SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH", str(tmp_path / "campaigns.sqlite3"))
    monkeypatch.setenv("SC_LAB_CLOSED_LOOP_DB_PATH", str(tmp_path / "closed.sqlite3"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "closed-loop-key")
    import app.config as config
    import app.main as main
    importlib.reload(config)
    importlib.reload(main)
    from fastapi.testclient import TestClient
    headers = {"X-SC-Lab-Key": "closed-loop-key"}
    workflow = {"id": "campaign-workflow", "projectId": "test", "nodes": [{"id": "evaluate", "method": "dataset.profile", "request": {"inputs": {"records": []}}}]}
    campaign = {
        "id": "adaptive-calibration", "workflowId": "campaign-workflow", "projectId": "test",
        "parameterSpace": {"temperature": {"type": "continuous", "min": 20, "max": 80}, "flow": {"type": "continuous", "min": 0.5, "max": 5}},
        "objective": {"path": "nodes.evaluate.result.metrics.score", "goal": "minimize"},
        "strategy": {"type": "random", "randomSeed": 332}, "budget": {"maxTrials": 5, "maxFailures": 2, "maxConcurrentTrials": 1},
        "run": {"parameterInputPath": "campaign.parameters", "autoAdvance": False},
    }
    with TestClient(main.app) as client:
        assert client.post("/v1/workflows", json=workflow, headers=headers).status_code == 200
        assert client.post("/v1/experiment-campaigns", json=campaign, headers=headers).status_code == 200
        assert client.post("/v1/closed-loop-campaigns/validate", json=loop_payload(), headers=headers).status_code == 200
        saved = client.post("/v1/closed-loop-campaigns", json=loop_payload(), headers=headers)
        assert saved.status_code == 200
        started = client.post("/v1/closed-loop-campaigns/reactor-loop/start", headers=headers)
        assert started.status_code == 200
        command = started.json()["command"]["command"]
        assert client.post(f"/v1/closed-loop-campaigns/reactor-loop/commands/{command['id']}/approve", json={"operator": "admin"}, headers=headers).status_code == 200
        assert client.post(f"/v1/closed-loop-campaigns/reactor-loop/commands/{command['id']}/dispatch", headers=headers).status_code == 200
        health = client.get("/v1/closed-loop-campaigns/health", headers=headers).json()
        assert health["version"] == "0.33.2"
        assert health["serviceVersion"] == "0.34.2"
        assert client.get("/health").json()["closedLoopCampaigns"]["version"] == "0.33.2"
