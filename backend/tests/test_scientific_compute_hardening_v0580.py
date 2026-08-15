from __future__ import annotations

import threading
import time

import pytest

from app.scientific_compute_hardening import (
    ScientificComputeHardeningError,
    ScientificComputeManager,
    assess_workload,
    dataset_window,
    policies,
)


def _manager(tmp_path, adapters=None, **kwargs):
    return ScientificComputeManager(str(tmp_path / "compute.sqlite3"), adapters or {"echo": lambda p: {"value": p.get("value")}}, **kwargs)


def test_policies_keep_compute_bounded_and_non_executable():
    p = policies()
    assert p["version"] == "0.58.0"
    assert p["boundedAsyncExecution"] is True
    assert p["persistentResultCache"] is True
    assert p["arbitraryCodeExecution"] is False
    assert p["automaticRemoteCompute"] is False


def test_workload_assessment_distinguishes_interactive_and_async():
    small = assess_workload({"rows": [{"x": 1, "y": 2}] * 20})
    large = assess_workload({"rowCount": 100_000, "columnCount": 20, "stageCount": 12})
    assert small["disposition"] == "interactive"
    assert large["disposition"] == "async-recommended"
    assert large["shape"]["estimatedCells"] == 2_000_000


def test_workload_assessment_rejects_beyond_hard_limits():
    result = assess_workload({"rowCount": 1_000_001, "columnCount": 2})
    assert result["ok"] is False
    assert result["disposition"] == "reject"
    assert "row limit exceeded" in result["violations"]


def test_dataset_window_is_bounded_and_hashed():
    rows = [{"x": i, "y": i * 2, "label": str(i)} for i in range(20)]
    result = dataset_window({"rows": rows, "offset": 5, "limit": 4, "columns": ["x", "y"]})
    assert result["returnedRows"] == 4
    assert result["rows"][0] == {"x": 5, "y": 10}
    assert result["hasMore"] is True
    assert len(result["sourceHash"]) == 64 and len(result["windowHash"]) == 64


def test_sync_execution_caches_by_semantic_request(tmp_path):
    calls = {"count": 0}
    def adapter(payload):
        calls["count"] += 1
        return {"answer": payload["value"] * 2}
    manager = _manager(tmp_path, {"double": adapter})
    try:
        first = manager.execute("double", {"value": 4, "requestId": "a"})
        second = manager.execute("double", {"value": 4, "requestId": "b"})
        assert first["cacheHit"] is False
        assert second["cacheHit"] is True
        assert calls["count"] == 1
        assert first["cacheKey"] == second["cacheKey"]
    finally:
        manager.shutdown()


def test_unregistered_operation_is_rejected(tmp_path):
    manager = _manager(tmp_path)
    try:
        with pytest.raises(ScientificComputeHardeningError):
            manager.execute("python.eval", {"code": "1+1"})
    finally:
        manager.shutdown()


def test_async_job_completes_and_exposes_result(tmp_path):
    manager = _manager(tmp_path, {"echo": lambda p: {"echo": p["value"]}})
    try:
        created = manager.submit("echo", {"value": "science"})
        job_id = created["job"]["id"]
        for _ in range(100):
            status = manager.status(job_id)
            if status["status"] in {"completed", "failed"}:
                break
            time.sleep(0.01)
        assert status["status"] == "completed"
        result = manager.result(job_id)
        assert result["ok"] is True
        assert result["result"] == {"echo": "science"}
    finally:
        manager.shutdown()


def test_async_queue_is_bounded(tmp_path):
    release = threading.Event()
    started = threading.Event()
    def slow(payload):
        started.set(); release.wait(2); return {"ok": payload.get("ok", True)}
    manager = _manager(tmp_path, {"slow": slow}, max_workers=1, max_queued=1)
    try:
        manager.submit("slow", {"ok": True})
        assert started.wait(1)
        manager.submit("slow", {"ok": True, "n": 2})
        with pytest.raises(ScientificComputeHardeningError):
            manager.submit("slow", {"ok": True, "n": 3})
    finally:
        release.set(); manager.shutdown()


def test_queued_job_can_be_cancelled_without_force_termination(tmp_path):
    release = threading.Event(); started = threading.Event()
    def slow(payload):
        started.set(); release.wait(2); return payload
    manager = _manager(tmp_path, {"slow": slow}, max_workers=1, max_queued=3)
    try:
        first = manager.submit("slow", {"n": 1})
        assert started.wait(1)
        second = manager.submit("slow", {"n": 2})
        cancelled = manager.cancel(second["job"]["id"])
        assert cancelled["job"]["status"] == "cancelled"
        assert cancelled["forceTermination"] is False
    finally:
        release.set(); manager.shutdown()


def test_cache_stats_and_clear_are_explicit(tmp_path):
    manager = _manager(tmp_path)
    try:
        manager.execute("echo", {"value": 1})
        stats = manager.cache_stats()
        assert stats["records"] == 1
        cleared = manager.clear_cache()
        assert cleared["cleared"] == 1
        assert manager.cache_stats()["records"] == 0
    finally:
        manager.shutdown()
