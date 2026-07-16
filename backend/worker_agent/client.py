from __future__ import annotations

import json
from pathlib import Path
import tempfile
import urllib.error
import urllib.request
from typing import Any

from .config import AgentConfig


class CoordinatorError(RuntimeError):
    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.status = status


class CredentialStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self, worker_id: str) -> str:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return ""
        if payload.get("workerId") != worker_id:
            return ""
        return str(payload.get("credential") or "")

    def save(self, worker_id: str, credential: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"schema": "sc-lab-worker-credential/0.31.2", "workerId": worker_id, "credential": credential}, indent=2)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as handle:
            handle.write(payload)
            tmp = Path(handle.name)
        tmp.chmod(0o600)
        tmp.replace(self.path)
        self.path.chmod(0o600)


class CoordinatorClient:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.store = CredentialStore(config.credential_file)
        self.credential = self.store.load(config.worker_id)

    def _request(self, path: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        url = f"{self.config.coordinator_url}{path}"
        body = None if payload is None else json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        request_headers = {"Accept": "application/json", "User-Agent": "Sustainable-Catalyst-Lab-Worker/0.31.2"}
        if body is not None:
            request_headers["Content-Type"] = "application/json"
        request_headers.update(headers or {})
        request = urllib.request.Request(url, data=body, headers=request_headers, method="GET" if body is None else "POST")
        try:
            with urllib.request.urlopen(request, timeout=self.config.request_timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {"ok": True}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(raw).get("detail") or json.loads(raw).get("message") or raw
            except json.JSONDecodeError:
                detail = raw or str(exc)
            raise CoordinatorError(str(detail), exc.code) from exc
        except urllib.error.URLError as exc:
            raise CoordinatorError(f"Coordinator request failed: {exc.reason}") from exc

    def enroll(self) -> dict[str, Any]:
        headers = {"X-SC-Lab-Worker-Enrollment": self.config.enrollment_token} if self.config.enrollment_token else {}
        result = self._request("/v1/worker-agent/enroll", self.config.worker_payload(), headers)
        credential = str(result.get("credential") or "")
        if not credential:
            raise CoordinatorError("Coordinator did not return a worker credential.")
        self.credential = credential
        self.store.save(self.config.worker_id, credential)
        return result

    def ensure_credential(self) -> str:
        if not self.credential:
            self.enroll()
        return self.credential

    def _worker_headers(self) -> dict[str, str]:
        return {"X-SC-Lab-Worker-Credential": self.ensure_credential()}

    def heartbeat(self, state: str, active_jobs: int = 0, queued_jobs: int = 0) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/heartbeat",
            {"state": state, "load": {"activeJobs": active_jobs, "queuedJobs": queued_jobs}},
            self._worker_headers(),
        )

    def claim(self) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/claim",
            {"leaseSeconds": self.config.lease_seconds},
            self._worker_headers(),
        )

    def acknowledge(self, contract_id: str) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/contracts/{contract_id}/acknowledge",
            {}, self._worker_headers(),
        )

    def renew(self, lease_id: str) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/leases/{lease_id}/renew",
            {"leaseSeconds": self.config.lease_seconds}, self._worker_headers(),
        )

    def release(self, lease_id: str, reason: str, requeue: bool = True) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/leases/{lease_id}/release",
            {"reason": reason, "requeue": requeue}, self._worker_headers(),
        )

    def complete(self, contract_id: str, receipt: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/contracts/{contract_id}/complete",
            {"ok": True, "result": receipt, "receiptHash": receipt.get("receiptHash"), "warnings": []},
            self._worker_headers(),
        )

    def fail(self, contract_id: str, message: str) -> dict[str, Any]:
        return self._request(
            f"/v1/worker-agent/{self.config.worker_id}/contracts/{contract_id}/complete",
            {"ok": False, "error": message, "warnings": []}, self._worker_headers(),
        )

    def rotate_credential(self) -> dict[str, Any]:
        result = self._request(
            f"/v1/worker-agent/{self.config.worker_id}/credential/rotate", {}, self._worker_headers()
        )
        credential = str(result.get("credential") or "")
        if not credential:
            raise CoordinatorError("Coordinator did not return the rotated credential.")
        self.credential = credential
        self.store.save(self.config.worker_id, credential)
        return result
