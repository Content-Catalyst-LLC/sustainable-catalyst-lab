from __future__ import annotations

import signal
from threading import Event, Thread
import time
import traceback
from typing import Callable

from app.compute import ComputeExecutionError
from app.worker_agent_runtime import WorkerAgentError, execute_contract, externalize_receipt_result, materialize_artifact_inputs, verify_contract

from .client import CoordinatorClient, CoordinatorError
from .config import AgentConfig


class LeaseRenewer:
    def __init__(self, client: CoordinatorClient, lease_id: str, interval_seconds: float):
        self.client = client
        self.lease_id = lease_id
        self.interval_seconds = max(10.0, interval_seconds)
        self.stop_event = Event()
        self.error: Exception | None = None
        self.thread = Thread(target=self._run, name=f"lease-renewer-{lease_id}", daemon=True)

    def _run(self) -> None:
        while not self.stop_event.wait(self.interval_seconds):
            try:
                self.client.renew(self.lease_id)
            except Exception as exc:  # the main runtime checks this before completion
                self.error = exc
                self.stop_event.set()
                return

    def __enter__(self) -> "LeaseRenewer":
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop_event.set()
        self.thread.join(timeout=2)


class WorkerAgent:
    def __init__(self, config: AgentConfig, log: Callable[[str], None] = print):
        self.config = config
        self.client = CoordinatorClient(config)
        self.log = log
        self.stop_event = Event()
        self.active_jobs = 0
        self.last_heartbeat = 0.0

    def request_stop(self, *_: object) -> None:
        self.stop_event.set()

    def install_signal_handlers(self) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, self.request_stop)
            except ValueError:
                pass

    def heartbeat(self, state: str = "online", force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self.last_heartbeat < self.config.heartbeat_interval_seconds:
            return
        self.client.heartbeat(state, self.active_jobs, 0)
        self.last_heartbeat = now

    def run_once(self) -> bool:
        self.client.ensure_credential()
        self.heartbeat(force=True)
        claim = self.client.claim()
        if not claim.get("claimed"):
            return False
        contract = claim.get("contract") or {}
        contract_id = str(contract.get("id") or "")
        lease_id = str(contract.get("leaseId") or "")
        if not contract_id or not lease_id:
            raise WorkerAgentError("Coordinator returned an incomplete lease contract.")
        verify_contract(
            contract,
            self.config.worker_id,
            self.config.contract_secret,
            self.config.allow_insecure_contracts,
        )
        materialized_inputs, materialized_artifacts = materialize_artifact_inputs(contract, self.client.download_artifact)
        self.client.acknowledge(contract_id)
        self.active_jobs = 1
        self.heartbeat(force=True)
        try:
            renew_interval = max(10.0, min(self.config.lease_seconds / 3.0, 120.0))
            with LeaseRenewer(self.client, lease_id, renew_interval) as renewer:
                receipt = execute_contract(
                    contract,
                    self.config.worker_id,
                    self.config.contract_secret,
                    {"mode": "worker-agent", "client": self.config.worker_id},
                    self.config.allow_insecure_contracts,
                    materialized_inputs,
                )
                receipt["materializedInputArtifacts"] = materialized_artifacts
                receipt = externalize_receipt_result(
                    receipt,
                    self.client.upload_artifact,
                    self.config.result_artifact_threshold_bytes,
                )
                if renewer.error:
                    raise CoordinatorError(f"Lease renewal failed during execution: {renewer.error}")
            self.client.complete(contract_id, receipt)
            self.log(f"completed {contract_id} method={receipt['method']} durationMs={receipt['durationMs']}")
            return True
        except ComputeExecutionError as exc:
            if exc.retryable:
                self.client.release(lease_id, str(exc), True)
            else:
                self.client.fail(contract_id, str(exc))
            self.log(f"compute failure {contract_id}: {exc}")
            return True
        except WorkerAgentError as exc:
            self.client.release(lease_id, str(exc), False)
            self.log(f"contract rejected {contract_id}: {exc}")
            return True
        except Exception as exc:
            try:
                self.client.release(lease_id, str(exc), True)
            except Exception:
                self.log(traceback.format_exc())
            self.log(f"worker failure {contract_id}: {exc}")
            return True
        finally:
            self.active_jobs = 0
            try:
                self.heartbeat(force=True)
            except Exception as exc:
                self.log(f"heartbeat warning: {exc}")

    def run_forever(self) -> None:
        self.install_signal_handlers()
        self.log(f"worker agent {self.config.worker_id} connecting to {self.config.coordinator_url}")
        try:
            while not self.stop_event.is_set():
                try:
                    worked = self.run_once()
                except CoordinatorError as exc:
                    if exc.status in {401, 403}:
                        self.log(f"worker authentication failed: {exc}")
                    else:
                        self.log(str(exc))
                    worked = False
                if self.config.once:
                    break
                if not worked:
                    self.stop_event.wait(self.config.poll_interval_seconds)
        finally:
            try:
                self.heartbeat("draining", force=True)
            except Exception:
                pass
