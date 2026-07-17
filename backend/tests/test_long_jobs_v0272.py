from __future__ import annotations

import time
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def wait_for(job_id: str, states: set[str], timeout: float = 20.0) -> dict:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        response = client.get(f"/v1/jobs/{job_id}")
        assert response.status_code == 200, response.text
        last = response.json()
        if last["status"] in states:
            return last
        time.sleep(0.05)
    raise AssertionError(f"Job {job_id} did not reach {states}; last={last}")


def submit_sweep(*, key: str, delay_ms: int = 0, cache_mode: str = "refresh", priority: int = 50) -> dict:
    values = [round(index / 100, 4) for index in range(1, 501)]
    response = client.post(
        "/v1/jobs",
        json={
            "operation": "core_run",
            "request": {
                "method": "simulation.parameter_sweep",
                "inputs": {
                    "model": "logistic_growth",
                    "parameter": "rate",
                    "values": values,
                    "fixed": {"initial": 10, "carryingCapacity": 100, "time": 10},
                },
                "parameters": {"checkpointChunkSize": 10, "checkpointDelayMs": delay_ms},
                "project_id": "checkpoint-project",
            },
            "idempotencyKey": key,
            "timeoutSeconds": 20,
            "priority": priority,
            "cacheMode": cache_mode,
        },
    )
    assert response.status_code == 202, response.text
    return response.json()


def test_checkpoint_history_and_partial_results():
    submitted = submit_sweep(key="checkpoint-history", delay_ms=1)
    final = wait_for(submitted["jobId"], {"completed"})
    assert final["checkpointAvailable"] is True
    assert final["checkpointSequence"] >= 2
    assert final["result"]["outputs"]["checkpointed"] is True
    checkpoints = client.get(f"/v1/jobs/{submitted['jobId']}/checkpoints").json()
    assert checkpoints["latestSequence"] == final["checkpointSequence"]
    assert checkpoints["history"]
    assert checkpoints["partialResult"]["totalRows"] == 500


def test_pause_and_resume_uses_checkpoint():
    submitted = submit_sweep(key="pause-resume", delay_ms=15, cache_mode="bypass")
    deadline = time.time() + 10
    current = None
    while time.time() < deadline:
        current = client.get(f"/v1/jobs/{submitted['jobId']}").json()
        if current["status"] == "running" and current["checkpointSequence"] >= 1:
            break
        time.sleep(0.05)
    assert current and current["checkpointSequence"] >= 1
    paused_response = client.post(f"/v1/jobs/{submitted['jobId']}/pause")
    assert paused_response.status_code == 200, paused_response.text
    paused = paused_response.json()
    assert paused["status"] == "paused"
    assert paused["checkpointAvailable"] is True
    sequence = paused["checkpointSequence"]
    resumed_response = client.post(f"/v1/jobs/{submitted['jobId']}/resume")
    assert resumed_response.status_code == 200, resumed_response.text
    final = wait_for(submitted["jobId"], {"completed"})
    assert final["resumedCount"] >= 1
    assert final["checkpointSequence"] >= sequence
    assert final["result"]["outputs"]["resumedFromRow"] > 0


def test_result_cache_returns_completed_job():
    first = submit_sweep(key="cache-first", cache_mode="refresh")
    first_final = wait_for(first["jobId"], {"completed"})
    payload = {
        "operation": "core_run",
        "request": {
            "method": "simulation.parameter_sweep",
            "inputs": {
                "model": "logistic_growth",
                "parameter": "rate",
                "values": [round(index / 100, 4) for index in range(1, 501)],
                "fixed": {"initial": 10, "carryingCapacity": 100, "time": 10},
            },
            "parameters": {"checkpointChunkSize": 10, "checkpointDelayMs": 0},
            "project_id": "checkpoint-project",
        },
        "cacheMode": "use",
    }
    # The cache key includes the request parameters. Match the completed request exactly.
    payload["request"]["parameters"]["checkpointDelayMs"] = 0
    # Create a fresh cached seed with the exact payload first.
    seed = client.post("/v1/jobs", json={**payload, "cacheMode": "refresh", "idempotencyKey": "cache-seed-exact"}).json()
    wait_for(seed["jobId"], {"completed"})
    cached_response = client.post("/v1/jobs", json=payload)
    assert cached_response.status_code == 202, cached_response.text
    cached = cached_response.json()
    assert cached["status"] == "completed"
    assert cached["cacheHit"] is True
    assert cached["result"]["provenance"]["service_version"] == "0.37.0"
    cache_status = client.get("/v1/cache/status").json()
    assert cache_status["records"] >= 1
    assert cache_status["hits"] >= 1
    assert first_final["result"]["outputs"]["rows"]


def test_priority_and_queue_capabilities_are_exposed():
    status = client.get("/v1/queue/status").json()
    assert status["priorityScheduling"] is True
    assert status["checkpointRecovery"] is True
    assert status["maxActiveJobsPerProject"] >= 1
    capabilities = client.get("/v1/capabilities").json()
    assert capabilities["jobs"]["checkpointRecovery"] is True
    assert capabilities["jobs"]["resultCaching"] is True
