from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import platform
from typing import Iterable

from app.registry import catalog


def _bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int, low: int, high: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(low, min(high, value))


def _float(name: str, default: float, low: float, high: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(low, min(high, value))


def _csv(value: str | None) -> list[str]:
    return list(dict.fromkeys(part.strip() for part in str(value or "").split(",") if part.strip()))


def _default_methods() -> list[str]:
    return [str(item["id"]) for item in catalog()]


def _default_packages(methods: Iterable[str]) -> list[str]:
    wanted = set(methods)
    packages: list[str] = []
    for item in catalog():
        if item["id"] not in wanted:
            continue
        for package in item.get("packages") or []:
            if package not in packages:
                packages.append(package)
    return packages


@dataclass
class AgentConfig:
    coordinator_url: str
    worker_id: str
    name: str
    worker_type: str = "local-python"
    enrollment_token: str = ""
    contract_secret: str = ""
    credential_file: Path = field(default_factory=lambda: Path.home() / ".config" / "sustainable-catalyst-lab" / "worker-credential.json")
    methods: list[str] = field(default_factory=_default_methods)
    packages: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=lambda: ["trusted", "python-core"])
    project_allowlist: list[str] = field(default_factory=list)
    memory_mb: int = 1024
    cpu_cores: int = max(1, os.cpu_count() or 1)
    max_concurrent_jobs: int = 1
    checkpointing: bool = True
    local_data: bool = False
    poll_interval_seconds: float = 5.0
    heartbeat_interval_seconds: int = 30
    lease_seconds: int = 300
    request_timeout_seconds: int = 30
    artifact_chunk_bytes: int = 1048576
    result_artifact_threshold_bytes: int = 262144
    allow_insecure_contracts: bool = False
    once: bool = False

    def __post_init__(self) -> None:
        self.coordinator_url = self.coordinator_url.rstrip("/")
        self.worker_id = self.worker_id.strip()
        self.name = self.name.strip() or self.worker_id
        self.worker_type = self.worker_type.strip().lower()
        self.methods = list(dict.fromkeys(self.methods or _default_methods()))
        self.packages = list(dict.fromkeys(self.packages or _default_packages(self.methods)))
        self.tags = list(dict.fromkeys(self.tags))
        self.project_allowlist = list(dict.fromkeys(self.project_allowlist))
        if not self.coordinator_url.startswith(("http://", "https://")):
            raise ValueError("Coordinator URL must use http:// or https://.")
        if not self.worker_id:
            raise ValueError("Worker ID is required.")
        if not self.contract_secret and not self.allow_insecure_contracts:
            raise ValueError("SC_LAB_WORKER_CONTRACT_SECRET is required unless insecure development contracts are explicitly enabled.")

    @classmethod
    def from_env(cls, **overrides: object) -> "AgentConfig":
        worker_id = str(overrides.pop("worker_id", "") or os.getenv("SC_LAB_WORKER_ID", f"worker-{platform.node() or 'local'}"))
        methods = overrides.pop("methods", None)
        packages = overrides.pop("packages", None)
        tags = overrides.pop("tags", None)
        projects = overrides.pop("project_allowlist", None)
        values = {
            "coordinator_url": os.getenv("SC_LAB_WORKER_COORDINATOR_URL", "http://127.0.0.1:8000"),
            "worker_id": worker_id,
            "name": os.getenv("SC_LAB_WORKER_NAME", platform.node() or worker_id),
            "worker_type": os.getenv("SC_LAB_WORKER_TYPE", "local-python"),
            "enrollment_token": os.getenv("SC_LAB_WORKER_ENROLLMENT_TOKEN", ""),
            "contract_secret": os.getenv("SC_LAB_WORKER_CONTRACT_SECRET", os.getenv("SC_LAB_DISPATCHER_CONTRACT_SECRET", "")),
            "credential_file": Path(os.getenv("SC_LAB_WORKER_CREDENTIAL_FILE", str(Path.home() / ".config" / "sustainable-catalyst-lab" / "worker-credential.json"))).expanduser(),
            "methods": _csv(os.getenv("SC_LAB_WORKER_METHODS")) if methods is None else methods,
            "packages": _csv(os.getenv("SC_LAB_WORKER_PACKAGES")) if packages is None else packages,
            "tags": _csv(os.getenv("SC_LAB_WORKER_TAGS", "trusted,python-core")) if tags is None else tags,
            "project_allowlist": _csv(os.getenv("SC_LAB_WORKER_PROJECT_ALLOWLIST")) if projects is None else projects,
            "memory_mb": _int("SC_LAB_WORKER_MEMORY_MB", 1024, 128, 1048576),
            "cpu_cores": _int("SC_LAB_WORKER_CPU_CORES", max(1, os.cpu_count() or 1), 1, 256),
            "max_concurrent_jobs": _int("SC_LAB_WORKER_MAX_CONCURRENT_JOBS", 1, 1, 128),
            "checkpointing": _bool("SC_LAB_WORKER_CHECKPOINTING", True),
            "local_data": _bool("SC_LAB_WORKER_LOCAL_DATA", False),
            "poll_interval_seconds": _float("SC_LAB_WORKER_POLL_INTERVAL_SECONDS", 5.0, 0.5, 300.0),
            "heartbeat_interval_seconds": _int("SC_LAB_WORKER_HEARTBEAT_INTERVAL_SECONDS", 30, 5, 3600),
            "lease_seconds": _int("SC_LAB_WORKER_LEASE_SECONDS", 300, 30, 3600),
            "request_timeout_seconds": _int("SC_LAB_WORKER_REQUEST_TIMEOUT_SECONDS", 30, 3, 300),
            "artifact_chunk_bytes": _int("SC_LAB_WORKER_ARTIFACT_CHUNK_BYTES", 1048576, 65536, 8388608),
            "result_artifact_threshold_bytes": _int("SC_LAB_WORKER_RESULT_ARTIFACT_THRESHOLD_BYTES", 262144, 1024, 16777216),
            "allow_insecure_contracts": _bool("SC_LAB_WORKER_ALLOW_INSECURE_CONTRACTS", False),
            "once": _bool("SC_LAB_WORKER_ONCE", False),
        }
        values.update(overrides)
        return cls(**values)

    def worker_payload(self) -> dict[str, object]:
        return {
            "id": self.worker_id,
            "name": self.name,
            "workerType": self.worker_type,
            "state": "online",
            "endpointMode": "secure-credential-pull-artifact-transport",
            "capabilities": {
                "methods": self.methods,
                "packages": self.packages,
                "cpuCores": self.cpu_cores,
                "memoryMb": self.memory_mb,
                "gpu": False,
                "checkpointing": self.checkpointing,
                "localData": self.local_data,
                "maxConcurrentJobs": self.max_concurrent_jobs,
                "architectures": [platform.machine(), platform.system().lower()],
                "artifactTransport": True,
                "resumableTransfers": True,
            },
            "load": {"activeJobs": 0, "queuedJobs": 0},
            "tags": self.tags,
            "projectAllowlist": self.project_allowlist,
            "metadata": {
                "agentVersion": "0.31.3",
                "pythonVersion": platform.python_version(),
                "platform": platform.platform(),
            },
        }
