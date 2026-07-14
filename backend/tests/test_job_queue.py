from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.jobs import PersistentJobQueue
from app.main import app

client = TestClient(app)


def wait_for(job_id: str, states: set[str], timeout: float = 12) -> dict:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        response = client.get(f"/v1/jobs/{job_id}")
        assert response.status_code == 200, response.text
        last = response.json()
        if last["status"] in states:
            return last
        time.sleep(0.05)
    raise AssertionError(f"Job did not reach {states}; last={last}")


def submit_delay(seconds: float, **extra) -> dict:
    payload = {
        "operation": "core_run",
        "request": {"method": "system.controlled_delay", "inputs": {"seconds": seconds}},
        **extra,
    }
    response = client.post("/v1/jobs", json=payload)
    assert response.status_code == 202, response.text
    return response.json()


def test_persistent_queue_completes_and_lists_jobs():
    submitted = submit_delay(0.05, idempotencyKey="complete-once")
    final = wait_for(submitted["jobId"], {"completed"})
    assert final["progress"] == 100
    assert final["result"]["outputs"]["requestedSeconds"] == 0.05
    listed = client.get("/v1/jobs", params={"limit": 10}).json()
    assert any(row["jobId"] == submitted["jobId"] for row in listed["jobs"])
    queue = client.get("/v1/queue/status").json()
    assert queue["persistent"] is True
    assert queue["storage"] == "sqlite-wal"


def test_active_duplicate_is_deduplicated():
    first = submit_delay(0.3, idempotencyKey="same-request")
    second = submit_delay(0.3, idempotencyKey="same-request")
    assert first["jobId"] == second["jobId"]
    assert second["deduplicated"] is True
    wait_for(first["jobId"], {"completed"})


def test_hard_timeout_terminates_worker():
    submitted = submit_delay(2, timeoutSeconds=1, maxAttempts=1)
    final = wait_for(submitted["jobId"], {"timed_out"}, timeout=8)
    assert final["error"]["code"] == "job_timeout"
    assert final["finishedAt"]


def test_cancel_and_manual_retry():
    submitted = submit_delay(0.8, idempotencyKey="cancel-retry")
    wait_for(submitted["jobId"], {"running"})
    cancelled = client.post(f"/v1/jobs/{submitted['jobId']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    retried = client.post(f"/v1/jobs/{submitted['jobId']}/retry")
    assert retried.status_code == 200, retried.text
    assert retried.json()["status"] == "queued"
    final = wait_for(submitted["jobId"], {"completed"})
    assert final["manualRetries"] == 1


def test_worker_health_endpoint():
    submitted = submit_delay(0.4, idempotencyKey="worker-health")
    wait_for(submitted["jobId"], {"running"})
    workers = client.get("/v1/workers").json()
    assert workers["model"] == "isolated-process-workers"
    assert workers["configuredWorkers"] >= 1
    assert any(row["jobId"] == submitted["jobId"] for row in workers["active"])
    wait_for(submitted["jobId"], {"completed"})


def test_restart_recovery_returns_running_job_to_queue(tmp_path: Path):
    database = tmp_path / "recovery.sqlite3"
    queue_one = PersistentJobQueue(str(database))
    record, _ = queue_one.submit(
        operation="core_run",
        payload={"method": "system.controlled_delay", "inputs": {"seconds": 1.5}},
        auth={"mode": "test", "client": "pytest"},
        timeout_seconds=5,
        max_attempts=1,
        idempotency_key="restart-recovery",
    )
    deadline = time.time() + 4
    while time.time() < deadline:
        current = queue_one.get(record["jobId"])
        if current and current["status"] == "running":
            break
        time.sleep(0.05)
    assert queue_one.get(record["jobId"])["status"] == "running"
    queue_one.stop()

    queue_two = PersistentJobQueue(str(database))
    recovered = queue_two.get(record["jobId"])
    assert recovered["status"] == "queued"
    assert "Recovered" in recovered["progressMessage"]
    queue_two.start()
    deadline = time.time() + 8
    while time.time() < deadline:
        recovered = queue_two.get(record["jobId"])
        if recovered and recovered["status"] == "completed":
            break
        time.sleep(0.05)
    assert recovered["status"] == "completed"
    queue_two.stop()
