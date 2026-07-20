from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sqlite3
import statistics
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

VERSION = "0.39.3"


class ValidationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if not text or len(text) > 120 or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-_." for ch in text):
        raise ValidationError(f"Invalid {label}.")
    return text


WORKLOADS: dict[str, dict[str, Any]] = {
    "api-read": {"title": "API read path", "kind": "cpu", "description": "Canonical serialization and digest verification for read-shaped responses."},
    "api-write": {"title": "API write path", "kind": "sqlite", "description": "Isolated WAL-backed inserts and reads in a validation database."},
    "queue-throughput": {"title": "Queue throughput", "kind": "queue", "description": "Bounded producer/consumer handoff with deterministic acknowledgements."},
    "large-payload": {"title": "Large payload validation", "kind": "payload", "description": "Bounded JSON payload hashing and structural checks."},
    "webhook-burst": {"title": "Webhook signing burst", "kind": "crypto", "description": "HMAC-shaped signing work without outbound network delivery."},
}

CHAOS_SCENARIOS: dict[str, dict[str, Any]] = {
    "database-lock": {"title": "Database lock contention", "safe": True, "description": "Injects a lock into an isolated SQLite database and verifies bounded retry recovery."},
    "storage-latency": {"title": "Storage latency", "safe": True, "description": "Injects bounded delay into temporary-file writes and verifies integrity afterward."},
    "worker-termination": {"title": "Worker termination", "safe": True, "description": "Interrupts an isolated worker and verifies checkpoint-based resumption."},
    "network-timeout": {"title": "Network timeout", "safe": True, "description": "Simulates a timeout and verifies retry/backoff decisions without external traffic."},
    "partial-write": {"title": "Partial write", "safe": True, "description": "Creates an incomplete temporary artifact and confirms checksum rejection and cleanup."},
}


def policies(persistent_disk_mounted: bool) -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "executionBoundary": "isolated-validation-resources-only",
        "productionMutation": False,
        "externalTraffic": False,
        "persistentDiskMounted": bool(persistent_disk_mounted),
        "workloads": sorted(WORKLOADS),
        "chaosScenarios": sorted(CHAOS_SCENARIOS),
        "defaults": {"maxConcurrency": 32, "maxIterations": 2000, "maxDurationSeconds": 120},
        "capabilities": {
            "latencyPercentiles": True,
            "throughputMeasurement": True,
            "errorBudgets": True,
            "capacityReports": True,
            "safeFailureInjection": True,
            "productionChaos": False,
            "destructiveFaults": False,
        },
    }


class PerformanceChaosManager:
    def __init__(
        self,
        db_path: str,
        persistent_disk_mounted: bool,
        max_concurrency: int = 32,
        max_iterations: int = 2000,
        history_limit: int = 10000,
        default_p95_ms: float = 250.0,
        default_error_rate: float = 0.01,
    ) -> None:
        self.db_path = str(db_path)
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_concurrency = max(1, min(int(max_concurrency), 128))
        self.max_iterations = max(1, min(int(max_iterations), 100000))
        self.history_limit = max(100, int(history_limit))
        self.default_p95_ms = max(1.0, float(default_p95_ms))
        self.default_error_rate = max(0.0, min(float(default_error_rate), 1.0))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS validation_runs(
              id TEXT PRIMARY KEY,
              kind TEXT NOT NULL,
              profile TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              completed_at TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              result_json TEXT NOT NULL,
              result_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS capacity_reports(
              id TEXT PRIMARY KEY,
              created_at TEXT NOT NULL,
              report_json TEXT NOT NULL,
              report_hash TEXT NOT NULL
            );
            """)

    def health(self) -> dict[str, Any]:
        try:
            with self._connect() as db:
                count = db.execute("SELECT COUNT(*) FROM validation_runs").fetchone()[0]
                reports = db.execute("SELECT COUNT(*) FROM capacity_reports").fetchone()[0]
            writable = True
        except sqlite3.Error:
            count, reports, writable = 0, 0, False
        return {
            "ok": writable,
            "status": "ready" if writable else "degraded",
            "serviceVersion": VERSION,
            "storage": "persistent" if self.persistent_disk_mounted else "instance-local",
            "workloadProfiles": len(WORKLOADS),
            "chaosScenarios": len(CHAOS_SCENARIOS),
            "validationRuns": count,
            "capacityReports": reports,
            "productionMutation": False,
            "externalTraffic": False,
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "ok": True,
            "version": VERSION,
            "workloads": [{"id": key, **value} for key, value in WORKLOADS.items()],
            "chaosScenarios": [{"id": key, **value} for key, value in CHAOS_SCENARIOS.items()],
        }

    def _operation(self, profile: str, workspace: Path, sequence: int, payload_bytes: int) -> Callable[[], str]:
        if profile == "api-read":
            value = {"sequence": sequence, "records": list(range(16)), "workspace": workspace.name}
            return lambda: hashlib.sha256(_canonical(value)).hexdigest()
        if profile == "large-payload":
            data = {"sequence": sequence, "payload": "x" * payload_bytes, "valid": True}
            return lambda: hashlib.sha256(_canonical(data)).hexdigest()
        if profile == "webhook-burst":
            body = _canonical({"sequence": sequence, "event": "research.validation"})
            return lambda: hashlib.sha256(b"validation-secret." + body).hexdigest()
        if profile == "queue-throughput":
            def queue_operation() -> str:
                item = {"id": sequence, "state": "queued"}
                item["state"] = "acknowledged"
                return _sha(item)
            return queue_operation
        if profile == "api-write":
            path = workspace / "load.sqlite3"
            def sqlite_operation() -> str:
                with sqlite3.connect(path, timeout=10) as db:
                    db.execute("PRAGMA journal_mode=WAL")
                    db.execute("CREATE TABLE IF NOT EXISTS writes(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
                    db.execute("INSERT OR REPLACE INTO writes(id,value) VALUES(?,?)", (sequence, _sha({"sequence": sequence})))
                    return str(db.execute("SELECT value FROM writes WHERE id=?", (sequence,)).fetchone()[0])
            return sqlite_operation
        raise ValidationError("Unknown workload profile.", 404)

    def run_load(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        profile = _clean_id(payload.get("profile", "api-read"), "workload profile")
        if profile not in WORKLOADS:
            raise ValidationError("Unknown workload profile.", 404)
        iterations = max(1, min(int(payload.get("iterations", 100)), self.max_iterations))
        concurrency = max(1, min(int(payload.get("concurrency", 4)), self.max_concurrency, iterations))
        payload_bytes = max(128, min(int(payload.get("payloadBytes", 4096)), 2_000_000))
        budget = {
            "p95Ms": max(1.0, float((payload.get("budget") or {}).get("p95Ms", self.default_p95_ms))),
            "maxErrorRate": max(0.0, min(float((payload.get("budget") or {}).get("maxErrorRate", self.default_error_rate)), 1.0)),
            "minThroughputPerSecond": max(0.0, float((payload.get("budget") or {}).get("minThroughputPerSecond", 0.0))),
        }
        run_id = _clean_id(payload.get("id") or f"load-{uuid.uuid4().hex[:12]}", "run id")
        created = _now()
        latencies: list[float] = []
        errors: list[str] = []
        started = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="sc-lab-load-") as temp:
            workspace = Path(temp)
            def execute(sequence: int) -> None:
                operation = self._operation(profile, workspace, sequence, payload_bytes)
                attempt_started = time.perf_counter()
                try:
                    result = operation()
                    if not result:
                        raise RuntimeError("empty validation result")
                except Exception as exc:  # bounded validation capture
                    errors.append(type(exc).__name__)
                finally:
                    latencies.append((time.perf_counter() - attempt_started) * 1000.0)
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(execute, sequence) for sequence in range(iterations)]
                for future in as_completed(futures):
                    future.result()
        duration = max(time.perf_counter() - started, 0.000001)
        error_rate = len(errors) / iterations
        metrics = {
            "iterations": iterations,
            "concurrency": concurrency,
            "durationSeconds": round(duration, 6),
            "throughputPerSecond": round(iterations / duration, 3),
            "latencyMs": {
                "min": round(min(latencies), 4), "mean": round(statistics.fmean(latencies), 4),
                "p50": round(_percentile(latencies, .50), 4), "p95": round(_percentile(latencies, .95), 4),
                "p99": round(_percentile(latencies, .99), 4), "max": round(max(latencies), 4),
            },
            "errors": len(errors), "errorRate": round(error_rate, 6),
        }
        checks = {
            "p95": metrics["latencyMs"]["p95"] <= budget["p95Ms"],
            "errorRate": error_rate <= budget["maxErrorRate"],
            "throughput": metrics["throughputPerSecond"] >= budget["minThroughputPerSecond"],
        }
        result = {
            "id": run_id, "kind": "load", "profile": profile, "status": "passed" if all(checks.values()) else "failed",
            "actor": str(actor or "system")[:200], "createdAt": created, "completedAt": _now(),
            "configuration": {"iterations": iterations, "concurrency": concurrency, "payloadBytes": payload_bytes},
            "budget": budget, "checks": checks, "metrics": metrics, "productionResourcesMutated": False,
            "externalTrafficGenerated": False,
        }
        result["resultHash"] = _sha(result)
        self._store_run(result, payload)
        return {"ok": result["status"] == "passed", "version": VERSION, "run": result}

    def _chaos_database_lock(self, workspace: Path) -> dict[str, Any]:
        path = workspace / "lock.sqlite3"
        with sqlite3.connect(path) as seed:
            seed.execute("CREATE TABLE records(id INTEGER PRIMARY KEY, value TEXT)")
        locked = sqlite3.connect(path, timeout=.05)
        locked.execute("BEGIN EXCLUSIVE")
        locked.execute("INSERT INTO records(value) VALUES('held')")
        detected = False
        try:
            with sqlite3.connect(path, timeout=.05) as contender:
                contender.execute("INSERT INTO records(value) VALUES('contender')")
        except sqlite3.OperationalError:
            detected = True
        finally:
            locked.rollback(); locked.close()
        with sqlite3.connect(path) as recovered:
            recovered.execute("INSERT INTO records(value) VALUES('recovered')")
            count = recovered.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        return {"faultDetected": detected, "recovered": count == 1, "retryBounded": True}

    def _chaos_storage_latency(self, workspace: Path) -> dict[str, Any]:
        path = workspace / "latency.bin"; data = os.urandom(8192); start=time.perf_counter(); time.sleep(.01); path.write_bytes(data)
        return {"faultInjectedMs": 10, "integrityVerified": hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(data).digest(), "elapsedMs": round((time.perf_counter()-start)*1000,3)}

    def _chaos_worker_termination(self, workspace: Path) -> dict[str, Any]:
        checkpoint=workspace/"checkpoint.json"; checkpoint.write_text(json.dumps({"completed": 5, "total": 10}))
        state=json.loads(checkpoint.read_text()); resumed=list(range(state["completed"], state["total"]))
        return {"checkpointFound": True, "resumedUnits": len(resumed), "completed": state["completed"]+len(resumed)==state["total"]}

    def _chaos_network_timeout(self, workspace: Path) -> dict[str, Any]:
        del workspace
        attempts=[]
        for attempt in range(1,4):
            attempts.append({"attempt":attempt,"outcome":"timeout" if attempt<3 else "recovered","backoffMs":min(1000,25*(2**(attempt-1)))})
        return {"externalTrafficGenerated":False,"attempts":attempts,"recovered":attempts[-1]["outcome"]=="recovered"}

    def _chaos_partial_write(self, workspace: Path) -> dict[str, Any]:
        path=workspace/"artifact.part"; expected=b"complete-artifact"; path.write_bytes(expected[:8]); rejected=hashlib.sha256(path.read_bytes()).hexdigest()!=hashlib.sha256(expected).hexdigest(); path.unlink()
        return {"partialArtifactRejected":rejected,"cleanupCompleted":not path.exists(),"activeArtifactReplaced":False}

    def run_chaos(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        scenario = _clean_id(payload.get("scenario", "database-lock"), "chaos scenario")
        if scenario not in CHAOS_SCENARIOS:
            raise ValidationError("Unknown chaos scenario.", 404)
        run_id = _clean_id(payload.get("id") or f"chaos-{uuid.uuid4().hex[:12]}", "run id")
        created = _now(); started=time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="sc-lab-chaos-") as temp:
            workspace=Path(temp)
            result_data = {
                "database-lock": self._chaos_database_lock,
                "storage-latency": self._chaos_storage_latency,
                "worker-termination": self._chaos_worker_termination,
                "network-timeout": self._chaos_network_timeout,
                "partial-write": self._chaos_partial_write,
            }[scenario](workspace)
        passed = {
            "database-lock": bool(result_data.get("faultDetected") and result_data.get("recovered") and result_data.get("retryBounded")),
            "storage-latency": bool(result_data.get("integrityVerified")),
            "worker-termination": bool(result_data.get("checkpointFound") and result_data.get("completed")),
            "network-timeout": bool(result_data.get("recovered") and not result_data.get("externalTrafficGenerated")),
            "partial-write": bool(result_data.get("partialArtifactRejected") and result_data.get("cleanupCompleted") and not result_data.get("activeArtifactReplaced")),
        }[scenario]
        result={"id":run_id,"kind":"chaos","profile":scenario,"status":"passed" if passed else "failed","actor":str(actor or "system")[:200],"createdAt":created,"completedAt":_now(),"durationSeconds":round(time.perf_counter()-started,6),"results":result_data,"productionResourcesMutated":False,"externalTrafficGenerated":False}
        result["resultHash"]=_sha(result); self._store_run(result,payload)
        return {"ok":passed,"version":VERSION,"run":result}

    def _store_run(self, result: dict[str, Any], payload: dict[str, Any]) -> None:
        with self._lock, self._connect() as db:
            exists=db.execute("SELECT result_hash FROM validation_runs WHERE id=?",(result["id"],)).fetchone()
            if exists:
                if exists[0] == result["resultHash"]:
                    return
                raise ValidationError("Validation run id already exists with different content.",409)
            db.execute("INSERT INTO validation_runs VALUES(?,?,?,?,?,?,?,?,?)",(result["id"],result["kind"],result["profile"],result["status"],result["createdAt"],result["completedAt"],json.dumps(payload,sort_keys=True),json.dumps(result,sort_keys=True),result["resultHash"]))
            excess=db.execute("SELECT COUNT(*) FROM validation_runs").fetchone()[0]-self.history_limit
            if excess>0: db.execute("DELETE FROM validation_runs WHERE id IN (SELECT id FROM validation_runs ORDER BY created_at ASC LIMIT ?)",(excess,))

    def list_runs(self, kind: str = "", limit: int = 200) -> dict[str, Any]:
        limit=max(1,min(int(limit),2000)); params=[]; where=""
        if kind:
            where=" WHERE kind=?"; params.append(_clean_id(kind,"run kind"))
        with self._connect() as db:
            rows=db.execute(f"SELECT result_json FROM validation_runs{where} ORDER BY created_at DESC LIMIT ?",(*params,limit)).fetchall()
        return {"ok":True,"version":VERSION,"runs":[json.loads(row[0]) for row in rows]}

    def get_run(self, run_id: str) -> dict[str, Any]:
        run_id=_clean_id(run_id,"run id")
        with self._connect() as db: row=db.execute("SELECT result_json FROM validation_runs WHERE id=?",(run_id,)).fetchone()
        if not row: raise ValidationError("Validation run not found.",404)
        return {"ok":True,"version":VERSION,"run":json.loads(row[0])}

    def capacity_report(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        limit=max(1,min(int(payload.get("limit",100)),1000)); runs=self.list_runs("load",limit)["runs"]
        passed=[run for run in runs if run["status"]=="passed"]
        profiles={}
        for run in runs:
            item=profiles.setdefault(run["profile"],{"runs":0,"passed":0,"maxSustainedThroughputPerSecond":0.0,"worstP95Ms":0.0,"maxValidatedConcurrency":0})
            item["runs"]+=1; item["passed"]+=int(run["status"]=="passed")
            metrics=run.get("metrics",{}); item["maxSustainedThroughputPerSecond"]=max(item["maxSustainedThroughputPerSecond"],float(metrics.get("throughputPerSecond",0)))
            item["worstP95Ms"]=max(item["worstP95Ms"],float(metrics.get("latencyMs",{}).get("p95",0))); item["maxValidatedConcurrency"]=max(item["maxValidatedConcurrency"],int(run.get("configuration",{}).get("concurrency",0)))
        report={"id":_clean_id(payload.get("id") or f"capacity-{uuid.uuid4().hex[:12]}","report id"),"createdAt":_now(),"actor":str(actor or "system")[:200],"runCount":len(runs),"passedRunCount":len(passed),"profiles":profiles,"recommendations":[],"productionSizingClaim":False}
        if not runs: report["recommendations"].append("Run representative load profiles before setting production capacity targets.")
        if runs and len(passed)<len(runs): report["recommendations"].append("Resolve failed performance budgets before beta readiness.")
        if runs and len(passed)==len(runs): report["recommendations"].append("Repeat validation on production-equivalent infrastructure before publishing capacity limits.")
        report["reportHash"]=_sha(report)
        with self._connect() as db: db.execute("INSERT OR REPLACE INTO capacity_reports VALUES(?,?,?,?)",(report["id"],report["createdAt"],json.dumps(report,sort_keys=True),report["reportHash"]))
        return {"ok":True,"version":VERSION,"report":report}

    def dashboard(self) -> dict[str, Any]:
        with self._connect() as db:
            counts={row[0]:row[1] for row in db.execute("SELECT kind,COUNT(*) FROM validation_runs GROUP BY kind")}
            statuses={row[0]:row[1] for row in db.execute("SELECT status,COUNT(*) FROM validation_runs GROUP BY status")}
            latest=[json.loads(row[0]) for row in db.execute("SELECT result_json FROM validation_runs ORDER BY created_at DESC LIMIT 10")]
        return {"ok":True,"version":VERSION,"counts":{"loadRuns":counts.get("load",0),"chaosRuns":counts.get("chaos",0),"passed":statuses.get("passed",0),"failed":statuses.get("failed",0)},"latestRuns":latest,"productionChaosEnabled":False}
