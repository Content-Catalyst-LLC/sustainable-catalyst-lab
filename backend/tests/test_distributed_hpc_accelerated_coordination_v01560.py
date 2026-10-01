from pathlib import Path
import pytest

from app.distributed_hpc_accelerated_coordination_v01560 import (
    DistributedCoordinationError,
    DistributedHPCCoordinationManager,
    MANIFEST_SCHEMA,
    VERSION,
)


class FakeCampaigns:
    def __init__(self):
        self.synced = []

    def execution_batch(self, campaign_id, limit, status):
        handoffs = []
        for i in range(min(limit, 5)):
            h = {
                "schema": "sc-lab-workspace-execution-handoff/0.155.0",
                "campaignId": campaign_id,
                "trialId": f"trial:{i+1}",
                "attempt": 1,
                "method": "simulation.parameter_sweep",
                "parameters": {"rate": 0.1 + i * 0.1},
                "requestedOutputs": ["summary"],
                "randomSeed": 155000 + i,
                "trialSpecHash": f"spec-{i+1}",
                "dispatchRequested": False,
            }
            h["handoffHash"] = f"handoff-{i+1}"
            handoffs.append(h)
        return {"ok": True, "handoffs": handoffs}

    def record_trial_state(self, campaign_id, trial_id, payload, actor):
        self.synced.append((campaign_id, trial_id, payload, actor))
        return {"ok": True}


def manager(tmp_path: Path):
    campaigns = FakeCampaigns()
    m = DistributedHPCCoordinationManager(str(tmp_path / "coord.sqlite3"), campaigns, True, 20, 50, 500, 1000)
    return m, campaigns


def target_payload(scheduler="slurm", accelerator="cuda", gpus=4, parallel=2):
    return {
        "name": "Research cluster A",
        "scheduler": scheduler,
        "queue": "research",
        "capabilities": {
            "cpuCores": 128,
            "memoryGB": 512,
            "gpuCount": gpus,
            "acceleratorKinds": ["cpu", accelerator],
            "gpuMemoryGB": 80,
            "mpi": True,
            "maxWalltimeMinutes": 2880,
            "maxArraySize": 1000,
            "maxParallelJobs": parallel,
        },
    }


def resources(accelerator="cuda", gpus=1):
    return {"cpuCores": 8, "memoryGB": 32, "gpuCount": gpus, "acceleratorKind": accelerator, "gpuMemoryGB": 16, "walltimeMinutes": 120, "mpiRanks": 1, "threadsPerRank": 8}


def test_health_and_policies(tmp_path):
    m, _ = manager(tmp_path)
    h = m.health()
    assert h["ok"] is True and h["version"] == VERSION
    assert h["acceleratorAwarePlacement"] is True
    assert h["hpcJobArrayPlanning"] is True
    assert h["automaticDispatch"] is False
    assert h["automaticFailover"] is False
    p = m.policies()
    assert "slurm" in p["supportedSchedulers"] and "kubernetes" in p["supportedSchedulers"]
    assert p["credentialsStored"] is False


def test_target_registry_and_secret_rejection(tmp_path):
    m, _ = manager(tmp_path)
    t = m.create_target("project:test", target_payload(), "tester")["target"]
    assert t["scheduler"] == "slurm"
    assert t["capabilities"]["gpuCount"] == 4
    assert m.list_targets("project:test")["count"] == 1
    with pytest.raises(DistributedCoordinationError):
        m.create_target("project:test", target_payload() | {"api_token": "do-not-store"}, "tester")


def test_campaign_plan_builds_bounded_waves_and_scheduler_contracts(tmp_path):
    m, _ = manager(tmp_path)
    target = m.create_target("project:test", target_payload(parallel=2), "tester")["target"]
    out = m.create_plan("project:test", {"campaignId": "campaign:test", "targetId": target["id"], "resources": resources(), "limit": 5, "maxParallel": 2}, "tester")
    plan = out["plan"]
    assert len(plan["definition"]["tasks"]) == 5
    assert [w["taskCount"] for w in plan["definition"]["waves"]] == [2, 2, 1]
    assert plan["definition"]["waves"][0]["schedulerBundle"]["scheduler"] == "slurm"
    assert plan["definition"]["automaticDispatch"] is False


def test_accelerator_eligibility_rejects_invalid_target(tmp_path):
    m, _ = manager(tmp_path)
    cpu = m.create_target("project:test", target_payload(scheduler="workspace", accelerator="cpu", gpus=0), "tester")["target"]
    with pytest.raises(DistributedCoordinationError) as exc:
        m.create_plan("project:test", {"campaignId": "campaign:test", "targetId": cpu["id"], "resources": resources("cuda", 1), "limit": 1}, "tester")
    assert "Target does not satisfy resource intent" in exc.value.detail


def test_receipts_and_explicit_campaign_sync(tmp_path):
    m, campaigns = manager(tmp_path)
    target = m.create_target("project:test", target_payload(), "tester")["target"]
    plan = m.create_plan("project:test", {"campaignId": "campaign:test", "targetId": target["id"], "resources": resources(), "limit": 2}, "tester")["plan"]
    result = m.record_receipt(plan["id"], {"trialId": "trial:1", "status": "succeeded", "executionRef": "workspace-run:1", "resultRef": "result:1", "details": {"metrics": {"loss": 0.2}}, "syncCampaignTrial": True}, "tester")
    assert result["campaignTrialSynchronized"] is True
    assert campaigns.synced and campaigns.synced[0][1] == "trial:1"
    summary = m.reconcile(plan["id"])
    assert summary["counts"]["succeeded"] == 1
    assert summary["automaticRetry"] is False


def test_failed_replan_is_advisory_only(tmp_path):
    m, _ = manager(tmp_path)
    t1 = m.create_target("project:test", target_payload(), "tester")["target"]
    t2 = m.create_target("project:test", target_payload(scheduler="kubernetes", parallel=4), "tester")["target"]
    plan = m.create_plan("project:test", {"campaignId": "campaign:test", "targetId": t1["id"], "resources": resources(), "limit": 1}, "tester")["plan"]
    m.record_receipt(plan["id"], {"trialId": "trial:1", "status": "failed", "details": {"error": "worker lost"}}, "tester")
    rp = m.replan_failed(plan["id"])
    assert rp["failedTaskCount"] == 1
    assert any(x["targetId"] == t2["id"] and x["eligible"] for x in rp["candidateTargets"])
    assert rp["automaticFailover"] is False
    assert rp["replanRequiresExplicitAction"] is True


def test_scheduler_bundles_are_descriptive_not_submitted(tmp_path):
    m, _ = manager(tmp_path)
    target = m.create_target("project:test", target_payload(scheduler="pbs"), "tester")["target"]
    plan = m.create_plan("project:test", {"campaignId": "campaign:test", "targetId": target["id"], "resources": resources(), "limit": 3}, "tester")["plan"]
    bundle = m.scheduler_bundle(plan["id"])
    assert bundle["submissionRequested"] is False
    assert bundle["bundles"][0]["scheduler"] == "pbs"
    assert bundle["bundles"][0]["directives"]["ncpus"] == 8


def test_manifest_digest_detects_tampering(tmp_path):
    m, _ = manager(tmp_path)
    target = m.create_target("project:test", target_payload(), "tester")["target"]
    plan = m.create_plan("project:test", {"campaignId": "campaign:test", "targetId": target["id"], "resources": resources(), "limit": 2}, "tester")["plan"]
    manifest = m.manifest(plan["id"])["manifest"]
    assert manifest["schema"] == MANIFEST_SCHEMA
    assert m.verify_manifest({"manifest": manifest})["ok"] is True
    tampered = dict(manifest); tampered["targetId"] = "target:tampered"
    assert m.verify_manifest({"manifest": tampered})["ok"] is False
